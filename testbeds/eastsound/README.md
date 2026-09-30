# Eastsound test bed

Public bid set for the Eastsound Sewer and Water District WWTP Upgrade Phase I (Wilson Engineering job 2020-070), used to prove the Project Wiki + Project Ledger design. No Big-D, client or employee data.

- **Plans:** `process/Sample_Project_Concurrent_Lane_Ultraplan_rev1.md` (master) and `process/Graph_Transfer_Ultraplan.md` (transfer, graph build, first proof run).
- **Baseline:** everything here at the transfer-baseline release is the record of the crawl. It isn't edited in place; fixes land as new revisions.
- **Folders:** `library/` original source files, read-only, with notes beside them · `index/` 00–04 rev1 and both schemas · `lanes/` the five lane outputs · `project/` Merge outputs, including the test bed's Issues Log · `process/` plans, build prompts, library fingerprints · `transfer/` Transfer step reports · `tools/` build scripts · `graph/` graph build outputs.
- **Rules:** AGENTS.md at the repo root.

## Folders

As they exist on `main`, 2026-09-30. `transfer/` and `graph/` aren't created yet.

- `library/` — native source files (main spec, Add. 4, CQA plan, three plan-set parts), read-only, with `.md` notes beside them.
- `derived/` — derived copies of library files, not sources; `bluebeam-ocr/` holds the person-made OCR copies of the plan set.
- `index/` — 00–04 index files, both schemas, `Library_Manifest.csv` and `Plan_Set_Crosswalk.csv`.
- `lanes/<lane>/` — one folder per lane; the lane Wiki, Ledger, Issues and Known Issues files aren't uploaded yet.
- `lanes/<lane>/as-delivered/` — each lane's per-page and per-component wiki packages, as delivered.
- `project/` — the Merge rev2 package, `01_Project_Wiki` to `07_Resplit_Pass`, with its README.md.
- `process/` — both Ultraplan rev1 files (the .docx is a reading copy), the Graph Transfer Ultraplan, the drag-and-drop order, the library fingerprints and the reorg report.
- `tools/` — test bed build scripts (`ledger_to_graph.py`).
- `_unsorted/` — files a sort couldn't place; its README.md gives each one's reason.
