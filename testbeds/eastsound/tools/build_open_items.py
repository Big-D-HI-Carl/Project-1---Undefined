#!/usr/bin/env python3
"""Build one open-items list for the Eastsound test bed: RFIs, conflicts, gaps, duplicates and checks.

Inputs (read-only):
  testbeds/eastsound/derived/reconciliation/   Summary.md, Ledger_Update_Proposal.csv, Ledger_ID_Map.csv
  testbeds/eastsound/project/03_Exceptions_and_Issues/   Exception_Report.md, Project_Known_Issues.md,
                                               Issues_Log.csv (the Merge Issues Log)
  testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv   only to map Exception numbers and lane
                                               issue IDs to Ledger rows, then to Ledger IDs
  ISSUES_LOG.md                                open entries that concern the drawings or specs

Outputs: testbeds/eastsound/derived/issues/Open_Items.csv and Open_Items_Summary.md. Nothing else is written.

No LLM calls and no library reads. Rows follow a fixed source order, lists inside a cell are sorted, line
endings are LF, files are UTF-8 without a BOM and there are no timestamps, so two runs on the same inputs
give identical bytes. The run stops, writing nothing, if a tie-out fails (listed at the end of the summary).

Run from the repo root (stdlib only):
  python testbeds/eastsound/tools/build_open_items.py [--out <folder>]
"""

import argparse
import csv
import hashlib
import io
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]   # this file: testbeds/eastsound/tools/
TB = REPO / "testbeds" / "eastsound"
REC = TB / "derived" / "reconciliation"
EXC_DIR = TB / "project" / "03_Exceptions_and_Issues"
SUMMARY_MD = REC / "Summary.md"
PROPOSALS = REC / "Ledger_Update_Proposal.csv"
ID_MAP = REC / "Ledger_ID_Map.csv"
EXC_MD = EXC_DIR / "Exception_Report.md"
KNOWN_MD = EXC_DIR / "Project_Known_Issues.md"
MERGE_LOG = EXC_DIR / "Issues_Log.csv"
LEDGER = TB / "project" / "02_Project_Ledger" / "Project_Ledger.csv"
ISSUES_LOG = REPO / "ISSUES_LOG.md"
OUT_DEFAULT = TB / "derived" / "issues"
INPUTS = (SUMMARY_MD, PROPOSALS, ID_MAP, EXC_MD, KNOWN_MD, MERGE_LOG, LEDGER, ISSUES_LOG)

COLUMNS = ["Item ID", "Title", "Type", "Ledger IDs", "Sheets", "Spec Sections", "Source Citation",
           "Confidence", "Status"]
TYPES = ("RFI", "conflict", "gap", "duplicate", "check")
TAG_ORDER = {"Unresolved": 0, "Inferred": 1, "Verified-Visual": 2, "Verified": 3}
DEFAULT_TAG = "Inferred"   # no tag stated: compiled by Merge or a lane, not re-read in this step
TITLE_MAX = 220
CITE_PART_MAX = 400

SHEET_RE = re.compile(r"\b([ACEGMS])(\d{1,2})\.(\d{1,2})([A-Z]?)\b")
SPEC_RE = re.compile(r"(?<![\d.])(\d{2}) (\d{2}) (\d{2})(?![\d.]|\w)")
BRACKET_RE = re.compile(r"[\[(]([^\[\]()]*)[\])]")
TAG_WORD_RE = re.compile(r"\b(Verified-Visual|Verified|Inferred|Unresolved)\b")
EXC_REF_RE = re.compile(r"#(\d+)")
MERGE_PTR_RE = re.compile(r"\[Merge\] Exceptions: ([#\d, ]+)")
LANES = ("Civil & Site", "Process & Mechanical", "Electrical & Controls", "Structural & Building",
         "Contract & General")
LANE_ISSUE_RE = re.compile(r"^(" + "|".join(re.escape(x) for x in LANES) + r") Issues? (.+?):")
ABBREV = {"Add", "Det", "No", "p", "pp", "Sch", "Mod", "St", "in", "ft", "e.g", "i.e", "vs", "Div", "approx"}

# Exception Report types and what each becomes here. Type 8 (PROPOSED tag approvals) is tag housekeeping,
# not a drawing or spec item; it stays in the Exception Report and is counted in the summary.
EXC_TYPES = {
    "Same tag, different attributes": 1,
    "Same item, different tags (not combined)": 2,
    "Drawing with no spec, or spec with no drawing": 3,
    "Bid item with no Ledger rows": 4,
    "Add. 4 item not recorded by any lane": 5,
    "Cross-lane item (Issues file)": 6,
    "03 carry-forward flag": 7,
    "PROPOSED tag awaiting approval": 8,
}

# ---------------------------------------------------------------- curated items (the owner named these)
# Each one names the source lines it rests on; the run stops if any anchor is missing from its file.
# "claims" are the source rows it absorbs, so they are not listed again.

CURATED = [
    {
        "key": "CUR:gen-rfi",
        "title": "Generator rating RFI: drawings show a 125 kW / 156 kVA standby generator (E1.1, E6.1); "
                 "26 32 13 ¶2.03 C.1 requires not less than 150.0 kW standby. Which governs, and do the "
                 "250/3 breaker, P-GEN feeder and pad change with it?",
        "type": "RFI",
        "ledger": {"L-0242": "GEN"},
        "sheets": ["E1.1", "E6.1"],
        "specs": ["26 32 13"],
        "cite": "reconciliation/Summary.md, RFI: generator rating (L-0242 GEN); Ledger_Update_Proposal.csv "
                "P-0241; E1.1 (set p.66) \"480Y/277V 125\" / \"kW DIESEL\"; E6.1 (set p.74) \"125kW / 156kVA\"; "
                "26 32 13 ¶2.03 C.1 (main spec p.326) \"not less than 150.0kW\" (all native text layer). "
                "Precedence between drawings and specs not checked in Prompt 9",
        "confidence": "Verified",
        "status": "Open — Engineer (RFI); drafted, owner to send",
        "anchors": [(SUMMARY_MD, "## RFI: generator rating (L-0242 GEN)"),
                    (SUMMARY_MD, "26 32 13 ¶2.03 C.1 (main spec p.326)"),
                    (SUMMARY_MD, "not less than 150.0kW"),
                    (ISSUES_LOG, "**Generator rating.**")],
        "claims": ["P:P-0241"],
    },
    {
        "key": "CUR:bid18",
        "title": "Bid Item 18: Add. 4 Clarification 5 calls the temporary back-up generator \"Bid Item #18\"; "
                 "the base bid form Item 18 is Train 3 stainless steel fabrication above water surface "
                 "(Bid Alternate 1). Add. 4 does not reissue the bid form.",
        "type": "conflict",
        "ledger": "bid18",
        "sheets": [],
        "specs": ["00 24 13", "00 31 13", "00 41 00", "26 05 00"],
        "cite": "Exception_Report.md #255: Add. 4 p.1 Clarification 5 \"Temporary Back Up Generator (Bid Item "
                "#18)\" vs 00 41 00 p.25 Item 18 and 00 24 13 ¶18 p.20 (04; Verified); base temporary generator "
                "00 31 13 p.21, 26 05 00 ¶1.016 C p.276 and ¶3.03 E.5 p.279 (04; Verified); reconciliation/"
                "Summary.md, Division 26 review (ATS: Add. 4 governs as the later document; row to Inferred); "
                "Ledger_Update_Proposal.csv P-0238, P-0239 (Add. 4 p.1, native text layer)",
        "confidence": "Verified",
        "status": "Open — Owner; needs Addenda 1–3 or the conformed bid form",
        "anchors": [(EXC_MD, "| 255 | 03 carry-forward flag | Bid Item #18"),
                    (SUMMARY_MD, "ATS: Add. 4 cites \"Bid Item #18\" for the temporary generator"),
                    (KNOWN_MD, "| Known 17 | Temporary generator bid item |")],
        "claims": ["P:P-0238", "P:P-0239", "EXC:255", "PB:48"],
    },
    {
        "key": "CUR:fence",
        "title": "Chain link fence: C2.1 keyed notes 6 (149 LF) and 8 (134 LF) of 6-ft chain link have no "
                 "Ledger row; L-0088 (126 LF, C2.5 keyed note 4) cites C2.5 and C2.1; L-0018 (149 LF removed, "
                 "C0.5 keyed note 16). Separate runs, covered by L-0088, or the line of the removed 149 LF?",
        "type": "conflict",
        "ledger": {"L-0018": "PROPOSED-Existing chain link fence 149 LF",
                   "L-0088": "PROPOSED-Chain link fence 126 LF"},
        "sheets": ["C0.5", "C2.1", "C2.5"],
        "specs": ["02 83 00"],
        "cite": "reconciliation/Summary.md, Chain link fence: for the owner's decision (C2.1 KN 6 and 8, C2.5 "
                "KN 4, C0.5 KN 16 and 20; OCR and Bluebeam reads, Inferred; C0.5 by-order numbers "
                "Unresolved); 02 83 00 ¶1.01 A fence height (Project_Known_Issues.md Part C, CS-12)",
        "confidence": "Inferred",
        "status": "Open — Owner/Engineer",
        "anchors": [(SUMMARY_MD, "## Chain link fence: for the owner's decision (not resolved)"),
                    (SUMMARY_MD, "(6) = 149 LF OF 6’ CHAIN LINK"),
                    (MERGE_LOG, "C2.1 shows 149 LF and 134 LF of 6-ft chain link fence"),
                    (ISSUES_LOG, "**Chain link fence.**")],
        "claims": ["MRG:55"],
    },
    {
        "key": "CUR:sd23",
        "title": "C2.3 storm drain lengths: callouts 20, 39 and 44 LF are untied; 28 + 20 LF = SD-2's 48 LF "
                 "and 39 + 44 LF = SD-3's 83 LF (arithmetic only). Confirm the segments on C2.3.",
        "type": "check",
        "ledger": {"L-0117": "SD-2", "L-0118": "SD-3"},
        "sheets": ["C2.3"],
        "specs": [],
        "cite": "reconciliation/Summary.md, Segment sums (Inferred leads, nothing tied) and Open decisions "
                "item 5; Held quantity leads, C2.3 (set p.22; OCR and Bluebeam reads)",
        "confidence": "Inferred",
        "status": "Open — person check",
        "anchors": [(SUMMARY_MD, "| L-0117 | SD-2 | 48 LF | C2.3 |"),
                    (SUMMARY_MD, "| L-0118 | SD-3 | 83 LF | C2.3 |"),
                    (SUMMARY_MD, "C2.3 callouts 20, 39 and 44 LF are untied")],
        "claims": [],
    },
    {
        "key": "CUR:hotbox",
        "title": "Hot Box duplicates: L-0337 PROPOSED-Hot-Box-1 and L-0338 PROPOSED-Hot-Box-2 (Electrical & "
                 "Controls) read as the printed \"Hot Box #1\" / \"Hot Box #2\" on E4.3, the tags of L-0057 and "
                 "L-0058 (Civil & Site). Keep both rows (decision A) or merge.",
        "type": "duplicate",
        "ledger": {"L-0057": "Hot Box #1", "L-0058": "Hot Box #2",
                   "L-0337": "PROPOSED-Hot-Box-1", "L-0338": "PROPOSED-Hot-Box-2"},
        "sheets": ["C1.3", "C7.6", "E4.3"],
        "specs": [],
        "cite": "reconciliation/Summary.md, Open decisions item 3; Ledger_Update_Proposal.csv P-0234, P-0235 "
                "(E4.3 set p.72, native text layer \"HOT BOX#1\", \"HOT BOX#2\"); Exception_Report.md #16, #17 "
                "(printed tag vs PROPOSED tag; C1.3 Add. 4 p.7, C7.6 Det. 1–3)",
        "confidence": "Verified",
        "status": "Open — Merge; owner decides keep both rows or merge",
        "anchors": [(SUMMARY_MD, "L-0337 PROPOSED-Hot-Box-1 and L-0338 PROPOSED-Hot-Box-2 carry the printed "
                                 "tags of L-0057 and L-0058"),
                    (EXC_MD, "| 16 | Same tag, different attributes | Printed tag vs PROPOSED tag — Hot Box #1"),
                    (EXC_MD, "| 17 | Same tag, different attributes | Printed tag vs PROPOSED tag — Hot Box #2"),
                    (ISSUES_LOG, "**Hot Box duplicates.**")],
        "claims": ["P:P-0234", "P:P-0235", "EXC:16", "EXC:17"],
    },
    {
        "key": "CUR:s-sheets",
        "title": "Add. 4 reissues of S2.3 and S4.1 (Add. 4 pp.9–10) show revision 3 \"Blower Building\", TH, "
                 "2/8/23; 01 item 12 says the reissues carry no Add. 4 revision entry. Add. 4 pp.4–8 (A1.1, "
                 "A1.2, C6.4, C1.3, C1.6A) not checked.",
        "type": "conflict",
        "ledger": {},
        "sheets": ["S2.3", "S4.1"],
        "specs": [],
        "cite": "ISSUES_LOG.md 2026-09-30 \"Add. 4 S-sheet reissues carry a revision entry; 01 item 12 says "
                "they don't\" (native Add. 4 pp.9–10 revision block, Verified-Visual); 01_Sheet_Index_rev2.md "
                "item 12; 00_Document_Register_rev3.md \"Per-sheet revision blocks\"",
        "confidence": "Verified-Visual",
        "status": "Open — Setup; check Add. 4 pp.4–8 on Carl's OK, then correct 01 item 12 and the 00 line",
        "anchors": [(ISSUES_LOG, "## 2026-09-30 — Add. 4 S-sheet reissues carry a revision entry; 01 item 12 "
                                 "says they don't — Open"),
                    (ISSUES_LOG, "revision 3, \"Blower Building\", TH, 2/8/23"),
                    (MERGE_LOG, "the S2.3 and S4.1 reissues show revision 3"),
                    (KNOWN_MD, "| §1 #3 | Add. 4 reissue revision entries (index vs source) |")],
        "claims": ["MRG:51", "PB:119", "ISS:Add. 4 S-sheet reissues carry a revision entry; 01 item 12 says "
                                       "they don't"],
    },
    {
        "key": "CUR:earthwork",
        "title": "Earthwork has no Ledger row: C0.2 states cut 3382 CY and fill 1598 CY; the MTO carries them "
                 "with no Ledger ID (Bid Item 1, Inferred). Two new rows proposed in New_Row_Candidates.csv.",
        "type": "gap",
        "ledger": {},
        "sheets": ["C0.2"],
        "specs": [],
        "cite": "reconciliation/Summary.md, Starter_MTO.csv (C0.2 earthwork totals, \"new row needed\") and "
                "New_Row_Candidates.csv; C0.2 reads are OCR and Bluebeam (Inferred)",
        "confidence": "Inferred",
        "status": "Open — owner approval; two new Ledger rows proposed",
        "anchors": [(SUMMARY_MD, "The C0.2 earthwork totals (cut 3382 CY, fill 1598 CY)"),
                    (ISSUES_LOG, "**Earthwork.**")],
        "claims": [],
    },
    {
        "key": "CUR:panels",
        "title": "Panel schedules MDP, LP1 and LP2 (E6.2) and LP1 (E2.2) are embedded images; the text layer "
                 "holds only their titles, so their contents can be confirmed only by eye.",
        "type": "check",
        "ledger": {"L-0240": "MDP", "L-0264": "LP-1", "L-0298": "LP2"},
        "sheets": ["E2.2", "E6.2"],
        "specs": [],
        "cite": "reconciliation/Summary.md, Needs_Check.csv and Division 26 review items (panel schedule "
                "titles located in the native text layer, image above: yes); Needs_Check.csv crop boxes",
        "confidence": "Verified",
        "status": "Open — person check",
        "anchors": [(SUMMARY_MD, "L-0240 MDP, L-0264 LP-1 and L-0298 LP2: panel schedule boxes on E6.2 (and "
                                 "E2.2 for LP1) are in Needs_Check.csv."),
                    (SUMMARY_MD, "The E6.2 and E2.2 panel schedules are embedded images"),
                    (ISSUES_LOG, "**Panel schedules.**")],
        "claims": [],
    },
]

# Part B items folded into another item (same issue). Type-6 Exception rows fold into the Part B item with the
# same lane and issue ID by rule (below); these are the extra ones.
PB_FOLD = {48: "CUR:bid18", 49: "EXC:257", 119: "CUR:s-sheets"}

# Merge Issues Log (Issues_Log.csv) rows. Every row is included, folded or excluded; the run stops if a new row
# appears that this table does not name. include: (type, status); fold: target keys; exclude: reason.
MERGE_INCLUDE = {
    5: ("duplicate", "Open — Owner; approve printed tags (Hot Box part: see the Hot Box item)"),
    9: ("gap", "Open — Owner"),
    18: ("check", "Open — Owner"),
    20: ("RFI", "Open — Engineer (RFI)"),
    21: ("conflict", "Open — Owner"),
    23: ("gap", "Open — Engineer"),
    34: ("conflict", "Open — Owner/Engineer"),
    56: ("gap", "Open — person check; native C0.3 now in library"),
    57: ("gap", "Open — Engineer; C1.1 and C1.2 now in library"),
    58: ("check", "Open — field check (pothole)"),
}
MERGE_FOLD = {
    3: ["EXC:3"], 4: ["EXC:15"], 22: ["MRG:57"] + [f"EXC:{n}" for n in range(132, 142)],
    24: ["CUR:bid18", "EXC:256", "EXC:257", "EXC:258", "EXC:259"], 39: ["PB:45"], 49: ["PB:64"],
    51: ["CUR:s-sheets"], 52: ["PB:137"], 55: ["CUR:fence"],
}
MERGE_ROLLUP = {82, 83, 84, 85, 86}   # "Decisions" roll-ups: each Part B row names its Issues Log number
MERGE_EXCLUDE_REASON = {
    8: "closed: the 10 sheets are now in the library (ISSUES_LOG.md \"Six sheets exist only in the Bluebeam "
       "OCR copies\" — Closed)",
    60: "input method (S sheets have no text layer); method theme T02 in Project_Known_Issues.md Part A",
    62: "umbrella entry; its document items are Part B rows",
    77: "duplicate spec text; the items are record-only (Project_Known_Issues.md Part C)",
}

# ISSUES_LOG.md open entries by title. Anything open and not named here is listed in the summary for review.
ISS_INCLUDE = {
    "Ledger Drawing Sheets: 80 rows cite no sheet number (78 PROPOSED, 2 printed)": ("gap", "Open — Merge"),
}
ISS_FOLD = {
    "Add. 4 S-sheet reissues carry a revision entry; 01 item 12 says they don't": ["CUR:s-sheets"],
    "Prompt 9 test-bed findings for the Merge Issues Log": ["CUR:gen-rfi", "CUR:fence", "CUR:hotbox",
                                                            "CUR:earthwork", "CUR:panels"],
    "Project_Ledger.csv repeats two Tags": ["EXC:3", "EXC:13"],
}
ISS_EXCLUDE = {
    "Two sessions ran the same reorg step": "workflow",
    "Native library files don't match Library_Fingerprint.csv (expected)": "library fingerprints",
    "Index and library notes call the 9 no-text-layer sheets \"image-only\"": "index wording",
    "Twelve Project Ledger rows are tagged stronger than their Bid Item fact": "Ledger tag level, not a "
                                                                                "document item",
    "Ledger Wiki Note \"CQA Plan\" has no Project Wiki note": "Wiki link",
    "Prompt 3 as written doesn't match the repo after the reorg": "prompt",
    "Read Method for the 10 native-only sheets is provisional": "index read method",
    "Ledger Tag uniqueness (checks.py, ledger_to_graph.py) conflicts with decision A": "tools and schema",
    "Ledger Tag uniqueness: graph part corrected after PR #9": "tools and schema",
}


class TieOutError(Exception):
    pass


# ---------------------------------------------------------------- text helpers

def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def trunc(s, n):
    s = norm(s)
    if len(s) <= n:
        return s
    cut = s[:n - 1]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut.rstrip(" ,;:—-") + "…"


def first_sentence(s, lo=40, hi=TITLE_MAX):
    """The text up to the first sentence end between lo and hi characters, else a word-boundary cut."""
    s = norm(s)
    for m in re.finditer(r"([.?])\s+(?=[A-Z\"'(])", s):
        end = m.start() + 1
        if end > hi:
            break
        word = re.findall(r"[\w.]+$", s[:m.start()])
        if end >= lo and not (word and word[0].rstrip(".") in ABBREV):
            return s[:end]
    return trunc(s, hi)


def sheets_in(text):
    return {"".join((m.group(1), m.group(2), ".", m.group(3), m.group(4))) for m in SHEET_RE.finditer(text)}


def specs_in(text):
    """Section numbers in CSI form; the division must be 00-49."""
    return {" ".join(m.groups()) for m in SPEC_RE.finditer(text) if int(m.group(1)) <= 49}


def sheet_key(s):
    m = SHEET_RE.fullmatch(s)
    return (m.group(1), int(m.group(2)), int(m.group(3)), m.group(4))


def weakest_tag(text, default=DEFAULT_TAG):
    """Weakest evidence tag stated inside brackets or parentheses; the default when none is stated."""
    found = [w for g in BRACKET_RE.findall(text) for w in TAG_WORD_RE.findall(g)]
    return min(found, key=TAG_ORDER.get) if found else default


def weaker(a, b):
    return a if TAG_ORDER[a] <= TAG_ORDER[b] else b


def id_key(lid):
    return int(lid.split("-")[1])


def md_rows(text, header_start):
    """Data rows of the first Markdown table after the line that starts with header_start."""
    lines = text.split("\n")
    i = next(n for n, line in enumerate(lines) if line.startswith(header_start))
    rows, seen_table = [], False
    for line in lines[i + 1:]:
        if line.startswith("|"):
            seen_table = True
            if re.fullmatch(r"\|[-| :]+\|", line.strip()):
                continue
            cells = [c.strip().replace("\\|", "|") for c in line.strip().strip("|").split(" | ")]
            if cells[0] not in ("#", "Theme", "Lane"):
                rows.append(cells)
        elif seen_table:
            break
    return rows


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(REPO).as_posix()


# ---------------------------------------------------------------- item model

class Item:
    def __init__(self, key, title, typ, ledger, sheets, specs, cite, confidence, status, text=""):
        self.key = key
        self.title = norm(title)
        self.type = typ
        self.ledger = set(ledger)
        self.sheets = set(sheets) | sheets_in(text)
        self.specs = set(specs) | specs_in(text)
        self.cite = [norm(cite)]
        self.confidence = confidence
        self.status = status
        self.fixed_confidence = False

    def absorb(self, cite, ledger=(), text="", confidence=None):
        if cite:
            self.cite.append("also " + norm(cite))
        self.ledger |= set(ledger)
        if not self.fixed_confidence:   # a named item keeps the sheets and sections it states
            self.sheets |= sheets_in(text)
            self.specs |= specs_in(text)
        if confidence and not self.fixed_confidence:
            self.confidence = confidence if self.confidence is None else weaker(self.confidence, confidence)

    def row(self, item_id):
        return [item_id, self.title, self.type, "; ".join(sorted(self.ledger, key=id_key)),
                "; ".join(sorted(self.sheets, key=sheet_key)), "; ".join(sorted(self.specs)),
                " | ".join(self.cite), self.confidence, self.status]


# ---------------------------------------------------------------- loaders

def load_ledger(checks):
    rows = list(csv.DictReader(io.StringIO(LEDGER.read_text(encoding="utf-8"), newline="")))
    id_map = list(csv.DictReader(io.StringIO(ID_MAP.read_text(encoding="utf-8"), newline="")))
    ok = len(rows) == len(id_map) and all(
        m["Ledger Row"] == str(i + 2) and m["Tag"] == r["Tag"] for i, (m, r) in enumerate(zip(id_map, rows)))
    checks.append(("Ledger_ID_Map rows = Project Ledger rows, same order and Tags", ok,
                   f"{len(id_map)} IDs, {len(rows)} Ledger records"))
    if not ok:
        raise TieOutError("Ledger_ID_Map.csv does not match Project_Ledger.csv row for row")
    by_row = {int(m["Ledger Row"]): m["Ledger ID"] for m in id_map}
    tags = {m["Ledger ID"]: m["Tag"] for m in id_map}
    exc_to_ids = defaultdict(set)
    issue_to_ids = defaultdict(set)
    for i, r in enumerate(rows):
        lid = by_row[i + 2]
        for m in MERGE_PTR_RE.finditer(r["Notes"]):
            for n in EXC_REF_RE.findall(m.group(1)):
                exc_to_ids[int(n)].add(lid)
        text = r["Notes"].split("[Merge]")[0] + " " + r["Source Citation"]
        lane = r["Lane"]
        if lane == "Civil & Site":
            keys = [f"CS-{n}" for n in re.findall(r"\bCS-(\d+)\b", text)]
        elif lane == "Process & Mechanical":
            keys = [n for g in re.findall(r"\bIssues? ((?:\d+(?:, | and |/))*\d+)(?![.\d])", text)
                    for n in re.findall(r"\d+", g)]
        elif lane == "Structural & Building":
            keys = [f"§1 #{n}" for n in re.findall(r"Issues, Conflicts #(\d+)", text)]
            keys += [f"§2 #{n}" for n in re.findall(r"(?:Issues, Missing(?: information)?|Missing information)"
                                                    r" #(\d+)", text)]
        elif lane == "Contract & General":
            keys = re.findall(r"\bIssues? (\d+\.\d+)\b", text)
        else:
            keys = [f"#{n}" for n in re.findall(r"\bIssues? #(\d+)\b", text)]
        for k in keys:
            issue_to_ids[(lane, k)].add(lid)
    bid18 = {by_row[i + 2] for i, r in enumerate(rows) if re.search(r"\b18\b[^;]*Unresolved", r["Bid Item"])}
    no_sheet = {by_row[i + 2] for i, r in enumerate(rows) if not SHEET_RE.search(r["Drawing Sheets"])}
    return tags, exc_to_ids, issue_to_ids, bid18, no_sheet


def load_exceptions(checks):
    text = EXC_MD.read_text(encoding="utf-8")
    rows = []
    for line in text.split("\n"):
        if re.match(r"^\| \d+ \| ", line):
            cells = [c.strip().replace("\\|", "|") for c in line.strip().strip("|").split(" | ")]
            if len(cells) != 7:
                raise TieOutError(f"Exception_Report.md row has {len(cells)} cells: {line[:80]}")
            rows.append(cells)
    head = text.split("## Merge rules")[0]
    stated = {name: int(n) for name, n in re.findall(r"^\| (.+?) \| (\d+) \|$", head, re.M)}
    total = int(re.search(r"\| \*\*Total\*\* \| \*\*(\d+)\*\* \|", head).group(1))
    counted = Counter(r[1] for r in rows)
    ok = (all(counted.get(name, 0) == stated.get(name) for name in EXC_TYPES) and len(rows) == total
          and [int(r[0]) for r in rows] == list(range(1, total + 1)))
    checks.append(("Exception Report rows by type = its Summary table", ok,
                   f"{len(rows)} rows; " + ", ".join(f"type {EXC_TYPES[k]} {counted.get(k, 0)}" for k in EXC_TYPES)))
    if not ok:
        raise TieOutError("Exception_Report.md rows do not match its Summary counts")
    return rows


def load_known(checks):
    text = KNOWN_MD.read_text(encoding="utf-8")
    part_b = md_rows(text, "## Part B")
    part_c = md_rows(text, "## Part C")
    stated_b = int(re.search(r"\*\*Part B — open document decisions:\*\* (\d+) items", text).group(1))
    stated_c = int(re.search(r"\*\*Part C — settled or record-only:\*\* (\d+) items", text).group(1))
    ok = len(part_b) == stated_b and all(len(r) == 10 for r in part_b) and len(part_c) == stated_c
    checks.append(("Project_Known_Issues Part B and Part C rows = stated counts", ok,
                   f"Part B {len(part_b)} of {stated_b}; Part C {len(part_c)} of {stated_c}"))
    if not ok:
        raise TieOutError("Project_Known_Issues.md Part B or Part C does not match its stated count")
    return part_b, part_c


def lane_key(lane, raw):
    return (lane, re.sub(r"^Issues? ", "", raw.strip()))


def load_issues_log():
    """Latest entry per title: (title, status, body, date)."""
    text = ISSUES_LOG.read_text(encoding="utf-8")
    latest = {}
    for block in re.split(r"\n(?=## )", text):
        head = block.split("\n", 1)[0]
        if not head.startswith("## "):
            continue
        parts = head[3:].split(" — ")
        if len(parts) < 3:
            continue
        title, status = " — ".join(parts[1:-1]), parts[-1].strip()
        latest[title] = (status, block, parts[0])
    return latest


# ---------------------------------------------------------------- builders

def status_who(text):
    eng = re.search(r"\b(Engineer|engineer|system integrator)\b", text)
    own = re.search(r"\bOwner\b|\bowner\b", text)
    if eng and own:
        return "Owner/Engineer"
    if eng:
        return "Engineer"
    if own:
        return "Owner"
    if "Merge" in text or re.search(r"\blane\b", text) or any(x in text for x in LANES):
        return "Merge"
    if "Setup" in text:
        return "Setup"
    return ""


def exc_item(r, exc_to_ids):
    num, typ_name, item, a, b, governs, _ = r
    n = int(num)
    t = EXC_TYPES[typ_name]
    text = " ".join((item, a, b, governs))
    if t == 1:
        typ = "conflict" if item.startswith("Combined row") else "duplicate"
        status = ("Open — Owner/Engineer" if typ == "conflict" else "Open — Merge")
    elif t == 2:
        typ, status = "duplicate", "Open — Merge"
    elif t == 3:
        typ, status = "gap", "Open — Merge"
    elif t == 4:
        typ, status = "gap", "Open — Owner; confirm no scope row is needed"
    elif t == 6:
        needed = item.split("Needed:", 1)[1] if "Needed:" in item else ""
        if governs.startswith("Owner:"):
            typ, status = "check", "Open — Merge; confirm the owning lane carries the scope"
        elif governs.startswith(("Add. 4", "Drawing vs spec")):
            typ, status = "conflict", "Open — Merge; carry the governing document named"
        elif re.search(r"\bRFI\b|\bEngineer\b", needed):
            typ, status = "RFI", "Open — Engineer (RFI)"
        else:
            typ = "conflict"
            status = "Open — " + (status_who(needed) or "Merge")
    else:   # 7
        typ = "conflict"
        status = "Open — " + (status_who(governs) or "Owner")
    title = first_sentence(item)
    if t == 2:
        title = "Same item on more than one row (not combined): " + title
    elif t == 6:
        title = "Cross-lane: " + title
    cite = (f"Exception_Report.md #{n} ({typ_name}): A: {trunc(a, CITE_PART_MAX)}; B: {trunc(b, CITE_PART_MAX)}"
            + (f"; Which governs: {trunc(governs, CITE_PART_MAX)}" if governs and governs != "—" else ""))
    return Item(f"EXC:{n}", title, typ, exc_to_ids.get(n, ()), (), (), cite, weakest_tag(text), status, text)


def pb_item(r, issue_to_ids):
    num, lane, iid, issue, typ_name, priority, resolver, status, exc_refs, log_refs = r
    if "RFI" in resolver or "bidder question" in resolver:
        typ = "RFI"
    elif typ_name.startswith(("Conflict", "Cross-lane conflict", "Bid item flag")):
        typ = "conflict"
    else:
        typ = "gap"
    who = "Engineer (RFI)" if typ == "RFI" else status_who(resolver)
    qual = {"Working answer — confirm": "working answer to confirm", "Open (partly closed)": "partly closed",
            "Design note": "design note", "Inferred": "Inferred answer to confirm"}.get(status, "")
    st = "Open — " + (who or "resolver not stated") + (f"; {qual}" if qual else "")
    cite = (f"Project_Known_Issues.md Part B #{num} ({lane} {iid}; {typ_name}"
            + (f", priority {priority}" if priority else "") + f"; resolver: {resolver or 'not stated'}"
            + f"; status: {status})"
            + (f"; related Exception Report {exc_refs}" if exc_refs and exc_refs != "—" else "")
            + f"; Issues_Log.csv {log_refs}")
    ids = issue_to_ids.get(lane_key(lane, iid), ())
    # Part B states no evidence tags; confidence comes from folded rows, else the default (set in build)
    return Item(f"PB:{num}", f"{lane} {iid}: {issue}", typ, ids, (), (), cite, None, st, issue)


def proposal_items(proposals, tags, claimed):
    groups = defaultdict(list)
    for p in proposals:
        if f"P:{p['Proposal No.']}" in claimed:
            continue
        cat = p["Category"]
        key = (p["Ledger ID"], cat) if cat != "owner's Division 26 review" else (p["Ledger ID"], cat, p["Field"])
        groups[key].append(p)
    items = []
    for key in sorted(groups, key=lambda k: (id_key(k[0]), k[1:])):
        ps = groups[key]
        lid, cat = key[0], key[1]
        tag = tags[lid]
        nums = ", ".join(p["Proposal No."] for p in ps)
        ev_sheets = [s for p in ps for s in re.split(r";\s*", p["Evidence Sheet"]) if SHEET_RE.fullmatch(s)]
        shown = ", ".join(sorted(set(ev_sheets), key=sheet_key))
        verified = [p for p in ps if p["Confidence"] == "Verified"]
        if cat == "cited, not found":
            variants = sorted({v for p in ps for v in re.findall(r'variant form was read on this sheet: "+([^"]+)"+',
                                                                   p["Reason"])})
            title = (f"{tag} ({lid}): tag not read on cited sheet(s) {shown}; confirm each cite (a detail, "
                     f"schedule or note may show the item untagged)"
                     + (f"; variant printed form read: {', '.join(variants)}" if variants else ""))
            conf, status = DEFAULT_TAG, "Open — person check"
        elif cat == "found, not cited":
            vs = sorted({p["Evidence Sheet"] for p in verified}, key=sheet_key)
            title = (f"{tag} ({lid}): tag read on {shown}, which the Ledger does not cite; add to Drawing "
                     f"Sheets if confirmed" + (f" (native text layer: {', '.join(vs)})" if vs else ""))
            conf = "Verified" if len(verified) == len(ps) else DEFAULT_TAG
            status = ("Open — owner approval" if len(verified) == len(ps) else
                      "Open — person check" + (f"; {len(verified)} Verified sheet add(s) await owner approval"
                                               if verified else ""))
        elif cat == "PROPOSED row, printed tag found":
            title = (f"{tag} ({lid}): the row's designation matches printed text read on {shown}; check the "
                     f"page image and whether the text is the item's tag")
            conf, status = DEFAULT_TAG, "Open — person check"
        else:   # owner's Division 26 review
            p = ps[0]
            field = "tag level" if p["Field"].startswith("Verified/") else p["Field"]
            title = (f"{tag} ({lid}): {field} {p['Current Value']} → {p['Proposed Value']} on the native text "
                     f"layer ({shown}); approve, noting the row's Notes still hold Inferred facts")
            conf, status = "Verified" if verified else DEFAULT_TAG, "Open — owner approval"
        evid = "; ".join(f"{p['Proposal No.']} {p['Evidence Sheet']} (set p.{p['Evidence Set Page']}, "
                         f"{p['Evidence Method']})" for p in ps)
        cite = f"reconciliation/Ledger_Update_Proposal.csv {nums} ({cat}): {evid}"
        item = Item(f"PG:{lid}:{'/'.join(key[1:])}", title, "check", [lid], ev_sheets, (), cite, conf, status)
        item.proposals = [p["Proposal No."] for p in ps]
        items.append(item)
    return items


# ---------------------------------------------------------------- main build

def build():
    checks = []
    texts = {p: p.read_text(encoding="utf-8") for p in INPUTS}
    tags, exc_to_ids, issue_to_ids, bid18, no_sheet = load_ledger(checks)
    exc_rows = load_exceptions(checks)
    part_b, part_c = load_known(checks)
    merge_rows = list(csv.DictReader(io.StringIO(texts[MERGE_LOG], newline="")))
    proposals = list(csv.DictReader(io.StringIO(texts[PROPOSALS], newline="")))
    iss = load_issues_log()

    # Curated anchors
    missing = [(rel(p), s) for c in CURATED for p, s in c["anchors"] if s not in texts[p]]
    checks.append(("Every curated item's source lines are present", not missing,
                   f"{sum(len(c['anchors']) for c in CURATED)} anchors in {len(CURATED)} items"
                   + (f"; missing: {missing}" if missing else "")))
    if missing:
        raise TieOutError(f"curated anchors missing: {missing}")
    ok = len(bid18) == 23 and "L-0239" in bid18
    checks.append(("Bid Item 18 Ledger rows = 23 (Exception Report #255)", ok, f"{len(bid18)} rows"))
    ok2 = len(no_sheet) == 80
    checks.append(("Ledger rows citing no sheet number = 80 (ISSUES_LOG.md entry)", ok2, f"{len(no_sheet)} rows"))
    if not (ok and ok2):
        raise TieOutError("Bid Item 18 or no-sheet row count differs from its source")
    s_title = "Add. 4 S-sheet reissues carry a revision entry; 01 item 12 says they don't"
    if iss.get(s_title, ("",))[0] != "Open":
        raise TieOutError(f"ISSUES_LOG.md entry is no longer Open: {s_title}")

    items = []
    claimed = set()
    for c in CURATED:
        if c["ledger"] == "bid18":
            ledger = bid18
        else:
            bad = {k: v for k, v in c["ledger"].items() if tags.get(k) != v}
            if bad:
                raise TieOutError(f"{c['key']}: Ledger ID Tags differ from Ledger_ID_Map.csv: {bad}")
            ledger = c["ledger"]
        it = Item(c["key"], c["title"], c["type"], ledger, c["sheets"], c["specs"], c["cite"],
                  c["confidence"], c["status"])
        it.fixed_confidence = True
        it.proposals = [x[2:] for x in c["claims"] if x.startswith("P:")]
        items.append(it)
        claimed |= set(c["claims"])

    items += proposal_items(proposals, tags, claimed)

    # Exception Report: types 1-7 are items unless claimed, folded into a Part B item, or settled (Part C)
    pb_keys = {lane_key(r[1], r[2]): int(r[0]) for r in part_b}
    pc_keys = {lane_key(r[0], r[1]) for r in part_c if r[1] != "—"}
    exc_fold, exc_settled, exc_type8 = {}, [], 0
    for r in exc_rows:
        n, t = int(r[0]), EXC_TYPES[r[1]]
        if t == 8:
            exc_type8 += 1
            continue
        if f"EXC:{n}" in claimed:
            continue
        m = LANE_ISSUE_RE.match(r[2]) if t == 6 else None
        k = lane_key(m.group(1), m.group(2)) if m else None
        if k in pc_keys:
            exc_settled.append(n)
        elif k in pb_keys:
            exc_fold[n] = f"PB:{pb_keys[k]}"
        else:
            items.append(exc_item(r, exc_to_ids))

    for r in part_b:
        if int(r[0]) in PB_FOLD:
            continue
        items.append(pb_item(r, issue_to_ids))

    by_merge = {int(r["#"]): r for r in merge_rows}
    unnamed = [n for n, r in by_merge.items()
               if r["Status"].startswith("Open") and n not in MERGE_INCLUDE and n not in MERGE_FOLD
               and n not in MERGE_ROLLUP and n not in MERGE_EXCLUDE_REASON
               and r["Area"] in ("Content", "Resplit pass", "Drawing controls", "Documents", "Inputs")]
    checks.append(("Every open Merge Issues Log row about content is named here", not unnamed,
                   f"{len(by_merge)} rows" + (f"; not named: {unnamed}" if unnamed else "")))
    if unnamed:
        raise TieOutError(f"Issues_Log.csv rows not classified: {unnamed}")
    for n in sorted(MERGE_INCLUDE):
        r = by_merge[n]
        typ, status = MERGE_INCLUDE[n]
        text = " ".join((r["Issue"], r["Impact"], r["Next step / owner"], r["Reference"]))
        ids = {lid for x in re.findall(r"Exception Report #([\d, #]+)", r["Reference"])
               for e in EXC_REF_RE.findall("#" + x) for lid in exc_to_ids.get(int(e), ())}
        cite = (f"Issues_Log.csv #{n} ({r['Area']}; {r['Status']}): {trunc(r['Next step / owner'], CITE_PART_MAX)}; "
                f"reference: {r['Reference']}")
        items.append(Item(f"MRG:{n}", first_sentence(r["Issue"]), typ, ids, (), (), cite, weakest_tag(text),
                          status, text))

    iss_open = {t: v for t, v in iss.items() if v[0] == "Open"}
    for title in sorted(ISS_INCLUDE):
        if title not in iss_open:
            raise TieOutError(f"ISSUES_LOG.md entry not open: {title}")
        typ, status = ISS_INCLUDE[title]
        status_, block, date = iss_open[title]
        ledger = no_sheet if title.startswith("Ledger Drawing Sheets") else set()
        cite = f"ISSUES_LOG.md {date} \"{title}\" (Open)"
        items.append(Item(f"ISS:{title}", title, typ, ledger, (), (), cite, weakest_tag(block), status))

    # Folds
    index = {it.key: it for it in items}

    def resolve(key):
        while key.startswith("PB:") and int(key[3:]) in PB_FOLD:
            key = PB_FOLD[int(key[3:])]
        return key

    exc_by_num = {int(r[0]): r for r in exc_rows}
    for n, target in sorted(exc_fold.items()):
        r = exc_by_num[n]
        text = " ".join(r[2:6])
        index[resolve(target)].absorb(f"Exception_Report.md #{n} (same lane issue)", exc_to_ids.get(n, ()),
                                      text, weakest_tag(text))
    for r in part_b:
        n = int(r[0])
        if n in PB_FOLD:
            index[resolve(f"PB:{n}")].absorb(f"Project_Known_Issues.md Part B #{n} ({r[1]} {r[2]}: {r[3]})",
                                             issue_to_ids.get(lane_key(r[1], r[2]), ()), r[3])
    for n in (255, 16, 17):
        r = exc_by_num[n]
        index["CUR:bid18" if n == 255 else "CUR:hotbox"].absorb(None, exc_to_ids.get(n, ()))   # cited already
    for n, targets in sorted(MERGE_FOLD.items()):
        for t in targets:
            index[resolve(t)].absorb(f"Issues_Log.csv #{n} ({trunc(by_merge[n]['Issue'], 120)})")
    for title, targets in sorted(ISS_FOLD.items()):
        if title not in iss_open:
            raise TieOutError(f"ISSUES_LOG.md entry not open: {title}")
        for t in targets:
            index[t].absorb(f"ISSUES_LOG.md {iss_open[title][2]} \"{title}\" (Open)")

    for it in items:
        if it.confidence is None:
            it.confidence = DEFAULT_TAG

    # Tie-outs on the result
    covered = [p for it in items for p in getattr(it, "proposals", [])]
    ok = sorted(covered) == sorted(p["Proposal No."] for p in proposals)
    checks.append(("Every Ledger_Update_Proposal row is in exactly one item", ok,
                   f"{len(proposals)} proposals, {len(covered)} placed"))
    placed_exc = {int(it.key[4:]) for it in items if it.key.startswith("EXC:")}
    exc_claimed = {int(x[4:]) for c in CURATED for x in c["claims"] if x.startswith("EXC:")}
    accounted = placed_exc | exc_claimed | set(exc_fold) | set(exc_settled)
    non8 = {int(r[0]) for r in exc_rows if EXC_TYPES[r[1]] != 8}
    ok_e = accounted == non8 and not (placed_exc & set(exc_fold))
    checks.append(("Exception rows of types 1–7 = items + folded + settled", ok_e,
                   f"{len(non8)} rows: {len(placed_exc)} items, {len(exc_claimed)} in curated items, "
                   f"{len(exc_fold)} folded into Part B items, {len(exc_settled)} settled (Part C); "
                   f"type 8 left out: {exc_type8}"))
    all_ids = set(tags)
    bad = [it.key for it in items if not it.title or it.type not in TYPES or it.confidence not in TAG_ORDER
           or not it.status.startswith("Open") or not it.cite[0] or not it.ledger <= all_ids]
    checks.append(("Every item has a title, type, Ledger IDs from the map, citation, confidence and Open status",
                   not bad, f"{len(items)} items" + (f"; bad: {bad[:5]}" if bad else "")))
    if not (ok and ok_e) or bad:
        raise TieOutError("result tie-out failed: " + "; ".join(c[0] for c in checks if not c[1]))

    stats = {
        "exc_type8": exc_type8, "exc_fold": exc_fold, "exc_settled": exc_settled,
        "merge": by_merge, "iss_open": iss_open, "part_b": len(part_b), "proposals": len(proposals),
        "exc_rows": len(exc_rows),
    }
    return items, checks, stats


def write_csv(items):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLUMNS)
    for i, it in enumerate(items, 1):
        w.writerow(it.row(f"OI-{i:04d}"))
    return buf.getvalue()


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows]
    return "\n".join(out)


def write_summary(items, checks, stats):
    ids = {it.key: f"OI-{i:04d}" for i, it in enumerate(items, 1)}
    src_name = {"CUR": "Named by the owner (reconciliation and logs)", "PG": "Ledger_Update_Proposal.csv",
                "EXC": "Exception_Report.md", "PB": "Project_Known_Issues.md Part B",
                "MRG": "Issues_Log.csv (Merge)", "ISS": "ISSUES_LOG.md"}
    by_type = Counter(it.type for it in items)
    by_src = defaultdict(Counter)
    for it in items:
        by_src[it.key.split(":")[0]][it.type] += 1
    by_conf = Counter(it.confidence for it in items)
    by_status = Counter(it.status.split(";")[0] for it in items)

    L = ["# Open items: summary", "",
         "Generated by `testbeds/eastsound/tools/build_open_items.py`. One row per open item in `Open_Items.csv`. "
         "Nothing here changes the Ledger, the Exception Report or a log; this list only gathers what is open. "
         "Confidence tags follow AGENTS.md and describe the evidence that the item exists, not its answer.", "",
         "Rebuild from the repo root (stdlib only): `python testbeds/eastsound/tools/build_open_items.py`. The "
         "list reflects the inputs at the SHA-256 values at the end; rebuild after any of them changes.", "",
         "## Counts by type", "",
         table(["Type", "Items"], [[t, by_type.get(t, 0)] for t in TYPES] + [["**all**", f"**{len(items)}**"]]),
         "", "## Counts by source and type", "",
         table(["Source"] + list(TYPES) + ["all"],
               [[src_name[s]] + [by_src[s].get(t, 0) for t in TYPES] + [sum(by_src[s].values())]
                for s in ("CUR", "PG", "EXC", "PB", "MRG", "ISS")]),
         "", "## Counts by confidence and by who acts next", "",
         table(["Confidence", "Items"], [[k, by_conf[k]] for k in sorted(by_conf, key=TAG_ORDER.get)]), "",
         table(["Status", "Items"], sorted(([k, v] for k, v in by_status.items()), key=lambda x: (-x[1], x[0]))),
         "", "## Owner-named items and Prompt 9 findings", ""]
    named = [("Generator RFI (125 kW drawings vs 150 kW, 26 32 13 ¶2.03 C.1)", "CUR:gen-rfi"),
             ("Bid Item 18 (base form Train 3 vs Add. 4 temporary generator)", "CUR:bid18"),
             ("Chain link fence (L-0018, L-0088, C2.1 keyed notes 6 and 8)", "CUR:fence"),
             ("C2.3 storm drain lengths (SD-2, SD-3)", "CUR:sd23"),
             ("Hot Box duplicates (L-0057/58 vs L-0337/38)", "CUR:hotbox"),
             ("Add. 4 revision 3 on S2.3 and S4.1", "CUR:s-sheets"),
             ("Earthwork has no Ledger row (Prompt 9 finding)", "CUR:earthwork"),
             ("Panel schedules are images (Prompt 9 finding)", "CUR:panels")]
    by_key = {it.key: it for it in items}
    L.append(table(["Item", "ID", "Type", "Confidence", "Status"],
                   [[n, ids[k], by_key[k].type, by_key[k].confidence, by_key[k].status] for n, k in named]))
    L += ["", "## Rules", "",
          "- **Types.** RFI: the source routes the item to the Engineer (\"RFI\", \"bidder question\"). conflict: "
          "two documents, sheets or rows disagree. gap: something is missing (a row, a spec section, a sheet, "
          "an input). duplicate: one item on two or more Ledger rows, or one tag or name on two items. check: a "
          "person confirms a read, a cite or a lane hand-off.",
          "- **Confidence.** The weakest tag the source states in brackets or parentheses for the item (Verified, "
          "Verified-Visual, Inferred, Unresolved). No tag stated means Inferred: the item was compiled by Merge "
          "or a lane and not re-read here. The owner-named items carry the tag of their own evidence.",
          "- **Status.** \"Open — <who acts next>\" (Engineer, Owner, Owner/Engineer, Merge, Setup, person check, "
          "owner approval), then any qualifier from the source.",
          "- **Ledger IDs** come from `derived/reconciliation/Ledger_ID_Map.csv`: through the \"[Merge] "
          "Exceptions: #n\" pointers in the Project Ledger's Notes, the lane issue IDs the Notes cite, or the "
          "proposal rows. Blank means the source ties the item to no Ledger row.",
          "- **Sheets and Spec Sections** are the sheet numbers and section numbers written in the item's source "
          "text. They are what the source cites, including sheets or sections the documents don't contain "
          "(C8.1, M4.1, 46 12 13).",
          "- **Ledger_Update_Proposal.csv:** one item per Ledger ID and category; each owner's Division 26 review "
          "field is its own item. Proposals that belong to a named item stay with it.",
          "- **Exception Report:** types 1–7 are items. A cross-lane row (type 6) with the same lane and issue ID "
          "as a Part B row is folded into it; one that matches a settled Part C row is left out. Type 8 "
          "(PROPOSED tag approvals) is tag housekeeping and is left out.",
          "- **Folded** rows add their citation, Ledger IDs, sheets and sections to the item they repeat.", "",
          "## Left out or folded", ""]
    merge = stats["merge"]
    rows = [["Exception_Report.md type 8, PROPOSED tag awaiting approval", stats["exc_type8"],
             "tag housekeeping; stays in the Exception Report for owner approval"],
            ["Exception_Report.md cross-lane rows folded into Part B items", len(stats["exc_fold"]),
             "#" + ", #".join(str(n) for n in sorted(stats["exc_fold"]))],
            ["Exception_Report.md cross-lane rows settled in Part C", len(stats["exc_settled"]),
             "#" + ", #".join(str(n) for n in sorted(stats["exc_settled"]))]]
    for n in sorted(merge):
        r = merge[n]
        if n in MERGE_INCLUDE:
            continue
        if n in MERGE_FOLD:
            why = "folded into " + ", ".join(sorted({ids[_resolve(t)] for t in MERGE_FOLD[n]}))
        elif n in MERGE_ROLLUP:
            why = "roll-up; each Part B row names this entry"
        elif n in MERGE_EXCLUDE_REASON:
            why = MERGE_EXCLUDE_REASON[n]
        elif not r["Status"].startswith("Open"):
            why = f"not open ({r['Status']})"
        else:
            why = f"method, schema or workflow ({r['Area']}), not a drawing or spec item"
        rows.append([f"Issues_Log.csv #{n}: {trunc(r['Issue'], 90)}", 1, why])
    for title in sorted(stats["iss_open"]):
        if title in ISS_INCLUDE:
            continue
        if title in ISS_FOLD:
            why = "folded into " + ", ".join(ids[t] for t in ISS_FOLD[title])
        elif title in ISS_EXCLUDE:
            why = f"repo housekeeping ({ISS_EXCLUDE[title]})"
        else:
            why = "not classified; review"
        rows.append([f"ISSUES_LOG.md (Open): {title}", 1, why])
    L.append(table(["Source rows", "Count", "Why"], rows))
    L += ["", "Project_Known_Issues.md Part A (method themes), Part C (settled) and Part D (carries with no "
          "conflict) are not open document items and are left out.", "",
          "## Tie-outs", "", table(["Check", "Result", "Detail"],
                                   [[c, "pass" if ok else "FAIL", d] for c, ok, d in checks]),
          "", "## Inputs (SHA-256)", "",
          table(["File", "SHA-256"], [[rel(p), sha256(p)] for p in INPUTS]), ""]
    return "\n".join(L)


def _resolve(key):
    while key.startswith("PB:") and int(key[3:]) in PB_FOLD:
        key = PB_FOLD[int(key[3:])]
    return key


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT, help="output folder (default: derived/issues/)")
    args = ap.parse_args(argv)
    try:
        items, checks, stats = build()
    except TieOutError as e:
        print(f"STOP, nothing written: {e}", file=sys.stderr)
        return 1
    csv_text = write_csv(items)
    md_text = write_summary(items, checks, stats)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, text in (("Open_Items.csv", csv_text), ("Open_Items_Summary.md", md_text)):
        with open(args.out / name, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    by_type = Counter(it.type for it in items)
    print(f"{len(items)} open items: " + ", ".join(f"{t} {by_type.get(t, 0)}" for t in TYPES))
    print(f"tie-outs: {sum(1 for c in checks if c[1])} of {len(checks)} pass; written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
