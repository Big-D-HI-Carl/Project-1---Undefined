# Project Ledger rev1 — Summary

Prompt 10: the expanded MTO. One row per component; the columns run left to right from "what and where" to everything connected to it. Built by `testbeds/eastsound/tools/build_ledger_rev1.py` (no LLM calls, deterministic). rev0 (`Project_Ledger.csv`, `.xlsx` and the by-CWP view) is unchanged.

## Files

| File | What it holds |
|---|---|
| Project_Ledger_rev1.csv | 449 rows × 39 columns, in `index/Ledger_Schema_rev1.csv` order |
| Project_Ledger_rev1.xlsx | Tabs Ledger, MTO Lines, Coverage, Candidates, Column Guide, plus Links (one row per link, each clickable) |
| MTO_Lines_rev1.csv | 114 MTO lines (machine copy of the MTO Lines tab) |
| Ledger_rev1_Summary.md | This file |

## Fill rate per band

Filled = the cell carries a fact. "None found", "Not linked", "Not stated", blanks, dashes, zero counts and an all-zero link basis count as not filled. Before = rev0's own values for the columns it had; columns new in rev1 start at 0.

| Band | Columns | Before (rev0, 447 rows) | After (447 base rows) | After (all 449 rows) |
|---|---|---|---|---|
| A Identity | 7 | 83.8% | 98.1% | 98.1% |
| B Where | 5 | 36.4% | 83.7% | 83.7% |
| C How much | 4 | 0.0% | 21.6% | 21.9% |
| D Specs & notes | 2 | 87.6% | 87.6% | 87.4% |
| E Submittals | 4 | 21.1% | 87.6% | 87.5% |
| F Inspections & tests | 4 | 21.1% | 83.4% | 83.0% |
| G Changes & issues | 5 | 4.0% | 57.8% | 57.7% |
| H Schedule & status | 5 | 0.0% | 99.6% | 99.2% |
| I Confidence & source | 3 | 99.7% | 99.7% | 99.7% |
| **All** | 39 | 36.7% | 80.4% | 80.3% |

Per column (filled cells; base rows before and after):

| Column | Band | Before | After |
|---|---|---|---|
| Ledger ID | A | new | 447 |
| Tag | A | 447 | 447 |
| Name | A | 447 | 447 |
| Discipline | A | 447 | 447 |
| Lane | A | 447 | 447 |
| Area/Building | A | 423 | 423 |
| Status | A | 410 | 410 |
| Drawing Sheets | B | 369 | 369 |
| Found On | B | new | 163 |
| CWP | B | new | 447 |
| CWP Name | B | new | 447 |
| Bid Item | B | 444 | 444 |
| Quantity | C | new | 72 |
| Unit | C | new | 105 |
| MTO Line IDs | C | new | 105 |
| Quantity Confidence | C | new | 105 |
| Spec Sections | D | 336 | 336 |
| Wiki Note(s) | D | 447 | 447 |
| Submittal Count | E | new | 396 |
| Submittal IDs | E | new | 396 |
| Submittal Link Basis | E | new | 396 |
| Submittal Req (Y/N) | E | 378 | 378 |
| Inspection/Test Count | F | new | 371 |
| Inspection/Test IDs | F | new | 371 |
| Inspection/Test Link Basis | F | new | 371 |
| Testing/Startup Req (Y/N) | F | 378 | 378 |
| Addenda | G | 90 | 90 |
| RFI IDs | G | new | 175 |
| Conflict/Gap Count | G | new | 358 |
| Conflict/Gap IDs | G | new | 358 |
| Exception Refs | G | new | 311 |
| Schedule Activity | H | new | 447 |
| Planned Start | H | new | 444 |
| Planned Finish | H | new | 444 |
| Submittal Approve-by | H | new | 444 |
| Tracker Status | H | new | 447 |
| Confidence | I | 447 | 447 |
| Source Citation | I | 447 | 447 |
| Notes | I | 443 | 443 |

## New rows

| Ledger ID | Tag | Page (a) | CWP (b) | Connected document (c) | Confidence |
|---|---|---|---|---|---|
| L-0448 | PROPOSED-Earthwork cut | C0.2 set p.9 [723.96,634.52,744.85,639.52] (Inferred, Bluebeam read) | CWP 31 — Discipline Civil + keyword "earthwork" (Inferred) | Wiki note C0.2 | Inferred |
| L-0449 | PROPOSED-Earthwork fill | C0.2 set p.9 [761.97,634.52,782.85,639.52] (Inferred, Bluebeam read) | CWP 31 — Discipline Civil + keyword "earthwork" (Inferred) | Wiki note C0.2 | Unresolved |

## Candidates held

403 candidates; 2 added, 401 not added (Candidates tab, one row each with the test result and reason).

| Category | Candidates |
|---|---|
| drawing reference or short label | 134 |
| I/O point or control-wiring designation | 119 |
| fails the three-part test | 63 |
| standard, rating or model | 49 |
| area | 25 |
| variant of a Ledger tag | 9 |
| added | 2 |
| held for a person | 2 |

Held for a person (pass the three-part test, but the documents name them as something other than a component, or as part of one):

- C-2W: Wiki note E4.3; Wiki note E6.3; Wiki note E7.3; Wiki note E7.4
- P-2W: Wiki note E4.3; Wiki note E6.3

## MTO

- Callout lines: the Prompt 9 tie rules run on every sheet. 177 leads (LF, EA, CY, SF, SY), 4 on base pages Add. 4 supersedes (left out), 119 callouts, 22 lines, 97 held (no tie, or reads disagree). The non-civil leads are notes, ratings and durations ("2 COATS", "100 AMPERES", "7 DAYS"), so none tie.
- Tag-count lines: 92, one EA per tagged component found on one of its cited sheets (best read kept). PROPOSED rows (no printed tag) and Pipe IDs (a run, measured in LF) get none. A range row counts only members that have no row of their own.
- Lines that count: 72 of 114. A line does not count when it is not Verified, its tie is ambiguous, it repeats a value already counted on another sheet, the row is measured in LF/CY/SF/SY (so a tag count would double count), or an open duplicate item names the row's twin.

| Unit | Lines that count | Total | Ledger rows with a total | Sum of Ledger Quantity |
|---|---|---|---|---|
| EA | 72 | 74 | 72 | 74 |

By row Status (the total mixes new, existing and demolished items; filter on Row Status in the MTO Lines tab):

| Unit | Row Status | Lines | Total |
|---|---|---|---|
| EA | Demolished | 1 | 1 |
| EA | Existing | 1 | 1 |
| EA | New | 58 | 60 |
| EA | Not stated | 12 | 12 |

Open duplicate items that name three or more rows, where two or more of those rows have a counted line. They are counted on each row; a person confirms they are separate components:

- OI-0005: L-0057 Hot Box #1, L-0058 Hot Box #2 — Hot Box duplicates: L-0337 PROPOSED-Hot-Box-1 and L-0338 PROPOSED-Hot-Box-2 (Electrical & Controls) read as the printed "Hot Box #1" / "Hot Box #2" on E4.3, the
- OI-0125: L-0256 BL-1, L-0257 BL-2, L-0258 BL-3, L-0259 BL-4 — Same item on more than one row (not combined): Biological treatment blowers (4): Count (4) and motor size (20 HP) agree.
- OI-0127: L-0272 EF-1, L-0273 EF-2 — Same item on more than one row (not combined): Blower Building exhaust fans (2): Count (2) and 1/2 HP agree.
- OI-0133: L-0322 EF-3, L-0323 EF-4, L-0324 EF-5 — Same item on more than one row (not combined): Existing dewatering / treatment building wall fans (3): Count (3) agrees.
- OI-0142: L-0140 DO #1 | DO-1, L-0141 DO #2 | DO-2 — Same item on more than one row (not combined): Train 3 dissolved oxygen and pH sensors: Contract & General carries separate DO and pH rows (package, Equipment A
- OI-0143: L-0287 IP-1, L-0288 IP-2, L-0289 IP-3, L-0290 IP-4 — Same item on more than one row (not combined): Influent pumps (4): Agree: 2 small (120–220 gpm, 3 HP) + 2 large (320–500 gpm, 5 HP).
- OI-0147: L-0291 F1 (Influent Pump Station), L-0292 F2 (Influent Pump Station), L-0293 F3 (Influent Pump Station), L-0294 F4 (Influent Pump Station) — Same item on more than one row (not combined): Influent Pump Station floats F1–F4: One Process & Mechanical roll-up row vs four Electrical & Controls rows.
- OI-0152: L-0330 2W-P1, L-0331 2W-P2 — Same item on more than one row (not combined): 2W pumps (2): Count agrees (1 duty, 1 standby; 5 HP).
- OI-0153: L-0332 LSH-111, L-0333 F2 (2W Pump Station), L-0334 F3 (2W Pump Station), L-0335 LSL-111 — Same item on more than one row (not combined): 2W floats F1–F4: One Process & Mechanical roll-up row vs four Electrical & Controls rows; E&C prints LSH-111 (F1)
- OI-0161: L-0341 UV1, L-0342 UV2 — Same item on more than one row (not combined): UV disinfection units (2): Two channels/units agree.

## Rules and judgment calls

- **Columns.** The 35 columns asked for, in bands A–I, plus Status (band A) and the two rev0 Y/N flags (bands E and F) so that no rev0 fact is lost. The tag column is named Confidence.
- **CWP.** Base rows keep their by-CWP assignment. A new row takes the first by-CWP rule that applies (1 spec section, 2 same-item group, 3 temporary, 4 keyword, 5 discipline). Rule 6 (parked in CWP 01) does not count as an assignment for the test. Rule 4 keeps the by-CWP keywords and adds "earthwork" from the name of CWP 31.
- **Connected document (test c).** A Wiki note or a Submittal/ITP line that names the candidate. Spec sections are reached through their Wiki notes (AGENTS.md rule 7; no library reads).
- **Never added:** I/O points (read only on E7.0–E9.3), areas, standards and ratings, drawing references; and variants of a Ledger tag (the same component).
- **Register links.** A Submittal or ITP line links to every row citing its spec section (the section's requirements apply to all its items); to the rows whose printed tag its text names (tag); and, only when it names no spec section, to the rows citing its sheet. The register's own Tag(s) column is Merge's computed linkage, so it is not used as a direct link.
- **Open items.** An item that names Ledger IDs links only to them (tag). One that names none links by spec section, else by sheet.
- **Found On** uses only assigned tag reads (Gate A). For PROPOSED rows it shows the boxed Drawing Sheets anchors from the crosswalk, with the match term and level as the OCR lane wrote them.
- **Confidence** of base rows is rev0's tag, unchanged. Prompt 9 proposals (sheet adds, Division 26 tags) are not applied; they still wait on the owner.
- **Links** are repo links on `main` (the native PDFs with #page, Project_Wiki.md and the register CSVs with line anchors).

## Tie-outs

| Check | Result | Detail |
|---|---|---|
| index/Ledger_Schema_rev1.csv = the rev1 columns | pass | 39 schema columns, 39 built |
| Ledger_ID_Map.csv = Project_Ledger.csv | pass | 447 IDs, 447 Ledger rows |
| Every base row has its by-CWP assignment | pass | 447 of 447 rows matched on Tag, Name, Lane and Area/Building |
| All 447 base rows present, in rev0 order, with rev0 Tag and Name | pass | 447 base rows, 449 rows in all |
| Ledger IDs unique and in the L-NNNN form | pass | 449 IDs |
| Every new row passes the three-part test | pass | 2 new rows; each has a sheet, set page and box, a CWP by rules 1-5 and a connected document |
| No new row is an I/O point, area, standard or drawing reference | pass | 2 new rows: the owner's earthwork rows and range members of Ledger tags only |
| No blank cell | pass | 0 blank cells |
| Every link carries its basis (tag, spec or sheet) | pass | 0 links without a basis |
| Direct links first in every link cell | pass | 0 cells out of order |
| Counts = linked IDs | pass | 0 rows differ |
| MTO totals tie to their lines (each row, and each unit overall) | pass | 0 rows differ; EA: 74 from 72 lines = 74 on 72 rows |
| Totals use Verified lines only | pass | 72 lines count |
| No MTO line is a dimension, elevation, slope or size | pass | units ['CY', 'EA', 'LF'] |
| MTO callouts = lines + held | pass | 119 callouts, 22 lines, 97 held |
| Every unmatched tag is a candidate | pass | 401 unmatched tags |

Links written: 7961 (Links tab).

## Inputs (SHA-256)

| File | SHA-256 |
|---|---|
| testbeds/eastsound/derived/issues/Open_Items.csv | 91ca7c6c57fdd0fff064489583359348537621b00a40ac197cb9145a5e53599b |
| testbeds/eastsound/derived/ocr/Ledger_Crosswalk.csv | 44e7e9bea3ac8c0382373941f4d1f0a24ae362b202475bf8b5d9301c597a4f33 |
| testbeds/eastsound/derived/ocr/Quantity_Hits.csv | d3cd54ae6eb626f74a43ef80b14762e8795f807421a776cbb17267b1f7362492 |
| testbeds/eastsound/derived/ocr/Sheet_Map.csv | dded6efd5223653a1f1762c7795669a36c26dda20bd53a12664cfe05150e1059 |
| testbeds/eastsound/derived/ocr/Spot_Check.csv | 6de8c58982d5706d2a7cd88042c7a2aabc02ed3ae7799ed597edbb6330092e66 |
| testbeds/eastsound/derived/ocr/Tag_Hits.csv | 67d180fbe800ca52bedcb235ae51676e80c5bfb2024a3b79d65b293128c7a435 |
| testbeds/eastsound/derived/ocr/Tag_Search_Forms.csv | d7b2ef0279be43da227bf4e111a7912761bb3200cb6c1208be51baca955a2f7f |
| testbeds/eastsound/derived/ocr/Unmatched_Tags.csv | 2e28cfde6795da42af48962a73634ce082b53ae5af57541062e8b1bb81f62e8f |
| testbeds/eastsound/derived/reconciliation/Ledger_ID_Map.csv | 1e6f2d57dab919b981bd89b55ed7706d8305aa449ad911dae54f36661607c697 |
| testbeds/eastsound/derived/reconciliation/New_Row_Candidates.csv | f8c5496e8620fd0ea459e87e31fa308292c4cfb0e1173f9867e2a41d121ec1e4 |
| testbeds/eastsound/derived/wiki/Wiki_Links.csv | 5601d7ba85517daa369c76cb53e5cd7cf497925dc701b9fa5e3f4fbd5de8a347 |
| testbeds/eastsound/derived/wiki/Wiki_Notes.csv | ba6e3559428c5a4276c84deb34f2a4b491c39b8a6393f17d0508003d06ef55f8 |
| testbeds/eastsound/index/Ledger_Schema_rev1.csv | 20ba26e8ffa1620fd89f483574ec645a64f8d4db6acf5ae5e3204a5aefc24519 |
| testbeds/eastsound/project/01_Project_Wiki/Project_Wiki.md | a3027eed7aadeee5aa7a40b6dc44de9e0a9756d8844d74fca6aa8e94a75210a2 |
| testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv | 0ed3af5640881f6fe2551b982d44653ddd92629cbcb5d47d68280a3ae6683e31 |
| testbeds/eastsound/project/02_Project_Ledger/Project_Ledger_by_CWP.csv | 7b34026476991d747d5edaaceafa2ab15ceee9fb5b8bda525bbbe7a8e9f8dcbf |
| testbeds/eastsound/project/03_Exceptions_and_Issues/Exception_Report.md | 9729ecc9c60a23c448226f1fae7fce18619cfe433408a0c3ad2d80e33b21c4dc |
| testbeds/eastsound/project/04_Submittals_ITP_QC/Inspection_Test_Plan.csv | 205cffe80849bf19601bd256f284c8ff592265227b856e3c435bbc83f9ef8414 |
| testbeds/eastsound/project/04_Submittals_ITP_QC/Submittal_Register.csv | 9980d8425dcf87708ad78afc4868434c2311a27a1e769f629d0cafde9600de64 |
| testbeds/eastsound/project/05_Schedule_and_Tracker/Installation_Tracker_by_CWP.csv | 3d5bd28446ba2451573fdb547e27ecad12ed63ad012746449089d1beddef6fff |
| testbeds/eastsound/project/05_Schedule_and_Tracker/Schedule_by_CWP.csv | eba6fb7c55b281c5749cbcf6f10e2a75b69e65c87db2cc5bc2935029caef13fa |
| testbeds/eastsound/tools/build_reconciliation.py | 06b50b60658c89520244491e6cea6a2e5e7cea952a508dcbcb520e2eb18845eb |
| testbeds/eastsound/tools/extract_drawing_text.py | 0e61e19737aa0acd351b04bb1fe1276502ad57f626b99e59df261b62d1bbebd1 |
