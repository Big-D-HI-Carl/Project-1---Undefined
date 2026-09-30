# graph/ — Ledger graph

The graph of the Project Ledger and the files derived from it, built by script with no LLM calls. It is a map, not a source: answers cite the Wiki note, Ledger row or document page, never the graph.

- **Inputs** (read-only; `Build_Inputs.csv` gives each one's path, status, row count and SHA-256 for the committed build):
  - `project/02_Project_Ledger/Project_Ledger.csv` (447 rows).
  - `derived/reconciliation/Ledger_ID_Map.csv` (447 Ledger IDs). Required.
  - `derived/wiki/Wiki_Notes.csv` and `derived/wiki/Wiki_Links.csv`.
  - `project/01_Project_Wiki/Project_Wiki.md`, for each note's text (`wiki_text` in `Build_Inputs.csv`).
  - `derived/reconciliation/Starter_MTO.csv`.
  - `derived/issues/Open_Items.csv`.
  - A derived input that is missing, or lacks a needed column, is skipped and marked in `Build_Inputs.csv`. Nothing is guessed in its place.
- **Script:** `tools/ledger_to_graph.py`, on graphifyy 0.9.72 (pinned in `requirements.txt`).
- **Outputs:** `graphify-out/graph.json`, `GRAPH_REPORT.md` and `graph.html`, plus `Build_Inputs.csv` and `Build_Counts.csv` here. Don't commit `cache/` or `.graphify_*`; they are gitignored.
- **Size:** 1,385 nodes and 7,678 links in the committed build (`Build_Counts.csv`).

  | Node type | Count | | Link | Count |
  |---|---|---|---|---|
  | item | 447 | | `shown_on` | 986 |
  | sheet | 99 | | `specified_in` | 536 |
  | spec | 117 | | `changed_by` | 153 |
  | addendum | 23 | | `described_in` | 1,437 |
  | note | 203 | | `describes` | 200 |
  | mto | 22 | | `mentions` | 523 |
  | open_item | 474 | | `references` | 1,480 |
  | | | | `quantity_of` | 21 |
  | | | | `measured_on` | 22 |
  | | | | `concerns` | 790 |
  | | | | `cites` | 1,530 |

- **Merge order:** the committed build used `derived/wiki/` from commit 331c923 (branch `claude/magical-euler-lnev7r`) and `derived/issues/Open_Items.csv` from commit ddb818e (branch `claude/jolly-rubin-dm4ese`). Those files reach main with their own PRs. Merge them first. If either file changes before it merges, rebuild and check the SHA-256 values in `Build_Inputs.csv`.

## Rebuild

Run from the repo root, with the pinned packages installed in `.venv`. `env -i` clears every variable, so no LLM key or cloud setting can reach graphify, and the proxy is dropped too. `GIT_DIR=no-git` stops graphify from stamping the current commit into the outputs (ISSUES_LOG, "Graph build inside the repo stamps the git commit…"). The script pins PYTHONHASHSEED itself, and so does `graphify cluster-only`.

```
env -i PATH="$PWD/.venv/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 GIT_DIR=no-git \
  python testbeds/eastsound/tools/ledger_to_graph.py testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv --out testbeds/eastsound/graph
env -i PATH="$PWD/.venv/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 GIT_DIR=no-git \
  graphify cluster-only testbeds/eastsound/graph --no-label
```

- The derived inputs default to the paths above. `--id-map`, `--wiki-notes`, `--wiki-links`, `--mto` and `--open-items` point at other files.
- On Windows, use a fresh PowerShell window:
  1. Remove every `*_API_KEY` variable, plus `AWS_PROFILE`, `AWS_REGION`, `AWS_DEFAULT_REGION`, `OLLAMA_HOST` and `OLLAMA_BASE_URL`.
  2. Set `$env:GIT_DIR = "no-git"`.
  3. Run the same two commands with `py -3` in place of `python`.

Two builds of the same inputs give byte-identical `graph.json`, `graph.html`, `GRAPH_REPORT.md`, `Build_Inputs.csv` and `Build_Counts.csv`. The report's first line carries the folder name and the date.

## What's in it

| Node type | ID | Label | From |
|---|---|---|---|
| item | `L-0242` (Ledger ID) | the Tag, e.g. `GEN` | one per Ledger row |
| sheet | `sheet:E6.1` | Sheet E6.1 | Ledger, Wiki, MTO, open items |
| spec | `spec:26 32 13` | Spec 26 32 13 | Ledger, Wiki, open items |
| addendum | `addendum:Add. 4 p.7` | Add. 4 p.7 | Ledger, Wiki |
| note | `note:26 32 13` | Wiki note 26 32 13 | Ledger Wiki Note(s), Wiki_Notes.csv |
| mto | `mto:13` | MTO line 13: 3 EA | Starter_MTO.csv |
| open_item | `open:OI-0001` | Item ID and the title's lead clause, e.g. `OI-0001 Generator rating RFI` | Open_Items.csv |

Every node carries `node_type`. `unlinked` on a node lists the values that made no link.

- **Items** carry `ledger_id`, `tag`, `item_name`, `ledger_line`, `ledger_level` (the tag as written), `citation` (Source Citation), `lane`, `bid_items`, `bid_item` (the raw cell), area, discipline, status and the two Y/N columns.
- **Notes** carry the Wiki_Notes.csv columns `title`, `lane`, `note_type`, `discipline`, `revision_date`, `where_it_lives` and `heading_line`. They also carry:
  - `note_text`: the note's body from Project_Wiki.md (rule 11);
  - `note_text_chars`: the full body's length;
  - `note_text_cut`: Y when the text was cut;
  - `note_text_source`: the file and heading line.
  - `wiki_note_found` is false for a Ledger note name with no Wiki note (CQA Plan).
- **MTO lines** carry every Starter_MTO.csv column (quantity, unit, sheet, set page, box, keyed note, method, confidence, ready, citation, bid item, tie basis).
- **Open items** carry every Open_Items.csv column; `open_type` is its Type, and `title` is the full title. They also carry:
  - `ledger_id_list`: the Ledger IDs the item names;
  - `item_links`: "linked", or "none: duplicate item" or "none: N Ledger IDs (over 15)" (rule 14).
  - 56 open items name no Ledger ID, sheet or spec, so they have no links.
- **Lane and Bid Item** are item attributes, not nodes, so they don't act as hubs that link everything in two steps (Carl, 2026-09-30).

| Link | From → to | Source |
|---|---|---|
| `shown_on` | item → sheet | Ledger Drawing Sheets |
| `specified_in` | item → spec | Ledger Spec Sections |
| `changed_by` | item → addendum | Ledger Addenda |
| `described_in` | item → note | Ledger Wiki Note(s) |
| `describes` | note → its own sheet or spec | Wiki_Notes.csv Note ID |
| `mentions` | note → item | Wiki_Links.csv, equipment tag |
| `references` | note → sheet, spec, addendum or note | Wiki_Links.csv |
| `quantity_of` | MTO line → item | Starter_MTO.csv Ledger ID |
| `measured_on` | MTO line → sheet | Starter_MTO.csv Sheet |
| `concerns` | open item → item | Open_Items.csv Ledger IDs (not for duplicate items or over 15 IDs) |
| `cites` | open item → sheet or spec | Open_Items.csv Sheets, Spec Sections |

- **Every link carries** `link_level` and `confidence`, `citation`, `source_file` and `source_location` (`L<line>` in that file), and `value` (the text it came from).
  - Ledger links also carry `ledger_level` (the row's tag as written), `ledger_line` and `note` (a location note such as "Det. 2" or "KN 3, 5").
  - Links to an item carry that item's `ledger_line`.
  - Wiki links carry `wiki_source` (tag line, related documents or body text), `wiki_confidence`, `wiki_line` (the Project Wiki line), `written_as` and `basis`, as written in Wiki_Links.csv. Their citation names the note, the source and the Project Wiki line.
- **Tag mapping:** Verified and Verified-Visual → EXTRACTED; Inferred → INFERRED; Unresolved → AMBIGUOUS.

## Parsing rules

Rules 1–10 were approved in Prompt 3 (2026-09-30). Rule 9 changed when the Ledger ID landed. Rules 11–14 cover the derived inputs.

1. Split on `;` outside parentheses. Addenda and Bid Item also split on `|`.
2. Blanks, `—`, "Not stated", "Not shown", "None (…)" and any value that doesn't parse make no link. The text stays on the node under `unlinked`.
3. **Sheets:** the ID is the leading sheet number, uppercased. C7.1 and C7.10 stay separate. The rest of the value becomes the link's note.
4. **Specs:** `NN NN NN`, or `Appendix X` as written. Text in parentheses becomes the note.
5. **Addenda:**
   - A value without "Add. N" takes the number from the value before it in the cell.
   - Page forms: "p.N", "p.N and p.M", and "pp.N–M" (expanded to single pages).
   - The node is "Add. 4 p.N". It is "Add. 4 p.1 Clarification N" or "Add. 4 p.2 <spec> ¶<para>" when the value names that item.
   - A value with no page, such as "drawing already shows W400", becomes a note on the link just before it.
6. **Bid items (attribute):** remove text in parentheses, a leading "Unresolved —", and any lead-in text before a colon. What's left is `N`, `N or M`, or `Equipment Alternate X`.
7. **Link level:** each link takes the weaker of its source's tag and any tag level written in that value.
8. **One link per source and target.** Ledger, MTO and open-item repeats merge their values and notes and keep the weakest level.
9. **Item key = Ledger ID** (DECISIONS.md 2026-09-30, "Every Ledger row gets a permanent Ledger ID; everything links by ID").
   - The script checks every Ledger row against Ledger_ID_Map.csv (Ledger Row and Tag) and stops if the map is stale.
   - The label is the Tag. A Tag on two rows is labeled `<Tag> [<Ledger ID>]`, because graphify merges nodes that share a label and a source file. Today that covers SD-1 (L-0073 storm drain, L-0315 sludge pump) and PROPOSED-Influent-Sampler (L-0320, L-0418).
   - No link joins rows that share a Tag. `NO_SAME_TAG` and the `same_tag` link are gone. The Influent-Sampler pair is a duplicate for Merge (ISSUES_LOG, "Project_Ledger.csv repeats two Tags"); it shows in the graph only if an open item names both IDs.
10. **Labels:** "Sheet …", "Spec …", "Wiki note …", "Add. 4 …", "MTO line …". IDs keep the `sheet:`, `spec:`, `addendum:`, `note:`, `mto:` and `open:` prefixes.
11. **Wiki notes:**
    - The Note ID is the note node's ID after `note:`, so a Wiki note and the Ledger's Wiki Note(s) value meet on one node.
    - A Note ID that parses as a sheet, spec or appendix gets one `describes` link to that node (Verified: the note's heading names its unit). "Add. 4 Generator Exhibit" and "QA plan" get none.
    - **Note text** (Carl, 2026-09-30):
      - The body runs from the line after the note's heading (Wiki_Notes.csv Heading Line) to the next level 1–3 heading. The script checks that the line is `### <Note ID> — `.
      - The "> Merge:" line is left out. The Project Wiki calls it Merge metadata, not note content. The rest is kept as written, with markdown tables and lists as they are.
      - Text over 2,000 characters is cut after the last full sentence that ends within 2,000 characters.
      - A sentence ends at `.`, `!` or `?` (plus any closing bracket or quote) before a line break, or before a space and a capital letter, bracket, quote or list or table mark.
      - Abbreviations such as "Add.", "Det.", "No.", "Sch.", "p." and "e.g." are not ends.
      - With no sentence end in range, the text would be cut at the last space and marked "…". No note needs this today.
12. **Wiki links:**
    - The level is the Confidence column (tag line and Related documents Verified, body text Inferred).
    - An equipment tag links to the Ledger ID in the file's Ledger ID column. If that is blank, an exact Tag match gives the ID, and the link is Inferred. If the Tag is on two rows, the link goes to the one row whose Wiki Note(s) cites this note, and is Inferred; otherwise it makes no link.
    - Sheets, specs and addenda parse by rules 3–5. "Add. N Clarification M" with no page links only when the Ledger graph has exactly one node for that clarification.
    - These make no link and stay on the note under `unlinked`: an equipment name with no Ledger ID (858 rows, e.g. "temporary bypass pumping"); a whole-addendum cite with no page ("Add. 4", "Add. 3") and "Add. 4 p.0" (67); a 5-digit legacy spec number such as "09900" (8); and "Appendix A", which has no Wiki note (2).
    - A note target links only to a Wiki note or a Ledger Wiki Note(s) name.
    - One link per note and target. When two sources give the same link, it keeps the stronger level and lists both sources in `wiki_source`, because each source supports it on its own.
13. **MTO lines:** each Ledger ID in the cell gets a `quantity_of` link and the sheet a `measured_on` link, both at the line's Confidence. A blank Ledger ID (the C0.2 earthwork lines) makes no item link. Its Tie Basis stays on the node.
14. **Open items:** Ledger IDs are read as `L-NNNN`. Sheets and Spec Sections split on `;` and `,` outside parentheses and parse by rules 3–4. The level is the item's Confidence.
    - Duplicate-type items, and items naming more than 15 Ledger IDs, keep their node and their sheet and spec links. They get no `concerns` links; their IDs are listed in `ledger_id_list` (Carl, 2026-09-30). This stops them joining the rows they compare, and stops the largest items acting as hubs.
    - Other open items keep their `concerns` links.

## Querying

```
graphify explain "GEN" --graph testbeds/eastsound/graph/graphify-out/graph.json
graphify explain "L-0242" --graph testbeds/eastsound/graph/graphify-out/graph.json
graphify explain "Sheet C1.3" --graph testbeds/eastsound/graph/graphify-out/graph.json
graphify path "Add. 4 p.8" "PROPOSED-Blower-Pad" --undirected --graph testbeds/eastsound/graph/graphify-out/graph.json
```

- **Look up an item by its Ledger ID or its Tag.** A Tag on two rows needs its label, for example `SD-1 [L-0315]`, or its ID.
- **Look up a sheet, spec, note, addendum, MTO line or open item by its full label or ID.** "Sheet C1.3" and `sheet:C1.3` work. A bare "C1.3" matches several nodes, and graphify picks one without warning.
- **`explain` lists at most 20 connections.** The full set is in graph.json.
- **Item-to-item paths need `--undirected`.**
- **Treat hub-based paths with care.** Add. 4 p.3 (the drawing-changes page, 43 items) can make short paths that don't reflect how the work connects.
- **Open items still link the rows they name.** Rule 14 takes duplicate items and the largest items out. The largest linked item is now OI-0319 (13 items).
  - One short SD-1 path remains. `graphify path "SD-1 [L-0073]" "SD-1 [L-0315]" --undirected` runs storm drain ← OI-0289 (Cross-lane, a conflict item) → sludge pump in two INFERRED hops.
  - OI-0289 concerns Electrical & Controls process equipment on E4.1, E4.2 and E6.1. Its L-0073 (the C2.2 storm drain) looks like a Tag match to the wrong SD-1 row (ISSUES_LOG, "Open item OI-0289 names the storm drain SD-1 row").
  - Without open items, the shortest SD-1 path is 4 hops: storm drain — Wiki note 33 41 00 — Add. 4 p.2 — Wiki note E4.1 — sludge pump.

## Example trace: generator → RFI → spec 26 32 13 → sheets

```
graphify explain "OI-0001" --graph testbeds/eastsound/graph/graphify-out/graph.json
graphify path "OI-0001 Generator rating RFI" "Sheet E10.3" --undirected --graph testbeds/eastsound/graph/graphify-out/graph.json
```

| Step | Link | Level | From |
|---|---|---|---|
| GEN (L-0242) ← OI-0001 Generator rating RFI | `concerns` | EXTRACTED (Verified) | Open_Items.csv L2 |
| OI-0001 → Spec 26 32 13 | `cites` | EXTRACTED (Verified) | Open_Items.csv L2 |
| OI-0001 → Sheet E1.1, Sheet E6.1 | `cites` | EXTRACTED (Verified) | Open_Items.csv L2 |
| Spec 26 32 13 ← Wiki note 26 32 13 | `describes` | EXTRACTED (Verified) | Wiki_Notes.csv L164 |
| Wiki note 26 32 13 → Sheet E1.1, E6.1, E10.3 | `references` | EXTRACTED (Verified) | Wiki_Links.csv L3445–L3464 |
| GEN → Spec 26 32 13 | `specified_in` | AMBIGUOUS (row Unresolved) | Project_Ledger.csv L243 |
| GEN → Sheet E1.1, E6.1, E6.3, E7.3, E10.3 | `shown_on` | AMBIGUOUS (row Unresolved) | Project_Ledger.csv L243 |

- The RFI is the one question on this chain: E1.1 and E6.1 show 125 kW / 156 kVA, and 26 32 13 ¶2.03 C.1 (main spec p.326) requires not less than 150.0 kW (OI-0001, from `derived/reconciliation/Summary.md`). The graph only points to those sources. Cite them, not the graph.
- The generator carries three more open items: OI-0325 (permanent generator bid item), OI-0172 (the same item on L-0242, L-0387 and L-0423) and OI-0063 (tag not read on E7.3 and E10.3).
