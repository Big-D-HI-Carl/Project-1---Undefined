# Progress Log

Append-only. One entry per session, in the format in AGENTS.md. Never edit or delete a past entry.

## 2026-09-30 — Bluebeam OCR copies moved to derived/
- Runtime: Claude Code
- Commits: b96d1a9..1394937, plus this log commit
- Done:
  - Moved the two Bluebeam OCR copies, unchanged, from the repo root to `testbeds/eastsound/derived/bluebeam-ocr/`.
  - Added `testbeds/eastsound/derived/bluebeam-ocr/README.md`. It records:
    - source file `eswd-wwtp-upgrade-ph1-11x17-plans.pdf` (Inferred);
    - OCR settings "Not stated" (none are stored in the files), plus the observed hidden OCR layer (Inferred);
    - date 2026-09-30;
    - Part 1 = 48 pages, G0.1 "1 OF 96" to C7.6 "48 OF 96", set pp.1–48;
    - Part 2 = 48 pages, C7.7 "49 OF 96" to E10.3 "96 OF 96", set pp.49–96;
    - OCR-only pages and sheets not in the library;
    - SHA-256 fingerprints.
  - Added the OCR rule and the `derived/` layout line to `AGENTS.md`.
- Tests:
  - `git diff --cached -M --name-status` → R100 for both PDFs.
  - `sha256sum -c` on the new paths → pass, 2/2.
  - Page-tree read on the new paths (stdlib script, not committed) → 48 + 48 pages.
  - `python tools/checks.py --all` / `--staged` → not run: `tools/checks.py` doesn't exist (Prompt 1 not run).
- Failures and fixes:
  - The container has no PDF tools (no pdfinfo, no pypdf). Fix: read the metadata, page trees and title-block text with a stdlib-only script in the session scratchpad.
  - The checks can't run. This is logged in ISSUES_LOG.md ("Uploaded repo tree is flat").
- Next:
  - Lay out the tree and restore `.gitattributes`, then run Prompt 1.
  - Supply the Bluebeam OCR settings for the README.
  - Add native copies of C0.7, C1.1, C1.2, C7.7, C7.8 and C7.9 to the library.

## 2026-09-30 — Inbox sort and root layout
- Runtime: Claude Code
- Commits: dae20bd..a9aa5c0, plus this log commit
- Done:
  - **Renames (first commit):** the Merge rev2 README moved to `testbeds/eastsound/project/README.md`. Then README (2).md → README.md, download → .gitattributes, download (1) → .gitignore, settings.json → .claude/settings.json. Blob IDs and SHA-256 are identical before and after.
  - **Library/ inbox → `testbeds/eastsound/library/`** (6 PDFs; `Library/` removed):
    - The main spec, Add. 4 and the CQA plan match Register rows 1, 3 and 4.
    - The three plan-set parts (27 + 21 + 48 pages) don't match any Register name.
  - **Crosswalk note:** added `testbeds/eastsound/library/Plan_Set_Parts.md`.
    - Part 1 = set pp.1–27 (G0.1–C3.2), Part 2 = 28–48 (C3.3–C7.6), Part 3 = 49–96 (C7.7–E10.3).
    - It has one row per file page: set page, sheet, how the sheet is known, and the plans_N page.
    - 87 pages are Verified from the native title block; the 9 image-only pages are Inferred.
  - **Root folded in:**
    - index/ 7, process/ 6, prompts/ 5, tools/ 1, project/ 28.
    - lanes/<lane>/as-delivered/: Civil 149, Process & Mechanical 152, Electrical & Controls 237, Structural & Building 66, Contract & General 90. Each package's own structure is restored (Components/, Civil_and_Site_Components/, the doubled upload folders dropped) so its relative links resolve.
    - `testbeds/eastsound/_unsorted/`: a 40-file byte-identical duplicate of the C&G page notes, with a README giving the reason.
  - **OCR README:** updated the "Library status" and "Not in library/" lines in `testbeds/eastsound/derived/bluebeam-ocr/README.md`.
- Tests:
  - `git show --name-status -M` on each move commit → R100 only. The exception is the first commit: there, README.md shows as a modify/delete/add pair by path, with its blob unchanged.
  - Baseline blob map vs the final tree → 801 baseline files, 792 moved, 0 mismatches. The only new or edited files are Plan_Set_Parts.md, `_unsorted/README.md` and the OCR README.
  - Relative .md link check over the lane packages → 3,612 resolved, 0 broken (1,517 broken before).
  - Native title-block read vs `01_Sheet_Index_rev1.md` → 87 of 96 match, 0 mismatches, 9 image-only.
  - `python tools/checks.py --all` / `--staged` → not run: the file doesn't exist (Prompt 1 not run).
- Failures and fixes:
  - The first `git mv` of the Merge README failed because `testbeds/eastsound/project/` didn't exist. Fix: created it and reran.
  - The scratch PDF reader missed page contents stored as an indirect array. Fix: resolved the array; the parts' title blocks then read normally.
  - The first crosswalk draft took the first sheet-like text on each page, which gave the C7.2 callouts on set pp.31, 34 and 36. Fix: take the sheet number immediately before the title-block labels. Now C4.1, C5.1 and C5.3, matching the Sheet Index.
  - The verification script kept a newline on baseline paths, so every lookup missed. Fix: stripped the newline and reran → 0 mismatches.
  - `git mv` left empty folders at the root. Fix: removed only the folders that held no files.
- Next:
  - Upload `prompts/05_repo_cleanup.md` and check its Step 3 against this layout.
  - Still missing:
    - **Prompts:** 06, Prompt_Workflow_Receipt_rev1, and Composer Prompt_1–6 (prompts/history/).
    - **Derived copies:** Missing_Pages_Page_001–004.png (derived/project-copies/).
    - **Index:** the Setup resplit list.
    - **Lanes:** the 20 canonical lane files (Wiki, Ledger, Issues, Known Issues × 5) and the build-script zips.
    - **Project:** the Merge build scripts.
    - **Process:** the redline .docx, and the original Sample_Project_Concurrent_Lane_Ultraplan.docx.
    - **Library:** div-26-electrical-specs.pdf and the plans_N extracts (or Register rows for the three parts); Addenda 1–3.
    - **Test-bed README:** `testbeds/eastsound/README.md`, whose kit text survives only in history (`8039650:README.md`).
  - Then run Prompt 1.

## 2026-09-30 — Layout rule and test-bed README
- Runtime: Claude Code
- Commits: 226024e..e0830b2, plus this log commit
- Done:
  - `AGENTS.md` Layout now lists `lanes/<lane>/as-delivered/` and `testbeds/eastsound/_unsorted/`.
  - Restored `testbeds/eastsound/README.md` from `8039650:README.md`, the kit's test-bed README, which had been overwritten at the root in 92585e6. This removes it from the missing list in the "Inbox sort and root layout" entry.
- Tests:
  - `git diff AGENTS.md` → 2 added lines, 0 removed.
  - Restored README blob → e894b11d, matching `8039650:README.md`.
  - `python tools/checks.py` → not run: the file doesn't exist (Prompt 1 not run).
- Failures and fixes: none
- Next:
  - On a person's OK, restore the three lane package READMEs found in history (ISSUES_LOG, "Three lane package READMEs were overwritten …").
  - Then the missing-inputs list and Prompt 1.

## 2026-09-30 — Repo cleanup (prompt 05): READMEs, library manifest and crosswalk, rulebook fixes
- Runtime: Claude Code
- Commits: 39ef888..28d710e, plus this log commit (branch `claude/charming-lamport-it1dac`, fast-forwarded to 9fec0a2 first)
- Done:
  - **Steps 0–1:** visibility check (public; Carl: "public repo is fine"); content-based mapping of all 792 files at 92585e6, checked by script and six verifier/skeptic agent pairs; layout conflicts listed. `git fetch` then showed the `claude/sharp-thompson-5q5d1f` session had already applied the moves (PRs #1, #2), so this session made none (ISSUES_LOG, "Two sessions ran the same reorg step").
  - **Lane READMEs:** restored byte for byte from 7fba2f5, 0b488b9 and 5f76965 into the Electrical & Controls, Civil & Site and Process & Mechanical `as-delivered/` packages.
  - **Prompts and READMEs:** `prompts/05_repo_cleanup.md` added; root README.md gets one pointer line to `testbeds/eastsound/`; `testbeds/eastsound/README.md` keeps the kit text and gains a Folders section.
  - **Library:** `testbeds/eastsound/index/Library_Manifest.csv` (6 native PDFs: path, bytes, SHA-256, page count, source URL "Not stated", Register row, upload commit); `testbeds/eastsound/index/Plan_Set_Crosswalk.csv` (99 rows, plans_N page → set page → native part page); pointer added to `library/Plan_Set_Parts.md`.
  - **Report:** `testbeds/eastsound/process/Repo_Reorg_Report_2026-09-30.md` (final mapping, missing files, `_unsorted/`, layout conflicts, library findings).
  - **Step 6:** AGENTS.md rule 5 (`.docx` only as a reading copy in process/) and Layout owners for `derived/` and `_unsorted/`; Prompt 1 expects an organized kit, drops the private-repo stop, records "The repo stays public." and adds the library-manifest check (acceptance test 2 updated to match).
- Tests:
  - Blob map 92585e6 → HEAD → 792 of 792 files present with unchanged blobs.
  - Relative .md link check, whole repo → 4,022 resolve, 0 broken.
  - Crosswalk vs native title blocks (pypdf 5.1.0 text layer for 90 rows; PyMuPDF 1.28.2 render for the 9 image-only pages, read visually) → 99 rows, 0 mismatches; vs `Plan_Set_Parts.md` → 0 differences.
  - Page counts, pypdf vs PyMuPDF → agree on 6 of 6; main spec 645, Add. 4 13, CQA plan 23 match the 00 Register.
  - Restored READMEs → blob IDs equal the history blobs, 3 of 3.
  - `python tools/checks.py --all` / `--staged` → not run: `tools/checks.py` doesn't exist (Prompt 1 not run).
- Failures and fixes:
  - `git fetch` found the other session's merged reorg. Fix: stopped and reported; Carl confirmed that session closed; work continued on top of 9fec0a2.
  - `git log --follow --diff-filter=A` named the wrong upload commits for the library PDFs (rename pairing). Fix: matched each file's blob against the four upload commits.
  - The title-block regex missed the C0.2 set page (no line break before "9OF"). Fix: allowed a letter before the number and reran.
  - Nine native pages are image-only, so the text layer can't confirm them. Fix: rendered each title block with PyMuPDF in a scratch venv (not committed) and read it; tagged Verified-Visual.
- Next:
  - Carl: decide the proposed AGENTS.md line "one session per step; check open sessions before starting one".
  - Setup: 00 Register rev2 (rows for the three parts; plans_N rows via the crosswalk; row 2 closed) and 01 rev2 (10 sheets now available; S-sheet "OF 96").
  - Revise Graph_Transfer_Ultraplan §6 Step 4's fingerprint check for the native files.
  - Upload the 20 lane files, the Composer prompts and Prompt_Workflow_Receipt_rev1.md, and Addenda 1–3.
  - Run Prompt 1 (`prompts/01_bootstrap_guardrails.md`).

## 2026-09-30 — OCR lane (Prompt 7 rev1): drawing text for the Ledger and MTO cross-reference
- Runtime: Claude Code
- Commits: c62c219..cdfa74c (Step 1 and the Gate A proposal, merged to main by Carl as PR #4), then 06af9c9..a0a19a1 plus this log commit on `claude/vibrant-davinci-7g3znj`, rebased onto 67e82f3 for a new PR.
- Done:
  - **Step 0:** stopped because PR #2 was open. Resumed once Carl merged it (9fec0a2). Ledger: 447 rows, 123 Unresolved. Drawings: three native parts plus Add. 4 (13 pp.). No master MTO exists, so outputs are keyed to join one later.
  - **Tools:**
    - `tools/extract_drawing_text.py` has four stages: `pages`, `forms`, `hits`, `report`.
    - Text-layer words carry their render mode, with rotation applied and sub-1 pt words dropped.
    - Tesseract reads every page at 400 dpi, upright and rotated 90°, merged by overlap with the higher confidence kept. The text layer wins over OCR.
    - The Bluebeam block is the mode-3 words from the OCR copies minus native matches.
    - Title blocks come from the SHEET label nearest the bottom-right corner, plus a rotated title-strip OCR pass (200 and 300 dpi, psm 11) where the text layer has none.
    - Parallel workers and sorted output; no LLM calls.
  - **Pins:** `requirements.txt` pins PyMuPDF 1.28.2, pytesseract 0.3.13, Pillow 12.3.0 and packaging 24.0. Tesseract 5.3.4 comes from apt.
  - **Outputs** in `testbeds/eastsound/derived/ocr/`:
    - 103 page files: 96 set pages and 7 Add. 4 pages.
    - Sheet_Map (103 rows), Tag_Search_Forms (447), Tag_Hits (839: 604 assigned, 234 off-citation short form, 1 with no "(E)" on its line), Quantity_Hits (1,903 leads, 161 in keyed notes), Ledger_Crosswalk (447), Unmatched_Tags (401), Spot_Check (25).
    - Findings.md, and a README.md that includes the stopword and generic-noun lists for review.
    - 33 MB in all; the largest file is 2.0 MB (`pages/056_S1.1.json`), so nothing is split.
  - **Gate A:** Carl approved with changes; each change is quoted in DECISIONS.md.
    - PROPOSED anchors under his rule: 250 Verified, 206 Inferred, 99 Unresolved (keyed notes 0 / 13 / 9; "sheet only" anchors 232 / 184 / 74).
    - PROPOSED rows by weakest anchor: 61 Verified, 116 Inferred, 135 Unresolved; 78 rows cite no sheet number.
    - Printed tags found on a cited sheet: 61 of 96 in the text layer alone, 81 of 96 by any method (exact).
  - **Findings:** C2.1's fence reads are 149 LF (keyed note 6) and 134 LF (keyed note 8), OCR only, stated and not reconciled with Ledger rows 19 and 89. The S sheets read "OF 96", agreeing (Inferred) with the Verified-Visual read in the ISSUES_LOG entry "00 Register rev2 needs rows…".
  - **Nothing else edited:** no Ledger, MTO, Wiki, index or source file.
- Tests:

  | # | Test | Expected | Actual | Result |
  |---|---|---|---|---|
  | 1 | Page files / Sheet_Map rows | 103 / 103 | 103 / 103 | pass |
  | 2 | Title-block sheet = 01 | ≥ 90 of 96 | 96 of 96; Add. 4 7 of 7; titles 103 of 103 | pass |
  | 3 | Set pp.14–16, 49–51 | C0.7, C1.1, C1.2, C7.7, C7.8, C7.9 | all 6 read in the text layer | pass |
  | 4 | S2.1 (set p.57) > 0 words | > 0 | Tesseract 568, Bluebeam 494 | pass |
  | 5 | C2.1 149 LF and 134 LF; SD-3 on C2.3 | found, with boxes | 149 LF: OCR + Bluebeam, KN 6; 134 LF: OCR + Bluebeam, KN 8 (Inferred); SD-3: text layer at 2 spots (Verified) | pass |
  | 6 | Spot check, 5 per discipline | 25 rows, crops shown | 25 rows (C/E/S/A/G × 5), seed 20260930, crops shown in chat and not committed, Human Result blank | pass (awaiting Carl's marks) |
  | 7 | Every Ledger row in the crosswalk | 447 | 447, in Ledger order | pass |
  | 8 | Determinism | byte-identical | two clean runs (no cache) and the committed files: 112 of 112 SHA-256 identical; the post-rebase run is also identical | pass |
  | 9 | `git diff --stat origin/main...HEAD` | lane folders only | `derived/ocr/` (111), `tools/extract_drawing_text.py`, ISSUES_LOG.md, plus this commit's PROGRESS_LOG.md and DECISIONS.md | pass |

  - Full clean run wall time at `--jobs 4` on 4 CPUs, no cache: 588 s and 594 s (547 s of it in the page stage). With the development cache: 122 s.
  - `python tools/checks.py --all` / `--staged` → not run: `tools/checks.py` doesn't exist (Prompt 1 not run).
- Failures and fixes:
  - Step 1 calibration failures are logged in ISSUES_LOG ("OCR lane Step 1: calibration failures fixed before the full run"). They were written at Gate A, not before each rerun.
  - The first timed full run never started because `/usr/bin/time` is missing. Fix: time with the shell `date`.
  - The Gate A preview turned up four problems, each fixed before the committed run:
    - Keyed-note headings matched sentences (C0.7, E0.1). Fix: the heading must stand alone.
    - "6' CHAIN LINK" still yielded a FT lead, because OCR split the line. Fix: the next word is checked by position.
    - Det. anchors matched only the title line. Fix: each detail gets a region.
    - Nouns included -ED participles. Fix: dropped.
  - Heredoc quoting escaped the quotes in the new DECISIONS entries. Fixed before commit; no committed line changed.
  - PR #4 was merged at cdfa74c while Step 2 was in progress. Fix: the unpushed commits were rebased onto main (ISSUES_LOG conflict resolved by keeping main's entries and appending mine), the outputs were rerun and matched byte for byte, and a new PR follows.
- Next:
  - Carl marks Spot_Check.csv (Human Result, Checked By, Date) against the crops, and reviews the README noun lists.
  - Carl decides the AGENTS.md OCR-copy line (ISSUES_LOG).
  - Upload the four schema CSVs to `index/`.
  - Setup corrects "image-only" in 01 and closes 01 item 10.
  - The Ledger and MTO update step, on Carl's approval only.

## 2026-09-30 — OCR lane follow-up before PR #6 merge
- Runtime: Claude Code
- Commits: 496b3f5..HEAD on `claude/vibrant-davinci-7g3znj` (PR #6)
- Done:
  - Owner items 1–6:
    - Sheet-only anchors are Verified only for the Name's quantity read in the text layer; a noun match is Inferred ("on sheet, location not pinned").
    - The extractor moved to `testbeds/eastsound/tools/` by git mv; the paths it records are updated.
    - cited_as comes from `index/Plan_Set_Crosswalk.csv`; source SHA-256 values are checked against `index/Library_Manifest.csv`, stopping on a mismatch.
    - AGENTS.md carries the approved OCR-copy sentence; the Bluebeam README matches.
    - The schema ISSUES entry is corrected: only Audit_Ledger and Spot_Check are missing.
  - `tools/checks.py`: the ledger rule covers only project/ and lanes/ Ledgers (the owner's choice), so `derived/ocr/Ledger_Crosswalk.csv` is no longer checked as a Ledger.
  - A pre-merge review (5 auditors, 3 skeptics each) upheld 1 of 8 findings: row 374 was Verified on the "3'" in another louver's "2'x3'". Fix: sizes in a Name must match whole, and every quantity is required.
  - Final counts:
    - Sheet-only anchors: 8 Verified, 405 Inferred, 77 Unresolved.
    - All anchors: 26 / 427 / 102.
    - PROPOSED rows: 9 / 166 / 137.
    - Non-PROPOSED rows unchanged.
  - Replaced the bad branch-update merge a8694d8 (ISSUES_LOG, DECISIONS).
- Tests:
  - Test 8: `extract_drawing_text.py --stage all --jobs 4`, two clean runs → byte-identical to each other and to f3e8865, 112 of 112 files (697 s and 615 s wall). Pass.
  - Test 9: `git diff --stat origin/main...HEAD` → `derived/ocr/`, the moved extractor, the three logs, plus the owner-approved AGENTS.md, Bluebeam README and `tools/checks.py`. Pass.
  - `python tools/checks.py --ci --range origin/main..HEAD` and `--ci --all` → run before push; results in the PR #6 description.
- Failures and fixes:
  - `checks.py` flagged Ledger_Crosswalk.csv; fixed by narrowing the glob.
  - Row 374 false Verified; fixed by whole-quantity matching.
  - a8694d8 dropped main's log entries; replaced.
- Next: Carl merges PR #6 once the check is green, marks Spot_Check.csv, and uploads the Audit_Ledger and Spot_Check schemas.

## 2026-09-30 — Prompt 1: bootstrap and guardrails
- Runtime: Claude Code
- Commits: dd5400d..bda1bdd (PR #5, merged as 72c5342); follow-up 57433d9..6bc0d53, plus this log commit (branch `claude/zen-goldberg-4syazk`)
- Done:
  - **Checks:** `tools/checks.py` enforces the AGENTS.md (checked) rules. It is Python 3.10+ and stdlib only, with modes `--staged`, `--range BASE..HEAD` and `--all`. The rules:
    - `read-only-sources`: a new library source needs its `Library_Manifest.csv` row in the same commit.
    - `append-only-logs`.
    - `ledger`: every `*Ledger*.csv` except `Ledger_Schema.csv` and `*_by_CWP*` views.
    - `unsafe-file`: over 50 MB, secret-like names, `_inbox/`, and `.datagate/`, which Prompt 1 did not list.
    - `data-gate`: reads DATAGATE_TERMS, with `.datagate/blocklist.txt` as the fallback, and never prints a term.
    - `exceptions`.
  - **Hook and CI:** `.githooks/pre-commit` (python3, then python, then `py -3`; stored as 100755). `.github/workflows/checks.yml` runs `--range` over the pushed or pull-request commits, then `--all`. It passes the DATAGATE_TERMS secret and uses actions/checkout@v7 and actions/setup-python@v7. `git config core.hooksPath .githooks` is set in this clone.
  - **Baseline exceptions:** `tools/check_exceptions.csv` lists `project/02_Project_Ledger/Project_Ledger.csv` (duplicate Tags) for the ledger rule. The `Project_Ledger_by_CWP.csv` row was added in #5 and removed once the ledger rule skipped `*_by_CWP*` views. ISSUES_LOG has the matching Open and Closed entries.
  - **README:** one line added on running the checks. DECISIONS.md has the four Prompt 1 §7 entries.
- Tests:
  - Acceptance tests 1–9, run in a throwaway clone under the system temp folder by a scratchpad harness (not committed) that drives real `git commit` calls through the hook. Final run: 33 OK, 0 MISMATCH. That covers all nine prompt tests plus extras:
    - DATAGATE_TERMS with no file;
    - the variable taking precedence over the file;
    - CI with the secret set and with it unset;
    - `.datagate/` forced in;
    - an exceptions row without its ISSUES_LOG entry;
    - a `*_by_CWP*` view;
    - the workflow's range step run locally for push, first push and pull request.
  - Test 6: the blocklist file holding TESTTERM plus a staged .md containing it → blocked, and the term does not appear in the output.
  - `python tools/checks.py --all` on the session base 67e82f3 → 5 FAIL in the 2 Project Ledger files before the exceptions and the `*_by_CWP*` skip; 2 FAIL in `Project_Ledger.csv` after the skip.
  - `python tools/checks.py --all` → pass (0 FAIL, 3 WARN). `python tools/checks.py --staged` → pass.
  - CI on #5: push run 36767230499 → success; pull_request run 36768503887 → success (range 67e82f3..bda1bdd: 0 FAIL).
- Failures and fixes:
  - After the `--ci` change, the harness still expected the old "skipped in CI" note (extra test x4). Fixed the harness expectation and reran everything. Logged in ISSUES_LOG, "Acceptance harness expected the old --ci data-gate note".
  - Test 6 waited for DATAGATE_TERMS, which was never set in this session. It ran with its own TESTTERM blocklist, as Carl directed.
- Next:
  - Carl:
    - add the DATAGATE_TERMS repository secret (GitHub → Settings → Secrets and variables → Actions) and the environment variable;
    - run `python tools/checks.py --all` with the variable set before relying on CI, in case a term already appears in a baseline file;
    - add `git config --system core.hooksPath .githooks` to the environment setup script.
  - Merge: fix the two duplicate Project Ledger Tags in a new revision, then drop the exceptions row.
  - Next prompt: `prompts/02_import_testbed.md`.

## 2026-09-30 — Setup: schema CSVs and 00 Register rev2
- Runtime: Claude Code
- Commits: 5aa6038..HEAD on `claude/trusting-dijkstra-y0jpw8` (draft PR)
- Done:
  - Set `git config core.hooksPath .githooks` in this clone; it was unset.
  - `testbeds/eastsound/index/Audit_Ledger_Schema.csv` (21 columns) and `Spot_Check_Schema.csv` (12 columns): header-only, in Carl's column order. Both are ASCII with no BOM and one LF-terminated header line, like `Ledger_Schema.csv`.
  - `testbeds/eastsound/index/00_Document_Register_rev2.md`, issued from rev1, which is unchanged:
    - Rows 31–36 register the six native files, with bytes, SHA-256, pages, source and the commit that added each.
    - Rows 5–30 are marked resolved through `Plan_Set_Crosswalk.csv`. The mapping was generated by script from the crosswalk and appended to the Index status cell only.
    - The S-sheet "OF 96" finding is recorded.
    - Part 1/2/3 short names were added.
  - ISSUES_LOG: three Open entries closed ("Index files cite plans_N extracts…", "00 Register rev2 needs rows…", "Audit_Ledger and Spot_Check schema CSVs…"). One new Open entry, "Index follow-ups after 00 Register rev2".
  - DECISIONS: Carl's in-session direction that the Setup role creates the two schemas.
  - My own choice: rev1 lines the task didn't name were left as they are. They are listed in the new Open entry.
- Tests:
  - `stat`, `sha256sum` and `pdfinfo` on the 6 library PDFs → 18 of 18 values match `Library_Manifest.csv`.
  - A crosswalk sanity script → 96 unique set pages; Part pages 27/21/48; 99 of 99 rows Match.
  - Schema byte checks (`file`, a csv.reader round-trip) → 21 and 12 columns, no BOM, no CR, one line each. Spot_Check_Schema = first 12 columns of `derived/ocr/Spot_Check.csv`.
  - rev1-to-rev2 diff script → only the header lines, 26 appended status notes and the new sections.
  - `python3 tools/checks.py --staged` via the hook → 0 FAIL, 1 WARN (data gate not run: no terms set).
  - `python3 tools/checks.py --all` → 0 FAIL, 3 WARN.
  - `python3 tools/checks.py --range origin/main..HEAD` → 0 FAIL, 1 WARN.
- Failures and fixes: none
- Next:
  - Carl reviews and merges the draft PR.
  - Setup issues 01 rev2 ("OF 96", the 10 sheets now in the library, "image-only").
  - Someone checks the native Add. 4 pp.9–10 S-sheet title blocks.
  - On Carl's OK: 00 rev3 for the stale rev1 lines, and a `Library_Manifest.csv` update for Register rows 31–36.

## 2026-09-30 — Prompt 3: Ledger graph build
- Runtime: Claude Code
- Commits: 9b798da..HEAD on `claude/admiring-sagan-5olq78` (draft PR)
- Done:
  - **Step 1:** `.venv` with `requirements.txt` (graphifyy 0.9.72). `core.hooksPath` set to `.githooks`.
  - **Step 2:** reported each link column's separators, samples and odd formats from `project/02_Project_Ledger/Project_Ledger.csv` (read-only). Carl approved the rules with his answers; they are quoted in DECISIONS.md.
  - **Step 3:** extended `testbeds/eastsound/tools/ledger_to_graph.py` in place:
    - paren-aware splitting;
    - sheet, spec, Addendum 4 item and Wiki note IDs;
    - Lane and Bid Item as item attributes;
    - repeated Tags keyed `<Tag> [L<line>]`, with a `same_tag` link;
    - link level = the weaker of the row's tag and any level written in the value;
    - values that make no link are kept on the item under `unlinked`;
    - PYTHONHASHSEED pinned.
  - **Build:** outputs in `testbeds/eastsound/graph/graphify-out/`: graph.json, GRAPH_REPORT.md and graph.html.
    - 791 nodes: 447 items, 86 sheets, 77 specs, 21 Add. 4 items, 160 Wiki notes.
    - 3,114 links: 986 shown_on, 536 specified_in, 153 changed_by, 1,437 described_in, 2 same_tag.
    - 15 communities.
  - Also added `testbeds/eastsound/.graphifyignore` (`library/`, `derived/bluebeam-ocr/`) and `testbeds/eastsound/graph/README.md` (rebuild, rules, queries, and the Prompt 9 ID note).
  - **Findings logged in ISSUES_LOG:** 12 over-tagged rows; the "CQA Plan" Wiki note has no heading; the same_tag path shortcut; Prompt 3 doesn't match the repo after the reorg.
- Tests: all graph commands ran under `env -i` (PATH, HOME, LANG, `GIT_DIR=no-git`; the proxy pointed at 127.0.0.1:9 for tests 6–8). Acceptance tests from a scratchpad harness, not committed:

  | # | Test | Expected | Actual | Result |
  |---|---|---|---|---|
  | 1 | Every Ledger Tag is a node; nodes ≥ rows | 447 rows each a node | 447 item nodes (SD-1 and PROPOSED-Influent-Sampler keyed by line), 791 nodes, 0 rows missing | pass |
  | 2 | Every link has a citation and the original tag level | 0 missing | 3,114 links: 0 without citation; 3,112 row links carry their row's tag and Source Citation exactly; 2 same_tag links cite both lines and are Unresolved | pass |
  | 3 | Tag-level counts match the Ledger | 264 Inferred, 123 Unresolved, 40 Verified-Visual, 20 Verified | identical on item nodes; links: 1,700 INFERRED, 973 AMBIGUOUS, 441 EXTRACTED | pass |
  | 4 | Five spot checks, five lanes, `explain` vs the row | links match exactly | L73 C&S (4 links), L163 P&M (8), L268 E&C Verified (8), L361 S&B (11), L423 C&G (6): all match; extra SD-1 [L316]: 13 row links plus same_tag, none of the storm drain's | pass |
  | 5 | Cross-lane trace from an Add. 4 item | hops and tags shown | `path "Add. 4 p.8" "PROPOSED-Blower-Pad" --undirected`, 5 hops, every link INFERRED: Add. 4 p.8 ← slab coring (C&S, L73) → Add. 4 p.3 ← MCC (E&C/S&B, L263) → Add. 4 p.4 ← Blower Pad (S&B, L361) | pass |
  | 6 | Two clean builds byte-identical | graph.json and graph.html identical | two clean builds and the committed files: graph.json, graph.html and GRAPH_REPORT.md all SHA-256 identical | pass (after the fix below) |
  | 7 | No LLM calls | builds succeed with keys unset | exit 0 and 0 for both builds; environment held only PATH, HOME, LANG, GIT_DIR and a dead proxy | pass |
  | 8 | Library excluded | 0 papers, 0 images, stops at key check | `found 105 code, 760 docs, 0 papers, 0 images`, then "no LLM API key found", exit 1 | pass |

  - `python3 tools/checks.py --all` → 0 FAIL, 3 WARN (data gate not run; the 2 listed Ledger exceptions). `--staged` on each commit → 0 FAIL.
- Failures and fixes:
  - The in-repo build differed from the clean builds by graphify's git commit stamp. Logged before the rerun (ISSUES_LOG, "Graph build inside the repo stamps the git commit…", Open, then Closed). Fix: `GIT_DIR=no-git`.
  - The Step 2 dry run showed test 8 would fail with only `library/` ignored. Fixed by Carl's `.graphifyignore` choice.
  - The README first said Add. 4 p.3 had 53 items (a count of cell values). Corrected to 43 before commit.
- Next:
  - Carl reviews and merges the draft PR.
  - Merge fixes SD-1, the influent-sampler duplicate and the 12 over-tagged rows in a new Ledger revision; rebuild the graph after.
  - Update `prompts/03_build_graph.md`.
  - Prompt 9 adds the Ledger ID column; switch the item key to it.

## 2026-09-30 — Prompt 3 follow-up before PR #9 merge
- Runtime: Claude Code
- Commits: e99a8a8..HEAD on `claude/admiring-sagan-5olq78` (PR #9)
- Done:
  - Merged main (PR #8, b8e1313) into the branch as e99a8a8. In PROGRESS_LOG, ISSUES_LOG and DECISIONS, main's entries come first and this branch's follow, byte for byte (checked against the merge base).
  - Dropped the same_tag link between the two SD-1 rows, per Carl: `NO_SAME_TAG` in `testbeds/eastsound/tools/ledger_to_graph.py`. The PROPOSED-Influent-Sampler link stays.
  - Updated `testbeds/eastsound/graph/README.md` (rule 9, link count, path note).
  - Rebuilt the graph: 791 nodes, 3,113 links (986 shown_on, 536 specified_in, 153 changed_by, 1,437 described_in, 1 same_tag), 17 communities.
  - This supersedes the counts in the "Prompt 3: Ledger graph build" entry.
- Tests: all graph commands under `env -i` with `GIT_DIR=no-git` and a dead proxy.
  - T1: 447 rows → 447 item nodes, 791 nodes, 0 rows missing → pass.
  - T2: 3,113 links; 0 without a citation; every row link carries its row's tag and Source Citation; the only same_tag link is the influent sampler's → pass.
  - T3: 264 / 123 / 40 / 20 on item nodes, the same as the Ledger → pass.
  - T4: `explain` on L73, L163, L268, L361 and L423 gives the same links as the rows (4, 8, 8, 11, 6). SD-1 [L316] has 13 row links and SD-1 [L74] has 6, with none between them → pass.
  - T5: `path "Add. 4 p.8" "PROPOSED-Blower-Pad" --undirected` → 5 hops through Add. 4 p.3 and MCC, unchanged → pass.
  - T6: the repo build and two clean builds are SHA-256 identical for graph.json, graph.html and GRAPH_REPORT.md → pass.
  - T7: exit 0 on every build and cluster-only with no keys → pass.
  - T8: `graphify extract` on a copy → `found 105 code, 761 docs, 0 papers, 0 images`, stops at the key check → pass.
  - `python3 tools/checks.py --all` → 0 FAIL, 3 WARN (data gate not run; the 2 listed Ledger exceptions). `--range origin/main..HEAD` (before this log commit) → 0 FAIL, 1 WARN. `--staged` → 0 FAIL on every commit.
- Failures and fixes: none.
- Next: Carl merges PR #9. Merge fixes the two repeated Tags and the 12 over-tagged rows; Prompt 9 adds the Ledger ID.

## 2026-09-30 — Setup: 01 rev2, 00 rev3, manifest Register rows, Add. 4 S-sheet check
- Runtime: Claude Code
- Commits: ffad91b..HEAD on `claude/trusting-dijkstra-y0jpw8`, restarted from main ce488d5 after PR #8 merged (new draft PR)
- Done:
  - `testbeds/eastsound/index/01_Sheet_Index_rev2.md` from rev1 (rev1 unchanged):
    - S-sheet totals "OF 96".
    - The 10 sheets indexed from native Parts 1 and 3 (Plan_Set_Crosswalk.csv), with a Native-only pages table. Their Read Method is set to provisional Visual (my choice, logged Open).
    - "no text layer (vector drawing)" replaces "image-only".
    - Summary counts and items 9 and 10 updated.
  - `00_Document_Register_rev3.md` from rev2 (rev2 unchanged):
    - The four stale rev1 lines are fixed.
    - The Add. 4 pp.9–10 result is recorded.
    - Rows 5–30 point to 01 rev2. This goes beyond the list and was approved in the plan.
  - `Library_Manifest.csv`: "00 Register Row" = 31–36; the parts' "no 00 Register row yet" note is dropped. Path, bytes and SHA-256 are unchanged.
  - Native Add. 4 pp.9–10, rendered: S2.3 "59 OF 96", S4.1 "61 OF 96". Both also show revision 3 "Blower Building" 2/8/23, logged Open against 01 item 12.
  - ISSUES_LOG: "Index follow-ups after 00 Register rev2" closed; two new Open entries.
- Tests:
  - `pdftoppm` renders of native Add. 4 pp.9–10: title block and revision block read.
  - `pdftotext` on the 10 native-only pages → each reads its own "N OF 96" and sheet number.
  - `pdftotext` and `pdfimages -list` on the 11 no-text-layer pages → 0 characters, or only the 10-character seal date; only rasters of about 1 in. or less.
  - Build scripts assert every replacement count. A diff of rev1→rev2 and rev2→rev3 shows only the planned lines. A csv comparison of the manifest shows only the Register Row and Notes cells changed.
  - `python3 tools/checks.py --staged` via the hook → 0 FAIL, 1 WARN (data gate not run).
  - `python3 tools/checks.py --all` → 0 FAIL, 3 WARN.
  - `python3 tools/checks.py --range origin/main..HEAD` → 0 FAIL, 1 WARN.
- Failures and fixes:
  - The 01 rev2 script's stale-term check first failed on the new Changes line, which names the old terms on purpose. The check now skips that line.
- Next:
  - Carl merges the draft PR.
  - Setup measures body chars for the 10 native-only sheets.
  - On Carl's OK, Setup checks the Add. 4 pp.4–8 revision blocks.
## 2026-09-30 — Prompt 9: OCR evidence reconciled into proposed Ledger updates and a starter civil MTO (proposal mode)
- Runtime: Claude Code
- Commits: 7efb30b..HEAD on `claude/vigilant-albattani-h4lspn` (draft PR)
- Done:
  - Set `git config core.hooksPath .githooks` in this clone; it was unset. Main was pulled at the start and again after PR #8 merged mid-session (fast-forward to b8e1313; #8 touched none of this step's inputs).
  - `AGENTS.md` Layout: one line for `derived/reconciliation/`, in its own commit (Carl's rule-8 request).
  - `testbeds/eastsound/tools/build_reconciliation.py` (location per Carl): reads `derived/ocr/` and the Ledger, and imports `extract_drawing_text.py` for its search-form, Name-quantity and unmatched-tag rules. It re-reads each Division 26 evidence line from the native text layer and stops, writing nothing, if any of its 25 tie-outs fails. Outputs go to `derived/reconciliation/` only.
  - `derived/reconciliation/`: README.md, Ledger_ID_Map.csv (447 IDs; L-0001 = Ledger Row 2), Ledger_Schema_rev1_Proposal.md (19 columns; one total Quantity per row), Ledger_Update_Proposal.csv, Starter_MTO.csv, Needs_Check.csv, New_Row_Candidates.csv, Summary.md.
  - Ledger_Update_Proposal.csv, 243 rows, 14 of them Verified changes:
    - Found, not cited: 18 rows (6 Verified sheet adds: Hot Box #1 E4.3, E7.4, E10.2; Hot Box #2 E4.3; EF-1 E0.1; DW-1 E2.1).
    - Cited, not found: 215 rows, all needs check (5 with a variant printed form, e.g. SDCB#1076).
    - PROPOSED printed tag found: 4 rows (L-0337 and L-0338 take "Hot Box #1" and "Hot Box #2", Verified; the same tags as L-0057 and L-0058, left for Merge).
    - Owner's Division 26 review: 6 rows (TS, T3, T2 to Verified; ATS to Inferred plus the bid split; GEN Notes RFI). Each carries its native text-layer box.
  - Starter_MTO.csv (C0–C2, C7): 83 leads, 48 callouts, 22 lines. 1 line is Ready (3 EA yard hydrants, L-0051, C1.3 Add. 4 p.7, text layer). The earthwork cut 3382 CY and fill 1598 CY have no Ledger ID, carry Bid Item 1 (Inferred) and "new row needed". 26 callouts are held and listed in Summary.md, including the C2.1 fence notes.
  - Needs_Check.csv: 25 checks (21 MTO lines; 4 panel schedules: MDP, LP1 and LP2 on E6.2, LP1 on E2.2). The schedules are embedded images; the text layer holds only their titles.
  - New_Row_Candidates.csv: 2 proposed earthwork rows, plus 721 tag-and-sheet rows for the 401 unmatched tags (1131 reads).
  - Summary.md: the chain link fence conflict (L-0018, L-0088 vs C2.1 keyed notes 6 and 8) and the generator RFI (125 kW on E1.1 and E6.1 vs "not less than 150.0kW" in 26 32 13 ¶2.03 C.1, main spec p.326), both left for Carl. Also held leads, segment sums (C2.3: 28 + 20 = SD-2's 48 LF; 39 + 44 = SD-3's 83 LF, Inferred) and open decisions.
  - My own choices, listed in README.md:
    - One OCR and one Bluebeam read of the same callout make one MTO line.
    - A count from "N <noun>" is kept only when the tied Ledger Name names the noun.
    - A cited-not-found sheet is never proposed for removal.
    - TS, T3 and T2 proposals note that their Notes still hold "Status New inferred" (weakest-tag rule).
- Tests:
  - `python3 tools/checks.py --all` at the start → 0 FAIL, 3 WARN.
  - `python3 testbeds/eastsound/tools/build_reconciliation.py` → 25 of 25 tie-outs pass. These include: found-not-cited 18 = crosswalk pairs; cited-not-found 215 = crosswalk pairs; Tag_Hits found sheets = crosswalk for 447 of 447 rows; unmatched reads per page and method = Unmatched_Tags for 401 tags and 1131 reads; every proposal cites evidence; no change on Inferred evidence; 9 Division 26 evidence reads and 4 panel boxes found in the native files.
  - Determinism: three runs (repo, two temp folders) → 6 of 6 generated files byte-identical (`cmp`). All 8 files are UTF-8 without a BOM and LF.
  - `python3 -m pyflakes testbeds/eastsound/tools/build_reconciliation.py` → clean.
  - `--crops` into the scratchpad → 25 PNGs; checks 1, 9 and 25 viewed (C0.2 cut, C0.5 keyed note 16, E6.2 LP2 schedule) and boxed as intended.
  - Hook `tools/checks.py --staged` on each commit → 0 FAIL, 1 WARN (data gate not run: no terms set).
  - Close-session checks are in the PR description.
- Failures and fixes:
  - Summary.md's RFI line first picked a cited-not-found row for GEN instead of the Division 26 row. Fixed before commit.
  - Segment sums first allowed three-callout sums, which gave a spurious SD-3 match (21 + 23 + 39). Limited to pairs before commit.
  - Logged in ISSUES_LOG.
- Next:
  - Carl reviews the draft PR. He marks Needs_Check.csv, decides the fence conflict, the GEN RFI, the Hot Box duplicates and schema rev1 (with the checks.py and ledger_to_graph.py changes it implies), then approves the Ledger update step.

## 2026-09-30 — Prompt 9 follow-up before PR #10 merge
- Runtime: Claude Code
- Commits: ea27a87..HEAD on `claude/vigilant-albattani-h4lspn` (PR #10)
- Done:
  - Merged main (PR #9, ce488d5) into the branch (ea27a87). In the three logs, main's entries come first and this branch's follow, byte for byte. PR #9 did not change AGENTS.md.
  - `testbeds/eastsound/derived/reconciliation/Ledger_Schema_rev1_Proposal.md`: the ledger_to_graph.py impact row now says the two SD-1 rows are separate nodes (`<Tag> [L<line>]`, from PR #9). The switch to Ledger ID is still pending (599a869).
  - ISSUES_LOG: a correction entry for the stale graph line in "Ledger Tag uniqueness (checks.py, ledger_to_graph.py) conflicts with decision A".
- Tests:
  - A script compared each merged log with origin/main and with this branch's additions → 3 of 3 exact, and AGENTS.md unchanged.
  - `python3 testbeds/eastsound/tools/build_reconciliation.py` → 25 of 25 tie-outs pass. A second run to a temp folder → 6 of 6 generated files identical to the committed ones (`cmp`). PR #9 changed none of this step's inputs.
  - `python3 tools/checks.py --all` → 0 FAIL, 3 WARN.
  - The hook's `--staged` → 0 FAIL on each commit.
  - `--range origin/main..HEAD` → result in the PR #10 description.
- Failures and fixes: none
- Next: Carl merges PR #10.
