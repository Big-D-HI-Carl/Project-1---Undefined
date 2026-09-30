# 02 Spec Index

Section-level index of the main spec (Parts 1–4). The Division 26 file is cross-referenced, not indexed.

- **Version:** rev1, issued 2026-09-29 · **Owner:** Setup thread (single writer) · **Supersedes:** 02_Spec_Index.md (rev0)
- **Changes:** Contract & General lane approved (decision A); six lane judgment calls accepted (decision D); 01 11 10 alias accepted, stays Unresolved (decision E); WSDOT tag rule (decision F); 14 imageless pages deferred (decision G); terms (decision H); bid items → 04_Bid_Item_Spine.md.
- **Project:** Eastsound Sewer and Water District, Wastewater Treatment Plant Upgrade Phase I (Wilson Engineering job 2020-070). Public bid set; test bed only.
- **Source:** Claude Project copy of the library (read-only converted copies, not native PDFs).
- **Tags:** Verified = read in the stored text layer · Verified-Visual = read from the page image · Inferred = derived, basis stated · Unresolved = conflict or missing, need stated.
- **Rules:** addenda supersede base documents (cite both, state which governs) · the body section number governs over the running header and the TOC · duplicates are not indexed: the Division 26 file (use the main spec) and plans_7 pp.1–3 (use plans_6) · claims that defer to WSDOT are tagged "Unresolved: external reference, not staged."
- **Terms:** thread = a chat (Setup, Composer, Merge) · lane = a crawl scope only (Civil & Site, Process & Mechanical, Electrical & Controls, Structural & Building, Contract & General).
- **Short names:** plans_N = `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_N.pdf` · Add. 4 = `addendum-no4-eswd.pdf` · main spec = `eswd-wwtp-upgrade-phase-i-specs.pdf` · p. = PDF page within the named file.

## Method

- A section starts on the page carrying its body "SECTION nn nn nn" line (decision 4: the body number governs). It ends on the page before the next start.
- Page counts reconcile with the running header "PAGE X OF Y" for 97 of 98 numbered sections. 43 11 00 uses its own numbering (431100-1 to -10) and also reconciles (Verified).
- The Division 26 file matches main spec pp.268–381 page for page (114/114, whitespace-normalized text; Verified). Division 26 file page = main spec page − 267.
- **WSDOT (decision F):** sections citing WSDOT (Verified): 00 24 13, 00 41 00, 00 73 00, 01 41 00, 01 45 00, 01 70 00, 02 92 00, 03 30 00, 03 40 00, 31 20 00, 31 23 33, 31 32 11, 32 12 16, 32 32 23, 33 05 00, 33 30 00, 33 31 00, 33 32 00, 33 41 00, Appendix C. Claims that defer to it are tagged "Unresolved: external reference, not staged."
- **Crawler hazard:** the running header project name has three forms ("ESWD WWTP UPGRADE - PHASE I", "EASTSOUND WWTP UPGRADE", "EASTSOUND WWTP UPGRADE – PHASE 1"). Key on the section number, never the header string.

## Summary

| Item | Count |
|---|---|
| Numbered sections | 98 (96 in the TOC + 00 00 00 Engineer’s Statement + 00 01 00 TOC) |
| Appendices | 9 (A–I) |
| Part dividers + cover | 4 + 1 |
| Division 26 entries in both files | 15 (26 00 00 + 14 sections) |
| Pages with no text and no stored image | 14, deferred (decision G): p.539, 576, 578, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 639 |
| Sections and appendices by lane | Civil & Site 23 · Process & Mechanical 17 · Electrical & Controls 14 · Structural & Building 16 · Contract & General 33 · Index only 4 |

## Spec lane mapping (MasterFormat division; judgment calls accepted, decision D)

Divisions 02 and 31–33 go to Civil & Site; 03, 05–10 and 13 to Structural & Building; 22, 23 and 40–46 to Process & Mechanical; 26 to Electrical & Controls; Divisions 00 and 01 plus Appendices D, E and I to Contract & General (decision A). Accepted judgment calls:

- 10 73 05 FRP Launder Covers → Process & Mechanical.
- 15 40 00 Misc. Plumbing → Process & Mechanical.
- 15 08 13 Temporary Construction Sign → Civil & Site.
- 23 34 00 Wall Fans & Louvered Vents → Process & Mechanical; cross-check E9.3 and A sheets.
- 33 30 00 Piping Systems → Civil & Site; cross-check Process & Mechanical for in-plant piping.
- Appendix F Plan of Interim Operation → Civil & Site, the same subject as sheet C0.7.

## Section table (document order)

| Section (body) | Title (TOC) | Start p. | End p. | Pages | Div 26 file p. | Lane | Addendum 4 | Notes | Tag |
|---|---|---|---|---|---|---|---|---|---|
| Cover | Cover (p.2 repeats the cover) | 1 | 2 | 2 | — | Index only | — | Date Dec. 30, 2022 | Verified |
| 00 00 00 | Engineer's Statement | 3 | 3 | 1 | — | Index only | — | Number from header only; not listed in TOC | Verified (header) |
| 00 01 00 | Table of Contents | 4 | 7 | 4 | — | Index only | — |  | Verified |
| — | Part 1 divider — Bidding Requirements | 8 | 8 | 1 | — | Index only | — |  | Verified |
| 00 11 16 | Invitation to Bid | 9 | 10 | 2 | — | Contract & General | — |  | Verified |
| 00 21 13 | Instructions to Bidders | 11 | 15 | 5 | — | Contract & General | — |  | Verified |
| 00 24 13 | Scopes of Bids | 16 | 20 | 5 | — | Contract & General | — | Bid item scopes → 04_Bid_Item_Spine.md | Verified |
| 00 31 13 | Preliminary Project Phase | 21 | 22 | 2 | — | Contract & General | — |  | Verified |
| 00 41 00 | Bid Proposal | 23 | 28 | 6 | — | Contract & General | Bid Item #18 cited — Add. 4 p.1, Clarification 5 (conflict) | Bid items and alternates → 04_Bid_Item_Spine.md. Bid Item #18 (p.25) conflicts with Add. 4 — Unresolved; flag: Merge exception report | Verified |
| 00 43 13 | Bid Bond Form | 29 | 29 | 1 | — | Contract & General | — |  | Verified |
| 00 43 93 | Bid Submittal Checklist | 30 | 30 | 1 | — | Contract & General | — |  | Verified |
| 00 45 13 | Contractor Qualifications | 31 | 31 | 1 | — | Contract & General | — |  | Verified |
| 00 45 19 | Non-Collusion Affidavit | 32 | 32 | 1 | — | Contract & General | — |  | Verified |
| 00 45 29 | Cert. of Compliance with Wage Payment Statues | 33 | 33 | 1 | — | Contract & General | — |  | Verified |
| 00 45 33 | List of Subcontractors – Bids on Public Works – Ident., Substitution of Subcontractors | 34 | 35 | 2 | — | Contract & General | — |  | Verified |
| 00 45 43 | Subcontractor Qualifications | 36 | 36 | 1 | — | Contract & General | — |  | Verified |
| — | Part 2 divider — Contracting Requirements | 37 | 37 | 1 | — | Index only | — |  | Verified |
| 00 51 00 | Notice of Award | 38 | 38 | 1 | — | Contract & General | — |  | Verified |
| 00 52 00 | Agreement Form | 39 | 40 | 2 | — | Contract & General | — |  | Verified |
| 00 53 00 | WPCRF Inserts | 41 | 65 | 25 | — | Contract & General | — |  | Verified |
| 00 54 00 | CDBG Conditions | 66 | 82 | 17 | — | Contract & General | — |  | Verified |
| 00 55 00 | Notice to Proceed | 83 | 83 | 1 | — | Contract & General | — |  | Verified |
| 00 61 13 | Performance & Payment Bond Forms | 84 | 86 | 3 | — | Contract & General | — |  | Verified |
| 00 61 23 | Retainage Bond Form | 87 | 87 | 1 | — | Contract & General | — |  | Verified |
| 00 73 00 | Supplementary Conditions | 88 | 121 | 34 | — | Contract & General | — |  | Verified |
| — | Part 3 divider — Technical Specifications | 122 | 122 | 1 | — | Index only | — |  | Verified |
| 01 11 10 | Summary of Work | 123 | 125 | 3 | — | Contract & General | — | Body number governs; alias 01 11 00 accepted (decision E); stays Unresolved — see conflict log | Unresolved |
| 01 31 00 | Project Coordination | 126 | 128 | 3 | — | Contract & General | — |  | Verified |
| 01 33 00 | Submittal Procedures | 129 | 132 | 4 | — | Contract & General | — |  | Verified |
| 01 41 00 | Regulatory Requirements | 133 | 135 | 3 | — | Contract & General | — |  | Verified |
| 01 45 00 | Quality Control | 136 | 141 | 6 | — | Contract & General | — |  | Verified |
| 01 50 00 | Temporary Facilities | 142 | 145 | 4 | — | Contract & General | — |  | Verified |
| 01 60 00 | Product Requirements | 146 | 148 | 3 | — | Contract & General | — |  | Verified |
| 01 66 00 | Product Storage and Handling Requirements | 149 | 151 | 3 | — | Contract & General | — |  | Verified |
| 01 70 00 | Execution and Closeout Requirements | 152 | 156 | 5 | — | Contract & General | — |  | Verified |
| 01 91 00 | Commissioning | 157 | 160 | 4 | — | Contract & General | — |  | Verified |
| 02 41 00 | Demolition | 161 | 162 | 2 | — | Civil & Site | — |  | Verified |
| 02 83 00 | Chain Link Fences and Gates | 163 | 168 | 6 | — | Civil & Site | — |  | Verified |
| 02 92 00 | Landscaping | 169 | 171 | 3 | — | Civil & Site | — |  | Verified |
| 03 30 00 | Cast-in-Place Concrete | 172 | 180 | 9 | — | Structural & Building | — |  | Verified |
| 03 40 00 | Precast Concrete | 181 | 185 | 5 | — | Structural & Building | — |  | Verified |
| 05 50 00 | Metal Fabrications | 186 | 199 | 14 | — | Structural & Building | — |  | Verified |
| 05 51 10 | Steel Stairs, Ladders and Grating Platforms | 200 | 202 | 3 | — | Structural & Building | — |  | Verified |
| 05 52 00 | Aluminum Handrailing and Guardrailing | 203 | 204 | 2 | — | Structural & Building | — |  | Verified |
| 05 53 00 | Grating | 205 | 206 | 2 | — | Structural & Building | — |  | Verified |
| 06 20 00 | Finish Carpentry | 207 | 208 | 2 | — | Structural & Building | — | Header reads 13 12 20 — see conflict log | Verified |
| 07 20 00 | Insulation | 209 | 210 | 2 | — | Structural & Building | — |  | Verified |
| 07 92 00 | Joint Sealants (TOC: Joint Seals) | 211 | 213 | 3 | — | Structural & Building | — | Header reads 13 12 20 — see conflict log | Verified |
| 08 10 00 | Metal Doors and Frames | 214 | 215 | 2 | — | Structural & Building | — |  | Verified |
| 08 70 00 | Finish Hardware | 216 | 224 | 9 | — | Structural & Building | — |  | Verified |
| 09 25 00 | Gypsum Drywall | 225 | 228 | 4 | — | Structural & Building | — |  | Verified |
| 09 90 00 | Misc. Plant Painting | 229 | 235 | 7 | — | Structural & Building | Add. 4 p.2, ¶2.01 I — Add. 4 governs |  | Verified |
| 09 97 23 | Concrete Protective Coating | 236 | 241 | 6 | — | Structural & Building | — |  | Verified |
| 10 52 00 | Fire Extinguishers | 242 | 242 | 1 | — | Structural & Building | — |  | Verified |
| 10 73 05 | FRP Launder Covers | 243 | 245 | 3 | — | Process & Mechanical | — |  | Verified |
| 13 12 20 | Metal Building Systems | 246 | 251 | 6 | — | Structural & Building | Cited, no change — Add. 4 p.1, Clarification 3 (¶2.03, ¶2.04) |  | Verified |
| 15 08 13 | Temporary Construction Sign | 252 | 252 | 1 | — | Civil & Site | — |  | Verified |
| 15 40 00 | Misc. Plumbing | 253 | 254 | 2 | — | Process & Mechanical | — |  | Verified |
| 22 13 29 | Submersible Sewerage Pumps | 255 | 262 | 8 | — | Process & Mechanical | — | Header spelling — see conflict log | Verified |
| 22 13 36 | Packaged Sludge Pumps | 263 | 264 | 2 | — | Process & Mechanical | Add. 4 p.2, ¶2.01 A — Add. 4 governs |  | Verified |
| 23 34 00 | Wall Fans and Louvered Vents | 265 | 267 | 3 | — | Process & Mechanical | — |  | Verified |
| 26 00 00 | Electrical TOC | 268 | 268 | 1 | 1 | Index only | — | No number in header or body; number per TOC p.5 | Inferred |
| 26 05 00 | General Electrical | 269 | 281 | 13 | 2–14 | Electrical & Controls | — |  | Verified |
| 26 05 19 | Wire and Cable | 282 | 288 | 7 | 15–21 | Electrical & Controls | — |  | Verified |
| 26 05 26 | Grounding and Bonding | 289 | 289 | 1 | 22 | Electrical & Controls | — |  | Verified |
| 26 05 33 | Raceways and Boxes | 290 | 296 | 7 | 23–29 | Electrical & Controls | — |  | Verified |
| 26 22 13 | Dry Type Transformers | 297 | 299 | 3 | 30–32 | Electrical & Controls | — |  | Verified |
| 26 24 16 | Panelboards | 300 | 304 | 5 | 33–37 | Electrical & Controls | — |  | Verified |
| 26 24 19 | Motor Control Centers | 305 | 311 | 7 | 38–44 | Electrical & Controls | — |  | Verified |
| 26 27 26 | Wiring Devices | 312 | 313 | 2 | 45–46 | Electrical & Controls | — |  | Verified |
| 26 28 16 | Disconnects and Switches | 314 | 315 | 2 | 47–48 | Electrical & Controls | — |  | Verified |
| 26 29 23 | Variable Frequency Drives | 316 | 320 | 5 | 49–53 | Electrical & Controls | — |  | Verified |
| 26 32 13 | Diesel Emergency Engine Generators | 321 | 337 | 17 | 54–70 | Electrical & Controls | — |  | Verified |
| 26 36 00 | Automatic Transfer Switches | 338 | 348 | 11 | 71–81 | Electrical & Controls | — | Header reads 26 30 00 — see conflict log | Verified |
| 26 51 19 | LED Lighting | 349 | 351 | 3 | 82–84 | Electrical & Controls | — |  | Verified |
| 26 80 00 | Control System | 352 | 381 | 30 | 85–114 | Electrical & Controls | Add. 4 p.2, ¶2.04 D — Add. 4 governs | Header title differs — see conflict log | Verified |
| 31 10 00 | Site Clearing | 382 | 382 | 1 | — | Civil & Site | — | Header title wrong — see conflict log | Verified |
| 31 20 00 | Earthwork | 383 | 388 | 6 | — | Civil & Site | — | Cites Sept 7, 2021 geotech report (p.383); Appendix C dates differ — Unresolved; flag: Merge exception report | Verified |
| 31 23 19 | Dewatering | 389 | 392 | 4 | — | Civil & Site | — |  | Verified |
| 31 23 33 | Trenching and Backfilling | 393 | 397 | 5 | — | Civil & Site | — | Header wording — see conflict log | Verified |
| 31 32 11 | Soil Surface Erosion Control | 398 | 400 | 3 | — | Civil & Site | — |  | Verified |
| 31 40 00 | Temporary Shoring Bracing | 401 | 403 | 3 | — | Civil & Site | — |  | Verified |
| 32 12 16 | Hot Mix Asphalt Paving | 404 | 407 | 4 | — | Civil & Site | — |  | Verified |
| 32 32 23 | Gravity Block Retaining Wall | 408 | 412 | 5 | — | Civil & Site | — |  | Verified |
| 33 05 00 | Common Works Results for Utilities | 413 | 419 | 7 | — | Civil & Site | — |  | Verified |
| 33 30 00 | Piping Systems | 420 | 429 | 10 | — | Civil & Site | — |  | Verified |
| 33 31 00 | Wastewater Piping | 430 | 435 | 6 | — | Civil & Site | — |  | Verified |
| 33 32 00 | Water Distribution Piping | 436 | 443 | 8 | — | Civil & Site | — |  | Verified |
| 33 33 00 | HDPE Piping | 444 | 446 | 3 | — | Civil & Site | — |  | Verified |
| 33 41 00 | Storm Utility Drainage Piping | 447 | 450 | 4 | — | Civil & Site | Add. 4 p.2, ¶2.02 — Add. 4 governs |  | Verified |
| 40 05 71 | Telescoping Valve | 451 | 452 | 2 | — | Process & Mechanical | — |  | Verified |
| 41 12 13 | Screw Conveyor System | 453 | 461 | 9 | — | Process & Mechanical | — |  | Verified |
| 43 11 00 | Blower Equipment | 462 | 471 | 10 | — | Process & Mechanical | — | Pages numbered 431100-1 to -10, no total — see conflict log | Verified |
| 43 22 10 | 2W Plant Water System Equipment | 472 | 475 | 4 | — | Process & Mechanical | Add. 4 p.2, ¶2.01 A — Add. 4 governs |  | Verified |
| 45 05 00 | Valves | 476 | 480 | 5 | — | Process & Mechanical | — |  | Verified |
| 46 33 33 | Emulsion Polymer Make-up System | 481 | 485 | 5 | — | Process & Mechanical | — |  | Verified |
| 46 41 23 | Submersible Mixers | 486 | 490 | 5 | — | Process & Mechanical | — |  | Verified |
| 46 51 21 | Coarse Bubble Diffusers | 491 | 491 | 1 | — | Process & Mechanical | — |  | Verified |
| 46 53 00 | Biological Treatment System | 492 | 501 | 10 | — | Process & Mechanical | — |  | Verified |
| 46 66 00 | UV Equipment | 502 | 508 | 7 | — | Process & Mechanical | — |  | Verified |
| 46 66 10 | UV Analytical Equipment | 509 | 509 | 1 | — | Process & Mechanical | — |  | Verified |
| 46 76 26 | Rotary Fan Press System | 510 | 531 | 22 | — | Process & Mechanical | — |  | Verified |
| — | Part 4 divider — Reference Documents | 532 | 532 | 1 | — | Index only | — |  | Verified |
| Appendix A | Anticipated Construction Sequence and Schedule | 533 | 533 | 1 | — | Index only | — | Pointer page: see 00 31 13 | Verified |
| Appendix B | Groundwater Level Analysis | 534 | 535 | 2 | — | Civil & Site | — |  | Verified |
| Appendix C | Geotechnical Report | 536 | 578 | 43 | — | Civil & Site | — | GeoEngineers report dated Nov 8, 2022 (p.537) + report addendum dated Dec 16, 2022 (p.577); deferred (decision G): no text and no stored image, p.539, 576, 578 | Verified |
| Appendix D | Washington State Prevailing Wage Rates | 579 | 601 | 23 | — | Contract & General | — |  | Verified |
| Appendix E | Federal Prevailing Wage Rates | 602 | 610 | 9 | — | Contract & General | — |  | Verified |
| Appendix F | Interim Plan of Operation | 611 | 620 | 10 | — | Civil & Site | — |  | Verified |
| Appendix G | Inadvertent Discovery Plan | 621 | 637 | 17 | — | Civil & Site | — | Deferred (decision G): no text and no stored image, p.628, 629, 630, 631, 632, 633, 634, 635, 636, 637 | Verified |
| Appendix H | Septic Tank Layout Drawing | 638 | 639 | 2 | — | Civil & Site | — | Deferred (decision G): no text and no stored image, p.639 | Verified |
| Appendix I | CDBG Funding- Required Documents | 640 | 645 | 6 | — | Contract & General | — |  | Verified |

## Header / body / TOC conflict log (decision 4)

| # | Section (body) | PDF pages | Conflict | Running header | Body | TOC | Resolution | Tag |
|---|---|---|---|---|---|---|---|---|
| 1 | 01 11 10 | 123–125 | Section number | 01 11 00 SUMMARY OF WORK | SECTION 01 11 10 – SUMMARY OF WORK | 01 11 00 Summary of Work (p.4) | Indexed as 01 11 10 per decision 4; alias 01 11 00 accepted (decision E). The body is likely a typo (MasterFormat 01 11 00 = Summary of Work; Inferred). | Unresolved |
| 2 | 06 20 00 | 207–208 | Section number and title | 13 12 20 METAL BUILDING SYSTEMS | SECTION 06 20 00 - FINISH CARPENTRY | 06 20 00 Finish Carpentry | Body governs | Verified |
| 3 | 07 92 00 | 211–213 | Section number and title | 13 12 20 METAL BUILDING SYSTEMS | SECTION 07 92 00 - JOINT SEALANTS | 07 92 00 Joint Seals | Body governs; title per body | Verified |
| 4 | 26 36 00 | 338–348 (Div 26 file 71–81) | Section number | 26 30 00 AUTOMATIC TRANSFER SWITCHES | SECTION 26 36 00 – AUTOMATIC TRANSFER SWITCHES | 26 36 00 | Body governs | Verified |
| 5 | 31 10 00 | 382 | Title | 31 10 00 WALL FANS & LOUVERED VENTS | SECTION 31 10 00 – SITE CLEARING | Site Clearing | Body governs | Verified |
| 6 | 26 80 00 | 352–381 (Div 26 file 85–114) | Title | 26 80 00 INSTRUMENTATION AND CONTROL | SECTION 26 80 00 – CONTROL SYSTEM | Control System | Body governs | Verified |
| 7 | 22 13 29 | 255–262 | Title spelling | SUMBERSIBLE SEWERAGE PUMPS | SUBMERSIBLE SEWERAGE PUMPS | Submersible Sewerage Pumps | Body governs | Verified |
| 8 | 31 23 33 | 393–397 | Title wording | TRENCHING AND BACKFILLING | TRENCHING AND BACKFILL | Trenching and Backfilling | Body governs | Verified |
| 9 | 43 11 00 | 462–471 | Page numbering | PAGE 431100-1 … 431100-10 (no total) | SECTION 43 11 00 – BLOWER EQUIPMENT | 43 11 00 | Count by sequence (10 pages) | Verified |
| 10 | 26 00 00 | 268 (Div 26 file 1) | No section number in header or body | ELECTRICAL TABLE OF CONTENTS | (no SECTION line) | Electrical TOC 26 00 00 (p.5) | Number from TOC only | Inferred |
| 11 | 00 00 00 | 3 | No body SECTION line; not in TOC | 00 00 00 ENGINEER'S STATEMENT | (no SECTION line) | (not listed) | Number from header only | Verified (header) |

Also checked, abbreviation or truncation only (not conflicts): headers of 00 45 29, 00 45 33, 00 45 43, 00 61 13, 01 66 00, 01 70 00, 26 32 13, 31 40 00.

## Unresolved spec items flagged for the Merge exception report

1. **Bid Item #18.** Add. 4 p.1 Clarification 5 titles it "Temporary Back Up Generator (Bid Item #18)". Base 00 41 00 (p.25) lists item 18 as "Train 3 – Stainless Steel Fabrication Above Water Surface, 1 LS" under Bid Alternate 1 (Verified). Full conflict record and base references: 04_Bid_Item_Spine.md.
2. **Geotech report date.** 31 20 00 ¶1.01 B (p.383) cites a "September 7, 2021 Geotechnical Engineering Report, GeoEngineers". Appendix C holds GeoEngineers documents dated November 8, 2022 (p.537) and December 16, 2022 (report addendum, p.577); the 2021 date appears nowhere in Appendix C (Verified). Both are base documents, so no addendum governs. Needed: engineer confirmation or the 2021 report.

## Pages with no text and no stored image (deferred, decision G)

p.539, 576, 578, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 639: Appendix C (p.539, 576, 578), Appendix G (p.628–637), Appendix H septic tank layout drawing (p.639). Not blocking. When page images are uploaded, they come back to the Setup thread.
