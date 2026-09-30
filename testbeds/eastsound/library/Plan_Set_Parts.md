# Plan set parts — 11x17 bid set, native

A note beside the three native parts of the 11x17 bid plan set. It maps each file page to its set page and sheet, and to the register copy the index files cite.

Short names used here:
- **Part 1** = `Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf`
- **Part 2** = `Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 2.pdf`
- **Part 3** = `Pages from eswd-wwtp-upgrade-ph1-11x17-plans - Part 3.pdf`
- **Sheet Index** = `testbeds/eastsound/index/01_Sheet_Index_rev1.md`
- **Register** = `testbeds/eastsound/index/00_Document_Register_rev1.md`
- plans_N is as the Register defines it.

## Parts

| Part | Pages | Set pages | Set p. = | First page | Last page | Bytes | SHA-256 |
|---|---|---|---|---|---|---|---|
| Part 1 | 27 | 1–27 | file p. | G0.1, "1 OF 96" | C3.2, "27 OF 96" | 16,402,728 | 9ca45d82bf86d16d3e2ce57eb76dccf597c497a7dc7f062fc7a171c4bc2c8d57 |
| Part 2 | 21 | 28–48 | file p. + 27 | C3.3 (image-only; Inferred) | C7.6, "48 OF 96" | 6,964,760 | 1176b4b114c25cd51383cb47896d5a651e4eb0f3363d17d651269f3d2a15dd84 |
| Part 3 | 48 | 49–96 | file p. + 48 | C7.7, "49 OF 96" | E10.3, "96 OF 96" | 16,904,936 | ffe9e975ceb153cab60328a2459d826f96f96e0edaa77e0279a1d27e2e6de5fa |

## How this was read

- **Page counts** come from each file's page tree (Verified).
- **Sheet and set page** are read in the native text layer, from the title block (Verified, 87 of 96 pages):
  - the sheet number is the one immediately before the PAGE/SHEET labels;
  - the set page is the number before "OF";
  - detail callouts earlier in the text stream are ignored. For example, C4.1, C5.1 and C5.3 (set pp.31, 34 and 36) carry C7.2 callouts ahead of their title blocks.
- **Image-only pages (9):** set pp.28, 29, 45 and 56–61 have no title-block text. Their sheets are Inferred: their neighbours read consecutive "N OF 96" values, and they're the same 9 sheets the Sheet Index marks Text = N.
- **Title** is copied from the Sheet Index's "Title (title block)" column, and that file's own tags apply. "(cover index)" marks sheets the Sheet Index had only from the G0.1 cover index.
- **Register copy** comes from the Sheet Index File and PDF p. columns. "None" means the Sheet Index lists the sheet as not in library.
- **File metadata** (Verified, PDF Info dictionary): Creator "Autodesk Civil 3D 2022", Producer "pdfplot16.hdi 16.01.173.00000", CreationDate 2026-09-30. None of the three carries a Bluebeam OCR layer.

## Findings

- **All 10 sheets the Sheet Index lists as not in library are here** (Verified): set pp.10, 14–16, 20, 22 and 25 (Part 1), and set pp.49–51 (Part 3 pp.1–3).
- **The Register has no rows for these three files** (Unresolved). It lists the plans_N extracts instead (rows 5–30), and none of those extracts is in this library. Index citations in plans_N form resolve only through the tables below until the Setup role, which owns `index/`, adds rows for the Parts.
- **C1.6A is not in the 96-page set.** It's an addendum-only sheet: Add. 4 p.8, "XX of 96".
- **The Bluebeam OCR copies cover the same 96 set pages:** `testbeds/eastsound/derived/bluebeam-ocr/`, OCR Part 1 = set pp.1–48, OCR Part 2 = set pp.49–96. Their text is Inferred only (AGENTS.md).

## File page → set page

### Part 1

| File p. | Set p. | Sheet | Title | How the sheet is known | Register copy |
|---|---|---|---|---|---|
| 1 | 1 | G0.1 | COVER SHEET | Verified: title block "G0.1", "1 OF 96" | plans_1 p.1 |
| 2 | 2 | G0.2 | LEGEND AND ABBREVIATIONS - CIVIL & ARCHITECTURAL | Verified: title block "G0.2", "2 OF 96" | plans_1 p.2 |
| 3 | 3 | G0.3 | NOTES & SPECIFICATIONS | Verified: title block "G0.3", "3 OF 96" | plans_1 p.3 |
| 4 | 4 | G0.4 | W.A.C. 332-130 COMPLIANCE SHEET | Verified: title block "G0.4", "4 OF 96" | plans_1 p.4 |
| 5 | 5 | G0.5 | PROCESS SCHEMATIC | Verified: title block "G0.5", "5 OF 96" | plans_1 p.5 |
| 6 | 6 | G0.6 | HYDRAULIC PROFILE | Verified: title block "G0.6", "6 OF 96" | plans_1 p.6 |
| 7 | 7 | G0.7 | DESIGN CRITERIA | Verified: title block "G0.7", "7 OF 96" | plans_1 p.7 |
| 8 | 8 | C0.1 | EXISTING CONDITIONS | Verified: title block "C0.1", "8 OF 96" | plans_1 p.8 |
| 9 | 9 | C0.2 | T.E.S.C. NARRATIVE | Verified: title block "C0.2", "9 OF 96" | plans_2Part-1 p.1 |
| 10 | 10 | C0.3 | T.E.S.C. PLAN (cover index) | Verified: title block "C0.3", "10 OF 96" | None (Sheet Index: not in library) |
| 11 | 11 | C0.4 | T.E.S.C. DETAILS | Verified: title block "C0.4", "11 OF 96" | plans_2Part-3 p.1 |
| 12 | 12 | C0.5 | DEMOLITION PLAN | Verified: title block "C0.5", "12 OF 96" | plans_2Part-4 p.1 |
| 13 | 13 | C0.6 | STAGING PLAN | Verified: title block "C0.6", "13 OF 96" | plans_2Part-5 p.1 |
| 14 | 14 | C0.7 | WWTP INTERIM PLAN OF OPERATION (cover index) | Verified: title block "C0.7", "14 OF 96" | None (Sheet Index: not in library) |
| 15 | 15 | C1.1 | SITE PIPING PLAN WITH GENERAL NOTES (cover index) | Verified: title block "C1.1", "15 OF 96" | None (Sheet Index: not in library) |
| 16 | 16 | C1.2 | SITE DIMENSIONAL PLAN (cover index) | Verified: title block "C1.2", "16 OF 96" | None (Sheet Index: not in library) |
| 17 | 17 | C1.3 | SITE PIPING PLAN WITH PIPING ID | Verified: title block "C1.3", "17 OF 96" | plans_3Part-1 p.1 |
| 18 | 18 | C1.4 | SITE PIPING PLAN WITH BURIED VALVE ID | Verified: title block "C1.4", "18 OF 96" | plans_3Part-2 p.1 |
| 19 | 19 | C1.5 | SITE PIPING PLAN WITH PIPE ELEVATIONS | Verified: title block "C1.5", "19 OF 96" | plans_3Part-3 p.1 |
| 20 | 20 | C2.1 | GRADING & STORM DRAINAGE PLAN (cover index) | Verified: title block "C2.1", "20 OF 96" | None (Sheet Index: not in library) |
| 21 | 21 | C2.2 | STORM DRAINAGE PLAN & PROFILE | Verified: title block "C2.2", "21 OF 96" | plans_3Part-5 p.1 |
| 22 | 22 | C2.3 | STORM DRAINAGE PLAN & PROFILES (cover index) | Verified: title block "C2.3", "22 OF 96" | None (Sheet Index: not in library) |
| 23 | 23 | C2.4 | STORM DRAINAGE PLAN & PROFILES | Verified: title block "C2.4", "23 OF 96" | plans_3Part-7 p.1 |
| 24 | 24 | C2.5 | RETAINING WALL PLAN & PROFILE | Verified: title block "C2.5", "24 OF 96" | plans_3Part-8 p.1 |
| 25 | 25 | C2.6 | PAVING PLAN (cover index) | Verified: title block "C2.6", "25 OF 96" | None (Sheet Index: not in library) |
| 26 | 26 | C3.1 | INFLUENT FLOW SPLITTER SITE PLAN | Verified: title block "C3.1", "26 OF 96" | plans_4Part-2 p.1 |
| 27 | 27 | C3.2 | INFLUENT FLOW SPLITTER ELEVATIONS | Verified: title block "C3.2", "27 OF 96" | plans_4Part-3 p.1 |

### Part 2

| File p. | Set p. | Sheet | Title | How the sheet is known | Register copy |
|---|---|---|---|---|---|
| 1 | 28 | C3.3 | TRAIN 3 PLAN | Inferred: no title-block text (image-only); sequence between neighbours | plans_4Part-4 p.1 |
| 2 | 29 | C3.4 | TRAIN 3 SECTION A | Inferred: no title-block text (image-only); sequence between neighbours | plans_4Part-5 p.1 |
| 3 | 30 | C3.5 | TRAIN 3 SECTION B | Verified: title block "C3.5", "30 OF 96" | plans_4Part-6 p.1 |
| 4 | 31 | C4.1 | INFLUENT PUMP STATION | Verified: title block "C4.1", "31 OF 96" | plans_4Part-7 p.1 |
| 5 | 32 | C4.2 | 2W PUMP STATION PLAN & PROFILE | Verified: title block "C4.2", "32 OF 96" | plans_4Part-8 p.1 |
| 6 | 33 | C4.3 | 2W EQUIPMENT LAYOUT | Verified: title block "C4.3", "33 OF 96" | plans_5 p.1 |
| 7 | 34 | C5.1 | UV DISINFECTION CHAMBER & DIGESTER PLAN | Verified: title block "C5.1", "34 OF 96" | plans_5 p.2 |
| 8 | 35 | C5.2 | UV DISINFECTION CHAMBER & DIGESTER SECTION "A" | Verified: title block "C5.2", "35 OF 96" | plans_5 p.3 |
| 9 | 36 | C5.3 | UV DISINFECTION CHAMBER & DIGESTER SECTION "B" | Verified: title block "C5.3", "36 OF 96" | plans_5 p.4 |
| 10 | 37 | C5.4 | UV DISINFECTION EQUIPMENT | Verified: title block "C5.4", "37 OF 96" | plans_5 p.5 |
| 11 | 38 | C6.1 | ROTARY FAN PRESS SYSTEM | Verified: title block "C6.1", "38 OF 96" | plans_5 p.6 |
| 12 | 39 | C6.2 | SLUDGE PUMP AND VALVING AREA | Verified: title block "C6.2", "39 OF 96" | plans_5 p.7 |
| 13 | 40 | C6.3 | DIGESTER BLOWER | Verified: title block "C6.3", "40 OF 96" | plans_5 p.8 |
| 14 | 41 | C6.4 | BIOLOGICAL TREATMENT BLOWERS | Verified: title block "C6.4", "41 OF 96" | plans_6 p.1 |
| 15 | 42 | C6.5 | BIOLOGICAL TREATMENT BLOWER ELEVATION | Verified: title block "C6.5", "42 OF 96" | plans_6 p.2 |
| 16 | 43 | C7.1 | CIVIL DETAILS | Verified: title block "C7.1", "43 OF 96" | plans_6 p.3 |
| 17 | 44 | C7.2 | CIVIL DETAILS | Verified: title block "C7.2", "44 OF 96" | plans_6 p.4 |
| 18 | 45 | C7.3 | CIVIL DETAILS | Inferred: no title-block text (image-only); sequence between neighbours | plans_6 p.5 |
| 19 | 46 | C7.4 | CIVIL DETAILS | Verified: title block "C7.4", "46 OF 96" | plans_6 p.6 |
| 20 | 47 | C7.5 | CIVIL DETAILS | Verified: title block "C7.5", "47 OF 96" | plans_6 p.7 |
| 21 | 48 | C7.6 | CIVIL DETAILS | Verified: title block "C7.6", "48 OF 96" | plans_6 p.8 |

### Part 3

| File p. | Set p. | Sheet | Title | How the sheet is known | Register copy |
|---|---|---|---|---|---|
| 1 | 49 | C7.7 | CIVIL DETAILS (cover index) | Verified: title block "C7.7", "49 OF 96" | None (Sheet Index: not in library) |
| 2 | 50 | C7.8 | CIVIL DETAILS (cover index) | Verified: title block "C7.8", "50 OF 96" | None (Sheet Index: not in library) |
| 3 | 51 | C7.9 | FLOW METER & VALVE VAULT DETAILS (cover index) | Verified: title block "C7.9", "51 OF 96" | None (Sheet Index: not in library) |
| 4 | 52 | C7.10 | FLOW METER & VALVE VAULT DETAILS | Verified: title block "C7.10", "52 OF 96" | plans_7 p.4 |
| 5 | 53 | A1.1 | BLOWER BUILDING PLAN | Verified: title block "A1.1", "53 OF 96" | plans_7 p.5 |
| 6 | 54 | A1.2 | BLOWER BUILDING EXTERIOR ELEVATIONS 1 | Verified: title block "A1.2", "54 OF 96" | plans_7 p.6 |
| 7 | 55 | A1.3 | BUILDING DETAILS | Verified: title block "A1.3", "55 OF 96" | plans_7 p.7 |
| 8 | 56 | S1.1 | STRUCTURAL NOTES | Inferred: no title-block text (image-only); sequence between neighbours | plans_7 p.8 |
| 9 | 57 | S2.1 | TRAIN 3 PLANS & SECTION | Inferred: no title-block text (image-only); sequence between neighbours | plans_8 p.1 |
| 10 | 58 | S2.2 | UV DISINFECTION CHAMBER & DIGESTER PLAN & SECTIONS | Inferred: no title-block text (image-only); sequence between neighbours | plans_8 p.2 |
| 11 | 59 | S2.3 | BLOWER BUILDING FOUNDATION PLAN & DETAILS | Inferred: no title-block text (image-only); sequence between neighbours | plans_8 p.3 |
| 12 | 60 | S2.4 | PUMP STATION LID, GENERATOR PAD, & FLOW SPLITTER PAD | Inferred: no title-block text (image-only); sequence between neighbours | plans_8 p.4 |
| 13 | 61 | S4.1 | TYP STRUCTURAL DETAILS | Inferred: no title-block text (image-only); sequence between neighbours | plans_8 p.5 |
| 14 | 62 | E0.1 | ELECTRICAL SYMBOLS AND ABBREVIATIONS | Verified: title block "E0.1", "62 OF 96" | plans_8 p.6 |
| 15 | 63 | E0.2 | ELECTRICAL DEMOLITION SITE PLAN AND ONE LINE DIAGRAM | Verified: title block "E0.2", "63 OF 96" | plans_8 p.7 |
| 16 | 64 | E0.3 | OVERALL ELECTRICAL SITE PLAN | Verified: title block "E0.3", "64 OF 96" | plans_8 p.8 |
| 17 | 65 | E0.4 | AREA CLASSIFICATION SITE PLAN | Verified: title block "E0.4", "65 OF 96" | plans_9 p.1 |
| 18 | 66 | E1.1 | ELECTRIC SERVICE AREA PLAN | Verified: title block "E1.1", "66 OF 96" | plans_9 p.2 |
| 19 | 67 | E2.1 | BLOWER BUILDING POWER, CONTROL AND GROUNDING PLAN | Verified: title block "E2.1", "67 OF 96" | plans_9 p.3 |
| 20 | 68 | E2.2 | BLOWER BUILDING LIGHTING AND HVAC PLAN | Verified: title block "E2.2", "68 OF 96" | plans_9 p.4 |
| 21 | 69 | E3.1 | TRAIN NO.3 ELECTRICAL PLAN AND ELEVATION | Verified: title block "E3.1", "69 OF 96" | plans_9 p.5 |
| 22 | 70 | E4.1 | INFLUENT PUMP STATION, WAS, DEWATERING ELECTRICAL PLAN | Verified: title block "E4.1", "70 OF 96" | plans_9 p.6 |
| 23 | 71 | E4.2 | INFLUENT PUMP STATION ELECTRICAL PLAN AND ELEVATION | Verified: title block "E4.2", "71 OF 96" | plans_9 p.7 |
| 24 | 72 | E4.3 | 2W PUMP STATION ELECTRICAL PLAN AND ELEVATION | Verified: title block "E4.3", "72 OF 96" | plans_9 p.8 |
| 25 | 73 | E5.1 | UV DISINFECTION CHAMBER & DIGESTER ELECTRICAL PLAN AND ELEVATION | Verified: title block "E5.1", "73 OF 96" | plans_10 p.1 |
| 26 | 74 | E6.1 | ELECTRICAL ONE LINE DIAGRAM AND LOAD CALCULATIONS | Verified: title block "E6.1", "74 OF 96" | plans_10 p.2 |
| 27 | 75 | E6.2 | ELECTRICAL PANEL SCHEDULES | Verified: title block "E6.2", "75 OF 96" | plans_10 p.3 |
| 28 | 76 | E6.3 | CONDUIT AND CONDUCTOR SCHEDULES | Verified: title block "E6.3", "76 OF 96" | plans_10 p.4 |
| 29 | 77 | E7.0 | CONTROL SYSTEM OVERVIEW | Verified: title block "E7.0", "77 OF 96" | plans_10 p.5 |
| 30 | 78 | E7.1 | MAIN PLC CONTROL PANEL ELEVATION | Verified: title block "E7.1", "78 OF 96" | plans_10 p.6 |
| 31 | 79 | E7.2 | MAIN PLC CONTROL PANEL - POWER WIRING DIAGRAM | Verified: title block "E7.2", "79 OF 96" | plans_10 p.7 |
| 32 | 80 | E7.3 | MAIN PLC CONTROL PANEL - DIGITAL INPUTS | Verified: title block "E7.3", "80 OF 96" | plans_10 p.8 |
| 33 | 81 | E7.4 | MAIN PLC CONTROL PANEL - DIGITAL OUTPUTS | Verified: title block "E7.4", "81 OF 96" | plans_11 p.1 |
| 34 | 82 | E7.5 | MAIN PLC CONTROL PANEL - ANALOG INPUTS - SHEET 1 | Verified: title block "E7.5", "82 OF 96" | plans_11 p.2 |
| 35 | 83 | E7.6 | MAIN PLC CONTROL PANEL - ANALOG INPUTS - SHEET 2 | Verified: title block "E7.6", "83 OF 96" | plans_11 p.3 |
| 36 | 84 | E7.7 | MAIN PLC CONTROL PANEL - ANALOG OUTPUTS | Verified: title block "E7.7", "84 OF 96" | plans_11 p.4 |
| 37 | 85 | E8.1 | INFLUENT PUMP STATION CONTROL PANEL ELEVATIONS | Verified: title block "E8.1", "85 OF 96" | plans_11 p.5 |
| 38 | 86 | E8.2 | INFLUENT PUMP STATION CONTROL PANEL-POWER WIRING DIAGRAM | Verified: title block "E8.2", "86 OF 96" | plans_11 p.6 |
| 39 | 87 | E8.3 | INFLUENT PUMP STATION CONTROL PANEL - DIGITAL INPUTS | Verified: title block "E8.3", "87 OF 96" | plans_11 p.7 |
| 40 | 88 | E8.4 | INFLUENT PUMP STATION CONTROL PANEL - DIGITAL OUTPUTS | Verified: title block "E8.4", "88 OF 96" | plans_11 p.8 |
| 41 | 89 | E8.5 | INFLUENT PUMP STATION CONTROL PANEL - ANALOG INPUTS | Verified: title block "E8.5", "89 OF 96" | plans_12 p.1 |
| 42 | 90 | E8.6 | INFLUENT PUMP STATION CONTROL PANEL - ANALOG OUTPUTS | Verified: title block "E8.6", "90 OF 96" | plans_12 p.2 |
| 43 | 91 | E9.1 | BLOWER BUILDING MOTOR CONTROL CENTER ELEVATION | Verified: title block "E9.1", "91 OF 96" | plans_12 p.3 |
| 44 | 92 | E9.2 | BLOWER BUILDING MOTOR CONTROL CENTER - VFD WIRING DIAGRAMS | Verified: title block "E9.2", "92 OF 96" | plans_12 p.4 |
| 45 | 93 | E9.3 | VENTILATION CONTROL PANEL ELEVATION AND WIRING DIAGRAM | Verified: title block "E9.3", "93 OF 96" | plans_12 p.5 |
| 46 | 94 | E10.1 | ELECTRICAL DETAILS - SHEET 1 | Verified: title block "E10.1", "94 OF 96" | plans_12 p.6 |
| 47 | 95 | E10.2 | ELECTRICAL DETAILS - SHEET 2 | Verified: title block "E10.2", "95 OF 96" | plans_12 p.7 |
| 48 | 96 | E10.3 | STANDBY DIESEL GENERATOR ELEVATIONS | Verified: title block "E10.3", "96 OF 96" | plans_12 p.8 |
