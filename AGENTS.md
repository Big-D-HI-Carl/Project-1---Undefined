# AGENTS.md

Canonical instructions for every coding agent in this repo (Claude Code, Codex, others). CLAUDE.md imports this file. Change rules here, not in CLAUDE.md.

## What this repo is
- Progress log and working files for the Heavy Industrial AI Implementation Program.
- First workstream: the Eastsound test bed, built on the public bid set for the Eastsound Sewer and Water District WWTP Upgrade Phase I plus addenda. It proves the Project Wiki + Project Ledger architecture, the crawl prompts, and two Phase 1 workflows before any company data is connected. It lives in `testbeds/eastsound/`.

## Hard rules
Rules marked (checked) are enforced by `tools/checks.py` in the pre-commit hook and in CI. The rest depend on you.

1. **Data (checked where possible).** Public-source material only, plus notes about work done in this repo. No Big-D, client or employee data; no internal names, budgets or schedules; no credentials or keys. This holds until Big-D approves this host. If unsure whether something qualifies, stop and ask.
2. **Sources are read-only (checked).** Never rename, move, edit or delete a source file under any `library/` folder. A person adds source files. Notes go beside their source as `.md` files; agents may add and edit those notes, and nothing else, inside `library/`.
3. **Logs are append-only (checked).** `PROGRESS_LOG.md`, `DECISIONS.md`, `ISSUES_LOG.md`: add entries at the end only. Correct or close something by appending a new entry that names the old one.
4. **Plain, runtime-neutral files.** `.md`, `.csv` (UTF-8, no BOM), `.xlsx`, `.json`, `.py`. Python is stdlib-only except packages pinned in `requirements.txt`. Nothing may depend on one AI tool's features.
5. **One writer per file.** `index/` belongs to the Setup role. A lane writes only in its own `lanes/<lane>/` folder. Merge writes only in `project/`.
6. **Retrieval goes through the Wiki, the Ledger and the graph built from them,** not bulk reads of `library/`. If a task can't be answered without reading the library, stop that task and log a design gap in `ISSUES_LOG.md`.
7. **Never bypass or rewrite.** No `--no-verify`, no disabling hooks, no force-push or rewriting pushed history. Changes to `tools/checks.py` go in their own commit, only when a person asked for them.

## Output standards (all project content)
- Cite every factual claim: sheet number, spec section and paragraph, or addendum number and item. Page cites use the file short names defined in `testbeds/eastsound/index/00_Document_Register_rev1.md`.
- Tag every claim: Verified (read in the text layer), Verified-Visual (read from the page image), Inferred (derived; state the reasoning), Unresolved (conflict or missing; state what's needed).
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
ISSUES_LOG.md              append-only, all workstreams
requirements.txt           pinned Python packages
.gitattributes             line-ending rules (Windows-safe)
.githooks/pre-commit       runs tools/checks.py --staged
.github/workflows/         CI: same checks on every push
.claude/settings.json      Claude Code guardrails
prompts/                   task prompts, plain markdown, any runtime
prompts/history/           earlier prompts and plans, reference only
tools/                     shared scripts, one copy of each
testbeds/eastsound/
  library/                 source documents (read-only, fixed structure) plus .md notes beside them
  index/                   00–04 inventory files, schemas, library manifest (Setup)
  lanes/<lane>/            Wiki, Ledger, Issues, Known Issues per lane
  project/                 merged Wiki and Ledger, registers, reports (Merge)
  graphify-out/            built graph: graph.json, GRAPH_REPORT.md, graph.html
_inbox/                    drop zone for a person's files; never committed
```
Lane folders: `civil-and-site`, `process-and-mechanical`, `electrical-and-controls`, `structural-and-building`, `contract-and-general`.

## Commands
- One-time per clone: `git config core.hooksPath .githooks`
- Checks: `python tools/checks.py --all` (whole tree), `--staged` (what the hook runs), `--range BASE..HEAD` (what CI runs). On Windows use `py -3` if `python` isn't found.
- Graph build: `python tools/ledger_to_graph.py testbeds/eastsound/project/Project_Ledger.csv --out testbeds/eastsound`, then `graphify cluster-only testbeds/eastsound --no-label`
- Graph queries: `graphify explain "<tag>" --graph testbeds/eastsound/graphify-out/graph.json`; for cross-item traces `graphify path "<A>" "<B>" --undirected --graph <same path>`

## Working rhythm
- Session start: confirm `git config core.hooksPath` returns `.githooks` (set it if not). Read the last 3 entries of `PROGRESS_LOG.md` and the open entries in `ISSUES_LOG.md`.
- Plan before any multi-file change. State assumptions explicitly.
- Work in batches of about 4 files or one logical step; commit after each batch. Commit message: `<area>: <what changed>`.
- When a test or check fails: append the failure mode and the fix to `ISSUES_LOG.md` before rerunning.
- Concurrent sessions each use their own branch (`lane/<name>`, `setup`, `merge`) and merge by pull request. A single session may commit to `main`.
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
ISSUES_LOG.md
```
## YYYY-MM-DD — <short title> — Open | Closed
- Workstream: <e.g., Repo setup, Eastsound test bed>
- Type: workflow failure | schema gap | input gap | content conflict | design gap
- Finding: <what happened, with citation>
- Fix or next action: <what was done or is needed>
```
Only a person makes decisions. An agent writes a DECISIONS.md entry only to record, in quotes, what the person said in the current session.

## Graph tooling
- `tools/ledger_to_graph.py` builds the graph from a Ledger CSV with no LLM calls, so every runtime produces the same graph.
- Tag mapping: Verified and Verified-Visual → EXTRACTED; Inferred → INFERRED; Unresolved → AMBIGUOUS. Every link keeps the original tag level, the Source Citation and the Ledger line number.
- graphify is pinned in `requirements.txt`. Call its CLI directly. Don't run `graphify install`, `graphify claude install` or `graphify hook install`; they rewrite agent config files and git hooks.
- Run graph commands with no LLM API keys in the environment. graphify's LLM extraction over prose is optional; if used, its output goes to `graphify-out/overlay/`, is labeled as model output, and is never written back to a Ledger.
