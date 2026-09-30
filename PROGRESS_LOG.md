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
