# Prompt 5 — Repo cleanup

> As run 2026-09-30 in Claude Code. The answers and corrections given during that run (branch, README, layout conflicts, library scope) are recorded in `testbeds/eastsound/process/Repo_Reorg_Report_2026-09-30.md` and in DECISIONS.md.

## Rules for this pass

* Move with `git mv` only. Don't edit, merge, deduplicate, delete or restyle any file. The only edits allowed are the ones listed in Steps 4–6.
* File names stay as uploaded, spaces included. Folders you create follow the target layout below.
* If you can't tell where a file belongs, put it in `testbeds/eastsound/_unsorted/` and say why. Don't guess.
* Source documents (drawings, specs, addenda, QA plan) are never renamed or edited. None should be in the repo yet. If you find one, report it; it goes in `testbeds/eastsound/library/` under its exact name.
* Work on a branch named `reorg`, with one commit per step. Open a pull request and don't merge it.

## Step 0 — Stop checks

* Send an unauthenticated GET to `https://api.github.com/repos/Big-D-HI-Carl/Project-1---Undefined`. A 404 means the repo is private: continue. A 200 means it's public: stop and tell me.
* Read these in full first: AGENTS.md, CLAUDE.md, both Sample_Project_Concurrent_Lane_Ultraplan_rev1 files, Graph_Transfer_Ultraplan.md, README.md, README (2).md, Drag_and_Drop_Order.md, 00_Document_Register_rev1.md.

## Target layout

```
README.md                        program front page (restored in Step 4)
AGENTS.md  CLAUDE.md  requirements.txt
PROGRESS_LOG.md  DECISIONS.md  ISSUES_LOG.md
.claude/settings.json            the uploaded settings.json (confirm by content)
prompts/                         01_bootstrap_guardrails.md to 04_retrieval_test.md, close_session.md, this prompt
prompts/history/                 earlier prompts (Composer prompts when uploaded)
tools/ledger_to_graph.py
testbeds/eastsound/
  README.md                      one line per folder below (new)
  process/                       both Ultraplan rev1 files, Graph_Transfer_Ultraplan.md,
                                 Drag_and_Drop_Order.md, this pass's report
  index/                         00–04 rev1 files, every schema CSV, Library_Fingerprint*.csv
  library/                       source documents only, flat, names exactly as in the 00 register
  lanes/<lane>/                  that lane's Wiki, Ledger, Issues and Known Issues
  lanes/<lane>/as-delivered/     that lane's per-page component and per-component wiki outputs,
                                 folder structure as uploaded
  project/                       Merge rev2 package: 01_Project_Wiki to 07_Resplit_Pass, plus its README.md
  derived/                       machine-made extracts (OCR text, sheet map); empty for now
  _unsorted/                     anything you can't place, with the reason in the report
```

Lane folder names: `civil-and-site`, `process-and-mechanical`, `electrical-and-controls`, `structural-and-building`, `contract-and-general`.

## Step 1 — Inventory and mapping table (no moves)

Walk the whole tree. Give one row per file or folder: current path | proposed path | how you know (file name, header line or content) | confidence.

### Deciding which lane a file belongs to

* Decide each file's lane from its own content (header, lane line, citations), not from its folder name.
* The area folders at the root come in pairs, one spelled with spaces and one with underscores (2W Pump Station and 2W_Pump_Station, Blower Building and Blower_Building, Influent Pump Station and Influent_Pump_Station, the UV Disinfection pair, Area not stated and Not_stated, and others). They are probably component wikis from different lanes. Open files in each folder to decide. Keep both folders; don't merge them.
* The loose component notes at the root belong with whichever lane's component wiki they came from. These are Buried_Valve_ID_, Pipe_ID_, PROPOSED-, SDCB_, SSMH_, SD-1 and Hot_Box_. Confirm the lane from their content.

### Specific files and folders

* Folders with a doubled path, such as Civil_and_Site_Pages/Civil_and_Site_Pages: move the inner folder and drop the empty outer one.
* Drawings/, Specifications/ and Addendum 4/: open each one and say what it holds before proposing a place.
* `download`, `download (1)` and README (2).md: identify each one with `file` and its first lines, then propose a place or `_unsorted/`.
* The root README.md is the Merge package README. It goes to `project/README.md`.

Folder-name conflicts Also list, one line each, where this layout differs from the folder names in Graph_Transfer_Ultraplan.md and rev1 (`graph/`, `process/`, `transfer/`). Don't change the layout for them; I'll decide.

Stop here and wait for my approval.

## Step 2 — Move

Apply the approved table with `git mv`. Make one commit per destination group: kit files, index, process, project, each lane, then unsorted. After each commit, check two things:

* The file count is the same before and after.
* `git diff --stat -M HEAD~1` shows renames only.

## Step 3 — Missing-file report

Compare what's in the repo now against these lists:

* Library: every file in 00_Document_Register_rev1.md. None are expected yet, so list them all as "to upload".
* Project: every file in the project/README.md folder map.
* Each lane: `<Lane>_Wiki.md`, `<Lane>_Ledger.csv`, `<Lane>_Issues.md`, `<Lane>_Known_Issues.md`.
* Index: Audit_Ledger_Schema.csv, Spot_Check_Schema.csv and the Setup resplit list.
* prompts/history: Composer Prompt_1_Civil_and_Site.md to Prompt_6_Merge.md, and Prompt_Workflow_Receipt_rev1.md.

Report it as a table: expected file | expected place | present | notes.

## Step 4 — READMEs

* Restore the root README.md from the repo's first commit. Find it with `git log --reverse --format=%H -- README.md | head -1`, then `git show <hash>:README.md`. Under the restored text, add exactly two lines: one saying the Eastsound test bed lives in `testbeds/eastsound/`, and "Rules: see AGENTS.md".
* Write `testbeds/eastsound/README.md` with one line per folder in the target layout, saying what it holds.

## Step 5 — Report and logs

* Write `testbeds/eastsound/process/Repo_Reorg_Report_<YYYY-MM-DD>.md`. Include the final mapping table, the missing-file table, the `_unsorted/` list with reasons, and the layout conflicts.
* Append one PROGRESS_LOG.md entry in the AGENTS.md format.
* Append one ISSUES_LOG.md entry:
   * Title: "Browser upload flattened the kit folders and replaced the program README"
   * Type: workflow failure
   * Fix: this pass. Upload future files from inside their target folder.
* Append to DECISIONS.md only what I state as a decision in this session, quoted.

## Step 6 — Rulebook fixes (separate commit, after the moves)

* AGENTS.md, Layout section: add `process/`, `derived/`, `_unsorted/` and `lanes/<lane>/as-delivered/`. Change no rules.
* prompts/01_bootstrap_guardrails.md:
   * Step 1 should expect the kit already committed and organized. Drop "starter kit as delivered" from its commit order.
   * The read-only-sources check should also fail when a non-.md file is added under `library/`, unless a matching row for it is added to `index/Library_Manifest.csv` in the same commit.

## Done when

* The root holds only what the target layout lists.
* Every uploaded file has a place, or is listed in `_unsorted/` with a reason.
* The pull request shows renames only, apart from the two READMEs, the report, the log entries and the Step 6 edits.
