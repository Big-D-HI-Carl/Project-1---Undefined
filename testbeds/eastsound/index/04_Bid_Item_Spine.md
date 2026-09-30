# 04 Bid Item Spine

Every bid item and alternate on the Phase I bid form, with its scope reference, lane, and every addendum item that references it. Ledger "Bid Item" values come from this file.

- **Version:** rev0, issued 2026-09-29 · **Owner:** Setup thread (single writer)
- **Changes:** Initial issue.
- **Project:** Eastsound Sewer and Water District, Wastewater Treatment Plant Upgrade Phase I (Wilson Engineering job 2020-070). Public bid set; test bed only.
- **Source:** Claude Project copy of the library (read-only converted copies, not native PDFs).
- **Tags:** Verified = read in the stored text layer · Verified-Visual = read from the page image · Inferred = derived, basis stated · Unresolved = conflict or missing, need stated.
- **Rules:** addenda supersede base documents (cite both, state which governs) · the body section number governs over the running header and the TOC · duplicates are not indexed: the Division 26 file (use the main spec) and plans_7 pp.1–3 (use plans_6) · claims that defer to WSDOT are tagged "Unresolved: external reference, not staged."
- **Terms:** thread = a chat (Setup, Composer, Merge) · lane = a crawl scope only (Civil & Site, Process & Mechanical, Electrical & Controls, Structural & Building, Contract & General).
- **Short names:** plans_N = `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_N.pdf` · Add. 4 = `addendum-no4-eswd.pdf` · main spec = `eswd-wwtp-upgrade-phase-i-specs.pdf` · p. = PDF page within the named file.

## Sources

- **Bid form:** 00 41 00 Bid Proposal, main spec pp.23–28: items pp.23–25; manufacturers list and equipment alternates pp.26–27; notes p.27 (Verified).
- **Scopes:** 00 24 13 Scopes of Bids, pp.16–20; bid form Note 2 points here (Verified).
- **Award basis:** 00 21 13 Instructions to Bidders p.14: the Owner may award the bid schedules and bid alternates in any combination (Verified).
- **Addenda:** Add. 4 only. Addenda 1–3 are not in the library and may revise the bid form (Unresolved).

**Ledger link:** the Ledger "Bid Item" column takes the item number (1–19) or "Equipment Alternate A"–"E". Item 1 carries all Contract Document work not itemized elsewhere (Inferred from 00 24 13 ¶1). Rows touching either #18 scope carry "18 — Unresolved (see 04)" until Addenda 1–3 are reviewed.

## Bid items (bid form order)

Item facts (number, description, quantity, unit, group, bid form page, Owner-entered amounts) are Verified. Base / Alternate for items 2–17 is Inferred: those items carry no alternate label. Lanes are Inferred from the scope reference and the 02 lane mapping.

| Item | Description (bid form) | Approx. qty | Unit | Group (as printed) | Base / Alternate | Amount entered by Owner | Bid form p. | Scope (00 24 13) | References in scope | Lane (Inferred) | Addenda referencing | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | WWTP Upgrade | 1 | LS | Base Bid – WWTP Expansion | Base | — | 23 | ¶1, p.16 (measured by Schedule of Values) | All Contract Documents; equipment basis per manufacturers list p.26 | All lanes (lump sum) | None explicit (see Add. 4 map) | — |
| 2 | Trench Safety Excavation Provisions | 1 | LS | Unit Quantity Bid Items | Base (Inferred) | — | 23 | ¶2, p.16 (titled "Trench Safety System") | WSDOT and OSHA rules — Unresolved: external reference, not staged. | Civil & Site | None explicit (see Add. 4 map) | Title wording differs in 00 24 13 (logged) |
| 3 | Bollards | 12 | EA | Unit Quantity Bid Items | Base (Inferred) | — | 23 | ¶3, p.16 | — | Civil & Site | None explicit (see Add. 4 map) | — |
| 4 | SWPPP Preparation | 1 | LS | Unit Quantity Bid Items | Base (Inferred) | — | 23 | ¶4, p.17 | 31 32 11; TESC plans; NPDES permit | Civil & Site | None explicit (see Add. 4 map) | — |
| 5 | Maintenance Work for SWPPP | 1 | LS | Unit Quantity Bid Items | Base (Inferred) | — | 23 | ¶5, p.17 | SWPPP; NPDES permit | Civil & Site | None explicit (see Add. 4 map) | — |
| 6 | Electrical | 1 | LS | Unit Quantity Bid Items | Base (Inferred) | — | 23 | ¶6, p.17 | All E sheets; Division 26 (breakdowns in 26 05 00, 26 80 00) | Electrical & Controls | None explicit (see Add. 4 map) | — |
| 7 | Minor Changes | 1 | EST. | Unit Quantity Bid Items | Base (Inferred) | $100,000.00 | 23 | ¶7, p.17 | General Conditions change procedure | Contract & General | None explicit (see Add. 4 map) | — |
| 8 | HMA Pavement | 10 | TN | Extra Work Items | Base (Inferred) | — | 24 | ¶8, p.17 | 32 12 16 | Civil & Site | None explicit (see Add. 4 map) | — |
| 9 | Structural Concrete | 10 | CY | Extra Work Items | Base (Inferred) | — | 24 | ¶9, p.18 | — | Structural & Building | None explicit (see Add. 4 map) | — |
| 10 | Over Excavation | 10 | CY | Extra Work Items | Base (Inferred) | — | 24 | ¶10, p.18 | — | Civil & Site | None explicit (see Add. 4 map) | — |
| 11 | Crushed Surfacing Top Course | 10 | TN | Extra Work Items | Base (Inferred) | — | 24 | ¶11, p.18 | WSDOT 9-03.9(3) — Unresolved: external reference, not staged. | Civil & Site | None explicit (see Add. 4 map) | — |
| 12 | Crushed Surfacing Base Course | 10 | TN | Extra Work Items | Base (Inferred) | — | 24 | ¶12, p.18 | WSDOT 9-03.9(3) — Unresolved: external reference, not staged. | Civil & Site | None explicit (see Add. 4 map) | — |
| 13 | Gravel Base | 10 | TN | Extra Work Items | Base (Inferred) | — | 24 | ¶13, p.19 | WSDOT 9-03.10 — Unresolved: external reference, not staged. | Civil & Site | None explicit (see Add. 4 map) | — |
| 14 | Gravel Backfill for Pipe Zone Bedding | 10 | TN | Extra Work Items | Base (Inferred) | — | 24 | ¶14, p.19 | WSDOT 9-03.12(3) — Unresolved: external reference, not staged. | Civil & Site | None explicit (see Add. 4 map) | — |
| 15 | Gravel Borrow | 10 | TN | Extra Work Items | Base (Inferred) | — | 24 | ¶15, p.19 | WSDOT 9-03.14(1) — Unresolved: external reference, not staged. | Civil & Site | None explicit (see Add. 4 map) | — |
| 16 | Bank Run Gravel for Trench Backfill | 10 | TN | Extra Work Items | Base (Inferred) | — | 24 | ¶16, p.19 | WSDOT 9-03.19 — Unresolved: external reference, not staged. | Civil & Site | None explicit (see Add. 4 map) | — |
| 17 | Extra SCADA/PLC Programmer Services | 1 | FA | Extra Work Items | Base (Inferred) | $100,000.00 | 24 | ¶17, pp.19–20 | Force account per WSDOT 1-09.6 — Unresolved: external reference, not staged. | Electrical & Controls | None explicit (see Add. 4 map) | — |
| 18 | Train 3 – Stainless Steel Fabrication Above Water Surface | 1 | LS | Bid Alternate 1 | Alternate (additive) | — | 25 | ¶18, p.20 | 46 53 00 | Process & Mechanical | Add. 4 p.1, Clarification 5 cites "Bid Item #18" as the temporary back-up generator — conflict | Conflict — Unresolved; flag: Merge exception report |
| 19 | Train 3 – Stainless Steel Fabrication Throughout | 1 | LS | Bid Alternate 2 | Alternate (additive) | — | 25 | ¶19, p.20 | 46 53 00 | Process & Mechanical | None explicit (see Add. 4 map) | — |

## Equipment alternates (deductive)

The bid form states that Base Bid Item #1 is based on the listed manufacturers (p.26). Alternates A–E are lump-sum deductions for other manufacturers, A–D on p.26 and E on p.27 (Verified). Spec links are Inferred by equipment title.

| Alternate | Description (bid form) | Base-bid manufacturer(s) | Pricing | Tied to | Spec section | Lane (Inferred) | Addenda referencing | Status |
|---|---|---|---|---|---|---|---|---|
| Equipment Alternate A | Furnish Submersible Pump Equipment other than specified | Flygt | Lump sum deduction | Base Bid Item 1 (p.26) | 22 13 29 (Inferred) | Process & Mechanical | None explicit | — |
| Equipment Alternate B | Furnish Biological Treatment System Equipment other than specified | Smith and Loveless | Lump sum deduction | Base Bid Item 1 (p.26) | 46 53 00 (Inferred) | Process & Mechanical | None explicit | — |
| Equipment Alternate C | Furnish Rotary Fan Press Dewatering Equipment other than specified | Fournier, Prime Solutions | Lump sum deduction | Base Bid Item 1 (p.26) | 46 76 26 (Inferred) | Process & Mechanical | None explicit | — |
| Equipment Alternate D | Furnish UV Disinfection Equipment other than specified | Trojan | Lump sum deduction | Base Bid Item 1 (p.26) | 46 66 00 (Inferred) | Process & Mechanical | None explicit | — |
| Equipment Alternate E | Furnish Generator Equipment other than specified | Cummins, Kohler, Caterpillar, Generac | Lump sum deduction | Base Bid Item 1 (p.26) | 26 32 13 (Inferred) | Electrical & Controls | None explicit | Item 1 vs Item 6 — Unresolved (see conflicts) |

## Bid form structure

- **Subtotals:** unit quantity bid items 2–7 (p.23); extra work items 8–17 (p.24); Bid Alternate 1, item 18 and Bid Alternate 2, item 19 (p.25); items 1–19, then 8.3% sales tax (Eastsound Sewer and Water District, San Juan County), then total bid (p.25). Verified.
- **Owner-entered amounts:** Item 7 Minor Changes $100,000.00 (EST.); Item 17 Extra SCADA/PLC Programmer Services $100,000.00 (FA). Verified.
- **Mobilization:** no separate item. Note 1 (p.27) puts mobilization payment under WSDOT 1-09.7 — Unresolved: external reference, not staged. Mobilization sits inside Item 1 (Inferred).
- **Receipt of addenda:** six blank acknowledgment slots (p.27). Verified.

## Addendum references to bid items

**Explicit citations (Verified): one.**

| Addendum item | Add. 4 p. | Bid item cited | Status |
|---|---|---|---|
| Clarification 5 — "Temporary Back Up Generator (Bid Item #18) – General Questions"; rental generator exhibit | p.1; pp.11–13 | 18 | Conflict — Unresolved; flag: Merge exception report |

**Add. 4 items with no bid-item citation → likely bid item (Inferred).** Basis: 00 24 13 ¶6 (p.17) puts all E-sheet and Division 26 work in Item 6; ¶1 (p.16) puts all other Contract Document work in Item 1.

| Add. 4 item | Add. 4 p. | Likely bid item(s) | Basis |
|---|---|---|---|
| Clarification 1 — surfacing demolition information (C0.5, C2.6) | p.1 | 1 | ¶1: all Contract Document work |
| Clarification 2 — exterior sealant, precast wet well and vault joints | p.1 | 1 | ¶1 |
| Clarification 3 — Q&A, metal building factory finish (13 12 20) | p.1 | 1 | ¶1 |
| Clarification 4 — Q&A, MCC size (E9.1); blower building footprint (A1.1) | p.1 | 6 (MCC); 1 (building) | ¶6: E sheets and Division 26; ¶1 |
| Clarification 5 — temporary back-up generator | p.1; exhibit pp.11–13 | Cited as 18 (conflict); by content 6 | 26 05 00 temporary power (pp.276, 279) is Division 26 → ¶6 |
| Specifications — 09 90 00 ¶2.01 I | p.2 | 1 | ¶1 |
| Specifications — 22 13 36 ¶2.01 A | p.2 | 1 (pumps); 6 (VFDs in the MCC) | ¶1; ¶6 |
| Specifications — 26 80 00 ¶2.04 D | p.2 | 6 | ¶6 names 26 80 00 |
| Specifications — 33 41 00 ¶2.02 | p.2 | 1 | ¶1 |
| Specifications — 43 22 10 ¶2.01 A | p.2 | 1 (pumps); 6 (VFDs in the MCC) | ¶1; ¶6 |
| Drawings — A1.1, A1.2 | p.3; sheets pp.4–5 | 1; 6 (MCC and control panel moves on A1.1) | ¶1; ¶6 |
| Drawings — C6.4 | p.3; sheet p.6 | 1 | ¶1 |
| Drawings — C1.3 | p.3; sheet p.7 | 1; 6 (hot box conduit and wiring moves per markup) | ¶1; ¶6 |
| Drawings — C1.6A | p.3; sheet p.8 | 1 | ¶1 |
| Drawings — S2.3, S4.1 | p.3; sheets pp.9–10 | 1 | ¶1 |

## Bid Item #18 conflict (flag: Merge exception report)

- **Source A — Add. 4 (Feb 9, 2023) p.1, Clarification 5:** heading "Temporary Back Up Generator (Bid Item #18) – General Questions"; rental generator exhibit pp.11–13. Verified.
- **Source B — base bid form 00 41 00 p.25:** Item 18 = "Train 3 – Stainless Steel Fabrication Above Water Surface", 1 LS, Bid Alternate 1. 00 24 13 ¶18 (p.20) matches. Verified.
- **Base references to a temporary generator:** 00 31 13 p.21 lists the milestone "Rent Temporary 480V Generator: Sept 25, 2023". 26 05 00 p.276 has the Contractor provide temporary equipment, including a power generator. 26 05 00 p.279 lists temporary power provisions limiting facility downtime to 20 minutes or less. "Temporary" appears nowhere in 00 41 00. Verified.
- **Governs:** Unresolved. Add. 4 is the latest document, but it doesn't reissue the bid form, so it can't be read as renumbering the items.
- **Readings (Inferred):** either an earlier addendum revised the bid form and added a temporary-generator item as #18, shifting the alternates; or Add. 4 cites the wrong item number, and the temporary generator stays in Item 6 through 26 05 00.
- **Needed:** Addenda 1–3 or the conformed bid form.

## Other bid-item conflicts

| # | Conflict | Source A | Source B | Status |
|---|---|---|---|---|
| 1 | Which item carries the permanent standby generator | 00 41 00 p.26: Base Bid Item #1 is based on the listed generator manufacturers; Equipment Alternate E is its deduction | 00 24 13 ¶6 (p.17): all Division 26 work is Item 6; generators are specified in 26 32 13 | Unresolved — candidate for the Merge exception report (owner to confirm) |
| 2 | Item 2 title | Bid form p.23: "Trench Safety Excavation Provisions" | 00 24 13 ¶2 (p.16): "Trench Safety System" | Wording only; same item and unit. Logged. |
