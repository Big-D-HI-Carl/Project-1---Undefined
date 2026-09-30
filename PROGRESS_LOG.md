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
