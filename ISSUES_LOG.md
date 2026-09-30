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
