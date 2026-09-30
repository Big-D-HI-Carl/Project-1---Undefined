# OCR lane findings

Machine reads from `testbeds/eastsound/tools/extract_drawing_text.py`. Text-layer reads are Verified; every OCR and Bluebeam read is Inferred until checked on the page image; every quantity is a lead, not a takeoff (README.md, confidence rule). Nothing here is in the Ledger or the MTO. Page and box cites use `Page Key` and PDF points (origin top left, rotation applied).

## Summary

- Pages: 96 set pages and 7 Addendum 4 reissue pages (`Sheet_Map.csv`).
- Words kept: 25317 text layer, 51830 OCR (Tesseract, not under a text-layer word), 45042 Bluebeam.
- Tag hits: 839 (604 assigned, 234 off-citation, short form, 1 qualifier (E) not on line).
- Quantity leads: 1903; in a keyed note: 161; with a tag within 24 pt: 230.
- Ledger rows in the crosswalk: 447. Tag-shaped text with no Ledger row: 401 distinct.

## Title blocks

- Sheet number read in the title block matches 01 on 96 of 96 set pages and 7 of 7 Addendum 4 pages.
  - Mismatches: none.
- Title read matches 01 on 103 of 103 pages (01's "(cover index)" marker ignored).
- 12 pages have no title block in the text layer and were read by the rotated title-strip OCR pass (Inferred): 028 C3.3, 029 C3.4, 045 C7.3, 056 S1.1, 057 S2.1, 058 S2.2, 059 S2.3, 060 S2.4, 061 S4.1, add4_p08 C1.6A, add4_p09 S2.3, add4_p10 S4.1. They are vector drawings without a text layer, not raster images.
- S-sheet page totals: S1.1 "56 OF 96", S2.1 "57 OF 96", S2.2 "58 OF 96", S2.3 "59 OF 96", S2.4 "60 OF 96", S4.1 "61 OF 96". 01 item 10 logged "OF 98" at stored image resolution; the native pages read OF 96 (OCR, Inferred): 056 1174.08,726.96,1178.88,761.04; 057 1174.32,727.20,1179.00,763.56; 058 1174.08,726.96,1178.88,759.84; 059 1174.08,726.96,1178.88,762.96; 060 1174.08,726.96,1178.88,762.72; 061 1174.08,726.96,1178.88,762.48.
- C1.6A (Add. 4 p.8) reads "XX OF 96" 1171.80,722.88,1179.36,765.72. It reissues no page of the 96-sheet set, so it governs nothing here (Unresolved: the base issue cites Addendum 3, not in the library).
- Addendum 4 supersession is taken from 01, not from title-block dates (the reissues keep the base dates): add4_p04 A1.1 governs set p.53; add4_p05 A1.2 governs set p.54; add4_p06 C6.4 governs set p.41; add4_p07 C1.3 governs set p.17; add4_p09 S2.3 governs set p.59; add4_p10 S4.1 governs set p.61.

## Sheets 01 lists as not in library, found

01 lists 10 sheets as not in library. All 10 are in the native parts and read in their title blocks:

| Set p. | 01 sheet | Read | Method | BBox (pt) | Native page |
|---|---|---|---|---|---|
| 10 | C0.3 | C0.3 | text-layer | 1131.16,727.21,1146.10,761.16 | Part 1 p.10 |
| 14 | C0.7 | C0.7 | text-layer | 1131.16,727.21,1146.10,761.16 | Part 1 p.14 |
| 15 | C1.1 | C1.1 | text-layer | 1131.16,727.21,1146.10,761.16 | Part 1 p.15 |
| 16 | C1.2 | C1.2 | text-layer | 1131.16,727.21,1146.10,761.16 | Part 1 p.16 |
| 20 | C2.1 | C2.1 | text-layer | 1131.16,727.21,1146.10,761.16 | Part 1 p.20 |
| 22 | C2.3 | C2.3 | text-layer | 1131.16,727.21,1146.10,761.16 | Part 1 p.22 |
| 25 | C2.6 | C2.6 | text-layer | 1131.16,727.21,1146.10,761.16 | Part 1 p.25 |
| 49 | C7.7 | C7.7 | text-layer | 1131.16,727.21,1146.10,761.16 | Part 3 p.1 |
| 50 | C7.8 | C7.8 | text-layer | 1131.16,727.21,1146.10,761.16 | Part 3 p.2 |
| 51 | C7.9 | C7.9 | text-layer | 1131.16,727.21,1146.10,761.16 | Part 3 p.3 |

## Known values (Test 5)

- C2.1 149 LF: bluebeam-ocr, 020 988.15,225.60,1000.81,229.60, keyed note 6 (read; Inferred): "(6) = 149 LF OF 6’ CHAIN LINK" (Inferred).
- C2.1 149 LF: ocr, 020 1000.08,224.64,1018.80,228.96, keyed note 6 (read; Inferred): "149 LF OF" (Inferred).
- C2.1 134 LF: ocr, 020 1000.08,272.16,1018.80,276.48, keyed note 8 (by order; Inferred): "©) = 134 LF OF" (Inferred).
- C2.1 134 LF: bluebeam-ocr, 020 1000.10,273.15,1012.76,277.15, keyed note 8 (by order; Inferred): "134 LF OF 6’ CHAIN LINK" (Inferred).
- SD-3 on C2.3: text layer, 022 773.83,318.00,818.54,330.57 (Verified).
- SD-3 on C2.3: text layer, 022 795.79,732.72,840.50,745.29 (Verified).

## Chain link fence rows: stated, not reconciled

- C2.1 keyed notes 6 and 8 read 149 LF and 134 LF of 6' chain link fence, each connected to existing. Both are OCR and Bluebeam reads only (Inferred; boxes above).
- Ledger row 89 "PROPOSED-Chain link fence 126 LF" (C2.5; C2.1) carries the C2.1 values only in its Notes. Its anchor check: C2.5: matched: quantity 126 LF (Inferred, 024) | C2.1: no match for the row's quantity or specific noun on the sheet.
- Ledger row 19 "PROPOSED-Existing chain link fence 149 LF" is a different fence: C0.5 (KN 16), existing, to be removed. Its anchor check: C0.5 KN 16: matched: quantity 149 LF (Inferred); number by order (Unresolved); 012 819.36,348.84,942.84,360.54.
- This lane does not reconcile them. The fence count and lengths need a person's check against C2.1, C2.5 and C0.5.

## Biggest crosswalk gaps

Printed tags not found on any page:

| Ledger row | Tag | Cited sheets | Hits not counted |
|---|---|---|---|
| 85 | SDCB 1076 | C2.2; C0.1 |  |
| 123 | INF1 | G0.5; C3.1; C3.2 |  |
| 125 | INF3 | G0.5; C3.1; C3.2; C3.3; C3.5 |  |
| 126 | SE1 | G0.5 | C0.3 [ocr; off-citation, short form]; C2.6 [ocr; off-citation, short form] |
| 128 | SE3 | G0.5; C3.3; C3.5 |  |
| 129 | WAS1 | G0.5; C6.2 |  |
| 130 | WAS2 | G0.5; C6.2 |  |
| 131 | WAS3 | G0.5; C3.3; C3.4; C6.2 |  |
| 207 | ESWD WWTP – Aerobic Digester Blower | C6.3; C6.4 |  |
| 208 | ESWD WWTP – Biological Treatment System Blowers (Trains 1 – 3) | C6.4; C6.5 |  |
| 247 | GEN (E) | E0.2 |  |
| 249 | SES (E) | E0.2 | C7.6 [ocr; qualifier (E) not on line] |

Printed tags with the most cited sheets where the tag was not read (top 15):

| Ledger row | Tag | Cited but not found | Found on |
|---|---|---|---|
| 297 | IPS | E4.1; E6.3; E7.0; E7.2; E8.1; E8.2; E8.3; E8.4; E8.5; E8.6; E9.1 | E6.1 [text-layer] |
| 264 | MCP | E2.2; E6.2; E7.0; E7.1; E7.2; E7.3; E7.4; E7.5; E7.6; E7.7 | A1.1 [text-layer]; E2.1 [text-layer]; E6.3 [bluebeam-ocr, ocr] |
| 257 | BL-1 | E7.1; E7.2; E7.3; E7.4; E9.1; E9.2 | E2.1 [text-layer]; E6.1 [bluebeam-ocr, text-layer]; E6.3 [bluebeam-ocr, ocr] |
| 258 | BL-2 | E7.1; E7.2; E7.3; E7.4; E9.1; E9.2 | E2.1 [text-layer]; E6.1 [bluebeam-ocr, ocr, text-layer]; E6.3 [bluebeam-ocr, ocr] |
| 259 | BL-3 | E7.1; E7.2; E7.3; E7.4; E9.1; E9.2 | E2.1 [text-layer]; E6.1 [bluebeam-ocr, ocr, text-layer]; E6.3 [bluebeam-ocr, ocr] |
| 260 | BL-4 | E7.1; E7.2; E7.3; E7.4; E9.1; E9.2 | E2.1 [text-layer]; E6.1 [bluebeam-ocr, ocr, text-layer]; E6.3 [bluebeam-ocr, ocr] |
| 261 | DB | E7.1; E7.2; E7.3; E7.4; E9.1; E9.2 | E2.1 [text-layer]; E6.1 [bluebeam-ocr, ocr, text-layer]; E6.3 [bluebeam-ocr, ocr] |
| 125 | INF3 | G0.5; C3.1; C3.2; C3.3; C3.5 |  |
| 288 | IP-1 | E6.3; E8.1; E8.2; E8.3; E8.4 | E4.1 [text-layer]; E4.2 [text-layer]; E6.1 [bluebeam-ocr, ocr, text-layer] |
| 289 | IP-2 | E6.3; E8.1; E8.2; E8.3; E8.4 | E4.1 [text-layer]; E4.2 [text-layer]; E6.1 [bluebeam-ocr, ocr, text-layer] |
| 290 | IP-3 | E6.3; E8.1; E8.2; E8.3; E8.4 | E4.1 [text-layer]; E4.2 [text-layer]; E6.1 [bluebeam-ocr, ocr, text-layer] |
| 291 | IP-4 | E6.3; E8.1; E8.2; E8.3; E8.4 | E4.1 [text-layer]; E4.2 [text-layer]; E6.1 [bluebeam-ocr, ocr, text-layer] |
| 331 | 2W-P1 | E4.3; E6.3; E7.3; E7.4; E9.1 | E6.1 [bluebeam-ocr, ocr, text-layer] |
| 332 | 2W-P2 | E4.3; E6.3; E7.3; E7.4; E9.1 | E6.1 [bluebeam-ocr, ocr, text-layer] |
| 131 | WAS3 | G0.5; C3.3; C3.4; C6.2 |  |

Printed tags found on sheets the row does not cite: 11 rows.

| Ledger row | Tag | Found but not cited |
|---|---|---|
| 12 | SSMH 1286 | C0.3 |
| 13 | SSMH 1285 | C0.3; C2.1 |
| 58 | Hot Box #1 | C1.1; E4.3; E6.3; E7.4; E10.2 |
| 59 | Hot Box #2 | C1.1; E4.3; E6.3 |
| 77 | SDCB #8 | C0.3 |
| 80 | SDCB #10 | C0.3 |
| 81 | SDCB #2 | C0.3 |
| 82 | SDCB #3 | C0.3 |
| 117 | SDCB #1 | C1.3 |
| 273 | EF-1 | E0.1 |
| 313 | DW-1 | E2.1 |

Tag hits not counted as found (Gate A rules): 234 off-citation, short form, 1 qualifier (E) not on line. Each is listed under its candidate rows in the crosswalk's "Hits Not Counted" column.

## PROPOSED anchors (Gate A rule)

Verified: the anchor was found in the native text layer and its text holds the row's quantity (value and unit), or, for a row whose Ledger Name has no quantity, a specific noun from the Name. Inferred: the same match read by OCR or Bluebeam. Unresolved: the anchor was not found, or its text does not match. A keyed note numbered by order is at best Inferred, and Unresolved where its block's entry count and highest marker read disagree. A sheet-only anchor (a cited sheet with no KN, Det. or Add. anchor) is Verified only when the row's quantity (value and unit) is read on that sheet in the text layer; a noun match anywhere on the sheet is Inferred ("on sheet, location not pinned").

| Anchor type | Verified | Inferred | Unresolved | Total |
|---|---|---|---|---|
| Add. 4 page | 0 | 1 | 1 | 2 |
| detail | 18 | 8 | 5 | 31 |
| keyed note | 0 | 13 | 9 | 22 |
| other | 0 | 0 | 10 | 10 |
| sheet only | 8 | 405 | 77 | 490 |
| all | 26 | 427 | 102 | 555 |

Anchors by match term:

| Anchor type | Match term | Verified | Inferred | Unresolved |
|---|---|---|---|---|
| Add. 4 page | no match | 0 | 0 | 1 |
| Add. 4 page | noun | 0 | 1 | 0 |
| detail | no match | 0 | 0 | 4 |
| detail | noun | 18 | 8 | 1 |
| keyed note | no match | 0 | 0 | 4 |
| keyed note | noun | 0 | 7 | 1 |
| keyed note | quantity | 0 | 6 | 4 |
| other | no match | 0 | 0 | 10 |
| sheet only | no match | 0 | 0 | 77 |
| sheet only | noun | 0 | 396 | 0 |
| sheet only | quantity | 8 | 9 | 0 |

PROPOSED rows by weakest anchor (the row's sheet evidence level): 166 Inferred, 137 Unresolved, 9 Verified; 78 rows cite no sheet number.

## Keyed-note blocks

| Page | Sheet | Heading read | Entries | Markers read | Highest marker | By order | Count check |
|---|---|---|---|---|---|---|---|
| 010 | C0.3 | KEYED NOTES. | 2 | 1 | 2 | 1 | entry count 2 matches the highest marker read |
| 012 | C0.5 | KEYED NOTES: | 25 | 22 | 28 | 6 | entry count 25 does not match the highest marker read (28); by-order numbers Unresolved |
| 013 | C0.6 | KEYED NOTES | 2 | 2 | 2 | 0 | entry count 2 matches the highest marker read |
| 014 | C0.7 | KEYED NOTES | 1 | 1 | 1 | 0 | entry count 1 matches the highest marker read |
| 015 | C1.1 | KEYED NOTES | 38 | 34 | 37 | 5 | entry count 38 does not match the highest marker read (37); by-order numbers Unresolved |
| 017 | C1.3 | KEYED NOTES | 2 | 1 | 2 | 1 | entry count 2 matches the highest marker read |
| 020 | C2.1 | KEYED NOTES. | 9 | 8 | 9 | 1 | entry count 9 matches the highest marker read |
| 024 | C2.5 | KEYED NOTES | 4 | 4 | 4 | 0 | entry count 4 matches the highest marker read |
| 025 | C2.6 | KEYED NOTES | 2 | 2 | 2 | 0 | entry count 2 matches the highest marker read |
| 026 | C3.1 | KEYED NOTES | 9 | 8 | 9 | 1 | entry count 9 matches the highest marker read |
| 027 | C3.2 | KEYED NOTES | 12 | 10 | 13 | 2 | entry count 12 does not match the highest marker read (13); by-order numbers Unresolved |
| 034 | C5.1 | KEYED NOTES | 5 | 4 | 6 | 1 | entry count 5 does not match the highest marker read (6); by-order numbers Unresolved |
| 039 | C6.2 | KEYED NOTES | 9 | 9 | 9 | 0 | entry count 9 matches the highest marker read |
| 040 | C6.3 | KEYED NOTES | 1 | 0 |  | 1 | no marker read; by-order numbers cannot be checked against a marker |
| 041 | C6.4 | KEYED NOTES | 2 | 0 |  | 2 | no marker read; by-order numbers cannot be checked against a marker |
| 042 | C6.5 | KEYED NOTES | 5 | 5 | 5 | 0 | entry count 5 matches the highest marker read |
| 046 | C7.4 | KEYED NOTES | 6 | 0 |  | 6 | no marker read; by-order numbers cannot be checked against a marker |
| 064 | E0.3 | KEY NOTES: | 1 | 1 | 1 | 0 | entry count 1 matches the highest marker read |
| 066 | E1.1 | KEY NOTES: | 6 | 6 | 6 | 0 | entry count 6 matches the highest marker read |
| 067 | E2.1 | KEY NOTES: | 8 | 8 | 8 | 0 | entry count 8 matches the highest marker read |
| 068 | E2.2 | KEY NOTES: | 4 | 4 | 4 | 0 | entry count 4 matches the highest marker read |
| 069 | E3.1 | KEY NOTES: | 9 | 9 | 9 | 0 | entry count 9 matches the highest marker read |
| 070 | E4.1 | KEY NOTES: | 9 | 9 | 9 | 0 | entry count 9 matches the highest marker read |
| 071 | E4.2 | KEY NOTES: | 4 | 4 | 4 | 0 | entry count 4 matches the highest marker read |
| 072 | E4.3 | KEY NOTES: | 5 | 5 | 5 | 0 | entry count 5 matches the highest marker read |
| 073 | E5.1 | KEY NOTES: | 5 | 5 | 5 | 0 | entry count 5 matches the highest marker read |
| 074 | E6.1 | KEY NOTES: | 5 | 5 | 5 | 0 | entry count 5 matches the highest marker read |
| 079 | E7.2 | KEY NOTES: | 1 | 1 | 1 | 0 | entry count 1 matches the highest marker read |
| 080 | E7.3 | KEY NOTES: | 2 | 1 | 1 | 2 | entry count 2 does not match the highest marker read (1); by-order numbers Unresolved |
| 085 | E8.1 | KEY NOTES: | 4 | 4 | 4 | 0 | entry count 4 matches the highest marker read |
| 087 | E8.3 | KEY NOTES: | 1 | 1 | 1 | 0 | entry count 1 matches the highest marker read |
| 092 | E9.2 | KEY NOTES: | 3 | 3 | 3 | 0 | entry count 3 matches the highest marker read |
| 095 | E10.2 | KEY NOTES: | 3 | 3 | 3 | 0 | entry count 3 matches the highest marker read |
| add4_p06 | C6.4 | KEYED NOTES. | 1 | 1 | 1 | 0 | entry count 1 matches the highest marker read |
| add4_p07 | C1.3 | KEYED NOTES | 2 | 1 | 2 | 1 | entry count 2 matches the highest marker read |

## S2.1, set p.57 (Test 4)

- No text layer. Tesseract words (both passes, deduplicated): 568. Bluebeam words: 494.
