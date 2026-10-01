# Project Ledger rev2 — Summary

Prompt 11: rev1 plus the owner's six decisions. rev2 is the current Ledger; rev0 (`Project_Ledger.csv`) and rev1 (`Project_Ledger_rev1.csv`) are history and unchanged. Built by `testbeds/eastsound/tools/build_ledger_rev2.py`, which imports `build_ledger_rev1.py` (no LLM calls, deterministic, no library reads).

## Files

| File | What it holds |
|---|---|
| Project_Ledger_rev2.csv | 529 rows × 39 columns, in `index/Ledger_Schema_rev1.csv` order |
| Project_Ledger_rev2.xlsx | The rev1 tabs (Ledger, MTO Lines, Coverage, Candidates, Column Guide, Links) plus Totals. The Ledger tab adds "Total incl. reads to verify" beside Quantity |
| MTO_Lines_rev2.csv | 190 MTO lines (machine copy of the MTO Lines tab; the graph reads it) |
| Ledger_rev2_Summary.md | This file |

## Changes applied

### 1. The 14 Verified proposals (Ledger_Update_Proposal.csv)

The 229 "needs check" proposals are left as they are.

| Proposal | Ledger ID | Tag (rev1) | Change | Evidence |
|---|---|---|---|---|
| P-0005 | L-0057 | Hot Box #1 | adds E4.3 to Drawing Sheets | E4.3 set p.72 [174.42,313.08,202.64,318.11], text-layer |
| P-0007 | L-0057 | Hot Box #1 | adds E7.4 to Drawing Sheets | E7.4 set p.81 [845.95,280.68,875.57,285.71], text-layer |
| P-0008 | L-0057 | Hot Box #1 | adds E10.2 to Drawing Sheets | E10.2 set p.95 [332.01,616.02,363.03,621.05], text-layer |
| P-0010 | L-0058 | Hot Box #2 | adds E4.3 to Drawing Sheets | E4.3 set p.72 [174.96,68.10,203.18,73.13], text-layer |
| P-0017 | L-0272 | EF-1 | adds E0.1 to Drawing Sheets | E0.1 set p.62 [312.30,85.56,323.20,90.59], text-layer |
| P-0018 | L-0312 | DW-1 | adds E2.1 to Drawing Sheets | E2.1 set p.67 [981.54,371.58,999.42,376.61], text-layer |
| P-0234 | L-0337 | PROPOSED-Hot-Box-1 | Tag 'PROPOSED-Hot-Box-1' -> 'Hot Box #1' | E4.3 set p.72 [174.42,313.08,202.64,318.11], text-layer |
| P-0235 | L-0338 | PROPOSED-Hot-Box-2 | Tag 'PROPOSED-Hot-Box-2' -> 'Hot Box #2' | E4.3 set p.72 [174.96,68.10,203.18,73.13], text-layer |
| P-0238 | L-0239 | ATS | Bid Item -> '6 (permanent ATS); 18 (temporary generator hookup and automatic load transfer test, Add. 4 p.1 Clarification 5)' | Add. 4 p.1 [94.31,458.99,442.55,572.45], text-layer (native) |
| P-0239 | L-0239 | ATS | Confidence Unresolved -> Inferred | Add. 4 p.1 [94.31,458.99,539.80,572.45], text-layer (native) |
| P-0240 | L-0241 | TS | Confidence Inferred -> Verified | E1.1 set p.66 [609.48,295.98,644.42,318.65], text-layer (native) |
| P-0241 | L-0242 | GEN | Notes take the RFI reason; the tag stays Unresolved | E1.1 set p.66 [216.90,504.24,251.93,515.21]; E6.1 set p.74 [255.78,255.12,293.23,260.15]; main spec p.326 [144.00,108.16,540.17,160.23], text-layer (native) |
| P-0242 | L-0297 | T3 | Confidence Inferred -> Verified | E6.1 set p.74 [1035.18,612.60,1067.13,631.67], text-layer (native) |
| P-0243 | L-0349 | T2 | Confidence Inferred -> Verified | E6.1 set p.74 [1058.04,384.90,1089.63,403.79]; E9.1 set p.91 [644.22,175.74,739.24,180.77], text-layer (native) |

### 2. Hot Box duplicates

L-0337 and L-0338 keep their IDs (IDs are permanent). Their Tags are the printed "Hot Box #1" and "Hot Box #2" (P-0234, P-0235), their Status is "Duplicate of L-0057" and "Duplicate of L-0058", and they count in no MTO total. Their link cells read "Not linked (duplicate of …; links moved there)". Drawing Sheets and the schedule columns stay on the duplicates, so no needs-check sheet moves onto L-0057/L-0058.

| Duplicate | Twin | Links moved (new on the twin) |
|---|---|---|
| L-0337 | L-0057 | Wiki Note(s) E2.2 (tag); Wiki Note(s) E6.2 (tag); Wiki Note(s) E6.3 (sheet); Submittal IDs SUB E6.2-01 (sheet) |
| L-0338 | L-0058 | Wiki Note(s) E2.2 (tag); Wiki Note(s) E6.2 (tag); Wiki Note(s) E6.3 (sheet); Submittal IDs SUB E6.2-01 (sheet) |

### 3. Earthwork

L-0448 (cut) and L-0449 (fill) stay. Quantity Confidence reads "Reference only (C0.2: not for bidding or take-off)"; their MTO lines (MTO-0113, MTO-0114) count in neither total. The fill read (Bluebeam 1598 CY against the Wiki note's 1,596 CY) is still for a person to check on the page image.

### 4. E6.3 conduit and feeder runs

Every run on the E6.3 power and control/signal schedules is its own row: 80 new rows, L-0450 to L-0529. P-SEC (L-0237) and P-TPS (L-0243) already had rows and are not added again. C-2W and P-2W, held in rev1, come in with the group. The roll-up row L-0353 stays and carries no MTO line.

- **Read:** the Tesseract words of `derived/ocr/pages/076_E6.3.json`, checked line by line against the Bluebeam words at the same height. Columns are cut at the whitespace gaps between the header words. A line with no ID continues the run above it; a line whose ID cell holds only a dash is an unnamed circuit.
- **Counts:** 38 named control/signal runs plus a DC spare, and 40 named power runs plus 2 unnamed UV controller circuits plus an AC spare. These are the counts Wiki note E6.3 gives (tie-out below).
- **Row:** the Tag as printed on E6.3, or PROPOSED- for the unnamed circuits and spares. The Name holds voltage, conduit, conductors, GND, from and to, as read. E6.3 shows no lengths. CWP 26 (rule 1, Spec 26 05 19). Spec Sections, Bid Item 6 and Status New follow the roll-up row L-0353 (Inferred); a run that reads (FUTURE) is Status Not stated. Drawing Sheets are E6.3 plus every sheet where the tag (or its plan spelling) is read in the native text layer. The Schedule Activity is L-0353's, via the roll-up.
- **Confidence:** Inferred, except Unresolved where the two OCR reads disagree, or where Wiki note E6.3 records a disagreement with another sheet (P-IP1 to P-IP4, P-2W, P-LT).
- **MTO:** one EA per run whose tag is read on a cited sheet (rev1 rule 4). The best read is the text layer, so these lines are Verified. PROPOSED rows get none.

| Ledger ID | Tag | Confidence | Drawing Sheets | Quantity | From → to (as read) |
|---|---|---|---|---|---|
| L-0450 | C-ATS | Inferred | E6.3 (control and signal schedule); E1.1 | 1 EA | GENERATOR CONTROL PANEL → ATS CONTROL AND STATUS SIGNALS |
| L-0451 | C-GEN | Inferred | E6.3 (control and signal schedule); E1.1 | 1 EA | GENERATOR CONTROL PANEL → PLC CONTROL PANEL |
| L-0452 | C-2W | Inferred | E6.3 (control and signal schedule); E4.3 | 1 EA | 2W PUMP STATION JBOX → PLC CONTROL PANEL |
| L-0453 | C-TCP3 | Inferred | E6.3 (control and signal schedule); E3.1 | 1 EA | TRAIN NO.3 CONTROL PANEL → PLC CONTROL PANEL |
| L-0454 | C-DO1 | Inferred | E6.3 (control and signal schedule); E3.1 | 1 EA | PLC CONTROL PANEL → DO TRANSMITTER NO.1 POWER |
| L-0455 | C-DO2 | Inferred | E6.3 (control and signal schedule); E3.1 | 1 EA | PLC CONTROL PANEL → DO TRANSMITTER NO.2 POWER |
| L-0456 | C-MCP | Inferred | E6.3 (control and signal schedule); E2.1 | 1 EA | PLC CONTROL PANEL → MCC |
| L-0457 | C-INT | Inferred | E6.3 (control and signal schedule); E2.1 | 1 EA | PLC CONTROL PANEL → DOOR INTRUSION SWITCH |
| L-0458 | C-2WPT | Inferred | E6.3 (control and signal schedule); E2.1 | 1 EA | PLC CONTROL PANEL → 2W PRESSURE SENSOR |
| L-0459 | C-SD1 | Inferred | E6.3 (control and signal schedule); E2.1 | 1 EA | PLC CONTROL PANEL → SMOKE/HEAT DETECTOR |
| L-0460 | C-DB | Inferred | E6.3 (control and signal schedule); E2.1 | 1 EA | PLC CONTROL PANEL → DIGESTER BLOWER ENCLOSURE |
| L-0461 | C-FME | Inferred | E6.3 (control and signal schedule); E5.1 | 1 EA | EFFLUENT FLOW METER PANEL → PLC CONTROL PANEL |
| L-0462 | C-UV | Inferred | E6.3 (control and signal schedule); E5.1 | 1 EA | PLC CONTROL PANEL → UV CONTROLLERS |
| L-0463 | C-BL1 | Inferred | E6.3 (control and signal schedule); E2.1 | 1 EA | PLC CONTROL PANEL → BLOWER ENCLOSURE #1 |
| L-0464 | C-BL2 | Inferred | E6.3 (control and signal schedule); E2.1 | 1 EA | PLC CONTROL PANEL → BLOWER ENCLOSURE #2 |
| L-0465 | C-BL3 | Inferred | E6.3 (control and signal schedule); E2.1 | 1 EA | PLC CONTROL PANEL → BLOWER ENCLOSURE #3 |
| L-0466 | C-BL4 | Inferred | E6.3 (control and signal schedule); E2.1 | 1 EA | PLC CONTROL PANEL → BLOWER ENCLOSURE #4 |
| L-0467 | S-LAB | Inferred | E6.3 (control and signal schedule); E0.3; E4.1; E7.0 | 1 EA | LAB SCADA COMPUTER AREA → INFLUENT CONTROL PANEL |
| L-0468 | S-LT-D | Inferred | E6.3 (control and signal schedule); E5.1 | 1 EA | LEVEL TRANSDUCER JBOX → PLC CONTROL PANEL |
| L-0469 | S-ICP | Inferred | E6.3 (control and signal schedule); E2.1; E4.1; E7.0 | 1 EA | PLC CONTROL PANEL → INFLUENT CONTROL PANEL |
| L-0470 | S-MCP | Inferred | E6.3 (control and signal schedule); E2.1 | 1 EA | PLC CONTROL PANEL → MCC |
| L-0471 | S-FLT1 | Inferred | E6.3 (control and signal schedule); E4.1 | 1 EA | INFLUENT WET WELL HANDHOLE → INFLUENT CONTROL PANEL |
| L-0472 | S-FLT2 | Inferred | E6.3 (control and signal schedule); E4.1 | 1 EA | INFLUENT WET WELL HANDHOLE → INFLUENT CONTROL PANEL |
| L-0473 | S-FLT3 | Inferred | E6.3 (control and signal schedule); E4.1 | 1 EA | INFLUENT WET WELL HANDHOLE → INFLUENT CONTROL PANEL |
| L-0474 | S-FLT4 | Inferred | E6.3 (control and signal schedule); E4.1 | 1 EA | INFLUENT WET WELL HANDHOLE → INFLUENT CONTROL PANEL |
| L-0475 | S-LT-IP | Inferred | E6.3 (control and signal schedule); E4.1 | 1 EA | INFLUENT WET WELL HANDHOLE → INFLUENT CONTROL PANEL |
| L-0476 | S-DW1 | Inferred | E6.3 (control and signal schedule); E4.1; E7.0 | 1 EA | INFLUENT CONTROL PANEL → DEWATERING SKID |
| L-0477 | S-FME | Inferred | E6.3 (control and signal schedule); E5.1 | 1 EA | EFFLUENT FLOW TUBE → FLOW TRANSMITTER |
| L-0478 | S-FMIN | Unresolved | E6.3 (control and signal schedule); E4.1 | 1 EA | INFLUENT FLOW TUBE → FLOW TRANSMITTER |
| L-0479 | S-FMPD | Inferred | E6.3 (control and signal schedule); E4.1 | 1 EA | PLANT DRAIN FLOW TUBE → FLOW TRANSMITTER |
| L-0480 | S-FMP2 | Inferred | E6.3 (control and signal schedule); E4.1 | 1 EA | PLANT 2 FLOW TUBE → FLOW TRANSMITTER |
| L-0481 | S-FMP3 | Inferred | E6.3 (control and signal schedule); E4.1 | 1 EA | PLANT 3 FLOW TUBE → FLOW TRANSMITTER |
| L-0482 | S-FMDW | Inferred | E6.3 (control and signal schedule); E4.1 | 1 EA | FLOW TRANSMITTER → INFLUENT PUMP STATION |
| L-0483 | S-FM2W | Inferred | E6.3 (control and signal schedule); E4.3 | 1 EA | FLOW TRANSMITTER → MAIN PLC PANEL |
| L-0484 | S-FP1 | Inferred | E6.3 (control and signal schedule); E4.1 | 1 EA | INFLUENT SAMPLER → INFLUENT CONTROL PANEL |
| L-0485 | S-FP2 | Inferred | E6.3 (control and signal schedule); E4.1 | 1 EA | POLYMER FEED PUMP → INFLUENT CONTROL PANEL |
| L-0486 | S-FP3 | Inferred | E6.3 (control and signal schedule); E2.1; E4.1 | 1 EA | EFFLUENT SAMPLER → MAIN PLC CONTROL PANEL |
| L-0487 | S-FP4 | Inferred | E6.3 (control and signal schedule); E2.1; E4.1 | 1 EA | HYPOCHLORITE FEED PUMP → MAIN PLC CONTROL PANEL |
| L-0488 | PROPOSED-Spare-Conduit-DC | Inferred | E6.3 (control and signal schedule) | None found | AS INDICATED → AS INDICATED |
| L-0489 | P-ATS | Inferred | E6.3 (power schedule); E1.1; E6.1 | 1 EA | CT ENCLOSURE → AUTOMATIC TRANSFER SWITCH |
| L-0490 | P-MDP | Inferred | E6.3 (power schedule); E1.1; E6.1 | 1 EA | AUTOMATIC TRANSFER SWITCH → MAIN 480V DISTRIBUTION PANEL |
| L-0491 | P-MCC | Inferred | E6.3 (power schedule); E1.1; E6.1 | 1 EA | MAIN 480V DISTRIBUTION PANEL → MOTOR CONTROL CENTER |
| L-0492 | P-GEN | Inferred | E6.3 (power schedule); E1.1; E6.1 | 1 EA | 480Y/277V GENERATOR → AUTOMATIC TRANSFER SWITCH |
| L-0493 | P-TSP | Inferred | E6.3 (power schedule); E1.1; E6.1 | 1 EA | MAIN 480V DISTRIBUTION PANEL → TRANSFORMER TS PRIMARY |
| L-0494 | P-2W | Unresolved | E6.3 (power schedule); E4.3 | 1 EA | MCC (SHIELDED 600V MOTOR CABLE) → 2W PUMPS |
| L-0495 | P-ICP | Inferred | E6.3 (power schedule); E2.1; E4.1; E6.1 | 1 EA | MCC → INFLUENT CONTROL PANEL |
| L-0496 | P-TCP1 | Inferred | E6.3 (power schedule); E6.1 | 1 EA | MCC (FUTURE) → TRAIN NO.1 CONTROL PANEL |
| L-0497 | P-TCP2 | Inferred | E6.3 (power schedule); E6.1 | 1 EA | MCC (FUTURE) → TRAIN NO.2 CONTROL PANEL |
| L-0498 | P-TCP3 | Inferred | E6.3 (power schedule); E3.1; E6.1 | 1 EA | MCC → TRAIN NO.3 CONTROL PANEL |
| L-0499 | P-BL-1 | Inferred | E6.3 (power schedule); E2.1; E6.1 | 1 EA | MCC → BLOWER 1 |
| L-0500 | P-BL-2 | Inferred | E6.3 (power schedule); E2.1; E6.1 | 1 EA | MCC → BLOWER 2 |
| L-0501 | P-BL-3 | Inferred | E6.3 (power schedule); E2.1; E6.1 | 1 EA | MCC → BLOWER 3 |
| L-0502 | P-BL-4 | Inferred | E6.3 (power schedule); E2.1; E6.1 | 1 EA | MCC → BLOWER 4 |
| L-0503 | P-DB | Inferred | E6.3 (power schedule); E2.1; E6.1 | 1 EA | MCC → DIGESTER BLOWER |
| L-0504 | P-WP1 | Inferred | E6.3 (power schedule); E2.1; E4.1; E6.1 | 1 EA | MCC → WAS PUMP 1 |
| L-0505 | P-WP2 | Inferred | E6.3 (power schedule); E2.1; E4.1; E6.1 | 1 EA | MCC → WAS PUMP 2/SWING PUMP |
| L-0506 | P-SD-1 | Inferred | E6.3 (power schedule); E2.1; E4.1; E6.1 | 1 EA | MCC → SLUDGE PUMP |
| L-0507 | P-IP1 | Unresolved | E6.3 (power schedule); E4.1; E6.1 | 1 EA | MCC → INFLUENT PUMP 1 |
| L-0508 | P-IP2 | Unresolved | E6.3 (power schedule); E4.1; E6.1 | 1 EA | MCC → INFLUENT PUMP 2 |
| L-0509 | P-IP3 | Unresolved | E6.3 (power schedule); E4.1; E6.1 | 1 EA | MCC → INFLUENT PUMP 3 |
| L-0510 | P-IP4 | Unresolved | E6.3 (power schedule); E4.1; E6.1 | 1 EA | MCC → INFLUENT PUMP 4 |
| L-0511 | P-DW-1 | Inferred | E6.3 (power schedule); E2.1; E4.1; E6.1 | 1 EA | MCC → DEWATERING SKID |
| L-0512 | P-CL3 | Inferred | E6.3 (power schedule); E3.1 | 1 EA | TRAIN NO.3 CONTROL PANEL → CLARIFIER DRIVE NO.3 |
| L-0513 | P-MX3A | Inferred | E6.3 (power schedule); E3.1 | 1 EA | TRAIN NO.3 CONTROL PANEL → CELL 3 SUBMERSIBLE MIXER 1 |
| L-0514 | P-MX3B | Inferred | E6.3 (power schedule); E3.1 | 1 EA | TRAIN NO.3 CONTROL PANEL → CELL 3 SUBMERSIBLE MIXER 2 |
| L-0515 | P-UV1 | Inferred | E6.3 (power schedule); E5.1 | 1 EA | MCC → UV1 PDR'S |
| L-0516 | PROPOSED-UV1-Controller-Circuit | Inferred | E6.3 (power schedule) | None found | MCC → UV1 CONTROLLER |
| L-0517 | P-UV2 | Inferred | E6.3 (power schedule); E5.1 | 1 EA | MCC → UV2 PDR'S |
| L-0518 | PROPOSED-UV2-Controller-Circuit | Inferred | E6.3 (power schedule) | None found | MCC → UV2 CONTROLLER |
| L-0519 | P-LT | Unresolved | E6.3 (power schedule); E5.1 | 1 EA | LIGHTING PANEL → LIGHT POLE/RECEPTACLE |
| L-0520 | P-WSV | Inferred | E6.3 (power schedule); E4.1 | 1 EA | INFLUENT CONTROL PANEL → WAS SOLENOID VALVES |
| L-0521 | P-TSS | Inferred | E6.3 (power schedule); E1.1; E6.1 | 1 EA | TRANSFORMER TS SECONDARY → EXISTING 208Y/120V 400A SHOP PANEL |
| L-0522 | P-AUX | Inferred | E6.3 (power schedule); E1.1 | 1 EA | MCC LIGHTING PANEL → GENERATOR AUX POWER FOR BATTER |
| L-0523 | P-HB1 | Inferred | E6.3 (power schedule); E4.3 | 1 EA | MCC LIGHTING PANEL (GFEP CIRCUIT) → HOT BOX #1 |
| L-0524 | P-HB2 | Inferred | E6.3 (power schedule); E4.3 | 1 EA | MCC LIGHTING PANEL (GFEP CIRCUIT) → HOT BOX #2 |
| L-0525 | P-2WSV | Inferred | E6.3 (power schedule); E4.3 | 1 EA | MCC CONTROL PANEL → HOT BOX #1 SOLENOID |
| L-0526 | P-TS3A | Inferred | E6.3 (power schedule); E3.1 | 1 EA | TRAIN NO.3 CONTROL PANEL → FIELD DEVICES |
| L-0527 | P-TS3B | Inferred | E6.3 (power schedule); E3.1 | 1 EA | TRAIN NO.3 CONTROL PANEL → POLE LIGHT AND RECEPTACLE |
| L-0528 | P-MCP | Inferred | E6.3 (power schedule); E2.1 | 1 EA | MCC LIGHTING PANEL → MAIN CONTROL PANEL POWER |
| L-0529 | PROPOSED-Spare-Conduit-AC | Inferred | E6.3 (power schedule) | None found | AS INDICATED → AS INDICATED |

Read checks where the Tesseract and Bluebeam text differs (spacing aside):

- L-0456 C-MCP: TO Tesseract 'MCC', Bluebeam 'IMCC' — taken as the same text (Bluebeam carries extra or split words)
- L-0464 C-BL2: FROM Tesseract 'PLC CONTROL PANEL', Bluebeam 'PLC PLC CONTROL CONTROL PANEL PAN EL' — taken as the same text (Bluebeam carries extra or split words)
- L-0476 S-DW1: FROM Tesseract 'INFLUENT CONTROL PANEL', Bluebeam 'INFLUENT EFFLUENT CONTROL FLOW PANEL TUBE' — taken as the same text (Bluebeam carries extra or split words)
- L-0478 S-FMIN: CONDUIT Tesseract '1"', Bluebeam 'T' — Unresolved; a person checks
- L-0492 P-GEN: SIZE Tesseract '#250 kemil', Bluebeam '#250 kcmil' — Wiki note E6.3 prints the Bluebeam read
- L-0505 P-WP2: TO Tesseract 'WAS PUMP 2/SWING PUMP', Bluebeam 'WAS SLUDGE PUMP 2/SWING PUMP PUMP' — taken as the same text (Bluebeam carries extra or split words)
- L-0522 P-AUX: TO Tesseract 'GENERATOR AUX POWER FOR BATTER', Bluebeam 'GENERATOR AUX POWER FOR BATTERY' — taken as the same text (Bluebeam carries extra or split words)

### 5. Two totals

Verified-only stays the headline (Quantity). "Total incl. reads to verify" adds the lines held back only because their read is Inferred or Unresolved. It sits beside the headline on the Ledger tab and the Totals tab, and at the end of Quantity Confidence in the CSV. A line held back for any other reason stays out of both totals: an ambiguous tie, a double count, a duplicate or reference-only row, or a row measured in LF. A duplicate pair named by an open item counts once in each total.

### 6. Current Ledger

The 02_Project_Ledger README and the project README name Project_Ledger_rev2 as current, with rev0 and rev1 as history. The graph is rebuilt from rev2 and MTO_Lines_rev2.csv.

## Fill rate per band, rev0 → rev1 → rev2

Filled = the cell carries a fact. "None found", "Not linked", "Not stated", blanks, dashes, zero counts and an all-zero link basis count as not filled. rev0 counts its own values for the columns it had; columns new in rev1 start at 0.

| Band | Columns | rev0 (447 rows) | rev1 (449 rows) | rev2 (529 rows) | rev2, 447 base rows |
|---|---|---|---|---|---|
| A Identity | 7 | 83.8% | 98.1% | 96.2% | 98.1% |
| B Where | 5 | 36.4% | 83.7% | 86.2% | 83.7% |
| C How much | 4 | 0.0% | 21.9% | 32.9% | 21.6% |
| D Specs & notes | 2 | 87.6% | 87.4% | 89.1% | 87.4% |
| E Submittals | 4 | 21.1% | 87.5% | 85.6% | 87.6% |
| F Inspections & tests | 4 | 21.1% | 83.0% | 81.8% | 83.4% |
| G Changes & issues | 5 | 4.0% | 57.7% | 53.5% | 57.6% |
| H Schedule & status | 5 | 0.0% | 99.2% | 96.3% | 99.6% |
| I Confidence & source | 3 | 99.7% | 99.7% | 99.7% | 99.7% |
| **All** | 39 | 36.7% | 80.3% | 80.3% | 80.4% |

## Rows added

rev2 has 529 rows: the 449 rev1 rows in rev1 order (447 rev0 rows, then L-0448 and L-0449) and 80 E6.3 run rows (L-0450 to L-0529).

| Group | Rows |
|---|---|
| E6.3 control and signal run | 38 |
| E6.3 control and signal spare | 1 |
| E6.3 power run | 38 |
| E6.3 power spare | 1 |
| E6.3 power unnamed circuit | 2 |

## Totals

| Unit | Verified-only lines | Verified-only total | Lines incl. reads to verify | Total incl. reads to verify | Added by reads to verify | Ledger rows (Verified / incl.) |
|---|---|---|---|---|---|---|
| EA | 148 | **150** | 166 | 168 | 18 | 148 / 165 |
| LF | 0 | **0** | 18 | 949 | 949 | 0 / 15 |

By group:

| Unit | Group | Verified-only lines | Verified-only total | Lines incl. reads | Total incl. reads |
|---|---|---|---|---|---|
| EA | E6.3 conduit and feeder runs | 78 | 78 | 78 | 78 |
| EA | Other components | 70 | 72 | 88 | 90 |
| LF | Other components | 0 | 0 | 18 | 949 |

By row Status (the totals mix new, existing and demolished items):

| Unit | Row Status | Verified-only lines | Verified-only total | Lines incl. reads | Total incl. reads |
|---|---|---|---|---|---|
| EA | Demolished | 1 | 1 | 2 | 2 |
| EA | Existing | 1 | 1 | 1 | 1 |
| EA | New | 132 | 134 | 148 | 150 |
| EA | Not stated | 14 | 14 | 15 | 15 |
| LF | Demolished | 0 | 0 | 10 | 644 |
| LF | New | 0 | 0 | 8 | 305 |

Lines in neither total: 6 of 190. Reasons (a line may have more than one):

- the row has callout lines in LF; the tag count would count the same item twice: 3
- Reference only: 2
- Unresolved line; totals use Verified lines only: 2
- Wiki note C0.2: 2
- Inferred line; totals use Verified lines only: 1
- Wiki note C0.2 reads fill 1,596 CY: 1
- tie ambiguous: 1

Open duplicate items that name three or more rows, where two or more of those rows have a counted line. They are counted on each row; a person confirms they are separate components:

- OI-0125: L-0256 BL-1, L-0257 BL-2, L-0258 BL-3, L-0259 BL-4 — Same item on more than one row (not combined): Biological treatment blowers (4): Count (4) and motor size (20 HP) agree.
- OI-0127: L-0272 EF-1, L-0273 EF-2 — Same item on more than one row (not combined): Blower Building exhaust fans (2): Count (2) and 1/2 HP agree.
- OI-0133: L-0322 EF-3, L-0323 EF-4, L-0324 EF-5 — Same item on more than one row (not combined): Existing dewatering / treatment building wall fans (3): Count (3) agrees.
- OI-0142: L-0140 DO #1 | DO-1, L-0141 DO #2 | DO-2 — Same item on more than one row (not combined): Train 3 dissolved oxygen and pH sensors: Contract & General carries separate DO and pH rows (package, Equipment A
- OI-0143: L-0287 IP-1, L-0288 IP-2, L-0289 IP-3, L-0290 IP-4 — Same item on more than one row (not combined): Influent pumps (4): Agree: 2 small (120–220 gpm, 3 HP) + 2 large (320–500 gpm, 5 HP).
- OI-0147: L-0291 F1 (Influent Pump Station), L-0292 F2 (Influent Pump Station), L-0293 F3 (Influent Pump Station), L-0294 F4 (Influent Pump Station) — Same item on more than one row (not combined): Influent Pump Station floats F1–F4: One Process & Mechanical roll-up row vs four Electrical & Controls rows.
- OI-0152: L-0330 2W-P1, L-0331 2W-P2 — Same item on more than one row (not combined): 2W pumps (2): Count agrees (1 duty, 1 standby; 5 HP).
- OI-0153: L-0332 LSH-111, L-0333 F2 (2W Pump Station), L-0334 F3 (2W Pump Station), L-0335 LSL-111 — Same item on more than one row (not combined): 2W floats F1–F4: One Process & Mechanical roll-up row vs four Electrical & Controls rows; E&C prints LSH-111 (F1)
- OI-0161: L-0341 UV1, L-0342 UV2 — Same item on more than one row (not combined): UV disinfection units (2): Two channels/units agree.
- OI-0005 (Hot Box #1/#2 and their twins) is settled by decision 2.

## Candidates

485 candidates (Candidates tab, one row each with the test result and reason).

| Source | Decision | Candidates |
|---|---|---|
| E6.3 run group (owner's decision 4, Prompt 11) | Added | 80 |
| E6.3 run group (owner's decision 4, Prompt 11) | Already a row | 2 |
| Prompt 9 proposed row (owner's decision) | Added | 2 |
| Prompt 9 unmatched tag | Added with the E6.3 run group | 2 |
| Prompt 9 unmatched tag | Not added | 399 |

## MTO

- 190 lines: 22 callout, 168 tag count. 148 count Verified-only; 184 count incl. reads to verify.
- Callouts: 177 leads, 4 on base pages Add. 4 supersedes, 119 callouts, 22 lines, 97 held (the rev1 rules, unchanged).
- MTO-0001 to MTO-0114 keep their rev1 numbers; the run lines follow.

## Rules and judgment calls

- **Proposals.** Each is checked against the rev0 value it names before it is applied; the three L-0057 sheet adds stack. Each changed row's Notes and Source Citation name the proposal and its evidence.
- **TS, T3, T2.** Verified as the owner decided. Their Notes still record the Inferred facts the proposals flagged (Status New), which the owner accepted with the change.
- **Duplicates.** "Links" are the link columns (Found On, MTO Line IDs, Wiki Note(s), Submittal IDs, Inspection/Test IDs, RFI IDs, Conflict/Gap IDs, Exception Refs). A link already on the twin keeps the stronger basis. Drawing Sheets and the schedule columns stay on the duplicate.
- **Runs.** Values are machine reads, so the rows are Inferred. Where the Tesseract and Bluebeam reads of a cell differ and Wiki note E6.3 prints exactly one of them (four characters or more), that one is used; otherwise both are shown and the row is Unresolved. A plan spelling (P-BL1 for P-BL-1) counts as the same tag; Wiki note E6.3 calls these cosmetic.
- **Incl. total for duplicate pairs.** When an open item names exactly two rows and both have a line in the incl. total, the line of the row without a Verified count drops out, so the pair counts once.
- **Links** are repo links on `main`, as in rev1.

## Tie-outs

| Check | Result | Detail |
|---|---|---|
| index/Ledger_Schema_rev1.csv = the CSV columns | pass | 39 schema columns, 39 built |
| Ledger_ID_Map.csv = Project_Ledger.csv | pass | 447 IDs, 447 Ledger rows |
| Every base row has its by-CWP assignment | pass | 447 of 447 rows matched on Tag, Name, Lane and Area/Building |
| The 14 Verified proposals: each found and applied, Current Value as in rev0 | pass | 14 Verified proposals, 14 applied, stale none; 229 needs-check proposals left as they are |
| E6.3 control and signal schedule matches Wiki note E6.3 | pass | read 38 named, 0 unnamed, 1 spare; the note says (38, 0, 1) |
| E6.3 power schedule matches Wiki note E6.3 | pass | read 40 named, 2 unnamed, 1 spare; the note says (40, 2, 1) |
| All 449 rev1 rows present, in rev1 order, with rev1 Tag and Name (Tags changed only by P-0234/P-0235) | pass | 449 rev1 rows, 529 rev2 rows; differ: none |
| Rows no decision touches are identical to rev1 (Quantity Confidence only gains the incl. total) | pass | 435 rows compared, 14 touched by a decision; differ: none |
| Ledger IDs unique and in the L-NNNN form | pass | 529 IDs |
| Every new row passes the three-part test | pass | 82 new rows (2 from rev1, 80 E6.3 runs); each has a sheet, set page and box, a CWP by rules 1-5 and a connected document |
| No new row is an I/O point, area, standard or drawing reference | pass | 80 run rows checked against the never-add categories; hits: none |
| Every E6.3 run is a Ledger row exactly once | pass | 82 schedule runs; 80 new rows, 2 already rows; 2 stray OCR lines skipped |
| No blank cell | pass | 0 blank cells |
| No blank link cell (CSV and Ledger tab) | pass | 13 link and total columns, 529 rows; 0 blank |
| Every link carries its basis (tag, spec or sheet) | pass | 0 links without a basis |
| Direct links first in every link cell | pass | 0 cells out of order |
| Counts = linked IDs | pass | 0 rows differ |
| Duplicate rows keep no links; their twins carry every moved link | pass | L-0337 -> L-0057: 4 links added; L-0338 -> L-0058: 4 links added |
| Verified-only totals tie to their lines (each row, and each unit overall) | pass | EA: 150 from 148 lines = 150 on 148 rows; LF: 0 from 0 lines = 0 on 0 rows |
| Totals incl. reads to verify tie to their lines (each row, and each unit overall) | pass | EA: 168 from 166 lines = 168 on 165 rows; LF: 949 from 18 lines = 949 on 15 rows |
| Every line that counts is also in the incl. total; incl. >= Verified-only per unit | pass | 148 lines count, 184 in the incl. total |
| Verified-only totals use Verified lines only | pass | 148 lines count |
| Incl. totals add only lines held back for their read level | pass | 36 lines added by reads to verify |
| Duplicate and earthwork rows count in no total | pass | 2 lines on those rows, 0 counted |
| No MTO line is a dimension, elevation, slope or size | pass | units ['CY', 'EA', 'LF'] |
| MTO callouts = lines + held | pass | 119 callouts, 22 lines, 97 held |
| Every unmatched tag is a candidate | pass | 401 unmatched tags |

Links written: 9612 (Links tab).

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
| testbeds/eastsound/derived/ocr/pages/076_E6.3.json | 4c48853fbea5abd9e442a25fb181fc5c2e2719ecb2c2bc798e401df4de3b161f |
| testbeds/eastsound/derived/reconciliation/Ledger_ID_Map.csv | 1e6f2d57dab919b981bd89b55ed7706d8305aa449ad911dae54f36661607c697 |
| testbeds/eastsound/derived/reconciliation/Ledger_Update_Proposal.csv | d456e1e57da5dc21c6f65879dd4636b23a81a02655552abb9b75dcc9d7a28fba |
| testbeds/eastsound/derived/reconciliation/New_Row_Candidates.csv | f8c5496e8620fd0ea459e87e31fa308292c4cfb0e1173f9867e2a41d121ec1e4 |
| testbeds/eastsound/derived/wiki/Wiki_Links.csv | 5601d7ba85517daa369c76cb53e5cd7cf497925dc701b9fa5e3f4fbd5de8a347 |
| testbeds/eastsound/derived/wiki/Wiki_Notes.csv | ba6e3559428c5a4276c84deb34f2a4b491c39b8a6393f17d0508003d06ef55f8 |
| testbeds/eastsound/index/Ledger_Schema_rev1.csv | 20ba26e8ffa1620fd89f483574ec645a64f8d4db6acf5ae5e3204a5aefc24519 |
| testbeds/eastsound/project/01_Project_Wiki/Project_Wiki.md | a3027eed7aadeee5aa7a40b6dc44de9e0a9756d8844d74fca6aa8e94a75210a2 |
| testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv | 0ed3af5640881f6fe2551b982d44653ddd92629cbcb5d47d68280a3ae6683e31 |
| testbeds/eastsound/project/02_Project_Ledger/Project_Ledger_by_CWP.csv | 7b34026476991d747d5edaaceafa2ab15ceee9fb5b8bda525bbbe7a8e9f8dcbf |
| testbeds/eastsound/project/02_Project_Ledger/Project_Ledger_rev1.csv | a78336a2e4c18ad3820071f05381c3678e50120c699c13523d9fc63690b3849a |
| testbeds/eastsound/project/03_Exceptions_and_Issues/Exception_Report.md | 9729ecc9c60a23c448226f1fae7fce18619cfe433408a0c3ad2d80e33b21c4dc |
| testbeds/eastsound/project/04_Submittals_ITP_QC/Inspection_Test_Plan.csv | 205cffe80849bf19601bd256f284c8ff592265227b856e3c435bbc83f9ef8414 |
| testbeds/eastsound/project/04_Submittals_ITP_QC/Submittal_Register.csv | 9980d8425dcf87708ad78afc4868434c2311a27a1e769f629d0cafde9600de64 |
| testbeds/eastsound/project/05_Schedule_and_Tracker/Installation_Tracker_by_CWP.csv | 3d5bd28446ba2451573fdb547e27ecad12ed63ad012746449089d1beddef6fff |
| testbeds/eastsound/project/05_Schedule_and_Tracker/Schedule_by_CWP.csv | eba6fb7c55b281c5749cbcf6f10e2a75b69e65c87db2cc5bc2935029caef13fa |
| testbeds/eastsound/tools/build_ledger_rev1.py | 369b79a6eefb24111bcb57d499cfac1c621d84d5fb2dd5918677b2dd5d05628f |
| testbeds/eastsound/tools/build_reconciliation.py | 06b50b60658c89520244491e6cea6a2e5e7cea952a508dcbcb520e2eb18845eb |
| testbeds/eastsound/tools/extract_drawing_text.py | 0e61e19737aa0acd351b04bb1fe1276502ad57f626b99e59df261b62d1bbebd1 |
| testbeds/eastsound/derived/ocr/pages/ (103 files; SHA-256 of their SHA-256 values in name order) | 4fe9245a0358fa2dae5ee9062da74649db03c5e0b45dee9fc8585bc45cdec6d2 |
