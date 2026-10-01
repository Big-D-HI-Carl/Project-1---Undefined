#!/usr/bin/env python3
"""Build a knowledge graph from a Project Ledger CSV and its derived files. No LLM calls.

Output is graphify-compatible: query it with `graphify explain` and
`graphify path --undirected` (pass --graph <out>/graphify-out/graph.json),
and render the report and viewer with `graphify cluster-only <out> --no-label`.

Every Ledger row becomes an item node keyed on its Ledger ID (the rev1 Ledger's own
Ledger ID column, checked against Ledger_ID_Map.csv; a rev0 Ledger takes the map's ID),
labeled with its Tag. Drawing Sheets, Spec Sections, Addenda and Wiki Note(s)
become links; Lane and Bid Item stay on the item node as attributes, so they
don't act as hubs. Parsing rules were approved in Prompt 3 step 2 (2026-09-30);
testbeds/eastsound/graph/README.md lists them, with the rules for the four
derived inputs:
  - Wiki_Notes.csv: note content as attributes on the note nodes;
  - Wiki_Links.csv: links from each note to items, sheets, specs, addenda, notes;
  - MTO_Lines_rev1.csv (or Starter_MTO.csv): one node per MTO line, linked to its Ledger ID(s)
    and sheet;
  - Open_Items.csv: one node per open item, linked to its Ledger IDs, sheets, specs.
A derived input that is missing or lacks a needed column is skipped, never
guessed; <out>/Build_Inputs.csv records what each build used.

Tested on graphifyy 0.9.72 / Python 3.11.

Usage: python testbeds/eastsound/tools/ledger_to_graph.py <ledger.csv> --out <folder>
       [--id-map F] [--wiki-notes F] [--wiki-links F] [--mto F] [--open-items F]
"""
import argparse
import csv
import hashlib
import io
import os
import re
import subprocess
import sys
from pathlib import Path

TAG_COL = "Verified/Verified-Visual/Inferred/Unresolved"
TAG_COL_REV1 = "Confidence"   # Ledger rev1 names the tag column Confidence
BASIS_SUFFIX = re.compile(r"^(.*?)\s*\((tag|spec|sheet)\)$")   # rev1 Wiki Note(s): "C2.2 (tag)"
LEVELS = ("Verified-Visual", "Verified", "Inferred", "Unresolved")  # longest match first
# Ledger tag level -> graphify confidence. The original level rides on every edge.
CONFIDENCE = {"Verified-Visual": "EXTRACTED", "Verified": "EXTRACTED",
              "Inferred": "INFERRED", "Unresolved": "AMBIGUOUS"}
RANK = {"Verified-Visual": 0, "Verified": 0, "Inferred": 1, "Unresolved": 2}
LEVEL_WORD = re.compile(r"\b(Verified-Visual|Verified|Inferred|Unresolved)\b")

# Values that mean "no link" (rule 2). Anything else that doesn't parse is also
# kept on the node under `unlinked`, never guessed.
NULL_VALUE = re.compile(r"^(?:[—–-]+|not stated|not shown|none\b.*)$", re.IGNORECASE)
SHEET = re.compile(r"^([A-Za-z]{1,2})\s*(\d+\.\d+)([A-Za-z]?)(?=$|[\s(])\s*(.*)$")
SPEC = re.compile(r"^(\d{2})[\s-]?(\d{2})[\s-]?(\d{2})(?=$|[\s(])\s*(.*)$")
APPENDIX = re.compile(r"^(Appendix [A-Z])\b\s*(.*)$")
ADD_NO = re.compile(r"^Add\.\s*(\d+)\b[\s,]*")
PAGE = re.compile(r"\bpp?\.\s*(\d+)(?:\s*[–-]\s*(\d+))?")
CLARIFICATION = re.compile(r"\bClarifications?\s+(\d+(?:\s*(?:,|and)\s*\d+)*)")
SPEC_PARA = re.compile(r"\b(\d{2} \d{2} \d{2}) ¶\s*(\d+(?:\.\d+)*(?: [A-Z]\b)?)")
BID = re.compile(r"^(\d+)(?:\s+or\s+(\d+))?\b")
ALTERNATE = re.compile(r"^Equipment Alternate ([A-Z])\b")
LEDGER_ID = re.compile(r"\bL-\d{4}\b")

HERE = Path(__file__).resolve().parent
DERIVED = HERE.parent / "derived"
PROJECT_WIKI = HERE.parent / "project" / "01_Project_Wiki" / "Project_Wiki.md"
DEFAULT_INPUTS = {
    "id_map": DERIVED / "reconciliation" / "Ledger_ID_Map.csv",
    "wiki_notes": DERIVED / "wiki" / "Wiki_Notes.csv",
    "wiki_links": DERIVED / "wiki" / "Wiki_Links.csv",
    "mto": HERE.parent / "project" / "02_Project_Ledger" / "MTO_Lines_rev1.csv",
    "open_items": DERIVED / "issues" / "Open_Items.csv",
}


def split_values(cell: str, seps: str = ";") -> list[str]:
    """Split on separators outside parentheses (rule 1)."""
    out, buf, depth = [], "", 0
    for ch in cell:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch in seps and depth == 0:
            out.append(buf)
            buf = ""
        else:
            buf += ch
    out.append(buf)
    return [" ".join(v.split()) for v in out if v.strip()]


def strip_parens(text: str) -> str:
    """Remove parenthetical text, nested or not."""
    prev = None
    while prev != text:
        prev, text = text, re.sub(r"\([^()]*\)", "", text)
    return " ".join(text.split())


def unwrap(note: str) -> str:
    """'(Det. 2)' -> 'Det. 2'; anything else is returned as written."""
    note = note.strip()
    if note.startswith("(") and note.endswith(")") and note.count("(") == 1:
        return note[1:-1].strip()
    return note


def level_of(raw: str) -> str | None:
    """Leading tag word: 'Unresolved: external reference, not staged' -> 'Unresolved'."""
    raw = raw.strip()
    return next((lv for lv in LEVELS if raw.startswith(lv)), None)


def weaker(level: str, text: str) -> str:
    """The weaker of a row level and any tag level written in a value (rule 7)."""
    for word in LEVEL_WORD.findall(text):
        if RANK[word] > RANK[level]:
            level = word
    return level


# Each parser returns ([(node id, label, note)], leftover) for one value.
def parse_sheet(value: str):
    m = SHEET.match(value)
    if not m:
        return [], value
    sheet = f"{m.group(1).upper()}{m.group(2)}{m.group(3).upper()}"
    return [(f"sheet:{sheet}", f"Sheet {sheet}", unwrap(m.group(4)))], None


def parse_spec(value: str):
    m = SPEC.match(value)
    if m:
        spec = f"{m.group(1)} {m.group(2)} {m.group(3)}"
        return [(f"spec:{spec}", f"Spec {spec}", unwrap(m.group(4)))], None
    m = APPENDIX.match(value)
    if m:
        return [(f"spec:{m.group(1)}", f"Spec {m.group(1)}", unwrap(m.group(2)))], None
    return [], value


def parse_note(value: str):
    m = BASIS_SUFFIX.match(value)
    if m:  # rev1: the link basis rides on the link as its note
        return [(f"note:{m.group(1)}", f"Wiki note {m.group(1)}", f"basis: {m.group(2)}")], None
    return [(f"note:{value}", f"Wiki note {value}", "")], None


def parse_unit(value: str):
    """A sheet, a spec section or an appendix, whichever parses."""
    found, left = parse_sheet(value)
    if found:
        return found, left
    return parse_spec(value)


def parse_addenda(cell: str):
    """Addenda cell -> ([(node id, label, note, fragment)], leftovers) (rule 5).

    A fragment without "Add. N" takes the number from the fragment before it.
    A fragment with no page is a note on the link(s) made just before it.
    """
    links, leftovers, number, last = [], [], None, []
    for frag in split_values(cell, ";|"):
        if NULL_VALUE.match(frag):
            leftovers.append(frag)
            continue
        m = ADD_NO.match(frag)
        if m:
            number, rest = m.group(1), frag[m.end():]
        else:
            rest = frag
        head = strip_parens(rest)
        pages = []
        for a, b in PAGE.findall(head):
            pages += [str(p) for p in range(int(a), int(b) + 1)] if b else [a]
        if not pages or number is None:
            if last:
                for link in last:
                    link[2].append(frag)
            else:
                leftovers.append(frag)
            continue
        items = []
        if len(pages) == 1:
            items = [f"{s} ¶{p}" for s, p in SPEC_PARA.findall(head)]
            c = CLARIFICATION.search(head)
            if c and not items:
                items = [f"Clarification {n}" for n in re.findall(r"\d+", c.group(1))]
        keys = [f"Add. {number} p.{pages[0]} {i}" for i in items] or \
               [f"Add. {number} p.{p}" for p in pages]
        last = [[f"addendum:{k}", k, [], frag] for k in keys]
        links += last
    return [(nid, label, "; ".join(notes), frag) for nid, label, notes, frag in links], leftovers


def parse_bids(cell: str) -> tuple[list[str], list[str]]:
    """Bid Item cell -> (['Bid Item 1', 'Equipment Alternate B'], leftovers) (rule 6)."""
    bids, leftovers = [], []
    for frag in split_values(cell, ";|"):
        if NULL_VALUE.match(frag):
            leftovers.append(frag)
            continue
        head = re.sub(r"^Unresolved\s*[—–-]\s*", "", strip_parens(frag))
        head = head.rsplit(":", 1)[-1].strip()
        m, a = BID.match(head), ALTERNATE.match(head)
        found = ([f"Bid Item {n}" for n in m.groups() if n] if m else
                 [f"Equipment Alternate {a.group(1)}"] if a else [])
        if not found:
            leftovers.append(frag)
        bids += [b for b in found if b not in bids]
    return bids, leftovers


# Ledger column -> (value parser, edge relation)
LINKS = {
    "Drawing Sheets": (parse_sheet, "shown_on"),
    "Spec Sections": (parse_spec, "specified_in"),
    "Wiki Note(s)": (parse_note, "described_in"),
}
ADDENDA = ("Addenda", "changed_by")
ITEM_FIELDS = {"Area/Building": "area", "Discipline": "discipline", "Status": "status",
               "Submittal Req (Y/N)": "submittal_req",
               "Testing/Startup Req (Y/N)": "testing_startup_req",
               # Ledger rev1 only; a rev0 Ledger leaves these out
               "CWP": "cwp", "Quantity": "quantity", "Unit": "unit",
               "Quantity Confidence": "quantity_confidence"}
DOC_TYPES = {"sheet": "sheet", "spec": "spec", "addendum": "addendum", "note": "note"}
NOTE_TEXT_MAX = 2000  # note text: the body up to the last full sentence within this
HEADING = re.compile(r"^#{1,3} ")  # a note body ends at the next level 1-3 heading
MERGE_LINE = re.compile(r"^> Merge: ")  # Merge metadata under each heading, not note content
# A sentence ends at . ! or ? (plus closing brackets or quotes) before a line break, or
# before a space and a capital, bracket, quote, list or table mark. Abbreviations that
# can come before a capital are not ends.
SENTENCE_END = re.compile(r"[.!?][)\]\"'’”]*(?=\n|$|[ \t]+[A-Z(\[\"“'‘|*\-])")
ABBREVIATIONS = {"add", "det", "no", "nos", "fig", "sht", "sec", "div", "ref", "vs", "mr",
                 "ms", "dr", "st", "co", "inc", "approx", "e.g", "i.e", "dept", "typ",
                 "min", "max", "inf", "mfr", "ea", "sch", "ft", "in", "p", "pp", "cf", "al"}
OPEN_ITEM_MAX_IDS = 15  # an open item naming more Ledger IDs gets no item links
# Fields a repeated link adds to (rule 8); the rest keep the first link's value.
MERGE_FIELDS = ("value", "note", "wiki_source", "wiki_confidence", "source_location",
                "wiki_line", "written_as", "basis")


def norm(header: str) -> str:
    return re.sub(r"[^a-z0-9]", "", header.lower())


def snake(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", header.lower()).strip("_")


def pin_hash_seed() -> None:
    """Re-run with PYTHONHASHSEED=0 so clustering is identical run to run
    (the same pin graphify applies to cluster-only)."""
    if os.environ.get("PYTHONHASHSEED") is None:
        env = dict(os.environ, PYTHONHASHSEED="0")
        sys.exit(subprocess.call([sys.executable, *sys.argv], env=env))


class Input:
    """One CSV input: its rows (with file line numbers) and its column lookup."""

    def __init__(self, name: str, path: Path | None, needed: dict[str, tuple[str, ...]],
                 optional: set[str] = frozenset()):
        self.name, self.path, self.rows, self.cols = name, path, [], {}
        self.rel = Path(os.path.relpath(path)).as_posix() if path else ""
        self.status, self.sha = "missing", ""
        if path is None or not path.is_file():
            return
        data = path.read_bytes()
        self.sha = hashlib.sha256(data).hexdigest()
        reader = csv.reader(io.StringIO(data.decode("utf-8-sig"), newline=""))
        header = next(reader, [])
        by_norm = {norm(h): i for i, h in reversed(list(enumerate(header)))}
        lacking = []
        for key, names in needed.items():
            idx = next((by_norm[norm(n)] for n in names if norm(n) in by_norm), None)
            if idx is None and key not in optional:
                lacking.append(names[0])
            self.cols[key] = idx
        self.header = header
        if lacking:
            self.status = "skipped: no column " + ", ".join(lacking)
            return
        while True:  # a row's line is its first file line (quoted cells can wrap)
            line = reader.line_num + 1
            rec = next(reader, None)
            if rec is None:
                break
            if any(v.strip() for v in rec):
                self.rows.append((line, rec))
        self.status = "used"

    def get(self, rec: list[str], key: str) -> str:
        idx = self.cols.get(key)
        return rec[idx].strip() if idx is not None and idx < len(rec) else ""

    def record(self, rec: list[str]) -> dict[str, str]:
        return {snake(h): (rec[i].strip() if i < len(rec) else "")
                for i, h in enumerate(self.header) if h.strip()}


class Graph:
    """Nodes and links, with one link per source and target (rule 8)."""

    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.edges: dict[tuple[str, str], dict] = {}
        self.warnings: list[str] = []

    def doc(self, nid: str, label: str, src: str) -> dict:
        """A sheet, spec, addendum or note node; source_file is the input that first named it."""
        kind = DOC_TYPES[nid.split(":", 1)[0]]
        return self.nodes.setdefault(nid, {"id": nid, "label": label, "node_type": kind,
                                           "file_type": "document", "source_file": src})

    def link(self, source: str, target: str, relation: str, level: str, keep: str, **attrs):
        """keep='weakest' merges repeats at the weakest level (Ledger rule 8);
        keep='strongest' keeps the best-supported level (independent sources)."""
        e = self.edges.get((source, target))
        if e is None:
            self.edges[(source, target)] = {
                "source": source, "target": target, "relation": relation,
                "confidence": CONFIDENCE[level], "link_level": level, **attrs}
            return
        if e["relation"] != relation:
            self.warnings.append(f"{source} -> {target}: relation {relation!r} merged "
                                 f"into {e['relation']!r}")
        new, old = RANK[level], RANK[e["link_level"]]
        if (keep == "weakest" and new > old) or (keep == "strongest" and new < old):
            e["link_level"], e["confidence"] = level, CONFIDENCE[level]
        for field in MERGE_FIELDS:  # other fields keep the first link's value
            text, have = attrs.get(field) or "", e.get(field) or ""
            if text and text not in have.split("; "):
                e[field] = f"{have}; {text}" if have else text


def load_ledger(g: Graph, ledger: Path, id_map: Input) -> tuple[dict, dict, list[str]]:
    """Ledger rows -> item nodes and their links. Returns (id -> node, tag -> [ids], errors)."""
    src = Path(os.path.relpath(ledger)).as_posix()
    with open(ledger, encoding="utf-8-sig", newline="") as f:
        rows = list(enumerate(csv.DictReader(f), start=2))  # line 1 is the header

    errors = []
    id_by_row: dict[int, tuple[str, str]] = {}
    for line, rec in id_map.rows:
        lid, row_no = id_map.get(rec, "id"), id_map.get(rec, "row")
        if not LEDGER_ID.fullmatch(lid) or not row_no.isdigit():
            errors.append(f"{id_map.rel} line {line}: bad Ledger ID {lid!r} or row {row_no!r}")
            continue
        if int(row_no) in id_by_row:
            errors.append(f"{id_map.rel} line {line}: Ledger Row {row_no} is mapped twice")
        id_by_row[int(row_no)] = (lid, id_map.get(rec, "tag"))
    if len({lid for lid, _ in id_by_row.values()}) != len(id_by_row):
        errors.append(f"{id_map.rel}: a Ledger ID is used twice")

    # Ledger rev1 carries its own Ledger ID. Rows the map covers must agree with it;
    # rows added after the map (L-0448 on) take the row's ID.
    own_id = bool(rows) and "Ledger ID" in rows[0][1]
    if own_id:
        seen_ids: dict[str, int] = {}
        for row_no, row in rows:
            lid = row["Ledger ID"].strip()
            if not LEDGER_ID.fullmatch(lid):
                errors.append(f"Ledger line {row_no}: bad Ledger ID {lid!r}")
            elif lid in seen_ids:
                errors.append(f"Ledger line {row_no}: Ledger ID {lid} repeats line {seen_ids[lid]}")
            seen_ids.setdefault(lid, row_no)
            mapped = id_by_row.get(row_no)
            if mapped and mapped[0] != lid:
                errors.append(f"Ledger line {row_no}: {lid} {row['Tag'].strip()!r} but {id_map.rel} has "
                              f"{mapped[0]} {mapped[1]!r}; the map is stale")
            elif mapped and mapped[1] != row["Tag"].strip():
                # The ID agrees and the Tag was changed since the map (Ledger rev2 applies the printed Tags of
                # P-0234/P-0235). IDs are permanent and Tags may change, so this is reported, not an error.
                g.warnings.append(f"Ledger line {row_no}: {lid} is {row['Tag'].strip()!r} in the Ledger and "
                                  f"{mapped[1]!r} in {id_map.rel} (Tag changed since the map; the ID agrees)")
            if not mapped and lid in {m[0] for m in id_by_row.values()}:
                errors.append(f"Ledger line {row_no}: {lid} is mapped to another row in {id_map.rel}")
            id_by_row[row_no] = (lid, row["Tag"].strip())
    tag_col = TAG_COL_REV1 if rows and TAG_COL not in rows[0][1] else TAG_COL

    # graphify merges nodes that share a source file and a label, so a Tag on two
    # rows (SD-1) is labeled "<Tag> [<Ledger ID>]"; every other item is labeled by its Tag.
    tag_count: dict[str, int] = {}
    for _, row in rows:
        tag_count[row["Tag"].strip()] = tag_count.get(row["Tag"].strip(), 0) + 1
    items, ids_by_tag = {}, {}
    for row_no, row in rows:
        tag = row["Tag"].strip()
        mapped = id_by_row.get(row_no)
        if mapped is None:
            errors.append(f"Ledger line {row_no}: Tag {tag!r} has no Ledger ID in {id_map.rel}")
            continue
        lid, map_tag = mapped
        if map_tag != tag:
            errors.append(f"Ledger line {row_no}: Tag {tag!r} but {id_map.rel} has "
                          f"{map_tag!r} for {lid}; the map is stale")
            continue
        ids_by_tag.setdefault(tag, []).append(lid)
        raw_level = row[tag_col].strip()
        level = level_of(raw_level)
        if level is None:  # never guess: weakest confidence, and report it
            g.warnings.append(f"unknown tag level, treated as Unresolved: Ledger line "
                              f"{row_no}: {tag!r} has {raw_level!r}")
            level = "Unresolved"
        citation = row["Source Citation"].strip()
        bids, bid_left = parse_bids(row["Bid Item"])
        unlinked = [f"Bid Item: {v}" for v in bid_left]
        common = {"ledger_level": raw_level, "citation": citation, "ledger_line": row_no,
                  "source_file": src, "source_location": f"L{row_no}"}

        def link(nid, label, note, value, relation):
            g.doc(nid, label, src)
            g.link(lid, nid, relation, weaker(level, value), "weakest",
                   **common, value=value, note=note)

        for col, (parse, relation) in LINKS.items():
            for value in split_values(row[col]):
                if NULL_VALUE.match(value):
                    unlinked.append(f"{col}: {value}")
                    continue
                found, leftover = parse(value)
                if leftover:
                    unlinked.append(f"{col}: {leftover}")
                for nid, label, note in found:
                    link(nid, label, note, value, relation)
        col, relation = ADDENDA
        found, leftovers = parse_addenda(row[col])
        unlinked += [f"{col}: {v}" for v in leftovers]
        for nid, label, note, frag in found:
            link(nid, label, note, frag, relation)

        node = {
            "id": lid, "label": f"{tag} [{lid}]" if tag_count[tag] > 1 else tag,
            "node_type": "item", "file_type": "concept",
            "source_file": src, "source_location": f"L{row_no}",
            "ledger_id": lid, "tag": tag, "item_name": row["Name"].strip(),
            "ledger_line": row_no, "ledger_level": raw_level, "citation": citation,
            "lane": split_values(row["Lane"]), "bid_items": bids,
            "bid_item": row["Bid Item"].strip(),
        }
        node.update({attr: row[col].strip() for col, attr in ITEM_FIELDS.items() if col in row})
        node["unlinked"] = unlinked
        items[lid] = node
    return items, ids_by_tag, errors


def input_level(g: Graph, raw: str, where: str) -> str:
    level = level_of(raw[:1].upper() + raw[1:])  # derived files may write "verified"
    if level is None:
        g.warnings.append(f"unknown tag level, treated as Unresolved: {where} has {raw!r}")
        return "Unresolved"
    return weaker(level, raw)


def ledger_ids(cell: str) -> tuple[list[str], str]:
    """'L-0117; L-0121' -> (['L-0117', 'L-0121'], leftover text)."""
    ids = []
    for lid in LEDGER_ID.findall(cell):
        if lid not in ids:
            ids.append(lid)
    rest = LEDGER_ID.sub("", cell).strip(" ;,/&")
    return ids, rest


def cut_at_sentence(text: str, limit: int = NOTE_TEXT_MAX) -> tuple[str, bool]:
    """(text up to the last full sentence within `limit` characters, whether it was cut).
    With no sentence end in range, cut at the last space and add "…"."""
    if len(text) <= limit:
        return text, False
    end = 0
    for m in SENTENCE_END.finditer(text):
        if m.end() > limit:
            break
        word = re.search(r"([A-Za-z.]+)[.!?]$", text[:m.start() + 1])
        if word and word.group(1).lower().strip(".") in ABBREVIATIONS:
            continue
        end = m.end()
    if end:
        return text[:end], True
    return text[:text.rfind(" ", 0, limit)].rstrip() + " …", True


class WikiText:
    """Note bodies from Project_Wiki.md, found by heading line."""

    def __init__(self, path: Path):
        self.path, self.rel = path, Path(os.path.relpath(path)).as_posix()
        self.lines, self.sha, self.status = [], "", "missing"
        if path.is_file():
            data = path.read_bytes()
            self.sha = hashlib.sha256(data).hexdigest()
            self.lines = data.decode("utf-8-sig").split("\n")
            self.status = "used"

    def body(self, note_id: str, heading_line: str) -> tuple[str | None, str]:
        """(the note body, or None, and why not). The body runs from the line after
        the heading to the next level 1-3 heading, less the Merge metadata line."""
        if not heading_line.isdigit() or not 0 < int(heading_line) <= len(self.lines):
            return None, f"heading line {heading_line!r} is not in {self.rel}"
        start = int(heading_line) - 1
        if not self.lines[start].rstrip("\r").startswith(f"### {note_id} — "):
            return None, f"{self.rel} line {heading_line} is not the heading of {note_id!r}"
        out = []
        for raw in self.lines[start + 1:]:
            text = raw.rstrip("\r")
            if HEADING.match(text):
                break
            if not MERGE_LINE.match(text):
                out.append(text.rstrip())
        body = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()
        return body, ""


def add_wiki_notes(g: Graph, notes: Input, wiki_ids: set[str], wiki: WikiText) -> dict:
    """Note content as attributes on note nodes, plus a `describes` link to its own unit.
    Returns counts: notes with text, text cut at a sentence, cut without one, no text."""
    counts = {"full": 0, "cut at a sentence": 0, "cut at a space": 0, "no text": 0}
    for line, rec in notes.rows:
        nid = notes.get(rec, "id")
        if not nid:
            g.warnings.append(f"{notes.rel} line {line}: blank Note ID")
            continue
        if nid in wiki_ids:
            g.warnings.append(f"{notes.rel} line {line}: Note ID {nid!r} repeats; first kept")
            continue
        wiki_ids.add(nid)
        node = g.doc(f"note:{nid}", f"Wiki note {nid}", notes.rel)
        attrs = notes.record(rec)
        for key in ("note_id", "document_id"):
            attrs.pop(key, None)
        if "type" in attrs:
            attrs["note_type"] = attrs.pop("type")
        for key in [k for k in attrs if k.startswith("summary")]:  # replaced by note_text
            attrs.pop(key)
        node.update({k: v for k, v in attrs.items() if k not in node})
        node.update({"source_file": notes.rel, "source_location": f"L{line}",
                     "wiki_note_found": True})
        body, why = (wiki.body(nid, attrs.get("heading_line", "")) if wiki.status == "used"
                     else (None, f"{wiki.rel} missing"))
        if body is None:
            g.warnings.append(f"{notes.rel} line {line}: no note text for {nid!r}: {why}")
            counts["no text"] += 1
            node.update({"note_text": "", "note_text_chars": 0, "note_text_cut": "",
                         "note_text_source": ""})
        else:
            text, cut = cut_at_sentence(body)
            counts["full" if not cut else "cut at a space" if text.endswith(" …")
                   else "cut at a sentence"] += 1
            node.update({"note_text": text, "note_text_chars": len(body),
                         "note_text_cut": "Y" if cut else "N",
                         "note_text_source": f"{wiki.rel} line {attrs.get('heading_line')}"})
        found, _ = parse_unit(nid)
        for unit, label, _ in found:
            g.doc(unit, label, notes.rel)
            heading = attrs.get("heading_line", "")
            g.link(f"note:{nid}", unit, "describes", "Verified", "strongest",
                   citation=f"Project Wiki note heading {nid!r}"
                            + (f" (line {heading})" if heading else ""),
                   source_file=notes.rel, source_location=f"L{line}", value=nid, note="")
    return counts


def add_wiki_links(g: Graph, links: Input, items: dict, ids_by_tag: dict,
                   wiki_ids: set[str], unlinked: dict[str, list[str]]) -> dict[str, int]:
    """Wiki_Links.csv rows -> links from note nodes. Returns counts of rows not linked."""
    skipped: dict[str, int] = {}
    addenda = {nid for nid in g.nodes if nid.startswith("addendum:")}

    def skip(note_id, why, text):
        unlinked.setdefault(f"note:{note_id}", []).append(f"{why}: {text}")
        skipped[why] = skipped.get(why, 0) + 1

    for line, rec in links.rows:
        note_id, ttype = links.get(rec, "id"), links.get(rec, "type").lower()
        target, source = links.get(rec, "target"), links.get(rec, "source")
        raw_conf = links.get(rec, "confidence")
        where = f"{links.rel} line {line}"
        if not note_id or not target:
            g.warnings.append(f"{where}: blank Note ID or Target")
            continue
        level = input_level(g, raw_conf, where)
        g.doc(f"note:{note_id}", f"Wiki note {note_id}", links.rel)
        wiki_line = links.get(rec, "wiki_line")
        attrs = {"citation": f"Wiki note {note_id}, {source or 'source not stated'}"
                             + (f" (Project Wiki line {wiki_line})" if wiki_line else ""),
                 "source_file": links.rel, "source_location": f"L{line}",
                 "wiki_source": source, "wiki_confidence": raw_conf, "value": target,
                 "wiki_line": wiki_line, "written_as": links.get(rec, "written_as"),
                 "basis": links.get(rec, "basis")}
        targets: list[tuple[str, str, str, str]] = []  # (nid, label, relation, level)
        if "equip" in ttype or ttype == "tag":
            ids, _ = ledger_ids(links.get(rec, "ledger_id"))
            ids = [i for i in ids if i in items]
            lv = level
            if not ids:
                ids = ids_by_tag.get(target, [])
                lv = weaker(level, "Inferred") if ids else level
            if len(ids) > 1:
                # A Tag on two rows (SD-1): keep the row that cites this note.
                cites = [i for i in ids if f"note:{note_id}" in
                         {t for (s, t) in g.edges if s == i}]
                ids, lv = (cites, weaker(lv, "Inferred")) if len(cites) == 1 else (ids, lv)
            if len(ids) != 1:
                skip(note_id, "equipment tag, no single Ledger ID" if ids else
                     "equipment tag, no Ledger ID", target)
                continue
            targets.append((ids[0], "", "mentions", lv))
        elif "sheet" in ttype:
            found, left = parse_sheet(target)
            if left:
                skip(note_id, "sheet did not parse", target)
            targets += [(n, lb, "references", level) for n, lb, _ in found]
        elif "spec" in ttype:
            found, left = parse_spec(target)
            if left:
                skip(note_id, "spec section did not parse", target)
            targets += [(n, lb, "references", level) for n, lb, _ in found]
        elif "addend" in ttype:
            found, left = parse_addenda(target)
            ids = [(n, lb) for n, lb, _, _ in found if not re.search(r" p\.0\b", lb)]
            if not ids:
                # "Add. 4 Clarification 5": link only when the Ledger graph has
                # exactly one node for that clarification.
                c = CLARIFICATION.search(target)
                a = ADD_NO.match(target)
                if c and a:
                    for n in re.findall(r"\d+", c.group(1)):
                        hits = sorted(x for x in addenda if re.fullmatch(
                            rf"addendum:Add\. {a.group(1)} p\.\d+ Clarification {n}", x))
                        if len(hits) == 1:
                            ids.append((hits[0], hits[0].split(":", 1)[1]))
            if not ids:
                skip(note_id, "addendum item did not parse", target)
            targets += [(n, lb, "references", level) for n, lb in ids]
        elif "note" in ttype:
            if target in wiki_ids or f"note:{target}" in g.nodes:
                targets.append((f"note:{target}", f"Wiki note {target}", "references", level))
            else:
                skip(note_id, "note not found", target)
        else:
            skip(note_id, f"target type {ttype!r} not handled", target)
        for nid, label, relation, lv in targets:
            if nid == f"note:{note_id}":
                continue
            if label:
                g.doc(nid, label, links.rel)
            extra = {"ledger_line": items[nid]["ledger_line"]} if nid in items else {}
            g.link(f"note:{note_id}", nid, relation, lv, "strongest", **attrs, **extra)
    return skipped


def add_mto(g: Graph, mto: Input, items: dict) -> list[str]:
    """Starter MTO lines -> nodes linked to their Ledger ID(s) and sheet."""
    problems = []
    for line, rec in mto.rows:
        no = mto.get(rec, "line")
        where = f"{mto.rel} line {line}"
        nid = f"mto:{no}"
        if not no or nid in g.nodes:
            problems.append(f"{where}: MTO Line {no!r} is blank or repeats")
            continue
        level = input_level(g, mto.get(rec, "confidence"), where)
        qty, unit = mto.get(rec, "quantity"), mto.get(rec, "unit")
        attrs = mto.record(rec)
        label = f"MTO line {no}" if no.isdigit() else no      # rev1 IDs read "MTO-0013"
        node = {"id": nid, "label": f"{label}: {qty} {unit}".strip(),
                "node_type": "mto", "file_type": "concept",
                "source_file": mto.rel, "source_location": f"L{line}",
                **{f"mto_{k}" if k in ("id", "label") else k: v for k, v in attrs.items()}}
        unlinked = []
        common = {"citation": mto.get(rec, "citation"), "source_file": mto.rel,
                  "source_location": f"L{line}", "ledger_level": mto.get(rec, "confidence")}
        ids, rest = ledger_ids(mto.get(rec, "ledger_id"))
        if rest and not NULL_VALUE.match(rest):
            unlinked.append(f"Ledger ID: {rest}")
        if not ids:
            unlinked.append("Ledger ID: blank (" + (mto.get(rec, "tie") or "no tie") + ")")
        for lid in ids:
            if lid not in items:
                unlinked.append(f"Ledger ID: {lid} not in the Ledger")
                continue
            g.link(nid, lid, "quantity_of", level, "weakest", **common,
                   ledger_line=items[lid]["ledger_line"], value=lid,
                   note=mto.get(rec, "tie"))
        for value in split_values(mto.get(rec, "sheet")):
            found, left = parse_sheet(value)
            if left:
                unlinked.append(f"Sheet: {left}")
            for sid, label, note in found:
                g.doc(sid, label, mto.rel)
                g.link(nid, sid, "measured_on", level, "weakest", **common, value=value,
                       note="; ".join(x for x in (note, mto.get(rec, "keyed_note")) if x))
        node["unlinked"] = unlinked
        g.nodes[nid] = node
    return problems


def short_title(title: str, limit: int = 60) -> str:
    """The lead clause of a title, for the label: up to the first colon, else `limit` chars.
    The full title stays on the node."""
    head = title.split(":", 1)[0].strip()
    if head and len(head) <= 80 and head != title:
        return head
    return title if len(title) <= limit else title[:limit].rstrip() + "…"


def add_open_items(g: Graph, oi: Input, items: dict) -> list[str]:
    """Open items -> nodes linked to their Ledger IDs, sheets and spec sections."""
    problems = []
    for line, rec in oi.rows:
        item_id = oi.get(rec, "id")
        where = f"{oi.rel} line {line}"
        nid = f"open:{item_id}"
        if not item_id or nid in g.nodes:
            problems.append(f"{where}: Item ID {item_id!r} is blank or repeats")
            continue
        level = input_level(g, oi.get(rec, "confidence"), where)
        title = oi.get(rec, "title")
        attrs = oi.record(rec)
        node = {"id": nid, "label": f"{item_id} {short_title(title)}".strip(),
                "node_type": "open_item",
                "file_type": "rationale", "source_file": oi.rel, "source_location": f"L{line}",
                **{f"open_{k}" if k in ("id", "label", "type") else k: v
                   for k, v in attrs.items()}}
        unlinked = []
        common = {"citation": oi.get(rec, "citation"), "source_file": oi.rel,
                  "source_location": f"L{line}", "ledger_level": oi.get(rec, "confidence")}
        ids, rest = ledger_ids(oi.get(rec, "ledger_ids"))
        if rest and not NULL_VALUE.match(rest):
            unlinked.append(f"Ledger IDs: {rest}")
        # Duplicate items and items naming many rows would join the rows they list
        # (Carl, 2026-09-30): they keep the node and their sheet and spec links, and
        # list the IDs instead of linking them.
        withheld = ("duplicate item" if oi.get(rec, "type").lower() == "duplicate" else
                    f"{len(ids)} Ledger IDs (over {OPEN_ITEM_MAX_IDS})"
                    if len(ids) > OPEN_ITEM_MAX_IDS else "")
        node["ledger_id_list"] = ids
        node["item_links"] = f"none: {withheld}" if withheld else "linked"
        for lid in ids:
            if lid not in items:
                unlinked.append(f"Ledger IDs: {lid} not in the Ledger")
                continue
            if withheld:
                continue
            g.link(nid, lid, "concerns", level, "weakest", **common,
                   ledger_line=items[lid]["ledger_line"], value=lid, note="")
        for col, key, parse in (("Sheets", "sheets", parse_sheet),
                                ("Spec Sections", "specs", parse_spec)):
            for value in split_values(oi.get(rec, key), ";,"):
                if NULL_VALUE.match(value):
                    continue
                found, left = parse(value)
                if left:
                    unlinked.append(f"{col}: {left}")
                for tid, label, note in found:
                    g.doc(tid, label, oi.rel)
                    g.link(nid, tid, "cites", weaker(level, value), "weakest", **common,
                           value=value, note=note)
        node["unlinked"] = unlinked
        g.nodes[nid] = node
    return problems


NEEDED = {
    "id_map": {"id": ("Ledger ID",), "row": ("Ledger Row",), "tag": ("Tag",)},
    "wiki_notes": {"id": ("Note ID", "Document ID")},
    "wiki_links": {"id": ("Note ID", "Document ID"), "type": ("Target Type",),
                   "target": ("Target",), "source": ("Source",),
                   "confidence": ("Confidence",), "ledger_id": ("Ledger ID", "Ledger IDs"),
                   "wiki_line": ("Wiki Line",), "written_as": ("Written As",),
                   "basis": ("Basis",)},
    "mto": {"line": ("MTO Line", "MTO Line ID"), "ledger_id": ("Ledger ID", "Ledger IDs"),
            "quantity": ("Quantity",), "unit": ("Unit",), "sheet": ("Sheet", "Sheets"),
            "confidence": ("Confidence",), "citation": ("Source Citation",),
            "keyed_note": ("Keyed Note",), "tie": ("Tie Basis",)},
    "open_items": {"id": ("Item ID",), "title": ("Title",), "type": ("Type",),
                   "ledger_ids": ("Ledger IDs", "Ledger ID"), "sheets": ("Sheets", "Sheet"),
                   "specs": ("Spec Sections", "Spec Section"),
                   "citation": ("Source Citation",), "confidence": ("Confidence",)},
}
# Columns a file may lack without being skipped.
OPTIONAL = {"wiki_links": {"ledger_id", "wiki_line", "written_as", "basis"},
            "mto": {"keyed_note", "tie"}}


def main() -> int:
    ap = argparse.ArgumentParser(description="Ledger CSV + derived files -> graphify graph.json (no LLM)")
    ap.add_argument("ledger", help="path to a Ledger CSV")
    ap.add_argument("--out", required=True, help="folder; graph.json goes to <out>/graphify-out/")
    ap.add_argument("--wiki", default=str(PROJECT_WIKI),
                    help=f"default {Path(os.path.relpath(PROJECT_WIKI)).as_posix()}")
    for key, path in DEFAULT_INPUTS.items():
        ap.add_argument(f"--{key.replace('_', '-')}", default=str(path),
                        help=f"default {Path(os.path.relpath(path)).as_posix()}")
    args = ap.parse_args()
    pin_hash_seed()

    from graphify.build import build_from_json
    from graphify.cluster import cluster
    from graphify.export import to_json

    inputs = {key: Input(key, Path(getattr(args, key)), needed, OPTIONAL.get(key, set()))
              for key, needed in NEEDED.items()}
    if inputs["id_map"].status != "used":
        print(f"ERROR {inputs['id_map'].rel}: {inputs['id_map'].status}; "
              f"the Ledger ID map is required", file=sys.stderr)
        return 2

    g = Graph()
    ledger = Path(args.ledger)
    items, ids_by_tag, errors = load_ledger(g, ledger, inputs["id_map"])
    if errors:
        for msg in errors:
            print(f"ERROR {msg}", file=sys.stderr)
        return 2
    wiki_ids: set[str] = set()
    extra_unlinked: dict[str, list[str]] = {}
    wiki_skipped: dict[str, int] = {}
    problems = []
    wiki = WikiText(Path(args.wiki))
    text_counts = {}
    if inputs["wiki_notes"].status == "used":
        text_counts = add_wiki_notes(g, inputs["wiki_notes"], wiki_ids, wiki)
    for nid, node in g.nodes.items():
        if node["node_type"] == "note":
            node.setdefault("wiki_note_found", False)
    if inputs["wiki_links"].status == "used":
        wiki_skipped = add_wiki_links(g, inputs["wiki_links"], items, ids_by_tag,
                                      wiki_ids, extra_unlinked)
    if inputs["mto"].status == "used":
        problems += add_mto(g, inputs["mto"], items)
    if inputs["open_items"].status == "used":
        problems += add_open_items(g, inputs["open_items"], items)
    for nid, node in g.nodes.items():
        if node["node_type"] == "note":
            node["unlinked"] = extra_unlinked.get(nid, [])

    clash = sorted(set(items) & set(g.nodes))
    problems += [f"node id {c!r} is both an item and another node" for c in clash]
    if problems:
        for msg in problems:
            print(f"ERROR {msg}", file=sys.stderr)
        return 2

    nodes = list(items.values()) + list(g.nodes.values())
    edges = list(g.edges.values())
    graph = build_from_json({"nodes": nodes, "edges": edges}, directed=True)
    communities = cluster(graph)
    out = Path(args.out) / "graphify-out"
    out.mkdir(parents=True, exist_ok=True)
    to_json(graph, communities, str(out / "graph.json"), force=True)

    kinds: dict[str, int] = {}
    for n in nodes:
        kinds[n["node_type"]] = kinds.get(n["node_type"], 0) + 1
    relations: dict[str, int] = {}
    for e in edges:
        relations[e["relation"]] = relations.get(e["relation"], 0) + 1

    # What each build used, and what it made: two small CSVs beside graphify-out/.
    with open(Path(args.out) / "Build_Inputs.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Input", "Path", "Status", "Rows", "SHA-256"])
        w.writerow(["ledger", Path(os.path.relpath(ledger)).as_posix(), "used", len(items),
                    hashlib.sha256(ledger.read_bytes()).hexdigest()])
        for key, inp in inputs.items():
            w.writerow([key, inp.rel, inp.status, len(inp.rows), inp.sha])
            if key == "wiki_notes":
                w.writerow(["wiki_text", wiki.rel, wiki.status if inp.status == "used"
                            else "not read", len(wiki.lines), wiki.sha])
    with open(Path(args.out) / "Build_Counts.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Kind", "Name", "Count"])
        w.writerows(["node type", k, kinds[k]] for k in sorted(kinds))
        w.writerows(["link relation", k, relations[k]] for k in sorted(relations))

    print(f"{len(items)} Ledger rows -> {len(items)} item nodes keyed on Ledger ID")
    for key, inp in inputs.items():
        print(f"input {key}: {inp.status} ({len(inp.rows)} rows) {inp.rel}")
    print(f"nodes by type {dict(sorted(kinds.items()))}")
    print(f"links by relation {dict(sorted(relations.items()))}")
    print(f"{graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges, "
          f"{len(communities)} communities -> {out / 'graph.json'}")
    for tag, ids in ids_by_tag.items():
        if len(ids) > 1:
            print(f"NOTE Tag {tag!r} is on {', '.join(ids)}; separate nodes labeled "
                  f"'<Tag> [<Ledger ID>]', no link between them")
    n_unlinked = sum(len(n.get("unlinked", [])) for n in nodes)
    print(f"NOTE {n_unlinked} values made no link; kept on their node under 'unlinked'")
    if text_counts:
        print("note text: " + ", ".join(f"{n} {k}" for k, n in text_counts.items()))
    withheld = [n for n in nodes if n.get("item_links", "").startswith("none")]
    if withheld:
        print(f"NOTE {len(withheld)} open items list their Ledger IDs without item links "
              f"({sum(1 for n in withheld if 'duplicate' in n['item_links'])} duplicate items, "
              f"{sum(1 for n in withheld if 'over' in n['item_links'])} over "
              f"{OPEN_ITEM_MAX_IDS} IDs)")
    for why, n in sorted(wiki_skipped.items()):
        print(f"NOTE Wiki_Links rows not linked: {n} x {why}")
    for msg in g.warnings:
        print(f"WARNING {msg}")
    print(f"next: graphify cluster-only {args.out} --no-label")
    return 1 if any(m.startswith("unknown tag level") for m in g.warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
