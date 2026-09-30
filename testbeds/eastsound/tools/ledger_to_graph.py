#!/usr/bin/env python3
"""Build a knowledge graph from a Project Ledger CSV. No LLM calls.

Output is graphify-compatible: query it with `graphify explain` and
`graphify path --undirected` (pass --graph <out>/graphify-out/graph.json),
and render the report and viewer with `graphify cluster-only <out> --no-label`.

Every Ledger row becomes an item node. Drawing Sheets, Spec Sections, Addenda
and Wiki Note(s) become links; Lane and Bid Item stay on the item node as
attributes, so they don't act as hubs. Parsing rules were approved in Prompt 3
step 2 (2026-09-30); testbeds/eastsound/graph/README.md lists them.

Tested on graphifyy 0.9.72 / Python 3.11.

Usage: python testbeds/eastsound/tools/ledger_to_graph.py <ledger.csv> --out <folder>
"""
import argparse
import csv
import os
import re
import subprocess
import sys
from pathlib import Path

TAG_COL = "Verified/Verified-Visual/Inferred/Unresolved"
LEVELS = ("Verified-Visual", "Verified", "Inferred", "Unresolved")  # longest match first
# Ledger tag level -> graphify confidence. The original level rides on every edge.
CONFIDENCE = {"Verified-Visual": "EXTRACTED", "Verified": "EXTRACTED",
              "Inferred": "INFERRED", "Unresolved": "AMBIGUOUS"}
RANK = {"Verified-Visual": 0, "Verified": 0, "Inferred": 1, "Unresolved": 2}
LEVEL_WORD = re.compile(r"\b(Verified-Visual|Verified|Inferred|Unresolved)\b")

# Values that mean "no link" (rule 2). Anything else that doesn't parse is also
# kept on the item node under `unlinked`, never guessed.
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
    return [(f"note:{value}", f"Wiki note {value}", "")], None


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
               "Testing/Startup Req (Y/N)": "testing_startup_req"}


def pin_hash_seed() -> None:
    """Re-run with PYTHONHASHSEED=0 so clustering is identical run to run
    (the same pin graphify applies to cluster-only)."""
    if os.environ.get("PYTHONHASHSEED") is None:
        env = dict(os.environ, PYTHONHASHSEED="0")
        sys.exit(subprocess.call([sys.executable, *sys.argv], env=env))


def main() -> int:
    ap = argparse.ArgumentParser(description="Ledger CSV -> graphify graph.json (no LLM)")
    ap.add_argument("ledger", help="path to a Ledger CSV")
    ap.add_argument("--out", required=True, help="folder; graph.json goes to <out>/graphify-out/")
    args = ap.parse_args()
    pin_hash_seed()

    from graphify.build import build_from_json
    from graphify.cluster import cluster
    from graphify.export import to_json

    src = Path(os.path.relpath(args.ledger)).as_posix()
    with open(args.ledger, encoding="utf-8-sig", newline="") as f:
        rows = list(enumerate(csv.DictReader(f), start=2))  # line 1 is the header

    # Rule 9: a Tag on more than one row is keyed "<Tag> [L<line>]" on every row.
    lines_by_tag: dict[str, list[int]] = {}
    for row_no, row in rows:
        lines_by_tag.setdefault(row["Tag"].strip(), []).append(row_no)
    repeated = {t: ls for t, ls in lines_by_tag.items() if len(ls) > 1}

    items, docs, edges, unknown, problems = [], {}, [], [], []
    item_ids: set[str] = set()

    for row_no, row in rows:
        tag = row["Tag"].strip()
        key = f"{tag} [L{row_no}]" if tag in repeated else tag
        if not tag or key in item_ids:
            problems.append(f"line {row_no}: Tag {tag!r} is blank or keys twice")
            continue
        item_ids.add(key)
        raw_level = row[TAG_COL].strip()
        level = level_of(raw_level)
        if level is None:  # never guess: weakest confidence, and report it
            unknown.append(f"line {row_no}: {tag!r} has tag level {raw_level!r}")
            level = "Unresolved"
        citation = row["Source Citation"].strip()
        bids, bid_left = parse_bids(row["Bid Item"])
        unlinked = [f"Bid Item: {v}" for v in bid_left]

        row_links: dict[str, dict] = {}  # target -> edge; rule 8, one link per target

        def link(nid, label, note, value, relation):
            docs.setdefault(nid, label)
            lv = weaker(level, value)
            e = row_links.get(nid)
            if e is None:
                row_links[nid] = {
                    "source": key, "target": nid, "relation": relation,
                    "confidence": CONFIDENCE[lv], "ledger_level": raw_level, "link_level": lv,
                    "citation": citation, "ledger_line": row_no,
                    "source_file": src, "source_location": f"L{row_no}",
                    "value": value, "note": note,
                }
                return
            if RANK[lv] > RANK[e["link_level"]]:
                e["link_level"], e["confidence"] = lv, CONFIDENCE[lv]
            for field, text in (("value", value), ("note", note)):
                if text and text not in e[field].split("; "):
                    e[field] = f"{e[field]}; {text}" if e[field] else text

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
        edges += row_links.values()

        node = {
            "id": key, "label": f"{key} {row['Name'].strip()}", "file_type": "concept",
            "source_file": src, "source_location": f"L{row_no}",
            "tag": tag, "item_name": row["Name"].strip(), "ledger_line": row_no,
            "ledger_level": raw_level, "citation": citation,
            "lane": split_values(row["Lane"]), "bid_items": bids,
            "bid_item": row["Bid Item"].strip(),
        }
        node.update({attr: row[col].strip() for col, attr in ITEM_FIELDS.items()})
        node["unlinked"] = unlinked
        items.append(node)

    # Rule 9: rows sharing a Tag get one Unresolved "same_tag" link each to the first.
    for tag, lines in repeated.items():
        first = f"{tag} [L{lines[0]}]"
        for other in lines[1:]:
            edges.append({
                "source": first, "target": f"{tag} [L{other}]", "relation": "same_tag",
                "confidence": CONFIDENCE["Unresolved"], "ledger_level": "Unresolved",
                "link_level": "Unresolved",
                "citation": f"{src} lines {lines[0]} and {other} share Tag {tag}",
                "ledger_line": other, "source_file": src,
                "source_location": f"L{lines[0]}, L{other}", "value": tag, "note": "",
            })

    clash = sorted(item_ids & set(docs))
    problems += [f"node id {c!r} is both an item and a linked document" for c in clash]
    if problems:
        for msg in problems:
            print(f"ERROR {msg}", file=sys.stderr)
        return 2

    nodes = items + [{"id": nid, "label": label, "file_type": "document", "source_file": src}
                     for nid, label in docs.items()]
    graph = build_from_json({"nodes": nodes, "edges": edges}, directed=True)
    communities = cluster(graph)
    out = Path(args.out) / "graphify-out"
    out.mkdir(parents=True, exist_ok=True)
    to_json(graph, communities, str(out / "graph.json"), force=True)

    kinds: dict[str, int] = {}
    for nid in docs:
        kinds[nid.split(":", 1)[0]] = kinds.get(nid.split(":", 1)[0], 0) + 1
    relations: dict[str, int] = {}
    for e in edges:
        relations[e["relation"]] = relations.get(e["relation"], 0) + 1
    print(f"{len(rows)} Ledger rows -> {len(items)} item nodes; linked nodes {kinds}")
    print(f"links {relations}")
    print(f"{graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges, "
          f"{len(communities)} communities -> {out / 'graph.json'}")
    for tag, lines in repeated.items():
        print(f"NOTE Tag {tag!r} repeats on lines {lines}; keyed '<Tag> [L<line>]'")
    print(f"NOTE {sum(len(n['unlinked']) for n in items)} values made no link; "
          f"kept on their item node under 'unlinked'")
    for msg in unknown:
        print(f"WARNING unknown tag level, treated as Unresolved: {msg}")
    print(f"next: graphify cluster-only {args.out} --no-label")
    return 1 if unknown else 0


if __name__ == "__main__":
    sys.exit(main())
