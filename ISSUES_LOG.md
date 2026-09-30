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

## 2026-09-30 — OCR lane Step 1: calibration failures fixed before the full run — Closed
- Workstream: Eastsound test bed (Prompt 7 OCR lane)
- Type: workflow failure
- Finding: These failures came up during the Step 1 calibration runs on set pp.20, 22, 28, 29, 45, 56–61, 70 and Add. 4 pp.7–10. Each one was fixed before the next run, but these entries were written afterward, at Gate A. The rule is to log a failure before rerunning.
  - The title block was not read on the 9 pages with no text layer, nor on Add. 4 pp.8–10. The full-page 400 dpi psm 3 passes skipped the title-block boxes; S2.1's sheet number read as "$2.1" and C3.3's "28 OF 96" as noise.
  - The strip anchor picked lowercase "scale" (from "Verify scale") and a plan-area SCALE label. OCR fragments ("PHASE 1") also slipped past the exact-match template test.
  - The word normalizer stripped the "$" before the $→S fix could read the sheet number.
  - The first full run never started, because `/usr/bin/time` is not installed in the container.
  - Keyed notes mis-numbered. The block missed markers 15 pt left of the heading, used the median line spacing, and read embedded detail bubbles as entries. Misread markers ("(1)" for 11) restarted the count.
  - Pipe ID and Buried Valve ID legend lines were missed (7 of 39), because an ID and its description on the same baseline merged into one line.
- Fix or next action: Done, in `tools/extract_drawing_text.py` (9c9edf1).
  - Title blocks: a rotated title-strip pass at 200 and 300 dpi, psm 11, anchored on the nearest uppercase title-block label, with the higher-confidence read kept per field. Template lines also match on 80% of their characters.
  - Sheet numbers: "$" is kept for the S fix.
  - Timing: the run is timed with shell `date` instead.
  - Keyed notes: an entry column of −30…+20 pt around the heading, 25th-percentile spacing, stray rows attached to their entry, entries starting only in the marker column, and read markers trusted only when they run on from the previous entry.
  - Legend lines: descriptions are taken from the words in each number's row band.
  - After the fixes: 96 of 96 title blocks match 01, and 39 of 39 legend lines are found.

## 2026-09-30 — PR #2 (sort pass) was not merged when the OCR lane started — Closed
- Workstream: Eastsound test bed (Prompt 7 OCR lane)
- Type: workflow failure
- Finding: Step 0 found PR #2 open and main still at the flat upload (1fc06ef), so none of the paths in the Prompt 7 amendments existed on main. The lane stopped at Step 0.
- Fix or next action: Done. The owner merged PR #2 (9fec0a2), and this branch was fast-forwarded to it. Step 0 was re-checked on the merged main: part SHA-256 values match `Plan_Set_Parts.md`, and the Ledger has 447 rows, 123 of them Unresolved.

## 2026-09-30 — Four schema CSVs need uploading to index/ — Open
- Workstream: Eastsound test bed
- Type: input gap
- Finding: Prompt 7 names Spot_Check_Schema columns, but no Spot_Check_Schema file is in the repo. The owner keeps the schema files in the Claude Project. `testbeds/eastsound/index/` holds Ledger_Schema.csv and Requirements_Schema.csv (both the 16-column rev0 headers, with no Quantity or Unit column). It holds no Audit_Ledger or Spot_Check schema. `derived/ocr/Spot_Check.csv` uses the column order the owner gave in session.
- Fix or next action: A person uploads the four schema CSVs (Requirements, Ledger, Audit_Ledger, Spot_Check) to `testbeds/eastsound/index/`, through the Setup role that owns index/. Agents don't create them.

## 2026-09-30 — AGENTS.md and the Bluebeam README still say OCR copies are a comparison column only — Open
- Workstream: Repo setup
- Type: content conflict
- Finding: The owner's 2026-09-30 decision (DECISIONS.md, "Bluebeam OCR hits go into Tag_Hits and Quantity_Hits, still Inferred") replaces the comparison-only rule. Two files still state the old rule: AGENTS.md Output standards ("OCR copies are a comparison column only") and `testbeds/eastsound/derived/bluebeam-ocr/README.md` (Rule, third bullet). Both are outside the OCR lane's write scope.
- Fix or next action: On the owner's OK, change the AGENTS.md line to: "OCR copies are Inferred only. They may feed tag and quantity leads (method bluebeam-ocr), never a text layer or a Verified read." Then update the Bluebeam README's Rule to match. Each goes in its own commit.

## 2026-09-30 — Index and library notes call the 9 no-text-layer sheets "image-only" — Open
- Workstream: Eastsound test bed
- Type: content conflict
- Finding: `library/Plan_Set_Parts.md` and `index/01_Sheet_Index_rev1.md` call C3.3, C3.4, C7.3, S1.1, S2.1–S2.4 and S4.1 "image-only". They are vector drawings with no text layer, not raster images (Prompt 7 amendments). `derived/ocr/Sheet_Map.csv` reads all 9 title blocks by OCR (Inferred).
- Fix or next action: The Setup role corrects the wording in 01; the build session corrects it in the Plan_Set_Parts.md note.

## 2026-09-30 — Ledger Drawing Sheets: 80 rows cite no sheet number (78 PROPOSED, 2 printed) — Open
- Workstream: Eastsound test bed
- Type: input gap
- Finding: 74 Ledger rows have a blank Drawing Sheets field: 72 PROPOSED rows plus 2 printed rows (Receiving Conveyor, Inclined Conveyor). 6 more rows name no sheet number ("—", "Not shown", "None (Add. 4 and 26 05 00 only)", "TESC plans (civil sheets, not numbered in source)"). The OCR lane can't check any of these against a sheet. `derived/ocr/Ledger_Crosswalk.csv` shows them as "no sheet cited" or "no sheet number cited".
- Fix or next action: The Merge role or the lanes add sheet citations where the documents give them.

## 2026-09-30 — Project_Ledger.csv repeats two Tags — Open
- Workstream: Eastsound test bed
- Type: content conflict
- Finding: `python tools/checks.py --all` (Prompt 1, acceptance test 9) fails the ledger check on the baseline file `testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv`:
  - `SD-1` names two different items. Line 74 is the storm drain alignment SD-1 (Civil & Site; C2.2; Unresolved). Line 316 is the 3 HP sludge pump (Electrical & Controls; E4.1, E6.1; Verified-Visual).
  - `PROPOSED-Influent-Sampler` is one item entered by two lanes. Line 321 is Electrical & Controls (E4.1 key note 6; Verified-Visual). Line 419 is Contract & General (main spec 00 31 13 ¶A.17; Inferred).
  - The file was not edited. It is listed in `tools/check_exceptions.csv` for the ledger rule, so the check warns instead of failing. That exception covers every ledger finding in this file until it is removed.
- Fix or next action: Merge issues a new Project Ledger revision that gives one of the two `SD-1` items its own Tag and folds the two influent-sampler rows into one, keeping both citations. Then remove the exceptions row.

## 2026-09-30 — Project_Ledger_by_CWP.csv doesn't follow the Ledger schema — Open
- Workstream: Eastsound test bed
- Type: schema gap
- Finding: The ledger check applies to every `*Ledger*.csv`, including the baseline CWP view `testbeds/eastsound/project/02_Project_Ledger/Project_Ledger_by_CWP.csv`, and fails it (Prompt 1, acceptance test 9):
  - It has 19 columns: CWP, CWP Name and CWP Basis ahead of the 16 columns in `testbeds/eastsound/index/Ledger_Schema.csv`.
  - It repeats the two duplicate Tags: `SD-1` at lines 107 and 304, and `PROPOSED-Influent-Sampler` at lines 432 and 439 (see "Project_Ledger.csv repeats two Tags").
  - The file was not edited. It is listed in `tools/check_exceptions.csv` for the ledger rule.
- Fix or next action: Carl decides whether the CWP view counts as a Ledger. If not, issue its next revision under a name without "Ledger", or ask for a checks.py change that narrows the file pattern. If it does, it needs its own schema. The duplicate Tags clear with the Project Ledger fix.

## 2026-09-30 — checks.py read the OCR lane's Ledger_Crosswalk.csv as a Project Ledger — Closed
- Workstream: Repo setup
- Type: workflow failure
- Finding: After main (PR #5) was merged into the OCR lane branch, `python tools/checks.py --all` gave 3 FAIL for `testbeds/eastsound/derived/ocr/Ledger_Crosswalk.csv`: the header differs from Ledger_Schema.csv, and two Tags repeat (lines 316 and 419). `is_ledger()` matched any file named `*ledger*.csv`. The crosswalk is not a Ledger; it is keyed on Ledger Row, and "SD-1" and "PROPOSED-Influent-Sampler" each name two rows. The pre-commit hook would block any commit of the regenerated file, and CI would fail on PR #6.
- Fix or next action: Carl chose "Narrow the checks.py glob". `is_ledger()` now covers only `*ledger*.csv` under a test bed's `project/` or `lanes/` folder, in its own commit. `prompts/01_bootstrap_guardrails.md` still describes the rule as every `*Ledger*.csv`; update that text when Prompt 1 is next revised.

## 2026-09-30 — Four schema CSVs need uploading to index/ — Closed
- Workstream: Eastsound test bed
- Type: input gap
- Finding: Corrects the 2026-09-30 Open entry "Four schema CSVs need uploading to index/". Ledger_Schema.csv and Requirements_Schema.csv are already in `testbeds/eastsound/index/` (Carl). Only the Audit_Ledger and Spot_Check schemas are missing.
- Fix or next action: Replaced by the next entry.

## 2026-09-30 — Audit_Ledger and Spot_Check schema CSVs need uploading to index/ — Open
- Workstream: Eastsound test bed
- Type: input gap
- Finding: No Audit_Ledger or Spot_Check schema file is in the repo. `testbeds/eastsound/derived/ocr/Spot_Check.csv` uses the column order Carl gave in session (DECISIONS.md, "Spot_Check.csv columns").
- Fix or next action: Carl uploads both to `testbeds/eastsound/index/`. Agents don't create them.

## 2026-09-30 — AGENTS.md and the Bluebeam README still say OCR copies are a comparison column only — Closed
- Workstream: Repo setup
- Type: content conflict
- Finding: Closes the 2026-09-30 Open entry of the same title. Carl approved the proposed wording.
- Fix or next action: Done. AGENTS.md Output standards now read "OCR copies are Inferred only. They may feed tag and quantity leads (method bluebeam-ocr), never a text layer or a Verified read." (269ccdc). `testbeds/eastsound/derived/bluebeam-ocr/README.md` matches (0927ea8).

## 2026-09-30 — OCR lane: a sheet-only quantity match was taken from another item's size — Closed
- Workstream: Eastsound test bed (Prompt 7 OCR lane)
- Type: workflow failure
- Finding: The pre-merge review of PR #6 (5 auditors, 3 skeptics per finding; 1 of 8 findings upheld) found Ledger row 374 (PROPOSED-WWTP-Building-Louver-3x7, "3 ft x 7 ft") marked Verified. The match was "A1.3: matched: quantity 3 FT", but the "3'" came from the text-layer callout "2'x3'" for row 372's louver; the 3'x7' size exists only in the OCR and Bluebeam reads of A1.3. The cause: the quantity match accepted any one value from the Ledger Name, and the foot form had no boundaries. The reported counts were one too high (sheet-only 9 Verified; PROPOSED rows 10 Verified).
- Fix or next action: Fixed in `testbeds/eastsound/tools/extract_drawing_text.py` before the rerun of Tests 8 and 9. A size in the Name ("A ft x B ft", with inches) must match as one string on one line. Every other quantity-unit value in the Name is required. A bare foot value counts as the quantity only when the Name has no other quantity or size, and it can't be taken from inside a size or feet-inch string. Also from the review: a tie now cites the governing Add. 4 page before the base page, and the script's docstring lists the two index inputs.

## 2026-09-30 — The branch update merge a8694d8 dropped main's log entries and failed CI — Closed
- Workstream: Repo setup
- Type: workflow failure
- Finding: `a8694d8` ("Merge branch 'main' into claude/vibrant-davinci-7g3znj", made through GitHub) kept the branch's PROGRESS_LOG.md, ISSUES_LOG.md and DECISIONS.md and dropped main's entries, including "Project_Ledger.csv repeats two Tags". The PR #6 check failed on it, because a `tools/check_exceptions.csv` row came in without its ISSUES_LOG entry. It also failed at a0a19a1, where the ledger rule flagged `derived/ocr/Ledger_Crosswalk.csv`. The range check tests every commit, so no later commit could clear a8694d8.
- Fix or next action: At Carl's direction, a8694d8 was replaced. The branch was pushed with `--force-with-lease` pinned to a8694d8, carrying a merge of main that keeps both sides' log entries. This is a one-off exception to AGENTS.md rule 8, approved by the owner. `tools/checks.py` keeps main's `*_by_CWP*` skip and adds the project/ and lanes/ narrowing.

## 2026-09-30 — Project_Ledger_by_CWP.csv doesn't follow the Ledger schema — Closed
- Workstream: Eastsound test bed
- Type: schema gap
- Finding: Closes the 2026-09-30 Open entry of the same title. Carl: "the ledger check excluding *_by_CWP files". `tools/checks.py` now leaves `*_by_CWP*` files out of the ledger rule, so the CWP view is no longer checked as a Ledger. Its row is removed from `tools/check_exceptions.csv`. The two duplicate Tags it repeats stay tracked under "Project_Ledger.csv repeats two Tags".
- Fix or next action: Done.

## 2026-09-30 — Acceptance harness expected the old --ci data-gate note — Closed
- Workstream: Repo setup
- Type: workflow failure
- Finding: The acceptance-test rerun for the Prompt 1 follow-up gave 32 OK and 1 MISMATCH.
  - Extra test x4, the CI whole-tree step (`--ci --all`), passed with exit 0. The harness was still looking for the old `NOTE | data-gate | - | skipped in CI (--ci)` line.
  - With `--ci`, `tools/checks.py` now reads the DATAGATE_TERMS secret. When the secret is missing it prints `WARN | data-gate | DATAGATE_TERMS | secret not set for this run; data gate not run`.
  - The harness expectation was out of date; checks.py behaved as intended.
- Fix or next action: The harness now expects the WARN line; it is a scratchpad script and is not committed. All tests were rerun.

## 2026-09-30 — Index files cite plans_N extracts that aren't in the library — Closed
- Workstream: Eastsound test bed
- Type: input gap
- Finding: Closes the 2026-09-30 Open entry of the same title. `testbeds/eastsound/index/00_Document_Register_rev2.md` does three things:
  - Rows 31–33 register the three native parts.
  - Rows 5–30 are marked resolved through `index/Plan_Set_Crosswalk.csv`, each with its Part pages.
  - Rows 34–36 register the other native files.
  `div-26-electrical-specs.pdf` (row 2) is settled by decision (DECISIONS.md, "Division 26 extract not uploaded; main spec governs"). `01_Sheet_Index_rev1.md` still cites plans_N pages, which resolve through the same crosswalk.
- Fix or next action: Done. 01 rev2 is tracked in "Index follow-ups after 00 Register rev2".

## 2026-09-30 — 00 Register rev2 needs rows for the three native plan-set parts — Closed
- Workstream: Eastsound test bed
- Type: input gap
- Finding: Closes the 2026-09-30 Open entry of the same title. `testbeds/eastsound/index/00_Document_Register_rev2.md` issued:
  - **Rows 31–33:** Part 1, Part 2 and Part 3.
  - **Rows 34–36:** the native main spec, Add. 4 and QA plan. Bytes, SHA-256 and page counts for all six were recomputed and match `Library_Manifest.csv`.
  - **Rows 5–30:** plans_N rows resolved through `Plan_Set_Crosswalk.csv`.
  - **Row 2:** closed by decision.
  - **S-sheet "OF 96":** recorded.
  rev2 cites both files as its sources; neither was edited. 01 rev2 was not in this session's task.
- Fix or next action: Done for 00. 01 rev2 and the remaining index items are in "Index follow-ups after 00 Register rev2".

## 2026-09-30 — Audit_Ledger and Spot_Check schema CSVs need uploading to index/ — Closed
- Workstream: Eastsound test bed
- Type: input gap
- Finding: Closes the 2026-09-30 Open entry of the same title. At Carl's direction in this session (DECISIONS.md, "The Setup role creates the Audit_Ledger and Spot_Check schema CSVs"), the Setup role created two header-only files in `testbeds/eastsound/index/`, in the column order Carl gave:
  - `Audit_Ledger_Schema.csv` (21 columns).
  - `Spot_Check_Schema.csv` (12 columns).
  Both are ASCII with no BOM and one LF-terminated header line, the same as `Ledger_Schema.csv`. `Spot_Check_Schema.csv` matches the first 12 columns of `derived/ocr/Spot_Check.csv`.
- Fix or next action: Done.

## 2026-09-30 — Index follow-ups after 00 Register rev2 — Open
- Workstream: Eastsound test bed
- Type: content conflict
- Finding: 00 rev2 changed only what its task named, so these index items still disagree with it:
  - `01_Sheet_Index_rev1.md` still logs S1.1–S4.1 as "OF 98" (open item 10; rows 56–61). The native Part 3 reads "OF 96" (00 rev2, "S-sheet page total"). The Add. 4 pp.9–10 reissues were not rechecked.
  - 01 rev1 still lists 10 sheets as not in library. All ten are in Part 1 and Part 3 (00 rev2 rows 31 and 33).
  - 00 rev2 still carries these rev1 lines:
    - The Referenced-documents row "10 drawing sheets … Assigned — unavailable".
    - The Stored-copy line "Native PDF metadata was not available".
    - "image-only" in rows 18, 19 and 24 (see "Index and library notes call the 9 no-text-layer sheets 'image-only'").
  - `Library_Manifest.csv` "00 Register Row" still reads "none" for the three parts. They are now rows 31–33; the other natives are rows 34–36.
- Fix or next action: Setup issues 01 rev2 and, on Carl's OK, 00 rev3 and a manifest update. Before that, a person or the Setup role checks the native Add. 4 pp.9–10 title blocks.

## 2026-09-30 — Graph build inside the repo stamps the git commit, so rebuilds differ by commit — Open
- Workstream: Eastsound test bed, graph build (Prompt 3)
- Type: workflow failure
- Finding: Two clean builds outside the repo gave byte-identical graph.json, graph.html and GRAPH_REPORT.md. The build in `testbeds/eastsound/graph/` did not match them.
  - graphify 0.9.72 adds `built_at_commit` (the output of `git rev-parse HEAD`) to graph.json when the output folder is inside a git checkout. `graphify cluster-only` stamps it again, and it adds a "Graph Freshness" section to GRAPH_REPORT.md.
  - graph.html was identical. Nothing else differed.
  - Effect: the same Ledger and script give a different graph.json at every commit, and a copy without `.git` gives no stamp at all. That breaks "rebuilds identically in any runtime".
- Fix or next action: Run both build commands with `GIT_DIR` set to a path that doesn't exist (for example `GIT_DIR=no-git`). git then reports no repository and graphify leaves the stamp out. graphify has no option for this. Document it in `testbeds/eastsound/graph/README.md`, rebuild, and rerun acceptance test 6 against the committed build.

## 2026-09-30 — Graph build inside the repo stamps the git commit, so rebuilds differ by commit — Closed
- Workstream: Eastsound test bed, graph build (Prompt 3)
- Type: workflow failure
- Finding: Closes the Open entry of the same title. Both build commands now run with `GIT_DIR=no-git`, and `testbeds/eastsound/graph/README.md` gives the full commands.
  - The build in the repo and two clean builds outside it match byte for byte: graph.json, graph.html and GRAPH_REPORT.md.
  - graph.json has no `built_at_commit` key.
- Fix or next action: Done.

## 2026-09-30 — Twelve Project Ledger rows are tagged stronger than their Bid Item fact — Open
- Workstream: Eastsound test bed
- Type: content conflict
- Finding: Twelve Electrical & Controls rows are tagged Verified-Visual, but their Bid Item cell reads "1 (equipment, Inferred per 04); 6 (power and control)".
  - The rows: lines 288–291 (IP-1 to IP-4), 313 (DW-1), 314–315 (WP-1, WP-2), 316 (SD-1), 318 (PROPOSED-WAS-Solenoid-Valves), 319 (PROPOSED-Polymer-Feed-Pump), 320 (PROPOSED-Hypochlorite-Feed-Pump) and 341 (PROPOSED-2W-Isolation-Valve-Solenoid).
  - AGENTS.md says a row's tag is the weakest tag of the facts in it, so these rows should read Inferred.
  - Found in Prompt 3 step 2. The Ledger was not edited, per Carl.
  - In the graph, Bid Item is an item attribute, so no link carries the overstated level. Each item node carries the row's tag as written.
- Fix or next action: Merge corrects the tag in a new Ledger revision. The graph picks it up on the next rebuild.

## 2026-09-30 — Ledger Wiki Note "CQA Plan" has no Project Wiki note — Open
- Workstream: Eastsound test bed
- Type: content conflict
- Finding: 159 of the 160 names in the Project Ledger's Wiki Note(s) column match a `### <name> — ` heading in `project/01_Project_Wiki/Project_Wiki.md`. "CQA Plan" (12 rows) matches none. The graph keeps it as the node "Wiki note CQA Plan", which points at no note.
- Fix or next action: Merge either adds a CQA Plan note to the Project Wiki or points those 12 rows at an existing note.

## 2026-09-30 — The same_tag link lets graph paths jump between the two SD-1 items — Open
- Workstream: Eastsound test bed, graph build (Prompt 3)
- Type: design gap
- Finding: Rule 9 keys the two SD-1 rows as `SD-1 [L74]` (storm drain) and `SD-1 [L316]` (sludge pump), joined by one AMBIGUOUS `same_tag` link.
  - `graphify path --undirected` treats that link like any other. The trace from "Add. 4 p.2 33 41 00 ¶2.02 F" to "MCC" ran storm drain → same_tag → sludge pump. That hop doesn't reflect how the work connects.
  - The link is labeled AMBIGUOUS, and `testbeds/eastsound/graph/README.md` warns about it.
- Fix or next action: It clears when Merge gives one SD-1 item its own Tag (entry "Project_Ledger.csv repeats two Tags"). Carl may instead drop the same_tag link from the script.

## 2026-09-30 — Prompt 3 as written doesn't match the repo after the reorg — Open
- Workstream: Eastsound test bed, graph build (Prompt 3)
- Type: workflow failure
- Finding: Found in Prompt 3 step 2 and run as Carl directed this session:
  - `prompts/03_build_graph.md` names `tools/ledger_to_graph.py` and `testbeds/eastsound/project/Project_Ledger.csv`. The files are at `testbeds/eastsound/tools/ledger_to_graph.py` and `testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv`.
  - Its `--out testbeds/eastsound` puts the outputs outside `graph/`, which AGENTS.md names as the graph folder.
  - Test 8 fails if `.graphifyignore` lists only `library/`: `graphify extract` finds 2 papers, the Bluebeam OCR PDFs in `derived/bluebeam-ocr/`.
  - Unsetting the four named keys isn't enough. graphify also picks a backend from `AWS_PROFILE`, `AWS_REGION` or `AWS_DEFAULT_REGION` (Bedrock) and from `OLLAMA_HOST` (Ollama), and this container has AWS credentials set.
- Fix or next action: This session used the real paths, `--out testbeds/eastsound/graph`, `.graphifyignore` listing `library/` and `derived/bluebeam-ocr/`, and `env -i` for every graph command. `prompts/03_build_graph.md` is outside this session's folder and was not edited; update it before the prompt is reused.

## 2026-09-30 — The same_tag link lets graph paths jump between the two SD-1 items — Closed
- Workstream: Eastsound test bed, graph build (Prompt 3)
- Type: design gap
- Finding: Closes the Open entry of the same title. Carl: "Drop the 'same tag' link between the two SD-1 rows. It creates false path traces, and the Ledger ID from Prompt 9 will replace it."
  - `testbeds/eastsound/tools/ledger_to_graph.py` now skips Tags in its `NO_SAME_TAG` list, which holds SD-1.
  - The rows stay keyed `SD-1 [L74]` and `SD-1 [L316]`, with no link between them.
  - The PROPOSED-Influent-Sampler rows (lines 321 and 419, one item entered by two lanes) keep their same_tag link.
  - Rebuilt graph: 791 nodes, 3,113 links, 1 same_tag link.
  - The trace from "Add. 4 p.2 33 41 00 ¶2.02 F" to "MCC" no longer passes through the SD-1 rows. It now runs 7 hops over sheet, note and addendum links.
- Fix or next action: Done. When Prompt 9 adds the Ledger ID column, key items by that ID and remove `NO_SAME_TAG`. The two SD-1 rows still need their Tag fix from Merge (entry "Project_Ledger.csv repeats two Tags").

## 2026-09-30 — Index follow-ups after 00 Register rev2 — Closed
- Workstream: Eastsound test bed
- Type: content conflict
- Finding: Closes the 2026-09-30 Open entry of the same title.
  - `testbeds/eastsound/index/01_Sheet_Index_rev2.md`:
    - S1.1–S4.1 read "OF 96". The native Part 3 title blocks and the Add. 4 pp.9–10 reissues both read it.
    - The 10 sheets are indexed from native Part 1 pp.10, 14–16, 20, 22, 25 and Part 3 pp.1–3, citing `Plan_Set_Crosswalk.csv`. Each title block's "N OF 96" was read in the native text layer (Verified).
    - C3.3, C3.4, C7.3 and the S sheets are "no text layer (vector drawing)". `pdftotext` and `pdfimages` on the native files find no text layer and no page-size raster.
  - `00_Document_Register_rev3.md` fixes the four stale rev1 lines: the 10-sheets row, the metadata note, "image-only" in rows 18, 19 and 24, and the Totals line.
  - `Library_Manifest.csv` "00 Register Row" now reads 31–36.
  - Add. 4 pp.9–10 on the native file: S2.3 "59 OF 96" and S4.1 "61 OF 96" (Verified-Visual).
  - The 01 and 00 parts of "Index and library notes call the 9 no-text-layer sheets 'image-only'" are done. That entry stays Open for `library/Plan_Set_Parts.md`, which the build session owns.
- Fix or next action: Done. Two new items follow: the Read Method for the 10 sheets, and the Add. 4 revision entries.

## 2026-09-30 — Read Method for the 10 native-only sheets is provisional — Open
- Workstream: Eastsound test bed
- Type: design gap
- Finding: `01_Sheet_Index_rev2.md` sets C0.3, C0.7, C1.1, C1.2, C2.1, C2.3, C2.6, C7.7, C7.8 and C7.9 to "Visual (rev2, provisional)".
  - Their body chars (text layer minus title block, decision C) were not measured on the native file.
  - The rev1 counts came from the Claude Project copies, so the method isn't reproducible here as written.
  - Total native text-layer characters are 268–695, title block included (01 rev2, "Native-only pages").
- Fix or next action: Setup measures body chars on the native text layer with a stated title-block rule, then sets Text or Visual in a 01 rev3. Until then lanes run a visual pass on these 10.

## 2026-09-30 — Add. 4 S-sheet reissues carry a revision entry; 01 item 12 says they don't — Open
- Workstream: Eastsound test bed
- Type: content conflict
- Finding: On the native Add. 4, pp.9 (S2.3) and 10 (S4.1) each show revision 3, "Blower Building", TH, 2/8/23, in the revision block (Verified-Visual; read 2026-09-30). The title-block date stays 10-15-2021. Two index lines disagree:
  - `01_Sheet_Index_rev2.md` item 12 (unchanged from rev1): the reissued pages have "no Add. 4 revision entry".
  - `00_Document_Register_rev3.md` "Per-sheet revision blocks": "the title block can't show supersession".
  Add. 4 pp.4–8 (A1.1, A1.2, C6.4, C1.3, C1.6A) were not checked.
- Fix or next action: On Carl's OK, Setup checks the revision blocks on native Add. 4 pp.4–8. Then it corrects 01 item 12 and the 00 line in the next revisions.
## 2026-09-30 — Prompt 9: two Summary.md defects caught in review before commit — Closed
- Workstream: Eastsound test bed (Prompt 9 reconciliation)
- Type: workflow failure
- Finding: Reviewing the first full run of `testbeds/eastsound/tools/build_reconciliation.py` turned up two defects in Summary.md:
  - The generator RFI line took the first update row for L-0242. That was a cited-not-found row (E7.3), not the Division 26 Notes proposal.
  - The segment-sum check allowed three callouts. It listed 21 + 23 + 39 = 83 LF for SD-3, although 21 and 23 LF are tied to other rows.
- Fix or next action: Done before commit. The RFI line selects the Division 26 Notes proposal and quotes its native text-layer reads and boxes. Segment sums use pairs only. The outputs were regenerated, and the determinism check was run afterwards.

## 2026-09-30 — Ledger Tag uniqueness (checks.py, ledger_to_graph.py) conflicts with decision A — Open
- Workstream: Repo setup
- Type: design gap
- Finding: Decision A makes the Ledger ID the key and keeps tags as printed, so two rows may share a Tag (SD-1, L-0073 and L-0315). Two tools still assume a unique Tag:
  - `tools/checks.py` requires unique Tags in every project/ and lanes/ Ledger. Project_Ledger.csv passes only through its `tools/check_exceptions.csv` row.
  - `testbeds/eastsound/tools/ledger_to_graph.py` uses the Tag as the node ID, so the two SD-1 rows become one graph node.
  - Prompt 9's proposal to give L-0337 and L-0338 the printed tags "Hot Box #1" and "Hot Box #2" would add two more shared Tags.
- Fix or next action: Proposed in `testbeds/eastsound/derived/reconciliation/Ledger_Schema_rev1_Proposal.md`, not made:
  - checks.py checks a unique Ledger ID instead of a unique Tag. This goes in its own commit, when a person asks.
  - ledger_to_graph.py keys nodes on Ledger ID.
  - Setup issues Ledger_Schema.csv rev1.

## 2026-09-30 — Prompt 9 test-bed findings for the Merge Issues Log — Open
- Workstream: Eastsound test bed
- Type: content conflict
- Finding: Prompt 9 (`testbeds/eastsound/derived/reconciliation/Summary.md`) found five test-bed items. Under the lane's write scope they can't go in the Merge Issues Log under `project/`:
  - **Generator rating.** E1.1 and E6.1 read 125 kW in the native text layer. 26 32 13 ¶2.03 C.1 (main spec p.326) requires not less than 150.0 kW standby. RFI drafted.
  - **Chain link fence.** C2.1 keyed notes 6 (149 LF) and 8 (134 LF) have no Ledger row. L-0088 (126 LF) cites C2.1 and C2.5. L-0018 (149 LF, remove) cites C0.5 keyed note 16.
  - **Hot Box duplicates.** L-0337 and L-0338 (Electrical & Controls) carry the printed tags of L-0057 and L-0058 (Civil & Site).
  - **Earthwork.** C0.2 states cut 3382 CY and fill 1598 CY; the Ledger has no earthwork row.
  - **Panel schedules.** The E6.2 and E2.2 schedules are embedded images, so any Ledger fact from them is at best Verified-Visual.
- Fix or next action: Carl decides the fence and the RFI. Merge carries all five into the test bed's Issues Log and resolves them in the next Ledger revision.

## 2026-09-30 — Ledger Tag uniqueness: graph part corrected after PR #9 — Open
- Workstream: Repo setup
- Type: design gap
- Finding: Corrects the 2026-09-30 Open entry "Ledger Tag uniqueness (checks.py, ledger_to_graph.py) conflicts with decision A".
  - That entry said `ledger_to_graph.py` "uses the Tag as the node ID, so the two SD-1 rows become one graph node". This was true at the branch base (b8e1313).
  - It is no longer true after PR #9 (ce488d5). A Tag on more than one row is now keyed `<Tag> [L<line>]`, so `SD-1 [L74]` and `SD-1 [L316]` are separate nodes with no link between them (`NO_SAME_TAG`).
  - The checks.py part of that entry stands.
- Fix or next action: Still open, as proposed in `testbeds/eastsound/derived/reconciliation/Ledger_Schema_rev1_Proposal.md` (impact row updated in 599a869):
  - checks.py checks a unique Ledger ID instead of a unique Tag.
  - ledger_to_graph.py keys every node on Ledger ID and drops `NO_SAME_TAG`.

## 2026-09-30 — Wiki parse: three matching defects caught in review before commit — Closed
- Workstream: Eastsound test bed, Wiki parse (`testbeds/eastsound/tools/parse_wiki.py`)
- Type: workflow failure
- Finding: Test runs into the scratchpad showed three defects:
  - Splitting tag lines at every ", " broke lists apart: "Hot Box #1, #2", "Pipe IDs 1–26", "Appendices B, C" and "Add. 4 p.1, Clarification 5". 39 printed-tag Ledger rows (the Pipe IDs and Buried Valve IDs) matched no note.
  - The hyphen-variant rule matched the seismic value "SD1 0.51g" (S1.1, 13 12 20) to SD-1.
  - A bare "F1" or "F4" on the 2W pump station notes (C4.2, E4.3, E7.3) resolved to "F1 (Influent Pump Station)", the only Ledger row with that printed form.
- Fix or next action: Fixed before commit.
  - A comma followed by a number, "#n", an appendix letter or "Clarification" no longer splits an item. Lists expand only when every member is a Ledger tag.
  - A variant is skipped when a number follows it.
  - A form that exists only with a qualifier needs the Ledger row to name the note, or the qualifier in the text. Otherwise Ledger ID is blank and Basis says why (12 links).

## 2026-09-30 — Wiki parse findings for Merge — Open
- Workstream: Eastsound test bed
- Type: content conflict
- Finding: From `testbeds/eastsound/derived/wiki/Parse_Report.md`:
  - **Ledger pointers.** 114 equipment-tag links match a Ledger row whose Wiki Note(s) does not name that note. Each has the Basis "the Ledger row does not cite this note" in Wiki_Links.csv.
  - **Tag not in any note.** L-0190 "S1–S2 [Aerobic Digester]" is the one printed-tag row whose tag no note writes.
  - **Same-name PROPOSED rows across lanes.** L-0101 and L-0148 (influent sample sump), L-0320 and L-0418 (influent sampler). Also L-0110 (contractor dewatering) and L-0427 (sludge dewatering), both "dewatering system". Links to these carry both IDs.
  - **Qualified tags with no row.** The 2W pump station notes print floats F1 and F4, and the Ledger has F1 and F4 only for the Influent Pump Station. 26 51 19 prints fixture types L1, L2 and X1 with no building named.
  - **Note ID.** The QA plan note's Document ID reads "CQA Plan" and its heading reads "QA plan". This is the same gap as the Open entry "Ledger Wiki Note 'CQA Plan' has no Project Wiki note".
- Fix or next action: Merge reviews these in the next Ledger revision. Nothing in the Ledger or Wiki was changed.

## 2026-09-30 — AGENTS.md Layout doesn't list derived/wiki/ — Open
- Workstream: Repo setup
- Type: design gap
- Finding: This session added `testbeds/eastsound/derived/wiki/` (Wiki parse outputs, written by `testbeds/eastsound/tools/parse_wiki.py`). The AGENTS.md Layout lists `derived/reconciliation/` but not this folder. This session's write scope doesn't include AGENTS.md.
- Fix or next action: On Carl's OK, add one Layout line under `derived/`: `wiki/  Wiki note and link tables parsed from project/01_Project_Wiki (derived; not a source)`.

## 2026-09-30 — Open-items build: two defects caught before the first output — Closed
- Workstream: Eastsound test bed (open-items list)
- Type: workflow failure
- Finding: The first two runs of `testbeds/eastsound/tools/build_open_items.py` stopped before writing anything:
  - The Ledger_ID_Map tie-out paired each map row with the wrong file's row (KeyError 'Ledger Row').
  - The S2.3/S4.1 anchor quoted "Blower Building" as the Merge Issues Log shows it, but `Issues_Log.csv` stores the quotes doubled, so the text check missed it.
- Fix or next action: Done. The tie-out pairs each map row with its Ledger row. The anchor now uses text with no quotes ("the S2.3 and S4.1 reissues show revision 3"). Both were fixed before any output was written.

## 2026-09-30 — Merge Issues Log still lists the 10 native-only sheets as missing — Open
- Workstream: Eastsound test bed
- Type: content conflict
- Finding: `testbeds/eastsound/project/03_Exceptions_and_Issues/Issues_Log.csv` #8 is still Open: "10 drawing sheets not in the library". The Closed entry "Six sheets exist only in the Bluebeam OCR copies" says all 10 are now in the native Part 1 and Part 3. The same stale state is in:
  - Merge #56 (C0.3: "Native copy of C0.3") and #57 (C1.1 and C1.2 "missing");
  - `Project_Known_Issues.md` Part B CS-01 ("C2.1/C2.3 (unavailable) may show it") and CS-19 ("C1.1 (unavailable) may show it").
  `derived/issues/Open_Items.csv` leaves #8 out and notes the native sheets on #56 and #57.
- Fix or next action: Merge closes #8 and updates the other four in its next revision. The C0.3, C1.1, C1.2, C2.1 and C2.3 questions can now be read on the native sheets.

## 2026-09-30 — AGENTS.md Layout doesn't list derived/issues/ — Open
- Workstream: Repo setup
- Type: design gap
- Finding: This session added `testbeds/eastsound/derived/issues/` (Open_Items.csv, Open_Items_Summary.md), built by `testbeds/eastsound/tools/build_open_items.py`, at Carl's request. The AGENTS.md Layout lists `derived/reconciliation/` but not `derived/issues/`. AGENTS.md was outside this session's write scope.
- Fix or next action: On Carl's request, add one Layout line under `derived/` in its own commit, for example: `issues/  open-items list built from reconciliation/, project/03_Exceptions_and_Issues/ and ISSUES_LOG.md (list only; nothing applied)`.
