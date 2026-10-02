# derived/graph — Project Wiki graph built from the Ledger

Build date: 2026-10-02. Owner: Graph lane. Built by `build/build_graph.py` with no LLM calls; the library PDFs are not read. The graph is a map, not a source: cite the Ledger row, the Wiki note or the document page, never the graph.

**Superseded:** the 2026-09-30 extraction graph in `testbeds/eastsound/graph/graphify-out/` (1,386 nodes, 7,284 edges, 85 communities) and its 2026-10-01 rebuild (1,636 nodes) are superseded by this build. They stay in place, unchanged, as history.

## Files

| File | What it holds |
|---|---|
| `Project_Graph.html` | The viewer. One self-contained file with D3 7.9.0 inlined; open it in a browser with the network off. Color = lane, shape = node type, size = edge count, dashed outline = Unresolved. |
| `nodes.csv` | One row per node (columns in the order below) |
| `edges.csv` | One row per edge: From, To, Edge Type, Label, Source Citation, Confidence |
| `Findings.md` | Every Ledger gap the build hit, logged and not fixed |
| `vault/` | One Markdown note per node, named by its Label, with [[wikilinks]] to every neighbour (opens as an Obsidian vault) |
| `graph.json` | The same graph in the field names of `graph/graphify-out/graph.json` |
| `Spot_Check.csv` | 20 nodes picked with seed 20261002, in `index/Spot_Check_Schema.csv` columns; Human Result is blank for a person to fill. Only a person marks Verified-Visual. |
| `Test_Report.md` | Results of `build/test_graph.py` |
| `build/` | `build_graph.py`, `viewer_template.py`, `test_graph.py` |

## Counts

| Node type | Count |
|---|---|
| Component | 447 |
| Sheet | 97 |
| Spec section | 77 |
| Spec paragraph | 280 |
| Addendum item | 15 |
| Bid item | 24 |
| Area/Building | 32 |
| **Total** | **972** |

| Edge type | Count |
|---|---|
| shown on | 986 |
| specified by | 1252 |
| modified by | 114 |
| paid under | 571 |
| located in | 437 |
| described by | 15 |
| related to | 491 |
| part of | 280 |
| **Total** | **4146** |

Findings: 17 kinds, 329 rows (`Findings.md`).

## Edge map

| Ledger column or source | Edge | From → To | Label |
|---|---|---|---|
| `Drawing Sheets` | shown on | Component → Sheet | the anchor in brackets (KN 16, Det. 3, Add. 4 p.7) |
| `Spec Sections` | specified by | Component → Spec section | the anchor in brackets, if any |
| `Source Citation` (¶ cites) | specified by | Component → Spec paragraph | the main spec page cited, if any |
| `Addenda` | modified by | Component → Addendum item | the Ledger text, less "— Add. 4 governs" |
| `Bid Item` | paid under | Component → Bid item | the Ledger text |
| `Area/Building` | located in | Component → Area/Building | the Ledger text, when it adds to the area name |
| `Wiki Note(s)` | described by | Component → Sheet, Spec section or Addendum item | only where no shown-on, specified-by or modified-by edge joins the pair; otherwise that edge's Label ends "also in Wiki note" (decision 2A) |
| Wiki note Related documents (`derived/wiki/Wiki_Links.csv`) | related to | Sheet → Sheet or Spec section | "listed in both notes" when each note lists the other |
| Paragraph number | part of | Spec paragraph → Spec section | — |

- One edge per citation. A pair cited twice keeps one edge and its Label starts "N citations".
- Every edge carries the Confidence of the Ledger row it came from, made weaker by any tag word in the cell (e.g. "1 (Inferred per 04)"). Related-to edges carry the Wiki link's Confidence, the stronger of the two notes when both list each other.
- Never invented: a value that doesn't match 01–04 or the Wiki makes no edge and goes to Findings.
- Not yet: "I/O point" edges (E7.4 → BL-1, OUT 0) come in a later pass from the OCR lane's Tag_Hits.

## Node rules

| Node type | One per | ID | Label | Open Link |
|---|---|---|---|---|
| Component | Ledger row (447) | Ledger ID + Tag, e.g. `L-0256 BL-1` (permanent IDs from `derived/reconciliation/Ledger_ID_Map.csv`) | Tag · name; untagged PROPOSED rows: name · first sheet (no tag) | the first cited sheet, else the first cited spec section |
| Sheet | 01 rev2 row (96 + C1.6A) | `Sheet E7.4` | sheet · Wiki note title | native part and page from `library/Plan_Set_Parts.md`; C1.6A: Add. 4 p.8. Add. 4 reissues also carry the reissue page |
| Spec section | 02 section the Ledger cites | `Spec 26 80 00` | section · 02 title (the body governs, so 26 80 00 reads Control System) | main spec start page from 02 |
| Spec paragraph | ¶ cited in a Ledger Source Citation | `Spec 26 80 00 ¶3.09 C` | section ¶paragraph · title | the cited main spec page, else the section start |
| Addendum item | 03 Addendum 4 item-map row | `Add. 4 Clarification 4` | Add. 4 · item as written in 03 | Add. 4 page from 03 |
| Bid item | 04 bid item or equipment alternate | `Bid Item 6` | Bid Item 6 · description | bid form page in the main spec |
| Area/Building | name in the Ledger column | `Area Blower Building` | the name | — |

Open Links are relative to this folder (`../../library/<file>#page=N`), so they work from any clone.

## Decisions recorded (Carl, 2026-10-02, Step 0)

Carl answered "OK, all A (Recommended)" to the five Step 0 options:

1. A — build from `Project_Ledger.csv` (447 rows), keyed on the permanent Ledger ID.
2. A — draw a described-by edge only where it adds a link; elsewhere mark the existing edge "also in Wiki note".
3. A — paragraph nodes from the Ledger Source Citation, joined to their section by part of.
4. A — also append PROGRESS_LOG.md and ISSUES_LOG.md entries; the build script lives in `build/`.
5. A — sheet Status from 01 rev2.

## Rebuild

From the repo root, with any Python 3.10+ (standard library only):

```
python testbeds/eastsound/derived/graph/build/build_graph.py
python testbeds/eastsound/derived/graph/build/test_graph.py
```

On Windows use `py -3`. The build sets PYTHONHASHSEED=0 itself. Two builds of the same inputs give byte-identical files. D3 comes from the npm tarball (sha512 pinned) or, offline, from the D3 block of the existing `Project_Graph.html` (sha256 pinned). D3 is © 2010-2023 Mike Bostock, ISC licence (the licence text is in the viewer).

Spot check picks (seed 20261002): L-0094 PROPOSED-Concrete walkway, Spec 10 73 05 ¶2.01 A, L-0074 PROPOSED-4in roof drain at SD-1, Spec 43 22 10, Spec 46 53 00 ¶2.01 C.6, Sheet C6.3, L-0309 PROPOSED-Effluent-Flow-Meter-Transmitter-Panel, L-0345 PROPOSED-UV-Power-Distribution-1, Spec 22 13 29 ¶2.03, L-0291 F1 (Influent Pump Station), Spec 46 53 00 ¶2.01 B.2, L-0025 PROPOSED-Existing 8in influent pipe, Spec 03 40 00 ¶2.02 D.1, Spec 46 41 23 ¶1.02 A, L-0440 PROPOSED-Aeration-Basins, L-0254 PROPOSED-Existing-208V-400A-Distribution-Panel, L-0208 PROPOSED-AERATION-AIR-HEADER, L-0418 PROPOSED-Influent-Sampler, Spec 00 41 00, Spec 26 05 26 ¶2.01 D.

## Inputs

| File | SHA-256 (first 16) |
|---|---|
| `testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv` | d9378c46ec558ce0 |
| `testbeds/eastsound/index/Ledger_Schema.csv` | e46171e56c435362 |
| `testbeds/eastsound/derived/reconciliation/Ledger_ID_Map.csv` | 1e6f2d57dab919b9 |
| `testbeds/eastsound/index/01_Sheet_Index_rev2.md` | c12e784831864847 |
| `testbeds/eastsound/index/01_Sheet_Index_rev1.md` | b0cdcb00a4b0085c |
| `testbeds/eastsound/index/02_Spec_Index_rev1.md` | 56d221653bcb9e1e |
| `testbeds/eastsound/index/03_Coverage_Gate_rev1.md` | b1d633cc61242930 |
| `testbeds/eastsound/index/04_Bid_Item_Spine.md` | a49e6ed6fea67f08 |
| `testbeds/eastsound/index/Spot_Check_Schema.csv` | d99c37a77b51473c |
| `testbeds/eastsound/library/Plan_Set_Parts.md` | 853c1c0b07738812 |
| `testbeds/eastsound/project/01_Project_Wiki/Project_Wiki.md` | a3027eed7aadeee5 |
| `testbeds/eastsound/derived/wiki/Wiki_Notes.csv` | ba6e3559428c5a42 |
| `testbeds/eastsound/derived/wiki/Wiki_Links.csv` | 5601d7ba85517daa |
| `testbeds/eastsound/tools/parse_wiki.py` | f4e5d0978575a784 |
