# Electrical & Controls — Wiki by Page and by Component

Two linked views of the Electrical & Controls stack of the Eastsound WWTP Phase I bid set: one file per page (what components each page shows) and one wiki per component (everything the crawl found on that component). Component tags in the page tables link to the component wikis; each component wiki links back to its pages.

- **Page files:** 55 — 35 drawing pages (E0.1–E10.3), 14 Division 26 sections, 6 Addendum 4 pages.
- **Component wikis:** 126 — one per Ledger row, filed by area under `Components/`.
- **Built from:** `Electrical_and_Controls_Ledger.csv` (126 rows), `Electrical_and_Controls_Wiki.md`, `Electrical_and_Controls_Issues.md` and `Electrical_and_Controls_Known_Issues.md`. Built 2026-09-30.
- **Drawing pages:** a component is on a page when its Ledger "Drawing Sheets" column lists that sheet. **Specifications:** one file per section (requirements and the Ledger Spec Sections column are section-level). **Addendum 4:** pages 1–3 (items 03 maps to this lane) and the generator exhibit, pages 11–13.
- **Placement:** each page file names its source PDF and page, so it can sit beside that document without renaming or moving the source.
- **Tag level:** Verified = text layer · Verified-Visual = page image · Inferred = derived · Unresolved = conflict or gap (see Issues).

## Page files

| File | Source PDF | Page | Components | Unresolved |
|---|---|---|---|---|
| [Drawings/062 E0.1 - Electrical Symbols and Abbreviations.md](Drawings/062%20E0.1%20-%20Electrical%20Symbols%20and%20Abbreviations.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf` | PDF p.6 (set p.62) | 0 | 0 |
| [Drawings/063 E0.2 - Electrical Demolition Site Plan and One Line Diagram.md](Drawings/063%20E0.2%20-%20Electrical%20Demolition%20Site%20Plan%20and%20One%20Line%20Diagram.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf` | PDF p.7 (set p.63) | 14 | 0 |
| [Drawings/064 E0.3 - Overall Electrical Site Plan.md](Drawings/064%20E0.3%20-%20Overall%20Electrical%20Site%20Plan.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_8.pdf` | PDF p.8 (set p.64) | 1 | 0 |
| [Drawings/065 E0.4 - Area Classification Site Plan.md](Drawings/065%20E0.4%20-%20Area%20Classification%20Site%20Plan.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf` | PDF p.1 (set p.65) | 0 | 0 |
| [Drawings/066 E1.1 - Electric Service Area Plan.md](Drawings/066%20E1.1%20-%20Electric%20Service%20Area%20Plan.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf` | PDF p.2 (set p.66) | 15 | 2 |
| [Drawings/067 E2.1 - Blower Building Power, Control and Grounding Plan.md](Drawings/067%20E2.1%20-%20Blower%20Building%20Power%2C%20Control%20and%20Grounding%20Plan.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf` | PDF p.3 (set p.67) | 16 | 1 |
| [Drawings/068 E2.2 - Blower Building Lighting and HVAC Plan.md](Drawings/068%20E2.2%20-%20Blower%20Building%20Lighting%20and%20HVAC%20Plan.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf` | PDF p.4 (set p.68) | 13 | 1 |
| [Drawings/069 E3.1 - Train No.3 Electrical Plan and Elevation.md](Drawings/069%20E3.1%20-%20Train%20No.3%20Electrical%20Plan%20and%20Elevation.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf` | PDF p.5 (set p.69) | 8 | 0 |
| [Drawings/070 E4.1 - Influent Pump Station, WAS, Dewatering Electrical Plan.md](Drawings/070%20E4.1%20-%20Influent%20Pump%20Station%2C%20WAS%2C%20Dewatering%20Electrical%20Plan.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf` | PDF p.6 (set p.70) | 41 | 3 |
| [Drawings/071 E4.2 - Influent Pump Station Electrical Plan and Elevation.md](Drawings/071%20E4.2%20-%20Influent%20Pump%20Station%20Electrical%20Plan%20and%20Elevation.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf` | PDF p.7 (set p.71) | 11 | 1 |
| [Drawings/072 E4.3 - 2W Pump Station Electrical Plan and Elevation.md](Drawings/072%20E4.3%20-%202W%20Pump%20Station%20Electrical%20Plan%20and%20Elevation.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_9.pdf` | PDF p.8 (set p.72) | 11 | 4 |
| [Drawings/073 E5.1 - UV Disinfection Chamber and Digester Electrical Plan and Elevation.md](Drawings/073%20E5.1%20-%20UV%20Disinfection%20Chamber%20and%20Digester%20Electrical%20Plan%20and%20Elevation.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf` | PDF p.1 (set p.73) | 10 | 2 |
| [Drawings/074 E6.1 - Electrical One Line Diagram and Load Calculations.md](Drawings/074%20E6.1%20-%20Electrical%20One%20Line%20Diagram%20and%20Load%20Calculations.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf` | PDF p.2 (set p.74) | 39 | 7 |
| [Drawings/075 E6.2 - Electrical Panel Schedules.md](Drawings/075%20E6.2%20-%20Electrical%20Panel%20Schedules.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf` | PDF p.3 (set p.75) | 25 | 4 |
| [Drawings/076 E6.3 - Conduit and Conductor Schedules.md](Drawings/076%20E6.3%20-%20Conduit%20and%20Conductor%20Schedules.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf` | PDF p.4 (set p.76) | 70 | 13 |
| [Drawings/077 E7.0 - Control System Overview.md](Drawings/077%20E7.0%20-%20Control%20System%20Overview.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf` | PDF p.5 (set p.77) | 15 | 2 |
| [Drawings/078 E7.1 - Main PLC Control Panel Elevation.md](Drawings/078%20E7.1%20-%20Main%20PLC%20Control%20Panel%20Elevation.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf` | PDF p.6 (set p.78) | 9 | 2 |
| [Drawings/079 E7.2 - Main PLC Control Panel - Power Wiring Diagram.md](Drawings/079%20E7.2%20-%20Main%20PLC%20Control%20Panel%20-%20Power%20Wiring%20Diagram.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf` | PDF p.7 (set p.79) | 8 | 2 |
| [Drawings/080 E7.3 - Main PLC Control Panel - Digital Inputs.md](Drawings/080%20E7.3%20-%20Main%20PLC%20Control%20Panel%20-%20Digital%20Inputs.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_10.pdf` | PDF p.8 (set p.80) | 27 | 7 |
| [Drawings/081 E7.4 - Main PLC Control Panel - Digital Outputs.md](Drawings/081%20E7.4%20-%20Main%20PLC%20Control%20Panel%20-%20Digital%20Outputs.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf` | PDF p.1 (set p.81) | 13 | 3 |
| [Drawings/082 E7.5 - Main PLC Control Panel - Analog Inputs - Sheet 1.md](Drawings/082%20E7.5%20-%20Main%20PLC%20Control%20Panel%20-%20Analog%20Inputs%20-%20Sheet%201.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf` | PDF p.2 (set p.82) | 5 | 2 |
| [Drawings/083 E7.6 - Main PLC Control Panel - Analog Inputs - Sheet 2.md](Drawings/083%20E7.6%20-%20Main%20PLC%20Control%20Panel%20-%20Analog%20Inputs%20-%20Sheet%202.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf` | PDF p.3 (set p.83) | 5 | 3 |
| [Drawings/084 E7.7 - Main PLC Control Panel - Analog Outputs.md](Drawings/084%20E7.7%20-%20Main%20PLC%20Control%20Panel%20-%20Analog%20Outputs.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf` | PDF p.4 (set p.84) | 4 | 1 |
| [Drawings/085 E8.1 - Influent Pump Station Control Panel Elevations.md](Drawings/085%20E8.1%20-%20Influent%20Pump%20Station%20Control%20Panel%20Elevations.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf` | PDF p.5 (set p.85) | 20 | 2 |
| [Drawings/086 E8.2 - Influent Pump Station Control Panel - Power Wiring Diagram.md](Drawings/086%20E8.2%20-%20Influent%20Pump%20Station%20Control%20Panel%20-%20Power%20Wiring%20Diagram.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf` | PDF p.6 (set p.86) | 5 | 1 |
| [Drawings/087 E8.3 - Influent Pump Station Control Panel - Digital Inputs.md](Drawings/087%20E8.3%20-%20Influent%20Pump%20Station%20Control%20Panel%20-%20Digital%20Inputs.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf` | PDF p.7 (set p.87) | 13 | 2 |
| [Drawings/088 E8.4 - Influent Pump Station Control Panel - Digital Outputs.md](Drawings/088%20E8.4%20-%20Influent%20Pump%20Station%20Control%20Panel%20-%20Digital%20Outputs.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_11.pdf` | PDF p.8 (set p.88) | 10 | 2 |
| [Drawings/089 E8.5 - Influent Pump Station Control Panel - Analog Inputs.md](Drawings/089%20E8.5%20-%20Influent%20Pump%20Station%20Control%20Panel%20-%20Analog%20Inputs.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf` | PDF p.1 (set p.89) | 4 | 2 |
| [Drawings/090 E8.6 - Influent Pump Station Control Panel - Analog Outputs.md](Drawings/090%20E8.6%20-%20Influent%20Pump%20Station%20Control%20Panel%20-%20Analog%20Outputs.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf` | PDF p.2 (set p.90) | 3 | 1 |
| [Drawings/091 E9.1 - Blower Building Motor Control Center Elevation.md](Drawings/091%20E9.1%20-%20Blower%20Building%20Motor%20Control%20Center%20Elevation.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf` | PDF p.3 (set p.91) | 20 | 5 |
| [Drawings/092 E9.2 - Blower Building Motor Control Center - VFD Wiring Diagrams.md](Drawings/092%20E9.2%20-%20Blower%20Building%20Motor%20Control%20Center%20-%20VFD%20Wiring%20Diagrams.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf` | PDF p.4 (set p.92) | 7 | 0 |
| [Drawings/093 E9.3 - Ventilation Control Panel Elevation and Wiring Diagram.md](Drawings/093%20E9.3%20-%20Ventilation%20Control%20Panel%20Elevation%20and%20Wiring%20Diagram.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf` | PDF p.5 (set p.93) | 7 | 1 |
| [Drawings/094 E10.1 - Electrical Details - Sheet 1.md](Drawings/094%20E10.1%20-%20Electrical%20Details%20-%20Sheet%201.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf` | PDF p.6 (set p.94) | 14 | 1 |
| [Drawings/095 E10.2 - Electrical Details - Sheet 2.md](Drawings/095%20E10.2%20-%20Electrical%20Details%20-%20Sheet%202.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf` | PDF p.7 (set p.95) | 11 | 0 |
| [Drawings/096 E10.3 - Standby Diesel Generator Elevations.md](Drawings/096%20E10.3%20-%20Standby%20Diesel%20Generator%20Elevations.md) | `Pages_from_eswd-wwtp-upgrade-ph1-11x17-plans_12.pdf` | PDF p.8 (set p.96) | 1 | 1 |
| [Specifications/26 05 00 - General Electrical.md](Specifications/26%2005%2000%20-%20General%20Electrical.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.269–281 | 12 | 1 |
| [Specifications/26 05 19 - Wire and Cable.md](Specifications/26%2005%2019%20-%20Wire%20and%20Cable.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.282–288 | 3 | 0 |
| [Specifications/26 05 26 - Grounding and Bonding.md](Specifications/26%2005%2026%20-%20Grounding%20and%20Bonding.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | p.289 | 3 | 0 |
| [Specifications/26 05 33 - Raceways and Boxes.md](Specifications/26%2005%2033%20-%20Raceways%20and%20Boxes.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.290–296 | 9 | 0 |
| [Specifications/26 22 13 - Dry Type Transformers.md](Specifications/26%2022%2013%20-%20Dry%20Type%20Transformers.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.297–299 | 3 | 0 |
| [Specifications/26 24 16 - Panelboards.md](Specifications/26%2024%2016%20-%20Panelboards.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.300–304 | 3 | 0 |
| [Specifications/26 24 19 - Motor Control Centers.md](Specifications/26%2024%2019%20-%20Motor%20Control%20Centers.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.305–311 | 1 | 0 |
| [Specifications/26 27 26 - Wiring Devices.md](Specifications/26%2027%2026%20-%20Wiring%20Devices.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.312–313 | 2 | 0 |
| [Specifications/26 28 16 - Disconnects and Switches.md](Specifications/26%2028%2016%20-%20Disconnects%20and%20Switches.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.314–315 | 5 | 0 |
| [Specifications/26 29 23 - Variable Frequency Drives.md](Specifications/26%2029%2023%20-%20Variable%20Frequency%20Drives.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.316–320 | 1 | 0 |
| [Specifications/26 32 13 - Diesel Emergency Engine Generator.md](Specifications/26%2032%2013%20-%20Diesel%20Emergency%20Engine%20Generator.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.321–337 | 1 | 1 |
| [Specifications/26 36 00 - Automatic Transfer Switches.md](Specifications/26%2036%2000%20-%20Automatic%20Transfer%20Switches.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.338–348 | 1 | 1 |
| [Specifications/26 51 19 - LED Lighting.md](Specifications/26%2051%2019%20-%20LED%20Lighting.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.349–351 | 6 | 1 |
| [Specifications/26 80 00 - Control System.md](Specifications/26%2080%2000%20-%20Control%20System.md) | `eswd-wwtp-upgrade-phase-i-specs.pdf` | pp.352–381 | 30 | 5 |
| [Addendum 4/Add 4 p01 - Clarifications (items 3, 4 and 5 bear on this lane).md](Addendum%204/Add%204%20p01%20-%20Clarifications%20%28items%203%2C%204%20and%205%20bear%20on%20this%20lane%29.md) | `addendum-no4-eswd.pdf` | PDF p.1 | 3 | 2 |
| [Addendum 4/Add 4 p02 - Specification items.md](Addendum%204/Add%204%20p02%20-%20Specification%20items.md) | `addendum-no4-eswd.pdf` | PDF p.2 | 14 | 3 |
| [Addendum 4/Add 4 p03 - Drawing items.md](Addendum%204/Add%204%20p03%20-%20Drawing%20items.md) | `addendum-no4-eswd.pdf` | PDF p.3 | 6 | 3 |
| [Addendum 4/Add 4 p11 - Rental generator exhibit, page 1 of 3.md](Addendum%204/Add%204%20p11%20-%20Rental%20generator%20exhibit%2C%20page%201%20of%203.md) | `addendum-no4-eswd.pdf` | PDF p.11 | 1 | 1 |
| [Addendum 4/Add 4 p12 - Rental generator exhibit, page 2 of 3.md](Addendum%204/Add%204%20p12%20-%20Rental%20generator%20exhibit%2C%20page%202%20of%203.md) | `addendum-no4-eswd.pdf` | PDF p.12 | 1 | 1 |
| [Addendum 4/Add 4 p13 - Rental generator exhibit, page 3 of 3.md](Addendum%204/Add%204%20p13%20-%20Rental%20generator%20exhibit%2C%20page%203%20of%203.md) | `addendum-no4-eswd.pdf` | PDF p.13 | 0 | 0 |

## Component wikis by area

### Electric Service Area (18)

| Component | Name | Type | Status | Tag level | Open items |
|---|---|---|---|---|---|
| [ATS](Components/Electric%20Service%20Area/ATS.md) | Automatic transfer switch, service-entrance rated, 480Y/277V, 400 A (permanent) | Transfer switch | New | Unresolved | 2 |
| [ATS (E)](Components/Electric%20Service%20Area/ATS%20%28E%29.md) | Existing automatic transfer switch, 4-wire, 3-pole | Transfer switch | Demolished | Verified-Visual | 0 |
| [GEN](Components/Electric%20Service%20Area/GEN.md) | Standby diesel generator, 480Y/277V, 125 kW / 156 kVA, sound-attenuated outdoor enclosure with sub-base diesel fuel tank (permanent) | Generator | New | Unresolved | 2 |
| [GEN (E)](Components/Electric%20Service%20Area/GEN%20%28E%29.md) | Existing standby diesel generator, 208Y/120V 3-ph, 30 kW / 37.5 kVA | Generator | Demolished | Verified-Visual | 0 |
| [MDP](Components/Electric%20Service%20Area/MDP.md) | Main distribution panel MDP, 480Y/277V 3-ph 4-W, 400 A bus, main lugs only, 42,000 AIC, surface mounted, with SPD | Panelboard | New | Inferred | 1 |
| [P-SEC](Components/Electric%20Service%20Area/P-SEC.md) | Utility secondary conduit and conductors, new utility transformer to service equipment (by contractor) | Raceway and feeder | New | Verified-Visual | 0 |
| [P-TPS](Components/Electric%20Service%20Area/P-TPS.md) | Replacement 200 A 208Y/120V feeder, existing switchgear to Panel TPS | Raceway and feeder | New | Verified | 0 |
| [SES (E)](Components/Electric%20Service%20Area/SES%20%28E%29.md) | Existing 300 A service entrance breaker, SUSE rated, NEMA 3R | Service equipment | Demolished | Verified-Visual | 0 |
| [TS](Components/Electric%20Service%20Area/TS.md) | Transformer TS, 75 kVA, 480–208Y/120V | Transformer | New | Inferred | 0 |
| [PROPOSED-CT-Enclosure-and-Meter-Base](Components/Electric%20Service%20Area/PROPOSED-CT-Enclosure-and-Meter-Base.md) | CT enclosure, landing pads and meter base (new; meter and CTs by utility) | Metering | New | Verified | 0 |
| [PROPOSED-Existing-CT-Enclosure-and-Meter](Components/Electric%20Service%20Area/PROPOSED-Existing-CT-Enclosure-and-Meter.md) | Existing current transformer enclosure and OPALCO utility meter | Metering | Demolished | Verified | 0 |
| [PROPOSED-Existing-Generator-Fuel-Tank-Exhaust-Louvers](Components/Electric%20Service%20Area/PROPOSED-Existing-Generator-Fuel-Tank-Exhaust-Louvers.md) | Existing diesel fuel tank, generator exhaust system and louvers | Generator auxiliaries | Demolished | Verified | 0 |
| [PROPOSED-Existing-Grounding-Electrode-System](Components/Electric%20Service%20Area/PROPOSED-Existing-Grounding-Electrode-System.md) | Existing grounding electrode system (kept; new equipment and electrodes bonded to it) | Grounding system | Existing | Verified | 0 |
| [PROPOSED-Existing-Meter-Base-and-Wall-Raceway](Components/Electric%20Service%20Area/PROPOSED-Existing-Meter-Base-and-Wall-Raceway.md) | Existing obsolete meter base and raceway on building wall | Metering | Demolished | Verified | 0 |
| [PROPOSED-Existing-Utility-Transformer-208V](Components/Electric%20Service%20Area/PROPOSED-Existing-Utility-Transformer-208V.md) | Existing OPALCO pad-mount utility transformer, 208Y/120V 3-ph, 45 kVA | Transformer | Demolished | Verified | 0 |
| [PROPOSED-Service-Area-Grounding-Electrode-System](Components/Electric%20Service%20Area/PROPOSED-Service-Area-Grounding-Electrode-System.md) | Grounding electrode systems at the new service: utility transformer grounding, generator pad rebar bond, separately derived system grounding | Grounding system | New | Inferred | 0 |
| [PROPOSED-Temporary-Backup-Generator](Components/Electric%20Service%20Area/PROPOSED-Temporary-Backup-Generator.md) | Temporary back-up generator (rental), connected to the permanent ATS until the permanent generator arrives; example cut sheet MQ Power 120 kW prime diesel | Generator (temporary) | Temporary | Unresolved | 2 |
| [PROPOSED-Utility-Transformer-480V](Components/Electric%20Service%20Area/PROPOSED-Utility-Transformer-480V.md) | Utility transformer, 480Y/277V, 225 kVA (new; furnished and installed by OPALCO) | Transformer | New | Verified-Visual | 1 |

### Blower Building (25)

| Component | Name | Type | Status | Tag level | Open items |
|---|---|---|---|---|---|
| [BL-1](Components/Blower%20Building/BL-1.md) | Aeration Blower No.1 — cell aeration blower, Cell 1, 20 HP, VFD in MCC | Blower | New | Inferred | 0 |
| [BL-2](Components/Blower%20Building/BL-2.md) | Aeration Blower No.2 — cell aeration blower, Cell 2, 20 HP, VFD in MCC | Blower | New | Inferred | 0 |
| [BL-3](Components/Blower%20Building/BL-3.md) | Aeration Blower No.3 — cell aeration blower, Cell 3, 20 HP, VFD in MCC | Blower | New | Inferred | 0 |
| [BL-4](Components/Blower%20Building/BL-4.md) | Aeration Blower No.4 — backup, 20 HP, VFD in MCC | Blower | New | Inferred | 0 |
| [EF-1](Components/Blower%20Building/EF-1.md) | Exhaust Fan 1, Blower Building (motor marked 1/2), circuit LP1-5 | Fan | New | Inferred | 0 |
| [EF-2](Components/Blower%20Building/EF-2.md) | Exhaust Fan 2, Blower Building (motor marked 1/2), circuit LP1-7 | Fan | New | Inferred | 0 |
| [L1 (Blower Building)](Components/Blower%20Building/L1%20%28Blower%20Building%29.md) | Light fixture type L1: narrow LED 4-ft, vapor tight, 120 V, 42 VA (Acuity CSVT-L48…) | Lighting | New | Verified-Visual | 0 |
| [L2 (Blower Building)](Components/Blower%20Building/L2%20%28Blower%20Building%29.md) | Light fixture type L2: LED wall pack, wet location, photocell, 120 V, 17 VA (Acuity ARC1 LED…) | Lighting | New | Verified-Visual | 0 |
| [LP-1](Components/Blower%20Building/LP-1.md) | Lighting panel LP1, 120/240 V 1-ph 3-W, 100 A bus, 100 A main breaker, 10,000 AIC, surface mounted | Panelboard | New | Inferred | 1 |
| [MCC](Components/Blower%20Building/MCC.md) | Motor control center, 480 V 3-ph 4-W, Blower Building, Allen-Bradley Centerline 2100 IntelliCENTER | Motor control center | New | Inferred | 0 |
| [MCP](Components/Blower%20Building/MCP.md) | Main Control Panel (PLC), Blower Building | Control panel | New | Unresolved | 2 |
| [ML-1](Components/Blower%20Building/ML-1.md) | Motorized louver ML-1, Blower Building (motor marked 1/6), louver and HVAC control circuit LP1-3 | Louver | New | Inferred | 0 |
| [T2](Components/Blower%20Building/T2.md) | Transformer T2, 20 kVA, 480–120/240V (MCC; feeds load center LP1) | Transformer | New | Inferred | 0 |
| [X1 (Blower Building)](Components/Blower%20Building/X1%20%28Blower%20Building%29.md) | Light fixture type X1: LED emergency combo with battery pack, 120 V, 6 VA (Lithonia ECC) | Lighting | New | Verified-Visual | 0 |
| [PROPOSED-2W-Pressure-Transducer](Components/Blower%20Building/PROPOSED-2W-Pressure-Transducer.md) | 2W system pressure transducer, 0–150 psi, 4–20 mA, Blower Building | Instrument | Not stated | Verified | 0 |
| [PROPOSED-Blower-Building-Control-Signal-Handholes](Components/Blower%20Building/PROPOSED-Blower-Building-Control-Signal-Handholes.md) | Electric control and signal handholes at the Blower Building (2 shown) | Handhole | New | Verified-Visual | 0 |
| [PROPOSED-Blower-Building-Door-Intrusion-Switch](Components/Blower%20Building/PROPOSED-Blower-Building-Door-Intrusion-Switch.md) | Door intrusion switch, magnetic reed SPDT, Interlogix Sentrol 2807T or equal | Instrument | New | Verified | 0 |
| [PROPOSED-Blower-Building-Grounding-Electrode-System](Components/Blower%20Building/PROPOSED-Blower-Building-Grounding-Electrode-System.md) | Blower Building grounding electrode system (ground rods, concrete-encased electrode, structural steel, metal water pipe) | Grounding system | New | Verified | 0 |
| [PROPOSED-Blower-Building-Manual-Louver](Components/Blower%20Building/PROPOSED-Blower-Building-Manual-Louver.md) | Manual louver, Blower Building | Louver | New | Inferred | 0 |
| [PROPOSED-Blower-Building-Power-Handholes](Components/Blower%20Building/PROPOSED-Blower-Building-Power-Handholes.md) | Electric power handholes at the Blower Building (2 shown) | Handhole | New | Verified-Visual | 0 |
| [PROPOSED-Blower-Building-Smoke-Heat-Detector](Components/Blower%20Building/PROPOSED-Blower-Building-Smoke-Heat-Detector.md) | Ceiling smoke/heat detector, System Sensor 4WTAR-B, Form C relay, sounder, 4-wire | Instrument | New | Verified | 0 |
| [PROPOSED-Blower-Building-Ventilation-Control-Panel](Components/Blower%20Building/PROPOSED-Blower-Building-Ventilation-Control-Panel.md) | Ventilation control panel: relay controls, one thermostat per exhaust fan, louver interlock | Control panel | New | Verified | 1 |
| [PROPOSED-Blower-High-Temperature-Switches](Components/Blower%20Building/PROPOSED-Blower-High-Temperature-Switches.md) | High-temperature switches at the aeration blowers (typ.) | Instrument | Not stated | Verified-Visual | 1 |
| [PROPOSED-Blower-PTC-Relay-Modules](Components/Blower%20Building/PROPOSED-Blower-PTC-Relay-Modules.md) | Blower motor PTC relay modules (5), furnished by the blower supplier, installed in the main PLC control panel | Relay modules | New | Inferred | 0 |
| [PROPOSED-VFDs-in-MCC](Components/Blower%20Building/PROPOSED-VFDs-in-MCC.md) | Variable frequency drives in the MCC (10), Allen-Bradley PowerFlex 753 with Ethernet module, each with a 3% line-side reactor; dV/dt filters on motor runs over 50 ft | Drives | New | Inferred | 0 |

### Treatment Trains (11)

| Component | Name | Type | Status | Tag level | Open items |
|---|---|---|---|---|---|
| [DO-1](Components/Treatment%20Trains/DO-1.md) | Dissolved oxygen sensor and transmitter, Zone 1 (Hach LDO probe, SC200 transmitter, 24 VDC) | Instrument | New | Verified | 0 |
| [DO-2](Components/Treatment%20Trains/DO-2.md) | Dissolved oxygen sensor and transmitter, second monitor (Hach LDO/SC200) | Instrument | New | Inferred | 0 |
| [TCP-1](Components/Treatment%20Trains/TCP-1.md) | Train No.1 control panel (FUTURE); MCC 30/3 unit and feeder P-TCP1 | Control panel | Not stated | Unresolved | 1 |
| [TCP-2](Components/Treatment%20Trains/TCP-2.md) | Train No.2 control panel (FUTURE); MCC 30/3 unit and feeder P-TCP2 | Control panel | Not stated | Unresolved | 1 |
| [TCP-3](Components/Treatment%20Trains/TCP-3.md) | Train No.3 control panel TCP-3 (by treatment system provider), 480 V 3-ph input, NEMA 4X Type 316 SS | Control panel | New | Inferred | 0 |
| [PROPOSED-Train-1-Flow-Meter](Components/Treatment%20Trains/PROPOSED-Train-1-Flow-Meter.md) | Train #1 flow meter, 8 in — future project, not in this project; Phase I provides transmitter space in the IPS panel only | Flow meter | Not stated | Verified-Visual | 0 |
| [PROPOSED-Train-3-Clarifier-Drive-Motor](Components/Treatment%20Trains/PROPOSED-Train-3-Clarifier-Drive-Motor.md) | Train No.3 clarifier drive motor | Process equipment | New | Inferred | 0 |
| [PROPOSED-Train-3-Local-Disconnects](Components/Treatment%20Trains/PROPOSED-Train-3-Local-Disconnects.md) | Local motor disconnects, NEMA 4X Type 316 SS, for the clarifier drive and two mixers (3) | Disconnect switch | New | Inferred | 0 |
| [PROPOSED-Train-3-Pole-Light](Components/Treatment%20Trains/PROPOSED-Train-3-Pole-Light.md) | Platform pole light: 4-in square aluminum pole, 12 ft, receptacle, photocell, local switch; Lithonia "#DXS0-LED-P3-30K-T3M-MVOLT-SPA-DNAXD" (as printed) or equal | Lighting | New | Verified | 0 |
| [PROPOSED-Train-3-Submersible-Mixer-A](Components/Treatment%20Trains/PROPOSED-Train-3-Submersible-Mixer-A.md) | Train No.3 submersible mixer A | Process equipment | New | Inferred | 0 |
| [PROPOSED-Train-3-Submersible-Mixer-B](Components/Treatment%20Trains/PROPOSED-Train-3-Submersible-Mixer-B.md) | Train No.3 submersible mixer B | Process equipment | New | Inferred | 0 |

### Influent Pump Station (21)

| Component | Name | Type | Status | Tag level | Open items |
|---|---|---|---|---|---|
| [F1 (Influent Pump Station)](Components/Influent%20Pump%20Station/F1%20%28Influent%20Pump%20Station%29.md) | Float switch F1, Eco-Float GP60NONC, non-mercury NO/NC — redundant large lag on at 19.00 (with timer) | Instrument | New | Inferred | 2 |
| [F2 (Influent Pump Station)](Components/Influent%20Pump%20Station/F2%20%28Influent%20Pump%20Station%29.md) | Float switch F2, Eco-Float GP60NONC, non-mercury NO/NC — redundant large lead on at 18.50 | Instrument | New | Inferred | 2 |
| [F3 (Influent Pump Station)](Components/Influent%20Pump%20Station/F3%20%28Influent%20Pump%20Station%29.md) | Float switch F3, Eco-Float GP60NONC, non-mercury NO/NC — redundant small lag on at 18.00 | Instrument | New | Inferred | 2 |
| [F4 (Influent Pump Station)](Components/Influent%20Pump%20Station/F4%20%28Influent%20Pump%20Station%29.md) | Float switch F4, Eco-Float GP60NONC, non-mercury NO/NC — redundant small lead on at 17.50 | Instrument | New | Inferred | 2 |
| [IP-1](Components/Influent%20Pump%20Station/IP-1.md) | Influent Pump No.1, 3 HP, explosion-proof (XP), 4.8 FLA | Pump | Not stated | Verified-Visual | 1 |
| [IP-2](Components/Influent%20Pump%20Station/IP-2.md) | Influent Pump No.2, 3 HP, explosion-proof (XP), 4.8 FLA | Pump | Not stated | Verified-Visual | 2 |
| [IP-3](Components/Influent%20Pump%20Station/IP-3.md) | Influent Pump No.3, 5 HP, explosion-proof (XP), 7.6 FLA | Pump | Not stated | Verified-Visual | 1 |
| [IP-4](Components/Influent%20Pump%20Station/IP-4.md) | Influent Pump No.4, 5 HP, explosion-proof (XP), 7.6 FLA | Pump | Not stated | Verified-Visual | 1 |
| [IPS](Components/Influent%20Pump%20Station/IPS.md) | Influent Pump Station control panel, 480 V 3-ph 3-W, NEMA 4X SS: 60 A main, starters for IP-1 to IP-4, T3 and LP2, Allen-Bradley CompactLogix PLC (1768-ENBT), network switch, flow-meter transmitters | Control panel | New | Unresolved | 5 |
| [LP2](Components/Influent%20Pump%20Station/LP2.md) | Panel LP2 (Influent Pump Station panel), 120/240 V 1-ph 3-W, 100 A bus, 60 A main breaker, 10,000 AIC, surface mounted | Panelboard | New | Inferred | 1 |
| [LT (Influent Pump Station)](Components/Influent%20Pump%20Station/LT%20%28Influent%20Pump%20Station%29.md) | Submersible level transducer: WIKA pressure transmitter, 316 SS, 0–15 psi, LevelGuard, 4–20 mA loop powered, vented, NEMA 4X termination enclosure | Instrument | New | Unresolved | 1 |
| [T3](Components/Influent%20Pump%20Station/T3.md) | Transformer T3, 10 kVA, 480–120/240V (inside IPS panel; feeds LP2) | Transformer | New | Inferred | 0 |
| [PROPOSED-Influent-Flow-Meter](Components/Influent%20Pump%20Station/PROPOSED-Influent-Flow-Meter.md) | Influent magnetic flow meter, Endress+Hauser Promag W400, Class I Div 2, EtherNet/IP, remote transmitter at the IPS panel, two 316L grounding rings | Flow meter | New | Inferred | 0 |
| [PROPOSED-Influent-Pump-Local-Disconnects](Components/Influent%20Pump%20Station/PROPOSED-Influent-Pump-Local-Disconnects.md) | Influent pump motor local disconnects (4) on the building wall within sight of the wet well; outdoor enclosures lockable Type 316 SS with drip shields | Disconnect switch | New | Verified-Visual | 0 |
| [PROPOSED-Influent-Pump-Seal-Fail-Overtemp-Relays](Components/Influent%20Pump%20Station/PROPOSED-Influent-Pump-Seal-Fail-Overtemp-Relays.md) | Influent pump seal-fail and overtemperature relays (4), Mini-CAS or equal, furnished by the pump manufacturer, installed in the IPS panel | Relay modules | New | Inferred | 0 |
| [PROPOSED-Influent-Sampler](Components/Influent%20Pump%20Station/PROPOSED-Influent-Sampler.md) | Influent sampler (Owner-furnished, contractor-installed); 120 V GFCI receptacle LP2-8 and 4–20 mA flow pace | Sampler | Not stated | Verified-Visual | 1 |
| [PROPOSED-Influent-Wet-Well-Instrument-Handhole](Components/Influent%20Pump%20Station/PROPOSED-Influent-Wet-Well-Instrument-Handhole.md) | Influent wet well instrumentation handhole, precast, traffic rated, solid bottom with sump and drain | Handhole | New | Verified-Visual | 0 |
| [PROPOSED-Influent-Wet-Well-Power-Handhole](Components/Influent%20Pump%20Station/PROPOSED-Influent-Wet-Well-Power-Handhole.md) | Influent wet well pump power handhole, precast, traffic rated, solid bottom with sump and drain | Handhole | New | Verified-Visual | 0 |
| [PROPOSED-Plant-2-Flow-Meter](Components/Influent%20Pump%20Station/PROPOSED-Plant-2-Flow-Meter.md) | Plant 2 magnetic flow meter ("Train #2 flow meter" on E7.0), Promag W400, remote transmitter at the IPS panel | Flow meter | New | Inferred | 0 |
| [PROPOSED-Plant-3-Flow-Meter](Components/Influent%20Pump%20Station/PROPOSED-Plant-3-Flow-Meter.md) | Plant 3 magnetic flow meter ("Train #3 flow meter" on E7.0), Promag W400, remote transmitter at the IPS panel | Flow meter | New | Inferred | 0 |
| [PROPOSED-Plant-Drain-Flow-Meter](Components/Influent%20Pump%20Station/PROPOSED-Plant-Drain-Flow-Meter.md) | Plant drain magnetic flow meter, Promag W400, remote transmitter at the IPS panel | Flow meter | New | Inferred | 0 |

### Treatment Building (19)

| Component | Name | Type | Status | Tag level | Open items |
|---|---|---|---|---|---|
| [DW-1](Components/Treatment%20Building/DW-1.md) | Dewatering skid with skid control panel DW-1: pre-wired and factory tested, UL/ETL labeled per WA L&I, 15 HP, 480 V 3-ph; skid PLC, operator interface and network switch | Process equipment package | New | Verified-Visual | 0 |
| [EF-3](Components/Treatment%20Building/EF-3.md) | Exhaust Fan EF-3, Treatment Building, motor marked 1/2, circuit LP2-7 (1,127 VA) | Fan | New | Inferred | 2 |
| [EF-4](Components/Treatment%20Building/EF-4.md) | Exhaust Fan EF-4, Treatment Building, motor marked 1/2, circuit LP2-9 (1,127 VA) | Fan | New | Inferred | 2 |
| [EF-5](Components/Treatment%20Building/EF-5.md) | Exhaust Fan EF-5, Treatment Building, motor marked 1/2, circuit LP2-11 (1,127 VA) | Fan | New | Inferred | 2 |
| [L2 (Treatment Building)](Components/Treatment%20Building/L2%20%28Treatment%20Building%29.md) | Light fixture type L2 wall packs on circuit LP2-3 ("wall pack lighting", 500 VA) | Lighting | New | Inferred | 0 |
| [SD-1](Components/Treatment%20Building/SD-1.md) | Sludge pump, 3 HP, VFD in MCC | Pump | Not stated | Verified-Visual | 0 |
| [TPS](Components/Treatment%20Building/TPS.md) | Panel TPS, 208Y/120V 3-ph 4-W, 200 A (kept; re-fed) | Panelboard | Existing | Verified | 0 |
| [WP-1](Components/Treatment%20Building/WP-1.md) | WAS Pump No.1, 3 HP, VFD in MCC | Pump | Not stated | Verified-Visual | 0 |
| [WP-2](Components/Treatment%20Building/WP-2.md) | WAS Pump No.2 / swing pump, 3 HP, VFD in MCC | Pump | Not stated | Verified-Visual | 0 |
| [PROPOSED-Gas-Alarm-Light-and-Horn](Components/Treatment%20Building/PROPOSED-Gas-Alarm-Light-and-Horn.md) | Local alarm light and horn for ventilation and gas monitoring, Treatment Building | Alarm device | New | Verified-Visual | 0 |
| [PROPOSED-H2S-Sensor](Components/Treatment%20Building/PROPOSED-H2S-Sensor.md) | Hydrogen sulfide (H2S) sensor, Treatment Building, circuit LP2-2 (500 VA) | Instrument | New | Verified-Visual | 0 |
| [PROPOSED-Methane-Sensor](Components/Treatment%20Building/PROPOSED-Methane-Sensor.md) | Methane gas sensor, Treatment Building, circuit LP2-4 (500 VA) | Instrument | New | Verified-Visual | 0 |
| [PROPOSED-Polymer-Feed-Pump](Components/Treatment%20Building/PROPOSED-Polymer-Feed-Pump.md) | Polymer feed pump at the dewatering skid; 120 V GFCI receptacle LP2-6 and 4–20 mA flow pace | Pump | Not stated | Verified-Visual | 0 |
| [PROPOSED-Treatment-Building-Control-Signal-Handhole](Components/Treatment%20Building/PROPOSED-Treatment-Building-Control-Signal-Handhole.md) | Electric control and signal handhole at the Treatment Building / IPS panel location | Handhole | New | Verified | 0 |
| [PROPOSED-Treatment-Building-Power-Handhole](Components/Treatment%20Building/PROPOSED-Treatment-Building-Power-Handhole.md) | Electric power handhole at the Treatment Building / IPS panel location | Handhole | New | Verified | 0 |
| [PROPOSED-Treatment-Building-Ventilation-Control-Panel](Components/Treatment%20Building/PROPOSED-Treatment-Building-Ventilation-Control-Panel.md) | Ventilation control panel, Treatment Building, NEMA 4X stainless steel | Control panel | New | Unresolved | 2 |
| [PROPOSED-WAS-and-Sludge-Pump-Local-Disconnects](Components/Treatment%20Building/PROPOSED-WAS-and-Sludge-Pump-Local-Disconnects.md) | Local motor disconnects for WP-1, WP-2 and SD-1 (3) | Disconnect switch | New | Inferred | 0 |
| [PROPOSED-WAS-Dewatering-Flow-Meter](Components/Treatment%20Building/PROPOSED-WAS-Dewatering-Flow-Meter.md) | Dewatering flow meter ("WAS flow meter" on E7.0), Promag W400 with local display, Cat 6 to the IPS panel | Flow meter | New | Inferred | 0 |
| [PROPOSED-WAS-Solenoid-Valves](Components/Treatment%20Building/PROPOSED-WAS-Solenoid-Valves.md) | WAS solenoid valves (3), WAS #1 to #3, 120 V from the IPS panel | Valve and solenoid | Not stated | Verified-Visual | 0 |

### 2W Pump Station (12)

| Component | Name | Type | Status | Tag level | Open items |
|---|---|---|---|---|---|
| [2W-P1](Components/2W%20Pump%20Station/2W-P1.md) | 2W Water Pump No.1, 5 HP, VFD in MCC (E4.3 tags it P-2W-1) | Pump | Not stated | Unresolved | 1 |
| [2W-P2](Components/2W%20Pump%20Station/2W-P2.md) | 2W Water Pump No.2, 5 HP, VFD in MCC (E4.3 tags it P-2W-2) | Pump | Not stated | Unresolved | 1 |
| [F2 (2W Pump Station)](Components/2W%20Pump%20Station/F2%20%282W%20Pump%20Station%29.md) | 2W float F2: valve close at 20.00 (factory float tree) | Instrument | New | Verified-Visual | 0 |
| [F3 (2W Pump Station)](Components/2W%20Pump%20Station/F3%20%282W%20Pump%20Station%29.md) | 2W float F3: valve open at 19.00 (factory float tree) | Instrument | New | Verified-Visual | 0 |
| [LSH-111](Components/2W%20Pump%20Station/LSH-111.md) | 2W float F1: high level alarm and redundant valve close at 22.00 (factory float tree) | Instrument | New | Verified-Visual | 0 |
| [LSL-111](Components/2W%20Pump%20Station/LSL-111.md) | 2W float F4: low level alarm and pumps off at 15.00 (factory float tree) | Instrument | New | Verified-Visual | 0 |
| [PROPOSED-2W-Flow-Meter](Components/2W%20Pump%20Station/PROPOSED-2W-Flow-Meter.md) | 2W flow meter, 1-in Promag W400, 24 VAC/DC, EtherNet/IP, local display, NEMA 4X, in Hot Box #1 | Flow meter | New | Inferred | 0 |
| [PROPOSED-2W-Isolation-Valve-Solenoid](Components/2W%20Pump%20Station/PROPOSED-2W-Isolation-Valve-Solenoid.md) | Isolation valve solenoid in Hot Box #1 (2W line) | Valve and solenoid | Not stated | Verified-Visual | 0 |
| [PROPOSED-2W-Pump-Local-Disconnects](Components/2W%20Pump%20Station/PROPOSED-2W-Pump-Local-Disconnects.md) | Local motor disconnects for the two 2W pumps (2) | Disconnect switch | New | Inferred | 0 |
| [PROPOSED-Hot-Box-1](Components/2W%20Pump%20Station/PROPOSED-Hot-Box-1.md) | Hot Box #1 (2W): houses the 1-in 2W flow meter, isolation valve solenoid, heat trace, GFEP and J-box | Enclosure (hot box) | Not stated | Unresolved | 1 |
| [PROPOSED-Hot-Box-2](Components/2W%20Pump%20Station/PROPOSED-Hot-Box-2.md) | Hot Box #2 (2W): heat trace on exposed piping | Enclosure (hot box) | Not stated | Unresolved | 1 |
| [PROPOSED-Hot-Box-Heat-Trace](Components/2W%20Pump%20Station/PROPOSED-Hot-Box-Heat-Trace.md) | Heat trace on all exposed 2W piping in Hot Boxes #1 and #2: Raychem BTV self-regulating or equal, dedicated 120 V 20 A GFEP circuits (LP1-10, LP1-12), NEMA 4X thermostat, end-of-line kit with indicator light | Heat trace | New | Verified | 1 |

### UV Disinfection Chamber and Digester (10)

| Component | Name | Type | Status | Tag level | Open items |
|---|---|---|---|---|---|
| [UV1](Components/UV%20Disinfection%20Chamber%20and%20Digester/UV1.md) | UV disinfection unit No.1 (UV modules on 10-ft cords, 2 per PDR) | UV equipment | New | Inferred | 0 |
| [UV2](Components/UV%20Disinfection%20Chamber%20and%20Digester/UV2.md) | UV disinfection unit No.2 (UV modules on 10-ft cords, 2 per PDR) | UV equipment | New | Inferred | 0 |
| [PROPOSED-Digester-Level-Transducer](Components/UV%20Disinfection%20Chamber%20and%20Digester/PROPOSED-Digester-Level-Transducer.md) | Digester level transducer: WIKA submersible, 316 SS, 0–15 psi, LevelGuard, 4–20 mA, vented, desiccant, NEMA 4X; J-box with terminals and desiccant on the handrail | Instrument | New | Unresolved | 1 |
| [PROPOSED-Effluent-Flow-Meter](Components/UV%20Disinfection%20Chamber%20and%20Digester/PROPOSED-Effluent-Flow-Meter.md) | Effluent magnetic flow meter in vault, Promag W400, remote housing, IP68 Type 6 potted submersible sensor, two 316L grounding rings | Flow meter | New | Inferred | 1 |
| [PROPOSED-Effluent-Flow-Meter-Transmitter-Panel](Components/UV%20Disinfection%20Chamber%20and%20Digester/PROPOSED-Effluent-Flow-Meter-Transmitter-Panel.md) | Effluent flow meter transmitter panel: stainless local control panel with the transmitter and instrument terminals, on handrail or rack with SS hardware | Control panel | New | Verified | 0 |
| [PROPOSED-UV-Area-Pole-Light](Components/UV%20Disinfection%20Chamber%20and%20Digester/PROPOSED-UV-Area-Pole-Light.md) | UV-area pole light: 4-in square aluminum pole 12 ft on a concrete base secured to the basin side, photocell, local on/off switch, WP/GFCI receptacle; Lithonia "#DXS0-LED-P3-30K-T3M-MVOLT-SPA-DNAXD" (as printed) or equal | Lighting | New | Unresolved | 1 |
| [PROPOSED-UV-Control-Panel-1](Components/UV%20Disinfection%20Chamber%20and%20Digester/PROPOSED-UV-Control-Panel-1.md) | UV control panel 1 (UV system controller), furnished with the UV system, installed by the contractor | Control panel | New | Inferred | 0 |
| [PROPOSED-UV-Control-Panel-2](Components/UV%20Disinfection%20Chamber%20and%20Digester/PROPOSED-UV-Control-Panel-2.md) | UV control panel 2 (UV system controller), furnished with the UV system, installed by the contractor | Control panel | New | Inferred | 0 |
| [PROPOSED-UV-Power-Distribution-1](Components/UV%20Disinfection%20Chamber%20and%20Digester/PROPOSED-UV-Power-Distribution-1.md) | UV power distribution 1: stainless splitter panel within 10 ft of the module power end, wiring gutter, J-boxes and (3) duplex GFCI power distribution receptacles (PDRs) with in-use wet-location covers on SS Unistrut; SS conduit and fittings | Power distribution | New | Verified-Visual | 0 |
| [PROPOSED-UV-Power-Distribution-2](Components/UV%20Disinfection%20Chamber%20and%20Digester/PROPOSED-UV-Power-Distribution-2.md) | UV power distribution 2: stainless splitter panel within 10 ft of the module power end, wiring gutter, J-boxes and (3) duplex GFCI power distribution receptacles (PDRs) with in-use wet-location covers on SS Unistrut; SS conduit and fittings | Power distribution | New | Verified-Visual | 0 |

### Existing Office-Lab-Shop Building (2)

| Component | Name | Type | Status | Tag level | Open items |
|---|---|---|---|---|---|
| [PROPOSED-Existing-208V-400A-Distribution-Panel](Components/Existing%20Office-Lab-Shop%20Building/PROPOSED-Existing-208V-400A-Distribution-Panel.md) | Existing 208Y/120V 400 A distribution panel (Square-D I-Line), Office Building, re-fed from transformer TS | Panelboard | Existing | Inferred | 0 |
| [PROPOSED-SCADA-Computer-System](Components/Existing%20Office-Lab-Shop%20Building/PROPOSED-SCADA-Computer-System.md) | SCADA computer system with Cat 6 network junction box, combo network/telephone outlet and SCADA alarm dialer connection | Control system | New | Verified-Visual | 0 |

### Site-wide and multi-area (3)

| Component | Name | Type | Status | Tag level | Open items |
|---|---|---|---|---|---|
| [PROPOSED-Conduit-and-Conductor-Runs](Components/Site-wide%20and%20multi-area/PROPOSED-Conduit-and-Conductor-Runs.md) | Conduit and conductor runs per the E6.3 schedules: 40 named power runs (+2 unnamed UV controller circuits, AC spare) and 38 named 24 VDC control/signal runs (+DC spare) | Raceway and feeder | New | Inferred | 1 |
| [PROPOSED-Electrical-Equipment-Housekeeping-Pads](Components/Site-wide%20and%20multi-area/PROPOSED-Electrical-Equipment-Housekeeping-Pads.md) | Concrete housekeeping pads under floor-mounted electrical equipment (MCC, main PLC panel, IPS panel) | Concrete pads | New | Inferred | 0 |
| [PROPOSED-Existing-200A-Feeder-to-Panel-TPS](Components/Site-wide%20and%20multi-area/PROPOSED-Existing-200A-Feeder-to-Panel-TPS.md) | Existing 200 A 208Y/120V power feeder to Panel TPS | Raceway and feeder | Demolished | Verified | 0 |

### Area not stated (5)

| Component | Name | Type | Status | Tag level | Open items |
|---|---|---|---|---|---|
| [DB](Components/Area%20not%20stated/DB.md) | Digester blower, 5 HP, VFD in MCC | Blower | Not stated | Inferred | 0 |
| [PROPOSED-Construction-Power-Service](Components/Area%20not%20stated/PROPOSED-Construction-Power-Service.md) | Dedicated construction power service (contractor-provided, contractor-paid energy) | Temporary power | Temporary | Verified | 0 |
| [PROPOSED-DB-Local-Disconnect](Components/Area%20not%20stated/PROPOSED-DB-Local-Disconnect.md) | Local disconnect for digester blower DB, NEMA 4X stainless steel | Disconnect switch | New | Verified-Visual | 0 |
| [PROPOSED-Effluent-Sampler](Components/Area%20not%20stated/PROPOSED-Effluent-Sampler.md) | Effluent sampler (Owner-furnished, contractor-installed); 120 V GFCI receptacle on LP1-14 and 4–20 mA flow pace | Sampler | Not stated | Verified-Visual | 1 |
| [PROPOSED-Hypochlorite-Feed-Pump](Components/Area%20not%20stated/PROPOSED-Hypochlorite-Feed-Pump.md) | Hypochlorite feed pump; 120 V GFCI receptacle on LP1-16 and 4–20 mA flow pace | Pump | Not stated | Verified-Visual | 0 |

