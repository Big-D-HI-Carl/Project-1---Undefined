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
