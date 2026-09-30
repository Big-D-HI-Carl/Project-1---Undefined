# Prompt 2 — Import the Eastsound test bed

Run from the repo root with /plan in front.

Before sending this, I will have:
- copied the native library files into `testbeds/eastsound/library/`, with the same file names and folder structure as the library the Claude Project used
- put everything else in `_inbox/`: the 00–04 rev1 inventory files, Ledger_Schema.csv, Requirements_Schema.csv; each lane's final Wiki, Ledger, Issues and Known Issues files; the Merge outputs (Project Wiki, Project Ledger CSV and XLSX, Exception Report, Submittal Register, Inspection and Test Plan, CWP workbook, running Issues Log, workflow test log); the governing plan; the Composer prompts

Goal: every file in its place, unchanged, with a verified manifest. Don't edit content. Findings get logged, not fixed.

## 1. Sort `_inbox/` — mapping table first
Show a table: file | destination | reason. Wait for my OK.
- 00–04 rev1 files and both schemas → `testbeds/eastsound/index/`
- lane files → `testbeds/eastsound/lanes/<lane>/`, matched on the lane name in the file name
- Merge outputs → `testbeds/eastsound/project/`
- governing plan and Composer prompts → `prompts/history/`
- anything unclear → leave in `_inbox/` and list it

After approval, move the files. Names stay unchanged.

## 2. Verify the library (read-only)
- Write `testbeds/eastsound/index/Library_Manifest.csv`: relative path, bytes, SHA-256, PDF page count, date added.
- Compare against `index/00_Document_Register_rev1.md`: every registered file present, no unregistered files, page counts match. The register counted pages on converted copies; the native files should match page for page. Each mismatch is one ISSUES_LOG.md entry (type: input gap) citing the register row.
- Page counts need a PDF library: propose `pypdf` pinned to an exact version in requirements.txt and wait for my OK.

## 3. Validate
- Run `python tools/checks.py --all`. Per ledger, report: rows, unique tags, header match, BOM, count per tag level.
- Expected row counts from the thread records: Civil & Site 115, Process & Mechanical 114, Electrical & Controls 126, Structural & Building 45, Contract & General 49 (derived: 449 lane rows in total minus the other four), Project Ledger 441. Each mismatch is an ISSUES_LOG.md entry (input gap).
- If an imported file fails a check, don't edit it. Add a row to `tools/check_exceptions.csv` with a matching ISSUES_LOG.md entry and list it for me. I'll decide on fixes separately.

## 4. Carry over the running Issues Log
Append the Merge thread's Issues Log entries to ISSUES_LOG.md under the heading "Imported from the Merge thread, 2026-09-30", text and numbering verbatim. The original file stays in `project/` as the record.

## 5. Record
- DECISIONS.md, decided by Carl: "Test bed imported. The library holds the native files; citations keep the short names defined in the 00 register."
- Commit per group: library and manifest; index; lanes; project; logs.
- Run prompts/close_session.md. Push if all checks pass.
