# Issues Log

Append-only. Repo and program issues, in the format in AGENTS.md. The test bed's own issues continue in the Merge Issues Log under testbeds/eastsound/project/, with its numbering.

## 2026-09-30 — Uploaded repo tree is flat; kit layout and guardrails not in place — Open
- Workstream: Repo setup
- Type: workflow failure
- Finding: The web upload put every file at the repo root: the index files, the Merge outputs, the lane component folders, `ledger_to_graph.py` and the prompts `01_bootstrap_guardrails.md` to `04_retrieval_test.md` and `close_session.md`. `testbeds/eastsound/` (except the new `derived/`), `library/`, `process/`, `prompts/`, `tools/`, `.claude/` and `.githooks/` don't exist, and no library source PDFs are in the repo. By their contents, `settings.json`, `download` and `download (1)` are the kit's `.claude/settings.json`, `.gitattributes` and `.gitignore` under the wrong names, so the byte guard, the ignore list and the library deny rules are all inactive. The root `README.md` is the Merge rev2 README; the repo README is `README (2).md`. Prompt 1 and `close_session.md` step 1 can't run as written because `tools/checks.py` doesn't exist.
- Fix or next action: A person lays the tree out per `Drag_and_Drop_Order.md` or approves an agent move plan, restores `.gitattributes` first, adds the library sources, then runs Prompt 1.

## 2026-09-30 — Six sheets exist only in the Bluebeam OCR copies — Open
- Workstream: Eastsound test bed
- Type: input gap
- Finding: C0.7, C1.1 and C1.2 (OCR Part 1 pp.14–16, set pp.14–16) and C7.7, C7.8 and C7.9 (OCR Part 2 pp.1–3, set pp.49–51) are in the OCR copies but not in the library (`01_Sheet_Index_rev1.md` status "not in library"; Merge README "Still open"). Under the 2026-09-30 decision their OCR text is Inferred only, so the copies don't close the gap. Detail: `testbeds/eastsound/derived/bluebeam-ocr/README.md`.
- Fix or next action: A person adds native copies of the six sheets to `testbeds/eastsound/library/`. Until then, Prompt 6 comparison rows for these sheets have no native column.

## 2026-09-30 — Six sheets exist only in the Bluebeam OCR copies — Closed
- Workstream: Eastsound test bed
- Type: input gap
- Finding: Closes the 2026-09-30 Open entry "Six sheets exist only in the Bluebeam OCR copies". The native plan-set parts now in `testbeds/eastsound/library/` hold all 10 sheets `01_Sheet_Index_rev1.md` lists as not in library, each read in the native title block (Verified; `testbeds/eastsound/library/Plan_Set_Parts.md`):
  - set pp.10, 14–16, 20, 22 and 25: C0.3, C0.7, C1.1, C1.2, C2.1, C2.3, C2.6 (Part 1);
  - set pp.49–51: C7.7, C7.8, C7.9 (Part 3 pp.1–3).
- Fix or next action: Done. `testbeds/eastsound/derived/bluebeam-ocr/README.md` now points at the native counterparts.

## 2026-09-30 — Uploaded repo tree is flat; kit layout and guardrails not in place — Closed
- Workstream: Repo setup
- Type: workflow failure
- Finding: Closes the 2026-09-30 Open entry of the same title.
  - 792 files moved into the AGENTS.md layout, with no content changes (blob IDs checked).
  - `.gitattributes`, `.gitignore`, `.claude/settings.json` and `README.md` restored by rename. The byte guard is active: PDFs are now binary to git.
  - Relative links in the lane packages: 3,612 resolve and 0 are broken, down from 1,517 broken before.
- Fix or next action: Done. Missing inputs are listed in the PROGRESS_LOG entry "Inbox sort and root layout". Next is Prompt 1 (`prompts/01_bootstrap_guardrails.md`), which adds `tools/checks.py`, `.githooks/` and CI.

## 2026-09-30 — Index files cite plans_N extracts that aren't in the library — Open
- Workstream: Eastsound test bed
- Type: input gap
- Finding:
  - `testbeds/eastsound/index/00_Document_Register_rev1.md` rows 5–30 and `01_Sheet_Index_rev1.md` cite the plans_N extracts. None of those extracts is in `testbeds/eastsound/library/`.
  - The library holds the same 96 set pages as three native parts under other names (Part 1 = set pp.1–27, Part 2 = 28–48, Part 3 = 49–96). The Register has no rows for them.
  - `div-26-electrical-specs.pdf` (Register row 2) isn't uploaded either.
- Fix or next action: `testbeds/eastsound/library/Plan_Set_Parts.md` maps every plans_N page to a Part page for now. The Setup role, which owns `index/`, adds Register rows for the three parts, or a person uploads the plans_N extracts.

## 2026-09-30 — Three lane package READMEs were overwritten at the repo root during upload — Open
- Workstream: Repo setup
- Type: workflow failure
- Finding: Each browser upload wrote its package README to the root README.md, and the next upload overwrote it. Three lane package READMEs now exist only in history, and each package's README slot is empty in the tree:
  - `7fba2f5:README.md` (blob acd2cc0d): "Electrical & Controls — Wiki by Page and by Component". Its package is now `testbeds/eastsound/lanes/electrical-and-controls/as-delivered/`.
  - `0b488b9:README.md` (blob 98886d2d): "Civil & Site — Component Wiki". Its package is now `testbeds/eastsound/lanes/civil-and-site/as-delivered/Civil_and_Site_Components/`.
  - `5f76965:README.md` (blob 63fd81cc): "Process & Mechanical — Component Wiki". Its package is now `testbeds/eastsound/lanes/process-and-mechanical/as-delivered/`.
  - The test-bed README had the same fate (`8039650:README.md`). It was restored to `testbeds/eastsound/README.md` in e0830b2.
- Fix or next action: On a person's OK, restore each one byte for byte as README.md in its package folder, one commit each.

## 2026-09-30 — Browser upload flattened the kit folders and replaced the program README — Closed
- Workstream: Repo setup
- Type: workflow failure
- Finding: The web uploads put every kit and lane folder at the repo root and wrote each package README over the root README.md in turn: the program README (7800b18), then Electrical & Controls (7fba2f5), Civil & Site (0b488b9), Process & Mechanical (5f76965), the kit test-bed README (8039650) and the Merge rev2 README (92585e6). The kit's program README arrived as `README (2).md`. The same failure is also logged in the entries "Uploaded repo tree is flat; kit layout and guardrails not in place" (Open, then Closed) and "Three lane package READMEs were overwritten at the repo root during upload".
- Fix or next action: This pass (`prompts/05_repo_cleanup.md`; report `testbeds/eastsound/process/Repo_Reorg_Report_2026-09-30.md`). The files were moved by the `claude/sharp-thompson-5q5d1f` session (dae20bd..41f811e); `README (2).md` became README.md; the three lane READMEs were restored in this pass. Upload future files from inside their target folder.

## 2026-09-30 — Three lane package READMEs were overwritten at the repo root during upload — Closed
- Workstream: Repo setup
- Type: workflow failure
- Finding: Closes the 2026-09-30 Open entry of the same title. Restored byte for byte, blob IDs matching history: `7fba2f5:README.md` → `testbeds/eastsound/lanes/electrical-and-controls/as-delivered/README.md` (39ef888), `0b488b9:README.md` → `testbeds/eastsound/lanes/civil-and-site/as-delivered/Civil_and_Site_Components/README.md` (9887a3e), `5f76965:README.md` → `testbeds/eastsound/lanes/process-and-mechanical/as-delivered/README.md` (fd05ef0). Their links resolve: 181, 115 and 114 of 181, 115 and 114.
- Fix or next action: Done.

## 2026-09-30 — Two sessions ran the same reorg step — Open
- Workstream: Repo setup
- Type: workflow failure
- Finding: While this session (branch `claude/charming-lamport-it1dac`) waited at the Step 1 approval stop of `prompts/05_repo_cleanup.md`, a second Claude Code session (`claude/sharp-thompson-5q5d1f`) sorted the inbox and moved all 792 files into the layout, merged as PRs #1 and #2 (9fec0a2). The results agreed (752 of 792 at the same paths; the rest a documented difference), but two build sessions worked the same folders, which AGENTS rule 6 and the Ultraplan rev1 §5 "one build session at a time" rule forbid. Found by `git fetch` before Step 2. Carl confirmed the other session is closed.
- Fix or next action: One session per step; check open sessions before starting one. A matching line for the AGENTS.md Working rhythm section is proposed to Carl; the entry stays Open until he decides.

## 2026-09-30 — 00 Register rev2 needs rows for the three native plan-set parts — Open
- Workstream: Eastsound test bed
- Type: input gap
- Finding: The library's drawing set is the three native parts (decision 2026-09-30), which have no rows in `testbeds/eastsound/index/00_Document_Register_rev1.md`. Register rows 5–30 name the 26 plans_N extracts, which aren't in the library and won't be uploaded; every plans_N page now resolves through `testbeds/eastsound/index/Plan_Set_Crosswalk.csv` (99 rows, each checked against the native title block, 0 mismatches). Row 2 (`div-26-electrical-specs.pdf`) is settled by decision: not uploaded, main spec governs. Related for 01 rev2: the 10 sheets 01 lists as not in library are in Part 1 and Part 3, and the native S1.1–S4.1 title blocks read "OF 96" (Verified-Visual), against 01 item 10's "OF 98" at stored resolution. Follows the Open entry "Index files cite plans_N extracts that aren't in the library".
- Fix or next action: Setup issues 00 rev2 (rows for Part 1, Part 2, Part 3; plans_N rows resolved through the crosswalk; row 2 closed by decision) and 01 rev2. Setup also adopts or replaces `Library_Manifest.csv` and `Plan_Set_Crosswalk.csv`, which this session wrote in `index/` at Carl's direction.

## 2026-09-30 — Native library files don't match Library_Fingerprint.csv (expected) — Open
- Workstream: Eastsound test bed
- Type: design gap
- Finding: `testbeds/eastsound/process/Library_Fingerprint.csv` and `_Pages.csv` fingerprint the Claude Project's converted copies (page bundles and text-only files), not the native PDFs. The native files' SHA-256 values and sizes differ (for example the main spec: 1,436,556 bytes converted, 17,502,025 bytes native), and the plan set is now three parts, not the 28 plans_N files. This is expected. `Library_Fingerprint.csv` is not edited; the natives are recorded in `testbeds/eastsound/index/Library_Manifest.csv`.
- Fix or next action: Revise Graph_Transfer_Ultraplan §6 Step 4 (and Appendix C step 1), whose check requires text to match on all 888 fingerprinted pages, before any Transfer run. Owner: the person approving the Transfer plan.
