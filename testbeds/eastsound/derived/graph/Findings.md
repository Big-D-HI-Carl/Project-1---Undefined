# Findings — Ledger gaps hit by the graph build

Built 2026-10-02 by `build/build_graph.py`. Every gap is logged here; the Ledger and the index files are not changed. Tags: Unresolved = a gap or conflict, with the need stated; Inferred = a possible match a person should confirm; Verified = read as written in the named file.

## Summary

| Finding | Count |
|---|---|
| Addenda values not matched to one 03 item | 1 |
| Area/Building names that may be the same place (not merged) | 16 |
| Area/Building not stated | 24 |
| Bid Item not stated | 3 |
| Bid Item text with no item number | 3 |
| Component labels made unique with the Ledger row | 5 |
| Drawing Sheets blank (no sheet cited) | 74 |
| Drawing Sheets values that are not a sheet number | 6 |
| Duplicate Tags (two Ledger rows, one Tag) | 4 |
| Paragraph citations with no section number beside them | 18 |
| Paragraph numbers in an unusual form | 6 |
| Sheets with no components (no Ledger row cites them) | 11 |
| Spec Sections blank | 111 |
| Spec Sections values that don't match 02 | 1 |
| Wiki Note(s) values with no Wiki note | 12 |
| Wiki note and 01 rev2 disagree on whether a sheet is in the library | 6 |
| Wiki notes with no sheet or spec node | 28 |

## Addenda values not matched to one 03 item (1)

Add. 4 p.3 lists five drawing items; the value names none and the row's sheets don't settle it, so no edge was made.

| Ledger row | Node ID | Value | Tag level |
|---|---|---|---|
| 360 | L-0359 PROPOSED-Blower-Building-Slab-and-Grade-Beams | Add. 4 p.3 | Unresolved |

## Area/Building names that may be the same place (not merged) (16)

Kept as separate areas; merging them is a person's call.

| Names | Ledger rows | Tag level |
|---|---|---|
| Electric Service Area / Electric Service Area / existing buildings | Electric Service Area: 16; Electric Service Area / existing buildings: 1 | Inferred |
| Existing building / Existing Dewatering/Train 1&2 Building Area | Existing building: 9; Existing Dewatering/Train 1&2 Building Area: 2 | Inferred |
| Existing building / Existing Metal Building adjacent to Train #2 | Existing building: 9; Existing Metal Building adjacent to Train #2: 1 | Inferred |
| Existing building / Existing Office Building | Existing building: 9; Existing Office Building: 4 | Inferred |
| Existing building / Existing Treatment Building | Existing building: 9; Existing Treatment Building: 1 | Inferred |
| Existing building / Existing WWTP Building | Existing building: 9; Existing WWTP Building: 2 | Inferred |
| Flow Splitter / Influent Flow Splitter | Flow Splitter: 2; Influent Flow Splitter: 14 | Inferred |
| Train 2 / Existing Dewatering/Train 1&2 Building Area | Train 2: 2; Existing Dewatering/Train 1&2 Building Area: 2 | Inferred |
| Train 2 / Existing Metal Building adjacent to Train #2 | Train 2: 2; Existing Metal Building adjacent to Train #2: 1 | Inferred |
| Train 2 / Train #2 Building | Train 2: 2; Train #2 Building: 2 | Inferred |
| Train 2 / Train No.2 | Train 2: 2; Train No.2: 1 | Inferred |
| Train 3 / Train No.3 | Train 3: 29; Train No.3: 8 | Inferred |
| Train #2 Building / Existing Dewatering/Train 1&2 Building Area | Train #2 Building: 2; Existing Dewatering/Train 1&2 Building Area: 2 | Inferred |
| Train #2 Building / Existing Metal Building adjacent to Train #2 | Train #2 Building: 2; Existing Metal Building adjacent to Train #2: 1 | Inferred |
| Treatment Building / Existing Treatment Building | Treatment Building: 18; Existing Treatment Building: 1 | Inferred |
| UV Disinfection Chamber / UV Disinfection Chamber & Digester | UV Disinfection Chamber: 9; UV Disinfection Chamber & Digester: 22 | Inferred |

## Area/Building not stated (24)

| Ledger row | Node ID | Value | Tag level |
|---|---|---|---|
| 91 | L-0090 PROPOSED-Floor drains | Not stated (in Train 2 and Train 3 flow meter vaults per C7.10) | Unresolved |
| 101 | L-0100 PROPOSED-Composite manholes, double manhole condition | Not stated | Unresolved |
| 139 | L-0138 PROPOSED-2W-FLOW-METER | Not stated (2W system) | Unresolved |
| 160 | L-0159 PROPOSED-CARBON-FEED-PUMPS | Not stated (feeds Train 3 Anoxic 2 per G0.5) | Unresolved |
| 228 | L-0227 PROPOSED-EYE-WASH-STATIONS | Not stated | Unresolved |
| 233 | L-0232 PROPOSED-UV-TRANSMISSIVITY-ANALYZER | Not stated | Unresolved |
| 261 | L-0260 DB | Not stated — drawn on E2.1 outside the Blower Building outline, beside a "building interior wall" | Unresolved |
| 262 | L-0261 PROPOSED-DB-Local-Disconnect | Not stated — at DB (see DB row) | Unresolved |
| 320 | L-0319 PROPOSED-Hypochlorite-Feed-Pump | Not stated (drawn on E4.1) | Unresolved |
| 322 | L-0321 PROPOSED-Effluent-Sampler | Not stated (drawn on E4.1) | Unresolved |
| 358 | L-0357 PROPOSED-Construction-Power-Service | Not stated | Unresolved |
| 391 | L-0390 PROPOSED-Existing-Slab-Trench-Infill | Not stated (existing building per C1.6A) | Unresolved |
| 399 | L-0398 PROPOSED-Steel-Stairs-Ladders-Platforms | Not stated (locations per civil drawings) | Unresolved |
| 408 | L-0407 PROPOSED-8in-Effluent-Flow-Meter | Not stated | Unresolved |
| 419 | L-0418 PROPOSED-Influent-Sampler | Not stated | Unresolved |
| 422 | L-0421 PROPOSED-Temporary-Back-Up-Generator | Not stated | Unresolved |
| 423 | L-0422 PROPOSED-Automatic-Transfer-Switch | Not stated | Unresolved |
| 424 | L-0423 PROPOSED-Permanent-Standby-Generator | Not stated | Unresolved |
| 425 | L-0424 PROPOSED-480V-Electrical-Service | Not stated | Unresolved |
| 427 | L-0426 PROPOSED-PLC-Control-Panel | Not stated | Unresolved |
| 432 | L-0431 PROPOSED-Temporary-Pump-and-Process-Equipment | Not stated | Unresolved |
| 440 | L-0439 PROPOSED-Temporary-Bypass-Alarm-Monitoring | Not stated | Unresolved |
| 447 | L-0446 PROPOSED-Magnetic-Flow-Meters | Not stated | Unresolved |
| 448 | L-0447 PROPOSED-Handrails | Not stated | Unresolved |

## Bid Item not stated (3)

| Ledger row | Node ID | Value | Tag level |
|---|---|---|---|
| 408 | L-0407 PROPOSED-8in-Effluent-Flow-Meter | Not stated | Unresolved |
| 419 | L-0418 PROPOSED-Influent-Sampler | Not stated | Unresolved |
| 447 | L-0446 PROPOSED-Magnetic-Flow-Meters | Not stated | Unresolved |

## Bid Item text with no item number (3)

Kept in the component's Bid Item field; no edge.

| Ledger row | Node ID | Value | Tag level |
|---|---|---|---|
| 321 | L-0320 PROPOSED-Influent-Sampler | sampler Owner-furnished | Inferred |
| 322 | L-0321 PROPOSED-Effluent-Sampler | sampler Owner-furnished | Inferred |
| 359 | L-0358 PROPOSED-Electrical-Equipment-Housekeeping-Pads | concrete per civil specifications | Inferred |

## Component labels made unique with the Ledger row (5)

| Ledger row | Label | Tag level |
|---|---|---|
| 392 | Precast wet well, 8 ft ID · no sheet (no tag) | Verified |
| 393 | Precast wet well, 8 ft ID · no sheet (no tag) | Verified |
| 395 | Precast vault, 4 ft x 4 ft · no sheet (no tag) | Verified |
| 396 | Precast vault, 4 ft x 4 ft · no sheet (no tag) | Verified |
| 397 | Precast vault, 4 ft x 4 ft · no sheet (no tag) | Verified |

## Drawing Sheets blank (no sheet cited) (74)

No shown-on edge; the component's Status carries 'no sheet cited'.

| Ledger row | Node ID | Name | Tag level |
|---|---|---|---|
| 161 | L-0160 PROPOSED-TRAIN-3-CONTROL-PANEL | Treatment system control panel, NEMA 4X 316 SS, 460 V 3-phase input, UL listed | Unresolved |
| 215 | L-0214 PROPOSED-IPS-MOTOR-SAVER-RELAYS | Flygt MiniCAS-120 motor saver relays for the influent pumps, supplied by Contractor to the Control Systems Integrator | Unresolved |
| 216 | L-0215 PROPOSED-SLUDGE-PUMP-LOCAL-PANELS | Sludge pump local electrical control panels (3), by pump manufacturer | Unresolved |
| 217 | L-0216 PROPOSED-YARD-HYDRANTS | 1-inch frost-proof yard hydrants with vacuum breakers (quantity not stated) | Unresolved |
| 218 | L-0217 PROPOSED-POST-HYDRANTS | 2-inch post hydrants with 2-inch atmospheric vacuum breakers (quantity not stated) | Unresolved |
| 219 | L-0218 PROPOSED-EXTERIOR-SANITARY-DRAINS | Exterior sanitary drain piping, ABS DWV, with unions and cleanouts | Unresolved |
| 220 | L-0219 PROPOSED-BLOWER-BLDG-WALL-FANS | Blower Building wall fans (2), Acme FQ18G6, 3,300 CFM, 1/2 HP, 120 V, each on its own Schaffer TH109 thermostat, with EBE445 gravity combination louver | Unresolved |
| 221 | L-0220 PROPOSED-BLOWER-BLDG-MOTORIZED-LOUVER | Blower Building motorized louvered vent, 36 x 84 in., Pottoroff EXD-645 with AF120 120 V spring-return actuator | Unresolved |
| 222 | L-0221 PROPOSED-BLOWER-BLDG-MANUAL-LOUVER | Blower Building manual louvered vent, 24 x 24 in., Pottoroff EXD-645 | Unresolved |
| 223 | L-0222 PROPOSED-EXISTING-BLDG-WALL-FANS | Existing Dewatering/Train 1&2 Building wall fans (3), Acme FQ18G6, 3,300 CFM, each on a manual on/off switch, with gravity combination louvers | Unresolved |
| 224 | L-0223 PROPOSED-EXISTING-BLDG-LOUVERS | Existing Dewatering/Train 1&2 Building manual louvered vents (2), 36 x 84 in., Pottoroff EXD-645 | Unresolved |
| 225 | L-0224 Receiving Conveyor | Receiving conveyor, horizontal shaftless, 9-in. flight, 6 ft 9 in., 304 SS U-trough, two inlets from rotary press cake chutes, 1 HP | Unresolved |
| 226 | L-0225 Inclined Conveyor | Inclined conveyor, shafted, 9-in. flight at 5-in. pitch, 17 ft 4 in. at 35 degrees, 304 SS tubular trough, outlet to bin, 5 HP | Unresolved |
| 227 | L-0226 PROPOSED-2W-AIR-GAP-ENCLOSURE | 2W air gap system in a fiberglass enclosure ("2W (Air Gap) Water Hot Box") | Unresolved |
| 228 | L-0227 PROPOSED-EYE-WASH-STATIONS | Wall-mount eye wash stations (quantity and locations not stated) | Unresolved |
| 232 | L-0231 PROPOSED-UV-INTENSITY-SENSORS | UV intensity sensors (2, one per bank), submersible, with low-UV alarm contact | Unresolved |
| 233 | L-0232 PROPOSED-UV-TRANSMISSIVITY-ANALYZER | UV transmissivity analyzer, Hach DR 1900 (1) | Unresolved |
| 235 | L-0234 PROPOSED-RFP-POLYMER-FLOWMETER | Rotary press polymer (dilution) flowmeter, 1-inch electromagnetic (E+H 10P), 5-80 gpm, at the flocculator inlet | Unresolved |
| 236 | L-0235 PROPOSED-RFP-INLET-PRESSURE-TRANSMITTER | Flocculator inlet pressure transmitter, E+H PMC71, 0-30 psi, HART | Unresolved |
| 392 | L-0391 PROPOSED-2W-Pump-Station-Precast-Wet-Well | Precast wet well, 8 ft ID (Oldcastle Infrastructure 96 in diameter), with 48 in x 30 in H-20 aluminum hatch and safety grate (LW Products HD-3C) — 2W Plant Water Pump Station | Unresolved |
| 393 | L-0392 PROPOSED-Influent-Pump-Station-Precast-Wet-Well | Precast wet well, 8 ft ID (Oldcastle Infrastructure 96 in diameter), with 48 in x 30 in H-20 aluminum hatch and safety grate (LW Products HD-3C) — Influent Pump Station | Unresolved |
| 394 | L-0393 PROPOSED-Influent-Pump-Station-Top-Slab | Influent Pump Station top slab per Contract Plan details, with new aluminum access hatch and safety grates | Unresolved |
| 395 | L-0394 PROPOSED-Influent-Flow-Meter-Valve-Vault | Precast vault, 4 ft x 4 ft (Oldcastle Infrastructure 4686-LA), with 36 in x 36 in H-20 single-leaf hatch (Halliday H1R3636) — Influent Flow Meter Valve Vault | Unresolved |
| 396 | L-0395 PROPOSED-Effluent-Flow-Meter-Valve-Vault | Precast vault, 4 ft x 4 ft (Oldcastle Infrastructure 4686-LA), with 36 in x 36 in H-20 single-leaf hatch (Halliday H1R3636) — Effluent Flow Meter Valve Vault | Unresolved |
| 397 | L-0396 PROPOSED-Plants-2-and-3-Flow-Meter-Vault | Precast vault, 4 ft x 4 ft (Oldcastle Infrastructure 4686-LA), with 36 in x 36 in H-20 single-leaf hatch (Halliday H1R3636) — Plants 2 & 3 Flow Meter Vault | Unresolved |
| 398 | L-0397 PROPOSED-Influent-Pump-Station-Meter-Vaults | Precast vaults, 4 ft x 4 ft (Oldcastle Infrastructure 4686-LA), with 36 in x 36 in H-20 single-leaf hatches (Halliday H1R3636) — Influent Pump Station Meter Vaults, quantity not stated | Unresolved |
| 400 | L-0399 PROPOSED-Boot-Brush-and-Pad | Boot and shoe brush with scraper (Gempler's #2900) on a concrete pad next to the Blower Building exterior door | Unresolved |
| 401 | L-0400 PROPOSED-Influent-Pump-Station-Interior-Coating | Epoxy protective lining, spray-applied 100% solids (Raven 405 or Tnemec G436), on all interior concrete surfaces — Influent Pump Station | Unresolved |
| 402 | L-0401 PROPOSED-Bollards | Bollards | Unresolved |
| 403 | L-0402 PROPOSED-Trench-Safety-System | Trench safety system | Unresolved |
| 405 | L-0404 PROPOSED-Temporary-Bypass-Pipe | Temporary bypass pipe (chlorine contact tank outlet to 8-inch plant outlet) | Unresolved |
| 406 | L-0405 PROPOSED-Temporary-8in-Effluent-Piping | Temporary 8-inch effluent piping | Unresolved |
| 407 | L-0406 PROPOSED-8in-Effluent-Piping | 8-inch effluent piping (new) | Unresolved |
| 408 | L-0407 PROPOSED-8in-Effluent-Flow-Meter | 8-inch effluent flow meter | Unresolved |
| 409 | L-0408 PROPOSED-Aerobic-Digester | Aerobic digester | Unresolved |
| 410 | L-0409 PROPOSED-UV-Disinfection-Chamber | UV disinfection chamber (UV channels #1 and #2) | Unresolved |
| 411 | L-0410 PROPOSED-UV-Disinfection-System | UV disinfection system equipment | Unresolved |
| 412 | L-0411 PROPOSED-Sludge-Pumps | Sludge pumps (peristaltic; WAS and digested sludge) | Unresolved |
| 413 | L-0412 PROPOSED-Yard-Piping | Yard piping | Unresolved |
| 414 | L-0413 PROPOSED-Yard-Piping-Vaults | Vaults associated with yard piping | Unresolved |
| 415 | L-0414 PROPOSED-2W-Air-Gap-Water-System | 2W air gap water system | Unresolved |
| 416 | L-0415 PROPOSED-Influent-Pump-Station | Influent pump station | Unresolved |
| 417 | L-0416 PROPOSED-Submersible-Pump-Equipment | Submersible pump equipment | Unresolved |
| 418 | L-0417 PROPOSED-Influent-Flow-Splitter | Influent flow splitter | Unresolved |
| 419 | L-0418 PROPOSED-Influent-Sampler | Influent sampler | Unresolved |
| 420 | L-0419 PROPOSED-Train-3 | Train 3 (third treatment train) | Unresolved |
| 421 | L-0420 PROPOSED-Train-3-Biological-Treatment-Equipment | Train 3 biological treatment system equipment | Unresolved |
| 422 | L-0421 PROPOSED-Temporary-Back-Up-Generator | Temporary back-up generator (rental, 480V) | Unresolved |
| 423 | L-0422 PROPOSED-Automatic-Transfer-Switch | Automatic transfer switch (permanent) | Unresolved |
| 424 | L-0423 PROPOSED-Permanent-Standby-Generator | Permanent 480V standby generator | Unresolved |
| 425 | L-0424 PROPOSED-480V-Electrical-Service | 480V electrical service (new) | Unresolved |
| 426 | L-0425 PROPOSED-Motor-Control-Center | Motor control center (MCC) | Unresolved |
| 427 | L-0426 PROPOSED-PLC-Control-Panel | PLC control panel (new) | Unresolved |
| 428 | L-0427 PROPOSED-Dewatering-System | Sludge dewatering system (rotary fan press) | Unresolved |
| 429 | L-0428 PROPOSED-Site-Final-Surfacing-and-Pavement | Final surfacing and pavement (entire site) | Unresolved |
| 430 | L-0429 PROPOSED-Funding-Recognition-Sign | Funding recognition sign (Ecology financial assistance) | Unresolved |
| 431 | L-0430 PROPOSED-Temporary-Barriers | Temporary barriers at openings and hazards (fencing, railing, barricades, steel plates, with warning signs or lights) | Unresolved |
| 432 | L-0431 PROPOSED-Temporary-Pump-and-Process-Equipment | Temporary pump and process equipment (removed at Final Completion) | Unresolved |
| 433 | L-0432 PROPOSED-Bypass-Pumping-System | Bypass pumping systems (influent and effluent) for WWTP shutdowns | Unresolved |
| 434 | L-0433 PROPOSED-Temporary-Construction-Dewatering | Temporary construction dewatering (excavations) | Unresolved |
| 435 | L-0434 PROPOSED-Temporary-Excavation-Support | Temporary excavation support (shoring, bracing, sheeting, cribbing) | Unresolved |
| 436 | L-0435 PROPOSED-Contractor-Field-Office | Contractor's field office (optional) | Unresolved |
| 437 | L-0436 PROPOSED-Temporary-Construction-Power | Temporary construction power and lighting (poles, transformer if required, cords, outlets, lamps) | Unresolved |
| 438 | L-0437 PROPOSED-Temporary-Construction-Water-Connection | Temporary metered construction water connection with backflow preventer (if agreed) | Unresolved |
| 439 | L-0438 PROPOSED-Temporary-Sanitary-Facilities | Temporary restrooms (contract service allowed) | Unresolved |
| 440 | L-0439 PROPOSED-Temporary-Bypass-Alarm-Monitoring | Temporary bypass alarm and status monitoring (cellular notification; wired to the existing WWTP control system) | Unresolved |
| 441 | L-0440 PROPOSED-Aeration-Basins | Aeration basins (Train 3) | Unresolved |
| 442 | L-0441 PROPOSED-Anoxic-Basins | Anoxic basins (Train 3) | Unresolved |
| 443 | L-0442 PROPOSED-Clarifier | Clarifier (Train 3) | Unresolved |
| 444 | L-0443 PROPOSED-Blowers | Blower equipment (blowers and drives) | Unresolved |
| 445 | L-0444 PROPOSED-Train-3-Dissolved-Oxygen-Sensors | Dissolved oxygen (DO) sensors, Train 3 | Unresolved |
| 446 | L-0445 PROPOSED-Train-3-pH-Sensors | pH sensors, Train 3 | Unresolved |
| 447 | L-0446 PROPOSED-Magnetic-Flow-Meters | Magnetic flow meters (all units; count and locations not stated) | Unresolved |
| 448 | L-0447 PROPOSED-Handrails | Handrails | Unresolved |

## Drawing Sheets values that are not a sheet number (6)

No edge made.

| Ledger row | Node ID | Value | Tag level |
|---|---|---|---|
| 110 | L-0109 PROPOSED-Temporary construction sign | — | Unresolved |
| 112 | L-0111 PROPOSED-Compost berm | — | Unresolved |
| 115 | L-0114 PROPOSED-Temporary cold-mix patches | — | Unresolved |
| 357 | L-0356 PROPOSED-Temporary-Backup-Generator | None (Add. 4 and 26 05 00 only) | Unresolved |
| 358 | L-0357 PROPOSED-Construction-Power-Service | Not shown | Unresolved |
| 404 | L-0403 PROPOSED-Erosion-and-Sediment-Control-Measures | TESC plans (civil sheets, not numbered in source) | Unresolved |

## Duplicate Tags (two Ledger rows, one Tag) (4)

Keyed by Ledger row, so each row is its own node; nothing is merged (Graph_Transfer_Ultraplan §5).

| Tag | Ledger row | Ledger ID | Name | Tag level |
|---|---|---|---|---|
| PROPOSED-Influent-Sampler | 321 | L-0320 | Influent sampler (Owner-furnished, contractor-installed); 120 V GFCI receptacle LP2-8 and 4–20 mA flow pace | Unresolved |
| PROPOSED-Influent-Sampler | 419 | L-0418 | Influent sampler | Unresolved |
| SD-1 | 74 | L-0073 | Storm drain alignment SD-1, 12-inch, 42 + 19 + 42 LF at 0.5% | Unresolved |
| SD-1 | 316 | L-0315 | Sludge pump, 3 HP, VFD in MCC | Unresolved |

## Paragraph citations with no section number beside them (18)

No paragraph node made; the section is not stated in the same citation segment.

| Ledger row | Node ID | Paragraph | Tag level |
|---|---|---|---|
| 151 | L-0150 PROPOSED-TRAIN-3-TREATMENT-SYSTEM | ¶1.03 A | Unresolved |
| 151 | L-0150 PROPOSED-TRAIN-3-TREATMENT-SYSTEM | ¶1.04 | Unresolved |
| 151 | L-0150 PROPOSED-TRAIN-3-TREATMENT-SYSTEM | ¶1.05 A | Unresolved |
| 151 | L-0150 PROPOSED-TRAIN-3-TREATMENT-SYSTEM | ¶3.03 | Unresolved |
| 152 | L-0151 PROPOSED-TRAIN-3-INNER-WALLS | ¶2.01 C.1 | Unresolved |
| 152 | L-0151 PROPOSED-TRAIN-3-INNER-WALLS | ¶2.01 C.4 | Unresolved |
| 155 | L-0154 PROPOSED-TRAIN-3-AERATION-DIFFUSERS | ¶2.01 E.2 | Unresolved |
| 159 | L-0158 PROPOSED-TRAIN-3-MLR-AIRLIFT | ¶2.01 C.7 | Unresolved |
| 161 | L-0160 PROPOSED-TRAIN-3-CONTROL-PANEL | ¶3.03 | Unresolved |
| 238 | L-0237 P-SEC | ¶3.03 F.2 | Unresolved |
| 239 | L-0238 PROPOSED-CT-Enclosure-and-Meter-Base | ¶3.03 F.2 | Unresolved |
| 246 | L-0245 PROPOSED-Existing-Utility-Transformer-208V | ¶3.03 D | Unresolved |
| 268 | L-0267 PROPOSED-Blower-Building-Smoke-Heat-Detector | ¶3.09 M | Unresolved |
| 269 | L-0268 PROPOSED-Blower-Building-Door-Intrusion-Switch | ¶3.09 L | Unresolved |
| 326 | L-0325 PROPOSED-Treatment-Building-Ventilation-Control-Panel | ¶3.09 J | Unresolved |
| 327 | L-0326 PROPOSED-Methane-Sensor | ¶3.09 J.5 | Unresolved |
| 328 | L-0327 PROPOSED-H2S-Sensor | ¶3.09 J.4 | Unresolved |
| 392 | L-0391 PROPOSED-2W-Pump-Station-Precast-Wet-Well | ¶1.06 | Unresolved |

## Paragraph numbers in an unusual form (6)

Written as in the Ledger Source Citation; may be a typo (e.g. 3.025, 1.012). Not corrected.

| Paragraph | Ledger rows | Tag level |
|---|---|---|
| 26 05 00 ¶1.012 | 262, 285, 300, 317, 337 | Unresolved |
| 26 05 00 ¶1.015 A | 358 | Unresolved |
| 26 05 00 ¶1.016 C | 357 | Unresolved |
| 33 05 00 ¶3.025 B | 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72 | Unresolved |
| 45 05 00 ¶2.011 B | 231 | Unresolved |
| 46 76 26 ¶1.0 A | 192, 196, 198, 199, 225, 226 | Unresolved |

## Sheets with no components (no Ledger row cites them) (11)

| Sheet | Title | Tag level |
|---|---|---|
| C1.1 | Site Piping Plan with General Notes (cover-index title) | Verified |
| C1.2 | Site Dimensional Plan (cover-index title) | Verified |
| C1.5 | Site Piping Plan with Pipe Elevations | Verified |
| C7.7 | Civil Details (cover-index title) | Verified |
| C7.8 | Civil Details (cover-index title) | Verified |
| C7.9 | Flow Meter & Valve Vault Details (cover-index title) | Verified |
| E0.1 | Electrical Symbols and Abbreviations | Verified |
| E0.4 | Area Classification Site Plan | Verified |
| G0.1 | Cover Sheet | Verified |
| G0.2 | Legend and Abbreviations – Civil & Architectural | Verified |
| G0.4 | W.A.C. 332-130 Compliance Sheet | Verified |

## Spec Sections blank (111)

| Ledger row | Node ID | Name | Tag level |
|---|---|---|---|
| 2 | L-0001 PROPOSED-Temporary bypass pumping system | Temporary bypass pumping, piping, holding tanks and storage | Unresolved |
| 3 | L-0002 PROPOSED-Temporary power generator | Temporary back-up power generator | Unresolved |
| 18 | L-0017 PROPOSED-Existing holding tanks | Existing holding tanks — remove and relocate on site per Owner | Unresolved |
| 30 | L-0029 PROPOSED-Off-site staging area | Contractor staging area off Mt Baker Road, with vehicle path to the project site | Unresolved |
| 58 | L-0057 Hot Box #1 | 2W water hot box #1 — flow meter and isolation valve (relocated per Add. 4) | Unresolved |
| 59 | L-0058 Hot Box #2 | 2W water hot box #2 — air gap piping (relocated per Add. 4) | Unresolved |
| 73 | L-0072 PROPOSED-Existing slab coring and repair | Existing building slab — core or saw cut for under-slab piping, then repair | Unresolved |
| 92 | L-0091 PROPOSED-Parking stall striping | Parking stall striping, including van-accessible stall and signs | Unresolved |
| 95 | L-0094 PROPOSED-Concrete walkway | Concrete walkway / pavement, 6-inch minimum, #3 at 12 in each way | Unresolved |
| 96 | L-0095 PROPOSED-WWTP tank and building signs | WWTP tank and building signs, 9 (UV Disinfection Chamber, Blower Building, Dewatering Facility, Influent Pump Station, Aerobic Digester, Train 1–3, 2W Water System Pump Station) | Unresolved |
| 97 | L-0096 PROPOSED-Buried valve label markers | Bronze buried valve label markers (Berntsen #C35FB) with cast iron valve boxes and concrete pads | Unresolved |
| 99 | L-0098 PROPOSED-Gravel surfacing | Gravel surfacing, 4-in compacted base course over subgrade at 95% | Unresolved |
| 103 | L-0102 PROPOSED-Hot Box #1 flow meter | 1-inch flow meter in Hot Box #1, 'per electrical design requirements' | Unresolved |
| 104 | L-0103 PROPOSED-Hot Box #1 solenoid valve | Solenoid valve, ASCO Redhat 8221, 3/4-inch, slow-closing, normally closed, 120 VAC, NEMA 4X | Unresolved |
| 107 | L-0106 PROPOSED-Train 2 flow meter | Train 2 flow meter, 8-inch, in Train 2 flow meter vault | Unresolved |
| 108 | L-0107 PROPOSED-Train 3 flow meter | Train 3 flow meter, 8-inch, in Train 3 flow meter vault | Unresolved |
| 123 | L-0122 INF1 | Train 1 influent line, flow splitter to existing Train 1, 8-inch | Unresolved |
| 124 | L-0123 INF2 | Train 2 influent line, flow splitter to existing Train 2, 8-inch DI | Unresolved |
| 125 | L-0124 INF3 | Train 3 influent line, flow splitter to Train 3, 8-inch | Unresolved |
| 126 | L-0125 SE1 | Train 1 secondary effluent line to effluent flow meter and UV | Unresolved |
| 127 | L-0126 SE2 | Train 2 secondary effluent line to effluent flow meter and UV | Unresolved |
| 128 | L-0127 SE3 | Train 3 secondary effluent line, 8-inch | Unresolved |
| 129 | L-0128 WAS1 | Train 1 waste activated sludge line to WAS pump | Unresolved |
| 130 | L-0129 WAS2 | Train 2 waste activated sludge line to WAS pump | Unresolved |
| 133 | L-0132 PROPOSED-EXISTING-INFLUENT-PIPING-REMOVAL | Existing influent piping conflicts at the splitter: dewater, abandon, remove | Unresolved |
| 134 | L-0133 PROPOSED-INFLUENT-FLOW-METER | Influent flow meter, 6-inch electromagnetic, 0-880 gpm | Unresolved |
| 135 | L-0134 PROPOSED-TRAIN-2-FLOW-METER | Train 2 influent flow meter, 8-inch electromagnetic, 0-470 gpm | Unresolved |
| 136 | L-0135 PROPOSED-TRAIN-3-FLOW-METER | Train 3 influent flow meter, 8-inch electromagnetic, 0-470 gpm | Unresolved |
| 137 | L-0136 PROPOSED-EFFLUENT-FLOW-METER | Plant effluent flow meter, 8-inch electromagnetic, 0-940 gpm | Unresolved |
| 143 | L-0142 PROPOSED-FLOW-SPLITTER-BOX | Influent flow splitter box, prefabricated 316 SS, 4 equal chambers with adjustable weirs, removable cover | Unresolved |
| 144 | L-0143 PROPOSED-FLOW-SPLITTER-SUPPORT | Concrete support pad for flow splitter box, about 6.5 x 4.0 x 1.3 ft tall, top elev 26.00 | Unresolved |
| 145 | L-0144 PROPOSED-INFLUENT-FLOW-METER-VAULT | Flow meter vault on the splitter inlet line (north) | Unresolved |
| 146 | L-0145 PROPOSED-TRAIN-2-FLOW-METER-VAULT | Train 2 flow meter vault | Unresolved |
| 147 | L-0146 PROPOSED-TRAIN-3-FLOW-METER-VAULT | Train 3 flow meter vault | Unresolved |
| 149 | L-0148 PROPOSED-INFLUENT-SAMPLE-SUMP | Influent sampling sump | Unresolved |
| 150 | L-0149 PROPOSED-EFFLUENT-SAMPLE-SUMP | Effluent sample sump (effluent sample chamber) | Unresolved |
| 169 | L-0168 PROPOSED-IPS-HATCHES | Influent Pump Station access hatches: 36x36-in. single leaf H-20 (Halliday H1R3636) and 30x48-in. single leaf H-20 over pumps (Halliday H1R3048) | Unresolved |
| 171 | L-0170 PROPOSED-STEP-INFLUENT-CONNECTION | 8-inch STEP influent connection to the new Influent Pump Station, IE 19.50 | Unresolved |
| 179 | L-0178 PROPOSED-UV-DIGESTER-STRUCTURE | UV Disinfection Chamber & Digester structure, concrete, about 45 x 13 ft: UV chamber, effluent sample chamber, aerobic digester | Unresolved |
| 182 | L-0181 PROPOSED-EFFLUENT-HEADER-TO-UV | Secondary effluent header through 8-inch effluent flow meter to UV Channels #1 and #2, 8-inch, with 8-inch gate valves (hand wheel) at channel inlets | Unresolved |
| 183 | L-0182 PROPOSED-UV-CHAMBER-DRAIN | UV chamber drain, 4-inch, with 4-inch gate valves | Unresolved |
| 184 | L-0183 PROPOSED-UV-DIGESTER-GRATING-GUARDRAIL | UV/digester guardrail with removable guard chains, removable grating over digester, aluminum access ladders (nominal 2 ft wide) | Unresolved |
| 187 | L-0186 PROPOSED-DIGESTER-AIR-LINES | Aerobic digester air supply lines, 3-inch and 4-inch | Unresolved |
| 188 | L-0187 PROPOSED-DIGESTED-SLUDGE-LINE | Digested sludge line, 2-inch SCH 80 PVC, digester to digested sludge pumps | Unresolved |
| 189 | L-0188 PROPOSED-WAS-PUMP-DISCHARGE-TO-DIGESTER | WAS pump discharge to aerobic digester, 3-inch | Unresolved |
| 190 | L-0189 PROPOSED-FINAL-EFFLUENT-LINE | Final effluent, UV chamber to existing SSMH *1288 and 12-inch outfall, 10-inch | Unresolved |
| 191 | L-0190 S1–S2 [Aerobic Digester] | Aerobic digester transducer level sensor(s): S1 high alarm 25.55, S2 low alarm 15.30 | Unresolved |
| 200 | L-0199 PROPOSED-DIGESTED-SLUDGE-FEED-TO-PRESS | Digested sludge feed to rotary fan press, 3-inch | Unresolved |
| 205 | L-0204 PROPOSED-WAS-SOLENOID-VALVES | WAS inlet solenoid valves (3, on WAS #1-#3), ASCO Redhat 8221G013, 2-inch, normally closed, 120 V coil, NEMA 4X | Unresolved |
| 211 | L-0210 PROPOSED-AIR-TO-TRAIN-1-STUB | 6-inch air piping to Train #1, terminated with blind flange inside existing metal building | Unresolved |
| 212 | L-0211 PROPOSED-AIR-TO-TRAIN-2-STUB | 6-inch air piping to Train #2, terminated with blind flange inside existing metal building | Unresolved |
| 234 | L-0233 PROPOSED-WAS-FLOW-METER | WAS flow meter, 2-inch, on the WAS line to the digester, per electrical design requirements | Unresolved |
| 248 | L-0247 PROPOSED-Existing-Generator-Fuel-Tank-Exhaust-Louvers | Existing diesel fuel tank, generator exhaust system and louvers | Unresolved |
| 253 | L-0252 PROPOSED-Existing-200A-Feeder-to-Panel-TPS | Existing 200 A 208Y/120V power feeder to Panel TPS | Unresolved |
| 254 | L-0253 TPS | Panel TPS, 208Y/120V 3-ph 4-W, 200 A (kept; re-fed) | Unresolved |
| 255 | L-0254 PROPOSED-Existing-208V-400A-Distribution-Panel | Existing 208Y/120V 400 A distribution panel (Square-D I-Line), Office Building, re-fed from transformer TS | Unresolved |
| 257 | L-0256 BL-1 | Aeration Blower No.1 — cell aeration blower, Cell 1, 20 HP, VFD in MCC | Unresolved |
| 258 | L-0257 BL-2 | Aeration Blower No.2 — cell aeration blower, Cell 2, 20 HP, VFD in MCC | Unresolved |
| 259 | L-0258 BL-3 | Aeration Blower No.3 — cell aeration blower, Cell 3, 20 HP, VFD in MCC | Unresolved |
| 260 | L-0259 BL-4 | Aeration Blower No.4 — backup, 20 HP, VFD in MCC | Unresolved |
| 261 | L-0260 DB | Digester blower, 5 HP, VFD in MCC | Unresolved |
| 271 | L-0270 PROPOSED-Blower-High-Temperature-Switches | High-temperature switches at the aeration blowers (typ.) | Unresolved |
| 273 | L-0272 EF-1 | Exhaust Fan 1, Blower Building (motor marked 1/2), circuit LP1-5 | Unresolved |
| 274 | L-0273 EF-2 | Exhaust Fan 2, Blower Building (motor marked 1/2), circuit LP1-7 | Unresolved |
| 275 | L-0274 ML-1 | Motorized louver ML-1, Blower Building (motor marked 1/6), louver and HVAC control circuit LP1-3 | Unresolved |
| 276 | L-0275 PROPOSED-Blower-Building-Manual-Louver | Manual louver, Blower Building | Unresolved |
| 280 | L-0279 PROPOSED-Blower-Building-Ventilation-Control-Panel | Ventilation control panel: relay controls, one thermostat per exhaust fan, louver interlock | Unresolved |
| 281 | L-0280 TCP-3 | Train No.3 control panel TCP-3 (by treatment system provider), 480 V 3-ph input, NEMA 4X Type 316 SS | Unresolved |
| 282 | L-0281 PROPOSED-Train-3-Clarifier-Drive-Motor | Train No.3 clarifier drive motor | Unresolved |
| 283 | L-0282 PROPOSED-Train-3-Submersible-Mixer-A | Train No.3 submersible mixer A | Unresolved |
| 284 | L-0283 PROPOSED-Train-3-Submersible-Mixer-B | Train No.3 submersible mixer B | Unresolved |
| 288 | L-0287 IP-1 | Influent Pump No.1, 3 HP, explosion-proof (XP), 4.8 FLA | Unresolved |
| 289 | L-0288 IP-2 | Influent Pump No.2, 3 HP, explosion-proof (XP), 4.8 FLA | Unresolved |
| 290 | L-0289 IP-3 | Influent Pump No.3, 5 HP, explosion-proof (XP), 7.6 FLA | Unresolved |
| 291 | L-0290 IP-4 | Influent Pump No.4, 5 HP, explosion-proof (XP), 7.6 FLA | Unresolved |
| 312 | L-0311 PROPOSED-Train-1-Flow-Meter | Train #1 flow meter, 8 in — future project, not in this project; Phase I provides transmitter space in the IPS panel only | Unresolved |
| 313 | L-0312 DW-1 | Dewatering skid with skid control panel DW-1: pre-wired and factory tested, UL/ETL labeled per WA L&I, 15 HP, 480 V 3-ph; skid PLC, operator interface and network switch | Unresolved |
| 314 | L-0313 WP-1 | WAS Pump No.1, 3 HP, VFD in MCC | Unresolved |
| 315 | L-0314 WP-2 | WAS Pump No.2 / swing pump, 3 HP, VFD in MCC | Unresolved |
| 316 | L-0315 SD-1 | Sludge pump, 3 HP, VFD in MCC | Unresolved |
| 318 | L-0317 PROPOSED-WAS-Solenoid-Valves | WAS solenoid valves (3), WAS #1 to #3, 120 V from the IPS panel | Unresolved |
| 319 | L-0318 PROPOSED-Polymer-Feed-Pump | Polymer feed pump at the dewatering skid; 120 V GFCI receptacle LP2-6 and 4–20 mA flow pace | Unresolved |
| 320 | L-0319 PROPOSED-Hypochlorite-Feed-Pump | Hypochlorite feed pump; 120 V GFCI receptacle on LP1-16 and 4–20 mA flow pace | Unresolved |
| 321 | L-0320 PROPOSED-Influent-Sampler | Influent sampler (Owner-furnished, contractor-installed); 120 V GFCI receptacle LP2-8 and 4–20 mA flow pace | Unresolved |
| 322 | L-0321 PROPOSED-Effluent-Sampler | Effluent sampler (Owner-furnished, contractor-installed); 120 V GFCI receptacle on LP1-14 and 4–20 mA flow pace | Unresolved |
| 323 | L-0322 EF-3 | Exhaust Fan EF-3, Treatment Building, motor marked 1/2, circuit LP2-7 (1,127 VA) | Unresolved |
| 324 | L-0323 EF-4 | Exhaust Fan EF-4, Treatment Building, motor marked 1/2, circuit LP2-9 (1,127 VA) | Unresolved |
| 325 | L-0324 EF-5 | Exhaust Fan EF-5, Treatment Building, motor marked 1/2, circuit LP2-11 (1,127 VA) | Unresolved |
| 331 | L-0330 2W-P1 | 2W Water Pump No.1, 5 HP, VFD in MCC (E4.3 tags it P-2W-1) | Unresolved |
| 332 | L-0331 2W-P2 | 2W Water Pump No.2, 5 HP, VFD in MCC (E4.3 tags it P-2W-2) | Unresolved |
| 338 | L-0337 PROPOSED-Hot-Box-1 | Hot Box #1 (2W): houses the 1-in 2W flow meter, isolation valve solenoid, heat trace, GFEP and J-box | Unresolved |
| 339 | L-0338 PROPOSED-Hot-Box-2 | Hot Box #2 (2W): heat trace on exposed piping | Unresolved |
| 340 | L-0339 PROPOSED-Hot-Box-Heat-Trace | Heat trace on all exposed 2W piping in Hot Boxes #1 and #2: Raychem BTV self-regulating or equal, dedicated 120 V 20 A GFEP circuits (LP1-10, LP1-12), NEMA 4X thermostat, end-of-line kit with indicator light | Unresolved |
| 341 | L-0340 PROPOSED-2W-Isolation-Valve-Solenoid | Isolation valve solenoid in Hot Box #1 (2W line) | Unresolved |
| 342 | L-0341 UV1 | UV disinfection unit No.1 (UV modules on 10-ft cords, 2 per PDR) | Unresolved |
| 343 | L-0342 UV2 | UV disinfection unit No.2 (UV modules on 10-ft cords, 2 per PDR) | Unresolved |
| 344 | L-0343 PROPOSED-UV-Control-Panel-1 | UV control panel 1 (UV system controller), furnished with the UV system, installed by the contractor | Unresolved |
| 345 | L-0344 PROPOSED-UV-Control-Panel-2 | UV control panel 2 (UV system controller), furnished with the UV system, installed by the contractor | Unresolved |
| 352 | L-0351 TCP-1 | Train No.1 control panel (FUTURE); MCC 30/3 unit and feeder P-TCP1 | Unresolved |
| 353 | L-0352 TCP-2 | Train No.2 control panel (FUTURE); MCC 30/3 unit and feeder P-TCP2 | Unresolved |
| 355 | L-0354 PROPOSED-Blower-PTC-Relay-Modules | Blower motor PTC relay modules (5), furnished by the blower supplier, installed in the main PLC control panel | Unresolved |
| 356 | L-0355 PROPOSED-Influent-Pump-Seal-Fail-Overtemp-Relays | Influent pump seal-fail and overtemperature relays (4), Mini-CAS or equal, furnished by the pump manufacturer, installed in the IPS panel | Unresolved |
| 362 | L-0361 PROPOSED-Blowers-Blower-Building | Blowers (4) on the blower pad | Unresolved |
| 363 | L-0362 PROPOSED-2W-Bladder-Tank-Assembly | 2W bladder tank assembly — 2 tanks, 24 in diameter | Unresolved |
| 364 | L-0363 PROPOSED-Louver-36x84-Motorized | Louver, 36 in x 84 in, motorized — Blower Building west wall | Unresolved |
| 365 | L-0364 PROPOSED-Louver-24x24-Manual | Louver, 24 in x 24 in, manual — Blower Building west wall | Unresolved |
| 366 | L-0365 PROPOSED-Exhaust-Fans-Blower-Building | Exhaust fans (2) with 24 in x 24 in wall vents — Blower Building east wall | Unresolved |
| 378 | L-0377 PROPOSED-Blower-Building-Foundation-Drains | Perimeter foundation drains, 4 in rigid ABS perforated pipe or drain tile in drain rock — Blower Building slab edge | Unresolved |
| 386 | L-0385 PROPOSED-Drain-Pump-Station-Hatches | Access hatches (2), 2 ft-6 in x 4 ft-0 in rough openings, in the drain pump station lid — per civil | Unresolved |
| 388 | L-0387 PROPOSED-Generator-on-S2.4 | Generator shown on the generator slab — "per civil, attachment by others" | Unresolved |
| 390 | L-0389 PROPOSED-Flow-Splitter | Flow splitter — per civil, attachment by others | Unresolved |

## Spec Sections values that don't match 02 (1)

No edge made.

| Ledger row | Node ID | Value | Tag level |
|---|---|---|---|
| 199 | L-0198 PROPOSED-SCREW-CONVEYOR | 46 12 13 (as printed on C6.1; not in the spec) | Unresolved |

## Wiki Note(s) values with no Wiki note (12)

No described-by edge. The Project Wiki's note for the CQA plan is titled 'QA plan'.

| Ledger row | Node ID | Value | Tag level |
|---|---|---|---|
| 214 | L-0213 PROPOSED-BLOWER-BUILDING \| PROPOSED-Blower-Building | CQA Plan | Unresolved |
| 409 | L-0408 PROPOSED-Aerobic-Digester | CQA Plan | Unresolved |
| 411 | L-0410 PROPOSED-UV-Disinfection-System | CQA Plan | Unresolved |
| 412 | L-0411 PROPOSED-Sludge-Pumps | CQA Plan | Unresolved |
| 415 | L-0414 PROPOSED-2W-Air-Gap-Water-System | CQA Plan | Unresolved |
| 416 | L-0415 PROPOSED-Influent-Pump-Station | CQA Plan | Unresolved |
| 418 | L-0417 PROPOSED-Influent-Flow-Splitter | CQA Plan | Unresolved |
| 420 | L-0419 PROPOSED-Train-3 | CQA Plan | Unresolved |
| 424 | L-0423 PROPOSED-Permanent-Standby-Generator | CQA Plan | Unresolved |
| 428 | L-0427 PROPOSED-Dewatering-System | CQA Plan | Unresolved |
| 436 | L-0435 PROPOSED-Contractor-Field-Office | CQA Plan | Unresolved |
| 444 | L-0443 PROPOSED-Blowers | CQA Plan | Unresolved |

## Wiki note and 01 rev2 disagree on whether a sheet is in the library (6)

01 rev2 found these sheets in the native parts after the Wiki note was written; the note summary still describes the sheet as unavailable. Needs a Wiki note revision (not done here).

| Sheet | Wiki note Type | 01 rev2 Status | Tag level |
|---|---|---|---|
| C0.7 | Drawing sheet — unavailable | Available — native Part 1 p.14 (rev2; Plan_Set_Crosswalk.csv line 15) | Unresolved |
| C1.1 | Drawing sheet — unavailable | Available — native Part 1 p.15 (rev2; Plan_Set_Crosswalk.csv line 16) | Unresolved |
| C1.2 | Drawing sheet — unavailable | Available — native Part 1 p.16 (rev2; Plan_Set_Crosswalk.csv line 17) | Unresolved |
| C7.7 | Drawing sheet — unavailable | Available — native Part 3 p.1 (rev2; Plan_Set_Crosswalk.csv line 53) | Unresolved |
| C7.8 | Drawing sheet — unavailable | Available — native Part 3 p.2 (rev2; Plan_Set_Crosswalk.csv line 54) | Unresolved |
| C7.9 | Drawing sheet — unavailable | Available — native Part 3 p.3 (rev2; Plan_Set_Crosswalk.csv line 55) | Unresolved |

## Wiki notes with no sheet or spec node (28)

| Note ID | Title | Why | Ledger rows citing it | Tag level |
|---|---|---|---|---|
| 00 11 16 | Invitation to Bid | spec section the Ledger does not cite | 0 | Unresolved |
| 00 21 13 | Instructions to Bidders | spec section the Ledger does not cite | 0 | Unresolved |
| 00 43 13 | Bid Bond Form | spec section the Ledger does not cite | 0 | Unresolved |
| 00 43 93 | Bid Submittal Checklist | spec section the Ledger does not cite | 0 | Unresolved |
| 00 45 13 | Contractor Qualifications | spec section the Ledger does not cite | 0 | Unresolved |
| 00 45 19 | Non-Collusion Affidavit | spec section the Ledger does not cite | 0 | Unresolved |
| 00 45 29 | Certification of Compliance with Wage Payment Statutes | spec section the Ledger does not cite | 0 | Unresolved |
| 00 45 33 | List of Subcontractors (Bids on Public Works — Identification, Substitution of Subcontractors) | spec section the Ledger does not cite | 0 | Unresolved |
| 00 45 43 | Subcontractor Qualifications | spec section the Ledger does not cite | 0 | Unresolved |
| 00 51 00 | Notice of Award | spec section the Ledger does not cite | 0 | Unresolved |
| 00 52 00 | Agreement Form | spec section the Ledger does not cite | 0 | Unresolved |
| 00 54 00 | CDBG Conditions (WA Dept. of Commerce, Attachment 7-A(1)) | spec section the Ledger does not cite | 0 | Unresolved |
| 00 55 00 | Notice to Proceed | spec section the Ledger does not cite | 0 | Unresolved |
| 00 61 13 | Performance and Payment Bond Forms | spec section the Ledger does not cite | 0 | Unresolved |
| 00 61 23 | Retainage Bond Form (Retainage Investment Option) | spec section the Ledger does not cite | 0 | Unresolved |
| 01 41 00 | Regulatory Requirements | spec section the Ledger does not cite | 0 | Unresolved |
| 01 60 00 | Product Requirements | spec section the Ledger does not cite | 0 | Unresolved |
| 01 66 00 | Product Storage and Handling Requirements | spec section the Ledger does not cite | 0 | Unresolved |
| 06 20 00 | Finish Carpentry | spec section the Ledger does not cite | 0 | Unresolved |
| 07 92 00 | Joint Sealants (TOC: Joint Seals) | spec section the Ledger does not cite | 0 | Unresolved |
| 31 10 00 | Site Clearing | spec section the Ledger does not cite | 0 | Unresolved |
| Add. 4 Generator Exhibit | Temporary back-up generator example cut sheet (Sunbelt Rentals) | carried on Add. 4 Clarification 5 (03: exhibit pp.11–13) | 2 | Unresolved |
| Appendix B | Groundwater Level Analysis | spec section the Ledger does not cite | 0 | Unresolved |
| Appendix D | Washington State Prevailing Wage Rates | spec section the Ledger does not cite | 0 | Unresolved |
| Appendix E | Federal Prevailing Wage Rates | spec section the Ledger does not cite | 0 | Unresolved |
| Appendix G | Inadvertent Discovery Plan | spec section the Ledger does not cite | 0 | Unresolved |
| Appendix I | CDBG Funding: Required Documents | spec section the Ledger does not cite | 0 | Unresolved |
| QA plan | Construction Quality Assurance Plan (Wilson Engineering) | not a sheet or spec section | 0 | Unresolved |
