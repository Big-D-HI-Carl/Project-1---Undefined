#!/usr/bin/env python3
"""Build a knowledge graph from a Project Ledger CSV. No LLM calls.

Output is graphify-compatible: query it with `graphify explain` and
`graphify path --undirected` (pass --graph <out>/graphify-out/graph.json),
and render the report and viewer with `graphify cluster-only <out> --no-label`.

Seed version. Tested on graphifyy 0.9.72 / Python 3.12 with a synthetic
fixture using the real 16-column Ledger header. Extend per Prompt 3.

Usage: python tools/ledger_to_graph.py <ledger.csv> --out <folder>
"""
import argparse
import csv
import sys
from pathlib import Path

from graphify.build import build_from_json
from graphify.cluster import cluster
from graphify.export import to_json

TAG_COL = "Verified/Verified-Visual/Inferred/Unresolved"
LEVELS = ("Verified-Visual", "Verified", "Inferred", "Unresolved")  # longest match first
# Ledger tag level -> graphify confidence. The original level rides on every edge.
CONFIDENCE = {"Verified-Visual": "EXTRACTED", "Verified": "EXTRACTED",
              "Inferred": "INFERRED", "Unresolved": "AMBIGUOUS"}
# Ledger column -> (node id prefix, edge relation)
LINKS = {
    "Drawing Sheets": ("sheet", "shown_on"),
    "Spec Sections": ("spec", "specified_in"),
    "Addenda": ("addendum", "changed_by"),
    "Bid Item": ("bid", "paid_under"),
    "Lane": ("lane", "crawled_in"),
    "Wiki Note(s)": ("note", "described_in"),
}
SEPARATOR = ";"  # confirm against the real Ledger before changing (Prompt 3, step 2)


def level_of(raw: str) -> str | None:
    """Leading tag word: 'Unresolved: external reference, not staged' -> 'Unresolved'."""
    raw = raw.strip()
    return next((lv for lv in LEVELS if raw.startswith(lv)), None)


def main() -> int:
    ap = argparse.ArgumentParser(description="Ledger CSV -> graphify graph.json (no LLM)")
    ap.add_argument("ledger", help="path to a Ledger CSV")
    ap.add_argument("--out", required=True, help="folder; graph.json goes to <out>/graphify-out/")
    args = ap.parse_args()

    src = Path(args.ledger).as_posix()
    nodes, edges, seen, unknown = [], [], set(), []

    def add_node(nid: str, label: str, kind: str) -> None:
        if nid not in seen:
            seen.add(nid)
            nodes.append({"id": nid, "label": label, "file_type": kind, "source_file": src})

    with open(args.ledger, encoding="utf-8-sig", newline="") as f:
        for row_no, row in enumerate(csv.DictReader(f), start=2):  # line 1 is the header
            tag = row["Tag"].strip()
            raw_level = row[TAG_COL].strip()
            level = level_of(raw_level)
            if level is None:  # never guess: weakest confidence, and report it
                unknown.append(f"line {row_no}: {tag!r} has tag level {raw_level!r}")
                level = "Unresolved"
            add_node(tag, f"{tag} {row['Name'].strip()}", "concept")
            for col, (prefix, relation) in LINKS.items():
                for value in (v.strip() for v in row.get(col, "").split(SEPARATOR)):
                    if not value:
                        continue
                    nid = f"{prefix}:{value}"
                    add_node(nid, f"Bid Item {value}" if prefix == "bid" else value, "document")
                    edges.append({
                        "source": tag, "target": nid, "relation": relation,
                        "confidence": CONFIDENCE[level], "ledger_level": raw_level,
                        "citation": row["Source Citation"].strip(),
                        "ledger_line": row_no, "source_file": src,
                    })

    graph = build_from_json({"nodes": nodes, "edges": edges}, directed=True)
    communities = cluster(graph)
    out = Path(args.out) / "graphify-out"
    out.mkdir(parents=True, exist_ok=True)
    to_json(graph, communities, str(out / "graph.json"), force=True)

    print(f"{graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges, "
          f"{len(communities)} communities -> {out / 'graph.json'}")
    for msg in unknown:
        print(f"WARNING unknown tag level, treated as Unresolved: {msg}")
    print(f"next: graphify cluster-only {args.out} --no-label")
    return 1 if unknown else 0


if __name__ == "__main__":
    sys.exit(main())
