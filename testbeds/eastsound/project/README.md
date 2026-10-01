# Eastsound WWTP Upgrade Phase I — Test Bed Outputs (Merge rev2)

Public bid set, test bed only. Built 2026-09-29 by the Merge thread from the five lane outputs, the index files 00–04, Addendum 4 and the four resplit sheet images.

- **Formats:** .md, .csv and .xlsx only, so any runtime can read them. Each .csv is UTF-8 without a byte-order mark; open it in Excel through Data > From Text/CSV, or use the matching .xlsx.
- **Tags:** Verified · Verified-Visual · Inferred · Unresolved, as in the lane files. Addendum 4 governs over base documents.
- **Edit these, nothing else:** Exception Report Disposition column; tracker status date, work type, step dates, weight and remarks; tracker Schedule tab dates and Rules of Credit weights. Everything else is generated.
- **Not included:** the library documents and the 15 lane files and 5 Known Issues files (inputs).

## How the files connect

- Project Wiki notes are cited by unit ID in the Ledger's "Wiki Note(s)" column.
- Project Ledger → Ledger by CWP → Schedule (each Ledger row sits in one activity) → Installation Tracker (planned dates look up the schedule).
- Submittal Register and ITP → by-CWP view with schedule dates → QC Requirements page (18 logs).
- Exception Report ↔ Issues Log ↔ Project Known Issues (each known issue shows its log entry and exception number).
- Drawing Controls Register → rescan and upload actions; the resplit pass fed the Wiki and Ledger.

## Folder map

### 01_Project_Wiki

- **Project_Wiki.md** — 202 notes, one per sheet, spec section, appendix and other unit, in index order. Four Civil & Site notes (C0.3, C2.1, C2.3, C2.6) come from the resplit pass.

### 02_Project_Ledger

The current Ledger is **Project_Ledger_rev2** (Prompt 11). rev0 and rev1 are history, kept unchanged. The folder's README.md gives the full list.

- **Project_Ledger_rev2.xlsx** — Current. 529 rows: the 449 rev1 rows plus 80 conduit and feeder runs from the E6.3 schedules. Columns in bands A–I. Tabs: Ledger, MTO Lines, Totals, Coverage, Candidates, Column Guide, Links. Verified-only total 150 EA (headline), with "Total incl. reads to verify" beside it.
- **Project_Ledger_rev2.csv** — Current, machine copy in Ledger_Schema_rev1.csv columns (UTF-8, no BOM). MTO_Lines_rev2.csv and Ledger_rev2_Summary.md go with it.
- **Project_Ledger_rev1.xlsx / .csv** — History (Prompt 10): the expanded MTO, 449 rows.
- **Project_Ledger.xlsx** — History (rev0): 447 rows in the exact Ledger_Schema.csv columns (123 Unresolved). Every row an exception touches ends its Notes with "[Merge] Exceptions: #n".
- **Project_Ledger.csv** — History (rev0): same rows, machine copy (UTF-8, no BOM — open in Excel through Data > From Text/CSV).
- **Project_Ledger_by_CWP.xlsx** — rev0 divided into 19 CWPs by construction division, color-coded, one tab per CWP, index with live counts. rev1 and rev2 carry a CWP column of their own.
- **Project_Ledger_by_CWP.csv** — Same view with CWP, CWP name and CWP basis columns added.

### 03_Exceptions_and_Issues

- **Exception_Report.xlsx** — 571 exceptions in 8 types; Disposition column has a drop-down (real conflict / lane error / acceptable).
- **Exception_Report.md** — Same report with merge rules, Add. 4 coverage table, Unresolved register and Merge workflow log.
- **Issues_Log.md** — Running issues log, 87 entries (Open 55, Logged 22, Worked around 5, Fixed 2, Deferred 2, Closed 1). Append-only.
- **Issues_Log.csv** — Same log, machine copy.
- **Project_Known_Issues.xlsx** — The five lane Known Issues files combined: 31 method themes, 139 open document decisions, settled items; each item points to its log entry and exception number.
- **Project_Known_Issues.md** — Same register as Markdown.

### 04_Submittals_ITP_QC

- **Submittals_and_Inspections_by_CWP.xlsx** — Submittal Register and Inspection & Test Plan divided by CWP, color-coded, with schedule dates.
- **Submittals_and_Inspections_by_CWP.csv** — Same lines, machine copy.
- **Phase1_Workflows.xlsx** — Phase 1 workflow test: both registers in Requirements_Schema.csv columns, test log and summary.
- **Submittal_Register.csv** — 145 submittal lines (Requirements_Schema.csv columns).
- **Inspection_Test_Plan.csv** — 103 inspection and test lines (Requirements_Schema.csv columns).
- **Phase1_Workflow_Test.md** — Verdict and test log for the two Phase 1 workflows.
- **QC_Requirements.xlsx** — 18 QC logs on one page, rolled up from the ITP, plus the ITP line map.
- **QC_Requirements.md** — Same page as Markdown.

### 05_Schedule_and_Tracker

- **Schedule_by_CWP.xlsx** — 146 activities: milestones, procurement, construction by CWP and work area, inspections, tests and start-ups; weekly Gantt colored by CWP.
- **Schedule_by_CWP.csv** — Activity list with IDs, dates and predecessors for P6 or MS Project import.
- **Installation_Tracker_by_CWP.xlsx** — 444 items in CWP sections, linked to the schedule; rules-of-credit progress, status date on the Summary tab, inputs in blue.
- **Installation_Tracker_by_CWP.csv** — Tracker baseline (planned dates, blank progress columns) for other tools.

### 06_Drawing_Controls

- **Drawing_Controls_Register.xlsx** — All 97 sheets plus the phantom C8.1: title checks, Add. 4 reissues, availability, read-method and legibility findings, rescan/upload actions.
- **Drawing_Controls_Register.csv** — Same register, machine copy.
- **Drawing_Controls_Register.md** — Rescan and upload action list plus sheets with findings.

### 07_Resplit_Pass

- **Civil_and_Site_Resplit_Pass.md** — Civil & Site pass on C0.3, C2.1, C2.3 and C2.6: Wiki notes, Ledger changes, issues.
- **Civil_and_Site_Resplit_Ledger.csv** — The 29 Civil rows added or changed by the pass, full schema.

## Still open

See Issues_Log.md (open entries) and Project_Known_Issues.md Part B. Top inputs still needed: Addenda 1–3; sheets C0.7, C1.1, C1.2, C7.7, C7.8, C7.9; native PDFs for the ten unreadable or low-confidence values.
