# Phase 1 Workflow Test — Submittal Register and Inspection & Test Plan

Eastsound WWTP Upgrade Phase I · test bed · Merge rev0 inputs (Project_Wiki.md, Project_Ledger.csv). Built 2026-09-29.

- **Method:** every Wiki note sentence that states a submittal (or a test, inspection, start-up or training requirement) becomes one row in the Requirements_Schema.csv format. The sentence is kept verbatim with its citation; Subtype, Timing, Acceptance and Responsible Party are parsed from it by keyword. Tags, sheets and bid items come from Project Ledger rows that cite the section (or sheet) and carry Y in the matching column. Rows ending "-00" are gaps: the Ledger flags a requirement the Wiki does not summarize.
- **Scope left out:** bid-phase sections 00 11 16–00 45 43 (bid submittals) and the QA plan (not a Contract Document, §1.3).
- **Output:** Submittal_Register.csv (145 rows: 139 requirements + 6 gap rows); Inspection_Test_Plan.csv (103 rows: 92 requirements + 11 gap rows); Phase1_Workflows.xlsx (both registers, this log, summary).

## Verdict

The retrieval rule held: both registers were built from the Wiki and Ledger without opening the library. They work as a first-pass register — every line is cited and linked to equipment where the Ledger allows — but not as an issued submittal log or ITP. Timing, acceptance values and hold/witness points mostly live in paragraph text that the 3–5 sentence notes do not carry. The fix is structural, not a rescan: have the crawl write Requirements rows alongside the Wiki notes.

## Test log

| Question | Answered from Wiki + Ledger? | Evidence | Fix |
|---|---|---|---|
| Build both registers from the Wiki and Ledger only | Yes | No library file opened. 139 submittal and 92 test/inspection requirements came from 98 and 70 Wiki notes; bid-phase sections 00 11 16–00 45 43 and the QA plan left out. | Retrieval rule held. |
| Link each requirement to equipment tags | Partly | Tags come from Ledger rows flagged Y that cite the section. 20 submittal and 9 test rows link to no tag; cross-lane items are often not flagged because each lane set Y only for its own stack. | Flag Y/N from the governing section regardless of lane, or add a governing-section column. |
| Submittal type (shop drawing, product data, O&M…) | Partly | Parsed from the note sentence by keyword; 20 of 139 rows fall back to "General submittal". | Capture one Requirements row per submittal item at crawl time. |
| Due date / timing | Mostly no | 123 of 139 submittal rows and 77 of 92 test rows have no timing in the note text. | Notes are 3–5 sentence summaries; timing lives in the ¶ text. Capture it in Requirements rows. |
| Test acceptance criteria | Partly | 70 of 92 test rows have no acceptance value in the note text. | Same fix; acceptance values need their own field at crawl time. |
| Responsible party | Partly | Applied as rules: submittals default to the Contractor (01 33 00); tests with no party in the sentence take the 01 45 00 split (Contractor-paid pressure, leakage, disinfection, equipment and start-up tests; Owner-paid special inspections and material testing), tagged Inferred. 19 of 92 test rows still have no party. | Capture the party in Requirements rows at crawl time. |
| Hold / witness points | No | Witness requirements appear in some sentences, but Requirements_Schema.csv has no hold/witness column. | Add a Hold/Witness/Review column to Requirements_Schema.csv. |
| Requirements the Ledger flags but the Wiki does not summarize | No | Submittal: 6 sections (01 45 00; 01 50 00; 08 10 00; 26 80 00; 33 31 00; 46 12 13). Test: 11 sections (05 50 00; 07 20 00; 08 10 00; 08 70 00; 09 25 00; 09 90 00; 13 12 20; 33 05 00; 41 12 13; 43 22 10; 46 12 13). Kept as gap rows ending "-00". | Crawl prompts should write Requirements rows, not just Y/N flags. |
| Requirements in drawing notes | Partly | Sheet-note sentences are included where they state a test, inspection or submittal (for example S1.1 special inspections, G0.3 inspection notice); the Ledger Y/N flags ignore them (Civil & Site CS-37). | Add a basis qualifier to the Y/N columns (spec / addendum / drawing / reference). |
| Sections checked and found to have no requirement | Yes | Lanes recorded 5 "no submittal" and 10 "no test" findings (e.g. 26 27 26); these are kept out of the registers. | None — useful negative evidence. |
| Confidence | Yes | Submittal rows: Inferred 116, Verified 15, Unresolved 10, Verified-Visual 4. Test rows: Inferred 82, Unresolved 13, Verified 7, Verified-Visual 1. Row tag = weakest of the sentence tag and the tag linkage. | Consider a separate confidence field for the linkage so verified requirements stay Verified. |
