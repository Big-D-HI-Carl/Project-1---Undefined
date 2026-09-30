#!/usr/bin/env python3
"""Parse the Project Wiki into a note table and a link table (derived/wiki).

Inputs (read-only):
  testbeds/eastsound/project/01_Project_Wiki/Project_Wiki.md        202 notes, level-3 headings, five lane formats
  testbeds/eastsound/derived/reconciliation/Ledger_ID_Map.csv       Ledger ID for each Ledger tag
  testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv   "Wiki Note(s)", used only to pick between
                                                                    Ledger rows that share a printed tag

Outputs (testbeds/eastsound/derived/wiki/ unless --out is given):
  Wiki_Notes.csv    one row per note
  Wiki_Links.csv    one row per note, target type, target and source
  Parse_Report.md   counts, tie-outs, rules, and every note, line or item that did not parse

No library files are read and no LLM calls are made. Rows are sorted, files are UTF-8 without a BOM with LF
line endings, and there are no timestamps, so two runs on the same inputs give identical bytes. Parse gaps are
listed in Parse_Report.md, not fatal. The run stops, writing nothing, only if an input is missing.

Run from anywhere (standard library only):
  python testbeds/eastsound/tools/parse_wiki.py [--out <folder>]
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
WIKI = TB / "project" / "01_Project_Wiki" / "Project_Wiki.md"
ID_MAP = TB / "derived" / "reconciliation" / "Ledger_ID_Map.csv"
LEDGER = TB / "project" / "02_Project_Ledger" / "Project_Ledger.csv"
OUT_DEFAULT = TB / "derived" / "wiki"

LANES = ("Civil & Site", "Process & Mechanical", "Electrical & Controls", "Structural & Building",
         "Contract & General")
FIELDS = ("Document ID", "Type", "Discipline", "Revision/Date", "Summary", "Tags", "Related documents")
SUMMARY_CHARS = 600
TYPES = ("equipment tag", "sheet", "spec section", "addendum item", "note")
SOURCES = ("tag line", "related documents", "body text")
CONF_RANK = {"Verified": 0, "Verified-Visual": 1, "Inferred": 2, "Unresolved": 3}

NOTES_HEADER = ["Note ID", "Title", "Lane", "Type", "Discipline", "Revision/Date",
                "Summary (first 600 characters)", "Where It Lives", "Heading Line"]
LINKS_HEADER = ["Note ID", "Target Type", "Target", "Source", "Confidence", "Ledger ID", "Target In Wiki",
                "Written As", "Basis", "Wiki Line"]

# ---------------------------------------------------------------- reference patterns
SHEET = r"[GCSAEM]\d{1,2}\.\d{1,2}A?"
B_BEFORE = r"(?<![A-Za-z0-9._/-])"          # "/" is allowed before a sheet (detail 5/C7.2), handled below
B_AFTER = r"(?![A-Za-z0-9]|\.\d)"
SHEET_RANGE_RE = re.compile(r"(?<![A-Za-z0-9.])(" + SHEET + r")\s*(?:–|—| to | through )\s*([GCSAEM]?)(\d{1,2}\.\d{1,2}A?)"
                            + B_AFTER)
SHEET_SERIES_RE = re.compile(r"(?<![A-Za-z0-9.])([GCSAEM]\d{1,2})\.x\b")
SHEET_RE = re.compile(r"(?<![A-Za-z0-9.])(" + SHEET + r")" + B_AFTER)
SPEC_RE = re.compile(r"(?<![\d.,])(\d{2} \d{2} \d{2})(?![\d])")
OLD_SPEC_RE = re.compile(r"(?<![\d.,])(\d{5})(?![\d])")    # pre-2004 five-digit numbers, spec parts only
NUM = r"\d+(?!\s\d{2}\s\d{2})"                 # a page number that is not the start of a spec number
PAGES = r"pp?\.\s*" + NUM + r"(?:\s*[–-]\s*" + NUM + r")?(?:\s*(?:,|and)\s*" + NUM + r"(?:\s*[–-]\s*" + NUM + r")?)*"
ADD_RE = re.compile(r"(?<![A-Za-z])(?:Add\.|Addendum)\s*(?:No\.\s*|#\s*)?(\d+)(?![\d.])"
                    r"(?:\s*\([A-Z][a-z]{2}[a-z.]*\s+\d{1,2},\s*\d{4}\))?"
                    r"(?P<pages>,?\s*" + PAGES + r")?"
                    r"(?P<clar>,?\s*Clarifications?\s*\d+(?:\s*(?:[–-]|,|and)\s*\d+)*)?")
ORPHAN_PAGES_RE = re.compile(r"(?<![A-Za-z_\d])" + PAGES)
NOTE_RES = (
    (re.compile(r"(?:Add\.\s*4\s+)?\b[Gg]enerator [Ee]xhibit\b"), "Add. 4 Generator Exhibit"),
    (re.compile(r"\b(?:CQA|QA) [Pp]lan\b"), "QA plan"),
    (re.compile(r"\bAppendix\s+([A-I])\b"), None),
    (re.compile(r"\bAppendices\s+([A-I](?:\s*(?:,|and)\s*[A-I]\b)*)"), None),
)
EMPTY_RE = re.compile(r"^(?:—|–|-|none\b|n/a\b|not stated\b|not numbered\b)", re.I)
NONE_NUMBERED_RE = re.compile(r"\b(?:none|not) (?:numbered|printed)\b", re.I)

# unparsed-item categories (checked in order)
ISSUE_RE = re.compile(r"\b(?:Issues?|Open checks?|Exceptions?)\b")
INDEX_RE = re.compile(r"\.md\b|\b0[0-4](?:_|\s+(?:item|items|Bid|Equipment|register|conflict|Other|row|Lane|\(|rev)"
                      r"|\s*\()|\b0[0-4]\s*$|^\s*0[0-4]\b")
EXTERNAL_RE = re.compile(r"WSDOT|Standard (?:Plans|Specifications)|\bWAC\b|\bRCW\b|NFPA|\bIBC\b|Ecology", re.I)


def fail(msg):
    print("STOP: " + msg, file=sys.stderr)
    sys.exit(1)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.resolve().relative_to(REPO).as_posix()


def conf_of(text):
    """The weakest tag word written in a piece of a tag line or Related documents line."""
    if re.search(r"\bUnresolved\b", text):
        return "Unresolved"
    if re.search(r"\bInferred\b", text):
        return "Inferred"
    return "Verified"


def weakest(*confs):
    return max(confs, key=lambda c: CONF_RANK[c])


def split_top(text, sep_re):
    """Split at sep_re matches that sit outside () and []. Returns (offset, piece) pairs."""
    out, depth, start, i = [], 0, 0, 0
    while i < len(text):
        ch = text[i]
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        elif depth == 0:
            m = sep_re.match(text, i)
            if m and m.end() > i:
                out.append((start, text[start:i]))
                i = start = m.end()
                continue
        i += 1
    out.append((start, text[start:]))
    return [(o, p) for o, p in out if p.strip()]


# A comma followed by a bare number, "#n", an appendix letter or "Clarification" continues a list
# ("Hot Box #1, #2", "Pipe IDs 8, 11, 13", "Appendices B, C", "Add. 4 p.1, Clarification 5").
ITEM_SEP = re.compile(r";\s*|,\s+(?![A-I](?:[,;)\s]|$)|#\d|\d+\b(?!\s\d{2}\s\d{2})|Clarifications?\b)")
SEGMENT_SEP = re.compile(r";\s*|\.\s+(?=[A-Z\"])")
PART_SEP_DOT = re.compile(r"\s+·\s+")
PART_SEP_CIVIL = re.compile(r";\s*(?=(?:Equipment|Spec sections|Spec|Sheets|Addenda)\s*:)")
PART_LABEL_RE = re.compile(r"^\s*(Equipment|Structures|Items|Scope|Spec sections|Spec(?: \([^)]*\))?|Sheets|Addenda)"
                           r"\s*(?::|—)\s*")
PART_CLASS = {"Equipment": "equipment", "Structures": "equipment", "Items": "equipment", "Scope": "equipment",
              "Sheets": "sheets", "Addenda": "addenda"}
SUBLABEL_RE = re.compile(r"^([A-Z][A-Za-z ]{1,25}):\s+")


# ---------------------------------------------------------------- inputs
def read_wiki():
    raw = WIKI.read_bytes().decode("utf-8")
    return raw.split("\n")


def parse_index(lines):
    """The Index table: unit, title, type, lane, index position, in Wiki order."""
    rows, inside = [], False
    for ln in lines:
        if ln.startswith("## "):
            inside = ln.strip() == "## Index"
            continue
        if inside and ln.startswith("| ") and not ln.startswith("| # ") and not ln.startswith("|---"):
            cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
            if len(cells) == 6 and cells[0].isdigit():
                rows.append(dict(zip(("No", "Unit", "Title", "Type", "Lane", "Position"), cells)))
    return rows


def read_ledger():
    id_rows = list(csv.DictReader(io.StringIO(ID_MAP.read_bytes().decode("utf-8"))))
    led_rows = list(csv.DictReader(io.StringIO(LEDGER.read_bytes().decode("utf-8"))))
    aligned = len(id_rows) == len(led_rows) and all(a["Tag"] == b["Tag"] for a, b in zip(id_rows, led_rows))
    cites = {}
    for a, b in zip(id_rows, led_rows):
        cites[a["Ledger ID"]] = {v.strip() for v in b.get("Wiki Note(s)", "").split(";") if v.strip()}
    return id_rows, cites, aligned


# ---------------------------------------------------------------- note blocks and the five lane formats
def note_blocks(lines):
    blocks, section, cur = [], "", None
    for no, ln in enumerate(lines, 1):
        if ln.startswith("## "):
            section, cur = ln[3:].strip(), None
            continue
        if ln.startswith("### ") and section not in ("Index",) and not section.startswith("Lane conventions"):
            head = ln[4:].strip()
            nid, _, title = head.partition(" — ")
            cur = {"id": nid.strip(), "title": title.strip(), "line": no, "section": section, "body": []}
            blocks.append(cur)
            continue
        if cur is not None and ln.strip():
            cur["body"].append((no, ln))
    return blocks


MERGE_RE = re.compile(r"^> Merge: lane — (.+?) · Issue references → (.+?) · index — (.+)$")
WHERE_RE = re.compile(r"^(Location|Where it lives|Lives in):\s*(.*)$")


def parse_civil(body):
    for no, ln in body:
        if not ln.startswith("|") and ln.count(" | ") == 6:
            vals = ln.split(" | ")
            return {f: (v.strip(), no) for f, v in zip(FIELDS, vals)}
    return None


def parse_pm(body):
    out = {}
    for no, ln in body:
        if ln.startswith("Document ID: "):
            for piece in re.split(r" \| (?=(?:Type|Discipline|Revision/Date): )", ln):
                k, _, v = piece.partition(": ")
                out[k.strip()] = (v.strip(), no)
        for k in ("Summary", "Tags", "Related documents"):
            if ln.startswith(k + ": "):
                out[k] = (ln[len(k) + 2:].strip(), no)
    return out if all(f in out for f in FIELDS) else None


def parse_ec(body):
    for i, (no, ln) in enumerate(body):
        if ln.startswith("| Document ID | Type |") and i + 2 < len(body) and body[i + 1][1].startswith("|---"):
            rno, row = body[i + 2]
            cells = [c.strip() for c in row.strip().strip("|").split(" | ")]
            if len(cells) == 7:
                return {f: (v, rno) for f, v in zip(FIELDS, cells)}
    return None


def parse_sb(body):
    out = {}
    for no, ln in body:
        m = re.match(r"^- \*\*([^*]+?):\*\*\s*(.*)$", ln)
        if m and m.group(1) in FIELDS:
            out[m.group(1)] = (m.group(2).strip(), no)
    return out if all(f in out for f in FIELDS) else None


def parse_cg(body):
    out = {}
    for no, ln in body:
        m = re.match(r"^\| ([A-Za-z/ ]+?) \| (.*) \|$", ln)
        if m and m.group(1) in FIELDS:
            out[m.group(1)] = (m.group(2).strip(), no)
    return out if all(f in out for f in FIELDS) else None


FORMATS = (("pipe line", parse_civil), ("labeled lines", parse_pm), ("seven-column table", parse_ec),
           ("bold bullets", parse_sb), ("field-value table", parse_cg))


def parse_note(block):
    note = dict(block)
    note["lane"] = note["merge_lane"] = ""
    note["where"], note["where_line"], note["format"], note["fields"] = "", 0, "", {}
    body = block["body"]
    if body:
        m = MERGE_RE.match(body[0][1])
        if m:
            note["merge_lane"] = m.group(1)
            note["lane"] = re.sub(r"\s*\(resplit pass\)$", "", m.group(1))
    for name, fn in FORMATS:
        got = fn(body)
        if got:
            note["format"], note["fields"] = name, got
            break
    for no, ln in body:
        m = WHERE_RE.match(ln)
        if m:
            note["where"], note["where_line"] = m.group(2).strip(), no
    return note


# ---------------------------------------------------------------- Ledger tag matching
class Ledger:
    def __init__(self, id_rows, cites):
        self.cites = cites
        self.forms = defaultdict(list)      # printed form -> [(Ledger ID, qualifier, Ledger tag)]
        self.no_e = {}                      # "SES" -> "SES (E)" where no new item carries the tag
        self.variant = {}                   # hyphen variant -> printed form
        self.proposed = defaultdict(list)   # normalised PROPOSED designation -> [Ledger ID]
        for r in id_rows:
            tag, lid = r["Tag"], r["Ledger ID"]
            if tag.startswith("PROPOSED-"):
                self.proposed[norm_name(tag[len("PROPOSED-"):])].append(lid)
                continue
            for alt in tag.split(" | "):
                alt = alt.strip()
                m = re.match(r"^(.*?)\s*[\(\[]([^)\]]+)[\)\]]$", alt)
                if m and m.group(2) != "E":
                    self.forms[m.group(1)].append((lid, m.group(2), tag))
                else:
                    self.forms[alt].append((lid, "", tag))
        for f in list(self.forms):
            if f.endswith(" (E)") and f[:-4] not in self.forms:
                self.forms[f[:-4]] = list(self.forms[f])
                self.no_e[f[:-4]] = f
        for f in list(self.forms):
            m = re.fullmatch(r"([A-Z]+)(-?)(\d+)", f)
            if m:
                v = m.group(1) + ("" if m.group(2) else "-") + m.group(3)
                if v not in self.forms:
                    self.variant[v] = f
        dash = sorted((f for f in self.forms if "–" in f), key=lambda s: (-len(s), s))
        plain = sorted((f for f in list(self.forms) + list(self.variant) if "–" not in f), key=lambda s: (-len(s), s))
        self.dash_re = self._alt(dash)
        self.plain_re = self._alt(plain)

    @staticmethod
    def _alt(forms):
        if not forms:
            return re.compile(r"(?!x)x")
        return re.compile(r"(?<![A-Za-z0-9#.-])(" + "|".join(re.escape(f) for f in forms) + r")" + B_AFTER)

    LIST_RE = re.compile(r"(?<![A-Za-z0-9#-])(?P<pre>[A-Z][A-Za-z]*(?: [A-Z][A-Za-z]*)*?)(?P<kind> IDs?| #)\s?"
                         r"(?P<nums>\d+(?:\s*(?:–|,|and|&|through)\s*#?\d+)+)" + B_AFTER)
    RANGE_RE = re.compile(r"(?<![A-Za-z0-9#-])(?P<pre>[A-Z][A-Z0-9]*?(?:-| #| )?)?(?P<a>\d+)(?P<sa>[A-Z]?)"
                          r"\s*(?:–| to | through )\s*(?P<pre2>[A-Z][A-Z0-9]*?(?:-| #| )?|#)?(?P<b>\d+)(?P<sb>[A-Z]?)"
                          + B_AFTER)

    def _range_members(self, m):
        pre, pre2 = m.group("pre") or "", m.group("pre2") or ""
        if pre2 and pre2 not in (pre, "#") and not pre.endswith(pre2):
            return []
        a, b, sa, sb = int(m.group("a")), int(m.group("b")), m.group("sa"), m.group("sb")
        if sa and sb and a == b and sa < sb:
            members = [f"{pre}{a}{chr(c)}" for c in range(ord(sa), ord(sb) + 1)]
        elif not sa and not sb and a < b <= a + 30:
            members = [f"{pre}{n}" for n in range(a, b + 1)]
        else:
            return []
        return members if all(x in self.forms for x in members) else []

    def _list_members(self, m):
        pre, kind = m.group("pre"), m.group("kind")
        nums = []
        for part in re.split(r"\s*(?:,|and|&)\s*", m.group("nums")):
            r = re.match(r"#?(\d+)(?:\s*(?:–|through)\s*#?(\d+))?$", part.strip())
            if not r:
                return []
            a = int(r.group(1))
            b = int(r.group(2)) if r.group(2) else a
            if b < a or b > a + 60:
                return []
            nums.extend(range(a, b + 1))
        members = [f"{pre} ID {n}" if "ID" in kind else f"{pre} #{n}" for n in nums]
        return members if all(x in self.forms for x in members) else []

    def find(self, text, variants=True):
        """Printed Ledger tags in text: [(start, end, written, form, basis)]. Ranges and lists come out as members.
        A hyphen variant (LP1 for LP-1) is skipped when a number follows it, as in "SD1 0.51g"."""
        hits, masked = [], list(text)

        def mask(s, e):
            for k in range(s, e):
                masked[k] = " "

        for m in self.dash_re.finditer(text):
            hits.append((m.start(), m.end(), m.group(1), m.group(1), ""))
            mask(m.start(), m.end())
        t = "".join(masked)
        for m in self.LIST_RE.finditer(t):
            members = self._list_members(m)
            if members:
                for x in members:
                    hits.append((m.start(), m.end(), m.group(0), x, f"expanded from list '{m.group(0)}'"))
                mask(m.start(), m.end())
        t = "".join(masked)
        for m in self.RANGE_RE.finditer(t):
            members = self._range_members(m)
            if members:
                for x in members:
                    hits.append((m.start(), m.end(), m.group(0), x, f"expanded from range '{m.group(0)}'"))
                mask(m.start(), m.end())
        t = "".join(masked)
        for m in self.plain_re.finditer(t):
            w = m.group(1)
            if w in self.variant:
                if not variants or re.match(r"\s*\d", t[m.end():]):
                    continue
                hits.append((m.start(), m.end(), w, self.variant[w], f"variant form of Ledger tag '{self.variant[w]}'"))
            else:
                hits.append((m.start(), m.end(), w, w, ""))
        return sorted(hits, key=lambda h: (h[0], h[3]))

    def resolve(self, form, note_id, context):
        """Ledger ID(s) for a printed form, and the basis. context = the item, segment or sentence, plus the
        note title. A form that exists only with a qualifier ("F1 (Influent Pump Station)") resolves only when
        the Ledger row names this note in Wiki Note(s) or the qualifier appears in the context."""
        cands = self.forms[form]
        ids = [c[0] for c in cands]
        qualified = all(c[1] for c in cands)
        cited = [c for c in cands if note_id in self.cites.get(c[0], set())]
        pool = cited or cands
        if len(pool) > 1 or (qualified and not cited):
            local = [c for c in pool if c[1] and c[1].lower() in context.lower()]
            if local:
                pool = local
            elif qualified and not cited:
                tags = ", ".join(sorted(c[2] for c in cands))
                return "", f"not resolved: Ledger tag(s) {tags}; no row names this note and no qualifier in the text"
        pick = sorted(c[0] for c in pool)
        if len(pick) == 1:
            if len(ids) > 1:
                how = "picked by the Ledger row's Wiki Note(s)" if cited and len(cited) == 1 else "picked by its qualifier in the text"
                return pick[0], f"Ledger tag shared by {len(ids)} rows; {how}"
            cites = "cites" if cited else "does not cite"
            how = f"Ledger tag '{self.no_e[form]}' written without (E)" if form in self.no_e else "Ledger tag"
            return pick[0], f"{how}; the Ledger row {cites} this note"
        return "; ".join(pick), f"Ledger tag ambiguous: {len(pick)} rows fit"


def norm_name(s):
    s = s.lower().replace("-", " ")
    s = re.sub(r"^(?:existing|new|proposed)\s+", "", s)
    return re.sub(r"\s+", " ", s).strip(" .")


# ---------------------------------------------------------------- reference extraction
class Refs:
    def __init__(self, sheet_order, wiki_ids):
        self.sheet_order = sheet_order
        self.sheet_pos = {s: i for i, s in enumerate(sheet_order)}
        self.wiki_ids = wiki_ids

    def extract(self, text, last_add=None, orphan_pages=False, old_spec=False):
        """Sheet, spec, addendum and note references in text.
        Returns (refs, masked_text, last_add); refs = [(type, target, written, basis, offset)]."""
        refs, masked = [], list(text)

        def take(m, s=None, e=None):
            s = m.start() if s is None else s
            e = m.end() if e is None else e
            for k in range(s, e):
                masked[k] = " "

        def cur():
            return "".join(masked)

        for rx, fixed in NOTE_RES:
            for m in rx.finditer(cur()):
                targets = [fixed] if fixed else [f"Appendix {x}" for x in re.findall(r"[A-I]\b", m.group(1))]
                for target in targets:
                    refs.append(("note", target, text[m.start():m.end()], "", m.start()))
                take(m)
        for m in ADD_RE.finditer(cur()):
            n = m.group(1)
            last_add = n
            written = text[m.start():m.end()].strip(" ,")
            for t in add_targets(n, m.group("pages"), m.group("clar")):
                refs.append(("addendum item", t, written, "", m.start()))
            take(m)
        if orphan_pages and last_add:
            for m in ORPHAN_PAGES_RE.finditer(cur()):
                written = text[m.start():m.end()]
                for t in add_targets(last_add, m.group(0), None):
                    refs.append(("addendum item", t, written, f"page with no addendum number; read as Add. {last_add}"
                                 " from the same Addenda list", m.start()))
                take(m)
        for m in SHEET_RANGE_RE.finditer(cur()):
            a = m.group(1)
            b = (m.group(2) or a[0]) + m.group(3)
            written = text[m.start():m.end()]
            if a in self.sheet_pos and b in self.sheet_pos and self.sheet_pos[a] < self.sheet_pos[b] \
                    and a[0] == b[0]:
                for s in self.sheet_order[self.sheet_pos[a]:self.sheet_pos[b] + 1]:
                    refs.append(("sheet", s, written, f"expanded from range '{written}' in Wiki index order", m.start()))
            else:
                for s in (a, b):
                    refs.append(("sheet", s, written, f"range '{written}' not expanded: endpoints not in the Wiki index",
                                 m.start()))
            take(m)
        for m in SHEET_SERIES_RE.finditer(cur()):
            pre = m.group(1) + "."
            written = text[m.start():m.end()]
            members = [s for s in self.sheet_order if s.startswith(pre)]
            for s in members:
                refs.append(("sheet", s, written, f"series '{written}' expanded from the Wiki index", m.start()))
            if not members:
                refs.append(("sheet", written, written, "series with no sheets in the Wiki index", m.start()))
            take(m)
        for m in SHEET_RE.finditer(cur()):
            refs.append(("sheet", m.group(1), m.group(1), "", m.start()))
            take(m)
        for m in SPEC_RE.finditer(cur()):
            refs.append(("spec section", m.group(1), m.group(1), "", m.start()))
            take(m)
        if old_spec:
            for m in OLD_SPEC_RE.finditer(cur()):
                refs.append(("spec section", m.group(1), m.group(1), "five-digit section number as written", m.start()))
                take(m)
        return refs, cur(), last_add


def add_targets(n, pages, clar):
    base = f"Add. {n}"
    pg = []
    if pages:
        body = re.sub(r"^,?\s*pp?\.\s*", "", pages.strip())
        for part in re.split(r"\s*(?:,|and)\s*", body):
            m = re.match(r"(\d+)(?:\s*[–-]\s*(\d+))?$", part.strip())
            if m:
                a = int(m.group(1))
                b = int(m.group(2)) if m.group(2) else a
                pg.extend(range(a, b + 1) if b >= a and b - a <= 40 else [a])
    cl = []
    if clar:
        body = re.sub(r"^,?\s*Clarifications?\s*", "", clar.strip())
        for part in re.split(r"\s*(?:,|and)\s*", body):
            m = re.match(r"(\d+)(?:\s*[–-]\s*(\d+))?$", part.strip())
            if m:
                a = int(m.group(1))
                b = int(m.group(2)) if m.group(2) else a
                cl.extend(range(a, b + 1) if b >= a else [a])
    if not pg and not cl:
        return [base]
    out = [f"{base} p.{p}" for p in pg[:-1]] if cl else [f"{base} p.{p}" for p in pg]
    if cl:
        head = f"{base} p.{pg[-1]}" if pg else base
        out += [f"{head} Clarification {c}" for c in cl]
    return out


def classify_unparsed(text):
    if ISSUE_RE.search(text):
        return "Issue or Exceptions reference (not a link type)"
    if INDEX_RE.search(text):
        return "index file reference (not a link type)"
    if EXTERNAL_RE.search(text):
        return "external reference (not a link type)"
    return "no target found"


# ---------------------------------------------------------------- link building
class Builder:
    def __init__(self, ledger, refs, wiki_ids):
        self.ledger, self.refs, self.wiki_ids = ledger, refs, wiki_ids
        self.links = {}          # key -> row dict
        self.unparsed = []       # (note id, line, source, category, text)
        self.empty = Counter()   # (source) -> count of explicit none markers
        self.self_refs = 0

    def add(self, note, ttype, target, source, conf, written, basis, line, offset, ledger_id=""):
        if ttype in ("sheet", "spec section", "note") and target == note["id"]:
            self.self_refs += 1
            return
        in_wiki = ""
        if ttype in ("sheet", "spec section", "note"):
            in_wiki = "Y" if target in self.wiki_ids else "N"
        key = (note["id"], ttype, target, source)
        row = {"Note ID": note["id"], "Target Type": ttype, "Target": target, "Source": source, "Confidence": conf,
               "Ledger ID": ledger_id, "Target In Wiki": in_wiki, "Written As": written.strip(), "Basis": basis,
               "Wiki Line": line, "_order": (note["line"], SOURCES.index(source), line, offset)}
        old = self.links.get(key)
        if old is None or CONF_RANK[conf] < CONF_RANK[old["Confidence"]]:
            self.links[key] = row

    def add_refs(self, note, refs, source, conf, line, extra_basis=""):
        for ttype, target, written, basis, off in refs:
            b = "; ".join(x for x in (extra_basis, basis) if x)
            c = weakest(conf, "Inferred") if basis.startswith("series") else conf
            self.add(note, ttype, target, source, c, written, b, line, off)

    def equipment_hits(self, note, text, source, conf, line, base_off, context, extra_basis=""):
        found = False
        for s, e, written, form, basis in self.ledger.find(text):
            lid, lbasis = self.ledger.resolve(form, note["id"], context)
            b = "; ".join(x for x in (extra_basis, basis, lbasis) if x)
            target = form if basis.startswith("expanded") else written
            self.add(note, "equipment tag", target, source, conf, text if source == "tag line" else written, b, line,
                     base_off + s, lid)
            found = True
        return found

    # tag line ---------------------------------------------------------------
    def tag_line(self, note):
        val, line = note["fields"]["Tags"]
        if note["format"] == "seven-column table":
            parts = [(0, val)]
        elif note["format"] == "pipe line":
            parts = split_top(val, PART_SEP_CIVIL)
        else:
            parts = split_top(val, PART_SEP_DOT)
        last_add = None
        for poff, part in parts:
            m = PART_LABEL_RE.match(part)
            if m:
                label = m.group(1)
                pclass = "spec" if label.startswith("Spec") else PART_CLASS[label]
                body, boff = part[m.end():], poff + m.end()
                part_conf = conf_of(label)
                labeled = True
            else:
                label, pclass, body, boff, part_conf, labeled = "", "equipment", part, poff, "Verified", False
            items = split_top(body, ITEM_SEP)
            for ioff, item in items:
                self.tag_item(note, item.strip(), pclass, labeled, part_conf, line, boff + ioff, last_add)
                if pclass == "addenda":
                    for mm in ADD_RE.finditer(item):
                        last_add = mm.group(1)

    def tag_item(self, note, item, pclass, labeled, part_conf, line, off, last_add):
        item = item.rstrip(".").strip()
        if not item:
            return
        is_empty = bool(EMPTY_RE.match(item)) or bool(NONE_NUMBERED_RE.search(item))
        conf = weakest(part_conf, conf_of(item))
        extra = ""
        if is_empty:
            conf, extra = weakest(conf, "Inferred"), "tag part reads 'none …'; the reference sits inside that note"
        refs, _, _ = self.refs.extract(item, last_add, orphan_pages=(pclass == "addenda"),
                                       old_spec=(pclass == "spec"))
        self.add_refs(note, refs, "tag line", conf, line, extra)
        if pclass == "equipment" and not is_empty and (labeled or not refs):
            target = SUBLABEL_RE.sub("", item).strip()
            if not self.equipment_hits(note, target, "tag line", conf, line, off, target + " " + note["title"]):
                lids = self.ledger.proposed.get(norm_name(target), [])
                if lids:
                    basis = "PROPOSED Ledger tag, same name" if len(lids) == 1 else \
                        f"PROPOSED Ledger tag, same name, ambiguous: {len(lids)} rows"
                    self.add(note, "equipment tag", target, "tag line", conf, item, basis, line, off,
                             "; ".join(sorted(lids)))
                else:
                    self.add(note, "equipment tag", target, "tag line", conf, item, "no Ledger tag in the item", line,
                             off)
            return
        if refs:
            return
        if is_empty:
            self.empty["tag line"] += 1
            return
        if pclass == "equipment":        # unlabeled part: an item with refs is refs only; handled above
            return
        self.unparsed.append((note["id"], line, f"tag line ({pclass})", classify_unparsed(item), item))

    # Related documents -------------------------------------------------------
    def related(self, note):
        val, line = note["fields"]["Related documents"]
        for off, seg in split_top(val, SEGMENT_SEP):
            seg = seg.strip().rstrip(".")
            if not seg:
                continue
            refs, masked, _ = self.refs.extract(seg)
            tagged = self.equipment_hits(note, masked, "related documents", conf_of(seg), line, off,
                                         seg + " " + note["title"])
            if refs:
                self.add_refs(note, refs, "related documents", conf_of(seg), line)
            if refs or tagged:
                continue
            if EMPTY_RE.match(seg):
                self.empty["related documents"] += 1
                continue
            self.unparsed.append((note["id"], line, "related documents", classify_unparsed(seg), seg))

    # body text ---------------------------------------------------------------
    def body(self, note):
        for fld in ("Revision/Date", "Summary"):
            val, line = note["fields"][fld]
            refs, _, _ = self.refs.extract(val)
            self.add_refs(note, refs, "body text", "Inferred", line, f"mention in {fld}")
            for s, e, written, form, basis in self.ledger.find(val):
                sent = sentence_at(val, s) + " " + note["title"]
                lid, lbasis = self.ledger.resolve(form, note["id"], sent)
                b = "; ".join(x for x in (f"mention in {fld}", basis, lbasis) if x)
                target = form if basis.startswith("expanded") else written
                self.add(note, "equipment tag", target, "body text", "Inferred", written, b, line, s, lid)


def natkey(s):
    return [(0, int(x), "") if x.isdigit() else (1, 0, x) for x in re.split(r"(\d+)", s)]


def sentence_at(text, pos):
    starts = [m.end() for m in re.finditer(r"[.;]\s+", text[:pos])]
    s = starts[-1] if starts else 0
    m = re.search(r"[.;]\s+", text[pos:])
    e = pos + m.start() if m else len(text)
    return text[s:e]


# ---------------------------------------------------------------- output
def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def md_cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def build():
    for p in (WIKI, ID_MAP, LEDGER):
        if not p.is_file():
            fail(f"input missing: {rel(p)}")
    lines = read_wiki()
    index = parse_index(lines)
    id_rows, cites, aligned = read_ledger()
    blocks = note_blocks(lines)
    notes = [parse_note(b) for b in blocks]
    wiki_ids = {n["id"] for n in notes}
    sheet_order = [r["Unit"] for r in index if r["Type"] == "Drawing sheet"]
    ledger = Ledger(id_rows, cites)
    refs = Refs(sheet_order, wiki_ids)
    b = Builder(ledger, refs, wiki_ids)

    note_fail = []
    for n in notes:
        if not n["lane"]:
            note_fail.append((n["id"], n["line"], "no Merge lane line under the heading"))
        if not n["fields"]:
            note_fail.append((n["id"], n["line"], "no lane format matched; fields left blank"))
            continue
        if not n["where"]:
            note_fail.append((n["id"], n["line"], "no Location / Where it lives / Lives in line"))
        for f in FIELDS:
            if not n["fields"][f][0]:
                note_fail.append((n["id"], n["fields"][f][1], f"empty field: {f}"))
        b.tag_line(n)
        b.related(n)
        b.body(n)

    # Wiki_Notes.csv
    note_rows = []
    for n in notes:
        f = n["fields"]
        g = lambda k: f[k][0] if f else ""
        note_rows.append([n["id"], n["title"], n["lane"], g("Type"), g("Discipline"), g("Revision/Date"),
                          g("Summary")[:SUMMARY_CHARS], n["where"], n["line"]])

    # Wiki_Links.csv
    type_rank = {t: i for i, t in enumerate(TYPES)}
    links = sorted(b.links.values(), key=lambda r: (r["_order"], type_rank[r["Target Type"]], natkey(r["Target"])))
    link_rows = [[r[h] for h in LINKS_HEADER] for r in links]

    report = make_report(lines, index, notes, note_fail, links, b, ledger, aligned, id_rows)
    return {"Wiki_Notes.csv": csv_text(NOTES_HEADER, note_rows),
            "Wiki_Links.csv": csv_text(LINKS_HEADER, link_rows),
            "Parse_Report.md": report}


def make_report(lines, index, notes, note_fail, links, b, ledger, aligned, id_rows):
    out = []
    w = out.append
    lane_idx = Counter(r["Lane"] for r in index)
    lane_notes = Counter(n["lane"] for n in notes)
    lane_fmt = defaultdict(Counter)
    for n in notes:
        lane_fmt[n["lane"]][n["format"] or "(none)"] += 1
    resplit = [n["id"] for n in notes if "resplit" in n["merge_lane"]]

    ties = []
    ties.append(("Note headings = Index rows", len(notes) == len(index) == 202,
                 f"{len(notes)} headings, {len(index)} Index rows, 202 expected"))
    same_order = [n["id"] for n in notes] == [r["Unit"] for r in index]
    ties.append(("Note IDs in Index order", same_order, "heading ID = Index Unit, row by row"))
    lane_ok = all(lane_notes[k] == lane_idx[k] for k in LANES) and set(lane_notes) <= set(LANES)
    ties.append(("Notes per lane = Index lane counts", lane_ok,
                 ", ".join(f"{k} {lane_notes[k]}/{lane_idx[k]}" for k in LANES)))
    lane_match = all(n["lane"] == r["Lane"] for n, r in zip(notes, index))
    ties.append(("Merge-line lane = Index lane, note by note", lane_match, "202 compared" if lane_match else "mismatch"))
    full = sum(1 for n in notes if n["fields"] and n["where"])
    ties.append(("Notes with all 7 fields and a location line", full == len(notes), f"{full} of {len(notes)}"))
    ties.append(("Ledger_ID_Map tags = Project_Ledger tags, row by row", aligned, f"{len(id_rows)} rows"))
    trunc = sum(1 for n in notes if n["fields"] and len(n["fields"]["Summary"][0]) > SUMMARY_CHARS)

    w("# Parse report — Project Wiki notes and links")
    w("")
    w("Built by `testbeds/eastsound/tools/parse_wiki.py` from the Merge rev1 Project Wiki. Deterministic: no "
      "timestamps, sorted rows, UTF-8 without a BOM, LF line endings. Rebuild from the repo root:")
    w("")
    w("```")
    w("python testbeds/eastsound/tools/parse_wiki.py")
    w("```")
    w("")
    w("## Inputs")
    w("")
    w("| File | Lines or rows | SHA-256 |")
    w("|---|---|---|")
    w(f"| `{rel(WIKI)}` | {len(lines)} lines | `{sha256(WIKI)}` |")
    w(f"| `{rel(ID_MAP)}` | {len(id_rows)} rows | `{sha256(ID_MAP)}` |")
    w(f"| `{rel(LEDGER)}` | {len(id_rows)} rows (Wiki Note(s) only) | `{sha256(LEDGER)}` |")
    w("")
    w("## Tie-outs")
    w("")
    w("| Check | Result | Detail |")
    w("|---|---|---|")
    for name, ok, detail in ties:
        w(f"| {name} | {'pass' if ok else 'FAIL'} | {md_cell(detail)} |")
    w("")
    w("## Notes parsed per lane")
    w("")
    w("| Lane | Index count | Parsed | Format |")
    w("|---|---|---|---|")
    for k in LANES:
        fmts = ", ".join(f"{f} ({c})" for f, c in sorted(lane_fmt[k].items()))
        w(f"| {k} | {lane_idx[k]} | {lane_notes[k]} | {fmts} |")
    w(f"| **Total** | {sum(lane_idx.values())} | {len(notes)} | |")
    w("")
    w(f"- The Civil & Site count includes {len(resplit)} resplit-pass notes ({', '.join(resplit)}); their "
      "Merge line reads \"Civil & Site (resplit pass)\" and the Lane column reads \"Civil & Site\".")
    w(f"- {trunc} summaries run past {SUMMARY_CHARS} characters and are cut at {SUMMARY_CHARS} in Wiki_Notes.csv. "
      "The full text stays in the Wiki.")
    idm = [(n["id"], n["fields"]["Document ID"][0]) for n in notes if n["fields"]
           and n["fields"]["Document ID"][0] != n["id"]]
    if idm:
        w("- The Document ID field differs from the heading ID in these notes. Note ID uses the heading, which "
          "matches the Index:")
        for nid, did in idm:
            w(f"  - {nid}: Document ID reads \"{did}\"")
    w("")
    w("## Links per type")
    w("")
    by = Counter((r["Target Type"], r["Source"]) for r in links)
    w("| Target type | Tag line | Related documents | Body text | Total |")
    w("|---|---|---|---|---|")
    for t in TYPES:
        cells = [by[(t, s)] for s in SOURCES]
        w(f"| {t} | " + " | ".join(str(c) for c in cells) + f" | {sum(cells)} |")
    tot = [sum(by[(t, s)] for t in TYPES) for s in SOURCES]
    w("| **Total** | " + " | ".join(str(c) for c in tot) + f" | {sum(tot)} |")
    w("")
    bc = Counter((r["Source"], r["Confidence"]) for r in links)
    w("| Source | " + " | ".join(CONF_RANK) + " |")
    w("|---|" + "---|" * len(CONF_RANK))
    for s in SOURCES:
        w(f"| {s} | " + " | ".join(str(bc[(s, c)]) for c in CONF_RANK) + " |")
    w("")
    w(f"- {b.self_refs} references from a note to itself were dropped (mostly the body-text citation of the note's "
      "own sheet or section).")
    w("- One row per note, target type, target and source. Where the same target is written twice in one source, "
      "the row keeps the stronger tag.")
    w("")
    w("## Equipment tags and the Ledger")
    w("")
    eq = [r for r in links if r["Target Type"] == "equipment tag"]
    matched = [r for r in eq if r["Ledger ID"]]
    amb = [r for r in matched if "; " in r["Ledger ID"]]
    ids = {x for r in matched for x in r["Ledger ID"].split("; ")}
    printed_ids = {r["Ledger ID"] for r in id_rows if not r["Tag"].startswith("PROPOSED-")}
    w(f"- Equipment tag links: {len(eq)} (tag line {sum(1 for r in eq if r['Source'] == 'tag line')}, body text "
      f"{sum(1 for r in eq if r['Source'] == 'body text')}).")
    w(f"- With a Ledger ID: {len(matched)} links, {len(ids)} distinct Ledger IDs "
      f"({len(ids & printed_ids)} of {len(printed_ids)} printed-tag rows; {len(ids - printed_ids)} PROPOSED rows).")
    nc = sum(1 for r in matched if "does not cite this note" in r["Basis"])
    w(f"- {nc} matched links point to a Ledger row whose Wiki Note(s) does not name this note. They are listed in "
      "Wiki_Links.csv (Basis column) for Merge to check; no Ledger change is made here.")
    missing = sorted(printed_ids - ids)
    tagmap = {r["Ledger ID"]: r["Tag"] for r in id_rows}
    w(f"- Printed-tag Ledger rows not found in any note: {len(missing)}.")
    if missing:
        w("  " + "; ".join(f"{i} {tagmap[i]}" for i in missing))
    unres = [r for r in eq if r["Basis"].find("not resolved:") >= 0]
    w(f"- Printed forms left without a Ledger ID because the only Ledger rows carry a qualifier that the text "
      f"does not support: {len(unres)}.")
    for r in unres:
        w(f"  - {r['Note ID']} ({r['Source']}): {r['Target']} — {r['Basis'].split('not resolved: ')[1]}")
    w(f"- Ambiguous Ledger matches (more than one row fits; all IDs listed in the cell): {len(amb)}.")
    for r in amb:
        w(f"  - {r['Note ID']} ({r['Source']}): {r['Target']} → {r['Ledger ID']}")
    w("")
    w("## Targets not in the Wiki")
    w("")
    w("Sheet, spec section and note targets with Target In Wiki = N (distinct target, link count, notes):")
    w("")
    notin = defaultdict(list)
    for r in links:
        if r["Target In Wiki"] == "N":
            notin[(r["Target Type"], r["Target"])].append(r["Note ID"])
    w("| Target type | Target | Links | Notes |")
    w("|---|---|---|---|")
    for (t, tg), ns in sorted(notin.items()):
        uniq = list(dict.fromkeys(ns))
        w(f"| {t} | {md_cell(tg)} | {len(ns)} | {md_cell(', '.join(uniq))} |")
    w("")
    w("## Notes that did not parse")
    w("")
    if note_fail:
        w("| Note | Wiki line | Problem |")
        w("|---|---|---|")
        for nid, ln, p in note_fail:
            w(f"| {md_cell(nid)} | {ln} | {md_cell(p)} |")
    else:
        w("None. All 202 notes matched their lane format and have all seven fields and a location line.")
    w("")
    w("## Lines and items that did not parse")
    w("")
    w("Pieces of a tag line or Related documents line that gave no link. Body text is prose and is not listed. "
      f"Explicit \"none\" entries are parsed, not listed: tag line {b.empty['tag line']}, Related documents "
      f"{b.empty['related documents']}.")
    w("")
    cat = Counter(u[3] for u in b.unparsed)
    w("| Category | Count |")
    w("|---|---|")
    for k, v in sorted(cat.items(), key=lambda kv: (kv[0] != "no target found", kv[0])):
        w(f"| {k} | {v} |")
    w("")
    for k in sorted(cat, key=lambda c: (c != "no target found", c)):
        w(f"### {k}")
        w("")
        w("| Note | Wiki line | Source | Text |")
        w("|---|---|---|---|")
        for nid, ln, src, c, txt in b.unparsed:
            if c == k:
                w(f"| {md_cell(nid)} | {ln} | {src} | {md_cell(txt)} |")
        w("")
    w("## Rules applied")
    w("")
    for r in RULES:
        w(f"- {r}")
    w("")
    return "\n".join(out)


RULES = (
    "Notes: every level-3 heading under the three note sections (Drawing sheets, Spec sections and appendices, "
    "Other units). Note ID and Title come from the heading, split at the first \" — \". Lane comes from the Merge "
    "line under the heading.",
    "Formats, as the lane preambles describe them: Civil & Site one pipe-separated line plus \"Location:\"; "
    "Process & Mechanical labeled lines plus \"Where it lives:\"; Electrical & Controls a seven-column table plus "
    "\"Where it lives:\"; Structural & Building bold bullets plus \"Lives in:\"; Contract & General a Field/Value "
    "table plus \"Location:\". The parser tries each format on every note and records the one that fits.",
    "Where It Lives is the text after the location label. Summary is cut at 600 characters.",
    "Tag line: split into its labeled parts (Equipment, Structures, Items or Scope; Spec; Sheets; Addenda), then "
    "into items at \";\" and \", \" outside brackets. Electrical & Controls writes one unlabeled list, so an item "
    "with a sheet, spec or addendum reference gives those links and any other item is an equipment tag. An "
    "unlabeled part in another lane is read the same way.",
    "Every item in a labeled equipment part is an equipment tag link. A sub-label such as \"Existing:\" is dropped "
    "from Target and kept in Written As.",
    "Related documents: split into pieces at \";\" and at sentence ends outside brackets. Each piece gives its "
    "sheet, spec, addendum and note references.",
    "Body text is the Revision/Date and Summary fields. Its references and printed Ledger tags are links tagged "
    "Inferred.",
    "Confidence: tag-line and Related-documents links are Verified as written, except that the weakest tag word "
    "the lane wrote on that piece governs (for example \"[by title, Inferred]\" or \"Spec (by subject, "
    "Inferred)\"), per the weakest-tag rule in AGENTS.md. A reference inside a \"none …\" entry is Inferred.",
    "Sheets: G, C, S, A and E numbers such as C1.6A, plus M (M4.1 is cited on C4.1 and is not in the set). A range such as C3.1–C3.5 is expanded in Wiki index order "
    "and keeps its source's tag. A series such as C2.x is expanded to the index sheets in that series and tagged "
    "Inferred, since the note names no members. Basis names each expansion.",
    "Spec sections: six digits in three pairs. Paragraph marks stay in Written As; Target is the section number. "
    "In a tag-line Spec part, a five-digit number written in the older format (01340, 15051) is also a spec "
    "section target; none of these is a Wiki note.",
    "Addendum items: \"Add. N\" or \"Addendum No. N\" with its pages and clarifications. One target per page "
    "(\"Add. 4 p.3\"); a clarification joins the page before it (\"Add. 4 p.1 Clarification 5\"). A bare page "
    "in an Addenda list takes the addendum number written before it in the same list.",
    "Note links: Appendix A–I, the QA plan (\"QA plan\" or \"CQA Plan\") and the Add. 4 generator exhibit. "
    "Links from a note to itself are dropped.",
    "Target In Wiki: Y when a sheet, spec section or note target is a Wiki note ID; blank for equipment and "
    "addendum items.",
    "Ledger ID: printed Ledger tags (Ledger_ID_Map.csv) are found by exact, case-sensitive text with word edges. "
    "\"A | B\" tags match either form. \"(E)\" is kept as part of the tag, except that SES (E), which has no new "
    "twin, also matches a bare \"SES\". A hyphen variant (LP1 for LP-1) matches and says so in Basis, unless a "
    "number follows it (\"SD1 0.51g\" is a seismic value, not SD-1). A range or list (SDCB #1–#10, INF1–INF3, "
    "Hot Box #1, #2, Pipe IDs 1–26) is expanded only when every member is a Ledger tag.",
    "A bracketed qualifier, such as \"(Influent Pump Station)\" on F1, is not printed on the drawings. A form that "
    "exists only with qualifiers gets a Ledger ID only when the Ledger row names this note in Wiki Note(s) or the "
    "qualifier appears in the item, sentence or note title; otherwise Ledger ID is blank and Basis says why.",
    "Where one printed form fits several Ledger rows, the rows whose Wiki Note(s) name this note are kept, then "
    "the rows whose qualifier appears in the same item, sentence or note title. If more than one row is left, all "
    "IDs go in the cell, separated by \"; \".",
    "PROPOSED Ledger tags are matched only to a whole tag-line equipment item with the same name (case, hyphens "
    "and a leading existing/new/proposed ignored). They are not searched in body text.",
    "Not link types, listed in the unparsed table by category: Issue and Exceptions references, index files "
    "(00–04), and external references (WSDOT, WAC and similar).",
)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="output folder (default: derived/wiki)")
    args = ap.parse_args()
    files = build()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (out / name).write_bytes(text.encode("utf-8"))
    print(f"wrote {len(files)} files to {out}")


if __name__ == "__main__":
    main()
