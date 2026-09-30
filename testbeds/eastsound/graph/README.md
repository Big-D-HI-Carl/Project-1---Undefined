# graph/ — Ledger graph

The graph of the Project Ledger, built by script with no LLM calls. It is a map, not a source: answers cite the Wiki note, Ledger row or document page, never the graph.

- **Input:** `project/02_Project_Ledger/Project_Ledger.csv` (447 rows, read-only).
- **Script:** `tools/ledger_to_graph.py`, on graphifyy 0.9.72 (pinned in `requirements.txt`).
- **Outputs** in `graphify-out/`: `graph.json`, `GRAPH_REPORT.md`, `graph.html`. Don't commit `cache/` or `.graphify_*`; they are gitignored.
- **Size:** 791 nodes (447 Ledger items, 86 sheets, 77 spec sections, 21 Addendum 4 items, 160 Wiki notes) and 3,113 links.

## Rebuild

Run from the repo root, with the pinned packages installed in `.venv`. `env -i` clears every variable, so no LLM key or cloud setting can reach graphify, and the proxy is dropped too. `GIT_DIR=no-git` stops graphify from stamping the current commit into the outputs (ISSUES_LOG, "Graph build inside the repo stamps the git commit…"). The script pins PYTHONHASHSEED itself, and so does `graphify cluster-only`.

```
env -i PATH="$PWD/.venv/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 GIT_DIR=no-git \
  python testbeds/eastsound/tools/ledger_to_graph.py testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv --out testbeds/eastsound/graph
env -i PATH="$PWD/.venv/bin:/usr/bin:/bin" HOME="$HOME" LANG=C.UTF-8 GIT_DIR=no-git \
  graphify cluster-only testbeds/eastsound/graph --no-label
```

On Windows, use a fresh PowerShell window:
1. Remove every `*_API_KEY` variable, plus `AWS_PROFILE`, `AWS_REGION`, `AWS_DEFAULT_REGION`, `OLLAMA_HOST` and `OLLAMA_BASE_URL`.
2. Set `$env:GIT_DIR = "no-git"`.
3. Run the same two commands with `py -3` in place of `python`.

Two builds of the same Ledger give byte-identical `graph.json`, `graph.html` and `GRAPH_REPORT.md`. The report's first line carries the folder name and the date.

## What's in it

- **Item nodes:** one per Ledger row. The ID is the Tag. The label is "Tag Name".
  - Each item carries `ledger_line`, `ledger_level` (the tag as written), `citation` (Source Citation), `lane`, `bid_items`, `bid_item` (the raw cell), area, discipline, status and the two Y/N columns.
  - It also carries `unlinked`: values that made no link. There are 18 in all, for example "Drawing Sheets: Not shown".
- **Linked nodes and their links:**

  | Column | Node ID | Label | Link |
  |---|---|---|---|
  | Drawing Sheets | `sheet:C1.3` | Sheet C1.3 | `shown_on` |
  | Spec Sections | `spec:33 31 00` | Spec 33 31 00 | `specified_in` |
  | Addenda | `addendum:Add. 4 p.7` | Add. 4 p.7 | `changed_by` |
  | Wiki Note(s) | `note:C1.3` | Wiki note C1.3 | `described_in` |

- **Lane and Bid Item** are item attributes, not nodes, so they don't act as hubs that link everything in two steps (Carl, 2026-09-30).
- **Every link carries:**
  - `ledger_level`: the row's tag as written;
  - `link_level` and `confidence`;
  - `citation`, `ledger_line` and `source_location` (`L<line>`);
  - `value`: the cell text it came from;
  - `note`: its location note, such as "Det. 2" or "KN 3, 5".
- **Tag mapping:** Verified and Verified-Visual → EXTRACTED; Inferred → INFERRED; Unresolved → AMBIGUOUS.

## Parsing rules (approved in Prompt 3, 2026-09-30)

1. Split on `;` outside parentheses. Addenda and Bid Item also split on `|`.
2. Blanks, `—`, "Not stated", "Not shown", "None (…)" and any value that doesn't parse make no link. The text stays on the item under `unlinked`.
3. **Sheets:** the ID is the leading sheet number, uppercased. C7.1 and C7.10 stay separate. The rest of the value becomes the link's note.
4. **Specs:** `NN NN NN`, or `Appendix X` as written. Text in parentheses becomes the note.
5. **Addenda:**
   - A value without "Add. N" takes the number from the value before it in the cell.
   - Page forms: "p.N", "p.N and p.M", and "pp.N–M" (expanded to single pages).
   - The node is "Add. 4 p.N". It is "Add. 4 p.1 Clarification N" or "Add. 4 p.2 <spec> ¶<para>" when the value names that item.
   - A value with no page, such as "drawing already shows W400", becomes a note on the link just before it.
6. **Bid items (attribute):** remove text in parentheses, a leading "Unresolved —", and any lead-in text before a colon. What's left is `N`, `N or M`, or `Equipment Alternate X`.
7. **Link level:** each link takes the weaker of the row's tag and any tag level written in that value.
8. **One link per item and target:** repeats merge their values and notes and keep the weakest level.
9. **Repeated Tags:** each row is keyed `<Tag> [L<line>]`. Today that covers SD-1 (lines 74 and 316) and PROPOSED-Influent-Sampler (lines 321 and 419).
   - PROPOSED-Influent-Sampler is one item entered by two lanes, so one `same_tag` link (AMBIGUOUS) joins its rows.
   - The two SD-1 rows are different items (storm drain, sludge pump), so they get no link (Carl, 2026-09-30). A link made false path traces between them. The script's `NO_SAME_TAG` list holds this exception.
   - **When Prompt 9 adds the permanent Ledger ID column, the item key switches from the Tag to that ID, and `NO_SAME_TAG` goes.**
10. **Labels:** "Sheet …", "Spec …", "Wiki note …", "Add. 4 …". IDs keep the `sheet:`, `spec:`, `addendum:` and `note:` prefixes.

## Querying

```
graphify explain "PROPOSED-Blower-Pad" --graph testbeds/eastsound/graph/graphify-out/graph.json
graphify explain "Sheet C1.3" --graph testbeds/eastsound/graph/graphify-out/graph.json
graphify path "Add. 4 p.8" "PROPOSED-Blower-Pad" --undirected --graph testbeds/eastsound/graph/graphify-out/graph.json
```

- **Look up a sheet, spec, note or addendum by its full label or ID.** "Sheet C1.3" and `sheet:C1.3` work. A bare "C1.3" matches several nodes, and graphify picks one without warning.
- **Look up a repeated Tag by its key,** for example `SD-1 [L316]`.
- **`explain` lists at most 20 connections.** The full set is in graph.json.
- **Item-to-item paths need `--undirected`.**
- **Treat hub-based paths with care.** Add. 4 p.3 (the drawing-changes page, 43 items) can make short paths that don't reflect how the work connects.
