#!/usr/bin/env python3
"""Reconcile the OCR lane's evidence into proposed Ledger updates and a starter civil MTO (Prompt 9, proposal mode).

Inputs (read-only):
  testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv
  testbeds/eastsound/derived/ocr/     Ledger_Crosswalk, Tag_Hits, Quantity_Hits, Unmatched_Tags, Sheet_Map,
                                      Spot_Check and pages/*.json
  testbeds/eastsound/index/Library_Manifest.csv   SHA-256 of each native file opened below (checked first)
  testbeds/eastsound/tools/extract_drawing_text.py   imported for its matching rules (search forms, Name
                                      quantities, the unmatched-tag scan); it is not run
  testbeds/eastsound/library/         only the owner's Division 26 review items: E1.1, E2.2, E6.1, E6.2 and
                                      E9.1 (Part 3), Add. 4 p.1 and main spec p.326, each read in the text layer

Outputs: testbeds/eastsound/derived/reconciliation/ only. Nothing is written to the Ledger or an MTO.

No LLM calls. Lists are sorted, boxes are rounded to 0.01 pt, line endings are LF, files are UTF-8 without a
BOM and there are no timestamps, so two runs on the same inputs give identical bytes. The run stops, writing
nothing, if a tie-out to Ledger_Crosswalk.csv or Unmatched_Tags.csv fails or a Division 26 evidence line is
not found in the native text layer.

Run from the repo root (the packages pinned in requirements.txt must be installed; the extractor imports them):
  python testbeds/eastsound/tools/build_reconciliation.py
  add --crops <folder outside the repo> to render each Needs_Check crop as a PNG
"""

import os
import sys

# The extractor pins these for repeatable output and re-executes itself if they are missing; set them here
# first so the import doesn't restart this script halfway.
if os.environ.get("PYTHONHASHSEED") != "0" or os.environ.get("OMP_THREAD_LIMIT") != "1":
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["OMP_THREAD_LIMIT"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)

import argparse
import csv
import importlib.util
import io
import itertools
import re
from collections import Counter, defaultdict
from pathlib import Path

import pymupdf

REPO = Path(__file__).resolve().parents[3]   # this file: testbeds/eastsound/tools/
TB = REPO / "testbeds" / "eastsound"
OCR = TB / "derived" / "ocr"
LIB = TB / "library"
LEDGER = TB / "project" / "02_Project_Ledger" / "Project_Ledger.csv"
MANIFEST = TB / "index" / "Library_Manifest.csv"
EXTRACTOR = TB / "tools" / "extract_drawing_text.py"
OUT_DEFAULT = TB / "derived" / "reconciliation"

_spec = importlib.util.spec_from_file_location("extract_drawing_text", EXTRACTOR)
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)

# ---------------------------------------------------------------- rules (README.md lists them)

TAG_COL = X.TAG_LEVEL_COL
METHOD_ORDER = {"text-layer": 0, "ocr": 1, "bluebeam-ocr": 2}
MTO_UNITS = ("LF", "EA", "CY", "SF", "SY")
PILOT_SHEET_RE = re.compile(r"^C[0127]\.\d+A?$")   # decision B: sheets C0-C2 and C7
CROP_PAD = 24.0          # pt added around a Needs_Check crop (the nearest-tag distance)
SAME_LINE = 0.5          # vertical overlap / smaller height that puts two boxes on one text line
CLUSTER = 40.0           # pt: the lines of one drawing label must sit this close to its first line
NEEDS_CHECK = "needs check"
PLUS_QTY_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?(?:\s*\+\s*\d+(?:\.\d+)?)+)\s?(LF|SF|SY|CY|EA)\b")
KN_LABEL_RE = re.compile(r"^(\d+) \((read|by order)(?:; marker read as \S+)?; "
                         r"(Verified|Verified-Visual|Inferred|Unresolved)\)$")
KN_ANCHOR_RE = re.compile(r"\bKN\s+([\d,\s–-]+)")
EXPLICIT_EA_RE = re.compile(r"\b(?:EA\.?|EACH)\b")

PART3 = LIB / "Pages from eswd-wwtp-upgrade-ph1-11x17-plans - Part 3.pdf"
ADD4 = LIB / "addendum-no4-eswd.pdf"
SPEC = LIB / "eswd-wwtp-upgrade-phase-i-specs.pdf"

# Owner's decision (Carl, 2026-09-30): the C0.2 earthwork totals go in the MTO with no Ledger ID and are
# proposed as new Ledger rows. The bid item follows index/04_Bid_Item_Spine.md: Item 1 carries all work not
# itemized elsewhere (00 24 13 ¶1, p.16; Inferred).
EARTHWORK_BID = "1 (Inferred: 04 puts work not itemized elsewhere in Item 1; 00 24 13 ¶1, p.16)"
NEW_ROWS = [  # (page key, unit, word before the value, proposed tag, proposed Name)
    ("009", "CY", "CUT", "PROPOSED-Earthwork cut", "Earthwork, total volume of proposed cut"),
    ("009", "CY", "FILL", "PROPOSED-Earthwork fill", "Earthwork, total volume of proposed fill"),
]

# Owner's Division 26 review (Carl, 2026-09-30). Every evidence line is re-read from the native text layer on
# each run; a drawing label's lines must sit within CLUSTER pt of its first line. Evidence: (file, page, where,
# [regex per line]). Drawing pages carry /Rotate 270; boxes are as displayed, like derived/ocr/.
E11 = (PART3, 18, "E1.1")
E61 = (PART3, 26, "E6.1")
E91 = (PART3, 43, "E9.1")
ADD4_P1 = (ADD4, 1, "Add. 4 p.1")
SPEC_P326 = (SPEC, 326, "main spec p.326")
DIV26 = [
    {"id": 241, "field": TAG_COL, "proposed": "Verified",
     "evidence": [E11 + ([r"TS", r"75 kVA", r"480-208Y/120V"],)],
     "reason": "E1.1 reads \"TS\", \"75 kVA\" and \"480-208Y/120V\" as one plan label in the native text layer, "
               "matching the Tag and Name."},
    {"id": 297, "field": TAG_COL, "proposed": "Verified",
     "evidence": [E61 + ([r"T3", r"10 kVA", r"480-120/240V"],)],
     "reason": "E6.1 reads \"T3\", \"10 kVA\" and \"480-120/240V\" as one one-line label in the native text layer, "
               "matching the Tag and Name."},
    {"id": 349, "field": TAG_COL, "proposed": "Verified",
     "evidence": [E61 + ([r"T2", r"20 kVA", r"480-120/240V"],), E91 + ([r"TRANSFORMER / 480-120/240V / 20 kVA"],)],
     "reason": "E6.1 reads \"T2\", \"20 kVA\" and \"480-120/240V\" as one one-line label, and E9.1 reads "
               "\"TRANSFORMER / 480-120/240V / 20 kVA\", both in the native text layer, matching the Tag and Name."},
    {"id": 239, "field": TAG_COL, "proposed": "Inferred",
     "evidence": [ADD4_P1 + ([r"Temporary Back Up Generator \(Bid Item #18\).*",
                              r"A: The transfer switch is to be the permanent ATS for the project.*",
                              r"A: Test generator connections, automatic load transfer test\."],)],
     "reason": "Add. 4 p.1 Clarification 5, \"Temporary Back Up Generator (Bid Item #18)\": the transfer switch is "
               "the permanent ATS; the temporary generator connects to it; \"Test generator connections, automatic "
               "load transfer test.\" Bid split: permanent ATS = Item 6 (00 24 13 ¶6, p.17: all E-sheet and "
               "Division 26 work, per 04; Inferred); temporary generator hookup and transfer test = Item 18 (Add. 4). "
               "Conflict, cited both ways: the base bid form 00 41 00 p.25 lists Item 18 as \"Train 3 – Stainless "
               "Steel Fabrication Above Water Surface\" (04, Item 18 row). Add. 4 governs as the later document; the "
               "item-number reading stays Inferred, so the row moves to Inferred, not Verified."},
    {"id": 239, "field": "Bid Item",
     "proposed": "6 (permanent ATS); 18 (temporary generator hookup and automatic load transfer test, Add. 4 p.1 "
                 "Clarification 5)",
     "evidence": [ADD4_P1 + ([r"Temporary Back Up Generator \(Bid Item #18\).*",
                              r"A: Test generator connections, automatic load transfer test\."],)],
     "reason": "Owner's bid split per Add. 4 p.1 Clarification 5 (see the tag proposal for this row). Item 6 for the "
               "permanent ATS is Inferred from 00 24 13 ¶6 (p.17) via 04; Item 18 is as Add. 4 cites it, against "
               "the base bid form's Item 18 (00 41 00 p.25)."},
    {"id": 242, "field": "Notes", "append":
        "[Prompt 9, owner's Division 26 review] RFI: the drawings show a 125 kW generator (E1.1 plan label "
        "\"480Y/277V 125 kW DIESEL GENERATOR\"; E6.1 one-line \"125kW / 156kVA\"), but 26 32 13 ¶2.03 C.1 (main spec "
        "p.326) requires a standby rating \"not less than 150.0kW\". The tag stays Unresolved until the Engineer "
        "answers.",
     "evidence": [E11 + ([r"480Y/277V 125", r"kW DIESEL"],), E61 + ([r"125kW / 156kVA"],),
                  SPEC_P326 + ([r"Capacities and Characteristics:", r".*not less than 150\.0kW.*"],)],
     "reason": "Drawings and spec disagree on the generator rating. Tag stays Unresolved; the new reason goes in "
               "Notes. Listed in Summary.md as an RFI."},
]
PANEL_CHECKS = [  # (Ledger ID number, page, sheet, title regex): raster schedules the owner will check by eye
    (240, 27, "E6.2", r"PANEL MDP"),
    (264, 27, "E6.2", r"PANEL LP1 \(MCC\)"),
    (264, 20, "E2.2", r"PANEL LP1 \(MCC\) SCHEDULE"),
    (298, 27, "E6.2", r"PANEL LP2 \(INFLUENT PUMP STATION PANEL\)"),
]

UPDATE_HEADER = ["Proposal No.", "Category", "Ledger ID", "Tag", "Field", "Current Value", "Proposed Value",
                 "Evidence Sheet", "Evidence Set Page", "Evidence BBox (pt)", "Evidence Method", "Confidence",
                 "Reason"]
MTO_HEADER = ["MTO Line", "Ledger ID", "Item", "Quantity", "Unit", "Sheet", "Set Page", "BBox (pt)", "Keyed Note",
              "Method", "Confidence", "Ready (Y/N)", "Source Citation", "Bid Item", "Tie Basis"]
CHECK_HEADER = ["Check No.", "Check Type", "MTO Line", "Ledger ID", "Item", "Quantity", "Unit", "Sheet", "Set Page",
                "Native Page", "Keyed Note", "Confidence", "Why Check", "Crop BBox (pt)", "Reads", "What to Check",
                "Human Result", "Checked By", "Date", "Note"]
CANDIDATE_HEADER = ["Candidate No.", "Candidate Type", "Tag Text", "Shape", "Sheet", "Pages", "Reads on Sheet",
                    "Text-Layer Reads", "OCR Reads", "Bluebeam Reads", "Max OCR Confidence", "Read Level",
                    "First BBox (pt)", "Tag Reads (All Sheets)", "Tag Sheets", "Proposed Name", "Bid Item",
                    "Quantity", "Unit", "MTO Line"]
ID_HEADER = ["Ledger ID", "Ledger Row", "Tag", "Name", "Lane"]
CATEGORIES = {"A": "found, not cited", "B": "cited, not found", "C": "PROPOSED row, printed tag found",
              "D": "owner's Division 26 review"}


# ---------------------------------------------------------------- small helpers

def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def rows_of(field):
    return [int(x) for x in field.split(";") if x.strip().isdigit()]


def box(s):
    return [float(v) for v in s.split(",")]


def fmt_box(b):
    return ",".join(f"{v:.2f}" for v in b)


def union(bs):
    return [min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)]


def pad(b, W, H):
    return [max(0.0, b[0] - CROP_PAD), max(0.0, b[1] - CROP_PAD), min(W, b[2] + CROP_PAD), min(H, b[3] + CROP_PAD)]


def same_line(a, b):
    ov = min(a[3], b[3]) - max(a[1], b[1])
    return ov > 0 and ov >= SAME_LINE * min(a[3] - a[1], b[3] - b[1])


def norm_tag(t):
    return re.sub(r"[^A-Z0-9]", "", t.upper())


def num_eq(a, b):
    try:
        return float(a) == float(b)
    except ValueError:
        return False


def read_key(q):
    """Preferred read first: text layer, then OCR by confidence, then Bluebeam; then position."""
    conf = float(q["Confidence"]) if q.get("Confidence") else 0.0
    return (METHOD_ORDER[q["Method"]], -conf, q["Page Key"], box(q["BBox (pt)"]))


def split_list(field):
    return [x.strip() for x in field.split(";") if x.strip()]


def found_sheets(field):
    """Ledger_Crosswalk "Sheets Found On": "C0.3 [bluebeam-ocr]; C2.1 [ocr, text-layer]" -> sheets."""
    return [re.sub(r"\s*\[.*$", "", x) for x in split_list(field)]


def md_cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return out + ["| " + " | ".join(md_cell(c) for c in r) + " |" for r in rows]


# ---------------------------------------------------------------- inputs

LEDGER_ROWS = X.load_ledger()                         # [(Ledger Row, record)], header = row 1
LROW = dict(LEDGER_ROWS)
LID = {i: f"L-{i - 1:04d}" for i, _ in LEDGER_ROWS}   # decision A: L-0001 = first record (Ledger Row 2)


def row_of_id(n):
    return n + 1


FORMS = {r["row"]: r for r in X.build_forms()}
XW = {int(r["Ledger Row"]): r for r in read_csv(OCR / "Ledger_Crosswalk.csv")}
HITS = read_csv(OCR / "Tag_Hits.csv")
QTY = read_csv(OCR / "Quantity_Hits.csv")
SMAP = {r["Page Key"]: r for r in read_csv(OCR / "Sheet_Map.csv")}
UNMATCHED = read_csv(OCR / "Unmatched_Tags.csv")
SPOT = read_csv(OCR / "Spot_Check.csv")
PAGES = {pg["page_key"]: pg for pg in X.load_pages(OCR)}
INPUTS = [LEDGER, MANIFEST, EXTRACTOR] + [OCR / n for n in (
    "Ledger_Crosswalk.csv", "Tag_Hits.csv", "Quantity_Hits.csv", "Unmatched_Tags.csv", "Sheet_Map.csv",
    "Spot_Check.csv")] + [PART3, ADD4, SPEC]

TIES, FAILS = [], []


def tie(name, ok, detail):
    """Record a tie-out; any failure stops the run before files are written."""
    TIES.append((name, "pass" if ok else "FAIL", detail))
    if not ok:
        FAILS.append(f"{name}: {detail}")


def check_sources():
    manifest = {r["Path"]: r["SHA-256"] for r in read_csv(MANIFEST)}
    bad = [p.relative_to(REPO).as_posix() for p in (PART3, ADD4, SPEC)
           if manifest.get(p.relative_to(REPO).as_posix()) != X.sha256_file(p)]
    if bad:
        sys.exit("Stopped: native files do not match index/Library_Manifest.csv: " + "; ".join(bad))


def page_label(pk):
    sm = SMAP[pk]
    return sm["Set Page"] if sm["Set Page"] else f"Add. 4 p.{sm['Native Page']}"


def page_cite(pk):
    sm = SMAP[pk]
    short = X.PART_SHORT.get(sm["Native File"], sm["Native File"])
    if sm["Set Page"]:
        return f"set p.{sm['Set Page']} ({short} p.{sm['Native Page']})"
    return f"Add. 4 p.{sm['Native Page']}"


def native_page(pk):
    sm = SMAP[pk]
    return f"{X.PART_SHORT.get(sm['Native File'], sm['Native File'])} p.{sm['Native Page']}"


SHEET_PAGES = defaultdict(list)
for _pk in sorted(SMAP):
    SHEET_PAGES[SMAP[_pk]["01 Sheet"]].append(_pk)
PART3_PAGE = {int(sm["Native Page"]): pk for pk, sm in SMAP.items()
              if sm["Native File"] == PART3.name and sm["Set Page"]}


def row_tokens(i):
    """Drawing Sheets tokens for a row: [(sheet, anchors, raw)]."""
    return [t for t in X.split_sheets(LROW[i]["Drawing Sheets"]) if t[0]]


def kn_numbers(anchor_text):
    nums = set()
    for m in KN_ANCHOR_RE.finditer(anchor_text):
        for part in m.group(1).split(","):
            part = part.strip()
            r = re.fullmatch(r"(\d+)\s*[–-]\s*(\d+)", part)
            if r:
                nums.update(range(int(r.group(1)), int(r.group(2)) + 1))
            elif part.isdigit():
                nums.add(int(part))
    return nums


def name_quantities(name):
    """X.name_quantities, plus each term of a sum the Name writes out ("42 + 19 + 42 LF")."""
    items = [(q["v"], q["u"]) for q in X.name_quantities(name) if q["kind"] == "quantity"]
    for m in PLUS_QTY_RE.finditer(name):
        for v in re.findall(r"\d+(?:\.\d+)?", m.group(1)):
            if (v, m.group(2)) not in items:
                items.append((v, m.group(2)))
    return items


def name_words(name):
    return {X.stem(w.upper()) for w in re.findall(r"[A-Za-z]{3,}", name)}


# ---------------------------------------------------------------- native text layer (Division 26 items only)

_DOCS = {}


def native_lines(path, page):
    """Text-layer lines of one native page: [(text, box as displayed)], whitespace collapsed."""
    doc = _DOCS.setdefault(path, pymupdf.open(path))
    pg = doc[page - 1]
    M = pg.rotation_matrix
    lines = defaultdict(list)
    for x0, y0, x1, y1, t, b, ln, wn in pg.get_text("words"):
        lines[(b, ln)].append((wn, t, pymupdf.Rect(x0, y0, x1, y1) * M))
    out = []
    for k in sorted(lines):
        ws = sorted(lines[k], key=lambda w: w[0])
        r = pymupdf.Rect(ws[0][2])
        for w in ws[1:]:
            r |= w[2]
        out.append((" ".join(w[1] for w in ws).strip(), [round(v, 2) for v in (r.x0, r.y0, r.x1, r.y1)]))
    return sorted(out, key=lambda x: (x[1][1], x[1][0], x[0]))


def find_label(path, page, patterns):
    """The first pattern's line, then each other pattern's nearest line; None unless all sit within CLUSTER."""
    lines = native_lines(path, page)
    firsts = [ln for ln in lines if re.fullmatch(patterns[0], ln[0])]
    for first in firsts:
        found = [first]
        for p in patterns[1:]:
            cands = [ln for ln in lines if re.fullmatch(p, ln[0])]
            if not cands:
                break
            best = min(cands, key=lambda ln: (X.edge_dist(first[1], ln[1]), ln[1]))
            if X.edge_dist(first[1], best[1]) > CLUSTER and path != SPEC and path != ADD4:
                break
            found.append(best)
        if len(found) == len(patterns):
            return found
    return None


def set_page_of(path, page):
    if path == PART3:
        return page_label(PART3_PAGE[page])
    return "Add. 4 p.1" if path == ADD4 else f"main spec p.{page}"


def build_div26():
    out = []
    for item in DIV26:
        i = row_of_id(item["id"])
        ev = []
        for path, page, where, pats in item["evidence"]:
            found = find_label(path, page, pats)
            tie(f"Division 26 evidence read: {LID[i]} {item['field']} on {where}", found is not None,
                f"{len(pats)} line(s): " + "; ".join(pats))
            if found:
                ev.append((where, set_page_of(path, page), fmt_box(union([f[1] for f in found])),
                           " / ".join(f"\"{f[0]}\"" for f in found)))
        if len(ev) != len(item["evidence"]):
            continue
        current = LROW[i][item["field"]]
        proposed = item.get("proposed") or (current.rstrip() + " || " + item["append"])
        reads = "; ".join(f"{w}{'' if w == sp else f' (set p.{sp})'}: {txt}" for w, sp, _, txt in ev)
        extra = ""
        if item["field"] == TAG_COL and item["proposed"] == "Verified" and "inferred" in LROW[i]["Notes"].lower():
            extra = (" Weakest-tag rule: this row's Notes still record Inferred facts (" +
                     "; ".join(sorted({m.group(0).strip() for m in re.finditer(r"[^.;]*\b[Ii]nferred\b[^.;]*",
                                                                               LROW[i]["Notes"])})) +
                     "). The row is Verified only if those are accepted too.")
        out.append(["D", LID[i], LROW[i]["Tag"], item["field"], current, proposed, "; ".join(e[0] for e in ev),
                    "; ".join(e[1] for e in ev), "; ".join(e[2] for e in ev), "text-layer (native)", "Verified",
                    item["reason"] + f" Native text layer: {reads}." + extra])
    return out


def panel_checks():
    """Panel schedules on E6.2 and E2.2 are raster images; the text layer holds only their titles. The crop is
    the image directly above the title (their x ranges overlap), plus the title."""
    out = []
    for n, page, sheet, title in PANEL_CHECKS:
        i = row_of_id(n)
        doc = _DOCS.setdefault(PART3, pymupdf.open(PART3))
        pg = doc[page - 1]
        tl = [ln for ln in native_lines(PART3, page) if re.fullmatch(title, ln[0])]
        imgs = []
        for im in pg.get_image_info():
            r = pymupdf.Rect(im["bbox"]) * pg.rotation_matrix
            imgs.append(([round(v, 2) for v in (r.x0, r.y0, r.x1, r.y1)], im["width"], im["height"]))
        hit = None
        if len(tl) == 1:
            t = tl[0][1]
            above = [im for im in imgs if im[0][3] <= t[1] and t[1] - im[0][3] <= 20 and im[0][0] < t[2]
                     and im[0][2] > t[0]]
            hit = min(above, key=lambda im: (t[1] - im[0][3], im[0])) if above else None
        tie(f"Panel schedule located: {LID[i]} {sheet} \"{title}\"", hit is not None,
            f"{len(tl)} title line(s), image above: {'yes' if hit else 'no'}")
        if not hit:
            continue
        pk = PART3_PAGE[page]
        cb = pad(union([hit[0], tl[0][1]]), PAGES[pk]["page"]["width"], PAGES[pk]["page"]["height"])
        out.append({"i": i, "pk": pk, "sheet": sheet, "title": tl[0][0], "title_box": tl[0][1],
                    "image_box": hit[0], "px": (hit[1], hit[2]), "crop": cb})
    return out


# ---------------------------------------------------------------- unmatched tags, per page and method

def unmatched_by_page():
    """Re-run the extractor's own unmatched-tag scan one page (and one read method) at a time."""
    comp = X.compile_forms(list(FORMS.values()))
    out = defaultdict(lambda: {"n": 0, "by": Counter(), "conf": None, "first": None, "text": None, "shape": None})
    for pk in sorted(PAGES):
        pg = PAGES[pk]
        bb = pg.get("bluebeam") or {}
        for m in METHOD_ORDER:
            sub = dict(pg, words=[w for w in pg["words"] if w["method"] == m],
                       bluebeam=dict(bb, words=list(bb.get("words", [])) if m == "bluebeam-ocr" else []))
            for r in X.unmatched_tags([sub], comp):
                e = out[(r[0].replace(" ", ""), pk)]
                e["n"] += r[2]
                e["by"][m] += r[2]
                e["text"] = e["text"] or r[0]
                e["shape"] = r[1]
                if r[6]:
                    c = float(r[6])
                    e["conf"] = c if e["conf"] is None else max(e["conf"], c)
                first = (METHOD_ORDER[m], box(r[8]))
                if e["first"] is None or first < e["first"]:
                    e["first"] = first
    return out


# ---------------------------------------------------------------- Ledger update proposals

def hits_by_row_sheet():
    by = defaultdict(list)           # (Ledger Row, sheet) -> assigned hits (individual rows and range rollups)
    for h in HITS:
        if h["Assignment"] != "assigned":
            continue
        for i in sorted(set(rows_of(h["Ledger Rows"]) + rows_of(h["Rollup Rows"]))):
            by[(i, h["Sheet"])].append(h)
    return by


def method_counts(hs):
    c = Counter(h["Method"] for h in hs)
    return ", ".join(f"{c[m]} {lab}" for m, lab in (("text-layer", "text layer"), ("ocr", "OCR"),
                                                     ("bluebeam-ocr", "Bluebeam")) if c[m])


def add_sheet(current, sheet):
    return (current.strip() + "; " + sheet) if current.strip() else sheet


def category_a(hits_by):
    out = []
    for i in sorted(XW):
        x = XW[i]
        for s in split_list(x["Sheets Found but Not Cited"]):
            hs = sorted(hits_by[(i, s)], key=read_key)
            tl = [h for h in hs if h["Method"] == "text-layer"]
            ev = tl[0] if tl else hs[0]
            fuzzy = " Some reads are fuzzy (a 1/I, 0/O, 5/S, 8/B or #/H swap)." if any(
                h["Fuzzy (Y/N)"] == "Y" for h in hs) else ""
            where = "; ".join(sorted({page_cite(h["Page Key"]) for h in hs}))
            if tl:
                conf, proposed = "Verified", add_sheet(LROW[i]["Drawing Sheets"], s)
                reason = (f"Tag read in the native text layer on {s} ({where}): {method_counts(hs)} read(s). "
                          f"The row does not cite {s}. This row adds {s} only.")
            else:
                conf, proposed = NEEDS_CHECK, ""
                reason = (f"Tag read on {s} ({where}) by OCR or Bluebeam only ({method_counts(hs)}; Inferred)."
                          f"{fuzzy} If the page image confirms it, add {s} to Drawing Sheets.")
            out.append(["A", LID[i], x["Tag"], "Drawing Sheets", LROW[i]["Drawing Sheets"], proposed, s,
                        page_label(ev["Page Key"]), ev["BBox (pt)"], ev["Method"], conf, reason])
    return out


def sheet_coverage(pks):
    return "; ".join(f"{page_cite(pk)}: text layer {SMAP[pk]['Text-Layer Characters']} characters, "
                     f"OCR {SMAP[pk]['OCR Words']} words, Bluebeam {SMAP[pk]['Bluebeam Words'] or 0} words"
                     for pk in pks)


def category_b(unm_page, unm_norm):
    out = []
    for i in sorted(XW):
        x = XW[i]
        raw = {t[0]: t[2] for t in row_tokens(i)}
        forms = FORMS[i]["forms"]
        for s in split_list(x["Sheets Cited but Not Found"]):
            pks = SHEET_PAGES.get(s, [])
            base = (f"Tag not read on {s} (cited as \"{raw.get(s, s)}\") in the text layer, OCR or Bluebeam "
                    f"(search forms: {', '.join(forms)}).")
            if not pks:
                out.append(["B", LID[i], x["Tag"], "Drawing Sheets", LROW[i]["Drawing Sheets"], "", s, "", "",
                            "sheet not in the plan set read by the OCR lane", NEEDS_CHECK,
                            base + " The sheet is not among the 96 set pages or the Add. 4 reissues."])
                continue
            variants = sorted({(k, pk) for fm in forms for (k, pk) in unm_norm.get(norm_tag(fm), []) if pk in pks})
            if variants:
                k, pk = min(variants, key=lambda v: (unm_page[v]["first"], v))
                e = unm_page[(k, pk)]
                seen = "; ".join(f"\"{unm_page[v]['text']}\" ({page_cite(v[1])}, "
                                 f"{', '.join(m for m in METHOD_ORDER if unm_page[v]['by'][m])})" for v in variants)
                reason = (base + f" A variant form was read on this sheet: {seen}. It is in Unmatched_Tags, not "
                          "counted as this tag. Check whether it is this tag as printed before changing the cite.")
                out.append(["B", LID[i], x["Tag"], "Drawing Sheets", LROW[i]["Drawing Sheets"], "", s, page_label(pk),
                            fmt_box(e["first"][1]), ", ".join(m for m in METHOD_ORDER if e["by"][m]), NEEDS_CHECK,
                            reason])
            else:
                reason = (base + f" Searched: {sheet_coverage(pks)}. Absence is not Verified evidence: the cite may "
                          "be to a detail, schedule or note that shows the item without its tag. Check the sheet "
                          "before removing it.")
                out.append(["B", LID[i], x["Tag"], "Drawing Sheets", LROW[i]["Drawing Sheets"], "", s,
                            "; ".join(page_label(pk) for pk in pks), "", "none read (text-layer, ocr, bluebeam-ocr)",
                            NEEDS_CHECK, reason])
    return out


def category_c(hits_by, unm_page, unm_norm):
    """A PROPOSED row whose own designation (the text after "PROPOSED-", letters and digits) equals a printed
    tag read on the drawings: a Ledger tag in Tag_Hits, or a text in Unmatched_Tags."""
    printed = defaultdict(list)
    for i, f in FORMS.items():
        if f["family"] == "printed":
            for fm in f["forms"]:
                if i not in printed[norm_tag(fm)]:
                    printed[norm_tag(fm)].append(i)
    out = []
    for i, r in LEDGER_ROWS:
        if FORMS[i]["family"] != "PROPOSED":
            continue
        cited = {t[0] for t in row_tokens(i)}
        for alias in [a.strip() for a in r["Tag"].split("|")]:
            slug = norm_tag(alias[len("PROPOSED"):]) if alias.upper().startswith("PROPOSED") else ""
            if not slug:
                continue
            for j in printed.get(slug, []):
                hs = sorted([h for (k, s), v in hits_by.items() if k == j for h in v], key=read_key)
                on = [h for h in hs if h["Sheet"] in cited]
                tl = [h for h in on if h["Method"] == "text-layer"]
                ev = (tl or on or hs or [None])[0]
                if ev is None:
                    continue
                twin = (f"The same printed tag is the Tag of {LID[j]} ({LROW[j]['Lane']}). Decision A keeps both "
                        f"rows with their own IDs; whether they are one item is a Merge decision.")
                if tl:
                    tls = ", ".join(sorted({h["Sheet"] for h in tl}, key=X.sheet_sort_key))
                    reason = (f"The row's own designation \"{alias}\" is the printed tag \"{LROW[j]['Tag']}\", read "
                              f"in the native text layer on {tls}, which this row cites (read as "
                              f"\"{tl[0]['Tag Text']}\"). Proposed as the Ledger already spells it. {twin}")
                    out.append(["C", LID[i], r["Tag"], "Tag", r["Tag"], LROW[j]["Tag"], ev["Sheet"],
                                page_label(ev["Page Key"]), ev["BBox (pt)"], ev["Method"], "Verified", reason])
                else:
                    reason = (f"The row's own designation \"{alias}\" is the printed tag \"{LROW[j]['Tag']}\", read "
                              f"only by OCR or Bluebeam, or not on a sheet this row cites (Inferred). {twin}")
                    out.append(["C", LID[i], r["Tag"], "Tag", r["Tag"], "", ev["Sheet"], page_label(ev["Page Key"]),
                                ev["BBox (pt)"], ev["Method"], NEEDS_CHECK, reason])
            by_key = defaultdict(list)
            for (k, pk) in unm_norm.get(slug, []):
                by_key[k].append(pk)
            for k in sorted(by_key):
                occ = [(pk, unm_page[(k, pk)]) for pk in by_key[k]]
                on = [(pk, e) for pk, e in occ if SMAP[pk]["01 Sheet"] in cited]
                tl = [(pk, e) for pk, e in on if e["by"]["text-layer"]]
                pk, e = min(tl or on or occ, key=lambda pe: (pe[1]["first"], pe[0]))
                sheets = ", ".join(f"{SMAP[p]['01 Sheet']} ({', '.join(m for m in METHOD_ORDER if x['by'][m])})"
                                   for p, x in sorted(occ, key=lambda pe: X.sheet_sort_key(SMAP[pe[0]]["01 Sheet"])))
                reason = (f"The row's own designation \"{alias}\" matches \"{e['text']}\" (Unmatched_Tags), read on "
                          f"{sheets}. The row cites {', '.join(sorted(cited, key=X.sheet_sort_key)) or 'no sheet'}.")
                if tl:
                    out.append(["C", LID[i], r["Tag"], "Tag", r["Tag"], e["text"], SMAP[pk]["01 Sheet"],
                                page_label(pk), fmt_box(e["first"][1]), "text-layer", "Verified", reason])
                else:
                    out.append(["C", LID[i], r["Tag"], "Tag", r["Tag"], "", SMAP[pk]["01 Sheet"], page_label(pk),
                                fmt_box(e["first"][1]), ", ".join(m for m in METHOD_ORDER if e["by"][m]),
                                NEEDS_CHECK, reason + " Inferred: check the page image and whether the text is the "
                                                      "item's tag."])
    return out


# ---------------------------------------------------------------- starter MTO (decision B)

SPOT_VV = {(r["Set Page"], r["BBox (pt)"]) for r in SPOT if r["Human Result"].strip() == "Verified-Visual"}


def read_level(q):
    if q["Method"] == "text-layer":
        return "Verified"
    if (q["Set Page"], q["BBox (pt)"]) in SPOT_VV:
        return "Verified-Visual"
    return "Inferred"


def group_reads(leads):
    """One printed callout can be read by OCR and by Bluebeam: reads of one page and unit are one callout when
    their boxes touch or overlap, or when they carry the same value in the same keyed-note entry."""
    parent = list(range(len(leads)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in itertools.combinations(range(len(leads)), 2):
        qa, qb = leads[a], leads[b]
        if (qa["Page Key"], qa["Unit"]) != (qb["Page Key"], qb["Unit"]):
            continue
        touch = X.edge_dist(box(qa["BBox (pt)"]), box(qb["BBox (pt)"])) == 0
        kn = bool(qa["Keyed Note"]) and qa["Keyed Note"].split(" ")[0] == qb["Keyed Note"].split(" ")[0] \
            and num_eq(qa["Value"], qb["Value"])
        if touch or kn:
            parent[find(a)] = find(b)
    groups = defaultdict(list)
    for a in range(len(leads)):
        groups[find(a)].append(leads[a])
    return [sorted(g, key=read_key) for g in groups.values()]


def kn_rows(sheet, n):
    return [i for i, _ in LEDGER_ROWS for (s, anchors, raw) in row_tokens(i) if s == sheet and n in kn_numbers(raw)]


def citing_rows(sheet):
    return sorted({i for i, _ in LEDGER_ROWS for t in row_tokens(i) if t[0] == sheet})


def has_qty(i, value, unit):
    return any(num_eq(v, value) and u == unit for v, u in name_quantities(LROW[i]["Name"]))


def nearest_hit(q):
    """The Tag_Hits entry Quantity_Hits named as the nearest tag (same page and form, closest box)."""
    qb = box(q["BBox (pt)"])
    cands = [h for h in HITS if h["Page Key"] == q["Page Key"] and h["Search Form"] == q["Nearest Tag"]]
    return min(cands, key=lambda h: (X.edge_dist(qb, box(h["BBox (pt)"])), h["BBox (pt)"])) if cands else None


def kn_of(g):
    labels = sorted({q["Keyed Note"] for q in g if q["Keyed Note"]})
    parsed = [KN_LABEL_RE.match(lb) for lb in labels]
    nums = {int(m.group(1)) for m in parsed if m}
    if len(nums) == 1:
        return nums.pop(), X.weakest([m.group(3) for m in parsed if m]), labels[0]
    return None


def tie_group(g, kn):
    """Ledger tie for one callout: keyed note, then a Name quantity on a cited sheet, then the nearest tag.
    Returns (rows, basis, tie level, keyed-note level applies)."""
    sheet, value, unit = g[0]["Sheet"], g[0]["Value"], g[0]["Unit"]
    if kn:
        cands = kn_rows(sheet, kn[0])
        if len(cands) == 1:
            return cands, f"keyed note {kn[0]} (Ledger Drawing Sheets anchor)", "Verified", True
        if cands:
            narrowed = [i for i in cands if has_qty(i, value, unit)]
            if len(narrowed) == 1:
                return narrowed, f"keyed note {kn[0]}; of {len(cands)} rows citing it, the Ledger Name holds " \
                                 f"{value} {unit}", "Verified", True
            return cands, f"keyed note {kn[0]}; ambiguous: {len(cands)} rows cite it", "Unresolved", True
    cands = [i for i in citing_rows(sheet) if has_qty(i, value, unit)]
    if len(cands) == 1:
        return cands, f"cited sheet {sheet}; the Ledger Name holds {value} {unit}", "Verified", False
    if cands:
        return cands, f"cited sheet {sheet}; ambiguous: {len(cands)} Ledger Names hold {value} {unit}", \
            "Unresolved", False
    near = sorted({i for q in g if not q["Nearest Tag Ledger Rows"].startswith("ambiguous")
                   for i in rows_of(q["Nearest Tag Ledger Rows"])})
    if len(near) == 1:
        lined = any(q["Nearest Tag"] != "none" and nearest_hit(q) and same_line(
            box(q["BBox (pt)"]), box(nearest_hit(q)["BBox (pt)"])) for q in g)
        dist = min(float(q["Distance (pt)"]) for q in g if q["Distance (pt)"])
        return near, (f"nearest tag {g[0]['Nearest Tag']} within 24 pt ({dist:.2f} pt"
                      + ("; same text line)" if lined else ")")), "Verified" if lined else "Inferred", False
    if near:
        return near, "nearest tag; ambiguous", "Unresolved", False
    return [], "", "", False


def count_noun_ok(g, rows):
    """A count read from "N <plural noun>" is kept only when the tied Ledger Name names that noun."""
    q = g[0]
    if q["Unit"] != "EA" or EXPLICIT_EA_RE.search(q["Raw Text"].upper()):
        return True
    noun = X.stem(q["Item"].upper())
    return all(noun in name_words(LROW[i]["Name"]) for i in rows)


def best_line(g):
    return sorted(g, key=lambda q: (-len(q["Line Text"]), METHOD_ORDER[q["Method"]], q["Line Text"]))[0]["Line Text"]


def new_row_for(g):
    for pk, unit, word, tag, name in NEW_ROWS:
        q = g[0]
        if q["Page Key"] == pk and q["Unit"] == unit and re.search(
                rf"\b{word}\s*=\s*{re.escape(q['Value'])}\s*{unit}\b", best_line(g).upper()):
            return tag, name
    return None


def kn_entry_box(pk, n):
    for blk in PAGES[pk].get("keyed_notes", []):
        for e in blk["entries"]:
            if e["number"] == n:
                return e["bbox"]
    return None


def build_mto():
    leads = [q for q in QTY if q["Unit"] in MTO_UNITS and PILOT_SHEET_RE.match(q["Sheet"])]
    stats = Counter(leads=len(leads))
    stats["superseded"] = sum(1 for q in leads if SMAP[q["Page Key"]]["Governed By"])
    leads = [q for q in leads if not SMAP[q["Page Key"]]["Governed By"]]
    groups = sorted(group_reads(leads), key=lambda g: (X.sheet_sort_key(g[0]["Sheet"]), g[0]["Page Key"],
                                                       box(g[0]["BBox (pt)"])[1], box(g[0]["BBox (pt)"])[0]))
    stats["callouts"] = len(groups)
    lines, held = [], []
    for g in groups:
        values = sorted({q["Value"] for q in g}, key=float)
        kn = kn_of(g)
        best = min((read_level(q) for q in g), key=X.LEVELS.index)
        entry = {"g": g, "kn": kn, "read": best, "new": None}
        if len(values) > 1:
            held.append((g, "reads disagree on the value: " + ", ".join(values)))
            continue
        nr = new_row_for(g)
        if nr:
            entry.update(rows=[], basis=f"new row needed: no Ledger row for this quantity; proposed as \"{nr[0]}\" "
                                        "in New_Row_Candidates.csv (owner's decision)",
                         tie_level="", kn_applies=False, conf=best, new=nr, bid=EARTHWORK_BID)
            lines.append(entry)
            continue
        rows, basis, tie_level, kn_applies = tie_group(g, kn)
        if not rows:
            held.append((g, "no Ledger tie: no keyed-note anchor, no Ledger Name quantity on a cited sheet, "
                            "no tag within 24 pt"))
            continue
        if not count_noun_ok(g, rows):
            held.append((g, f"count noun \"{g[0]['Item']}\" is not named in the tied Ledger row "
                            f"({', '.join(LID[i] for i in rows)}); not a counted item"))
            continue
        levels = [best, tie_level] + ([kn[1]] if kn_applies else [])
        entry.update(rows=rows, basis=basis, tie_level=tie_level, kn_applies=kn_applies, conf=X.weakest(levels),
                     bid="; ".join(sorted({LROW[i]["Bid Item"] for i in rows})))
        lines.append(entry)
    return lines, held, stats


def mto_rows(lines):
    mto, checks = [], []
    for n, e in enumerate(lines, start=1):
        g, rows, kn = e["g"], e["rows"], e["kn"]
        q = g[0]
        pk = q["Page Key"]
        e["line"] = n
        ready = "Y" if e["conf"] in ("Verified", "Verified-Visual") else "N"
        ids = "; ".join(LID[i] for i in rows)
        item = best_line(g) if not e["new"] else f"{e['new'][1]}: {best_line(g)}"
        cite = f"{q['Sheet']}" + (f" Keyed Note {kn[0]}" if kn else "") + f", {page_cite(pk)}"
        if rows:
            cite += "; " + "; ".join(f"{LID[i]} Drawing Sheets \"{LROW[i]['Drawing Sheets']}\"" for i in rows)
        else:
            cite += "; bid item per index/04_Bid_Item_Spine.md (Item 1: work not itemized elsewhere)"
        methods = "; ".join(sorted({x["Method"] for x in g}, key=METHOD_ORDER.get))
        mto.append([n, ids, item, q["Value"], q["Unit"], q["Sheet"], page_label(pk), q["BBox (pt)"],
                    kn[2] if kn else "", methods, e["conf"], ready, cite, e["bid"], e["basis"]])
        if ready == "Y":
            continue
        why = []
        if e["read"] == "Inferred":
            why.append("quantity read by OCR or Bluebeam only (Inferred)")
        if e.get("kn_applies") and kn[1] != "Verified":
            why.append(f"keyed-note number {kn[2]}")
        if e["tie_level"] == "Inferred":
            why.append("tie by distance only")
        if e["tie_level"] == "Unresolved":
            why.append("tie ambiguous: " + e["basis"])
        if e["new"]:
            why.append("no Ledger row yet (new row needed)")
        crop = [box(x["BBox (pt)"]) for x in g]
        if kn:
            eb = kn_entry_box(pk, kn[0])
            if eb:
                crop.append(eb)
        if e["basis"].startswith("nearest tag") and nearest_hit(q):
            crop.append(box(nearest_hit(q)["BBox (pt)"]))
        cb = pad(union(crop), PAGES[pk]["page"]["width"], PAGES[pk]["page"]["height"])
        reads = " | ".join(f"{x['Method']} {x['BBox (pt)']} \"{x['Raw Text']}\""
                           + (f" conf {x['Confidence']}" if x["Confidence"] else "") for x in g)
        owner = ("; ".join(f"{LID[i]} {LROW[i]['Name']}" for i in rows) if rows
                 else f"a new Ledger row \"{e['new'][0]}\"")
        what = (f"On {q['Sheet']} ({page_cite(pk)}), inside the crop box: does the drawing read {q['Value']} "
                f"{q['Unit']} for \"{best_line(g)}\"" + (f", in keyed note {kn[0]}" if kn else "")
                + f"? Does it belong to {owner}?")
        checks.append({"type": "MTO line", "line": n, "ids": ids, "item": item, "qty": q["Value"], "unit": q["Unit"],
                       "sheet": q["Sheet"], "pk": pk, "kn": kn[2] if kn else "", "conf": e["conf"],
                       "why": "; ".join(why), "crop": cb, "reads": reads, "what": what,
                       "marks": [box(x["BBox (pt)"]) for x in g]})
    return mto, checks


def panel_rows(panels):
    out = []
    for p in panels:
        i = p["i"]
        what = (f"On {p['sheet']} ({page_cite(p['pk'])}), inside the crop box: read the \"{p['title']}\" schedule "
                f"and check it against {LID[i]} {LROW[i]['Tag']}: Name \"{LROW[i]['Name']}\"; Notes on circuits, "
                "totals and SPD. Mark each fact Verified-Visual or note the difference.")
        out.append({"type": "panel schedule (owner's Division 26 review)", "line": "", "ids": LID[i],
                    "item": f"{p['title']} schedule (raster image; the text layer holds only the title)",
                    "qty": "", "unit": "", "sheet": p["sheet"], "pk": p["pk"], "kn": "",
                    "conf": LROW[i][TAG_COL],
                    "why": "Owner's Division 26 review: the schedule is an embedded image, so its contents can be "
                           "checked only on the page image (Verified-Visual)",
                    "crop": p["crop"],
                    "reads": f"text-layer {fmt_box(p['title_box'])} \"{p['title']}\" | image {fmt_box(p['image_box'])} "
                             f"{p['px'][0]}x{p['px'][1]} px",
                    "what": what, "marks": [p["title_box"]]})
    return out


def check_table(checks):
    return [[n, c["type"], c["line"], c["ids"], c["item"], c["qty"], c["unit"], c["sheet"], page_label(c["pk"]),
             native_page(c["pk"]), c["kn"], c["conf"], c["why"], fmt_box(c["crop"]), c["reads"], c["what"],
             "", "", "", ""] for n, c in enumerate(checks, start=1)]


def save_crops(checks, folder):
    from PIL import Image, ImageDraw
    folder.mkdir(parents=True, exist_ok=True)
    z = 200 / 72.0
    for n, c in enumerate(checks, start=1):
        pg = PAGES[c["pk"]]
        doc = _DOCS.setdefault(REPO / pg["source"]["file"], pymupdf.open(REPO / pg["source"]["file"]))
        page = doc[pg["source"]["page"] - 1]
        clip = pymupdf.Rect(c["crop"])          # displayed coordinates, as PyMuPDF renders a rotated page
        pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip, alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        d = ImageDraw.Draw(img)
        for b in c["marks"]:
            d.rectangle([(b[0] - clip.x0) * z - 3, (b[1] - clip.y0) * z - 3, (b[2] - clip.x0) * z + 3,
                         (b[3] - clip.y0) * z + 3], outline=(220, 0, 0), width=3)
        img.save(folder / f"check_{n:03d}_{c['sheet']}_{c['pk']}.png")


# ---------------------------------------------------------------- new-row candidates

def build_candidates(unm_page, lines):
    rows = []
    for e in lines:
        if not e["new"]:
            continue
        g = e["g"]
        c = Counter(q["Method"] for q in g)
        confs = [float(q["Confidence"]) for q in g if q["Confidence"]]
        rows.append(["proposed Ledger row (owner's decision)", e["new"][0], "", g[0]["Sheet"],
                     page_label(g[0]["Page Key"]), len(g), c["text-layer"], c["ocr"], c["bluebeam-ocr"],
                     f"{max(confs):.2f}" if confs else "", e["conf"], g[0]["BBox (pt)"], "", "", e["new"][1],
                     e["bid"], g[0]["Value"], g[0]["Unit"], e["line"]])
    by_tag_sheet = defaultdict(lambda: {"pks": [], "n": 0, "by": Counter(), "conf": None, "first": None})
    for (k, pk), e in sorted(unm_page.items()):
        c = by_tag_sheet[(k, SMAP[pk]["01 Sheet"])]
        c["pks"].append(pk)
        c["n"] += e["n"]
        c["by"].update(e["by"])
        if e["conf"] is not None:
            c["conf"] = e["conf"] if c["conf"] is None else max(c["conf"], e["conf"])
        first = (pk, e["first"][1])
        if c["first"] is None or first < c["first"]:
            c["first"] = first
    order = {r["Tag Text"].replace(" ", ""): n for n, r in enumerate(UNMATCHED)}
    unm_key = {r["Tag Text"].replace(" ", ""): r for r in UNMATCHED}
    for (k, s) in sorted(by_tag_sheet, key=lambda ks: (order[ks[0]], X.sheet_sort_key(ks[1]))):
        c = by_tag_sheet[(k, s)]
        u = unm_key[k]
        rows.append(["unmatched tag", u["Tag Text"], u["Shape"], s, "; ".join(page_label(p) for p in c["pks"]),
                     c["n"], c["by"]["text-layer"], c["by"]["ocr"], c["by"]["bluebeam-ocr"],
                     "" if c["conf"] is None else f"{c['conf']:.2f}",
                     "Verified" if c["by"]["text-layer"] else "Inferred", fmt_box(c["first"][1]),
                     u["Occurrences"], len(split_list(u["Sheets"])), "", "", "", "", ""])
    return [[n] + r for n, r in enumerate(rows, start=1)]


# ---------------------------------------------------------------- segment sums (Summary only, Inferred)

def segment_sums(lines, held):
    """Two callouts on a row's cited pilot sheet whose values add up to a quantity the Ledger Name states. At
    least one of them must be untied. Reported as Inferred leads; nothing is tied by this."""
    callouts = [(e["g"], e["rows"]) for e in lines if not e["new"]] + [(g, None) for g, _ in held]
    out = []
    for i, r in LEDGER_ROWS:
        for v, u in name_quantities(r["Name"]):
            if u not in MTO_UNITS:
                continue
            for sheet in sorted({t[0] for t in row_tokens(i)}, key=X.sheet_sort_key):
                pool = [(g, rows) for g, rows in callouts if g[0]["Sheet"] == sheet and g[0]["Unit"] == u]
                for k in (2,):
                    for combo in itertools.combinations(pool, k):
                        if any(rows is None for _, rows in combo) and \
                                abs(sum(float(g[0]["Value"]) for g, _ in combo) - float(v)) < 1e-9:
                            out.append((LID[i], r["Tag"], f"{v} {u}", sheet, " + ".join(
                                f"{g[0]['Value']} {u} ({'untied' if rows is None else 'tied to ' + '; '.join(LID[x] for x in rows)}; "
                                f"{g[0]['BBox (pt)']})" for g, rows in combo)))
    return out


# ---------------------------------------------------------------- Summary.md

def ev_label(sheets, pages):
    return "; ".join(s if s == p or p.startswith("main spec") else f"{s} (set p.{p})"
                     for s, p in zip(sheets.split("; "), pages.split("; ")))


def basis_kind(basis):
    for prefix, kind in (("keyed note", "keyed note"), ("cited sheet", "Ledger Name quantity on a cited sheet"),
                         ("nearest tag", "nearest tag"), ("new row needed", "new row needed")):
        if basis.startswith(prefix):
            return kind + (" (ambiguous)" if "ambiguous" in basis else "")
    return "other"


def summary(updates, mto, checks, held, stats, cands, sums):
    count = Counter((u[1], "Verified change" if u[11] == "Verified" else NEEDS_CHECK) for u in updates)
    ready = Counter(m[11] for m in mto)
    by_basis = Counter(basis_kind(m[14]) for m in mto)
    ctype = Counter(c[1] for c in checks)
    out = ["# Prompt 9 reconciliation: summary", "",
           "Proposal mode. Nothing here is applied to the Project Ledger or an MTO; the Ledger update is a later "
           "step the owner approves. Generated by `testbeds/eastsound/tools/build_reconciliation.py` from the OCR "
           "lane's outputs in `derived/ocr/` (method rules in README.md). Read levels follow AGENTS.md: a native "
           "text-layer read is Verified; OCR and Bluebeam reads are Inferred until a person marks them "
           "Verified-Visual.", "",
           "## Ledger IDs (decision A)", "",
           f"- {len(LEDGER_ROWS)} Ledger records get IDs L-0001 to L-{len(LEDGER_ROWS):04d}, in current row order. "
           "L-0001 is the first record, which the OCR crosswalk calls Ledger Row 2 (the header is row 1): "
           "**Ledger ID = L-(Ledger Row − 1)**. `Ledger_ID_Map.csv` lists every pair.",
           "- Rows 19 and 89 in the prompt (crosswalk numbering) are **L-0018** and **L-0088**.",
           f"- SD-1 stays two rows: {LID[74]} (storm drain, Civil & Site) and {LID[316]} (3 HP sludge pump, "
           "Electrical & Controls). Tags stay as printed.", "",
           "## Ledger_Update_Proposal.csv", ""]
    out += md_table(["Category", "Verified change", "Needs check", "Total"], [
        [CATEGORIES[k], count[(CATEGORIES[k], "Verified change")], count[(CATEGORIES[k], NEEDS_CHECK)],
         count[(CATEGORIES[k], "Verified change")] + count[(CATEGORIES[k], NEEDS_CHECK)]] for k in "ABCD"]
        + [["all", sum(v for (c, t), v in count.items() if t == "Verified change"),
            sum(v for (c, t), v in count.items() if t == NEEDS_CHECK), len(updates)]])
    out += ["", "A change is proposed only on Verified evidence (a native text-layer read). Inferred evidence and "
                "absences are listed as \"needs check\" with no proposed value. Off-citation short-form hits "
                "(234) and the one \"(E) not on line\" hit stay out, per the Gate A rules.", "",
            "Verified changes:", ""]
    out += md_table(["Proposal", "Ledger ID", "Tag", "Field", "Current", "Proposed", "Evidence"], [
        [u[0], u[2], u[3], u[4], u[5] if len(u[5]) <= 60 else u[5][:57] + "…",
         u[6] if len(u[6]) <= 70 else u[6][:67] + "…", ev_label(u[7], u[8])] for u in updates if u[11] == "Verified"])
    out += ["", "## Starter_MTO.csv (decision B: C0–C2 and C7)", "",
            f"- Quantity leads in LF, EA, CY, SF or SY on the pilot sheets: {stats['leads']}; on a base page Add. 4 "
            f"supersedes: {stats['superseded']} (left out).",
            f"- One printed callout read by both OCR and Bluebeam is one line. Callouts: {stats['callouts']}.",
            f"- MTO lines: {len(mto)} (Ready Y {ready['Y']}, Ready N {ready['N']}). Held out: {len(held)} "
            "(table below).",
            "- Lines by tie: " + "; ".join(f"{k} {v}" for k, v in sorted(by_basis.items())) + ".",
            "- Ready = Y only for Verified or Verified-Visual. Every other line is \"needs check\" and is in "
            "Needs_Check.csv.",
            f"- SD-1 ({LID[74]}) is three lines, 42 + 19 + 42 LF; the Ledger total is 103 LF (schema proposal: one "
            "total Quantity per row, segments in the MTO).",
            "- The C0.2 earthwork totals (cut 3382 CY, fill 1598 CY) are MTO lines with no Ledger ID, Bid Item 1 "
            "(Inferred) and \"new row needed\"; both are proposed rows in New_Row_Candidates.csv.", "",
            "## Needs_Check.csv", "",
            f"- {len(checks)} checks: " + "; ".join(f"{v} {k}" for k, v in sorted(ctype.items())) + ".",
            "- Each has a crop box in PDF points (as displayed, origin top left) on the named page. "
            "`--crops <folder>` renders them as PNGs outside the repo.",
            "- The E6.2 and E2.2 panel schedules are embedded images: the text layer holds only their titles, so "
            "their contents can be confirmed only by eye.", "",
            "## New_Row_Candidates.csv", "",
            f"- {sum(1 for c in cands if c[1].startswith('proposed'))} proposed Ledger rows (earthwork cut and fill, "
            "owner's decision).",
            f"- {len(UNMATCHED)} unmatched tags, {sum(1 for c in cands if c[1] == 'unmatched tag')} tag-and-sheet "
            f"rows, {sum(c[6] for c in cands if c[1] == 'unmatched tag')} reads; "
            f"{sum(1 for c in cands if c[1] == 'unmatched tag' and c[11] == 'Verified')} rows have a text-layer "
            "read. Candidates only: many are sizes, standards, model numbers or area names, not items.", "",
            "## RFI: generator rating (L-0242 GEN)", ""]
    gen = [u for u in updates if u[1] == CATEGORIES["D"] and u[2] == LID[243] and u[4] == "Notes"][0]
    out += [f"- Evidence ({gen[0]}), native text layer, Verified: "
            + gen[12].split("Native text layer: ", 1)[1].rstrip(".") + ". Boxes: "
            + "; ".join(f"{w} {b}" for w, b in zip(gen[7].split("; "), gen[9].split("; "))) + ".",
            "- Spec: 26 32 13 ¶2.03 C.1 (main spec p.326): \"Power Output Ratings: Electrical output power rating for "
            "Standby operation of not less than 150.0kW, at 80 percent lagging power factor, 277/480\". Verified.",
            "- Question for the Engineer: the drawings show a 125 kW / 156 kVA standby generator; 26 32 13 ¶2.03 C.1 "
            "requires not less than 150.0 kW standby. Which rating governs, and do the generator breaker (250/3), "
            "feeder (P-GEN) and pad change with it?",
            "- Proposal: L-0242 keeps Unresolved; the RFI is appended to its Notes. Precedence between drawings and "
            "specifications was not checked (Unresolved: not read in this step).", "",
            "## Chain link fence: for the owner's decision (not resolved)", ""]
    fence = []
    for e in [x for x in held if x[0][0]["Sheet"] in ("C2.1",) and "CHAIN" in best_line(x[0]).upper()]:
        g = e[0]
        fence.append(["C2.1", kn_of(g)[2] if kn_of(g) else "", f"{g[0]['Value']} {g[0]['Unit']}", best_line(g),
                      "; ".join(q["Method"] for q in g), g[0]["BBox (pt)"], "none (held out of the MTO)"])
    for m in mto:
        if "CHAIN" in m[2].upper():
            fence.append([m[5], m[8], f"{m[3]} {m[4]}", m[2], m[9], m[7], f"{m[1]} (MTO line {m[0]}, {m[10]})"])
    fence.sort(key=lambda f: (X.sheet_sort_key(f[0]), f[1]))
    out += md_table(["Sheet", "Keyed note", "Quantity", "Read", "Method", "BBox (pt)", "Ledger"], fence)
    out += ["",
            f"- {LID[19]} \"{LROW[19]['Name']}\" cites {LROW[19]['Drawing Sheets']}.",
            f"- {LID[89]} \"{LROW[89]['Name']}\" cites {LROW[89]['Drawing Sheets']}.",
            "- Questions: (1) Are C2.1 keyed notes 6 (149 LF) and 8 (134 LF) new 6' fence runs separate from C2.5 "
            f"keyed note 4 (126 LF)? (2) Does {LID[89]} (126 LF, cites C2.5 and C2.1) cover them, or does each need "
            f"its own row? (3) Is the new 149 LF run on C2.1 the line of the 149 LF removed under C0.5 keyed note 16 "
            f"({LID[19]})? All reads here are OCR or Bluebeam (Inferred); C0.5's block count disagrees with its "
            "highest marker, so its by-order numbers are Unresolved.", "",
            "## Held quantity leads (not in the MTO)", ""]
    out += md_table(["Sheet", "Page", "Quantity", "Read", "Method", "BBox (pt)", "Why held"], [
        [g[0]["Sheet"], page_label(g[0]["Page Key"]), f"{g[0]['Value']} {g[0]['Unit']}", best_line(g)[:70],
         "; ".join(q["Method"] for q in g), g[0]["BBox (pt)"], why] for g, why in held])
    out += ["", "## Segment sums (Inferred leads, nothing tied)", "",
            "Two callouts on a cited sheet whose values add up to a quantity the Ledger Name states, at least one of "
            "them untied. Arithmetic only (Inferred); a person decides."] + [""]
    out += md_table(["Ledger ID", "Tag", "Ledger Name quantity", "Sheet", "Callouts"], sums) if sums else ["None."]
    out += ["", "## Division 26 review items (owner, 2026-09-30)", "",
            "Each evidence line was re-read from the native text layer (Part 3, Add. 4, main spec) on this run; the "
            "boxes are in the proposals.", ""]
    out += md_table(["Proposal", "Ledger ID", "Tag", "Field", "Proposed"], [
        [u[0], u[2], u[3], u[4], u[6] if len(u[6]) <= 80 else "… " + u[6][-77:]] for u in updates if u[1] == CATEGORIES["D"]])
    out += ["", "- L-0240 MDP, L-0264 LP-1 and L-0298 LP2: panel schedule boxes on E6.2 (and E2.2 for LP1) are in "
                "Needs_Check.csv.",
            "- TS, T3 and T2 rows: their Notes still say \"Status New inferred\" (and TS: G3 grounding \"by context "
            "(Inferred)\"). A row's tag is the weakest of its facts, so Verified holds only if those are accepted too; "
            "each proposal says so.",
            "- ATS: Add. 4 cites \"Bid Item #18\" for the temporary generator; the base bid form's Item 18 is Train 3 "
            "stainless steel (04). Add. 4 governs as the later document; the row goes to Inferred, not Verified.", "",
            "## Open decisions for the owner", "",
            "1. Chain link fence (above).",
            "2. Generator rating RFI (above).",
            f"3. {LID[338]} PROPOSED-Hot-Box-1 and {LID[339]} PROPOSED-Hot-Box-2 carry the printed tags of "
            f"{LID[58]} and {LID[59]}: keep both rows (decision A) or merge (Merge role).",
            "4. Ledger schema rev1 and the checks.py Tag-uniqueness rule (Ledger_Schema_rev1_Proposal.md).",
            "5. C2.3 callouts 20, 39 and 44 LF are untied; see Segment sums for how they may add up to SD-2 and SD-3.",
            "", "## Tie-outs", ""]
    out += md_table(["Check", "Result", "Detail"], TIES)
    out += ["", "## Inputs (SHA-256)", ""]
    out += md_table(["File", "SHA-256"], [[p.relative_to(REPO).as_posix(), X.sha256_file(p)] for p in INPUTS])
    return out


# ---------------------------------------------------------------- run

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="output folder (default: derived/reconciliation)")
    ap.add_argument("--crops", default="", help="also render each Needs_Check crop as a PNG here (outside the repo)")
    args = ap.parse_args()
    out = Path(args.out).resolve()
    check_sources()

    tie("Ledger rows = crosswalk rows", len(LEDGER_ROWS) == len(XW) and all(
        XW[i]["Tag"] == r["Tag"] for i, r in LEDGER_ROWS), f"{len(LEDGER_ROWS)} Ledger records, {len(XW)} crosswalk rows")
    unm_page = unmatched_by_page()
    unm_tot = Counter()
    for (k, pk), e in unm_page.items():
        unm_tot[k] += e["n"]
    keys = {r["Tag Text"].replace(" ", ""): int(r["Occurrences"]) for r in UNMATCHED}
    bad = [k for k in set(keys) | set(unm_tot) if keys.get(k) != unm_tot.get(k)]
    tie("Unmatched reads by page and method = Unmatched_Tags Occurrences", not bad,
        f"{len(keys)} tags, {sum(unm_tot.values())} reads, {len(bad)} mismatched")
    unm_norm = defaultdict(list)
    for (k, pk) in sorted(unm_page):
        unm_norm[norm_tag(k)].append((k, pk))
    hits_by = hits_by_row_sheet()
    mis = [i for i, x in XW.items()
           if {s for (j, s) in hits_by if j == i} != set(found_sheets(x["Sheets Found On"]))]
    tie("Found sheets from Tag_Hits = crosswalk Sheets Found On", not mis, f"{len(XW)} rows, {len(mis)} mismatched")

    updates = category_a(hits_by) + category_b(unm_page, unm_norm) + category_c(hits_by, unm_page, unm_norm) \
        + build_div26()
    updates.sort(key=lambda u: (u[0], int(u[1][2:]), X.sheet_sort_key(u[6].split(";")[0]), u[3], u[7]))
    updates = [[f"P-{n:04d}", CATEGORIES[u[0]]] + u[1:] for n, u in enumerate(updates, start=1)]
    lines, held, stats = build_mto()
    mto, checks = mto_rows(lines)
    checks += panel_rows(panel_checks())
    cands = build_candidates(unm_page, lines)
    sums = segment_sums(lines, held)

    pairs_a = sum(len(split_list(x["Sheets Found but Not Cited"])) for x in XW.values())
    pairs_b = sum(len(split_list(x["Sheets Cited but Not Found"])) for x in XW.values())
    got = Counter(u[1] for u in updates)
    tie("Found-not-cited proposals = crosswalk Sheets Found but Not Cited", got[CATEGORIES["A"]] == pairs_a,
        f"{got[CATEGORIES['A']]} proposals, {pairs_a} row-sheet pairs in "
        f"{sum(1 for x in XW.values() if x['Sheets Found but Not Cited'])} rows")
    tie("Cited-not-found proposals = crosswalk Sheets Cited but Not Found", got[CATEGORIES["B"]] == pairs_b,
        f"{got[CATEGORIES['B']]} proposals, {pairs_b} row-sheet pairs in "
        f"{sum(1 for x in XW.values() if x['Sheets Cited but Not Found'])} rows")
    tie("Every proposal cites evidence", all(u[7] and u[10] and u[12] and (u[9] or u[10].startswith(("none read",
                                                                                                        "sheet not")))
                                             for u in updates), f"{len(updates)} proposals")
    tie("Every Verified proposal rests on a text-layer read and has a proposed value",
        all(u[6] and "text-layer" in u[10] for u in updates if u[11] == "Verified"),
        f"{sum(1 for u in updates if u[11] == 'Verified')} Verified")
    tie("No change proposed on Inferred evidence", all(not u[6] for u in updates if u[11] != "Verified"),
        f"{sum(1 for u in updates if u[11] != 'Verified')} needs-check rows carry no proposed value")
    tie("New-row candidates cover the unmatched tags", {c[2].replace(" ", "") for c in cands if c[1] == "unmatched tag"}
        == set(keys) and sum(c[6] for c in cands if c[1] == "unmatched tag") == sum(keys.values()),
        f"{len(keys)} tags, {sum(1 for c in cands if c[1] == 'unmatched tag')} tag-sheet rows")
    tie("MTO callouts = lines + held", len(lines) + len(held) == stats["callouts"],
        f"{stats['callouts']} callouts, {len(lines)} lines, {len(held)} held")
    tie("Needs_Check holds every MTO line not Ready", sum(1 for c in checks if c["type"] == "MTO line")
        == sum(1 for m in mto if m[11] == "N"), f"{sum(1 for m in mto if m[11] == 'N')} lines not Ready")
    tie("Every MTO line with no Ledger ID is a new-row line", all(m[1] or m[14].startswith("new row needed")
                                                                  for m in mto), f"{len(mto)} lines")
    if FAILS:
        sys.exit("Stopped: tie-out failed, nothing written:\n  " + "\n  ".join(FAILS))

    files = {
        "Ledger_ID_Map.csv": csv_text(ID_HEADER, [[LID[i], i, r["Tag"], r["Name"], r["Lane"]] for i, r in LEDGER_ROWS]),
        "Ledger_Update_Proposal.csv": csv_text(UPDATE_HEADER, updates),
        "Starter_MTO.csv": csv_text(MTO_HEADER, mto),
        "Needs_Check.csv": csv_text(CHECK_HEADER, check_table(checks)),
        "New_Row_Candidates.csv": csv_text(CANDIDATE_HEADER, cands),
        "Summary.md": "\n".join(summary(updates, mto, check_table(checks), held, stats, cands, sums)).rstrip("\n")
        + "\n",
    }
    out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (out / name).write_bytes(text.encode("utf-8"))
    if args.crops:
        save_crops(checks, Path(args.crops).resolve())
    print(f"wrote {len(files)} files to {out}: {len(updates)} proposals, {len(mto)} MTO lines, "
          f"{len(checks)} checks, {len(cands)} candidates")


if __name__ == "__main__":
    main()
