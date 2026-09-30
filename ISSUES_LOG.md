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
