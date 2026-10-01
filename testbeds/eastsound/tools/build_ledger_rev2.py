#!/usr/bin/env python3
"""Project Ledger rev2 (Prompt 11): rev1 plus the owner's six decisions.

  1. The 14 Verified changes in derived/reconciliation/Ledger_Update_Proposal.csv are applied (6 sheet adds;
     TS, T3, T2 to Verified; ATS to Inferred with the Add. 4 bid split; GEN keeps Unresolved with the RFI in
     Notes; the Hot Box twins' printed Tags). The 229 "needs check" proposals are left as they are.
  2. Hot Box twins: L-0337 and L-0338 keep their IDs, take Status "Duplicate of L-0057 / L-0058", hand their
     links to L-0057 / L-0058 and count in no MTO total.
  3. Earthwork L-0448 / L-0449 stay, marked "Reference only (C0.2: not for bidding or take-off)", and count in no
     total.
  4. Conduit and feeder runs are components: every run in the E6.3 power and control/signal schedules is its own
     row (CWP 26, Inferred), read from the OCR page file and put through the same three-part test.
  5. Two totals: Verified-only (the headline, in Quantity) and "Total incl. reads to verify" beside it.
  6. rev2 is the current Ledger (the READMEs say so; the graph is rebuilt from it).

build_ledger_rev1.py is imported as a module and reused (base rows, candidates, MTO rules, links, xlsx writer);
it is not run, and its own outputs stay as they are.

Inputs (read-only): everything build_ledger_rev1.py reads, plus
  project/02_Project_Ledger/Project_Ledger_rev1.csv     rev1 rows (all present in rev2) and the rev1 fill rate
  derived/reconciliation/Ledger_Update_Proposal.csv     the Prompt 9 proposals
  derived/ocr/pages/*.json                               E6.3 schedule words (Tesseract and Bluebeam) and the
                                                         tag reads of the runs on every page
No library file is opened.

Outputs (project/02_Project_Ledger/, new files only):
  Project_Ledger_rev2.csv     the Ledger in index/Ledger_Schema_rev1.csv columns
  Project_Ledger_rev2.xlsx    tabs Ledger, MTO Lines, Totals, Coverage, Candidates, Column Guide, Links
  MTO_Lines_rev2.csv          the MTO lines (machine copy of the MTO Lines tab; the graph build reads it)
  Ledger_rev2_Summary.md      changes applied, fill rate rev0 -> rev1 -> rev2, rows added, both totals, tie-outs

No LLM calls. Sorted rows and lines, fixed zip dates, LF line endings, UTF-8 without a BOM: two runs give
identical bytes. The run stops, writing nothing, if a tie-out fails.

Run from the repo root with the packages pinned in requirements.txt installed:
  python testbeds/eastsound/tools/build_ledger_rev2.py [--out <folder>]
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
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("build_ledger_rev1", HERE / "build_ledger_rev1.py")
L1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L1)
R, X = L1.R, L1.X

TB = L1.TB
LEDGER_DIR = L1.LEDGER_DIR
REV1_CSV = LEDGER_DIR / "Project_Ledger_rev1.csv"
PROPOSALS = TB / "derived" / "reconciliation" / "Ledger_Update_Proposal.csv"
PAGES = R.OCR / "pages"
RUN_PAGE = PAGES / "076_E6.3.json"
RUN_SHEET = "E6.3"
OUT_DEFAULT = LEDGER_DIR

HEADER = L1.HEADER
TAG_COL0 = L1.TAG_COL0
NONE_FOUND, NOT_LINKED = L1.NONE_FOUND, L1.NOT_LINKED
BASES = L1.BASES
STRONG = L1.STRONG
OWNER = "owner's decision, Prompt 11"
DUPES = {"L-0337": "L-0057", "L-0338": "L-0058"}             # decision 2: duplicate -> twin
EARTHWORK = ("L-0448", "L-0449")                              # decision 3
REFERENCE_ONLY = "Reference only (C0.2: not for bidding or take-off)"
ROLLUP = "L-0353"                                             # PROPOSED-Conduit-and-Conductor-Runs
RUN_SPECS = ["26 05 19", "26 05 33"]                          # the roll-up row's sections (Wire and Cable; Raceways)
INCL = "Total incl. reads to verify"
SOFT_RE = re.compile(r"^(Inferred|Unresolved) line; totals use Verified lines only$")
WORD_NUM = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4}

TIE = L1.tie            # tie-outs go to L1.TIES / L1.FAILS


def lid_num(lid):
    return int(lid[2:])


def rel(p):
    return L1.rel(p)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def note_text(nid):
    return L1.NOTE_BODIES.get(nid, "")


def wiki_cite(nid):
    n = L1.NOTES.get(nid)
    return f"Wiki note {nid} (Project_Wiki.md line {n['Heading Line']})" if n else f"Wiki note {nid}"


def add_note(cell, text):
    """Append to a Notes cell after the " || " separator the lane and Merge notes use, so a note added here is never
    read as part of a "[Merge] Exceptions: #n" list (rev1's Exception Refs parse stops at "|")."""
    return f"{cell.rstrip()} || {text}" if cell.strip() else text


def norm(s):
    """Comparison form of a schedule cell: upper case, no spaces or OCR fill characters."""
    return re.sub(r"[\s_.|~=]", "", s.upper())


# ---------------------------------------------------------------- decision 1: the Verified proposals

def set_page_label(v):
    return f"set p.{v}" if v.isdigit() else v


def evidence(p):
    """'E6.1 set p.74 [box]; E9.1 set p.91 [box]': each evidence sheet with its own page and box."""
    sh, pg, bx = (p[k].split("; ") for k in ("Evidence Sheet", "Evidence Set Page", "Evidence BBox (pt)"))
    if not len(sh) == len(pg) == len(bx):
        sh, pg, bx = [p["Evidence Sheet"]], [p["Evidence Set Page"]], [p["Evidence BBox (pt)"]]
    return "; ".join(f"{s}{'' if g == s else ' ' + set_page_label(g)} [{b}]" for s, g, b in zip(sh, pg, bx)) + \
        f", {p['Evidence Method']}"


def apply_proposals(rows):
    """Apply the Verified proposals to the base rows in place; returns the change records."""
    recs = L1.read_csv(PROPOSALS)
    ver = sorted((p for p in recs if p["Confidence"] == "Verified"), key=lambda p: p["Proposal No."])
    by = {r["_lid"]: r for r in rows}
    changes, stale = [], []
    for p in ver:
        r = by[p["Ledger ID"]]
        field = p["Field"]
        old0 = r["_rev0"][field]
        if old0 != p["Current Value"]:
            stale.append(p["Proposal No."])
            continue
        if field == "Drawing Sheets":
            added = p["Proposed Value"][len(p["Current Value"]):].lstrip("; ").strip()
            if not p["Proposed Value"].startswith(p["Current Value"]) or not added:
                stale.append(p["Proposal No."])
                continue
            before = r[field]
            r[field] = f"{before}; {added}"
            r["_sheets"] = [s for s, _, _ in X.split_sheets(r[field]) if s]
            what = f"adds {added} to Drawing Sheets"
        else:
            before = r[field]
            r[field] = p["Proposed Value"]
            what = {"Tag": f"Tag {before!r} -> {p['Proposed Value']!r}",
                    TAG_COL0: f"Confidence {before} -> {p['Proposed Value']}",
                    "Bid Item": f"Bid Item -> {p['Proposed Value']!r}",
                    "Notes": "Notes take the RFI reason; the tag stays Unresolved"}[field]
        ev = evidence(p)
        r["Notes"] = add_note(r["Notes"], f"[rev2] {p['Proposal No.']} applied ({OWNER}): {what}; evidence {ev}.")
        r["Source Citation"] = r["Source Citation"].rstrip() + f"; [rev2] {p['Proposal No.']}: {ev}"
        changes.append({"no": p["Proposal No."], "lid": r["_lid"], "tag": r["_rev0"]["Tag"], "field":
                        "Confidence" if field == TAG_COL0 else field, "what": what, "evidence": ev,
                        "category": p["Category"]})
    TIE("The 14 Verified proposals: each found and applied, Current Value as in rev0",
        len(ver) == 14 and not stale and len(changes) == 14,
        f"{len(ver)} Verified proposals, {len(changes)} applied, stale {stale or 'none'}; "
        f"{sum(1 for p in recs if p['Confidence'] == 'needs check')} needs-check proposals left as they are")
    return changes


# ---------------------------------------------------------------- decision 4: the E6.3 schedules

COLS = ["ID", "VOLTAGE", "CONDUIT", "WIRE QTY", "SIZE", "GND", "FROM", "TO"]
TAG_ID = re.compile(r"(?i)^[CPS]-[A-Z0-9]")
DASH = re.compile(r"^[—–-]+$")


def cy(w):
    return (w["bbox"][1] + w["bbox"][3]) / 2


def schedule_headers(words):
    """One header line per table: the words VOLTAGE ... TO on one line. Column centres come from them; the ID
    column sits left of VOLTAGE (Tesseract does not read the left table's ID header)."""
    out = []
    for v in sorted((w for w in words if w["text"] == "VOLTAGE"), key=lambda w: w["bbox"][0]):
        line = sorted((w for w in words if abs(cy(w) - cy(v)) < 2.5
                       and v["bbox"][0] - 45 <= w["bbox"][0] <= v["bbox"][0] + 420), key=lambda w: w["bbox"][0])

        def get(name):
            return next(w for w in line if w["text"] == name)

        def mid(w):
            return (w["bbox"][0] + w["bbox"][2]) / 2
        qty, gnd = get("QTY"), get("GND")
        size = [w for w in line if qty["bbox"][2] < w["bbox"][0] < gnd["bbox"][0]][0]
        out.append({"y": cy(v), "x0": v["bbox"][0] - 45, "x1": get("TO")["bbox"][2] + 62,
                    "cen": {"ID": v["bbox"][0] - 25, "VOLTAGE": mid(v), "CONDUIT": mid(get("CONDUIT")),
                            "WIRE QTY": (get("WIRE")["bbox"][0] + qty["bbox"][2]) / 2, "SIZE": mid(size),
                            "GND": mid(gnd), "FROM": mid(get("FROM")), "TO": mid(get("TO"))}})
    return out


def column_edges(h, body):
    """Cut between two column centres at the middle of the widest gap that the fewest words cross."""
    edges = [h["x0"]]
    for a, b in zip(COLS, COLS[1:]):
        lo, hi = h["cen"][a], h["cen"][b]
        counts, x = [], lo
        while x <= hi:
            counts.append((x, sum(1 for w in body if w["bbox"][0] < x < w["bbox"][2])))
            x += 0.25
        least = min(n for _, n in counts)
        runs, cur = [], []
        for x, n in counts:
            if n == least:
                cur.append(x)
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        best = max(runs, key=lambda r: (r[-1] - r[0], -r[0]))
        edges.append(round((best[0] + best[-1]) / 2, 2))
    edges.append(h["x1"])
    return edges


def schedule_lines(words, h):
    body = [w for w in words if h["x0"] <= w["bbox"][0] < h["x1"] and h["y"] + 3 < cy(w) < 665]
    edges = column_edges(h, body)

    def col(w):
        x = w["bbox"][0] + 0.5
        for i, c in enumerate(COLS):
            if edges[i] <= x < edges[i + 1]:
                return c
        return None
    body.sort(key=lambda w: (cy(w), w["bbox"][0]))
    groups, cur, last = [], [], None
    for w in body:
        if last is not None and cy(w) - last > 2.6:
            groups.append(cur)
            cur = []
        cur.append(w)
        last = cy(w)
    if cur:
        groups.append(cur)
    lines = []
    for g in groups:      # two IDs on one line: split the line at the nearer ID
        ids = [w for w in g if col(w) == "ID" and (TAG_ID.match(w["text"]) or w["text"].upper() == "SPARE")]
        if len(ids) > 1:
            for idw in ids:
                lines.append([w for w in g if min(ids, key=lambda i: (abs(cy(i) - cy(w)), i["bbox"][1])) is idw])
        else:
            lines.append(g)
    out = []
    for g in lines:
        cells = {c: [] for c in COLS}
        for w in sorted(g, key=lambda w: w["bbox"][0]):
            c = col(w)
            if c:
                cells[c].append(w)
        out.append({"y": sum(cy(w) for w in g) / len(g), "cells": cells})
    out.sort(key=lambda r: r["y"])
    return out, edges


def clean(ws):
    """(cell text, the cell holds only a dash): OCR fill characters, stray marks and lone lower-case letters out."""
    toks, dash = [], False
    for w in ws:
        t = w["text"].strip("_|~=.").strip()
        if DASH.match(t):
            dash = True
            continue
        if not t or re.fullmatch(r"[a-z]", t) or re.fullmatch(r"[_|~=.:;,'`]+", t):
            continue
        toks.append(t)
    text = " ".join(toks)
    return text, dash and not text


def cells_agree(col, a, b):
    if norm(a) == norm(b):
        return True
    if col in ("FROM", "TO"):     # Bluebeam overlay text may carry extra words from a neighbouring line
        nb, pos = norm(b), 0
        for wd in a.split():
            i = nb.find(norm(wd), pos)
            if i < 0:
                return False
            pos = i + len(norm(wd))
        return True
    return False


def e63_note():
    body = note_text(RUN_SHEET)
    counts = {}
    m = re.search(r"Power schedule: (\d+) named runs plus (\w+) unnamed [^;]*? and an? AC spare", body)
    counts["Power"] = (int(m.group(1)), WORD_NUM[m.group(2)], 1) if m else None
    m = re.search(r"Control and signal schedule: (\d+) named [^;]*?runs plus an? DC spare", body)
    counts["Control and signal"] = (int(m.group(1)), 0, 1) if m else None
    aliases = defaultdict(list)
    m = re.search(r"ID spellings differ \(([^)]*)\)", body)
    for pair in (m.group(1).split(", ") if m else []):
        a, b = pair.split("/")
        aliases[a].append(b)
        aliases[b].append(a)
    conflicts = {}
    m = re.search(r"Disagreements with other sheets: (.*?) \[Verified-Visual\]", body)
    for clause in L1.split_outside(m.group(1) if m else "", ";"):
        if "cosmetic" in clause:
            continue
        for t in expand_tags(clause):
            conflicts.setdefault(t, clause)
    return body, counts, aliases, conflicts


def expand_tags(text):
    """Run tags named in a text, with ranges such as "P-IP1 to P-IP4" expanded."""
    out = []
    for m in re.finditer(r"\b([CPS]-[A-Z0-9]*?[A-Z])(\d+) to \1(\d+)\b", text):
        out += [f"{m.group(1)}{n}" for n in range(int(m.group(2)), int(m.group(3)) + 1)]
    out += re.findall(r"(?<![A-Za-z0-9-])[CPS]-[A-Z0-9][A-Z0-9-]*(?![A-Za-z0-9-])", text)
    return out


def parse_schedules():
    """The E6.3 runs: Tesseract words are the read, Bluebeam words at the same height are the check."""
    d = json.loads(RUN_PAGE.read_text(encoding="utf-8"))
    assert d["sheet_01"] == RUN_SHEET
    ocr = [w for w in d["words"] if w["method"] == "ocr"]
    bbw = d["bluebeam"]["words"]
    body, wiki_counts, aliases, conflicts = e63_note()
    wnorm = norm(body)
    t_heads, b_heads = schedule_headers(ocr), schedule_headers(bbw)
    runs, noise = [], 0
    for th, bh in zip(t_heads, b_heads):
        tlines, _ = schedule_lines(ocr, th)
        blines, _ = schedule_lines(bbw, bh)
        ids = [clean(ln["cells"]["ID"])[0].upper() for ln in tlines]
        kind = "Power" if sum(i.startswith("P-") for i in ids) > sum(i[:2] in ("C-", "S-") for i in ids) \
            else "Control and signal"
        table = []
        for ln in tlines:
            idt, iddash = clean(ln["cells"]["ID"])
            near = [b for b in blines if abs(b["y"] - ln["y"]) < 3.2]
            bl = min(near, key=lambda b: abs(b["y"] - ln["y"])) if near else None
            vals, disputes, variants = {}, [], []
            for c in COLS[1:]:
                a, adash = clean(ln["cells"][c])
                b, bdash = clean(bl["cells"][c]) if bl else ("", False)
                if a and b and not cells_agree(c, a, b):
                    in_a, in_b = len(norm(a)) >= 4 and norm(a) in wnorm, len(norm(b)) >= 4 and norm(b) in wnorm
                    if in_b and not in_a:
                        vals[c] = b
                        disputes.append((c, a, b, "Wiki note E6.3 prints the Bluebeam read"))
                    elif in_a and not in_b:
                        vals[c] = a
                        disputes.append((c, a, b, "Wiki note E6.3 prints the Tesseract read"))
                    else:
                        vals[c] = f"{a} (Tesseract) / {b} (Bluebeam)"
                        disputes.append((c, a, b, ""))
                else:
                    vals[c] = a or b or ("—" if adash or bdash else "")
                    if a and b and norm(a) != norm(b):
                        variants.append((c, a, b))
            filled = [c for c in COLS[1:] if vals[c] and vals[c] != "—"]
            rec = {"y": ln["y"], "vals": vals, "disputes": disputes, "variants": variants,
                   "tess": [w for c in COLS for w in ln["cells"][c]], "id_words": ln["cells"]["ID"],
                   "bb_id": [w for w in (bl["cells"]["ID"] if bl else [])]}
            if idt and (TAG_ID.match(idt) or idt.upper() == "SPARE"):
                table.append({"kind": kind, "id": idt.upper(), "lines": [rec], "y": ln["y"]})
            elif not idt and iddash and len(filled) >= 2:
                table.append({"kind": kind, "id": "", "lines": [rec], "y": ln["y"],
                              "under": table[-1]["id"] if table else ""})
            elif table and len(filled) >= 2:
                table[-1]["lines"].append(rec)
            else:
                noise += 1
        runs += table
        named = sum(1 for r in table if TAG_ID.match(r["id"]))
        unnamed = sum(1 for r in table if not r["id"])
        spares = sum(1 for r in table if r["id"] == "SPARE")
        TIE(f"E6.3 {kind.lower()} schedule matches Wiki note E6.3", wiki_counts.get(kind) == (named, unnamed, spares),
            f"read {named} named, {unnamed} unnamed, {spares} spare; the note says {wiki_counts.get(kind)}")
    return runs, aliases, conflicts, noise


# ---------------------------------------------------------------- run reads on every page

def page_files():
    return sorted(PAGES.glob("*.json"))


def scan_reads(forms_by_run):
    """Every word on every page whose letters and digits equal a run's printed form (the E6.3 ID or a plan
    spelling): Tag_Hits-shaped records, so the rev1 read rules (read_key, read_level, hit_entry) apply."""
    keyed = defaultdict(list)
    for tag, forms in forms_by_run.items():
        for f in forms:
            keyed[R.norm_tag(f)].append(tag)
    out = defaultdict(list)
    for path in page_files():
        d = json.loads(path.read_text(encoding="utf-8"))
        pk = d["page_key"]
        words = [(w, w["method"]) for w in d["words"]] + [(w, "bluebeam-ocr") for w in (d.get("bluebeam") or {})
                                                            .get("words", [])]
        for w, method in words:
            t = w["text"].strip(".,;:()[]")
            if "-" not in t or not re.match(r"(?i)^[CPS]-", t):
                continue
            for tag in keyed.get(R.norm_tag(t), []):
                out[tag].append({
                    "Tag Text": t, "Page Key": pk, "Set Page": str(d["set_page"] or ""), "Sheet": d["sheet_01"],
                    "BBox (pt)": R.fmt_box(w["bbox"]), "Method": method,
                    "Confidence": f"{w['conf']:.2f}" if method == "ocr" and w.get("conf") is not None else "",
                    "Search Form": X.norm_form(tag), "Assignment": "assigned"})
    for tag in out:
        out[tag].sort(key=R.read_key)
    return out


# ---------------------------------------------------------------- decision 4: run rows and their candidates

def describe(run):
    """Name text for a run: every schedule line, values as read."""
    first = run["lines"][0]["vals"]

    def v(vals, c, missing="not read"):
        return vals[c] if vals[c] else missing
    if run["id"] == "SPARE":
        head = f"Spare conduit ({first['VOLTAGE']}) on the E6.3 {run['kind'].lower()} schedule"
    elif not run["id"]:
        head = f"Unnamed {run['kind'].lower()} circuit under {run['under']} on E6.3 (no ID printed)"
    else:
        head = f"{run['kind']} run {run['id']}"
    parts = []
    for n, ln in enumerate(run["lines"]):
        vals = ln["vals"]
        bits = []
        if n == 0 or vals["VOLTAGE"]:
            bits.append(v(vals, "VOLTAGE"))
        if n == 0 or vals["CONDUIT"]:
            bits.append(f"conduit {v(vals, 'CONDUIT', 'blank')}")
        qty, size = vals["WIRE QTY"], vals["SIZE"]
        bits.append("conductors " + ("none listed (dash)" if qty == "—" and not size else
                                     " ".join(x for x in (qty, size) if x) or "blank"))
        bits.append(f"GND {'none listed (dash)' if vals['GND'] == '—' else v(vals, 'GND', 'blank')}")
        fr, to = vals["FROM"], vals["TO"]
        if fr or to:
            bits.append(f"from {fr or 'blank'} to {to or 'blank'}" if n == 0 or fr else f"to {to}")
        parts.append(("; " if n == 0 else "; with ") + ", ".join(bits))
    return head + ":" + parts[0][1:] + "".join(parts[1:]) + ". Length: not shown on E6.3."


def run_tag(run):
    if run["id"] == "SPARE":
        return f"PROPOSED-Spare-Conduit-{run['lines'][0]['vals']['VOLTAGE'] or 'Unknown'}"
    if not run["id"]:
        to = run["lines"][0]["vals"]["TO"]
        return "PROPOSED-" + "-".join(w if re.search(r"\d", w) else w.capitalize() for w in to.split()) + "-Circuit"
    return run["id"]


def range_named(tag, body):
    m = re.match(r"^(.*?)(\d+)$", tag)
    if not m:
        return False
    pre, n = m.group(1), int(m.group(2))
    for mm in re.finditer(re.escape(pre) + r"(\d+) to " + re.escape(pre) + r"(\d+)", body):
        if int(mm.group(1)) <= n <= int(mm.group(2)):
            return True
    return False


def build_runs(rows, new, cands, next_id):
    """The E6.3 run rows (L-0450 on). A run already carried by a Ledger row (P-SEC, P-TPS) is not added again."""
    runs, aliases, conflicts, noise = parse_schedules()
    by_tag = {}
    for r in rows + new:
        if X.family(r["Tag"]) == "printed":
            for f in X.printed_forms(r["Tag"])[0]:
                by_tag.setdefault(R.norm_tag(f), r)
    forms = {}
    for run in runs:
        if TAG_ID.match(run["id"]):
            forms[run["id"]] = [run["id"]] + aliases.get(run["id"], [])
    reads = scan_reads(forms)
    for tag, hs in reads.items():   # plan spellings actually printed (P-BL2 for P-BL-2) are forms too
        for h in hs:
            if h["Method"] == "text-layer" and h["Tag Text"].upper() not in [f.upper() for f in forms[tag]]:
                forms[tag].append(h["Tag Text"].upper())
    rollup = next(r for r in rows if r["_lid"] == ROLLUP)
    added, n = [], next_id
    spec_c = "; ".join(f"Spec {sp} ({wiki_cite(sp).split(' (')[0]}; roll-up row {ROLLUP})" for sp in RUN_SPECS
                       if sp in L1.NOTES)
    body = note_text(RUN_SHEET)
    for run in runs:
        tag = run_tag(run)
        first = run["lines"][0]
        tess = sorted(first["id_words"] or first["tess"], key=lambda w: w["bbox"][0])[0]
        box = tess["bbox"] if TAG_ID.match(run["id"]) else [   # no tag of its own: the whole schedule line
            f(w["bbox"][i] for w in first["tess"]) for f, i in ((min, 0), (min, 1), (max, 2), (max, 3))]
        e63 = [{"Tag Text": tess["text"], "Page Key": "076", "Set Page": "76", "Sheet": RUN_SHEET,
                "BBox (pt)": R.fmt_box(box), "Method": "ocr", "Confidence": f"{tess['conf']:.2f}",
                "Search Form": X.norm_form(tag), "Assignment": "assigned"}]
        hits = reads.get(run["id"], []) if TAG_ID.match(run["id"]) else []
        if not hits:
            hits = e63
        hits = sorted(hits, key=R.read_key)
        text_sheets = sorted({h["Sheet"] for h in hits if h["Method"] == "text-layer"} - {RUN_SHEET},
                             key=L1.sheet_key)
        sheets = [RUN_SHEET] + text_sheets
        found = [L1.hit_entry(s, hs, sheets, "tag" if TAG_ID.match(run["id"]) else "sheet")   # no tag: the line
                 for s, hs in L1.best_per_sheet(hits)]
        best = hits[0]
        best_e63 = next((h for h in hits if h["Sheet"] == RUN_SHEET), e63[0])
        # (c) connected documents
        if TAG_ID.match(run["id"]):
            pats = [L1.tag_pattern(f) for f in forms[run["id"]]]
            notes = sorted({nid for p in pats for nid in L1.wiki_naming(p)} |
                           {nid for nid, b in L1.NOTE_BODIES.items() if range_named(run["id"], b)})
            regs = sorted({rid for p in pats for rid in L1.register_naming(p)})
        else:
            phrase = ("unnamed 120 V UV controller circuits" if not run["id"] else
                      f"{first['vals']['VOLTAGE']} spare")
            notes = [RUN_SHEET] if re.search(re.escape(phrase).replace(r"\ ", r"\s+"), body, re.I) else []
            regs = []
        cw = L1.cwp_for(RUN_SPECS, [], False, tag, "Electrical")
        test = {"a": f"{best['Sheet']} {L1.page_tag(best['Page Key'])} [{best['BBox (pt)']}] "
                     f"({R.read_level(best)}, {best['Method']})"
                     + (f"; E6.3 p.76 [{best_e63['BBox (pt)']}] ({R.read_level(best_e63)}, {best_e63['Method']})"
                        if best is not best_e63 else ""),
                "b": f"{cw[0]} — {cw[1]}" if cw else "",
                "c": "; ".join([f"Wiki note {x}" for x in notes] + regs + ([spec_c] if spec_c else []))}
        named = R.norm_tag(run["id"]) in by_tag if TAG_ID.match(run["id"]) else False
        cand = {"src": "E6.3 run group (owner's decision 4, Prompt 11)", "tag": tag, "name": "", "sheets":
                "; ".join(sheets), "first": test["a"], "level": R.read_level(best), "test": test, "cat": "",
                "lid": ""}
        if named:
            r0 = by_tag[R.norm_tag(run["id"])]
            cand.update(decision="Already a row", cat="already a Ledger row",
                        reason=f"the Ledger already carries {run['id']} as {r0['_lid']}; not added again",
                        lid=r0["_lid"])
            cands.append(cand)
            continue
        if not all(test.values()):
            cand.update(decision="Not added", cat="fails the three-part test",
                        reason="fails " + ", ".join(L1.TEST_WHY[k] for k, v in test.items() if not v))
            cands.append(cand)
            continue
        lid = f"L-{n:04d}"
        n += 1
        why_unres = [f"{c}: Tesseract reads {a!r}, Bluebeam {b!r}" for ln in run["lines"]
                     for c, a, b, how in ln["disputes"] if not how]
        settled = [f"{c}: Tesseract reads {a!r}, Bluebeam {b!r}; {how}" for ln in run["lines"]
                   for c, a, b, how in ln["disputes"] if how]
        settled += [f"{c}: Bluebeam reads {b!r}, taken as the same text as Tesseract's {a!r}" for ln in run["lines"]
                    for c, a, b in ln["variants"]]
        conflict = conflicts.get(run["id"], "")
        level = "Unresolved" if why_unres or conflict else L1.weakest(["Inferred", R.read_level(best_e63)])
        future = any("(FUTURE)" in v for ln in run["lines"] for v in ln["vals"].values())
        plan = [f for f in forms.get(run["id"], [])[1:]]
        name = describe(run)
        reads_txt = "; ".join(e["label"] for e in found)
        row = {
            "Tag": tag, "Name": name, "Discipline": "Electrical", "Lane": rollup["Lane"],
            "Area/Building": "Not stated (E6.3 gives from and to only)", "Status": "Not stated" if future else "New",
            "Drawing Sheets": "; ".join([f"{RUN_SHEET} ({run['kind'].lower()} schedule)"] + text_sheets),
            "Bid Item": f"6 (Inferred: same as the roll-up row {ROLLUP})", "CWP": cw[0], "CWP Name": L1.CWP_NAME[cw[0]],
            "_cwp_basis": cw[1], "Spec Sections": "; ".join(RUN_SPECS), "Wiki Note(s)": RUN_SHEET,
            "Submittal Req (Y/N)": "Not stated (new row)", "Testing/Startup Req (Y/N)": "Not stated (new row)",
            "Addenda": "", TAG_COL0: level,
            "Source Citation": (f"E6.3 {run['kind'].lower()} schedule, {R.page_cite('076')}: Tesseract read of the "
                                f"line at [{R.fmt_box(box)}], checked against the Bluebeam read of the "
                                f"same line; reads: {reads_txt}; {wiki_cite(RUN_SHEET)}; spec sections "
                                f"{' and '.join(RUN_SPECS)} as on roll-up row {ROLLUP}"),
            "Notes": (f"[rev2] New row: E6.3 {run['kind'].lower()} schedule ({OWNER}, decision 4: conduit and feeder "
                      f"runs are components). Values are OCR reads of the schedule (Tesseract, checked against "
                      f"Bluebeam; Inferred); E6.3 shows no run length. Three-part test: page {test['a']}; "
                      f"{test['b']}; connected document {test['c']}. Spec Sections and Bid Item follow the roll-up "
                      f"row {ROLLUP} (Inferred)"
                      + ("; Status Not stated: the schedule reads (FUTURE)" if future else
                         "; Status New follows the roll-up row (\"all scheduled runs are new work\")") + "."
                      + (f" Plan spelling: {', '.join(plan)}." if plan else "")
                      + (f" Read check: {'; '.join(settled)}." if settled else "")
                      + (f" Unresolved: the two OCR reads disagree ({'; '.join(why_unres)}); a person checks the "
                         f"page image." if why_unres else "")
                      + (f" Unresolved: Wiki note E6.3 records \"{conflict}\" (Verified-Visual)." if conflict else "")),
            "_lid": lid, "Ledger ID": lid, "_line": None, "_new": True, "_rev0": None, "_rev0row": None,
            "_sheets": sheets, "_specs": list(RUN_SPECS), "_found": found,
            "_hits": hits if TAG_ID.match(run["id"]) else [], "_named_notes": [x for x in notes if x in L1.NOTES],
            "_siblings": [], "_run": run}
        L1.CWPOF[lid] = cw[0]
        added.append(row)
        cand.update(decision="Added", reason="passes (a), (b) and (c)", lid=lid, name=name[:120])
        cands.append(cand)
    # C-2W and P-2W were held in rev1 as unmatched tags; they come in with the group.
    lid_of = {r["Tag"]: r["_lid"] for r in added}
    for c in cands:
        if c["src"] == "Prompt 9 unmatched tag" and c["tag"] in lid_of:
            c.update(decision="Added with the E6.3 run group", cat="added (E6.3 run group)", lid=lid_of[c["tag"]],
                     reason=f"conduit/feeder run ({OWNER}, decision 4); row {lid_of[c['tag']]} comes from the E6.3 "
                            "schedule")
    return added, runs, noise


# ---------------------------------------------------------------- decisions 2, 3 and 5 on the MTO

def mark_mto(mto, dup_pairs):
    """Earthwork and duplicate rows count in no total; each line gets its 'incl. reads to verify' flag."""
    for m in mto:
        ew = [x for x in m["lids"] if x in EARTHWORK]
        du = [x for x in m["lids"] if x in DUPES]
        if ew:
            m["why"].append(f"{REFERENCE_ONLY}; {OWNER}")
        for x in du:
            m["why"].append(f"duplicate row of {DUPES[x]} ({OWNER}); counted on {DUPES[x]}")
        m["counts"] = "Y" if not m["why"] else "N"
        m["incl"] = "Y" if m["counts"] == "Y" or (len(m["lids"]) == 1 and m["why"] and all(
            SOFT_RE.match(w) for w in m["why"])) else "N"
    # A duplicate pair (open item naming exactly two rows) counts once in the incl. total too, unit by unit: lines in
    # different units are different quantities (OI-0112 pairs the SD-1 storm drain, LF, with the SD-1 pump, EA).
    for a, b, oi in dup_pairs:
        for unit in sorted({m["unit"] for m in mto if m["lids"] in ([a], [b])}):
            la = [m for m in mto if m["lids"] == [a] and m["unit"] == unit and m["incl"] == "Y"]
            lb = [m for m in mto if m["lids"] == [b] and m["unit"] == unit and m["incl"] == "Y"]
            if not (la and lb):
                continue
            if any(m["counts"] == "Y" for m in lb) and not any(m["counts"] == "Y" for m in la):
                drop, keep = la, b
            else:
                drop, keep = lb, a
            for m in drop:
                if m["counts"] == "N":
                    m["why"].append(f"duplicate of {keep} per {oi}; counted once, on {keep}")
                    m["incl"] = "N"


def totals_by(mto, key):
    out = {}
    for m in mto:
        for flag, slot in (("counts", 0), ("incl", 1)):
            if m[flag] == "Y":
                k = key(m)
                cur = out.setdefault(k, [[0, 0.0], [0, 0.0]])
                cur[slot][0] += 1
                cur[slot][1] += float(m["qty"])
    return out


# ---------------------------------------------------------------- after assemble: moves, totals, schedule

def move_links(built):
    """Decision 2: a duplicate row's links go to its twin (deduped, stronger basis kept, direct links first)."""
    by = {b["Ledger ID"]: b for b in built}
    moved = {}
    for dup, twin in DUPES.items():
        d, t = by[dup], by[twin]
        new_labels = []
        for col in L1.BASIS_COLS:
            tl = list(t["_links"][col])
            for x in d["_links"][col]:
                same = [y for y in tl if y["label"] == x["label"]]
                if same:
                    y = same[0]
                    if BASES.index(x["basis"]) < BASES.index(y["basis"]):
                        tl[tl.index(y)] = dict(y, basis=x["basis"])
                else:
                    tl.append(dict(x))
                    new_labels.append((col, x["label"], x["basis"]))
            if col in ("Submittal IDs", "Inspection/Test IDs", "RFI IDs", "Conflict/Gap IDs"):
                tl = sorted(tl, key=lambda x: x["label"])
            t["_links"][col] = L1.ordered(tl)
            if t["_links"][col]:
                t[col] = L1.cell(t["_links"][col])
            d["_links"][col] = []
            d[col] = f"{NOT_LINKED} (duplicate of {twin}; links moved there)"
        for tb in (t, d):
            tb["Submittal Count"] = len(tb["_links"]["Submittal IDs"])
            tb["Submittal Link Basis"] = L1.basis_counts(tb["_links"]["Submittal IDs"])
            tb["Inspection/Test Count"] = len(tb["_links"]["Inspection/Test IDs"])
            tb["Inspection/Test Link Basis"] = L1.basis_counts(tb["_links"]["Inspection/Test IDs"])
            tb["Conflict/Gap Count"] = len(tb["_links"]["Conflict/Gap IDs"])
        d["Quantity"] = f"Not totaled: duplicate of {twin}"
        d["Unit"] = f"{NOT_LINKED} (duplicate of {twin})"
        d["Quantity Confidence"] = f"Not totaled: duplicate of {twin} ({OWNER}); its quantity is counted on {twin}"
        listing = "; ".join(f"{col} {lab} ({bas})" for col, lab, bas in new_labels) or "none new (all already here)"
        t["Notes"] = add_note(t["Notes"], f"[rev2] Links moved here from duplicate row {dup} ({OWNER}): {listing}.")
        moved[dup] = new_labels
    return moved


def incl_cells(built, mto):
    """Quantity Confidence states the incl. total; the Ledger tab shows it in its own column."""
    by_lid = defaultdict(list)
    for m in mto:
        if len(m["lids"]) == 1:
            by_lid[m["lids"][0]].append(m)
    for b in built:
        lid = b["Ledger ID"]
        lines = by_lid.get(lid, [])
        inc = [m for m in lines if m["incl"] == "Y"]
        units = sorted({m["unit"] for m in inc})
        if lid in DUPES:
            val = f"Not totaled: duplicate of {DUPES[lid]}"
        elif lid in EARTHWORK:
            val = "Not totaled: reference only"
        elif len(units) == 1:
            val = L1.num(sum(float(m["qty"]) for m in inc))
            b["_incl_unit"] = units[0]
            b["_incl_n"] = len(inc)
        elif len(units) > 1:
            val = "Not totaled: lines in more than one unit"
        elif lines:
            val = "None: no line qualifies (MTO Lines: Not Totaled Because)"
        else:
            val = NONE_FOUND
        b["_incl"] = val
        if lines and lid not in DUPES and lid not in EARTHWORK:
            txt = (f"{L1.fmt_num(val)} {units[0]} ({len(inc)} line{'s' if len(inc) != 1 else ''})"
                   if len(units) == 1 else val)
            b["Quantity Confidence"] = b["Quantity Confidence"].rstrip() + f"; {INCL.lower()}: {txt}"


def earthwork_cells(built):
    for b in built:
        if b["Ledger ID"] in EARTHWORK:
            b["Quantity"] = "Not totaled: reference only (C0.2)"
            b["Quantity Confidence"] = REFERENCE_ONLY


def run_schedule(built, run_ids):
    roll = next(b for b in built if b["Ledger ID"] == ROLLUP)
    for b in built:
        if b["Ledger ID"] in run_ids:
            b["Schedule Activity"] = f"{roll['Schedule Activity']} (via roll-up row {ROLLUP}; Inferred)"
            b["Planned Start"], b["Planned Finish"] = roll["Planned Start"], roll["Planned Finish"]
            b["Submittal Approve-by"] = roll["Submittal Approve-by"]
            b["Tracker Status"] = f"{NOT_LINKED} (the tracker carries the roll-up row {ROLLUP})"
            b["_links"]["Schedule Activity"] = [dict(x) for x in roll["_links"]["Schedule Activity"]]


# ---------------------------------------------------------------- xlsx tabs

HEADER_TAB = HEADER[:HEADER.index("Quantity") + 1] + [INCL] + HEADER[HEADER.index("Quantity") + 1:]
BANDS_TAB = [(code, name, cols[:cols.index("Quantity") + 1] + [INCL] + cols[cols.index("Quantity") + 1:]
              if "Quantity" in cols else cols) for code, name, cols in L1.BANDS]
MTO_HEADER = (L1.MTO_HEADER[:L1.MTO_HEADER.index("Counts To Total (Y/N)") + 1] + ["Counts Incl. Reads to Verify (Y/N)"]
              + L1.MTO_HEADER[L1.MTO_HEADER.index("Counts To Total (Y/N)") + 1:])
NUM_RE = re.compile(r"-?\d+(\.\d+)?")


def ledger_tab(built, pos):
    sh = L1.Sheet("Ledger")
    band_row, head = [], []
    col = 1
    for bi, (code, name, cols) in enumerate(BANDS_TAB):
        band_row += [(f"{code}  {name}", L1.S_BAND + bi, None)] + [("", L1.S_BAND + bi, None)] * (len(cols) - 1)
        sh.merges.append(f"{L1.col_letter(col)}1:{L1.col_letter(col + len(cols) - 1)}1")
        head += [(c, L1.S_BHEAD + bi, None) for c in cols]
        for k, c in enumerate(cols):
            sh.widths.append(12 if c == INCL else L1.COL_WIDTH.get(c, 14))
            sh.levels.append(0 if k == 0 or c == "Tag" else 1)
        col += len(cols)
    sh.add(band_row)
    sh.add(head)
    for r in built:
        cells = []
        for c in HEADER_TAB:
            v = r["_incl"] if c == INCL else r[c]
            ln = None
            lk = r["_links"].get(c)
            if lk:
                ln = lk[0]["url"] if len(lk) == 1 else f"#'Links'!A{pos[(r['Ledger ID'], c)]}"
            if c == "Ledger ID":
                ln = f"#'Links'!A{pos[(r['Ledger ID'], '')]}" if (r["Ledger ID"], "") in pos else None
            if c in ("Quantity", INCL) and NUM_RE.fullmatch(str(v)):
                v = L1.num(v)
            cells.append((v, L1.S_LINK if ln else L1.S_WRAP, ln))
        sh.add(cells)
    sh.freeze = (2, 2)
    sh.filter = (2, len(built) + 2, len(HEADER_TAB))
    return sh


def mto_record(m):
    tags = "; ".join(L1.ROWS_BY_LID[x]["Tag"] for x in m["lids"])
    rec = L1.mto_record(m, tags)
    i = L1.MTO_HEADER.index("Counts To Total (Y/N)") + 1
    return rec[:i] + [m["incl"]] + rec[i:]


def group_of(m, run_lids):
    return "E6.3 conduit and feeder runs" if m["lids"] and m["lids"][0] in run_lids else "Other components"


def totals_rows(mto, ledger_sums):
    """[(unit, V lines, V total, V rows, V Ledger sum, I lines, I total, I rows, I Ledger sum)]"""
    t = totals_by(mto, lambda m: m["unit"])
    out = []
    for unit in sorted(t):
        (vn, vt), (inn, it) = t[unit]
        vr, vs, ir, is_ = ledger_sums.get(unit, (0, 0.0, 0, 0.0))
        out.append((unit, vn, vt, vr, vs, inn, it, ir, is_))
    return out


TOT_HEAD = ("Unit", "Verified-only: lines", "Verified-only: total", "Ledger rows with a Verified total",
            "Sum of Ledger Quantity", "Incl. reads to verify: lines", "Total incl. reads to verify",
            "Ledger rows with a total incl. reads", f"Sum of Ledger \"{INCL}\"", "Added by reads to verify")


def add_totals_block(sh, mto, ledger_sums, run_lids):
    S = L1.S_WRAP
    sh.add([("Totals by unit. Verified-only is the headline (Quantity column); the total incl. reads to verify adds "
             "lines held back only because their read is Inferred or Unresolved", L1.S_TITLE, None)])
    sh.add([(h, L1.S_HEAD, None) for h in TOT_HEAD])
    for unit, vn, vt, vr, vs, inn, it, ir, is_ in totals_rows(mto, ledger_sums):
        sh.add([(unit, S, None), (vn, S, None), (L1.num(vt), S, None), (vr, S, None), (L1.num(vs), S, None),
                (inn, S, None), (L1.num(it), S, None), (ir, S, None), (L1.num(is_), S, None),
                (L1.num(it - vt), S, None)])
    sh.add([])
    sh.add([("By unit and group", L1.S_TITLE, None)])
    sh.add([(h, L1.S_HEAD, None) for h in ("Unit", "Group", "Verified-only: lines", "Verified-only: total",
                                            "Incl. reads to verify: lines", "Total incl. reads to verify")])
    for (unit, grp), ((vn, vt), (inn, it)) in sorted(totals_by(mto, lambda m: (m["unit"], group_of(m, run_lids)))
                                                     .items()):
        sh.add([(unit, S, None), (grp, S, None), (vn, S, None), (L1.num(vt), S, None), (inn, S, None),
                (L1.num(it), S, None)])
    sh.add([])
    sh.add([("By unit and row Status (the totals mix new, existing and demolished items)", L1.S_TITLE, None)])
    sh.add([(h, L1.S_HEAD, None) for h in ("Unit", "Row Status", "Verified-only: lines", "Verified-only: total",
                                            "Incl. reads to verify: lines", "Total incl. reads to verify")])
    for (unit, st), ((vn, vt), (inn, it)) in sorted(totals_by(
            mto, lambda m: (m["unit"], L1.ROWS_BY_LID[m["lids"][0]]["Status"])).items()):
        sh.add([(unit, S, None), (st, S, None), (vn, S, None), (L1.num(vt), S, None), (inn, S, None),
                (L1.num(it), S, None)])


def mto_tab(mto, ledger_sums, run_lids):
    sh = L1.Sheet("MTO Lines")
    sh.widths = [11, 14, 18, 11, 10, 48, 9, 6, 7, 10, 26, 14, 18, 11, 9, 11, 50, 9, 50, 16, 60]
    sh.add([(h, L1.S_HEAD, None) for h in MTO_HEADER])
    for m in mto:
        u, _ = L1.sheet_link(m["sheet"])
        cells = []
        for h, v in zip(MTO_HEADER, mto_record(m)):
            ln = None
            if h == "Ledger ID" and len(m["lids"]) == 1:
                ln = f"#'Ledger'!A{L1.LEDGER_POS[m['lids'][0]]}"
            if h == "Sheet":
                ln = u
            if h == "Quantity":
                v = L1.num(v)
            cells.append((v, L1.S_LINK if ln else L1.S_WRAP, ln))
        sh.add(cells)
    sh.add([])
    add_totals_block(sh, mto, ledger_sums, run_lids)
    sh.freeze = (1, 1)
    sh.filter = (1, len(mto) + 1, len(MTO_HEADER))
    return sh


def totals_tab(mto, ledger_sums, run_lids):
    sh = L1.Sheet("Totals")
    sh.widths = [30, 30, 14, 14, 14, 14, 16, 16, 18, 14]
    add_totals_block(sh, mto, ledger_sums, run_lids)
    sh.add([])
    sh.add([("Rules", L1.S_TITLE, None)])
    for t in ("Verified-only: lines that count (Counts To Total = Y): Verified or Verified-Visual reads, no "
              "ambiguous tie, no double count, not a duplicate or reference-only row.",
              f"{INCL}: the Verified-only lines plus lines held back only because their read is Inferred or "
              "Unresolved (Counts Incl. Reads to Verify = Y). Lines held back for any other reason stay out.",
              "Never in either total: the earthwork rows L-0448 and L-0449 (reference only, C0.2 Item 15) and the "
              "duplicate rows L-0337 and L-0338 (counted on L-0057 and L-0058).",
              "E6.3 conduit and feeder runs: one EA per run whose tag is read on a cited sheet (rev1 rule 4). "
              "E6.3 shows no lengths, so no run has an LF line. The group includes P-SEC (L-0237) and P-TPS (L-0243)."):
        sh.add([(t, L1.S_WRAP, None)])
    return sh


def fill_counts(rows, getter):
    return {c: sum(1 for r in rows if L1.filled(c, getter(r, c))) for c in HEADER}


def band_rates(counts, nrows):
    out = []
    for code, name, cols in L1.BANDS:
        out.append((code, name, len(cols), sum(counts[c] for c in cols) / (nrows * len(cols))))
    out.append(("All", "", len(HEADER), sum(counts.values()) / (nrows * len(HEADER))))
    return out


def coverage_tab(fills, built, mto):
    sh = L1.Sheet("Coverage")
    sh.widths = [30, 10, 16, 16, 16, 16, 12, 12]
    S = L1.S_WRAP
    (r0, n0), (r1, n1), (r2, n2), (r2b, nb) = fills
    sh.add([("Fill rate per band (filled cells / all cells); \"None found\", \"Not linked\", \"Not stated\", blanks, "
             "dashes and zero counts are not filled", L1.S_TITLE, None)])
    sh.add([(h, L1.S_HEAD, None) for h in ("Band", "Columns", f"rev0 ({n0} rows)", f"rev1 ({n1} rows)",
                                            f"rev2 ({n2} rows)", f"rev2 ({nb} base rows)")])
    b0, b1, b2, bb = band_rates(r0, n0), band_rates(r1, n1), band_rates(r2, n2), band_rates(r2b, nb)
    for x0, x1, x2, xb in zip(b0, b1, b2, bb):
        st = L1.S_HEAD if x0[0] == "All" else S
        sh.add([(f"{x0[0]} {x0[1]}".strip(), st, None), (x0[2], st, None), (L1.pct(x0[3]), st, None),
                (L1.pct(x1[3]), st, None), (L1.pct(x2[3]), st, None), (L1.pct(xb[3]), st, None)])
    sh.add([])
    sh.add([("Fill per column (filled cells)", L1.S_TITLE, None)])
    sh.add([(h, L1.S_HEAD, None) for h in ("Column", "Band", f"rev0 ({n0})", f"rev1 ({n1})", f"rev2 ({n2})",
                                            f"rev2 base ({nb})", "None found", "Not linked")])
    for c in HEADER:
        sh.add([(c, S, None), (L1.BAND_OF[c][0], S, None), (r0[c] if c in L1.REV0_OF else "new", S, None),
                (r1[c], S, None), (r2[c], S, None), (r2b[c], S, None),
                (sum(1 for r in built if str(r[c]).startswith(NONE_FOUND)), S, None),
                (sum(1 for r in built if str(r[c]).startswith(NOT_LINKED)), S, None)])
    sh.add([])
    sh.add([("Links by basis (row-to-document links)", L1.S_TITLE, None)])
    sh.add([(h, L1.S_HEAD, None) for h in ("Column", "tag", "spec", "sheet", "Rows with a link", "Links")])
    for c in L1.BASIS_COLS:
        cnt = Counter(x["basis"] for b in built for x in b["_links"][c])
        sh.add([(c, S, None)] + [(cnt[k], S, None) for k in BASES]
               + [(sum(1 for b in built if b["_links"][c]), S, None), (sum(cnt.values()), S, None)])
    sh.add([])
    sh.add([("MTO", L1.S_TITLE, None)])
    sh.add([(h, L1.S_HEAD, None) for h in ("Line type", "Unit", "Confidence", "Counts", "Counts incl. reads",
                                            "Lines")])
    for k, v in sorted(Counter((m["type"], m["unit"], m["conf"], m["counts"], m["incl"]) for m in mto).items()):
        sh.add([(x, S, None) for x in k] + [(v, S, None)])
    return sh


def column_guide(run_first, run_last):
    g = dict(L1.COLUMN_GUIDE)
    g["Ledger ID"] = ("L-NNNN, permanent (decision A). L-0001 to L-0447 are the rev0 rows in rev0 order; L-0448 and "
                      f"L-0449 came in rev1; {run_first} to {run_last} are the E6.3 conduit and feeder runs (rev2).",
                      "derived/reconciliation/Ledger_ID_Map.csv", "never blank")
    g["Status"] = ("New, Existing, Temporary or Demolished (carried from rev0), or \"Duplicate of L-NNNN\" for a row "
                   "the owner ruled a duplicate (rev2: L-0337, L-0338).", "Ledger rev0; owner's decisions",
                   "\"Not stated\" as in rev0")
    g["Quantity"] = ("The headline total: the sum of the row's MTO lines that count (Verified lines only, no double "
                     "counting).", "MTO Lines tab", "Not totaled: … | None found")
    g[INCL] = ("Ledger tab only (the CSV keeps the schema rev1 columns and states the same figure at the end of "
               "Quantity Confidence): the Verified-only total plus the row's lines held back only because their "
               "read is Inferred or Unresolved.", "MTO Lines tab (Counts Incl. Reads to Verify)",
               "None found | None: no line qualifies | Not totaled: …")
    g["Quantity Confidence"] = ("Tag level of the total and how many lines were or were not totaled; ends with the "
                                "total incl. reads to verify. Earthwork rows: \"Reference only (C0.2: not for "
                                "bidding or take-off)\".", "MTO Lines tab", "None found (and why)")
    g["Notes"] = ("Lane and Merge notes; \"[rev1]\" and \"[rev2]\" mark what each revision added.", "Ledger rev0",
                  "None found (no notes in rev0)")
    return g


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="output folder (default: project/02_Project_Ledger)")
    args = ap.parse_args()
    out = Path(args.out).resolve()

    schema = next(csv.reader(io.StringIO(L1.SCHEMA_REV1.read_text(encoding="utf-8"))))
    TIE("index/Ledger_Schema_rev1.csv = the CSV columns", schema == HEADER,
        f"{len(schema)} schema columns, {len(HEADER)} built")
    rows = L1.base_rows()
    for r in rows:
        r["_rev0row"] = r["_rev0"]
    changes = apply_proposals(rows)
    for r in rows:
        if r["_lid"] in DUPES:
            r["Status"] = f"Duplicate of {DUPES[r['_lid']]}"
            r["Notes"] = add_note(r["Notes"], f"[rev2] Duplicate of {DUPES[r['_lid']]} ({OWNER}): the ID stays (IDs "
                                              f"are permanent); its links moved to {DUPES[r['_lid']]} and it counts "
                                              "in no MTO total.")
    hits_for = L1.hits_by_row()
    new, cands = L1.build_new_rows(rows, hits_for)
    for r in new:
        r["_rev0row"] = None
        if r["_lid"] in EARTHWORK:
            r["Notes"] = add_note(r["Notes"], f"[rev2] {REFERENCE_ONLY} ({OWNER}, decision 3): the row stays and "
                                              "counts in no total.")
    runs_rows, runs, noise = build_runs(rows, new, cands, max(lid_num(r["_lid"]) for r in rows + new) + 1)
    run_ids = [r["_lid"] for r in runs_rows]
    roll = next(r for r in rows if r["_lid"] == ROLLUP)
    roll["Notes"] = add_note(roll["Notes"], (f"[rev2] Each E6.3 run now has its own row ({OWNER}, decision 4): "
                                              f"{run_ids[0]} to {run_ids[-1]}; P-SEC (L-0237) and P-TPS (L-0243) "
                                              "already had rows. This row stays as the roll-up and carries no MTO "
                                              "line, so nothing is counted twice."))
    allrows = rows + new + runs_rows
    for r in allrows:
        L1.ROWS_BY_LID[r["_lid"]] = r
    dup_pairs = L1.dup_pairs_from_open()
    mto, held, stats = L1.build_mto(allrows, hits_for, dup_pairs)
    mark_mto(mto, dup_pairs)
    for n, m in enumerate(mto, start=2):
        L1.MTO_ROW[m["id"]] = n
    for n, r in enumerate(allrows, start=3):
        L1.LEDGER_POS[r["_lid"]] = n
    built = L1.assemble(allrows, mto, hits_for)
    for b, r in zip(built, allrows):
        b["_rev0row"] = r["_rev0row"]
    moved = move_links(built)
    earthwork_cells(built)
    run_schedule(built, set(run_ids))
    incl_cells(built, mto)
    by_b = {b["Ledger ID"]: b for b in built}
    rev1 = L1.read_csv(REV1_CSV)

    # ---- tie-outs
    ids = [b["Ledger ID"] for b in built]
    tagged = {c["lid"] for c in changes if c["field"] == "Tag"}
    bad1 = [r["Ledger ID"] for r, b in zip(rev1, built) if r["Ledger ID"] != b["Ledger ID"] or r["Name"] != b["Name"]
            or (r["Tag"] != b["Tag"] and r["Ledger ID"] not in tagged)]
    TIE(f"All {len(rev1)} rev1 rows present, in rev1 order, with rev1 Tag and Name (Tags changed only by P-0234/P-0235)",
        len(built) >= len(rev1) and not bad1, f"{len(rev1)} rev1 rows, {len(built)} rev2 rows; differ: {bad1 or 'none'}")
    touched = {c["lid"] for c in changes} | set(DUPES) | set(DUPES.values()) | set(EARTHWORK) | {ROLLUP}
    drift = [(r["Ledger ID"], c) for r, b in zip(rev1, built) if r["Ledger ID"] not in touched for c in HEADER
             if r[c] != str(b[c]) and not (c == "Quantity Confidence" and b[c].startswith(r[c] + "; "))]
    TIE("Rows no decision touches are identical to rev1 (Quantity Confidence only gains the incl. total)", not drift,
        f"{len(rev1) - len(touched)} rows compared, {len(touched)} touched by a decision; differ: {drift[:5] or 'none'}")
    TIE("Ledger IDs unique and in the L-NNNN form", len(set(ids)) == len(ids) and all(
        re.fullmatch(r"L-\d{4}", i) for i in ids), f"{len(ids)} IDs")
    newc = [c for c in cands if c["decision"] == "Added"]
    new_ids = [r["_lid"] for r in new + runs_rows]
    TIE("Every new row passes the three-part test", sorted(c["lid"] for c in newc) == sorted(new_ids) and all(
        c["test"]["a"] and c["test"]["b"] and c["test"]["c"] and re.search(r"\[[\d.,]+\]", c["test"]["a"])
        and re.search(r"(set )?p\.\d+|Add\. 4 p\.\d+", c["test"]["a"]) for c in newc),
        f"{len(new_ids)} new rows ({len(new)} from rev1, {len(runs_rows)} E6.3 runs); each has a sheet, set page and "
        "box, a CWP by rules 1-5 and a connected document")
    never = [(r["Tag"], name) for r in runs_rows for name, fn, _ in L1.NEVER_ADD if fn(r["Tag"], r["_sheets"])]
    TIE("No new row is an I/O point, area, standard or drawing reference", not never,
        f"{len(runs_rows)} run rows checked against the never-add categories; hits: {never or 'none'}")
    sched_tags = [run_tag(x) for x in runs]
    TIE("Every E6.3 run is a Ledger row exactly once", all(
        sum(1 for b in built if b["Tag"] == t or (TAG_ID.match(t) and R.norm_tag(b["Tag"]) == R.norm_tag(t))) == 1
        for t in sched_tags), f"{len(sched_tags)} schedule runs; {len(runs_rows)} new rows, "
                              f"{len(sched_tags) - len(runs_rows)} already rows; {noise} stray OCR lines skipped")
    blanks = [(b["Ledger ID"], c) for b in built for c in HEADER if str(b[c]).strip() == ""]
    TIE("No blank cell", not blanks, f"{len(blanks)} blank cells" + (f", first {blanks[:3]}" if blanks else ""))
    lblank = [(b["Ledger ID"], c) for b in built for c in L1.LINK_COLS + [INCL]
              if str(b["_incl"] if c == INCL else b[c]).strip() == ""]
    TIE("No blank link cell (CSV and Ledger tab)", not lblank, f"{len(L1.LINK_COLS) + 1} link and total columns, "
        f"{len(built)} rows; {len(lblank)} blank")
    nobasis = [(b["Ledger ID"], c, x["label"]) for b in built for c in L1.BASIS_COLS for x in b["_links"][c]
               if x["basis"] not in BASES or f"({x['basis']})" not in b[c]]
    TIE("Every link carries its basis (tag, spec or sheet)", not nobasis, f"{len(nobasis)} links without a basis")
    order_bad = [(b["Ledger ID"], c) for b in built for c in L1.BASIS_COLS
                 if [BASES.index(x["basis"]) for x in b["_links"][c]] != sorted(
                     BASES.index(x["basis"]) for x in b["_links"][c])]
    TIE("Direct links first in every link cell", not order_bad, f"{len(order_bad)} cells out of order")
    cnt_bad = [b["Ledger ID"] for b in built if b["Submittal Count"] != len(b["_links"]["Submittal IDs"])
               or b["Inspection/Test Count"] != len(b["_links"]["Inspection/Test IDs"])
               or b["Conflict/Gap Count"] != len(b["_links"]["Conflict/Gap IDs"])]
    TIE("Counts = linked IDs", not cnt_bad, f"{len(cnt_bad)} rows differ")
    dup_left = [(d, c) for d in DUPES for c in L1.BASIS_COLS if by_b[d]["_links"][c]]
    dup_lost = [(d, c, lab) for d, labs in moved.items() for c, lab, _ in labs
                if lab not in [x["label"] for x in by_b[DUPES[d]]["_links"][c]]]
    TIE("Duplicate rows keep no links; their twins carry every moved link", not dup_left and not dup_lost,
        "; ".join(f"{d} -> {DUPES[d]}: {len(moved[d])} links added" for d in DUPES))
    # both totals, per row and per unit
    ledger_sums, qbad = {}, []
    for flag, col in (("counts", "Quantity"), ("incl", "_incl")):
        for b in built:
            lines = [m for m in mto if m["lids"] == [b["Ledger ID"]] and m[flag] == "Y"]
            q = b[col]
            if NUM_RE.fullmatch(str(q)):
                unit = b["Unit"] if flag == "counts" else b.get("_incl_unit")
                if abs(sum(float(m["qty"]) for m in lines) - float(q)) > 1e-9 or {m["unit"] for m in lines} != {unit}:
                    qbad.append((flag, b["Ledger ID"]))
            elif lines:
                qbad.append((flag, b["Ledger ID"]))
    for unit in sorted({m["unit"] for m in mto}):
        vr = [b for b in built if b["Unit"] == unit and NUM_RE.fullmatch(str(b["Quantity"]))]
        ir = [b for b in built if b.get("_incl_unit") == unit and NUM_RE.fullmatch(str(b["_incl"]))]
        ledger_sums[unit] = (len(vr), sum(float(b["Quantity"]) for b in vr), len(ir), sum(float(b["_incl"]) for b in ir))
    trows = totals_rows(mto, ledger_sums)
    TIE("Verified-only totals tie to their lines (each row, and each unit overall)",
        not [x for x in qbad if x[0] == "counts"] and all(abs(vt - vs) < 1e-9 for _, _, vt, _, vs, *_ in trows),
        "; ".join(f"{u}: {L1.num(vt)} from {vn} lines = {L1.num(vs)} on {vr} rows" for u, vn, vt, vr, vs, *_ in trows))
    TIE("Totals incl. reads to verify tie to their lines (each row, and each unit overall)",
        not [x for x in qbad if x[0] == "incl"] and all(abs(it - is_) < 1e-9 for *_, it, _, is_ in trows),
        "; ".join(f"{u}: {L1.num(it)} from {inn} lines = {L1.num(is_)} on {ir} rows"
                  for u, *_, inn, it, ir, is_ in trows))
    TIE("Every line that counts is also in the incl. total; incl. >= Verified-only per unit",
        all(m["incl"] == "Y" for m in mto if m["counts"] == "Y") and all(it >= vt for _, _, vt, _, _, _, it, _, _
                                                                          in trows),
        f"{sum(1 for m in mto if m['counts'] == 'Y')} lines count, {sum(1 for m in mto if m['incl'] == 'Y')} in "
        "the incl. total")
    TIE("Verified-only totals use Verified lines only", all(m["conf"] in STRONG for m in mto if m["counts"] == "Y"),
        f"{sum(1 for m in mto if m['counts'] == 'Y')} lines count")
    TIE("Incl. totals add only lines held back for their read level",
        all(m["counts"] == "Y" or all(SOFT_RE.match(w) for w in m["why"]) for m in mto if m["incl"] == "Y"),
        f"{sum(1 for m in mto if m['incl'] == 'Y' and m['counts'] == 'N')} lines added by reads to verify")
    excl = [m["id"] for m in mto if any(x in DUPES or x in EARTHWORK for x in m["lids"])
            and (m["counts"] == "Y" or m["incl"] == "Y")]
    TIE("Duplicate and earthwork rows count in no total", not excl,
        f"{sum(1 for m in mto if any(x in DUPES or x in EARTHWORK for x in m['lids']))} lines on those rows, "
        f"{len(excl)} counted")
    TIE("No MTO line is a dimension, elevation, slope or size", all(m["unit"] in R.MTO_UNITS for m in mto),
        f"units {sorted({m['unit'] for m in mto})}")
    TIE("MTO callouts = lines + held", sum(1 for m in mto if m["type"] == "callout") + len(held) == stats["callouts"],
        f"{stats['callouts']} callouts, {sum(1 for m in mto if m['type'] == 'callout')} lines, {len(held)} held")
    TIE("Every unmatched tag is a candidate", {c["tag"] for c in cands if c["src"] == "Prompt 9 unmatched tag"}
        == {u["Tag Text"] for u in R.UNMATCHED}, f"{len(R.UNMATCHED)} unmatched tags")
    if L1.FAILS:
        sys.exit("Stopped: tie-out failed, nothing written:\n  " + "\n  ".join(L1.FAILS))

    # ---- files
    ledger_csv = L1.csv_text(HEADER, [[b[c] for c in HEADER] for b in built])
    mto_csv = L1.csv_text(MTO_HEADER, [mto_record(m) for m in mto])
    links_sh, pos = L1.links_tab(built)
    ledger_sh = ledger_tab(built, pos)
    base = [b for b in built if b["_rev0row"] is not None]
    fills = [(fill_counts(base, lambda r, c: r["_rev0row"][L1.REV0_OF[c]] if c in L1.REV0_OF else ""), len(base)),
             (fill_counts(rev1, lambda r, c: r[c]), len(rev1)),
             (fill_counts(built, lambda r, c: r[c]), len(built)),
             (fill_counts(base, lambda r, c: r[c]), len(base))]
    run_lids = set(run_ids) | {"L-0237", "L-0243"}
    cand_recs = [[n, c["src"], c["tag"], c["name"] or "—", c["sheets"], c["first"], c["level"],
                  c["test"]["a"] or "No", c["test"]["b"] or "No", c["test"]["c"] or "No", c["cat"] or "—",
                  c["decision"], c["reason"], c["lid"] or "—"] for n, c in enumerate(cands, start=1)]
    guide_map = column_guide(run_ids[0], run_ids[-1])
    guide = [[BAND_NAME[c], c, *guide_map[c]] for c in HEADER_TAB]
    guide += [["", "", "", "", ""],
              ["Rules", "Blank cells", "None found = searched and empty; Not linked = the source doesn't cover the "
                                      "row; counts show 0.", "", ""],
              ["Rules", "Link basis", "tag = the source names this row (its Tag or Ledger ID); spec = the source "
                                     "applies to a spec section the row cites; sheet = same sheet. Direct (tag) links "
                                     "first.", "", ""],
              ["Rules", "Links", "In the Ledger tab a cell with one link opens it; a cell with several opens the Links "
                                "tab at that row and column (repo links for now).", "", ""],
              ["Rules", "Quantities", "EA for each tagged component found on one of its cited sheets (E6.3 runs "
                                     "included); callout lines by the Prompt 9 tie rules on every sheet; no dimensions, "
                                     "elevations, slopes or sizes; no double counting; Add. 4 governs. Verified-only is "
                                     "the headline; the total incl. reads to verify sits beside it (Totals tab).",
               "", ""],
              ["Rules", "Duplicates", "L-0337 and L-0338 are duplicates of L-0057 and L-0058 (owner's decision 2): IDs "
                                     "kept, links moved to the twin, no total.", "", ""],
              ["Rules", "Confidence", "Verified (text layer), Verified-Visual (page image), Inferred (derived; OCR and "
                                     "Bluebeam reads), Unresolved (conflict or missing).", "", ""]]
    sheets = [ledger_sh, mto_tab(mto, ledger_sums, run_lids), totals_tab(mto, ledger_sums, run_lids),
              coverage_tab(fills, built, mto),
              L1.table_tab("Candidates", L1.CAND_HEADER, cand_recs, [8, 30, 22, 36, 26, 36, 10, 36, 34, 40, 26, 10,
                                                                      60, 10]),
              L1.table_tab("Column Guide", ["Band", "Column", "What it holds", "Source", "When there is nothing"],
                           guide, [20, 24, 90, 44, 44]),
              links_sh]
    xlsx = L1.write_xlsx(sheets)
    summary = summary_md(built, new, runs_rows, runs, cands, mto, changes, moved, fills, trows, run_lids,
                         sum(len(x) for b in built for x in b["_links"].values()), held, stats)
    files = {"Project_Ledger_rev2.csv": ledger_csv.encode("utf-8"), "MTO_Lines_rev2.csv": mto_csv.encode("utf-8"),
             "Project_Ledger_rev2.xlsx": xlsx, "Ledger_rev2_Summary.md": summary.encode("utf-8")}
    out.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (out / name).write_bytes(data)
    print(f"wrote {len(files)} files to {out}: {len(built)} rows ({len(runs_rows)} E6.3 runs new), {len(mto)} MTO "
          f"lines ({sum(1 for m in mto if m['counts'] == 'Y')} count, {sum(1 for m in mto if m['incl'] == 'Y')} incl. "
          f"reads to verify), {len(cands)} candidates")
    for name, ok, detail in L1.TIES:
        print(f"  {ok}: {name} ({detail})")


BAND_NAME = {c: f"{code} {name}" for code, name, cols in BANDS_TAB for c in cols}


# ---------------------------------------------------------------- summary

def summary_md(built, new, runs_rows, runs, cands, mto, changes, moved, fills, trows, run_lids, nlinks, held,
               stats):
    (r0, n0), (r1, n1), (r2, n2), (r2b, nb) = fills
    b0, b1, b2, bb = band_rates(r0, n0), band_rates(r1, n1), band_rates(r2, n2), band_rates(r2b, nb)
    by = {b["Ledger ID"]: b for b in built}
    first, last = runs_rows[0]["_lid"], runs_rows[-1]["_lid"]
    L = ["# Project Ledger rev2 — Summary", "",
         "Prompt 11: rev1 plus the owner's six decisions. rev2 is the current Ledger; rev0 (`Project_Ledger.csv`) and "
         "rev1 (`Project_Ledger_rev1.csv`) are history and unchanged. Built by "
         "`testbeds/eastsound/tools/build_ledger_rev2.py`, which imports `build_ledger_rev1.py` (no LLM calls, "
         "deterministic, no library reads).", "",
         "## Files", "",
         "| File | What it holds |", "|---|---|",
         f"| Project_Ledger_rev2.csv | {len(built)} rows × {len(HEADER)} columns, in `index/Ledger_Schema_rev1.csv` "
         "order |",
         "| Project_Ledger_rev2.xlsx | The rev1 tabs (Ledger, MTO Lines, Coverage, Candidates, Column Guide, Links) "
         f"plus Totals. The Ledger tab adds \"{INCL}\" beside Quantity |",
         f"| MTO_Lines_rev2.csv | {len(mto)} MTO lines (machine copy of the MTO Lines tab; the graph reads it) |",
         "| Ledger_rev2_Summary.md | This file |", "",
         "## Changes applied", "",
         "### 1. The 14 Verified proposals (Ledger_Update_Proposal.csv)", "",
         "The 229 \"needs check\" proposals are left as they are.", "",
         "| Proposal | Ledger ID | Tag (rev1) | Change | Evidence |", "|---|---|---|---|---|"]
    L += [f"| {c['no']} | {c['lid']} | {c['tag']} | {c['what']} | {c['evidence']} |" for c in changes]
    L += ["", "### 2. Hot Box duplicates", "",
          "L-0337 and L-0338 keep their IDs (IDs are permanent). Their Tags are the printed \"Hot Box #1\" and "
          "\"Hot Box #2\" (P-0234, P-0235), their Status is \"Duplicate of L-0057\" and \"Duplicate of L-0058\", and "
          "they count in no MTO total. Their link cells read \"Not linked (duplicate of …; links moved there)\". "
          "Drawing Sheets and the schedule columns stay on the duplicates, so no needs-check sheet moves onto "
          "L-0057/L-0058.", "", "| Duplicate | Twin | Links moved (new on the twin) |", "|---|---|---|"]
    for d, labs in moved.items():
        L.append(f"| {d} | {DUPES[d]} | " + ("; ".join(f"{c} {lab} ({bas})" for c, lab, bas in labs) or "none") + " |")
    L += ["", "### 3. Earthwork", "",
          f"L-0448 (cut) and L-0449 (fill) stay. Quantity Confidence reads \"{REFERENCE_ONLY}\"; their MTO lines "
          "(MTO-0113, MTO-0114) count in neither total. The fill read (Bluebeam 1598 CY against the Wiki note's 1,596 "
          "CY) is still for a person to check on the page image.", "",
          "### 4. E6.3 conduit and feeder runs", "",
          f"Every run on the E6.3 power and control/signal schedules is its own row: {len(runs_rows)} new rows, "
          f"{first} to {last}. P-SEC (L-0237) and P-TPS (L-0243) already had rows and are not added again. "
          "C-2W and P-2W, held in rev1, come in with the group. The roll-up row L-0353 stays and carries no MTO line.",
          "",
          "- **Read:** the Tesseract words of `derived/ocr/pages/076_E6.3.json`, checked line by line against the "
          "Bluebeam words at the same height. Columns are cut at the whitespace gaps between the header words. A line "
          "with no ID continues the run above it; a line whose ID cell holds only a dash is an unnamed circuit.",
          f"- **Counts:** {sum(1 for x in runs if x['kind'] == 'Control and signal' and TAG_ID.match(x['id']))} named "
          "control/signal runs plus a DC spare, and "
          f"{sum(1 for x in runs if x['kind'] == 'Power' and TAG_ID.match(x['id']))} named power runs plus "
          f"{sum(1 for x in runs if not x['id'])} unnamed UV controller circuits plus an AC spare. These are the "
          "counts Wiki note E6.3 gives (tie-out below).",
          "- **Row:** the Tag as printed on E6.3, or PROPOSED- for the unnamed circuits and spares. The Name holds "
          "voltage, conduit, conductors, GND, from and to, as read. E6.3 shows no lengths. CWP 26 (rule 1, Spec 26 05 "
          "19). Spec Sections, Bid Item 6 and Status New follow the roll-up row L-0353 (Inferred); a run that reads "
          "(FUTURE) is Status Not stated. Drawing Sheets are E6.3 plus every sheet where the tag (or its plan "
          "spelling) is read in the native text layer. The Schedule Activity is L-0353's, via the roll-up.",
          "- **Confidence:** Inferred, except Unresolved where the two OCR reads disagree, or where Wiki note E6.3 "
          "records a disagreement with another sheet (P-IP1 to P-IP4, P-2W, P-LT).",
          "- **MTO:** one EA per run whose tag is read on a cited sheet (rev1 rule 4). The best read is the text "
          "layer, so these lines are Verified. PROPOSED rows get none.", "",
          "| Ledger ID | Tag | Confidence | Drawing Sheets | Quantity | From → to (as read) |", "|---|---|---|---|---|---|"]
    for r in runs_rows:
        v = r["_run"]["lines"][0]["vals"]
        b = by[r["_lid"]]
        L.append(f"| {r['_lid']} | {r['Tag']} | {b['Confidence']} | {b['Drawing Sheets']} | "
                 f"{b['Quantity']} {b['Unit'] if NUM_RE.fullmatch(str(b['Quantity'])) else ''} | "
                 f"{v['FROM'] or '—'} → {v['TO'] or '—'} |".replace("  |", " |"))
    reads = [(r["_lid"], r["Tag"], [f"{c} Tesseract {a!r}, Bluebeam {b!r} — {how or 'Unresolved; a person checks'}"
                                     for c, a, b, how in ln["disputes"]]
              + [f"{c} Tesseract {a!r}, Bluebeam {b!r} — taken as the same text (Bluebeam carries extra or split "
                 "words)" for c, a, b in ln["variants"]])
             for r in runs_rows for ln in r["_run"]["lines"] if ln["disputes"] or ln["variants"]]
    if reads:
        L += ["", "Read checks where the Tesseract and Bluebeam text differs (spacing aside):", ""]
        L += [f"- {lid} {tag}: " + "; ".join(xs) for lid, tag, xs in reads]
    L += ["", "### 5. Two totals", "",
          f"Verified-only stays the headline (Quantity). \"{INCL}\" adds the lines held back only because their read "
          "is Inferred or Unresolved. It sits beside the headline on the Ledger tab and the Totals tab, and at the end "
          "of Quantity Confidence in the CSV. A line held back for any other reason stays out of both totals: an "
          "ambiguous tie, a double count, a duplicate or reference-only row, or a row measured in LF. A duplicate pair "
          "named by an open item counts once in each total.", "",
          "### 6. Current Ledger", "",
          "The 02_Project_Ledger README and the project README name Project_Ledger_rev2 as current, with rev0 and rev1 "
          "as history. The graph is rebuilt from rev2 and MTO_Lines_rev2.csv.", "",
          "## Fill rate per band, rev0 → rev1 → rev2", "",
          "Filled = the cell carries a fact. \"None found\", \"Not linked\", \"Not stated\", blanks, dashes, zero "
          "counts and an all-zero link basis count as not filled. rev0 counts its own values for the columns it had; "
          "columns new in rev1 start at 0.", "",
          f"| Band | Columns | rev0 ({n0} rows) | rev1 ({n1} rows) | rev2 ({n2} rows) | rev2, {nb} base rows |",
          "|---|---|---|---|---|---|"]
    for x0, x1, x2, xb in zip(b0, b1, b2, bb):
        lab = "**All**" if x0[0] == "All" else f"{x0[0]} {x0[1]}"
        L.append(f"| {lab} | {x0[2]} | {L1.pct(x0[3])} | {L1.pct(x1[3])} | {L1.pct(x2[3])} | {L1.pct(xb[3])} |")
    L += ["", "## Rows added", "",
          f"rev2 has {n2} rows: the {n1} rev1 rows in rev1 order (447 rev0 rows, then L-0448 and L-0449) and "
          f"{len(runs_rows)} E6.3 run rows ({first} to {last}).", "",
          "| Group | Rows |", "|---|---|"]
    for k, v in sorted(Counter(("E6.3 " + x["_run"]["kind"].lower() + (" run" if TAG_ID.match(x["_run"]["id"]) else
                                 " spare" if x["_run"]["id"] == "SPARE" else " unnamed circuit"))
                               for x in runs_rows).items()):
        L.append(f"| {k} | {v} |")
    L += ["", "## Totals", "",
          "| Unit | Verified-only lines | Verified-only total | Lines incl. reads to verify | Total incl. reads to "
          "verify | Added by reads to verify | Ledger rows (Verified / incl.) |", "|---|---|---|---|---|---|---|"]
    for unit, vn, vt, vr, vs, inn, it, ir, is_ in trows:
        L.append(f"| {unit} | {vn} | **{L1.num(vt)}** | {inn} | {L1.num(it)} | {L1.num(it - vt)} | {vr} / {ir} |")
    L += ["", "By group:", "", "| Unit | Group | Verified-only lines | Verified-only total | Lines incl. reads | "
          "Total incl. reads |", "|---|---|---|---|---|---|"]
    for (unit, grp), ((vn, vt), (inn, it)) in sorted(totals_by(mto, lambda m: (m["unit"], group_of(m, run_lids)))
                                                     .items()):
        L.append(f"| {unit} | {grp} | {vn} | {L1.num(vt)} | {inn} | {L1.num(it)} |")
    L += ["", "By row Status (the totals mix new, existing and demolished items):", "",
          "| Unit | Row Status | Verified-only lines | Verified-only total | Lines incl. reads | Total incl. reads |",
          "|---|---|---|---|---|---|"]
    for (unit, st), ((vn, vt), (inn, it)) in sorted(totals_by(
            mto, lambda m: (m["unit"], L1.ROWS_BY_LID[m["lids"][0]]["Status"])).items()):
        L.append(f"| {unit} | {st} | {vn} | {L1.num(vt)} | {inn} | {L1.num(it)} |")
    why = Counter()
    for m in mto:
        if m["incl"] == "N":
            for w in m["why"]:
                why[re.sub(r" \(.*|: .*|L-\d{4}.*| per OI.*|; owner.*", "", w).strip()] += 1
    L += ["", f"Lines in neither total: {sum(1 for m in mto if m['incl'] == 'N')} of {len(mto)}. Reasons (a line may "
          "have more than one):", ""]
    L += [f"- {k}: {v}" for k, v in sorted(why.items(), key=lambda kv: (-kv[1], kv[0]))]
    groups = L1.dup_groups(mto)
    L += ["", "Open duplicate items that name three or more rows, where two or more of those rows have a counted "
          "line. They are counted on each row; a person confirms they are separate components:", ""]
    L += [f"- {oi}: " + ", ".join(x + " " + L1.ROWS_BY_LID[x]["Tag"] for x in ids) + f" — {title[:160]}"
          for oi, ids, title in groups if not set(DUPES) & set(LID_LIST(oi))] or ["- None."]
    L += ["- OI-0005 (Hot Box #1/#2 and their twins) is settled by decision 2."]
    L += ["", "## Candidates", "",
          f"{len(cands)} candidates (Candidates tab, one row each with the test result and reason).", "",
          "| Source | Decision | Candidates |", "|---|---|---|"]
    for (src, dec), v in sorted(Counter((c["src"], c["decision"]) for c in cands).items()):
        L.append(f"| {src} | {dec} | {v} |")
    L += ["", "## MTO", "",
          f"- {len(mto)} lines: {sum(1 for m in mto if m['type'] == 'callout')} callout, "
          f"{sum(1 for m in mto if m['type'] == 'tag count')} tag count. "
          f"{sum(1 for m in mto if m['counts'] == 'Y')} count Verified-only; "
          f"{sum(1 for m in mto if m['incl'] == 'Y')} count incl. reads to verify.",
          f"- Callouts: {stats['leads']} leads, {stats['superseded']} on base pages Add. 4 supersedes, "
          f"{stats['callouts']} callouts, {sum(1 for m in mto if m['type'] == 'callout')} lines, {len(held)} held "
          "(the rev1 rules, unchanged).",
          "- MTO-0001 to MTO-0114 keep their rev1 numbers; the run lines follow.", "",
          "## Rules and judgment calls", "",
          "- **Proposals.** Each is checked against the rev0 value it names before it is applied; the three L-0057 "
          "sheet adds stack. Each changed row's Notes and Source Citation name the proposal and its evidence.",
          "- **TS, T3, T2.** Verified as the owner decided. Their Notes still record the Inferred facts the proposals "
          "flagged (Status New), which the owner accepted with the change.",
          "- **Duplicates.** \"Links\" are the link columns (Found On, MTO Line IDs, Wiki Note(s), Submittal IDs, "
          "Inspection/Test IDs, RFI IDs, Conflict/Gap IDs, Exception Refs). A link already on the twin keeps the "
          "stronger basis. Drawing Sheets and the schedule columns stay on the duplicate.",
          "- **Runs.** Values are machine reads, so the rows are Inferred. Where the Tesseract and Bluebeam reads of a "
          "cell differ and Wiki note E6.3 prints exactly one of them (four characters or more), that one is used; "
          "otherwise both are shown and the row is Unresolved. A plan spelling (P-BL1 for P-BL-1) counts as the same "
          "tag; Wiki note E6.3 calls these cosmetic.",
          "- **Incl. total for duplicate pairs.** When an open item names exactly two rows and both have a line in "
          "the incl. total, the line of the row without a Verified count drops out, so the pair counts once.",
          "- **Links** are repo links on `main`, as in rev1.", "",
          "## Tie-outs", "", "| Check | Result | Detail |", "|---|---|---|"]
    L += [f"| {n} | {ok} | {d} |" for n, ok, d in L1.TIES]
    pages = page_files()
    pages_sha = hashlib.sha256("".join(sha(p) for p in pages).encode()).hexdigest()
    L += ["", f"Links written: {nlinks} (Links tab).", "", "## Inputs (SHA-256)", "", "| File | SHA-256 |", "|---|---|"]
    ins = L1.INPUT_FILES + [L1.SCHEMA_REV1, REV1_CSV, PROPOSALS, RUN_PAGE, HERE / "build_ledger_rev1.py"]
    L += [f"| {rel(p)} | {sha(p)} |" for p in sorted(set(ins), key=lambda p: rel(p))]
    L.append(f"| testbeds/eastsound/derived/ocr/pages/ ({len(pages)} files; SHA-256 of their SHA-256 values in name "
             f"order) | {pages_sha} |")
    return "\n".join(L) + "\n"


def LID_LIST(oi):
    for _, o in L1.OPEN:
        if o["Item ID"] == oi:
            return L1.LID_RE.findall(o["Ledger IDs"])
    return []


if __name__ == "__main__":
    main()
