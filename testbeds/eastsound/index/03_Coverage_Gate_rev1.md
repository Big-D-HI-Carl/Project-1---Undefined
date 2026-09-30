# 03 Coverage Gate

Coverage check before the crawl lanes start.

- **Version:** rev1, issued 2026-09-29 · **Owner:** Setup thread (single writer) · **Supersedes:** 03_Coverage_Gate.md (rev0, verdict HOLD)
- **Changes:** Verdict PASS; gate decisions A–H logged; checks 5, 6, 8, 11 closed; check 12 added (bid item spine).
- **Project:** Eastsound Sewer and Water District, Wastewater Treatment Plant Upgrade Phase I (Wilson Engineering job 2020-070). Public bid set; test bed only.
- **Source:** Claude Project copy of the library (read-only converted copies, not native PDFs).
- **Tags:** Verified = read in the stored text layer · Verified-Visual = read from the page image · Inferred = derived, basis stated · Unresolved = conflict or missing, need stated.
- **Rules:** addenda supersede base documents (cite both, state which governs) · the body section number governs over the running header and the TOC · duplicates are not indexed: the Division 26 file (use the main spec) and plans_7 pp.1–3 (use plans_6) · claims that defer to WSDOT are tagged "Unresolved: external reference, not staged."
- **Terms:** thread = a chat (Setup, Composer, Merge) · lane = a crawl scope only (Civil & Site, Process & Mechanical, Electrical & Controls, Structural & Building, Contract & General).
- **Short names:** plans_N = `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_N.pdf` · Add. 4 = `addendum-no4-eswd.pdf` · main spec = `eswd-wwtp-upgrade-phase-i-specs.pdf` · p. = PDF page within the named file.

## Verdict: PASS

The crawl lanes are cleared to start on their available scope. Non-blocking open items: 10 sheets assigned — unavailable (resplit pending, SETUP_Resplit_List_rev1.md); 14 spec pages deferred (decision G); Addenda 1–3 not in the library. Resplit uploads and the 14 spec pages come back to the Setup thread, which stays open as the inventory owner.

## Gate close-out decisions

| Decision | Owner decision | Applied in |
|---|---|---|
| A | Fifth crawl lane "Contract & General" approved: Divisions 00 and 01, Appendices D, E, I, and the QA plan | 00, 02, 03 |
| B | Ledger_Schema.csv is in Project files. Columns: Tag, Name, Bid Item, Lane, Area/Building, Discipline, Drawing Sheets, Spec Sections, Addenda, Submittal Req, Testing/Startup Req, Wiki Note(s), Status, Tag level, Source Citation, Notes | 03 (check 11; lane prompt rules) |
| C | Read Method threshold 300 body characters; the 20 affected sheets re-flagged Visual | 01, 03, resplit list |
| D | The six spec lane judgment calls in 02 are accepted | 02 |
| E | The 01 11 10 / 01 11 00 alias is accepted; it stays Unresolved | 02 |
| F | Claims that defer to WSDOT are tagged "Unresolved: external reference, not staged." | All file headers; 00, 02, 03, 04 |
| G | The 14 spec pages with no text or image are deferred; not blocking | 02, 03 |
| H | Terms: thread = a chat (Setup, Composer, Merge); lane = a crawl scope only | All file headers |

Setup decisions 1–9 stay in force: missing sheets carried as assigned but unavailable (1); plans_6 copies only (2); Division 26 file not indexed, page offset kept (3); body section number governs, conflicts logged (4); Read Method and the Verified-Visual tag (5, threshold per C); lane scopes (6, G sheets split by title); WSDOT excluded (7); Bid Item #18 and geotech date flagged for Merge (8); S-sheet "OF 98" low priority (9).

## Gate checks

| # | Check | Result | Evidence | Action |
|---|---|---|---|---|
| 1 | Every library file has a register row | PASS | 30/30 files in 00 | — |
| 2 | Every page is accounted for (indexed, duplicate, or logged unreadable) | PASS | 884/884: drawings 89 (86 indexed + 3 duplicates), main spec 645, Division 26 file 114 (duplicate), Add. 4 13, QA plan 23 | — |
| 3 | Every cover-index sheet has a row and a status | PASS, open items | 96/96 rows: 86 available, 10 assigned — unavailable | Re-split and upload (SETUP_Resplit_List_rev1.md) |
| 4 | Every TOC section and appendix located; body number governs | PASS | 96/96 TOC sections + 00 00 00 + 00 01 00; 9/9 appendices; all page counts reconcile | — |
| 5 | Every crawlable unit has exactly one lane | PASS | 96 sheets + C1.6A; 95 crawlable sections (3 index-only); 8 crawlable appendices (A index-only); QA plan → Contract & General (decision A) | — |
| 6 | Every sheet has a Read Method | PASS, open items | Visual 40 · Text 46 (decision C); C1.6A and 7 Add. 4 pages set; 10 unavailable set on upload | Set on upload |
| 7 | Duplicates excluded | PASS | plans_7 pp.1–3 (decision 2); Division 26 file (decision 3) | — |
| 8 | Unreadable pages logged with a remedy | PASS, deferred | 11 image-only drawing pages → visual pass; 14 spec pages deferred (decision G) | — |
| 9 | Conflicts logged; Merge flags set | PASS | 8 sheet title mismatches, S page total, 11 spec conflict entries, 2 bid-item conflicts; 2 owner flags + 1 candidate for the Merge exception report | — |
| 10 | External references handled | PASS | WSDOT not staged (decision 7); tag rule set (decision F) | — |
| 11 | Ledger schema available for lane output | PASS | Ledger_Schema.csv in Project files (decision B). Not readable from the Setup thread, whose Project snapshot predates the upload; the Composer thread confirms the columns on first read. | — |
| 12 | Bid item spine available for the Ledger "Bid Item" column | PASS | 04_Bid_Item_Spine.md: 19 bid items + 5 equipment alternates, each with scope reference and lane; #18 conflict flagged | — |

## Lane scopes

| Lane | Drawings | Spec sections | Appendices | Other |
|---|---|---|---|---|
| Civil & Site | G0.1–G0.4 (adj.), C0.x–C2.x, C7.x, C1.6A | Divisions 02, 31, 32, 33; 15 08 13 | B, C, F, G, H | — |
| Process & Mechanical | G0.5–G0.7 (adj.), C3.x–C6.x | Divisions 22, 23, 40, 41, 43, 45, 46; 10 73 05; 15 40 00 | — | — |
| Electrical & Controls | All E sheets (E0.1–E10.3) | Division 26 (main spec only) | — | Add. 4 generator exhibit pp.11–13 |
| Structural & Building | S and A sheets | Divisions 03, 05–09; 10 52 00; 13 12 20 | — | — |
| Contract & General | — | Divisions 00, 01 | D, E, I | QA plan |
| Index only (not crawled) | — | Cover, 00 00 00, 00 01 00, 26 00 00, 4 part dividers | A (pointer to 00 31 13) | Division 26 file, plans_7 pp.1–3 (duplicates) |

## Coverage by lane

| Lane | Sheets available | Sheets unavailable | Visual sheets | Spec sections + appendices | Spec pages | Other documents | Add. 4 items (primary) |
|---|---|---|---|---|---|---|---|
| Civil & Site | 23 | 10 | 13 | 23 | 155 | — | 4 |
| Process & Mechanical | 20 | 0 | 18 | 17 | 99 | — | 3 |
| Electrical & Controls | 35 | 0 | 2 | 14 | 113 | — | 3 |
| Structural & Building | 9 | 0 | 8 | 16 | 77 | — | 5 |
| Contract & General | 0 | 0 | 0 | 33 | 188 | QA plan (23 pp.) | 0 |

C1.6A counts as available and Visual under Civil & Site.

## Addendum 4 item map

| Item | Add. 4 p. | Touches | Primary lane | Also affects |
|---|---|---|---|---|
| Clarification 1 — surfacing demolition information | p.1 | C0.5, C2.6 (C2.6 unavailable) | Civil & Site | — |
| Clarification 2 — exterior sealant, precast wet well and vault joints | p.1 | No sheet or section cited; related 03 40 00 (Inferred) | Structural & Building | Process & Mechanical (wet well); Civil & Site (vaults) |
| Clarification 3 — Q&A, metal building factory finish | p.1 | 13 12 20 ¶2.03, ¶2.04 (no change) | Structural & Building | — |
| Clarification 4 — Q&A, MCC size and blower building footprint | p.1 | E9.1; A1.1 (reissued p.4) | Electrical & Controls | Structural & Building (A1.1) |
| Clarification 5 — temporary back-up generator, Bid Item #18 | p.1; exhibit pp.11–13 | 00 41 00 (conflict) | Electrical & Controls | Contract & General; flag: Merge exception report |
| Specifications — 09 90 00 ¶2.01 I | p.2 | 09 90 00 | Structural & Building | — |
| Specifications — 22 13 36 ¶2.01 A | p.2 | 22 13 36 | Process & Mechanical | Electrical & Controls (MCC VFDs) |
| Specifications — 26 80 00 ¶2.04 D | p.2 | 26 80 00 | Electrical & Controls | — |
| Specifications — 33 41 00 ¶2.02 | p.2 | 33 41 00 | Civil & Site | — |
| Specifications — 43 22 10 ¶2.01 A | p.2 | 43 22 10 | Process & Mechanical | Electrical & Controls (MCC VFDs) |
| Drawings — A1.1, A1.2, edits in red | p.3; sheets pp.4–5 | A1.1, A1.2 | Structural & Building | Electrical & Controls (MCC, control panel locations) |
| Drawings — C6.4, edits in red | p.3; sheet p.6 | C6.4 | Process & Mechanical | — |
| Drawings — C1.3, edits in red | p.3; sheet p.7 | C1.3 | Civil & Site | — |
| Drawings — C1.6A, edits in red | p.3; sheet p.8 | C1.6A (not in cover index) | Civil & Site | Process & Mechanical (process piping) |
| Drawings — S2.3, S4.1, clouded edits | p.3; sheets pp.9–10 | S2.3, S4.1 | Structural & Building | — |

Likely bid item for each Add. 4 item: 04_Bid_Item_Spine.md.

## Merge exception report: carry-forward flags

| Flag | Source A | Source B | Governs | Needed |
|---|---|---|---|---|
| Bid Item #18 (owner flag) | Add. 4 p.1 Clarification 5: "Temporary Back Up Generator (Bid Item #18)" | 00 41 00 p.25: item 18 = Train 3 stainless steel fabrication (Bid Alternate 1); base carries a temporary generator in 00 31 13 p.21 and 26 05 00 pp.276, 279 | Unresolved — Add. 4 doesn't reissue the bid form | Addenda 1–3 or the conformed bid form; full record in 04_Bid_Item_Spine.md |
| Geotech report date (owner flag) | 31 20 00 ¶1.01 B p.383: GeoEngineers report Sept 7, 2021 | Appendix C: GeoEngineers Nov 8, 2022 (p.537) + Dec 16, 2022 addendum (p.577) | Unresolved — both are base documents | Engineer confirmation or the 2021 report |
| Permanent generator bid item (candidate) | 00 41 00 p.26: Base Bid Item #1 based on listed generator makes | 00 24 13 ¶6 p.17: all Division 26 work in Item 6 (26 32 13 generators) | Unresolved | Owner to confirm the flag |
| E5.1 title (carry, lower priority) | Cover index: UV DISINFECTION & CLARIFIER … | Title block: UV DISINFECTION CHAMBER & DIGESTER … | Title block used for indexing | Engineer confirmation |
| 01 11 10 section number (carry, lower priority) | Body: 01 11 10 | TOC and header: 01 11 00 | Body, per decision 4; alias accepted (decision E) | Confirm |

## Requirements for every lane prompt (written by the Composer thread)

1. Retrieve through your lane's rows in 01_Sheet_Index_rev1.md, 02_Spec_Index_rev1.md, 03_Coverage_Gate_rev1.md, and 04_Bid_Item_Spine.md. Don't bulk-read library files; if an answer needs the whole set, log it as a design gap.
2. Read Method = Visual (image-only, 300 or fewer body chars, or schedule tables) → run a visual pass on the page image and tag every claim from it Verified-Visual. Claims from the text layer are Verified.
3. Addenda supersede: where a row has an Addendum 4 entry, read the addendum item, cite both, and state that Add. 4 governs.
4. Section identity = the body SECTION number, with the accepted alias 01 11 10 = 01 11 00. Never key on running headers.
5. Skip the duplicates: Division 26 file, plans_7 pp.1–3.
6. Assigned — unavailable sheets: record the gap; don't infer their content.
7. Cross-lane content: log it for Merge; don't take ownership.
8. Cite every claim: file + PDF page + sheet, spec section ¶ + PDF page, or addendum number + item + page.
9. Claims that defer to WSDOT: tag "Unresolved: external reference, not staged."
10. Ledger rows use the Ledger_Schema.csv columns exactly (decision B): Tag, Name, Bid Item, Lane, Area/Building, Discipline, Drawing Sheets, Spec Sections, Addenda, Submittal Req, Testing/Startup Req, Wiki Note(s), Status, Tag level, Source Citation, Notes. "Bid Item" values come from 04_Bid_Item_Spine.md; rows touching either #18 scope carry "18 — Unresolved (see 04)".
11. Terms: thread = a chat (Setup, Composer, Merge); lane = a crawl scope.

## Workflow log

- **Setup thread, run 1 (inventory crawl):** outputs not written; the tool budget ran out during verification. Fix: write outputs as you go, and batch visual checks. Applied from run 2.
- **Setup thread, run 2:** rev0 set issued; gate HOLD (front-end lane, Ledger schema). Test cases logged: the body-governs rule produced 01 11 10 (alias kept), and the ≤20-character threshold left 20 label-only sheets as Text.
- **Setup thread, run 3 (gate close-out):** decisions A–H applied; rev1 set issued (00, 01, 02, 03, resplit list) and 04 added; test case 2 fixed by decision C; verdict PASS. Stopped here.
