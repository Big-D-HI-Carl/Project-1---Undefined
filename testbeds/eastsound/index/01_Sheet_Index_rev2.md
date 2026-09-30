# 01 Sheet Index

Sheet-level index of the Phase I drawing set with location, lane, and read method. Inventory only.

- **Version:** rev2, issued 2026-09-30 · **Owner:** Setup thread (single writer) · **Supersedes:** 01_Sheet_Index_rev1.md
- **Changes in rev2:** the 10 sheets rev1 listed as not in library are indexed from native Parts 1 and 3 (`index/Plan_Set_Crosswalk.csv`); the S-sheet page totals read "OF 96" on the native files (rev1 logged a misread from the stored copies); "image-only" is replaced with "no text layer (vector drawing)" for C3.3, C3.4, C7.3 and the S sheets. The Summary counts, items 9 and 10, and a Native-only pages table follow from these. Nothing else changed from rev1.
- **Changes in rev1:** Read Method threshold raised to 300 body characters (decision C): 20 sheets re-flagged Visual, and the Add. 4 reissues of A1.1 and A1.2 follow them; terms (decision H).
- **Project:** Eastsound Sewer and Water District, Wastewater Treatment Plant Upgrade Phase I (Wilson Engineering job 2020-070). Public bid set; test bed only.
- **Source:** Claude Project copy of the library (read-only converted copies, not native PDFs).
- **Source (rev2):** the 10 sheets added in rev2 cite the native parts in `testbeds/eastsound/library/`. Every other row still cites its plans_N copy, which resolves to a native page through `index/Plan_Set_Crosswalk.csv`.
- **Tags:** Verified = read in the stored text layer · Verified-Visual = read from the page image · Inferred = derived, basis stated · Unresolved = conflict or missing, need stated.
- **Rules:** addenda supersede base documents (cite both, state which governs) · the body section number governs over the running header and the TOC · duplicates are not indexed: the Division 26 file (use the main spec) and plans_7 pp.1–3 (use plans_6) · claims that defer to WSDOT are tagged "Unresolved: external reference, not staged."
- **Terms:** thread = a chat (Setup, Composer, Merge) · lane = a crawl scope only (Civil & Site, Process & Mechanical, Electrical & Controls, Structural & Building, Contract & General).
- **Short names:** plans_N = `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_N.pdf` · Add. 4 = `addendum-no4-eswd.pdf` · main spec = `eswd-wwtp-upgrade-phase-i-specs.pdf` · p. = PDF page within the named file.
- **Short names (rev2):** Part 1 = `Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf` · Part 2 = `Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 2.pdf` · Part 3 = `Pages from eswd-wwtp-upgrade-ph1-11x17-plans - Part 3.pdf` (as in `00_Document_Register_rev2.md`).

## Method

- **Source list:** "Index to Drawings" on G0.1 (plans_1 p.1), 96 sheets in positions 1–96 (Verified). Index position = set page = title block "N OF 96" on all 96 sheets (Verified / Verified-Visual): the 86 available in rev1, and the 10 added in rev2, each read in the native text layer. The S sheets read "OF 96" on native Part 3 (item 10). The full set's PDF page N is taken to be set page N (Inferred).
- **Title** is the title-block title. Where the cover index differs, the difference is logged below.
- **Discipline** comes from the sheet prefix (Inferred).
- **Lane** follows decision 6, plus the G-sheet adjustment below.
- **Body chars** = characters left in the stored text layer after removing title-block text.
- **Read Method** (decisions 5 and C): Visual = page with no text layer (vector drawing), 300 or fewer body chars, or schedule tables (E6.2, E6.3). Everything else is Text. Lane prompts must run a visual pass on every Visual sheet and tag claims from it Verified-Visual. "(rev1)" marks sheets re-flagged by decision C.
- **Read Method for the 10 sheets added in rev2 (provisional):** they have a text layer, but body chars were not measured on the native file by this method. They are set "Visual (rev2, provisional)" (Inferred: Visual is the conservative setting under decision C, so lanes run a visual pass) until measured.

## Summary

| Item | Count |
|---|---|
| Sheets on cover index | 96 |
| Available | 96 (rev2: 86 + the 10 native-only sheets) |
| Assigned — unavailable | 0 (rev2: the 10 are in native Parts 1 and 3; Plan_Set_Crosswalk.csv) |
| Sheets issued by addendum only (not on cover index) | 1 (C1.6A) |
| Drawing pages in library | 96 native pages (Parts 1–3) + 7 Add. 4 reissue pages (rev2). The 89 plans_N pages cited here (86 indexed + 3 duplicates) are Claude Project copies that resolve to native pages through Plan_Set_Crosswalk.csv |
| Base drawing pages with a text layer | 80 of 89 plans_N pages (no text layer (vector drawing): 9); the 10 native-only sheets all have a text layer (rev2) |
| Read Method, available sheets | Visual 40 · Text 46 · Visual (rev2, provisional) 10 |
| Lane totals (all 96) | Civil & Site 32 · Process & Mechanical 20 · Electrical & Controls 35 · Structural & Building 9 |

## Lane adjustments (decision 6)

- **G0.1–G0.7 had no lane in decision 6.** They are split by title (Inferred): G0.5 Process Schematic, G0.6 Hydraulic Profile, and G0.7 Design Criteria go to Process & Mechanical. G0.1 Cover, G0.2 civil and architectural legend, G0.3 Notes & Specifications, and G0.4 W.A.C. 332-130 survey compliance go to Civil & Site. They are marked "(adj.)". The split is carried from rev0, and the gate closed PASS with it in place (03_Coverage_Gate_rev1.md).
- **No other reassignment.** Cross-lane content goes to Merge instead of moving the sheet: C7.4, C7.6, C7.9–C7.10, and C1.6A are cross-checks for Process & Mechanical; A1.1 is a cross-check for Electrical & Controls. Basis: view titles (Verified) and C1.6A markups (Verified-Visual).

## Read Method change, rev0 → rev1 (decision C)

The threshold rose from 20 to 300 body characters. 20 sheets moved from Text to Visual: C0.1 (37), C0.4 (238), C2.2 (72), C3.2 (75), C3.5 (36), C4.1 (46), C4.2 (84), C4.3 (198), C5.2 (110), C5.3 (137), C5.4 (272), C6.1 (51), C6.2 (35), C6.3 (22), C7.1 (216), C7.4 (222), C7.6 (127), C7.10 (136), A1.1 (108), A1.2 (90). The Add. 4 reissues of A1.1 and A1.2 follow their base sheets to Visual. The lowest body-character count still Text is C1.5 (334).

## Sheet table (cover-index order)

| Set p. | Sheet | Title (title block) | Discipline | Lane | File | PDF p. | Text | Body chars | Read Method | Status | Addendum 4 | ID source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | G0.1 | COVER SHEET | General | Civil & Site (adj.) | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 1 | Y | 4242 | Text | Available | — | Verified |
| 2 | G0.2 | LEGEND AND ABBREVIATIONS - CIVIL & ARCHITECTURAL | General | Civil & Site (adj.) | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 2 | Y | 832 | Text | Available — title differs from cover index (Unresolved, see log) | — | Verified |
| 3 | G0.3 | NOTES & SPECIFICATIONS | General | Civil & Site (adj.) | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 3 | Y | 5928 | Text | Available | — | Verified |
| 4 | G0.4 | W.A.C. 332-130 COMPLIANCE SHEET | General | Civil & Site (adj.) | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 4 | Y | 7539 | Text | Available | — | Verified |
| 5 | G0.5 | PROCESS SCHEMATIC | General | Process & Mechanical (adj.) | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 5 | Y | 1 | Visual | Available | — | Verified |
| 6 | G0.6 | HYDRAULIC PROFILE | General | Process & Mechanical (adj.) | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 6 | Y | 1 | Visual | Available | — | Verified |
| 7 | G0.7 | DESIGN CRITERIA | General | Process & Mechanical (adj.) | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 7 | Y | 6410 | Text | Available | — | Verified |
| 8 | C0.1 | EXISTING CONDITIONS | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 8 | Y | 37 | Visual (rev1) | Available | — | Verified |
| 9 | C0.2 | T.E.S.C. NARRATIVE | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_2Part-1.pdf | 1 | Y | 8 | Visual | Available | — | Verified |
| 10 | C0.3 | T.E.S.C. PLAN (cover index) | Civil | Civil & Site | Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 10 | Y | — | Visual (rev2, provisional) | Available — native Part 1 p.10 (rev2; Plan_Set_Crosswalk.csv line 11) | — | Verified (native title block "10 OF 96"; Plan_Set_Crosswalk.csv) |
| 11 | C0.4 | T.E.S.C. DETAILS | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_2Part-3.pdf | 1 | Y | 238 | Visual (rev1) | Available | — | Verified |
| 12 | C0.5 | DEMOLITION PLAN | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_2Part-4.pdf | 1 | Y | 2 | Visual | Available | Cited — Add. 4 p.1, Clarification 1 | Verified |
| 13 | C0.6 | STAGING PLAN | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_2Part-5.pdf | 1 | Y | 8 | Visual | Available | — | Verified |
| 14 | C0.7 | WWTP INTERIM PLAN OF OPERATION (cover index) | Civil | Civil & Site | Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 14 | Y | — | Visual (rev2, provisional) | Available — native Part 1 p.14 (rev2; Plan_Set_Crosswalk.csv line 15) | — | Verified (native title block "14 OF 96"; Plan_Set_Crosswalk.csv) |
| 15 | C1.1 | SITE PIPING PLAN WITH GENERAL NOTES (cover index) | Civil | Civil & Site | Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 15 | Y | — | Visual (rev2, provisional) | Available — native Part 1 p.15 (rev2; Plan_Set_Crosswalk.csv line 16) | — | Verified (native title block "15 OF 96"; Plan_Set_Crosswalk.csv) |
| 16 | C1.2 | SITE DIMENSIONAL PLAN (cover index) | Civil | Civil & Site | Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 16 | Y | — | Visual (rev2, provisional) | Available — native Part 1 p.16 (rev2; Plan_Set_Crosswalk.csv line 17) | — | Verified (native title block "16 OF 96"; Plan_Set_Crosswalk.csv) |
| 17 | C1.3 | SITE PIPING PLAN WITH PIPING ID | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-1.pdf | 1 | Y | 1626 | Text | Available | Reissued — Add. 4 p.7 governs | Verified |
| 18 | C1.4 | SITE PIPING PLAN WITH BURIED VALVE ID | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-2.pdf | 1 | Y | 1000 | Text | Available | — | Verified |
| 19 | C1.5 | SITE PIPING PLAN WITH PIPE ELEVATIONS | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-3.pdf | 1 | Y | 334 | Text | Available | — | Verified |
| 20 | C2.1 | GRADING & STORM DRAINAGE PLAN (cover index) | Civil | Civil & Site | Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 20 | Y | — | Visual (rev2, provisional) | Available — native Part 1 p.20 (rev2; Plan_Set_Crosswalk.csv line 21) | — | Verified (native title block "20 OF 96"; Plan_Set_Crosswalk.csv) |
| 21 | C2.2 | STORM DRAINAGE PLAN & PROFILE | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-5.pdf | 1 | Y | 72 | Visual (rev1) | Available | — | Verified |
| 22 | C2.3 | STORM DRAINAGE PLAN & PROFILES (cover index) | Civil | Civil & Site | Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 22 | Y | — | Visual (rev2, provisional) | Available — native Part 1 p.22 (rev2; Plan_Set_Crosswalk.csv line 23) | — | Verified (native title block "22 OF 96"; Plan_Set_Crosswalk.csv) |
| 23 | C2.4 | STORM DRAINAGE PLAN & PROFILES | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-7.pdf | 1 | Y | 822 | Text | Available | — | Verified |
| 24 | C2.5 | RETAINING WALL PLAN & PROFILE | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-8.pdf | 1 | Y | 14 | Visual | Available | — | Verified |
| 25 | C2.6 | PAVING PLAN (cover index) | Civil | Civil & Site | Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 25 | Y | — | Visual (rev2, provisional) | Available — native Part 1 p.25 (rev2; Plan_Set_Crosswalk.csv line 26) | Cited — Add. 4 p.1, Clarification 1 | Verified (native title block "25 OF 96"; Plan_Set_Crosswalk.csv) |
| 26 | C3.1 | INFLUENT FLOW SPLITTER SITE PLAN | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-2.pdf | 1 | Y | 10 | Visual | Available | — | Verified |
| 27 | C3.2 | INFLUENT FLOW SPLITTER ELEVATIONS | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-3.pdf | 1 | Y | 75 | Visual (rev1) | Available | — | Verified |
| 28 | C3.3 | TRAIN 3 PLAN | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-4.pdf | 1 | N | 0 | Visual | Available | — | Verified-Visual |
| 29 | C3.4 | TRAIN 3 SECTION A | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-5.pdf | 1 | N | 0 | Visual | Available | — | Verified-Visual |
| 30 | C3.5 | TRAIN 3 SECTION B | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-6.pdf | 1 | Y | 36 | Visual (rev1) | Available | — | Verified |
| 31 | C4.1 | INFLUENT PUMP STATION | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-7.pdf | 1 | Y | 46 | Visual (rev1) | Available | — | Verified |
| 32 | C4.2 | 2W PUMP STATION PLAN & PROFILE | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-8.pdf | 1 | Y | 84 | Visual (rev1) | Available | — | Verified |
| 33 | C4.3 | 2W EQUIPMENT LAYOUT | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 1 | Y | 198 | Visual (rev1) | Available | — | Verified |
| 34 | C5.1 | UV DISINFECTION CHAMBER & DIGESTER PLAN | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 2 | Y | 483 | Text | Available | — | Verified |
| 35 | C5.2 | UV DISINFECTION CHAMBER & DIGESTER SECTION "A" | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 3 | Y | 110 | Visual (rev1) | Available | — | Verified |
| 36 | C5.3 | UV DISINFECTION CHAMBER & DIGESTER SECTION "B" | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 4 | Y | 137 | Visual (rev1) | Available | — | Verified |
| 37 | C5.4 | UV DISINFECTION EQUIPMENT | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 5 | Y | 272 | Visual (rev1) | Available | — | Verified |
| 38 | C6.1 | ROTARY FAN PRESS SYSTEM | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 6 | Y | 51 | Visual (rev1) | Available | — | Verified |
| 39 | C6.2 | SLUDGE PUMP AND VALVING AREA | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 7 | Y | 35 | Visual (rev1) | Available — title differs from cover index (Unresolved, see log) | — | Verified |
| 40 | C6.3 | DIGESTER BLOWER | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 8 | Y | 22 | Visual (rev1) | Available | — | Verified |
| 41 | C6.4 | BIOLOGICAL TREATMENT BLOWERS | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 1 | Y | 2 | Visual | Available | Reissued — Add. 4 p.6 governs | Verified |
| 42 | C6.5 | BIOLOGICAL TREATMENT BLOWER ELEVATION | Civil | Process & Mechanical | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 2 | Y | 2 | Visual | Available | — | Verified |
| 43 | C7.1 | CIVIL DETAILS | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 3 | Y | 216 | Visual (rev1) | Available | — | Verified |
| 44 | C7.2 | CIVIL DETAILS | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 4 | Y | 480 | Text | Available | — | Verified |
| 45 | C7.3 | CIVIL DETAILS | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 5 | N | 0 | Visual | Available | — | Verified-Visual |
| 46 | C7.4 | CIVIL DETAILS | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 6 | Y | 222 | Visual (rev1) | Available | — | Verified |
| 47 | C7.5 | CIVIL DETAILS | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 7 | Y | 363 | Text | Available | — | Verified |
| 48 | C7.6 | CIVIL DETAILS | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 8 | Y | 127 | Visual (rev1) | Available | — | Verified |
| 49 | C7.7 | CIVIL DETAILS (cover index) | Civil | Civil & Site | Pages from eswd-wwtp-upgrade-ph1-11x17-plans - Part 3.pdf | 1 | Y | — | Visual (rev2, provisional) | Available — native Part 3 p.1 (rev2; Plan_Set_Crosswalk.csv line 53) | — | Verified (native title block "49 OF 96"; Plan_Set_Crosswalk.csv) |
| 50 | C7.8 | CIVIL DETAILS (cover index) | Civil | Civil & Site | Pages from eswd-wwtp-upgrade-ph1-11x17-plans - Part 3.pdf | 2 | Y | — | Visual (rev2, provisional) | Available — native Part 3 p.2 (rev2; Plan_Set_Crosswalk.csv line 54) | — | Verified (native title block "50 OF 96"; Plan_Set_Crosswalk.csv) |
| 51 | C7.9 | FLOW METER & VALVE VAULT DETAILS (cover index) | Civil | Civil & Site | Pages from eswd-wwtp-upgrade-ph1-11x17-plans - Part 3.pdf | 3 | Y | — | Visual (rev2, provisional) | Available — native Part 3 p.3 (rev2; Plan_Set_Crosswalk.csv line 55) | — | Verified (native title block "51 OF 96"; Plan_Set_Crosswalk.csv) |
| 52 | C7.10 | FLOW METER & VALVE VAULT DETAILS | Civil | Civil & Site | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 4 | Y | 136 | Visual (rev1) | Available | — | Verified |
| 53 | A1.1 | BLOWER BUILDING PLAN | Architectural | Structural & Building | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 5 | Y | 108 | Visual (rev1) | Available | Reissued — Add. 4 p.4 governs | Verified |
| 54 | A1.2 | BLOWER BUILDING EXTERIOR ELEVATIONS 1 | Architectural | Structural & Building | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 6 | Y | 90 | Visual (rev1) | Available | Reissued — Add. 4 p.5 governs | Verified |
| 55 | A1.3 | BUILDING DETAILS | Architectural | Structural & Building | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 7 | Y | 434 | Text | Available | — | Verified |
| 56 | S1.1 | STRUCTURAL NOTES | Structural | Structural & Building | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 8 | N | 0 | Visual | Available — page total reads "OF 96" (native Part 3 p.8; Plan_Set_Crosswalk.csv line 60) | — | Verified-Visual |
| 57 | S2.1 | TRAIN 3 PLANS & SECTION | Structural | Structural & Building | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 1 | N | 0 | Visual | Available — page total reads "OF 96" (native Part 3 p.9; Plan_Set_Crosswalk.csv line 61) | — | Verified-Visual |
| 58 | S2.2 | UV DISINFECTION CHAMBER & DIGESTER PLAN & SECTIONS | Structural | Structural & Building | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 2 | N | 0 | Visual | Available — page total reads "OF 96" (native Part 3 p.10; Plan_Set_Crosswalk.csv line 62) | — | Verified-Visual |
| 59 | S2.3 | BLOWER BUILDING FOUNDATION PLAN & DETAILS | Structural | Structural & Building | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 3 | N | 0 | Visual | Available — page total reads "OF 96" (native Part 3 p.11; Plan_Set_Crosswalk.csv line 63) | Reissued — Add. 4 p.9 governs | Verified-Visual |
| 60 | S2.4 | PUMP STATION LID, GENERATOR PAD, & FLOW SPLITTER PAD | Structural | Structural & Building | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 4 | N | 0 | Visual | Available — page total reads "OF 96" (native Part 3 p.12; Plan_Set_Crosswalk.csv line 64) | — | Verified-Visual |
| 61 | S4.1 | TYP STRUCTURAL DETAILS | Structural | Structural & Building | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 5 | N | 0 | Visual | Available — page total reads "OF 96" (native Part 3 p.13; Plan_Set_Crosswalk.csv line 65) | Reissued — Add. 4 p.10 governs; Detail 8 cited p.3 | Verified-Visual |
| 62 | E0.1 | ELECTRICAL SYMBOLS AND ABBREVIATIONS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 6 | Y | 7209 | Text | Available | — | Verified |
| 63 | E0.2 | ELECTRICAL DEMOLITION SITE PLAN AND ONE LINE DIAGRAM | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 7 | Y | 1865 | Text | Available | — | Verified |
| 64 | E0.3 | OVERALL ELECTRICAL SITE PLAN | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 8 | Y | 1376 | Text | Available | — | Verified |
| 65 | E0.4 | AREA CLASSIFICATION SITE PLAN | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 1 | Y | 1999 | Text | Available — title differs from cover index (Unresolved, see log) | — | Verified |
| 66 | E1.1 | ELECTRIC SERVICE AREA PLAN | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 2 | Y | 1992 | Text | Available — title differs from cover index (Unresolved, see log) | — | Verified |
| 67 | E2.1 | BLOWER BUILDING POWER, CONTROL AND GROUNDING PLAN | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 3 | Y | 2572 | Text | Available | — | Verified |
| 68 | E2.2 | BLOWER BUILDING LIGHTING AND HVAC PLAN | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 4 | Y | 1211 | Text | Available | — | Verified |
| 69 | E3.1 | TRAIN NO.3 ELECTRICAL PLAN AND ELEVATION | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 5 | Y | 4061 | Text | Available — title differs from cover index (Unresolved, see log) | — | Verified |
| 70 | E4.1 | INFLUENT PUMP STATION, WAS, DEWATERING ELECTRICAL PLAN | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 6 | Y | 3769 | Text | Available | — | Verified |
| 71 | E4.2 | INFLUENT PUMP STATION ELECTRICAL PLAN AND ELEVATION | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 7 | Y | 2439 | Text | Available | — | Verified |
| 72 | E4.3 | 2W PUMP STATION ELECTRICAL PLAN AND ELEVATION | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 8 | Y | 1965 | Text | Available | — | Verified |
| 73 | E5.1 | UV DISINFECTION CHAMBER & DIGESTER ELECTRICAL PLAN AND ELEVATION | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 1 | Y | 3094 | Text | Available — title differs from cover index (Unresolved, see log) | — | Verified |
| 74 | E6.1 | ELECTRICAL ONE LINE DIAGRAM AND LOAD CALCULATIONS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 2 | Y | 1891 | Text | Available | — | Verified |
| 75 | E6.2 | ELECTRICAL PANEL SCHEDULES | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 3 | Y | 66 | Visual | Available | — | Verified |
| 76 | E6.3 | CONDUIT AND CONDUCTOR SCHEDULES | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 4 | Y | 24 | Visual | Available | — | Verified |
| 77 | E7.0 | CONTROL SYSTEM OVERVIEW | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 5 | Y | 1243 | Text | Available | — | Verified |
| 78 | E7.1 | MAIN PLC CONTROL PANEL ELEVATION | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 6 | Y | 474 | Text | Available | — | Verified |
| 79 | E7.2 | MAIN PLC CONTROL PANEL - POWER WIRING DIAGRAM | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 7 | Y | 1607 | Text | Available | — | Verified |
| 80 | E7.3 | MAIN PLC CONTROL PANEL - DIGITAL INPUTS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 8 | Y | 2027 | Text | Available | — | Verified |
| 81 | E7.4 | MAIN PLC CONTROL PANEL - DIGITAL OUTPUTS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 1 | Y | 927 | Text | Available | — | Verified |
| 82 | E7.5 | MAIN PLC CONTROL PANEL - ANALOG INPUTS - SHEET 1 | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 2 | Y | 643 | Text | Available | — | Verified |
| 83 | E7.6 | MAIN PLC CONTROL PANEL - ANALOG INPUTS - SHEET 2 | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 3 | Y | 694 | Text | Available | — | Verified |
| 84 | E7.7 | MAIN PLC CONTROL PANEL - ANALOG OUTPUTS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 4 | Y | 387 | Text | Available | — | Verified |
| 85 | E8.1 | INFLUENT PUMP STATION CONTROL PANEL ELEVATIONS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 5 | Y | 2772 | Text | Available | — | Verified |
| 86 | E8.2 | INFLUENT PUMP STATION CONTROL PANEL-POWER WIRING DIAGRAM | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 6 | Y | 701 | Text | Available — title differs from cover index (Unresolved, see log) | — | Verified |
| 87 | E8.3 | INFLUENT PUMP STATION CONTROL PANEL - DIGITAL INPUTS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 7 | Y | 1677 | Text | Available | — | Verified |
| 88 | E8.4 | INFLUENT PUMP STATION CONTROL PANEL - DIGITAL OUTPUTS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 8 | Y | 691 | Text | Available | — | Verified |
| 89 | E8.5 | INFLUENT PUMP STATION CONTROL PANEL - ANALOG INPUTS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 1 | Y | 662 | Text | Available | — | Verified |
| 90 | E8.6 | INFLUENT PUMP STATION CONTROL PANEL - ANALOG OUTPUTS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 2 | Y | 373 | Text | Available | — | Verified |
| 91 | E9.1 | BLOWER BUILDING MOTOR CONTROL CENTER ELEVATION | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 3 | Y | 1561 | Text | Available | Cited — Add. 4 p.1, Clarification 4 | Verified |
| 92 | E9.2 | BLOWER BUILDING MOTOR CONTROL CENTER - VFD WIRING DIAGRAMS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 4 | Y | 1277 | Text | Available | — | Verified |
| 93 | E9.3 | VENTILATION CONTROL PANEL ELEVATION AND WIRING DIAGRAM | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 5 | Y | 612 | Text | Available | — | Verified |
| 94 | E10.1 | ELECTRICAL DETAILS - SHEET 1 | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 6 | Y | 1596 | Text | Available | — | Verified |
| 95 | E10.2 | ELECTRICAL DETAILS - SHEET 2 | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 7 | Y | 1604 | Text | Available | — | Verified |
| 96 | E10.3 | STANDBY DIESEL GENERATOR ELEVATIONS | Electrical | Electrical & Controls | Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 8 | Y | 1025 | Text | Available | — | Verified |

## Sheets issued by addendum only

| Sheet | Title (title block) | Discipline | Lane | File | PDF p. | Text | Body chars | Read Method | Status | ID source |
|---|---|---|---|---|---|---|---|---|---|---|
| C1.6A | BURIED PIPING IN BUILDING | Civil | Civil & Site | addendum-no4-eswd.pdf | 8 | Y | 720 | Visual | Available as Add. 4 reissue; page "XX of 96"; cites Addendum #3 — base issue not in library (Unresolved) | Verified-Visual |

## Unresolved and logged items

| # | Item | Source A | Source B | Handling |
|---|---|---|---|---|
| 1 | E5.1 title — substantive | Cover index (plans_1 p.1): "UV DISINFECTION & CLARIFIER ELECTRICAL PLAN AND ELEVATION" | Title block (plans_10 p.1): "UV DISINFECTION CHAMBER & DIGESTER ELECTRICAL PLAN AND ELEVATION" | Index uses the title block; cover title kept as alias. Needs engineer confirmation or Addenda 1–3. |
| 2 | S2.2 title — wording | Cover index: "UV DISINFECTION & DIGESTER PLAN & SECTIONS" | Title block (plans_8 p.2): "UV DISINFECTION CHAMBER & DIGESTER PLAN & SECTIONS" | Index uses the title block; cover title kept as alias. |
| 3 | E0.4 title — wording | Cover index: "AREA CLASSIFICATION PLAN" | Title block (plans_9 p.1): "AREA CLASSIFICATION SITE PLAN" | Index uses the title block; cover title kept as alias. |
| 4 | E1.1 title — wording | Cover index: "ELECTRICAL SERVICE AREA PLAN" | Title block (plans_9 p.2): "ELECTRIC SERVICE AREA PLAN" | Index uses the title block; cover title kept as alias. |
| 5 | E3.1 title — wording | Cover index: "TRAIN CELL NO.3 ELECTRICAL PLAN AND ELEVATION" | Title block (plans_9 p.5): "TRAIN NO.3 ELECTRICAL PLAN AND ELEVATION" | Index uses the title block; cover title kept as alias. |
| 6 | E8.2 title — wording | Cover index: "INFLUENT PUMP STATION CONTROL PANEL - POWER WIRING DIAGRAMS" | Title block (plans_11 p.6): "INFLUENT PUMP STATION CONTROL PANEL-POWER WIRING DIAGRAM" | Index uses the title block; cover title kept as alias. |
| 7 | G0.2 title — cosmetic (& vs and) | Cover index: "LEGEND & ABBREVIATIONS - CIVIL & ARCHITECTURAL" | Title block (plans_1 p.2): "LEGEND AND ABBREVIATIONS - CIVIL & ARCHITECTURAL" | Index uses the title block; cover title kept as alias. |
| 8 | C6.2 title — cosmetic (& vs and) | Cover index: "SLUDGE PUMP & VALVING AREA" | Title block (plans_5 p.7): "SLUDGE PUMP AND VALVING AREA" | Index uses the title block; cover title kept as alias. |
| 9 | 10 sheets missing from library | G0.1 cover index | C0.3, C0.7, C1.1, C1.2, C2.1, C2.3, C2.6, C7.7, C7.8, C7.9 | Resolved (rev2): all 10 are in the library as native Part 1 pp.10, 14–16, 20, 22, 25 and Part 3 pp.1–3. Each title block reads its set page "N OF 96" in the native text layer (Plan_Set_Crosswalk.csv; Verified). Read Method provisional (Method). |
| 10 | S-sheet page total (low priority, decision 9) | All other sheets and the cover index: 96 sheets | Native title blocks: S1.1, S2.1–S2.4, S4.1 read "OF 96" on Part 3 pp.8–13 (Plan_Set_Crosswalk.csv lines 60–65; Verified-Visual). The Add. 4 reissues read "59 OF 96" (S2.3, Add. 4 p.9) and "61 OF 96" (S4.1, Add. 4 p.10) on the native Add. 4 (Verified-Visual, read 2026-09-30) | Resolved (rev2): the set total is 96. rev1's reading at stored image resolution was a misread (Inferred: every native title block and the cover index agree on 96). |
| 11 | C1.6A not on cover index | G0.1 index (C1.1–C1.5 only) | Add. 4 p.8: sheet C1.6A, page "XX of 96", note "SEE ADDENDUM #3" (Verified-Visual) | Indexed as addendum-only sheet; base issue needs Addendum 3. |
| 12 | Add. 4 reissues keep base title blocks | Add. 4 p.3 lists edits to A1.1, A1.2, C6.4, C1.3, C1.6A, S2.3, S4.1 | Reissued pages keep NOV 2, 2022 or 10-15-2021 dates; no Add. 4 revision entry (Verified-Visual) | Supersession tracked by addendum reference, not title block (Inferred design rule). |

## Resolved by decision

- plans_7 pp.1–3 (C7.4, C7.5, C7.6) duplicate plans_6 pp.6–8 with identical text (Verified). Only the plans_6 copies are indexed (decision 2).

## Page-level text extraction log

Every drawing page in the Claude Project copies: 89 base pages in file order, then 7 Add. 4 reissue pages. The 10 native-only sheets follow in their own table (rev2).

| File | PDF p. | Sheet | Text (Y/N) | Title block in text | Body chars | Read Method | Indexed | Note |
|---|---|---|---|---|---|---|---|---|
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 1 | G0.1 | Y | Y | 4242 | Text | Yes | Cover index source |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 2 | G0.2 | Y | Y | 832 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 3 | G0.3 | Y | Y | 5928 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 4 | G0.4 | Y | Y | 7539 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 5 | G0.5 | Y | Y | 1 | Visual | Yes | 1 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 6 | G0.6 | Y | Y | 1 | Visual | Yes | 1 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 7 | G0.7 | Y | Y | 6410 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_1.pdf | 8 | C0.1 | Y | Y | 37 | Visual | Yes | 37 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_2Part-1.pdf | 1 | C0.2 | Y | Y | 8 | Visual | Yes | 8 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_2Part-3.pdf | 1 | C0.4 | Y | Y | 238 | Visual | Yes | 238 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_2Part-4.pdf | 1 | C0.5 | Y | Y | 2 | Visual | Yes | 2 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_2Part-5.pdf | 1 | C0.6 | Y | Y | 8 | Visual | Yes | 8 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-1.pdf | 1 | C1.3 | Y | Y | 1626 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-2.pdf | 1 | C1.4 | Y | Y | 1000 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-3.pdf | 1 | C1.5 | Y | Y | 334 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-5.pdf | 1 | C2.2 | Y | Y | 72 | Visual | Yes | 72 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-7.pdf | 1 | C2.4 | Y | Y | 822 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_3Part-8.pdf | 1 | C2.5 | Y | Y | 14 | Visual | Yes | 14 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-2.pdf | 1 | C3.1 | Y | Y | 10 | Visual | Yes | 10 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-3.pdf | 1 | C3.2 | Y | Y | 75 | Visual | Yes | 75 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-4.pdf | 1 | C3.3 | N | N | 0 | Visual | Yes | Only the 11-02-2022 seal date extracts; ID Verified-Visual |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-5.pdf | 1 | C3.4 | N | N | 0 | Visual | Yes | Only the 11-02-2022 seal date extracts; ID Verified-Visual |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-6.pdf | 1 | C3.5 | Y | Y | 36 | Visual | Yes | 36 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-7.pdf | 1 | C4.1 | Y | Y | 46 | Visual | Yes | 46 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_4Part-8.pdf | 1 | C4.2 | Y | Y | 84 | Visual | Yes | 84 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 1 | C4.3 | Y | Y | 198 | Visual | Yes | 198 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 2 | C5.1 | Y | Y | 483 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 3 | C5.2 | Y | Y | 110 | Visual | Yes | 110 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 4 | C5.3 | Y | Y | 137 | Visual | Yes | 137 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 5 | C5.4 | Y | Y | 272 | Visual | Yes | 272 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 6 | C6.1 | Y | Y | 51 | Visual | Yes | 51 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 7 | C6.2 | Y | Y | 35 | Visual | Yes | 35 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_5.pdf | 8 | C6.3 | Y | Y | 22 | Visual | Yes | 22 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 1 | C6.4 | Y | Y | 2 | Visual | Yes | 2 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 2 | C6.5 | Y | Y | 2 | Visual | Yes | 2 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 3 | C7.1 | Y | Y | 216 | Visual | Yes | 216 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 4 | C7.2 | Y | Y | 480 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 5 | C7.3 | N | N | 0 | Visual | Yes | Only the 11-02-2022 seal date extracts; ID Verified-Visual |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 6 | C7.4 | Y | Y | 222 | Visual | Yes | 222 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 7 | C7.5 | Y | Y | 363 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_6.pdf | 8 | C7.6 | Y | Y | 127 | Visual | Yes | 127 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 1 | C7.4 | Y | Y | 222 | Visual | No | Duplicate of plans_6 p.6 — not indexed |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 2 | C7.5 | Y | Y | 363 | Text | No | Duplicate of plans_6 p.7 — not indexed |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 3 | C7.6 | Y | Y | 127 | Visual | No | Duplicate of plans_6 p.8 — not indexed |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 4 | C7.10 | Y | Y | 136 | Visual | Yes | 136 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 5 | A1.1 | Y | Y | 108 | Visual | Yes | 108 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 6 | A1.2 | Y | Y | 90 | Visual | Yes | 90 chars of body text |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 7 | A1.3 | Y | Y | 434 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_7.pdf | 8 | S1.1 | N | N | 0 | Visual | Yes | No text layer (vector drawing); ID Verified-Visual |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 1 | S2.1 | N | N | 0 | Visual | Yes | No text layer (vector drawing); ID Verified-Visual |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 2 | S2.2 | N | N | 0 | Visual | Yes | No text layer (vector drawing); ID Verified-Visual |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 3 | S2.3 | N | N | 0 | Visual | Yes | No text layer (vector drawing); ID Verified-Visual |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 4 | S2.4 | N | N | 0 | Visual | Yes | No text layer (vector drawing); ID Verified-Visual |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 5 | S4.1 | N | N | 0 | Visual | Yes | No text layer (vector drawing); ID Verified-Visual |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 6 | E0.1 | Y | Y | 7209 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 7 | E0.2 | Y | Y | 1865 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf | 8 | E0.3 | Y | Y | 1376 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 1 | E0.4 | Y | Y | 1999 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 2 | E1.1 | Y | Y | 1992 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 3 | E2.1 | Y | Y | 2572 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 4 | E2.2 | Y | Y | 1211 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 5 | E3.1 | Y | Y | 4061 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 6 | E4.1 | Y | Y | 3769 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 7 | E4.2 | Y | Y | 2439 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf | 8 | E4.3 | Y | Y | 1965 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 1 | E5.1 | Y | Y | 3094 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 2 | E6.1 | Y | Y | 1891 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 3 | E6.2 | Y | Y | 66 | Visual | Yes | schedule tables not in text layer |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 4 | E6.3 | Y | Y | 24 | Visual | Yes | schedule tables not in text layer |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 5 | E7.0 | Y | Y | 1243 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 6 | E7.1 | Y | Y | 474 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 7 | E7.2 | Y | Y | 1607 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf | 8 | E7.3 | Y | Y | 2027 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 1 | E7.4 | Y | Y | 927 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 2 | E7.5 | Y | Y | 643 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 3 | E7.6 | Y | Y | 694 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 4 | E7.7 | Y | Y | 387 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 5 | E8.1 | Y | Y | 2772 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 6 | E8.2 | Y | Y | 701 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 7 | E8.3 | Y | Y | 1677 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf | 8 | E8.4 | Y | Y | 691 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 1 | E8.5 | Y | Y | 662 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 2 | E8.6 | Y | Y | 373 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 3 | E9.1 | Y | Y | 1561 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 4 | E9.2 | Y | Y | 1277 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 5 | E9.3 | Y | Y | 612 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 6 | E10.1 | Y | Y | 1596 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 7 | E10.2 | Y | Y | 1604 | Text | Yes |  |
| Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf | 8 | E10.3 | Y | Y | 1025 | Text | Yes |  |
| addendum-no4-eswd.pdf | 4 | A1.1 | Y | Y | 832 | Visual | Yes (addendum) | Add. 4 reissue, governs over base; base sheet is Visual |
| addendum-no4-eswd.pdf | 5 | A1.2 | Y | Y | 244 | Visual | Yes (addendum) | Add. 4 reissue, governs over base; base sheet is Visual |
| addendum-no4-eswd.pdf | 6 | C6.4 | Y | Y | 427 | Visual | Yes (addendum) | Add. 4 reissue, governs over base; base sheet is Visual |
| addendum-no4-eswd.pdf | 7 | C1.3 | Y | Y | 2227 | Text | Yes (addendum) | Add. 4 reissue, governs over base |
| addendum-no4-eswd.pdf | 8 | C1.6A | Y | N | 720 | Visual | Yes (addendum) | Add. 4 reissue, governs over base; title block not in text layer; markup text only |
| addendum-no4-eswd.pdf | 9 | S2.3 | N | N | 0 | Visual | Yes (addendum) | Add. 4 reissue, governs over base; no text layer (vector drawing) |
| addendum-no4-eswd.pdf | 10 | S4.1 | N | N | 0 | Visual | Yes (addendum) | Add. 4 reissue, governs over base; no text layer (vector drawing) |

**Pages with no text layer (vector drawing) (11):** C3.3 (plans_4Part-4 p.1), C3.4 (plans_4Part-5 p.1), C7.3 (plans_6 p.5), S1.1 (plans_7 p.8), S2.1 (plans_8 p.1), S2.2 (plans_8 p.2), S2.3 (plans_8 p.3), S2.4 (plans_8 p.4), S4.1 (plans_8 p.5), S2.3 (Add. 4 p.9), S4.1 (Add. 4 p.10). All IDs were read from the page image (Verified-Visual). C1.6A (Add. 4 p.8) has text, but only its markups; its title block is not in the text layer.
Rev2: these are vector drawings, not raster images. On the native files each page has no text layer (C3.3, C3.4 and C7.3 hold only the 11-02-2022 seal date), and the only rasters are about 1 in. across or smaller (pdftotext, pdfimages on native Part 2 pp.1, 2, 18, Part 3 pp.8–13 and Add. 4 pp.9–10; Verified, 2026-09-30).

## Native-only pages (rev2)

The 10 sheets with no plans_N copy, read on the native parts on 2026-09-30 with pdftotext (Verified). "Text-layer chars" counts every non-space character on the page, title block included, so it is not the Body chars measure above.

| File | PDF p. | Set p. | Sheet | Text (Y/N) | Title block in text | Text-layer chars | Read Method | Indexed | Note |
|---|---|---|---|---|---|---|---|---|---|
| Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 10 | 10 | C0.3 | Y | Y | 570 | Visual (rev2, provisional) | Yes (rev2) | Title block reads "10 OF 96" in the text layer |
| Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 14 | 14 | C0.7 | Y | Y | 268 | Visual (rev2, provisional) | Yes (rev2) | Title block reads "14 OF 96" in the text layer |
| Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 15 | 15 | C1.1 | Y | Y | 582 | Visual (rev2, provisional) | Yes (rev2) | Title block reads "15 OF 96" in the text layer |
| Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 16 | 16 | C1.2 | Y | Y | 285 | Visual (rev2, provisional) | Yes (rev2) | Title block reads "16 OF 96" in the text layer |
| Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 20 | 20 | C2.1 | Y | Y | 557 | Visual (rev2, provisional) | Yes (rev2) | Title block reads "20 OF 96" in the text layer |
| Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 22 | 22 | C2.3 | Y | Y | 647 | Visual (rev2, provisional) | Yes (rev2) | Title block reads "22 OF 96" in the text layer |
| Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf | 25 | 25 | C2.6 | Y | Y | 547 | Visual (rev2, provisional) | Yes (rev2) | Title block reads "25 OF 96" in the text layer |
| Pages from eswd-wwtp-upgrade-ph1-11x17-plans - Part 3.pdf | 1 | 49 | C7.7 | Y | Y | 545 | Visual (rev2, provisional) | Yes (rev2) | Title block reads "49 OF 96" in the text layer |
| Pages from eswd-wwtp-upgrade-ph1-11x17-plans - Part 3.pdf | 2 | 50 | C7.8 | Y | Y | 695 | Visual (rev2, provisional) | Yes (rev2) | Title block reads "50 OF 96" in the text layer |
| Pages from eswd-wwtp-upgrade-ph1-11x17-plans - Part 3.pdf | 3 | 51 | C7.9 | Y | Y | 450 | Visual (rev2, provisional) | Yes (rev2) | Title block reads "51 OF 96" in the text layer |
