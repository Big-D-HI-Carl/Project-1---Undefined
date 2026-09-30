# Prompt 3 — Build the Ledger graph

Run from the repo root with /plan in front.

Goal: a graph of the Project Ledger that rebuilds identically in any runtime, with zero LLM calls, queryable with graphify's CLI. The seed `tools/ledger_to_graph.py` was tested on graphifyy 0.9.72 against a synthetic fixture: 19 nodes, 18 links, two builds byte-identical.

## 1. Environment
Create `.venv` and install `requirements.txt`. Run every graph command with no LLM keys in the environment (ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, GOOGLE_API_KEY unset).

## 2. Read the input before changing the script
From `testbeds/eastsound/project/Project_Ledger.csv` (read-only), report for each link column (Drawing Sheets, Spec Sections, Addenda, Bid Item, Lane, Wiki Note(s)): the separator actually used between values, 5 sample values, and odd formats (ranges like C1.3–C1.5, "Not stated", blanks, notes inside the cell). Propose parsing and ID-normalization rules from that evidence ("Add. 4" vs "Addendum 4", spacing in spec numbers) and wait for my OK. The seed splits on ";" only.

## 3. Extend the seed
Keep its tag mapping and link attributes (original tag level, Source Citation, Ledger line). Add the approved parsing and normalization rules. Every Ledger row must become a node, including rows with no links. Then:
- `python tools/ledger_to_graph.py testbeds/eastsound/project/Project_Ledger.csv --out testbeds/eastsound`
- `graphify cluster-only testbeds/eastsound --no-label` (writes GRAPH_REPORT.md and graph.html beside graph.json)
- create `testbeds/eastsound/.graphifyignore` containing `library/`

## 4. Acceptance tests — table: test | expected | actual
1. Every Ledger Tag is a node; node count ≥ row count
2. Every link carries a citation and the original tag level
3. Tag-level counts in the graph match the Ledger
4. Five spot checks across five lanes: `graphify explain "<tag>" --graph testbeds/eastsound/graphify-out/graph.json` beside the Ledger row; links must match the row exactly
5. One cross-lane trace: an Add. 4 item to a tag in another lane with `graphify path "<A>" "<B>" --undirected --graph <same path>`; show the hops and tags
6. Determinism: two clean builds give byte-identical graph.json and graph.html; GRAPH_REPORT.md may differ only in its first line (folder name and date)
7. No LLM calls: builds succeed with all keys unset
8. Library excluded: on a temp copy of `testbeds/eastsound` (without graphify-out/), with all keys unset, run `graphify extract <copy>`. It stops at the key check; its "found ..." line must show 0 papers and 0 images. Never run this with a key set: it would start a paid LLM extraction.

Any failure: append the failure mode and fix to ISSUES_LOG.md before rerunning.

## 5. Record
Commit the script, `.graphifyignore`, graph.json, GRAPH_REPORT.md and graph.html (not cache/ or .graphify_* files). Run prompts/close_session.md.
