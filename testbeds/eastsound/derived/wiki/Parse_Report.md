# Parse report — Project Wiki notes and links

Built by `testbeds/eastsound/tools/parse_wiki.py` from the Merge rev1 Project Wiki. Deterministic: no timestamps, sorted rows, UTF-8 without a BOM, LF line endings. Rebuild from the repo root:

```
python testbeds/eastsound/tools/parse_wiki.py
```

## Inputs

| File | Lines or rows | SHA-256 |
|---|---|---|
| `testbeds/eastsound/project/01_Project_Wiki/Project_Wiki.md` | 2522 lines | `a3027eed7aadeee5aa7a40b6dc44de9e0a9756d8844d74fca6aa8e94a75210a2` |
| `testbeds/eastsound/derived/reconciliation/Ledger_ID_Map.csv` | 447 rows | `1e6f2d57dab919b981bd89b55ed7706d8305aa449ad911dae54f36661607c697` |
| `testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv` | 447 rows (Wiki Note(s) only) | `0ed3af5640881f6fe2551b982d44653ddd92629cbcb5d47d68280a3ae6683e31` |

## Tie-outs

| Check | Result | Detail |
|---|---|---|
| Note headings = Index rows | pass | 202 headings, 202 Index rows, 202 expected |
| Note IDs in Index order | pass | heading ID = Index Unit, row by row |
| Notes per lane = Index lane counts | pass | Civil & Site 56/56, Process & Mechanical 37/37, Electrical & Controls 50/50, Structural & Building 25/25, Contract & General 34/34 |
| Merge-line lane = Index lane, note by note | pass | 202 compared |
| Notes with all 7 fields and a location line | pass | 202 of 202 |
| Ledger_ID_Map tags = Project_Ledger tags, row by row | pass | 447 rows |

## Notes parsed per lane

| Lane | Index count | Parsed | Format |
|---|---|---|---|
| Civil & Site | 56 | 56 | pipe line (56) |
| Process & Mechanical | 37 | 37 | labeled lines (37) |
| Electrical & Controls | 50 | 50 | seven-column table (50) |
| Structural & Building | 25 | 25 | bold bullets (25) |
| Contract & General | 34 | 34 | field-value table (34) |
| **Total** | 202 | 202 | |

- The Civil & Site count includes 4 resplit-pass notes (C0.3, C2.1, C2.3, C2.6); their Merge line reads "Civil & Site (resplit pass)" and the Lane column reads "Civil & Site".
- 184 summaries run past 600 characters and are cut at 600 in Wiki_Notes.csv. The full text stays in the Wiki.
- The Document ID field differs from the heading ID in these notes. Note ID uses the heading, which matches the Index:
  - 01 11 10: Document ID reads "01 11 10 (body governs; header and TOC read 01 11 00 — alias accepted, stays Unresolved per 02 conflict 1 / 03 decision E; cited, not re-raised)"
  - QA plan: Document ID reads "CQA Plan (file `cqa-plan-eswd-wwtp-ph1-2022-12-01.pdf`; 00 register row 4)"

## Links per type

| Target type | Tag line | Related documents | Body text | Total |
|---|---|---|---|---|
| equipment tag | 1309 | 45 | 239 | 1593 |
| sheet | 433 | 705 | 210 | 1348 |
| spec section | 349 | 415 | 123 | 887 |
| addendum item | 73 | 38 | 116 | 227 |
| note | 13 | 30 | 4 | 47 |
| **Total** | 2177 | 1233 | 692 | 4102 |

| Source | Verified | Verified-Visual | Inferred | Unresolved |
|---|---|---|---|---|
| tag line | 2129 | 0 | 48 | 0 |
| related documents | 1160 | 0 | 73 | 0 |
| body text | 0 | 0 | 692 | 0 |

- 166 references from a note to itself were dropped (mostly the body-text citation of the note's own sheet or section).
- One row per note, target type, target and source. Where the same target is written twice in one source, the row keeps the stronger tag.

## Equipment tags and the Ledger

- Equipment tag links: 1593 (tag line 1309, related documents 45, body text 239).
- With a Ledger ID: 735 links, 217 distinct Ledger IDs (134 of 135 printed-tag rows; 83 PROPOSED rows).
- 114 matched links point to a Ledger row whose Wiki Note(s) does not name this note. They are listed in Wiki_Links.csv (Basis column) for Merge to check; no Ledger change is made here.
- Printed-tag Ledger rows not found in any note: 1.
  L-0190 S1–S2 [Aerobic Digester]
- Printed forms left without a Ledger ID because the only Ledger rows carry a qualifier that the text does not support: 12.
  - C4.2 (body text): F1 — Ledger tag(s) F1 (Influent Pump Station); no row names this note and no qualifier in the text
  - C4.2 (body text): F4 — Ledger tag(s) F4 (Influent Pump Station); no row names this note and no qualifier in the text
  - E4.3 (body text): F1 — Ledger tag(s) F1 (Influent Pump Station); no row names this note and no qualifier in the text
  - E4.3 (body text): F4 — Ledger tag(s) F4 (Influent Pump Station); no row names this note and no qualifier in the text
  - E7.3 (tag line): F1 — Ledger tag(s) F1 (Influent Pump Station); no row names this note and no qualifier in the text
  - E7.3 (tag line): F4 — Ledger tag(s) F4 (Influent Pump Station); no row names this note and no qualifier in the text
  - 26 51 19 (tag line): L1 — Ledger tag(s) L1 (Blower Building); no row names this note and no qualifier in the text
  - 26 51 19 (tag line): L2 — Ledger tag(s) L2 (Blower Building), L2 (Treatment Building); no row names this note and no qualifier in the text
  - 26 51 19 (tag line): X1 — Ledger tag(s) X1 (Blower Building); no row names this note and no qualifier in the text
  - 26 51 19 (related documents): L1 — Ledger tag(s) L1 (Blower Building); no row names this note and no qualifier in the text
  - 26 51 19 (related documents): L2 — Ledger tag(s) L2 (Blower Building), L2 (Treatment Building); no row names this note and no qualifier in the text
  - 26 51 19 (related documents): X1 — Ledger tag(s) X1 (Blower Building); no row names this note and no qualifier in the text
- Ambiguous Ledger matches (more than one row fits; all IDs listed in the cell): 7.
  - G0.5 (tag line): influent sample sump → L-0101; L-0148
  - C4.1 (tag line): influent sample sump → L-0101; L-0148
  - C7.5 (tag line): influent sample sump → L-0101; L-0148
  - E4.1 (tag line): influent sampler → L-0320; L-0418
  - E6.2 (tag line): influent sampler → L-0320; L-0418
  - 00 31 13 (tag line): influent sampler → L-0320; L-0418
  - 00 31 13 (tag line): dewatering system → L-0110; L-0427

## Targets not in the Wiki

Sheet, spec section and note targets with Target In Wiki = N (distinct target, link count, notes):

| Target type | Target | Links | Notes |
|---|---|---|---|
| note | Appendix A | 2 | 00 31 13 |
| sheet | C8.1 | 2 | 08 70 00 |
| sheet | M4.1 | 2 | C4.1 |
| spec section | 00 22 13 | 4 | 00 43 93, 01 33 00 |
| spec section | 00 25 13 | 2 | 01 31 00 |
| spec section | 00 33 00 | 1 | 31 23 33 |
| spec section | 00 43 36 | 2 | 01 33 00 |
| spec section | 00 45 14 | 2 | 01 33 00 |
| spec section | 00 72 00 | 2 | 01 70 00 |
| spec section | 01 11 00 | 5 | G0.3, 01 31 00, 01 50 00, 02 41 00 |
| spec section | 01 30 00 | 10 | 01 60 00, 01 66 00, 31 23 19, 33 05 00, 33 30 00, 41 12 13 |
| spec section | 01300 | 1 | 31 23 33 |
| spec section | 01340 | 2 | 41 12 13, 46 33 33 |
| spec section | 01400 | 1 | 32 12 16 |
| spec section | 03300 | 1 | 02 83 00 |
| spec section | 04 60 00 | 2 | 05 50 00 |
| spec section | 05500 | 1 | 02 83 00 |
| spec section | 09 91 00 | 2 | 43 22 10 |
| spec section | 09900 | 1 | 33 31 00 |
| spec section | 15051 | 1 | C7.5 |
| spec section | 22 10 00 | 2 | 33 31 00 |
| spec section | 22 13 16 | 2 | 46 76 26 |
| spec section | 26 30 00 | 1 | 26 36 00 |
| spec section | 46 12 13 | 3 | C6.1, 41 12 13 |

## Notes that did not parse

None. All 202 notes matched their lane format and have all seven fields and a location line.

## Lines and items that did not parse

Pieces of a tag line or Related documents line that gave no link. Body text is prose and is not listed. Explicit "none" entries are parsed, not listed: tag line 267, Related documents 0.

| Category | Count |
|---|---|
| no target found | 43 |
| Issue or Exceptions reference (not a link type) | 37 |
| external reference (not a link type) | 3 |
| index file reference (not a link type) | 23 |

### no target found

| Note | Wiki line | Source | Text |
|---|---|---|---|
| G0.1 | 311 | tag line (sheets) | Index of all 96 sheets |
| G0.2 | 319 | tag line (sheets) | All civil and architectural sheets |
| G0.2 | 319 | related documents | all C and A sheets |
| C0.5 | 405 | tag line (sheets) | C1 site piping sheets |
| C0.5 | 405 | tag line (sheets) | C2 storm drainage sheets |
| C0.5 | 405 | tag line (sheets) | electrical sheets (all cited) |
| C3.2 | 529 | tag line (sheets) | "see structural drawings" |
| C5.2 | 609 | tag line (sheets) | detail 1 on this sheet |
| C7.6 | 727 | related documents | E sheets (power, heat trace) |
| E0.1 | 895 | related documents | All E sheets |
| E4.2 | 985 | related documents | influent pump station civil/mechanical sheets (other lanes) |
| E5.1 | 1005 | related documents | UV and digester process sheets (Process & Mechanical stack) |
| E6.3 | 1035 | related documents | all E plan sheets (conduit tags) |
| E7.0 | 1045 | related documents | Bid Item 17 SCADA/PLC programmer services (04) |
| E7.1 | 1055 | related documents | civil pad specification (Civil & Site stack) |
| E7.2 | 1065 | related documents | blower specification (Process & Mechanical stack) |
| E8.1 | 1125 | related documents | civil pad specification (Civil & Site stack) |
| E8.1 | 1125 | related documents | influent pump specification (Process & Mechanical stack) |
| E8.2 | 1135 | related documents | influent pump specification (Process & Mechanical stack) |
| E10.1 | 1215 | related documents | civil drainage rock and backfill (Civil & Site stack) |
| E10.2 | 1225 | related documents | civil piping sheets (sizes, Civil & Site stack) |
| E10.3 | 1235 | related documents | civil pad (Civil & Site stack) |
| 00 24 13 | 1292 | tag line (sheets) | all E sheets |
| 00 31 13 | 1308 | tag line (addenda) | bid item no. per existing flag |
| 00 41 00 | 1324 | tag line (addenda) | Bid Item #18 Unresolved (existing flag) |
| 00 73 00 | 1564 | tag line (addenda) | SC 2 ranks Addenda third (p.88) |
| 01 41 00 | 1628 | tag line (spec) | General Conditions |
| 01 41 00 | 1628 | tag line (sheets) | all (dimension and diagrammatic rules) |
| 01 45 00 | 1644 | tag line (spec) | Division 46 (other lane) |
| 01 70 00 | 1708 | tag line (sheets) | record drawings (all) |
| 01 70 00 | 1708 | tag line (addenda) | posted to the record set (¶1.07.B) |
| 01 91 00 | 1725 | related documents | Division 46 (other lane) |
| 02 41 00 | 1733 | tag line (sheets) | electrical drawings (cited) |
| 05 52 00 | 1819 | related documents | civil sheets (Process & Mechanical lane) |
| 15 40 00 | 2002 | related documents | Civil & Site site sheets for locations |
| 22 13 29 | 2011 | tag line (spec) | Division 26 (related, ¶1.02) |
| 26 05 00 | 2041 | related documents | General Conditions (Contract & General stack) |
| 31 20 00 | 2187 | tag line (sheets) | Grading and erosion control plans (cited) |
| 43 22 10 | 2323 | tag line (sheets) | "as indicated on the Plans" |
| 45 05 00 | 2333 | tag line (sheets) | "shown on the drawings" |
| 46 53 00 | 2373 | tag line (sheets) | "as shown on the drawings" (no sheet numbers cited) |
| 46 66 00 | 2383 | tag line (spec) | Division 26 (related) |
| Appendix C | 2419 | tag line (sheets) | Figure 2 site and exploration plan (p.559, not read) |

### Issue or Exceptions reference (not a link type)

| Note | Wiki line | Source | Text |
|---|---|---|---|
| G0.5 | 346 | related documents | Issue 18 |
| G0.6 | 356 | related documents | Issue 7 |
| G0.7 | 366 | related documents | Anoxic table reads "TRAIN #4 (PROPOSED)" — Issue 1 |
| G0.7 | 366 | related documents | Issues 2, 3, 4, 6 |
| G0.7 | 366 | related documents | Issue 32 |
| C3.1 | 520 | related documents | Issue 7 |
| C3.2 | 530 | related documents | Issue 7 |
| C3.2 | 530 | related documents | Issue 40 |
| C3.3 | 540 | related documents | Issues 2, 3 |
| C3.4 | 550 | related documents | Issues 4, 5, 10 |
| C3.5 | 560 | related documents | Issues 4, 5, 10 |
| C4.1 | 570 | related documents | Issue 11 |
| C4.2 | 580 | related documents | Issue 12 |
| C4.2 | 580 | related documents | Issue 39 |
| C5.2 | 610 | related documents | Issue 15 |
| C5.3 | 620 | related documents | Issue 15 |
| C5.4 | 630 | related documents | Issue 13 |
| C6.1 | 640 | related documents | Issues 14, 16 |
| C6.2 | 650 | related documents | Issues 17, 18 |
| C6.3 | 660 | related documents | Issue 19 |
| C6.4 | 670 | related documents | Issue 19 |
| 01 11 10 | 1580 | tag line (spec) | General Conditions (identity — Issues 2.6) |
| 01 31 00 | 1596 | tag line (spec) | General Conditions (Issues 2.6) |
| 10 73 05 | 1970 | related documents | Issue 20 |
| 22 13 36 | 2022 | related documents | Issue 21 |
| 23 34 00 | 2032 | related documents | Issue 25 |
| 41 12 13 | 2304 | related documents | Issues 14, 22, 23 |
| 43 11 00 | 2314 | related documents | Issues 6, 24 |
| 43 22 10 | 2324 | related documents | Issues 12, 26, 27 |
| 45 05 00 | 2334 | related documents | Issues 28, 31 |
| 46 33 33 | 2344 | related documents | Issues 16, 29 |
| 46 41 23 | 2354 | related documents | Issue 30 |
| 46 53 00 | 2374 | related documents | Issues 2, 3, 4, 5, 6, 8, 9 |
| 46 53 00 | 2374 | related documents | Issue 41 |
| 46 66 00 | 2384 | related documents | Issues 13, 32, 33 |
| 46 66 10 | 2394 | related documents | Issue 34 |
| 46 76 26 | 2404 | related documents | Issues 18, 22, 35, 36, 37, 38 |

### external reference (not a link type)

| Note | Wiki line | Source | Text |
|---|---|---|---|
| C3.4 | 549 | tag line (spec) | WSDOT 9-03.12(1)A cited |
| C3.5 | 559 | tag line (spec) | WSDOT 9-03.12(1)A cited |
| C5.2 | 609 | tag line (spec) | WSDOT 9-03.12(1)A cited |

### index file reference (not a link type)

| Note | Wiki line | Source | Text |
|---|---|---|---|
| G0.1 | 311 | related documents | 01_Sheet_Index_rev1.md (built from this index) |
| C0.2 | 381 | related documents | 04 Bid Items 4–5 |
| C5.4 | 630 | related documents | 04 Equipment Alternate D (Trojan base) |
| C6.1 | 640 | related documents | 04 Equipment Alternate C |
| C7.3 | 703 | related documents | 04 Items 8, 11–13 |
| S2.1 | 829 | related documents | 04 Bid Items 18–19 |
| 00 24 13 | 1293 | related documents | 04_Bid_Item_Spine.md |
| 00 41 00 | 1325 | related documents | 04_Bid_Item_Spine.md |
| 06 20 00 | 1847 | related documents | 02 conflict log #2 |
| 07 92 00 | 1875 | related documents | 02 conflict log #3 |
| 22 13 29 | 2012 | related documents | 04 Equipment Alternate A (Flygt base; spec link now matches by manufacturer) |
| 26 05 00 | 2041 | related documents | 04 Bid Item #18 conflict |
| 26 32 13 | 2141 | related documents | 04 Other bid-item conflicts #1 (permanent generator bid item) |
| 26 36 00 | 2151 | related documents | 04 Bid Item #18 conflict |
| 26 80 00 | 2171 | related documents | 04 Bid Item 17 (SCADA/PLC programmer) |
| 31 20 00 | 2187 | related documents | 04 Items 10–16 |
| 31 23 33 | 2203 | related documents | 04 Item 2 (Trench Safety) and Items 14, 16 |
| 31 32 11 | 2211 | related documents | 04 Items 4–5 (SWPPP) |
| 31 40 00 | 2219 | related documents | 04 Item 2 (Trench Safety Excavation Provisions) |
| 32 12 16 | 2227 | related documents | 04 Item 8 (HMA Pavement, extra work) |
| 46 66 00 | 2384 | related documents | 04 Equipment Alternate D (Trojan base, confirmed here) |
| 46 76 26 | 2404 | related documents | 04 Equipment Alternate C (Fournier, Prime Solutions base) |
| Add. 4 Generator Exhibit | 2503 | related documents | 04 Bid Item #18 conflict |

## Rules applied

- Notes: every level-3 heading under the three note sections (Drawing sheets, Spec sections and appendices, Other units). Note ID and Title come from the heading, split at the first " — ". Lane comes from the Merge line under the heading.
- Formats, as the lane preambles describe them: Civil & Site one pipe-separated line plus "Location:"; Process & Mechanical labeled lines plus "Where it lives:"; Electrical & Controls a seven-column table plus "Where it lives:"; Structural & Building bold bullets plus "Lives in:"; Contract & General a Field/Value table plus "Location:". The parser tries each format on every note and records the one that fits.
- Where It Lives is the text after the location label. Summary is cut at 600 characters.
- Tag line: split into its labeled parts (Equipment, Structures, Items or Scope; Spec; Sheets; Addenda), then into items at ";" and ", " outside brackets. Electrical & Controls writes one unlabeled list, so an item with a sheet, spec or addendum reference gives those links and any other item is an equipment tag. An unlabeled part in another lane is read the same way.
- Every item in a labeled equipment part is an equipment tag link. A sub-label such as "Existing:" is dropped from Target and kept in Written As.
- Related documents: split into pieces at ";" and at sentence ends outside brackets. Each piece gives its sheet, spec, addendum and note references.
- Body text is the Revision/Date and Summary fields. Its references and printed Ledger tags are links tagged Inferred.
- Confidence: tag-line and Related-documents links are Verified as written, except that the weakest tag word the lane wrote on that piece governs (for example "[by title, Inferred]" or "Spec (by subject, Inferred)"), per the weakest-tag rule in AGENTS.md. A reference inside a "none …" entry is Inferred.
- Sheets: G, C, S, A and E numbers such as C1.6A, plus M (M4.1 is cited on C4.1 and is not in the set). A range such as C3.1–C3.5 is expanded in Wiki index order and keeps its source's tag. A series such as C2.x is expanded to the index sheets in that series and tagged Inferred, since the note names no members. Basis names each expansion.
- Spec sections: six digits in three pairs. Paragraph marks stay in Written As; Target is the section number. In a tag-line Spec part, a five-digit number written in the older format (01340, 15051) is also a spec section target; none of these is a Wiki note.
- Addendum items: "Add. N" or "Addendum No. N" with its pages and clarifications. One target per page ("Add. 4 p.3"); a clarification joins the page before it ("Add. 4 p.1 Clarification 5"). A bare page in an Addenda list takes the addendum number written before it in the same list.
- Note links: Appendix A–I, the QA plan ("QA plan" or "CQA Plan") and the Add. 4 generator exhibit. Links from a note to itself are dropped.
- Target In Wiki: Y when a sheet, spec section or note target is a Wiki note ID; blank for equipment and addendum items.
- Ledger ID: printed Ledger tags (Ledger_ID_Map.csv) are found by exact, case-sensitive text with word edges. "A | B" tags match either form. "(E)" is kept as part of the tag, except that SES (E), which has no new twin, also matches a bare "SES". A hyphen variant (LP1 for LP-1) matches and says so in Basis, unless a number follows it ("SD1 0.51g" is a seismic value, not SD-1). A range or list (SDCB #1–#10, INF1–INF3, Hot Box #1, #2, Pipe IDs 1–26) is expanded only when every member is a Ledger tag.
- A bracketed qualifier, such as "(Influent Pump Station)" on F1, is not printed on the drawings. A form that exists only with qualifiers gets a Ledger ID only when the Ledger row names this note in Wiki Note(s) or the qualifier appears in the item, sentence or note title; otherwise Ledger ID is blank and Basis says why.
- Where one printed form fits several Ledger rows, the rows whose Wiki Note(s) name this note are kept, then the rows whose qualifier appears in the same item, sentence or note title. If more than one row is left, all IDs go in the cell, separated by "; ".
- PROPOSED Ledger tags are matched only to a whole tag-line equipment item with the same name (case, hyphens and a leading existing/new/proposed ignored). They are not searched in body text.
- Not link types, listed in the unparsed table by category: Issue and Exceptions references, index files (00–04), and external references (WSDOT, WAC and similar).
