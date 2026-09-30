# AGENTS.md

Canonical instructions for every coding agent in this repo (Claude Code, Codex, others). CLAUDE.md imports this file. Change rules here, not in CLAUDE.md.

## What this repo is
- Progress log and working files for the Heavy Industrial AI Implementation Program.
- First workstream: the Eastsound test bed in `testbeds/eastsound/`, built on the public bid set for the Eastsound Sewer and Water District WWTP Upgrade Phase I plus addenda. It proves the Project Wiki + Project Ledger architecture before any company data is connected.
- Governing plans, both in `testbeds/eastsound/process/`: `Sample_Project_Concurrent_Lane_Ultraplan_rev1.md` (master) and `Graph_Transfer_Ultraplan.md` (transfer, graph build, first proof run).

## Hard rules
Rules marked (checked) are enforced by `tools/checks.py` in the pre-commit hook and in CI, once Prompt 1 has added them. The rest depend on you.

1. **Data (checked where possible).** Public-source material only, plus notes about work done in this repo. No Big-D, client or employee data; no internal names, budgets or schedules; no credentials or keys. This holds until Big-D approves this host. If unsure whether something qualifies, stop and ask.
2. **Sources are read-only (checked).** Never rename, move, edit or delete a source file under any `library/` folder. A person adds source files. Notes go beside their source as `.md` files; agents may add and edit those notes, and nothing else, inside `library/`.
3. **Logs are append-only (checked).** `PROGRESS_LOG.md`, `DECISIONS.md`, `ISSUES_LOG.md`: add entries at the end only. Correct or close something by appending a new entry that names the old one.
4. **The baseline is frozen.** Files in the transfer-baseline release are never edited in place. Fixes land afterward as new revisions, so the history shows each one.
5. **Plain, runtime-neutral files.** `.md`, `.csv` (UTF-8, no BOM), `.xlsx`, `.json`, `.py`. `.docx` only as a reading copy in `testbeds/eastsound/process/`. Python is stdlib-only except packages pinned in `requirements.txt`. Nothing may depend on one AI tool's features.
6. **One writer per file.** `index/` belongs to the Setup role. A lane writes only in its own `lanes/<lane>/` folder. Merge writes only in `project/`. The build session, meaning the Transfer thread or one Claude Code session and never both at once, owns `transfer/`, `tools/` and `graph/` under `testbeds/eastsound/`, plus the notes beside library files.
7. **Retrieval goes through the Wiki, the Ledger and the graph built from them,** not bulk reads of `library/`. If a task can't be answered without reading the library, stop that task and log a design gap.
8. **Never bypass or rewrite.** No `--no-verify`, no disabling hooks, no force-push or rewriting pushed history. Changes to `tools/checks.py` go in their own commit, only when a person asked for them.

## Output standards (all project content)
- Cite every factual claim: sheet number, spec section and paragraph, or addendum number and item. Page cites use the file short names defined in `testbeds/eastsound/index/00_Document_Register_rev1.md`.
- Tag every claim: Verified (read in the text layer), Verified-Visual (read from the page image), Inferred (derived; state the reasoning), Unresolved (conflict or missing; state what's needed).
- Text from OCR copies under `testbeds/eastsound/derived/` counts as OCR and is tagged Inferred, never Verified or a text layer. Verified text-layer reads come only from the native files in `library/`. OCR copies are Inferred only. They may feed tag and quantity leads (method bluebeam-ocr), never a text layer or a Verified read.
- Addenda supersede base documents. On a conflict, cite both and state which governs.
- The body section number governs over running headers and the TOC. A claim that defers to WSDOT is tagged "Unresolved: external reference, not staged."
- Ledger CSVs use the exact 16-column header in `testbeds/eastsound/index/Ledger_Schema.csv`. A row's tag is the weakest tag of the facts in it.
- Wiki note format: Document ID | Type | Discipline | Revision/Date | 3–5 sentence summary | Tags (equipment, spec sections, sheets, addenda) | Related documents.
- Don't fill gaps with typical practice unless it's tagged Inferred with the reasoning. "Not stated" beats a guess.
- Plain-English names, no coded labels. "Thread" means one chat or agent session; "lane" means a crawl scope only.

## Layout
```
AGENTS.md                  canonical rules (this file)
CLAUDE.md                  imports AGENTS.md, plus Claude Code specifics
README.md
PROGRESS_LOG.md            append-only, one entry per session
DECISIONS.md               append-only, decisions made by a person
ISSUES_LOG.md              append-only, repo and program issues
requirements.txt           pinned Python packages
.gitattributes             byte guard: no line-ending changes except git hooks
.gitignore
.claude/settings.json      Claude Code guardrails
.githooks/pre-commit       runs tools/checks.py --staged (Prompt 1 adds it)
.github/workflows/         CI: the same checks on every push (Prompt 1 adds it)
prompts/                   task prompts, plain markdown, any runtime
tools/                     repo-wide scripts (Prompt 1 adds checks.py)
testbeds/eastsound/
  library/                 original source files (read-only) plus .md notes beside them
  derived/                 derived copies of library files; not sources. Each subfolder is owned by the lane that writes it; bluebeam-ocr/ is owned by Carl
    issues/                open-items list built from reconciliation/, project/03_Exceptions_and_Issues/ and ISSUES_LOG.md (list only; nothing applied)
    reconciliation/        proposed Ledger updates, starter MTO and new-row candidates built from derived/ocr/ (proposals only; nothing applied)
    wiki/                  Wiki note and link tables parsed from project/01_Project_Wiki (derived; not a source)
  index/                   00–04 rev1, Ledger_Schema.csv, Requirements_Schema.csv (Setup)
  lanes/<lane>/            Wiki, Ledger, Issues, Known Issues per lane
    as-delivered/          lane packages as delivered (component wikis, page notes, build-script zips)
  project/                 Merge outputs, including the test bed's Issues Log
  process/                 Ultraplans, build prompts, library fingerprints
  transfer/                Transfer step reports
  tools/                   test bed build scripts
  graph/                   graph build outputs
  _unsorted/               files a sort couldn't place; README.md gives each one's reason. Owned by Carl
_inbox/                    drop zone for a person's files; never committed
```
Lane folders: `civil-and-site`, `process-and-mechanical`, `electrical-and-controls`, `structural-and-building`, `contract-and-general`.

## Commands
- One-time per clone, after Prompt 1: `git config core.hooksPath .githooks`
- Checks: `python tools/checks.py --all` (whole tree), `--staged` (what the hook runs), `--range BASE..HEAD` (what CI runs). On Windows use `py -3` if `python` isn't found.
- Graph build: follow the build step in `Graph_Transfer_Ultraplan.md`. The seed script `testbeds/eastsound/tools/ledger_to_graph.py <ledger.csv> --out <folder>` writes `<folder>/graphify-out/graph.json`; `graphify cluster-only <folder> --no-label` adds GRAPH_REPORT.md and graph.html.
- Graph queries: `graphify explain "<tag>" --graph <path to graph.json>`; for cross-item traces `graphify path "<A>" "<B>" --undirected --graph <same path>`

## Working rhythm
- Session start: once Prompt 1 has run, confirm `git config core.hooksPath` returns `.githooks` (set it if not). Read the last 3 entries of `PROGRESS_LOG.md` and the open entries in `ISSUES_LOG.md`.
- Plan before any multi-file change. State assumptions explicitly.
- Work in batches of about 4 files or one logical step; commit after each batch. Commit message: `<area>: <what changed>`.
- When a test or check fails: log the failure mode and the fix before rerunning.
- Concurrent sessions each use their own branch (`lane/<name>`, `setup`, `merge`, `build`) and merge by pull request. A single session may commit to `main`.
- End every session with `prompts/close_session.md`. Push only after checks pass.

## Log entry formats
PROGRESS_LOG.md
```
## YYYY-MM-DD — <session title>
- Runtime: Claude Code | Codex | manual
- Commits: <first hash>..<last hash>
- Done: <what changed, with file paths>
- Tests: <command> → pass/fail, counts
- Failures and fixes: <or "none">
- Next: <next step>
```
DECISIONS.md
```
## YYYY-MM-DD — <decision in plain words>
- Decided by: <name>
- Why: <one or two sentences>
- Replaces: <earlier entry, or "none">
```
ISSUES_LOG.md (repo and program issues)
```
## YYYY-MM-DD — <short title> — Open | Closed
- Workstream: <e.g., Repo setup>
- Type: workflow failure | schema gap | input gap | content conflict | design gap
- Finding: <what happened, with citation>
- Fix or next action: <what was done or is needed>
```
The test bed's own issues continue in the Merge Issues Log under `testbeds/eastsound/project/`, keeping its numbering and columns.

Only a person makes decisions. An agent writes a DECISIONS.md entry only to record, in quotes, what the person said in the current session.

## Graph tooling
- The core graph is built from the Ledger by script with no LLM calls, so every runtime produces the same graph. Outputs go in `testbeds/eastsound/graph/`.
- Tag mapping: Verified and Verified-Visual → EXTRACTED; Inferred → INFERRED; Unresolved → AMBIGUOUS. Every link keeps the original tag level, the Source Citation and the Ledger line number.
- graphify is pinned in `requirements.txt`. Call its CLI directly. Don't run `graphify install`, `graphify claude install` or `graphify hook install`; they rewrite agent config files and git hooks.
- Run graph commands with no LLM API keys in the environment. graphify's LLM extraction over prose is optional; if used, its output goes to `testbeds/eastsound/graph/overlay/`, is labeled as model output, and is never written back to a Ledger.
