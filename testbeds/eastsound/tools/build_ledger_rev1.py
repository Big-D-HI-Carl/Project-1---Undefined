#!/usr/bin/env python3
"""Project Ledger rev1: the expanded MTO (Prompt 10). One row per component; the columns run left to right
from "what and where" to everything connected to it.

Inputs (read-only):
  project/02_Project_Ledger/Project_Ledger.csv          rev0, 447 rows (kept whole; rev0 files are not touched)
  project/02_Project_Ledger/Project_Ledger_by_CWP.csv   CWP per row (the by-CWP rules, "CWP Rules" tab)
  project/01_Project_Wiki/Project_Wiki.md               note bodies (candidate test) and link targets
  project/03_Exceptions_and_Issues/Exception_Report.md  exception numbers -> lines
  project/04_Submittals_ITP_QC/Submittal_Register.csv, Inspection_Test_Plan.csv
  project/05_Schedule_and_Tracker/Installation_Tracker_by_CWP.csv, Schedule_by_CWP.csv
  derived/reconciliation/Ledger_ID_Map.csv, New_Row_Candidates.csv   (Prompt 9)
  derived/ocr/                                          via build_reconciliation.py (Tag_Hits, Quantity_Hits, ...)
  derived/wiki/Wiki_Notes.csv, Wiki_Links.csv
  derived/issues/Open_Items.csv
  tools/build_reconciliation.py is imported for the Prompt 9 MTO tie rules; it is not run. No library file is
  opened.

Outputs (project/02_Project_Ledger/, new files only):
  Project_Ledger_rev1.csv     the Ledger, in index/Ledger_Schema_rev1.csv columns
  Project_Ledger_rev1.xlsx    tabs Ledger, MTO Lines, Coverage, Candidates, Column Guide, Links
  MTO_Lines_rev1.csv          the MTO lines (machine copy of the MTO Lines tab; the graph build reads it)
  Ledger_rev1_Summary.md      fill rate per band before and after, new rows, candidates, totals, tie-outs

No LLM calls. Rows and lines are sorted, the xlsx is written with the standard library (fixed zip dates),
line endings are LF and files are UTF-8 without a BOM, so two runs give identical bytes. The run stops,
writing nothing, if a tie-out fails.

Run from the repo root with the packages pinned in requirements.txt installed:
  python testbeds/eastsound/tools/build_ledger_rev1.py [--out <folder>]
"""

import os
import sys

# build_reconciliation.py (and the extractor it imports) pin these and re-execute if they are missing.
if os.environ.get("PYTHONHASHSEED") != "0" or os.environ.get("OMP_THREAD_LIMIT") != "1":
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["OMP_THREAD_LIMIT"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)

import argparse
import csv
import hashlib
import importlib.util
import io
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
TB = HERE.parent
REPO = TB.parents[1]
_spec = importlib.util.spec_from_file_location("build_reconciliation", HERE / "build_reconciliation.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)
X = R.X

PROJECT = TB / "project"
LEDGER_DIR = PROJECT / "02_Project_Ledger"
LEDGER = LEDGER_DIR / "Project_Ledger.csv"
BY_CWP = LEDGER_DIR / "Project_Ledger_by_CWP.csv"
WIKI = PROJECT / "01_Project_Wiki" / "Project_Wiki.md"
EXCEPTIONS = PROJECT / "03_Exceptions_and_Issues" / "Exception_Report.md"
SUBMITTALS = PROJECT / "04_Submittals_ITP_QC" / "Submittal_Register.csv"
ITP = PROJECT / "04_Submittals_ITP_QC" / "Inspection_Test_Plan.csv"
TRACKER = PROJECT / "05_Schedule_and_Tracker" / "Installation_Tracker_by_CWP.csv"
SCHEDULE = PROJECT / "05_Schedule_and_Tracker" / "Schedule_by_CWP.csv"
ID_MAP = TB / "derived" / "reconciliation" / "Ledger_ID_Map.csv"
NEW_CANDIDATES = TB / "derived" / "reconciliation" / "New_Row_Candidates.csv"
WIKI_NOTES = TB / "derived" / "wiki" / "Wiki_Notes.csv"
WIKI_LINKS = TB / "derived" / "wiki" / "Wiki_Links.csv"
OPEN_ITEMS = TB / "derived" / "issues" / "Open_Items.csv"
SCHEMA_REV1 = TB / "index" / "Ledger_Schema_rev1.csv"
LIB_REL = "testbeds/eastsound/library/"
REPO_URL = "https://github.com/Big-D-HI-Carl/Project-1---Undefined/blob/main/"  # repo links for now
OUT_DEFAULT = LEDGER_DIR

TAG_COL0 = "Verified/Verified-Visual/Inferred/Unresolved"   # rev0 tag column
STRONG = ("Verified", "Verified-Visual")
LEVEL_RE = re.compile(r"\b(Verified-Visual|Verified|Inferred|Unresolved)\b")
SPEC_RE = re.compile(r"^(\d{2}) ?(\d{2}) ?(\d{2})\b")
SHEET_RE = re.compile(r"^([A-Z]{1,2}\d{1,2}\.\d{1,2}[A-Z]?)\b")
OI_ID = re.compile(r"\bOI-\d{4}\b")
EXC_RE = re.compile(r"\[Merge\] Exceptions?: ([^|]*?)\.?(?:\s*$|\s*\|)")
LID_RE = re.compile(r"\bL-\d{4}\b")
ANCHOR_BOX_RE = re.compile(r"; (\w+) ([\d.]+,[\d.]+,[\d.]+,[\d.]+)$")
CONTROL_SHEET_RE = re.compile(r"^E(7\.\d|8\.\d|9\.\d)$")   # E7.0-E9.3: PLC, control panel and MCC wiring sheets

# ---------------------------------------------------------------- the rev1 columns, in bands

BANDS = [
    ("A", "Identity", ["Ledger ID", "Tag", "Name", "Discipline", "Lane", "Area/Building", "Status"]),
    ("B", "Where", ["Drawing Sheets", "Found On", "CWP", "CWP Name", "Bid Item"]),
    ("C", "How much", ["Quantity", "Unit", "MTO Line IDs", "Quantity Confidence"]),
    ("D", "Specs & notes", ["Spec Sections", "Wiki Note(s)"]),
    ("E", "Submittals", ["Submittal Count", "Submittal IDs", "Submittal Link Basis", "Submittal Req (Y/N)"]),
    ("F", "Inspections & tests", ["Inspection/Test Count", "Inspection/Test IDs", "Inspection/Test Link Basis",
                                  "Testing/Startup Req (Y/N)"]),
    ("G", "Changes & issues", ["Addenda", "RFI IDs", "Conflict/Gap Count", "Conflict/Gap IDs", "Exception Refs"]),
    ("H", "Schedule & status", ["Schedule Activity", "Planned Start", "Planned Finish", "Submittal Approve-by",
                                "Tracker Status"]),
    ("I", "Confidence & source", ["Confidence", "Source Citation", "Notes"]),
]
HEADER = [c for _, _, cols in BANDS for c in cols]
BAND_OF = {c: (code, name) for code, name, cols in BANDS for c in cols}
# rev1 column -> the rev0 column it carries (for the "before" fill rate)
REV0_OF = {"Tag": "Tag", "Name": "Name", "Discipline": "Discipline", "Lane": "Lane", "Area/Building": "Area/Building",
           "Status": "Status", "Drawing Sheets": "Drawing Sheets", "Bid Item": "Bid Item",
           "Spec Sections": "Spec Sections", "Wiki Note(s)": "Wiki Note(s)",
           "Submittal Req (Y/N)": "Submittal Req (Y/N)", "Testing/Startup Req (Y/N)": "Testing/Startup Req (Y/N)",
           "Addenda": "Addenda", "Confidence": TAG_COL0, "Source Citation": "Source Citation", "Notes": "Notes"}
LINK_COLS = ["Drawing Sheets", "Found On", "MTO Line IDs", "Spec Sections", "Wiki Note(s)", "Submittal IDs",
             "Inspection/Test IDs", "Addenda", "RFI IDs", "Conflict/Gap IDs", "Exception Refs", "Schedule Activity"]
BASIS_COLS = ["Found On", "MTO Line IDs", "Wiki Note(s)", "Submittal IDs", "Inspection/Test IDs", "RFI IDs",
              "Conflict/Gap IDs", "Exception Refs"]   # cells whose every link names its basis
NONE_FOUND = "None found"
NOT_LINKED = "Not linked"
BASES = ("tag", "spec", "sheet")

MTO_HEADER = ["MTO Line ID", "Ledger ID", "Tag", "Row Status", "Line Type", "Item", "Quantity", "Unit", "Sheet", "Set Page",
              "BBox (pt)", "Keyed Note", "Method", "Confidence", "Counts To Total (Y/N)", "Not Totaled Because",
              "Link Basis", "Tie Basis", "Bid Item", "Source Citation"]
CAND_HEADER = ["Candidate No.", "Source", "Tag Text", "Proposed Name", "Sheets", "First Read (sheet, set page, box)",
               "Read Level", "(a) Page", "(b) CWP", "(c) Connected Document", "Category", "Decision", "Reason",
               "Ledger ID"]

# CWP rules (Project_Ledger_by_CWP.xlsx, "CWP Rules" tab), applied in order to a new row.
LEGACY_SPEC = {"02 83 00": "32", "02 92 00": "32", "15 08 13": "01", "15 40 00": "22"}
# Rule 4 keywords: the (discipline, keyword) pairs the by-CWP view used, plus "earthwork" from the name of
# CWP 31 (Earthwork, Dewatering & Erosion Control) for the owner's earthwork rows.
CWP_KEYWORDS = [("remove", "02"), ("sump", "03"), ("signs", "10"), ("bollard", "32"), ("striping", "32"),
                ("walkway", "32"), ("drain", "33"), ("piping", "33"), ("septic", "33"), ("valve label markers", "33"),
                ("header", "33"), ("stub", "33"), ("line", "33"), ("hot box", "43"), ("2w", "43"), ("feed", "46"),
                ("hypochlorite", "46"), ("solenoid", "46"), ("splitter", "46"), ("sampler", "46"),
                ("earthwork", "31")]
CWP_DISCIPLINE = {"Electrical": "26", "Controls": "26"}

# Candidate categories that are never added as rows (Prompt 10 rule 1), checked in this order. Each is a
# pattern on the printed text, with or without a sheet condition, and the reason written in the Candidates tab.
NEVER_ADD = [
    ("I/O point or control-wiring designation", lambda t, sh: bool(sh) and all(CONTROL_SHEET_RE.match(s) for s in sh),
     "read only on the PLC, control-panel and MCC wiring sheets (E7.0-E9.3): an I/O point, relay, terminal or "
     "nameplate designation inside a panel that has its own row"),
    ("area", lambda t, sh: re.fullmatch(r"(TRAIN|TRIAN|CELL|ZONE|BASIN|PLANT|AND|ONE|TWO|UNIT|ELEV)[#-]?\d+", t),
     "an area, train, cell, zone or elevation label, not a component"),
    ("standard, rating or model", lambda t, sh: re.fullmatch(
        r"[ACF]-?\d{2,3}|NAD83|NGVD29|IP\d\d|RS\d{3}|CAT\d|H-?20|R-?\d{2,3}|KW\d+|SET-\d\w*|CM2|M1[0O]|SD1|"
        r"[WL]\d{1,2}|C\d{3}|B-\d+|YR-\d{4}|[A-Z]{1,2}\d{3}|H2S", t),
     "a standard or rating (ASTM grade, datum, enclosure or network rating, loading class, R-value, steel shape, "
     "BMP code, design year), a manufacturer model number (W400, SC200) or a measured gas (H2S), not a component"),
    ("drawing reference or short label", lambda t, sh: re.fullmatch(
        r"DWG-\d+|NOTE#\d+|[A-Z]\d{1,2}|[A-Z]{2}\d{1,2}[A-Z]?|TB-\d+", t),
     "a drawing, detail or note reference, or a short letter-number label (conduit, setpoint, legend or note "
     "number) that names no component"),
]


# ---------------------------------------------------------------- small helpers

def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_csv_lines(path):
    """[(file line of the record, record)]; quoted cells may wrap."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        out = []
        while True:
            line = reader.line_num + 1
            rec = next(reader, None)
            if rec is None:
                break
            out.append((line, dict(zip(header, rec))))
    return out


def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def rel(p):
    return Path(p).resolve().relative_to(REPO).as_posix()


def url_of(path, anchor=""):
    return REPO_URL + quote(path) + anchor


def split_outside(cell, seps=";"):
    out, buf, depth = [], "", 0
    for ch in cell or "":
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch in seps and depth == 0:
            out.append(buf)
            buf = ""
        else:
            buf += ch
    out.append(buf)
    return [" ".join(v.split()) for v in out if v.strip()]


def specs_of(cell):
    out = []
    for v in split_outside(cell, ";,"):
        m = SPEC_RE.match(v)
        key = f"{m.group(1)} {m.group(2)} {m.group(3)}" if m else (
            re.match(r"Appendix [A-Z]\b", v).group(0) if re.match(r"Appendix [A-Z]\b", v) else "")
        if key and key not in out:
            out.append(key)
    return out


def sheets_of(cell):
    out = []
    for v in split_outside(cell, ";,"):
        m = SHEET_RE.match(v.strip().upper())
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out


def level_word(text):
    m = LEVEL_RE.search(text or "")
    return m.group(1) if m else ""


def weakest(levels):
    return X.weakest([lv for lv in levels if lv])


def num(v):
    f = float(v)
    return int(f) if f == int(f) else round(f, 2)


def fmt_num(v):
    return str(num(v))


def sheet_key(s):
    return X.sheet_sort_key(s)


def lid_num(lid):
    return int(lid[2:])


def filled(col, value):
    """A cell carries information: not blank, not a "none" marker, not a zero count or all-zero basis."""
    v = str(value).strip()
    if not v or v in ("—", "-", "–", "0") or v.startswith((NONE_FOUND, NOT_LINKED, "Not stated", "Not totaled",
                                                           "None", "Not scheduled")):
        return False
    if col.endswith("Link Basis") and re.fullmatch(r"tag 0; spec 0; sheet 0", v):
        return False
    return True


# ---------------------------------------------------------------- inputs

TIES, FAILS = [], []


def tie(name, ok, detail):
    TIES.append((name, "pass" if ok else "FAIL", detail))
    if not ok:
        FAILS.append(f"{name}: {detail}")


INPUT_FILES = [LEDGER, BY_CWP, WIKI, EXCEPTIONS, SUBMITTALS, ITP, TRACKER, SCHEDULE, ID_MAP, NEW_CANDIDATES,
               WIKI_NOTES, WIKI_LINKS, OPEN_ITEMS, HERE / "build_reconciliation.py", R.EXTRACTOR] + [
    R.OCR / n for n in ("Ledger_Crosswalk.csv", "Tag_Hits.csv", "Quantity_Hits.csv", "Unmatched_Tags.csv",
                        "Sheet_Map.csv", "Spot_Check.csv", "Tag_Search_Forms.csv")]

LROWS = R.LEDGER_ROWS                       # [(Ledger Row, rev0 record)]
LROW = R.LROW
LID = R.LID                                 # Ledger Row -> Ledger ID
ROW_OF = {v: k for k, v in LID.items()}     # Ledger ID -> Ledger Row
SMAP = R.SMAP
XW = R.XW
FORMS = R.FORMS
WIKI_LINES = WIKI.read_text(encoding="utf-8").split("\n")
NOTES = {r["Note ID"]: r for r in read_csv(WIKI_NOTES)}
WLINKS = read_csv(WIKI_LINKS)
OPEN = read_csv_lines(OPEN_ITEMS)
SUBS = read_csv_lines(SUBMITTALS)
ITPS = read_csv_lines(ITP)
TRACK = read_csv_lines(TRACKER)
SCHED = read_csv_lines(SCHEDULE)
CWPV = read_csv(BY_CWP)
CWP_NAME = {r["CWP"]: r["CWP Name"] for r in CWPV}


def note_body(nid):
    """Note body from Project_Wiki.md, from its heading line to the next level 1-3 heading."""
    n = NOTES.get(nid)
    if not n or not n["Heading Line"].isdigit():
        return ""
    out = []
    for line in WIKI_LINES[int(n["Heading Line"]):]:
        if re.match(r"^#{1,3} ", line):
            break
        out.append(line)
    return "\n".join(out)


NOTE_BODIES = {nid: note_body(nid) for nid in NOTES}


def exception_lines():
    out = {}
    for n, line in enumerate(EXCEPTIONS.read_text(encoding="utf-8").split("\n"), start=1):
        m = re.match(r"^\| (\d+) \|", line)
        if m:
            out.setdefault(int(m.group(1)), n)
    return out


EXC_LINE = exception_lines()

# ---------------------------------------------------------------- link targets (repo links for now)

SHEET_PAGE = {}     # sheet -> (file, page, label): the governing page (Add. 4 reissue when it governs)
for _pk in sorted(SMAP):
    _sm = SMAP[_pk]
    _s = _sm["01 Sheet"]
    _gov = _sm["Native File"] == "addendum-no4-eswd.pdf"
    if _s not in SHEET_PAGE or _gov:
        SHEET_PAGE[_s] = (_sm["Native File"], int(_sm["Native Page"]),
                          f"Add. 4 p.{_sm['Native Page']}" if _gov else
                          f"set p.{_sm['Set Page']}, {X.PART_SHORT.get(_sm['Native File'], _sm['Native File'])} "
                          f"p.{_sm['Native Page']}")
WIKI_REL = rel(WIKI)


def sheet_link(s):
    if s in SHEET_PAGE:
        f, p, label = SHEET_PAGE[s]
        return url_of(LIB_REL + f, f"#page={p}"), label
    return url_of("testbeds/eastsound/index/01_Sheet_Index_rev2.md"), "not in the plan set; see 01"


def note_link(nid):
    n = NOTES.get(nid)
    if n and n["Heading Line"].isdigit():
        return url_of(WIKI_REL, f"?plain=1#L{n['Heading Line']}"), f"Project Wiki line {n['Heading Line']}"
    return url_of(WIKI_REL), "no Wiki note by this ID"


def spec_link(sp):
    if sp in NOTES:
        return note_link(sp)
    return url_of(LIB_REL + "eswd-wwtp-upgrade-phase-i-specs.pdf"), "main spec"


def csv_line_link(path, line):
    return url_of(rel(path), f"?plain=1#L{line}")


# ---------------------------------------------------------------- CWP rule for a new row

def cwp_for(specs, siblings, temporary, text, discipline):
    """(CWP, basis, level) by the by-CWP rules 1-5; None when only rule 6 (parked in CWP 01) would apply."""
    for sp in specs:
        div = LEGACY_SPEC.get(sp, sp[:2]) if SPEC_RE.match(sp) else ""
        if div and "02" <= sp[:2] <= "46":
            cwp = f"CWP {div}"
            if cwp in CWP_NAME:
                return cwp, f"Spec {sp} (first technical section cited)", "Verified"
    if siblings:
        cwps = [(lid_num(s), CWPOF[s]) for s in siblings if s in CWPOF]
        if cwps:
            cwp = sorted(cwps)[0][1]
            return cwp, ("Same-item group: " + ", ".join(sorted(siblings, key=lid_num)) + " (Inferred)"), "Inferred"
    if temporary:
        return "CWP 01", "Temporary item; no technical section cited", "Inferred"
    low = text.lower()
    for kw, div in CWP_KEYWORDS:
        if re.search(rf"(?<![a-z0-9]){re.escape(kw)}(?![a-z0-9])", low):
            return f"CWP {div}", f"Discipline {discipline} + keyword \"{kw}\" (Inferred)", "Inferred"
    if discipline in CWP_DISCIPLINE:
        return f"CWP {CWP_DISCIPLINE[discipline]}", f"Discipline {discipline} (Inferred)", "Inferred"
    return None


CWPOF = {}       # Ledger ID -> CWP (filled for base rows below)
EARTHWORK_FLAGS = {}   # new earthwork Tag -> notes that keep its MTO line out of the total

# ---------------------------------------------------------------- base rows

def base_rows():
    idmap = read_csv(ID_MAP)
    tie("Ledger_ID_Map.csv = Project_Ledger.csv", len(idmap) == len(LROWS) and all(
        m["Ledger ID"] == LID[i] and m["Tag"] == r["Tag"] and int(m["Ledger Row"]) == i
        for m, (i, r) in zip(idmap, LROWS)), f"{len(idmap)} IDs, {len(LROWS)} Ledger rows")
    cwp = {(r["Tag"], r["Name"], r["Lane"], r["Area/Building"]): r for r in CWPV}
    rows = []
    for i, r in LROWS:
        lid = LID[i]
        c = cwp.get((r["Tag"], r["Name"], r["Lane"], r["Area/Building"]))
        row = {k: v for k, v in r.items()}
        row.update({"_lid": lid, "_line": i, "_new": False, "_rev0": r,
                    "_sheets": [s for s, _, _ in X.split_sheets(r["Drawing Sheets"]) if s],
                    "_specs": specs_of(r["Spec Sections"]), "_cwp_basis": c["CWP Basis"] if c else ""})
        row["Ledger ID"] = lid
        row["CWP"], row["CWP Name"] = (c["CWP"], c["CWP Name"]) if c else ("", "")
        CWPOF[lid] = row["CWP"]
        rows.append(row)
    tie("Every base row has its by-CWP assignment", all(r["CWP"] for r in rows),
        f"{sum(1 for r in rows if r['CWP'])} of {len(rows)} rows matched on Tag, Name, Lane and Area/Building")
    return rows


# ---------------------------------------------------------------- Found On

def best_per_sheet(hits):
    by = defaultdict(list)
    for h in hits:
        by[h["Sheet"]].append(h)
    return [(s, sorted(by[s], key=R.read_key)) for s in sorted(by, key=sheet_key)]


def page_tag(pk):
    sm = SMAP[pk]
    return f"p.{sm['Set Page']}" if sm["Set Page"] else f"Add. 4 p.{sm['Native Page']}"


def superseded(pk):
    return bool(SMAP[pk]["Governed By"])


def hit_entry(sheet, hs, cited, basis):
    h = hs[0]
    more = len(hs) - 1
    flags = []
    if superseded(h["Page Key"]):
        flags.append(f"base page superseded by {SMAP[h['Page Key']]['Governed By'].replace('addendum-no4-eswd.pdf', 'Add. 4')}")
    if sheet not in cited:
        flags.append("sheet not cited")
    label = (f"{sheet} {page_tag(h['Page Key'])} [{h['BBox (pt)']}] {h['Method']}"
             + (f" (+{more} read{'s' if more > 1 else ''})" if more else "")
             + (f" — {', '.join(flags)}" if flags else ""))
    return {"label": label, "basis": basis, "sheet": sheet, "pk": h["Page Key"], "level": R.read_level(h)}


def found_on(row, hits_for):
    """Tag reads assigned to the row (tag), or for PROPOSED rows the boxed Drawing Sheets anchors (sheet)."""
    if row["_new"]:
        return row["_found"]
    i = row["_line"]
    hits = hits_for.get(i, [])
    if hits:
        return [hit_entry(s, hs, row["_sheets"], "tag") for s, hs in best_per_sheet(hits)]
    x = XW[i]
    out = []
    if x["Family"] == "PROPOSED":
        for seg in [s for s in x["Anchor Check"].split(" | ") if s]:
            m = ANCHOR_BOX_RE.search(seg)
            if not m or "matched" not in seg or m.group(1) not in SMAP:
                continue
            sheet = seg.split(" ", 1)[0].rstrip(":")
            what = seg[:m.start()].replace("; ", ", ")
            out.append({"label": f"{sheet} {page_tag(m.group(1))} [{m.group(2)}] anchor: {what}",
                        "basis": "sheet", "sheet": sheet, "pk": m.group(1),
                        "level": weakest(LEVEL_RE.findall(seg)) or "Inferred"})
        return out
    return []


def hits_by_row():
    by = defaultdict(list)
    for h in R.HITS:
        if h["Assignment"] == "assigned":
            for i in R.rows_of(h["Ledger Rows"]):
                by[i].append(h)
    return by


# ---------------------------------------------------------------- MTO

def range_parts(tag):
    """'F1–F4 [2W Pump Station]' -> (['F1', 'F2', 'F3', 'F4'], '2W Pump Station'); not a range -> ([], '')."""
    forms, _, is_range = X.printed_forms(tag)
    m = re.search(r"[\[(]([^\])]+)[\])]\s*$", tag)
    return (forms, m.group(1).strip() if m else "") if is_range else ([], "")


def individual_rows(members, qual, rows):
    """A member's own row: Tag '<member> (<qualifier>)', or another tag in the same Area/Building whose Name
    names the member (LSH-111 "2W float F1", OI-0153). Range rows themselves are skipped."""
    out = {}
    for r in sorted(rows, key=lambda r: lid_num(r["_lid"])):
        if range_parts(r["Tag"])[0]:
            continue
        m = re.fullmatch(r"(\S+) \((.+)\)", r["Tag"])
        if m and m.group(1) in members and m.group(2).strip() == qual:
            out.setdefault(m.group(1), r["_lid"])
            continue
        if r["Area/Building"].strip().lower() == qual.lower():
            for f in members:
                if re.search(rf"(?<![A-Za-z0-9-]){re.escape(f)}(?![A-Za-z0-9-])", r["Name"]):
                    out.setdefault(f, r["_lid"])
    return out


def callout_lines():
    """The Prompt 9 starter-MTO rules (leads, one callout one line, keyed note / Name quantity / nearest tag,
    count nouns, weakest confidence, Add. 4 governs) run on every sheet, not just the civil pilot."""
    R.PILOT_SHEET_RE = re.compile(r".*")
    lines, held, stats = R.build_mto()
    return lines, held, stats


def build_mto(rows, hits_for, dup_pairs):
    by_lid = {r["_lid"]: r for r in rows}
    clines, held, stats = callout_lines()
    mto = []
    for e in clines:
        g, q = e["g"], e["g"][0]
        pk = q["Page Key"]
        kn = e["kn"]
        if e["new"]:
            lids = [r["_lid"] for r in rows if r["_new"] and r["Tag"] == e["new"][0]]
            tieb = f"new row in rev1 ({', '.join(lids)}); owner's decision on the C0.2 earthwork totals" \
                if lids else e["basis"]
            basis = "tag"
        else:
            lids = [LID[i] for i in e["rows"]]
            tieb = e["basis"]
            basis = "tag" if tieb.startswith("nearest tag") else "sheet"
        cite = f"{q['Sheet']}" + (f" Keyed Note {kn[0]}" if kn else "") + f", {R.page_cite(pk)}"
        mto.append({"type": "callout", "lids": lids, "item": R.best_line(g) if not e["new"] else
                    f"{e['new'][1]}: {R.best_line(g)}", "qty": q["Value"], "unit": q["Unit"], "sheet": q["Sheet"],
                    "pk": pk, "box": q["BBox (pt)"], "kn": kn[2] if kn else "",
                    "method": "; ".join(sorted({x["Method"] for x in g}, key=R.METHOD_ORDER.get)),
                    "conf": e["conf"], "basis": basis, "tie": tieb, "bid": e["bid"], "cite": cite, "why": []})
    # Tag-count lines: one EA per tagged component found on one of its cited sheets (Prompt 10 rule 4).
    for r in rows:
        tag = r["Tag"]
        fam = X.family(tag)
        if fam == "PROPOSED" or fam == "Pipe ID":
            continue
        cited = r["_sheets"]
        if r["_new"]:
            hits = r["_hits"]
        else:
            hits = [h for h in hits_for.get(r["_line"], [])]
        members, qual = range_parts(tag)
        per_form = defaultdict(list)
        for h in hits:
            if h["Sheet"] in cited and not superseded(h["Page Key"]):
                per_form[X.norm_form(h["Search Form"])].append(h)
        if members:
            own = individual_rows(members, qual, rows)
            forms = [f for f in members if f not in own]
            r["_range_note"] = ("range row; members with their own rows: "
                                + (", ".join(f"{f} {own[f]}" for f in members if f in own) or "none"))
        else:
            forms = sorted(per_form)
            if len(forms) > 1:      # aliases of one tag ("DO #1 | DO-1"): one component
                forms = [sorted(forms, key=lambda f: R.read_key(sorted(per_form[f], key=R.read_key)[0]))[0]]
                per_form = {forms[0]: sorted((h for hs in per_form.values() for h in hs), key=R.read_key)}
        for f in forms:
            hs = sorted(per_form.get(X.norm_form(f), []), key=R.read_key)
            if not hs:
                continue
            h = hs[0]
            mto.append({"type": "tag count", "lids": [r["_lid"]], "item": f"tag {h['Tag Text']} read on {h['Sheet']}",
                        "qty": "1", "unit": "EA", "sheet": h["Sheet"], "pk": h["Page Key"], "box": h["BBox (pt)"],
                        "kn": "", "method": h["Method"], "conf": R.read_level(h), "basis": "tag",
                        "tie": f"tag {f} found on cited sheet {h['Sheet']} ({len(hs)} read(s) on cited sheets; "
                               f"best read kept)",
                        "bid": r["Bid Item"], "cite": f"{h['Sheet']}, {R.page_cite(h['Page Key'])}; "
                                                     f"{r['_lid']} Drawing Sheets \"{r['Drawing Sheets']}\"",
                        "why": []})
    for m in mto:
        if m["type"] == "callout" and len(m["lids"]) == 1 and ROWS_BY_LID[m["lids"][0]]["Tag"] in EARTHWORK_FLAGS:
            for flag in EARTHWORK_FLAGS[ROWS_BY_LID[m["lids"][0]]["Tag"]]:
                m["why"].append(flag)
                if "reads" in flag:
                    m["conf"] = "Unresolved"
    # No double counting (Add. 4 already governs inside the callout rules).
    measured = defaultdict(set)
    for m in mto:
        if m["type"] == "callout":
            for lid in m["lids"]:
                measured[lid].add(m["unit"])
    for m in mto:
        lid = m["lids"][0] if len(m["lids"]) == 1 else ""
        if m["type"] == "tag count":
            r = by_lid[lid]
            nq = [u for _, u in R.name_quantities(r["Name"]) if u in R.MTO_UNITS]
            if measured[lid]:
                m["why"].append(f"the row has callout lines in {', '.join(sorted(measured[lid]))}; the tag count "
                                "would count the same item twice")
            elif nq:
                m["why"].append(f"the Ledger Name states the quantity in {', '.join(sorted(set(nq)))}; a tag count "
                                "is not the row's quantity")
    seen = {}
    for m in sorted(mto, key=lambda m: (sheet_key(m["sheet"]), m["pk"])):
        if m["type"] != "callout" or len(m["lids"]) != 1:
            continue
        key = (m["lids"][0], m["qty"], m["unit"])
        if key in seen and seen[key]["sheet"] != m["sheet"]:
            m["why"].append(f"same value and unit for this row as the line on {seen[key]['sheet']}; likely the "
                            "same run drawn twice")
        seen.setdefault(key, m)
    # Duplicate rows named by an open "duplicate" item: the lower Ledger ID keeps the count.
    totaled = {m["lids"][0] for m in mto if len(m["lids"]) == 1 and not m["why"] and m["conf"] in STRONG}
    for a, b, oi in dup_pairs:
        if a in totaled and b in totaled:
            for m in mto:
                if m["lids"] == [b] and not m["why"]:
                    m["why"].append(f"duplicate of {a} per {oi}; counted once, on {a}")
    for m in mto:
        if len(m["lids"]) > 1:
            m["why"].append("tie ambiguous: " + m["tie"])
        if m["conf"] not in STRONG:
            m["why"].append(f"{m['conf']} line; totals use Verified lines only")
        m["counts"] = "Y" if not m["why"] else "N"
    mto.sort(key=lambda m: (min(lid_num(x) for x in m["lids"]) if m["lids"] else 99999, m["type"] != "callout",
                            sheet_key(m["sheet"]), m["pk"], R.box(m["box"])[1], R.box(m["box"])[0]))
    for n, m in enumerate(mto, start=1):
        m["id"] = f"MTO-{n:04d}"
    return mto, held, stats


def dup_pairs_from_open():
    """Open duplicate items that name exactly two Ledger IDs: the two rows are one component. Items naming
    three or more IDs don't say which rows pair up (OI-0005 names Hot Box #1 and #2 and their PROPOSED twins),
    so they are only checked and reported (dup_groups)."""
    out = []
    for _, o in OPEN:
        ids = sorted(set(LID_RE.findall(o["Ledger IDs"])), key=lid_num)
        if o["Type"].lower() == "duplicate" and len(ids) == 2:
            out.append((ids[0], ids[1], o["Item ID"]))
    return out


def dup_groups(mto):
    """Open duplicate items naming three or more IDs where two or more of the rows have a counted line."""
    counted = {m["lids"][0] for m in mto if m["counts"] == "Y"}
    out = []
    for _, o in OPEN:
        ids = sorted(set(LID_RE.findall(o["Ledger IDs"])), key=lid_num)
        if o["Type"].lower() == "duplicate" and len(ids) > 2 and len(counted & set(ids)) > 1:
            out.append((o["Item ID"], sorted(counted & set(ids), key=lid_num), o["Title"]))
    return out


# ---------------------------------------------------------------- new rows and candidates

def tag_pattern(t):
    """The printed text as written: a space may be added or dropped around "#" and "-" and between words, but
    the "#" or "-" itself must be there ("SD-1" does not match "SD1 = 0.51g")."""
    parts = re.findall(r"[A-Za-z]+|\d+|[#-]| ", t.strip())
    body = ""
    for p in parts:
        body += rf"\s?{re.escape(p)}\s?" if p in "#-" else r"\s?" if p == " " else re.escape(p)
    return re.compile(r"(?<![A-Za-z0-9.#-])" + body + r"(?![A-Za-z0-9]|\.\d|-\d)")


def wiki_naming(pattern):
    return sorted(nid for nid, body in NOTE_BODIES.items() if pattern.search(body))


def register_naming(pattern):
    return sorted({rec["Req ID"] for _, rec in SUBS + ITPS if pattern.search(rec["Item"])})


def ledger_variant(t, rows, sheets):
    """A Ledger row whose printed tag has the same letters and digits (a short one must also cite a sheet the
    text was read on), or ends with them and cites such a sheet (BOX#1 in HOT BOX#1)."""
    k = R.norm_tag(t)
    for r in rows:
        if X.family(r["Tag"]) != "printed":
            continue
        overlap = bool(set(sheets) & set(r["_sheets"]))
        for f in X.printed_forms(r["Tag"])[0]:
            nf = R.norm_tag(f)
            if (nf == k and (len(k) >= 4 or overlap)) or (len(k) >= 4 and nf.endswith(k) and overlap):
                return r["_lid"], r["Tag"]
    return None


def first_sheet_discipline(sheets):
    d = {"E": "Electrical", "C": "Civil", "S": "Structural", "A": "Architectural", "G": "General"}
    return d.get(sheets[0][0], "Not stated") if sheets else "Not stated"


TEST_WHY = {"a": "(a) no sheet read with set page and box", "b": "(b) no CWP by rules 1-5",
            "c": "(c) no Wiki note or register entry names it"}


def build_new_rows(rows, hits_for):
    """Candidates from Prompt 9 (earthwork, unmatched tags) and range members with no row; each one is added
    only when it passes the three-part test and is not a never-add category."""
    new, cands = [], []
    next_id = max(lid_num(r["_lid"]) for r in rows) + 1
    proposed_lines = R.NEW_ROWS
    nrc = read_csv(NEW_CANDIDATES)

    def add_row(fields):
        nonlocal next_id
        lid = f"L-{next_id:04d}"
        next_id += 1
        fields.update({"_lid": lid, "Ledger ID": lid, "_line": None, "_new": True, "_rev0": None})
        new.append(fields)
        CWPOF[lid] = fields["CWP"]
        return lid

    # 1. The owner's earthwork rows (C0.2 cut and fill totals).
    for pk, unit, word, tag, name in proposed_lines:
        c = next(x for x in nrc if x["Tag Text"] == tag)
        val = c["Quantity"]
        pat = re.compile(rf"(?i)\b{word}\s+(?:=\s*)?([\d,]+(?:\.\d+)?)\s*{unit}\b")
        notes, conflict, take_off = [], "", ""
        for nid, body in sorted(NOTE_BODIES.items()):
            m = pat.search(body)
            if m:
                notes.append(nid)
                said = m.group(1).replace(",", "")
                if float(said) != float(val):
                    conflict = (f"Wiki note {nid} reads {word.lower()} {m.group(1)} {unit} "
                                f"({level_word(body[m.end():m.end() + 400]) or 'level not stated'}); the Bluebeam "
                                f"read is {val} {unit}")
                if re.search(r"not for bidding or take-?off", body[m.start():m.start() + 600]):
                    take_off = (f"Wiki note {nid}: the drawing states the cut and fill are estimated for the TESC "
                                "narrative only, not for bidding or take-off")
        regs = []
        cw = cwp_for([], [], False, name, "Civil")
        test = {"a": f"{c['Sheet']} set p.{c['Pages']} [{c['First BBox (pt)']}] ({c['Read Level']}, Bluebeam read)",
                "b": f"{cw[0]} — {cw[1]}" if cw else "",
                "c": "; ".join([f"Wiki note {n}" for n in notes] + regs)}
        cand = {"src": "Prompt 9 proposed row (owner's decision)", "tag": tag, "name": name, "sheets": c["Sheet"],
                "first": test["a"], "level": c["Read Level"], "test": test, "cat": "", "lid": ""}
        if all(test.values()):
            note = notes[0]
            line = NOTES[note]["Heading Line"]
            EARTHWORK_FLAGS[tag] = [x for x in (conflict, take_off) if x]
            lid = add_row({
                "Tag": tag, "Name": name, "Discipline": "Civil", "Lane": "Civil & Site", "Area/Building": "Site",
                "Status": "New", "Drawing Sheets": c["Sheet"], "Bid Item": c["Bid Item"], "CWP": cw[0],
                "CWP Name": CWP_NAME[cw[0]], "_cwp_basis": cw[1], "Spec Sections": "",
                "Wiki Note(s)": note, "Submittal Req (Y/N)": "Not stated (new row)",
                "Testing/Startup Req (Y/N)": "Not stated (new row)", "Addenda": "",
                TAG_COL0: weakest([c["Read Level"], cw[2], "Verified"] + (["Unresolved"] if conflict else [])),
                "Source Citation": f"{c['Sheet']} set p.{c['Pages']} (Part 1 p.{c['Pages']}), Bluebeam read at "
                                   f"[{c['First BBox (pt)']}]: \"CUT = 3382 CY, FILL = 1598 CY\"; Wiki note {note} "
                                   f"(Project_Wiki.md line {line}); New_Row_Candidates.csv no. {c['Candidate No.']}",
                "Notes": f"[rev1] New row, Prompt 9 owner's decision (DECISIONS.md 2026-09-30, \"The C0.2 earthwork "
                         f"totals go in the starter MTO and are proposed as new Ledger rows\"). Three-part test: page "
                         f"{test['a']}; CWP {test['b']}; connected document {test['c']}. Quantity read by Bluebeam "
                         f"only (Inferred), so it is not totaled."
                         + (f" Unresolved: {conflict}; the page image decides." if conflict else "")
                         + (f" {take_off}." if take_off else ""),
                "_sheets": [c["Sheet"]], "_specs": [], "_found": [{
                    "label": f"{c['Sheet']} {page_tag(pk)} [{c['First BBox (pt)']}] bluebeam-ocr (quantity callout)",
                    "basis": "sheet", "sheet": c["Sheet"], "pk": pk, "level": c["Read Level"]}],
                "_hits": [], "_named_notes": notes, "_siblings": []})
            cand.update(decision="Added", reason="passes (a), (b) and (c)", lid=lid)
        else:
            cand.update(decision="Not added", cat="fails the three-part test",
                        reason="fails " + ", ".join(TEST_WHY[k] for k, v in test.items() if not v))
        cands.append(cand)

    # 2. Range members with no row of their own (e.g. floats F1 and F4 at the 2W pump station; OI-0475).
    for r in sorted(rows, key=lambda r: lid_num(r["_lid"])):
        members, qual = range_parts(r["Tag"])
        if not members or not qual:
            continue
        own = individual_rows(members, qual, rows + new)
        if not own:
            continue                 # no member has a row: the range row is the component (S1-S2)
        sibs = sorted(own.values(), key=lid_num)
        sib_rows = [x for x in rows if x["_lid"] in sibs]
        for f in members:
            if f in own:
                continue
            notes = sorted({w["Note ID"] for w in WLINKS if w["Target"] == f and w["Target Type"].startswith("equip")
                            and not w["Ledger ID"] and qual.lower() in (NOTES.get(w["Note ID"], {}).get("Title", "")
                                                                         .lower())})
            sheets = []
            for s in [n for n in notes if SHEET_RE.match(n)] + r["_sheets"] + [s for x in sib_rows for s in x["_sheets"]]:
                if s not in sheets:
                    sheets.append(s)
            hits = [h for h in R.HITS if X.norm_form(h["Search Form"]) == f and h["Sheet"] in sheets and (
                (h["Assignment"] == "assigned" and r["_line"] in R.rows_of(h["Ledger Rows"])) or
                (h["Assignment"] == "off-citation, short form" and r["_line"] in R.rows_of(h["Candidate Rows"])))]
            found = [hit_entry(s, hs, sheets, "tag") for s, hs in best_per_sheet(hits)]
            best = sorted(hits, key=R.read_key)[0] if hits else None
            disc = sib_rows[0]["Discipline"]
            cw = cwp_for([], sibs, False, f, disc)
            test = {"a": (f"{best['Sheet']} {page_tag(best['Page Key'])} [{best['BBox (pt)']}] "
                          f"({R.read_level(best)}, {best['Method']})") if best else "",
                    "b": f"{cw[0]} — {cw[1]}" if cw else "",
                    "c": "; ".join(f"Wiki note {n}" for n in notes)}
            tag = f"{f} ({qual})"
            name = f"{qual} float switch {f} (printed on the {qual} notes; the Ledger had {f} only for the other " \
                   f"station)" if "float" in r["Name"].lower() else f"{qual} {f}"
            cand = {"src": f"range member with no row ({r['_lid']} {r['Tag']}; OI-0475)", "tag": tag, "name": name,
                    "sheets": "; ".join(sheets), "first": test["a"],
                    "level": R.read_level(best) if best else "", "test": test, "cat": "", "lid": ""}
            if all(test.values()):
                lvl = weakest([R.read_level(best), cw[2]] + [w["Confidence"].capitalize() for w in WLINKS
                                                             if w["Target"] == f and w["Note ID"] in notes])
                lid = add_row({
                    "Tag": tag, "Name": name, "Discipline": disc, "Lane": sib_rows[0]["Lane"], "Area/Building": qual,
                    "Status": sib_rows[0]["Status"], "Drawing Sheets": "; ".join(sheets),
                    "Bid Item": f"{sib_rows[0]['Bid Item']} (Inferred: same as {', '.join(sibs)})",
                    "CWP": cw[0], "CWP Name": CWP_NAME[cw[0]], "_cwp_basis": cw[1], "Spec Sections": "",
                    "Wiki Note(s)": "; ".join(notes), "Submittal Req (Y/N)": "Not stated (new row)",
                    "Testing/Startup Req (Y/N)": "Not stated (new row)", "Addenda": "", TAG_COL0: lvl,
                    "Source Citation": "; ".join(e["label"] for e in found) + "; " + "; ".join(
                        f"Wiki note {n} (Project_Wiki.md line {NOTES[n]['Heading Line']})" for n in notes)
                                       + "; derived/issues/Open_Items.csv OI-0475",
                    "Notes": f"[rev1] New row: range member {f} of {r['_lid']} \"{r['Tag']}\" with no row of its own "
                             f"(siblings {', '.join(sibs)} have rows). Three-part test: page {test['a']}; CWP "
                             f"{test['b']}; connected document {test['c']}. Discipline, Lane, Status and Bid Item follow "
                             f"the siblings (Inferred). Closes the float part of OI-0475 once approved.",
                    "_sheets": sheets, "_specs": [], "_found": found, "_hits": hits, "_named_notes": notes,
                    "_siblings": sibs})
                cand.update(decision="Added", reason="passes (a), (b) and (c)", lid=lid)
            else:
                cand.update(decision="Not added", cat="fails the three-part test",
                            reason="fails " + ", ".join(TEST_WHY[k] for k, v in test.items() if not v))
            cands.append(cand)

    # 3. Unmatched tags (Prompt 9 New_Row_Candidates.csv, one candidate per tag).
    by_tag = defaultdict(list)
    for c in nrc:
        if c["Candidate Type"] == "unmatched tag":
            by_tag[c["Tag Text"]].append(c)
    order = [u["Tag Text"] for u in R.UNMATCHED]
    all_rows = rows + new
    for t in order:
        cs = sorted(by_tag[t], key=lambda c: sheet_key(c["Sheet"]))
        sheets = [c["Sheet"] for c in cs]
        best = sorted(cs, key=lambda c: (c["Read Level"] != "Verified", sheet_key(c["Sheet"])))[0]
        first = f"{best['Sheet']} {('p.' + best['Pages'].split('; ')[0]) if best['Pages'][:1].isdigit() else best['Pages'].split('; ')[0]} [{best['First BBox (pt)']}]"
        pat = tag_pattern(t)
        notes = wiki_naming(pat)
        regs = register_naming(pat)
        spec_notes = [n for n in notes if SPEC_RE.match(n)]
        disc = first_sheet_discipline(sheets)
        cw = cwp_for(spec_notes, [], False, t, disc)
        test = {"a": f"{first} ({best['Read Level']})",
                "b": f"{cw[0]} — {cw[1]}" if cw else "",
                "c": "; ".join([f"Wiki note {n}" for n in notes] + regs)}
        cat, why = "", ""
        var = ledger_variant(t, all_rows, sheets)
        for name, test_fn, reason in NEVER_ADD:
            if name == "drawing reference or short label" and var:
                cat, why = "variant of a Ledger tag", f"same letters and digits as {var[1]} ({var[0]}); the same " \
                                                      "component, so a new row would double count it"
                break
            if test_fn(t, sheets):
                cat, why = name, reason
                break
        if not cat and var:
            cat, why = "variant of a Ledger tag", f"same letters and digits as {var[1]} ({var[0]}); the same " \
                                                  "component, so a new row would double count it"
        if not cat and not (test["c"] and test["b"]):
            cat = "fails the three-part test"
            why = "fails " + "; ".join(TEST_WHY[k] + (" (rule 6 would only park it in CWP 01)" if k == "b" else "")
                                       for k in ("c", "b") if not test[k])
        if not cat:
            cat = "held for a person"
            why = ("passes the three-part test, but the documents name it as a conduit run, setpoint, label or "
                   "part of a component that has a row; a person decides whether it is a component")
        cands.append({"src": "Prompt 9 unmatched tag", "tag": t, "name": "", "sheets": "; ".join(sheets),
                      "first": test["a"], "level": best["Read Level"], "test": test, "cat": cat,
                      "decision": "Held" if cat == "held for a person" else "Not added", "reason": why, "lid": ""})
    return new, cands


# ---------------------------------------------------------------- links

def link(label, basis, url, item=None, level=""):
    return {"label": label, "basis": basis, "url": url, "item": item or label, "level": level}


def register_links(rows, recs, path):
    """Register lines -> rows. A line links to the rows whose printed tag its Item names (tag), to every row
    that cites one of its spec sections (spec: the requirement applies to the section), and, when it names no
    spec section, appendix or exhibit, to the rows that cite one of its sheets (sheet). Each pair keeps its
    strongest basis."""
    out = defaultdict(dict)
    printed = [(r, [R.norm_tag(f) for f in X.printed_forms(r["Tag"])[0]]) for r in rows
               if X.family(r["Tag"]) == "printed"]
    pats = {r["_lid"]: [tag_pattern(f) for f in X.printed_forms(r["Tag"])[0] if len(R.norm_tag(f)) >= 3]
            for r, _ in printed}
    for line, rec in recs:
        rid = rec["Req ID"]
        specs, sheets = specs_of(rec["Spec Sections"]), sheets_of(rec["Drawing Sheets"])
        names_doc = bool(rec["Spec Sections"].strip())     # a spec section, appendix or exhibit
        for r in rows:
            lid = r["_lid"]
            basis = ""
            if any(p.search(rec["Item"]) for p in pats.get(lid, [])):
                basis = "tag"
            elif specs and set(specs) & set(r["_specs"]):
                basis = "spec"
            elif not names_doc and sheets and set(sheets) & set(r["_sheets"]):
                basis = "sheet"
            if basis:
                out[lid][rid] = link(rid, basis, csv_line_link(path, line), level=level_word(rec[TAG_COL0]))
    return out


def open_item_links(rows, types):
    """Open items -> rows: the Ledger IDs an item names (tag); an item naming none links by its spec sections
    (spec), else by its sheets (sheet)."""
    out = defaultdict(dict)
    for line, o in OPEN:
        if o["Type"] not in types:
            continue
        ids = set(LID_RE.findall(o["Ledger IDs"]))
        specs, sheets = specs_of(o["Spec Sections"]), sheets_of(o["Sheets"])
        url = csv_line_link(OPEN_ITEMS, line)
        for r in rows:
            lid = r["_lid"]
            if ids:
                basis = "tag" if lid in ids else ""
            elif specs:
                basis = "spec" if set(specs) & set(r["_specs"]) else ""
            else:
                basis = "sheet" if sheets and set(sheets) & set(r["_sheets"]) else ""
            if basis:
                out[lid][o["Item ID"]] = link(o["Item ID"], basis, url, level=o["Confidence"])
    return out


def wiki_links(rows):
    """Wiki notes per row: notes that name the row (tag, Wiki_Links equipment links), notes for its spec
    sections (spec) and its sheets (sheet), plus the notes rev0 cited (spec or sheet by note type)."""
    named = defaultdict(set)
    for w in WLINKS:
        if w["Target Type"].startswith("equip"):
            for lid in LID_RE.findall(w["Ledger ID"]):
                named[lid].add(w["Note ID"])
    out = {}
    for r in rows:
        lid = r["_lid"]
        got = {}
        for n in sorted(set(named.get(lid, ())) | set(r.get("_named_notes", []))):
            got[n] = "tag"
        for sp in r["_specs"]:
            if sp in NOTES and sp not in got:
                got[sp] = "spec"
        for s in r["_sheets"]:
            if s in NOTES and s not in got:
                got[s] = "sheet"
        for n in split_outside(r["Wiki Note(s)"], ";"):
            n = re.sub(r"\s*\(.*\)$", "", n).strip()
            if n and n not in got:
                typ = NOTES.get(n, {}).get("Type", "")
                got[n] = "sheet" if typ.lower().startswith("drawing") else "spec"
        out[lid] = [link(n, b, note_link(n)[0], level="") for n, b in got.items()]
    return out


def ordered(links):
    """Direct (tag) links first, then spec, then sheet; the order within a basis is kept."""
    return sorted(links, key=lambda x: BASES.index(x["basis"]))


def cell(links, empty=NONE_FOUND):
    if not links:
        return empty
    return "; ".join(f"{x['label']} ({x['basis']})" for x in links)


def basis_counts(links):
    c = Counter(x["basis"] for x in links)
    return "; ".join(f"{b} {c[b]}" for b in BASES)


# ---------------------------------------------------------------- schedule

def schedule_info():
    track = {(t["Tag"], t["Item"], t["Lane"], t["Area/Building"]): (line, t) for line, t in TRACK}
    sched = {s["ID"]: (line, s) for line, s in SCHED}
    unsched = {}
    for line, s in SCHED:
        if s["Type"] == "Not scheduled":
            for t in [x.strip() for x in s["Ledger tags"].split(";") if x.strip()]:
                unsched[t] = (line, s)
    return track, sched, unsched


STEP_COLS = ["Submittal approved", "On site / ready", "Installed / removed", "Tested / inspected",
             "Turned over / closed"]


def tracker_status(t):
    done = [c for c in STEP_COLS if t[c].strip()]
    if not done:
        return "Not started (baseline: no progress entered)"
    return f"{done[-1]} {t[done[-1]].strip()}"


# ---------------------------------------------------------------- assemble the rows

def assemble(rows, mto, hits_for):
    subs = register_links(rows, SUBS, SUBMITTALS)
    itps = register_links(rows, ITPS, ITP)
    rfis = open_item_links(rows, {"RFI"})
    gaps = open_item_links(rows, {"conflict", "gap"})
    notes = wiki_links(rows)
    track, sched, unsched = schedule_info()
    mto_by = defaultdict(list)
    for m in mto:
        for lid in m["lids"]:
            mto_by[lid].append(m)
    out = []
    for r in rows:
        lid = r["_lid"]
        rev0 = r["_rev0"]
        L = {}
        # A Identity / B Where
        sheet_links = []
        for v in split_outside(r["Drawing Sheets"], ";"):
            m = SHEET_RE.match(v)
            if m:
                u, lab = sheet_link(m.group(1))
                sheet_links.append(link(m.group(1), "sheet", u, item=f"{v} — {lab}"))
        L["Drawing Sheets"] = sheet_links
        fo = found_on(r, hits_for)
        L["Found On"] = [link(e["label"], e["basis"], sheet_link(e["sheet"])[0] if e["sheet"] in SHEET_PAGE else
                              sheet_link(e["sheet"])[0], level=e["level"]) for e in fo]
        if r["_new"]:
            found_empty = NONE_FOUND
        elif XW[r["_line"]]["Family"] == "PROPOSED":
            found_empty = NOT_LINKED + " (PROPOSED tag is not printed; no boxed anchor matched)"
        else:
            found_empty = NONE_FOUND + " (tag searched on every page)"
        # C How much
        lines = mto_by.get(lid, [])
        L["MTO Line IDs"] = [link(m["id"], m["basis"], f"#'MTO Lines'!A{MTO_ROW[m['id']]}",
                                  item=f"{m['id']}: {m['qty']} {m['unit']} {m['sheet']} ({m['conf']}; "
                                       f"counts {m['counts']})", level=m["conf"]) for m in lines]
        tot = [m for m in lines if m["counts"] == "Y" and len(m["lids"]) == 1]
        units = sorted({m["unit"] for m in tot})
        if len(units) == 1:
            qty = fmt_num(sum(float(m["qty"]) for m in tot))
            unit = units[0]
            qconf = f"Verified — {len(tot)} line{'s' if len(tot) > 1 else ''} totaled" + (
                f"; {len(lines) - len(tot)} other line(s) not totaled" if len(lines) > len(tot) else "")
        elif len(units) > 1:
            qty, unit = "Not totaled: Verified lines in more than one unit", "; ".join(units)
            qconf = "Unresolved — " + qty
        elif lines:
            qty = "Not totaled: no Verified line"
            measured_lines = [m for m in lines if m["type"] == "callout"] or lines
            unit = "; ".join(sorted({m["unit"] for m in measured_lines}))
            levels = Counter(m["conf"] for m in lines)
            qconf = (f"{weakest([m['conf'] for m in measured_lines])} — not totaled; lines: "
                     + ", ".join(f"{levels[lv]} {lv}" for lv in X.LEVELS if levels[lv])
                     + " (MTO Lines: Not Totaled Because)")
        else:
            qty = unit = NONE_FOUND
            qconf = NONE_FOUND + (f" (rollup row: {r['_range_note']})" if r.get("_range_note") else
                                  " (no MTO line: no tied callout and no tag found on a cited sheet)")
        # D Specs & notes
        spec_links = []
        for v in split_outside(r["Spec Sections"], ";"):
            sp = specs_of(v)
            if sp:
                spec_links.append(link(sp[0], "spec", spec_link(sp[0])[0], item=v))
        L["Spec Sections"] = spec_links
        L["Wiki Note(s)"] = notes[lid]
        # E / F
        L["Submittal IDs"] = sorted(subs.get(lid, {}).values(), key=lambda x: x["label"])
        L["Inspection/Test IDs"] = sorted(itps.get(lid, {}).values(), key=lambda x: x["label"])
        # G
        add_links = []
        for v in split_outside(r["Addenda"], ";|"):
            if v in ("—", "-") or not v:
                continue
            pm = re.search(r"Add\. 4 p\.(\d+)", v)
            add_links.append(link(v, "tag", url_of(LIB_REL + "addendum-no4-eswd.pdf",
                                                   f"#page={pm.group(1)}" if pm else ""), item=v))
        L["Addenda"] = add_links
        L["RFI IDs"] = sorted(rfis.get(lid, {}).values(), key=lambda x: x["label"])
        L["Conflict/Gap IDs"] = sorted(gaps.get(lid, {}).values(), key=lambda x: x["label"])
        exc = []
        for m in EXC_RE.finditer(r["Notes"]):
            for n in re.findall(r"#(\d+)", m.group(1)):
                if int(n) in EXC_LINE and f"#{n}" not in [e["label"] for e in exc]:
                    exc.append(link(f"#{n}", "tag", url_of(rel(EXCEPTIONS), f"?plain=1#L{EXC_LINE[int(n)]}")))
        L["Exception Refs"] = exc
        # H
        sched_links = []
        if r["_new"]:
            act = start = finish = appr = NOT_LINKED + " (new row; the rev0 schedule predates it)"
            status = NOT_LINKED + " (new row; not in the rev0 tracker)"
        else:
            hit = track.get((rev0["Tag"], rev0["Name"], rev0["Lane"], rev0["Area/Building"]))
            if hit:
                tline, t = hit
                sline, s = sched.get(t["Schedule activity ID"], (None, None))
                act = f"{t['Schedule activity ID']} {t['Schedule activity']}"
                if sline:
                    sched_links.append(link(act, "tag", csv_line_link(SCHEDULE, sline)))
                start, finish = t["Planned start"] or NONE_FOUND, t["Planned finish"] or NONE_FOUND
                appr = t["Submittal approve-by"] or (NONE_FOUND + " (no submittal)")
                status = tracker_status(t)
            elif rev0["Tag"] in unsched:
                sline, s = unsched[rev0["Tag"]]
                act = f"{s['ID']} {s['Activity']}"
                sched_links.append(link(act, "tag", csv_line_link(SCHEDULE, sline)))
                start = finish = appr = f"Not scheduled ({s['Date basis']})"
                status = f"Not tracked ({s['Date basis']})"
            else:
                act = start = finish = appr = status = NOT_LINKED
        L["Schedule Activity"] = sched_links
        # order every link list: tag, then spec, then sheet
        for k in BASIS_COLS:
            L[k] = ordered(L[k])
        row = {
            "Ledger ID": lid, "Tag": r["Tag"], "Name": r["Name"], "Discipline": r["Discipline"], "Lane": r["Lane"],
            "Area/Building": r["Area/Building"], "Status": r["Status"],
            "Drawing Sheets": r["Drawing Sheets"].strip() if r["Drawing Sheets"].strip() not in ("", "—") else
            NONE_FOUND + (" (no sheet cited in rev0)" if not r["_new"] else ""),
            "Found On": cell(L["Found On"], found_empty), "CWP": r["CWP"], "CWP Name": r["CWP Name"],
            "Bid Item": r["Bid Item"],
            "Quantity": qty, "Unit": unit, "MTO Line IDs": cell(L["MTO Line IDs"], NONE_FOUND),
            "Quantity Confidence": qconf,
            "Spec Sections": r["Spec Sections"].strip() or NONE_FOUND + (" (no spec section cited in rev0)"
                                                                          if not r["_new"] else ""),
            "Wiki Note(s)": cell(L["Wiki Note(s)"]),
            "Submittal Count": len(L["Submittal IDs"]), "Submittal IDs": cell(L["Submittal IDs"]),
            "Submittal Link Basis": basis_counts(L["Submittal IDs"]),
            "Submittal Req (Y/N)": r["Submittal Req (Y/N)"],
            "Inspection/Test Count": len(L["Inspection/Test IDs"]), "Inspection/Test IDs": cell(L["Inspection/Test IDs"]),
            "Inspection/Test Link Basis": basis_counts(L["Inspection/Test IDs"]),
            "Testing/Startup Req (Y/N)": r["Testing/Startup Req (Y/N)"],
            "Addenda": r["Addenda"].strip() if r["Addenda"].strip() not in ("", "—") else
            NONE_FOUND + " (Add. 4 checked; Addenda 1-3 not staged)",
            "RFI IDs": cell(L["RFI IDs"]), "Conflict/Gap Count": len(L["Conflict/Gap IDs"]),
            "Conflict/Gap IDs": cell(L["Conflict/Gap IDs"]), "Exception Refs": cell(L["Exception Refs"]),
            "Schedule Activity": act, "Planned Start": start, "Planned Finish": finish, "Submittal Approve-by": appr,
            "Tracker Status": status,
            "Confidence": r[TAG_COL0], "Source Citation": r["Source Citation"],
            "Notes": r["Notes"].strip() or NONE_FOUND + " (no notes in rev0)",
            "_links": L, "_new": r["_new"], "_cwp_basis": r["_cwp_basis"],
        }
        out.append(row)
    return out


MTO_ROW = {}     # MTO line ID -> its row in the MTO Lines tab


# ---------------------------------------------------------------- xlsx (standard library writer)

def col_letter(n):
    s = ""
    while n:
        n, rem = divmod(n - 1, 26)
        s = chr(65 + rem) + s
    return s


ILLEGAL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def xml_text(v):
    v = ILLEGAL.sub("", str(v))
    return v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


BAND_DARK = ["1F4E79", "385723", "7F6000", "833C0B", "3A3838", "203864", "7030A0", "005B5B", "595959"]
BAND_LIGHT = ["DDEBF7", "E2EFDA", "FFF2CC", "FCE4D6", "EDEDED", "D9E1F2", "E4DFEC", "DDF2F2", "F2F2F2"]
# cellXfs: 0 default, 1 wrap, 2 link, 3 header plain, 4 title, 5.. band titles, 14.. band headers
S_WRAP, S_LINK, S_HEAD, S_TITLE, S_BAND, S_BHEAD = 1, 2, 3, 4, 5, 14


def styles_xml():
    fills = ['<fill><patternFill patternType="none"/></fill>', '<fill><patternFill patternType="gray125"/></fill>',
             '<fill><patternFill patternType="solid"><fgColor rgb="FFD9D9D9"/><bgColor indexed="64"/></patternFill></fill>']
    fills += [f'<fill><patternFill patternType="solid"><fgColor rgb="FF{c}"/><bgColor indexed="64"/></patternFill></fill>'
              for c in BAND_DARK + BAND_LIGHT]
    fonts = ['<font><sz val="10"/><name val="Calibri"/><family val="2"/></font>',
             '<font><b/><sz val="10"/><name val="Calibri"/><family val="2"/></font>',
             '<font><u/><sz val="10"/><color rgb="FF0563C1"/><name val="Calibri"/><family val="2"/></font>',
             '<font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Calibri"/><family val="2"/></font>',
             '<font><b/><sz val="12"/><name val="Calibri"/><family val="2"/></font>']
    top = '<alignment vertical="top" wrapText="1"/>'
    xfs = ['<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>',
           f'<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1">{top}</xf>',
           f'<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1">{top}</xf>',
           f'<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" '
           f'applyAlignment="1">{top}</xf>',
           '<xf numFmtId="0" fontId="4" fillId="0" borderId="0" xfId="0" applyFont="1"/>']
    xfs += [f'<xf numFmtId="0" fontId="3" fillId="{3 + i}" borderId="0" xfId="0" applyFont="1" applyFill="1" '
            f'applyAlignment="1"><alignment vertical="center"/></xf>' for i in range(9)]
    xfs += [f'<xf numFmtId="0" fontId="1" fillId="{12 + i}" borderId="0" xfId="0" applyFont="1" applyFill="1" '
            f'applyAlignment="1">{top}</xf>' for i in range(9)]
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<fonts count="{len(fonts)}">{"".join(fonts)}</fonts>'
            f'<fills count="{len(fills)}">{"".join(fills)}</fills>'
            '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
            '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
            f'<cellXfs count="{len(xfs)}">{"".join(xfs)}</cellXfs>'
            '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
            '</styleSheet>')


class Sheet:
    def __init__(self, name):
        self.name = name
        self.rows = []          # [[(value, style, link)]]
        self.widths = []
        self.levels = []        # outline level per column
        self.freeze = None      # (cols, rows)
        self.filter = None      # (first row, last row, ncols)
        self.merges = []

    def add(self, cells):
        self.rows.append(cells)


def sheet_xml(sh):
    rels, links, rid = {}, [], {}
    ncol = max(len(r) for r in sh.rows)
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
           'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">']
    if any(sh.levels):
        out.append('<sheetPr><outlinePr summaryBelow="0" summaryRight="0"/></sheetPr>')
    out.append(f'<dimension ref="A1:{col_letter(ncol)}{len(sh.rows)}"/>')
    if sh.freeze:
        c, r = sh.freeze
        tl = f"{col_letter(c + 1)}{r + 1}"
        pane = "bottomRight" if c and r else ("bottomLeft" if r else "topRight")
        attrs = (f' xSplit="{c}"' if c else "") + (f' ySplit="{r}"' if r else "")
        out.append(f'<sheetViews><sheetView workbookViewId="0"><pane{attrs} topLeftCell="{tl}" activePane="{pane}" '
                   f'state="frozen"/><selection pane="{pane}" activeCell="{tl}" sqref="{tl}"/></sheetView></sheetViews>')
    else:
        out.append('<sheetViews><sheetView workbookViewId="0"/></sheetViews>')
    out.append(f'<sheetFormatPr defaultRowHeight="13"{" outlineLevelCol=" + chr(34) + "1" + chr(34) if any(sh.levels) else ""}/>')
    out.append("<cols>")
    for i, w in enumerate(sh.widths, start=1):
        lv = sh.levels[i - 1] if i - 1 < len(sh.levels) else 0
        out.append(f'<col min="{i}" max="{i}" width="{w}" customWidth="1"' + (f' outlineLevel="{lv}"' if lv else "")
                   + "/>")
    out.append("</cols><sheetData>")
    for rn, cells in enumerate(sh.rows, start=1):
        out.append(f'<row r="{rn}">')
        for cn, (v, s, ln) in enumerate(cells, start=1):
            ref = f"{col_letter(cn)}{rn}"
            if v is None or v == "":
                if s:
                    out.append(f'<c r="{ref}" s="{s}"/>')
                continue
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out.append(f'<c r="{ref}" s="{s}"><v>{v}</v></c>')
            else:
                text = str(v)
                if len(text) > 32767:
                    raise SystemExit(f"Stopped: cell {sh.name}!{ref} is over 32,767 characters")
                out.append(f'<c r="{ref}" s="{s}" t="inlineStr"><is><t xml:space="preserve">{xml_text(text)}</t></is></c>')
            if ln:
                if ln.startswith("#"):
                    links.append(f'<hyperlink ref="{ref}" location="{xml_text(ln[1:])}" display="{xml_text(str(v))[:250]}"/>')
                else:
                    if ln not in rid:
                        rid[ln] = f"rId{len(rid) + 1}"
                        rels[rid[ln]] = ln
                    links.append(f'<hyperlink ref="{ref}" r:id="{rid[ln]}"/>')
        out.append("</row>")
    out.append("</sheetData>")
    if sh.filter:
        a, b, n = sh.filter
        out.append(f'<autoFilter ref="A{a}:{col_letter(n)}{b}"/>')
    if sh.merges:
        out.append(f'<mergeCells count="{len(sh.merges)}">' + "".join(f'<mergeCell ref="{m}"/>' for m in sh.merges)
                   + "</mergeCells>")
    if links:
        out.append("<hyperlinks>" + "".join(links) + "</hyperlinks>")
    out.append("</worksheet>")
    rel_xml = None
    if rels:
        rel_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(f'<Relationship Id="{k}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                             f'relationships/hyperlink" Target="{xml_text(v)}" TargetMode="External"/>'
                             for k, v in rels.items()) + "</Relationships>")
    return "".join(out), rel_xml


def write_xlsx(sheets):
    buf = io.BytesIO()
    names = [s.name for s in sheets]
    defined = "".join(
        f'<definedName name="_xlnm._FilterDatabase" localSheetId="{i}" hidden="1">\'{s.name}\'!$A${s.filter[0]}:'
        f'${col_letter(s.filter[2])}${s.filter[1]}</definedName>' for i, s in enumerate(sheets) if s.filter)
    files = [
        ("[Content_Types].xml",
         '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
         '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
         '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
         '<Default Extension="xml" ContentType="application/xml"/>'
         '<Override PartName="/xl/workbook.xml" '
         'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
         '<Override PartName="/xl/styles.xml" '
         'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
         + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
                   f'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                   for i in range(1, len(sheets) + 1)) + "</Types>"),
        ("_rels/.rels",
         '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
         'officeDocument" Target="xl/workbook.xml"/></Relationships>'),
        ("xl/workbook.xml",
         '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
         '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
         'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
         '<bookViews><workbookView activeTab="0"/></bookViews><sheets>'
         + "".join(f'<sheet name="{xml_text(n)}" sheetId="{i}" r:id="rId{i}"/>' for i, n in enumerate(names, start=1))
         + "</sheets>" + (f"<definedNames>{defined}</definedNames>" if defined else "") + "</workbook>"),
        ("xl/_rels/workbook.xml.rels",
         '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                   f'relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(sheets) + 1))
         + f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
           'relationships/styles" Target="styles.xml"/></Relationships>'),
        ("xl/styles.xml", styles_xml()),
    ]
    for i, s in enumerate(sheets, start=1):
        body, rels = sheet_xml(s)
        files.append((f"xl/worksheets/sheet{i}.xml", body))
        if rels:
            files.append((f"xl/worksheets/_rels/sheet{i}.xml.rels", rels))
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, text.encode("utf-8"), compresslevel=6)
    return buf.getvalue()


# ---------------------------------------------------------------- tabs

COL_WIDTH = {"Ledger ID": 9, "Tag": 22, "Name": 40, "Discipline": 12, "Lane": 14, "Area/Building": 18, "Status": 10,
             "Drawing Sheets": 22, "Found On": 40, "CWP": 8, "CWP Name": 24, "Bid Item": 14, "Quantity": 10,
             "Unit": 6, "MTO Line IDs": 24, "Quantity Confidence": 28, "Spec Sections": 18, "Wiki Note(s)": 32,
             "Submittal IDs": 36, "Inspection/Test IDs": 36, "RFI IDs": 22, "Conflict/Gap IDs": 26,
             "Exception Refs": 16, "Schedule Activity": 30, "Source Citation": 50, "Notes": 60, "Addenda": 24}

COLUMN_GUIDE = {
    "Ledger ID": ("L-NNNN, permanent (decision A). L-0001 to L-0447 are the rev0 rows in rev0 order; new rows take "
                  "the next number.", "derived/reconciliation/Ledger_ID_Map.csv", "never blank"),
    "Tag": ("Tag as printed; PROPOSED- when no printed tag was found. Two rows may share a Tag (SD-1).",
            "Ledger rev0", "never blank"),
    "Name": ("What the component is.", "Ledger rev0", "never blank"),
    "Discipline": ("Discipline as the lane recorded it.", "Ledger rev0", "never blank"),
    "Lane": ("Crawl lane that recorded the row.", "Ledger rev0", "never blank"),
    "Area/Building": ("Area or building.", "Ledger rev0", "\"Not stated\" as in rev0"),
    "Status": ("New, Existing, Temporary or Demolished (carried from rev0 so no rev0 fact is lost).", "Ledger rev0",
               "\"Not stated\" as in rev0"),
    "Drawing Sheets": ("Sheets the row cites, with anchors (KN, Det.). Each sheet links to its page in the native "
                       "plan set, or to the Add. 4 reissue when Add. 4 governs.", "Ledger rev0",
                       "None found (no sheet cited in rev0)"),
    "Found On": ("Where the OCR lane read the tag: sheet, set page, box [x0,y0,x1,y1] in PDF points (origin top "
                 "left), read method, and how many more reads on that sheet. PROPOSED rows show their boxed "
                 "Drawing Sheets anchors instead. Basis: tag = the tag itself was read; sheet = an anchor on a cited "
                 "sheet held the row's noun or quantity.",
                 "derived/ocr/Tag_Hits.csv, Ledger_Crosswalk.csv (Anchor Check)",
                 "None found (tag searched on every page) | Not linked (PROPOSED tag is not printed)"),
    "CWP": ("Construction work package, by the by-CWP rules (CWP Rules tab of Project_Ledger_by_CWP.xlsx).",
            "Project_Ledger_by_CWP.csv; new rows by the same rules", "never blank"),
    "CWP Name": ("Package name.", "Project_Ledger_by_CWP.csv", "never blank"),
    "Bid Item": ("Bid item as the Ledger records it.", "Ledger rev0", "\"Not stated\" as in rev0"),
    "Quantity": ("One total per row: the sum of the row's MTO lines that count (Verified lines only, no double "
                 "counting).", "MTO Lines tab",
                 "Not totaled: no Verified line | None found"),
    "Unit": ("Unit of the total, or of the lines when nothing is totaled.", "MTO Lines tab", "None found"),
    "MTO Line IDs": ("Every MTO line tied to the row, with its basis: tag (tag count, or nearest tag) or sheet "
                     "(keyed-note anchor or Ledger Name quantity on a cited sheet). Click to jump to the MTO Lines "
                     "tab.", "MTO Lines tab", "None found"),
    "Quantity Confidence": ("Tag level of the total and how many lines were or were not totaled.", "MTO Lines tab",
                            "None found (and why)"),
    "Spec Sections": ("Spec sections the row cites; each links to its Wiki note.", "Ledger rev0",
                      "None found (no spec section cited in rev0)"),
    "Wiki Note(s)": ("Wiki notes that name the row (tag), cover one of its spec sections (spec) or one of its sheets "
                     "(sheet), plus the notes rev0 cited. Each opens the note in Project_Wiki.md.",
                     "derived/wiki/Wiki_Links.csv, Wiki_Notes.csv; Ledger rev0", "None found"),
    "Submittal Count": ("Number of Submittal Register lines linked.", "Submittal_Register.csv", "0"),
    "Submittal IDs": ("Register lines with their basis: tag = the line's text names the row's printed tag; spec = "
                      "the line belongs to a spec section the row cites (a section requirement applies to every item "
                      "in it); sheet = the line names no spec section and comes from a sheet the row cites.",
                      "Submittal_Register.csv", "None found"),
    "Submittal Link Basis": ("Count of links by basis.", "computed", "tag 0; spec 0; sheet 0"),
    "Submittal Req (Y/N)": ("The lane's own flag (carried from rev0 so no rev0 fact is lost).", "Ledger rev0",
                            "\"Not stated\" as in rev0"),
    "Inspection/Test Count": ("Number of ITP lines linked.", "Inspection_Test_Plan.csv", "0"),
    "Inspection/Test IDs": ("ITP lines with their basis; same rules as Submittal IDs.", "Inspection_Test_Plan.csv",
                            "None found"),
    "Inspection/Test Link Basis": ("Count of links by basis.", "computed", "tag 0; spec 0; sheet 0"),
    "Testing/Startup Req (Y/N)": ("The lane's own flag (carried from rev0).", "Ledger rev0",
                                  "\"Not stated\" as in rev0"),
    "Addenda": ("Addendum items the row records; Add. 4 governs over the base documents.", "Ledger rev0",
                "None found (Add. 4 checked; Addenda 1-3 not staged)"),
    "RFI IDs": ("Open items of type RFI: tag = the item names this Ledger ID; an item naming no Ledger ID links by "
                "its spec sections (spec), else its sheets (sheet).", "derived/issues/Open_Items.csv", "None found"),
    "Conflict/Gap Count": ("Number of conflict and gap open items linked.", "derived/issues/Open_Items.csv", "0"),
    "Conflict/Gap IDs": ("Open items of type conflict or gap, same rules as RFI IDs.", "derived/issues/Open_Items.csv",
                         "None found"),
    "Exception Refs": ("Exception Report numbers Merge attached to the row (\"[Merge] Exceptions\" in Notes); "
                       "basis tag (the report names this row).", "Exception_Report.md", "None found"),
    "Schedule Activity": ("Activity that carries the row.", "Installation_Tracker_by_CWP.csv, Schedule_by_CWP.csv",
                          "Not linked (new row) | Not scheduled (future work)"),
    "Planned Start": ("Planned start of that activity.", "Installation_Tracker_by_CWP.csv", "as Schedule Activity"),
    "Planned Finish": ("Planned finish.", "Installation_Tracker_by_CWP.csv", "as Schedule Activity"),
    "Submittal Approve-by": ("Approve-by date for the row's submittals.", "Installation_Tracker_by_CWP.csv",
                             "None found (no submittal)"),
    "Tracker Status": ("Latest progress step entered in the tracker.", "Installation_Tracker_by_CWP.csv",
                       "Not started (baseline: no progress entered)"),
    "Confidence": ("The row's tag: the weakest of its key facts, as in rev0. New rows: the weakest of their page "
                   "read, CWP rule and connected document.", "Ledger rev0; new rows computed", "never blank"),
    "Source Citation": ("Where each fact was read.", "Ledger rev0", "never blank"),
    "Notes": ("Lane and Merge notes; \"[rev1]\" marks what this revision added.", "Ledger rev0",
              "None found (no notes in rev0)"),
}


def ledger_tab(rows, links_sheet_pos):
    sh = Sheet("Ledger")
    band_row, head = [], []
    col = 1
    for bi, (code, name, cols) in enumerate(BANDS):
        band_row += [(f"{code}  {name}", S_BAND + bi, None)] + [("", S_BAND + bi, None)] * (len(cols) - 1)
        sh.merges.append(f"{col_letter(col)}1:{col_letter(col + len(cols) - 1)}1")
        head += [(c, S_BHEAD + bi, None) for c in cols]
        for k, c in enumerate(cols):
            sh.widths.append(COL_WIDTH.get(c, 14))
            sh.levels.append(0 if k == 0 or c == "Tag" else 1)
        col += len(cols)
    sh.add(band_row)
    sh.add(head)
    for r in rows:
        cells = []
        for c in HEADER:
            v = r[c]
            ln = None
            lk = r["_links"].get(c)
            if lk:
                ln = lk[0]["url"] if len(lk) == 1 else f"#'Links'!A{links_sheet_pos[(r['Ledger ID'], c)]}"
            if c == "Ledger ID":
                ln = f"#'Links'!A{links_sheet_pos[(r['Ledger ID'], '')]}" if (r["Ledger ID"], "") in links_sheet_pos \
                    else None
            if c == "Quantity" and re.fullmatch(r"-?\d+(\.\d+)?", str(v)):
                v = num(v)
            cells.append((v, S_LINK if ln else S_WRAP, ln))
        sh.add(cells)
    sh.freeze = (2, 2)
    sh.filter = (2, len(rows) + 2, len(HEADER))
    return sh


def links_tab(rows):
    sh = Sheet("Links")
    sh.widths = [10, 22, 18, 60, 8, 12, 70]
    head = ["Ledger ID", "Tag", "Column", "Item", "Basis", "Level", "Opens"]
    sh.add([(h, S_HEAD, None) for h in head])
    pos = {}
    for r in rows:
        first = True
        for c in LINK_COLS:
            for x in r["_links"].get(c, []):
                rn = len(sh.rows) + 1
                if first:
                    pos[(r["Ledger ID"], "")] = rn
                    first = False
                pos.setdefault((r["Ledger ID"], c), rn)
                sh.add([(r["Ledger ID"], S_LINK, f"#'Ledger'!A{LEDGER_POS[r['Ledger ID']]}"), (r["Tag"], S_WRAP, None),
                        (c, S_WRAP, None), (x["item"], S_LINK, x["url"]), (x["basis"], S_WRAP, None),
                        (x["level"] or "—", S_WRAP, None),
                        (x["url"] if not x["url"].startswith("#") else "this workbook: " + x["url"][1:], S_WRAP, None)])
    sh.freeze = (0, 1)
    sh.filter = (1, len(sh.rows), len(head))
    return sh, pos


LEDGER_POS = {}


def mto_tab(mto, totals):
    sh = Sheet("MTO Lines")
    sh.widths = [11, 14, 18, 11, 10, 48, 9, 6, 7, 10, 26, 14, 18, 11, 9, 50, 9, 50, 16, 60]
    sh.add([(h, S_HEAD, None) for h in MTO_HEADER])
    for m in mto:
        u, _ = sheet_link(m["sheet"])
        tags = "; ".join(ROWS_BY_LID[x]["Tag"] for x in m["lids"]) if m["lids"] else ""
        vals = mto_record(m, tags)
        cells = []
        for h, v in zip(MTO_HEADER, vals):
            ln = None
            if h == "Ledger ID" and len(m["lids"]) == 1:
                ln = f"#'Ledger'!A{LEDGER_POS[m['lids'][0]]}"
            if h == "Sheet":
                ln = u
            if h == "Quantity":
                v = num(v)
            cells.append((v, S_LINK if ln else S_WRAP, ln))
        sh.add(cells)
    sh.add([])
    sh.add([("Totals (lines that count; they tie to the Ledger Quantity column)", S_TITLE, None)])
    sh.add([(h, S_HEAD, None) for h in ("Unit", "Lines that count", "Total", "Ledger rows with a total",
                                          "Sum of Ledger Quantity")])
    for unit, (n, tot, nrows, ltot) in sorted(totals.items()):
        sh.add([(unit, S_WRAP, None), (n, S_WRAP, None), (num(tot), S_WRAP, None), (nrows, S_WRAP, None),
                (num(ltot), S_WRAP, None)])
    sh.add([])
    sh.add([("Totals by row Status (lines that count)", S_TITLE, None)])
    sh.add([(h, S_HEAD, None) for h in ("Unit", "Row Status", "Lines", "Total")])
    for (unit, st), (n, t) in sorted(status_totals(mto).items()):
        sh.add([(unit, S_WRAP, None), (st, S_WRAP, None), (n, S_WRAP, None), (num(t), S_WRAP, None)])
    sh.freeze = (1, 1)
    sh.filter = (1, len(mto) + 1, len(MTO_HEADER))
    return sh


def status_totals(mto):
    out = {}
    for m in mto:
        if m["counts"] == "Y":
            k = (m["unit"], ROWS_BY_LID[m["lids"][0]]["Status"])
            n, t = out.get(k, (0, 0.0))
            out[k] = (n + 1, t + float(m["qty"]))
    return out


def mto_record(m, tags):
    status = "; ".join(sorted({ROWS_BY_LID[x]["Status"] for x in m["lids"]})) or "—"
    return [m["id"], "; ".join(m["lids"]), tags, status, m["type"], m["item"], m["qty"], m["unit"], m["sheet"],
            R.page_label(m["pk"]), m["box"], m["kn"], m["method"], m["conf"], m["counts"],
            "; ".join(m["why"]) if m["why"] else "—", m["basis"], m["tie"], m["bid"], m["cite"]]


ROWS_BY_LID = {}


def table_tab(name, header, records, widths):
    sh = Sheet(name)
    sh.widths = widths
    sh.add([(h, S_HEAD, None) for h in header])
    for rec in records:
        sh.add([(v, S_WRAP, None) for v in rec])
    sh.freeze = (0, 1)
    sh.filter = (1, len(records) + 1, len(header))
    return sh


# ---------------------------------------------------------------- coverage and summary

def fill_table(rows):
    """Per column: filled cells before (rev0 values) and after (rev1 values)."""
    base = [r for r in rows if not r["_new"]]
    out = []
    for c in HEADER:
        before = sum(1 for r in base if c in REV0_OF and filled(c, r["_rev0row"][REV0_OF[c]]))
        after_base = sum(1 for r in base if filled(c, r[c]))
        after_all = sum(1 for r in rows if filled(c, r[c]))
        out.append((c, before, after_base, after_all))
    return out


def band_fill(ft, nbase, nall):
    out = []
    for code, name, cols in BANDS:
        rows_ = [x for x in ft if x[0] in cols]
        cells_b = nbase * len(cols)
        cells_a = nall * len(cols)
        b = sum(x[1] for x in rows_)
        ab = sum(x[2] for x in rows_)
        aa = sum(x[3] for x in rows_)
        out.append((code, name, len(cols), b / cells_b, ab / cells_b, aa / cells_a))
    return out


def pct(x):
    return f"{100 * x:.1f}%"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="output folder (default: project/02_Project_Ledger)")
    args = ap.parse_args()
    out = Path(args.out).resolve()

    schema = next(csv.reader(io.StringIO(SCHEMA_REV1.read_text(encoding="utf-8"))))
    tie("index/Ledger_Schema_rev1.csv = the rev1 columns", schema == HEADER,
        f"{len(schema)} schema columns, {len(HEADER)} built")
    rows = base_rows()
    for r in rows:
        r["_rev0row"] = r["_rev0"]
    hits_for = hits_by_row()
    new, cands = build_new_rows(rows, hits_for)
    for r in new:
        r["_rev0row"] = None
    allrows = rows + new
    for r in allrows:
        ROWS_BY_LID[r["_lid"]] = r
    mto, held, stats = build_mto(allrows, hits_for, dup_pairs_from_open())
    for n, m in enumerate(mto, start=2):
        MTO_ROW[m["id"]] = n
    for n, r in enumerate(allrows, start=3):
        LEDGER_POS[r["_lid"]] = n
    built = assemble(allrows, mto, hits_for)
    for b, r in zip(built, allrows):
        b["_rev0row"] = r["_rev0row"]

    # ---- tie-outs
    ids = [r["Ledger ID"] for r in built]
    base_ids = [LID[i] for i, _ in LROWS]
    tie("All 447 base rows present, in rev0 order, with rev0 Tag and Name",
        ids[:len(base_ids)] == base_ids and len(base_ids) == 447 and all(
            b["Tag"] == r["Tag"] and b["Name"] == r["Name"] for b, (_, r) in zip(built, LROWS)),
        f"{len(base_ids)} base rows, {len(built)} rows in all")
    tie("Ledger IDs unique and in the L-NNNN form", len(set(ids)) == len(ids) and all(
        re.fullmatch(r"L-\d{4}", i) for i in ids), f"{len(ids)} IDs")
    newc = [c for c in cands if c["decision"] == "Added"]
    tie("Every new row passes the three-part test", len(newc) == len(new) and all(
        c["test"]["a"] and c["test"]["b"] and c["test"]["c"] and re.search(r"\[[\d.,]+\]", c["test"]["a"])
        and re.search(r"(set )?p\.\d+|Add\. 4 p\.\d+", c["test"]["a"]) for c in newc),
        f"{len(new)} new rows; each has a sheet, set page and box, a CWP by rules 1-5 and a connected document")
    tie("No new row is an I/O point, area, standard or drawing reference",
        all(not c["cat"] and c["src"] != "Prompt 9 unmatched tag" for c in newc),
        f"{len(newc)} new rows: the owner's earthwork rows and range members of Ledger tags only")
    blanks = [(b["Ledger ID"], c) for b in built for c in HEADER if str(b[c]).strip() == ""]
    tie("No blank cell", not blanks, f"{len(blanks)} blank cells" + (f", first {blanks[:3]}" if blanks else ""))
    nobasis = []
    for b in built:
        for c in BASIS_COLS:
            for x in b["_links"][c]:
                if x["basis"] not in BASES or f"({x['basis']})" not in b[c]:
                    nobasis.append((b["Ledger ID"], c, x["label"]))
    tie("Every link carries its basis (tag, spec or sheet)", not nobasis, f"{len(nobasis)} links without a basis")
    order_bad = [(b["Ledger ID"], c) for b in built for c in BASIS_COLS
                 if [BASES.index(x["basis"]) for x in b["_links"][c]] != sorted(
                     BASES.index(x["basis"]) for x in b["_links"][c])]
    tie("Direct links first in every link cell", not order_bad, f"{len(order_bad)} cells out of order")
    cnt_bad = [b["Ledger ID"] for b in built if b["Submittal Count"] != len(b["_links"]["Submittal IDs"])
               or b["Inspection/Test Count"] != len(b["_links"]["Inspection/Test IDs"])
               or b["Conflict/Gap Count"] != len(b["_links"]["Conflict/Gap IDs"])]
    tie("Counts = linked IDs", not cnt_bad, f"{len(cnt_bad)} rows differ")
    totals = {}
    qbad = []
    for b in built:
        lines = [m for m in mto if m["lids"] == [b["Ledger ID"]] and m["counts"] == "Y"]
        q = b["Quantity"]
        if re.fullmatch(r"-?\d+(\.\d+)?", str(q)):
            s = sum(float(m["qty"]) for m in lines)
            if abs(s - float(q)) > 1e-9 or {m["unit"] for m in lines} != {b["Unit"]}:
                qbad.append(b["Ledger ID"])
        elif lines:
            qbad.append(b["Ledger ID"])
    for m in mto:
        if m["counts"] == "Y":
            n, t, _, _ = totals.get(m["unit"], (0, 0.0, 0, 0.0))
            totals[m["unit"]] = (n + 1, t + float(m["qty"]), 0, 0.0)
    for unit in totals:
        rs = [b for b in built if b["Unit"] == unit and re.fullmatch(r"-?\d+(\.\d+)?", str(b["Quantity"]))]
        n, t, _, _ = totals[unit]
        totals[unit] = (n, t, len(rs), sum(float(b["Quantity"]) for b in rs))
    tie("MTO totals tie to their lines (each row, and each unit overall)",
        not qbad and all(abs(t - lt) < 1e-9 for _, t, _, lt in totals.values()),
        f"{len(qbad)} rows differ; " + "; ".join(f"{u}: {num(t)} from {n} lines = {num(lt)} on {nr} rows"
                                                 for u, (n, t, nr, lt) in sorted(totals.items())))
    tie("Totals use Verified lines only", all(m["conf"] in STRONG for m in mto if m["counts"] == "Y"),
        f"{sum(1 for m in mto if m['counts'] == 'Y')} lines count")
    tie("No MTO line is a dimension, elevation, slope or size", all(m["unit"] in R.MTO_UNITS for m in mto),
        f"units {sorted({m['unit'] for m in mto})}")
    tie("MTO callouts = lines + held", sum(1 for m in mto if m["type"] == "callout") + len(held) == stats["callouts"],
        f"{stats['callouts']} callouts, {sum(1 for m in mto if m['type'] == 'callout')} lines, {len(held)} held")
    tie("Every unmatched tag is a candidate", {c["tag"] for c in cands if c["src"] == "Prompt 9 unmatched tag"}
        == {u["Tag Text"] for u in R.UNMATCHED}, f"{len(R.UNMATCHED)} unmatched tags")
    if FAILS:
        sys.exit("Stopped: tie-out failed, nothing written:\n  " + "\n  ".join(FAILS))

    # ---- files
    csv_rows = [[b[c] for c in HEADER] for b in built]
    ledger_csv = csv_text(HEADER, csv_rows)
    mto_csv = csv_text(MTO_HEADER, [mto_record(m, "; ".join(ROWS_BY_LID[x]["Tag"] for x in m["lids"])) for m in mto])
    links_sh, pos = links_tab(built)
    ledger_sh = ledger_tab(built, pos)
    ft = fill_table(built)
    nbase, nall = len(base_ids), len(built)
    bands = band_fill(ft, nbase, nall)
    cov = Sheet("Coverage")
    cov.widths = [30, 10, 14, 14, 14, 14, 14]
    cov.add([("Fill rate per band (filled cells / all cells); \"None found\", \"Not linked\", \"Not stated\", "
              "blanks, dashes and zero counts are not filled", S_TITLE, None)])
    cov.add([(h, S_HEAD, None) for h in ("Band", "Columns", f"Before (rev0, {nbase} rows)",
                                          f"After ({nbase} base rows)", f"After (all {nall} rows)")])
    for code, name, n, b, ab, aa in bands:
        cov.add([(f"{code} {name}", S_WRAP, None), (n, S_WRAP, None), (pct(b), S_WRAP, None), (pct(ab), S_WRAP, None),
                 (pct(aa), S_WRAP, None)])
    tb = sum(x[1] for x in ft) / (nbase * len(HEADER))
    tab_ = sum(x[2] for x in ft) / (nbase * len(HEADER))
    taa = sum(x[3] for x in ft) / (nall * len(HEADER))
    cov.add([("All bands", S_HEAD, None), (len(HEADER), S_HEAD, None), (pct(tb), S_HEAD, None),
             (pct(tab_), S_HEAD, None), (pct(taa), S_HEAD, None)])
    cov.add([])
    cov.add([("Fill per column (filled cells)", S_TITLE, None)])
    cov.add([(h, S_HEAD, None) for h in ("Column", "Band", f"Before (rev0, {nbase})", f"After ({nbase} base)",
                                          f"After (all {nall})", "None found", "Not linked")])
    for c, b, ab, aa in ft:
        cov.add([(c, S_WRAP, None), (BAND_OF[c][0], S_WRAP, None), (b if c in REV0_OF else "new", S_WRAP, None),
                 (ab, S_WRAP, None), (aa, S_WRAP, None),
                 (sum(1 for r in built if str(r[c]).startswith(NONE_FOUND)), S_WRAP, None),
                 (sum(1 for r in built if str(r[c]).startswith(NOT_LINKED)), S_WRAP, None)])
    cov.add([])
    cov.add([("Links by basis (row-to-document links)", S_TITLE, None)])
    cov.add([(h, S_HEAD, None) for h in ("Column", "tag", "spec", "sheet", "Rows with a link", "Links")])
    for c in BASIS_COLS:
        cnt = Counter(x["basis"] for b in built for x in b["_links"][c])
        cov.add([(c, S_WRAP, None)] + [(cnt[k], S_WRAP, None) for k in BASES]
                + [(sum(1 for b in built if b["_links"][c]), S_WRAP, None), (sum(cnt.values()), S_WRAP, None)])
    cov.add([])
    cov.add([("MTO", S_TITLE, None)])
    cov.add([(h, S_HEAD, None) for h in ("Line type", "Unit", "Confidence", "Counts", "Lines")])
    for k, v in sorted(Counter((m["type"], m["unit"], m["conf"], m["counts"]) for m in mto).items()):
        cov.add([(k[0], S_WRAP, None), (k[1], S_WRAP, None), (k[2], S_WRAP, None), (k[3], S_WRAP, None),
                 (v, S_WRAP, None)])
    held_reasons = Counter(re.sub(r" \(.*|: .*|\".*", "", why) for _, why in held)
    cov.add([("Quantity leads (LF, EA, CY, SF, SY) on every sheet", S_WRAP, None), (stats["leads"], S_WRAP, None)])
    cov.add([("Leads on base pages Add. 4 supersedes (left out)", S_WRAP, None), (stats["superseded"], S_WRAP, None)])
    cov.add([("Callouts (reads grouped)", S_WRAP, None), (stats["callouts"], S_WRAP, None)])
    for k, v in sorted(held_reasons.items()):
        cov.add([(f"Callouts held: {k}", S_WRAP, None), (v, S_WRAP, None)])
    cand_recs = []
    for n, c in enumerate(cands, start=1):
        cand_recs.append([n, c["src"], c["tag"], c["name"] or "—", c["sheets"], c["first"], c["level"],
                          c["test"]["a"] or "No", c["test"]["b"] or "No", c["test"]["c"] or "No", c["cat"] or "—",
                          c["decision"], c["reason"], c["lid"] or "—"])
    cand_sh = table_tab("Candidates", CAND_HEADER, cand_recs, [8, 30, 22, 36, 26, 36, 10, 36, 34, 40, 26, 10, 60, 10])
    guide = [[BAND_OF[c][0] + " " + BAND_OF[c][1], c, *COLUMN_GUIDE[c]] for c in HEADER]
    guide += [["", "", "", "", ""],
              ["Rules", "Blank cells", "None found = searched and empty; Not linked = the source doesn't cover the "
                                      "row; counts show 0.", "", ""],
              ["Rules", "Link basis", "tag = the source names this row (its Tag or Ledger ID); spec = the source applies "
                                     "to a spec section the row cites; sheet = same sheet. Direct (tag) links first.",
               "", ""],
              ["Rules", "Links", "In the Ledger tab a cell with one link opens it; a cell with several opens the Links "
                                "tab at that row and column, where every sheet, Wiki note and register ID is a link "
                                "(repo links for now).", "", ""],
              ["Rules", "Quantities", "EA for each tagged component found on one of its cited sheets; callout lines by "
                                     "the Prompt 9 tie rules on every sheet; no dimensions, elevations, slopes or sizes; "
                                     "no double counting; Add. 4 governs; totals use Verified lines only.", "", ""],
              ["Rules", "Confidence", "Verified (text layer), Verified-Visual (page image), Inferred (derived; OCR and "
                                     "Bluebeam reads), Unresolved (conflict or missing).", "", ""]]
    guide_sh = table_tab("Column Guide", ["Band", "Column", "What it holds", "Source", "When there is nothing"],
                         guide, [20, 24, 90, 44, 44])
    mto_sh = mto_tab(mto, totals)
    xlsx = write_xlsx([ledger_sh, mto_sh, cov, cand_sh, guide_sh, links_sh])
    summary = summary_md(built, new, cands, mto, held, stats, bands, ft, totals, nbase, nall, tb, tab_, taa,
                         sum(len(x) for b in built for x in b["_links"].values()))
    files = {"Project_Ledger_rev1.csv": ledger_csv.encode("utf-8"), "MTO_Lines_rev1.csv": mto_csv.encode("utf-8"),
             "Project_Ledger_rev1.xlsx": xlsx, "Ledger_rev1_Summary.md": summary.encode("utf-8")}
    out.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (out / name).write_bytes(data)
    print(f"wrote {len(files)} files to {out}: {len(built)} rows ({len(new)} new), {len(mto)} MTO lines "
          f"({sum(1 for m in mto if m['counts'] == 'Y')} count), {len(cands)} candidates")
    for name, ok, detail in TIES:
        print(f"  {ok}: {name} ({detail})")


def summary_md(built, new, cands, mto, held, stats, bands, ft, totals, nbase, nall, tb, tab_, taa, nlinks):
    L = ["# Project Ledger rev1 — Summary", "",
         "Prompt 10: the expanded MTO. One row per component; the columns run left to right from \"what and where\" "
         "to everything connected to it. Built by `testbeds/eastsound/tools/build_ledger_rev1.py` (no LLM calls, "
         "deterministic). rev0 (`Project_Ledger.csv`, `.xlsx` and the by-CWP view) is unchanged.", "",
         "## Files", "",
         "| File | What it holds |", "|---|---|",
         f"| Project_Ledger_rev1.csv | {nall} rows × {len(HEADER)} columns, in `index/Ledger_Schema_rev1.csv` order |",
         "| Project_Ledger_rev1.xlsx | Tabs Ledger, MTO Lines, Coverage, Candidates, Column Guide, plus Links (one row "
         "per link, each clickable) |",
         f"| MTO_Lines_rev1.csv | {len(mto)} MTO lines (machine copy of the MTO Lines tab) |",
         "| Ledger_rev1_Summary.md | This file |", "",
         "## Fill rate per band", "",
         "Filled = the cell carries a fact. \"None found\", \"Not linked\", \"Not stated\", blanks, dashes, zero counts "
         "and an all-zero link basis count as not filled. Before = rev0's own values for the columns it had; columns "
         "new in rev1 start at 0.", "",
         f"| Band | Columns | Before (rev0, {nbase} rows) | After ({nbase} base rows) | After (all {nall} rows) |",
         "|---|---|---|---|---|"]
    for code, name, n, b, ab, aa in bands:
        L.append(f"| {code} {name} | {n} | {pct(b)} | {pct(ab)} | {pct(aa)} |")
    L.append(f"| **All** | {len(HEADER)} | {pct(tb)} | {pct(tab_)} | {pct(taa)} |")
    L += ["", "Per column (filled cells; base rows before and after):", "",
          "| Column | Band | Before | After |", "|---|---|---|---|"]
    for c, b, ab, aa in ft:
        L.append(f"| {c} | {BAND_OF[c][0]} | {b if c in REV0_OF else 'new'} | {ab} |")
    L += ["", "## New rows", ""]
    if new:
        L += ["| Ledger ID | Tag | Page (a) | CWP (b) | Connected document (c) | Confidence |", "|---|---|---|---|---|---|"]
        for c in [c for c in cands if c["decision"] == "Added"]:
            r = next(b for b in built if b["Ledger ID"] == c["lid"])
            L.append(f"| {c['lid']} | {c['tag']} | {c['test']['a']} | {c['test']['b']} | {c['test']['c']} | "
                     f"{r['Confidence']} |")
    else:
        L.append("None.")
    L += ["", "## Candidates held", "",
          f"{len(cands)} candidates; {len(new)} added, {sum(1 for c in cands if c['decision'] != 'Added')} not added "
          "(Candidates tab, one row each with the test result and reason).", "",
          "| Category | Candidates |", "|---|---|"]
    for k, v in sorted(Counter(c["cat"] or "added" for c in cands).items(), key=lambda kv: (-kv[1], kv[0])):
        L.append(f"| {k} | {v} |")
    hp = [c for c in cands if c["cat"] == "held for a person"]
    if hp:
        L += ["", "Held for a person (pass the three-part test, but the documents name them as something other than a "
              "component, or as part of one):", ""]
        L += [f"- {c['tag']}: {c['test']['c']}" for c in hp]
    L += ["", "## MTO", "",
          f"- Callout lines: the Prompt 9 tie rules run on every sheet. {stats['leads']} leads (LF, EA, CY, SF, SY), "
          f"{stats['superseded']} on base pages Add. 4 supersedes (left out), {stats['callouts']} callouts, "
          f"{sum(1 for m in mto if m['type'] == 'callout')} lines, {len(held)} held (no tie, or reads disagree). The "
          "non-civil leads are notes, ratings and durations (\"2 COATS\", \"100 AMPERES\", \"7 DAYS\"), so none tie.",
          f"- Tag-count lines: {sum(1 for m in mto if m['type'] == 'tag count')}, one EA per tagged component found on "
          "one of its cited sheets (best read kept). PROPOSED rows (no printed tag) and Pipe IDs (a run, measured in "
          "LF) get none. A range row counts only members that have no row of their own.",
          f"- Lines that count: {sum(1 for m in mto if m['counts'] == 'Y')} of {len(mto)}. A line does not count when "
          "it is not Verified, its tie is ambiguous, it repeats a value already counted on another sheet, the row is "
          "measured in LF/CY/SF/SY (so a tag count would double count), or an open duplicate item names the row's twin.",
          "", "| Unit | Lines that count | Total | Ledger rows with a total | Sum of Ledger Quantity |",
          "|---|---|---|---|---|"]
    for unit, (n, t, nr, lt) in sorted(totals.items()):
        L.append(f"| {unit} | {n} | {num(t)} | {nr} | {num(lt)} |")
    L += ["", "By row Status (the total mixes new, existing and demolished items; filter on Row Status in the MTO "
          "Lines tab):", "", "| Unit | Row Status | Lines | Total |", "|---|---|---|---|"]
    L += [f"| {u} | {st} | {n} | {num(t)} |" for (u, st), (n, t) in sorted(status_totals(mto).items())]
    groups = dup_groups(mto)
    L += ["", "Open duplicate items that name three or more rows, where two or more of those rows have a counted "
          "line. They are counted on each row; a person confirms they are separate components:", ""]
    L += [f"- {oi}: " + ", ".join(x + " " + ROWS_BY_LID[x]["Tag"] for x in ids) + f" — {title[:160]}"
          for oi, ids, title in groups] or ["- None."]
    L += ["", "## Rules and judgment calls", "",
          "- **Columns.** The 35 columns asked for, in bands A–I, plus Status (band A) and the two rev0 Y/N flags "
          "(bands E and F) so that no rev0 fact is lost. The tag column is named Confidence.",
          "- **CWP.** Base rows keep their by-CWP assignment. A new row takes the first by-CWP rule that applies "
          "(1 spec section, 2 same-item group, 3 temporary, 4 keyword, 5 discipline). Rule 6 (parked in CWP 01) does "
          "not count as an assignment for the test. Rule 4 keeps the by-CWP keywords and adds \"earthwork\" from the "
          "name of CWP 31.",
          "- **Connected document (test c).** A Wiki note or a Submittal/ITP line that names the candidate. Spec "
          "sections are reached through their Wiki notes (AGENTS.md rule 7; no library reads).",
          "- **Never added:** I/O points (read only on E7.0–E9.3), areas, standards and ratings, drawing references; "
          "and variants of a Ledger tag (the same component).",
          "- **Register links.** A Submittal or ITP line links to every row citing its spec section (the section's "
          "requirements apply to all its items); to the rows whose printed tag its text names (tag); and, only when "
          "it names no spec section, to the rows citing its sheet. The register's own Tag(s) column is Merge's "
          "computed linkage, so it is not used as a direct link.",
          "- **Open items.** An item that names Ledger IDs links only to them (tag). One that names none links by "
          "spec section, else by sheet.",
          "- **Found On** uses only assigned tag reads (Gate A). For PROPOSED rows it shows the boxed Drawing Sheets "
          "anchors from the crosswalk, with the match term and level as the OCR lane wrote them.",
          "- **Confidence** of base rows is rev0's tag, unchanged. Prompt 9 proposals (sheet adds, Division 26 tags) "
          "are not applied; they still wait on the owner.",
          "- **Links** are repo links on `main` (the native PDFs with #page, Project_Wiki.md and the register CSVs "
          "with line anchors).", "",
          "## Tie-outs", "", "| Check | Result | Detail |", "|---|---|---|"]
    L += [f"| {n} | {ok} | {d} |" for n, ok, d in TIES]
    L += ["", f"Links written: {nlinks} (Links tab).", "", "## Inputs (SHA-256)", "", "| File | SHA-256 |", "|---|---|"]
    L += [f"| {rel(p)} | {sha(p)} |" for p in sorted(INPUT_FILES + [SCHEMA_REV1], key=lambda p: rel(p))]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
