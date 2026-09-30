# Civil & Site — Component Wiki

Eastsound WWTP Upgrade Phase I · Civil & Site lane · one page per Ledger row, as of Sep 30, 2026.

## How these pages are built

- Front matter and the Ledger row come straight from Civil_and_Site_Ledger.csv.
- 'Where it's shown' parses the Ledger's Drawing Sheets column and links to the page files in Civil_and_Site_Pages. Extract both zips into the same folder so links resolve.
- 'What the documents require' pulls requirements from the spec sections on the Ledger row, filtered by component class. Class comes from the drawing legend or Ledger name (for example, 'DI GRAV.' on C1.3 makes a gravity sewer). Every requirement carries its paragraph, page and tag.
- Extrapolated content is labeled: 10 requirements come from sections that apply by their own scope but aren't on the Ledger row (storm sewer removal, wall design basis, groundwater data, Appendix F interim operation). They're marked Inferred at the heading.
- Related components and issue links are curated from the drawings, keyed notes and the Issues file; inferred links say so.
- Priorities and fixes live in Civil_and_Site_Known_Issues.md; submittal and testing flags follow the spec-section rule (Issues CS-37).

## Lane-wide issues not repeated on every page

- CS-23, CS-24, CS-28 — trench backfill, compaction and tracer wire; noted on every buried-work page.
- CS-32 — who provides construction staking; applies to all new site work.
- CS-37 — submittal and testing flags count spec requirements only.

## Index (115 components)

### Demolition and relocation (20)

| Component | Status | Tag level | Issues |
|---|---|---|---|
| [PROPOSED-Asphalt pavement sawcut and removal](PROPOSED-Asphalt_pavement_sawcut_and_removal.md) | Demolished | Unresolved | 0 |
| [PROPOSED-Existing 1.5in sump force main](PROPOSED-Existing_1.5in_sump_force_main.md) | Demolished | Inferred | 1 |
| [PROPOSED-Existing 10in effluent outfall pipe](PROPOSED-Existing_10in_effluent_outfall_pipe.md) | Demolished | Inferred | 0 |
| [PROPOSED-Existing 4in roof drain pipe](PROPOSED-Existing_4in_roof_drain_pipe.md) | Demolished | Inferred | 0 |
| [PROPOSED-Existing 4in storm drain 8 LF](PROPOSED-Existing_4in_storm_drain_8_LF.md) | Demolished | Inferred | 0 |
| [PROPOSED-Existing 6in drain pipe to sump station](PROPOSED-Existing_6in_drain_pipe_to_sump_station.md) | Demolished | Inferred | 1 |
| [PROPOSED-Existing 8in effluent outfall pipe](PROPOSED-Existing_8in_effluent_outfall_pipe.md) | Demolished | Inferred | 0 |
| [PROPOSED-Existing 8in influent pipe](PROPOSED-Existing_8in_influent_pipe.md) | Demolished | Inferred | 1 |
| [PROPOSED-Existing 8in slab over pre-aeration basin](PROPOSED-Existing_8in_slab_over_pre-aeration_basin.md) | Demolished | Inferred | 1 |
| [PROPOSED-Existing Train 1 influent pipe](PROPOSED-Existing_Train_1_influent_pipe.md) | Existing | Inferred | 0 |
| [PROPOSED-Existing basin internal piping](PROPOSED-Existing_basin_internal_piping.md) | Demolished | Inferred | 1 |
| [PROPOSED-Existing chain link fence 119 LF](PROPOSED-Existing_chain_link_fence_119_LF.md) | Demolished | Inferred | 0 |
| [PROPOSED-Existing chain link fence 149 LF](PROPOSED-Existing_chain_link_fence_149_LF.md) | Demolished | Inferred | 0 |
| [PROPOSED-Existing generator fuel tank and spill basin](PROPOSED-Existing_generator_fuel_tank_and_spill_basin.md) | Demolished | Inferred | 1 |
| [PROPOSED-Existing holding tanks](PROPOSED-Existing_holding_tanks.md) | Existing | Inferred | 0 |
| [PROPOSED-Existing retaining wall 61 LF](PROPOSED-Existing_retaining_wall_61_LF.md) | Demolished | Inferred | 0 |
| [PROPOSED-Existing storm drain and catch basin 87 LF](PROPOSED-Existing_storm_drain_and_catch_basin_87_LF.md) | Demolished | Inferred | 1 |
| [PROPOSED-Existing storm drain at roof drain 7 ft](PROPOSED-Existing_storm_drain_at_roof_drain_7_ft.md) | Demolished | Inferred | 0 |
| [SSMH 1285](SSMH_1285.md) | Demolished | Inferred | 0 |
| [SSMH 1286](SSMH_1286.md) | Demolished | Inferred | 1 |

### Buried piping (32)

| Component | Status | Tag level | Issues |
|---|---|---|---|
| [PROPOSED-4in roof drain at SD-1](PROPOSED-4in_roof_drain_at_SD-1.md) | New | Inferred | 0 |
| [PROPOSED-Gravity sewer cleanouts](PROPOSED-Gravity_sewer_cleanouts.md) | New | Inferred | 0 |
| [PROPOSED-Interim 8in HDPE effluent pipe](PROPOSED-Interim_8in_HDPE_effluent_pipe.md) | Temporary | Unresolved | 0 |
| [PROPOSED-Post hydrant](PROPOSED-Post_hydrant.md) | New | Unresolved | 1 |
| [PROPOSED-Water line relocation at storm drain](PROPOSED-Water_line_relocation_at_storm_drain.md) | Not stated | Inferred | 0 |
| [Pipe ID 1](Pipe_ID_1.md) | Existing | Inferred | 0 |
| [Pipe ID 10](Pipe_ID_10.md) | New | Inferred | 1 |
| [Pipe ID 11](Pipe_ID_11.md) | New | Inferred | 1 |
| [Pipe ID 12](Pipe_ID_12.md) | New | Unresolved | 1 |
| [Pipe ID 13](Pipe_ID_13.md) | New | Inferred | 1 |
| [Pipe ID 14](Pipe_ID_14.md) | New | Inferred | 0 |
| [Pipe ID 15](Pipe_ID_15.md) | New | Unresolved | 1 |
| [Pipe ID 16](Pipe_ID_16.md) | New | Inferred | 0 |
| [Pipe ID 17](Pipe_ID_17.md) | New | Inferred | 0 |
| [Pipe ID 18](Pipe_ID_18.md) | New | Inferred | 0 |
| [Pipe ID 19](Pipe_ID_19.md) | New | Unresolved | 1 |
| [Pipe ID 2](Pipe_ID_2.md) | New | Inferred | 0 |
| [Pipe ID 20](Pipe_ID_20.md) | New | Unresolved | 1 |
| [Pipe ID 21](Pipe_ID_21.md) | New | Unresolved | 1 |
| [Pipe ID 22](Pipe_ID_22.md) | New | Unresolved | 3 |
| [Pipe ID 23](Pipe_ID_23.md) | New | Inferred | 1 |
| [Pipe ID 24](Pipe_ID_24.md) | New | Inferred | 0 |
| [Pipe ID 25](Pipe_ID_25.md) | New | Inferred | 0 |
| [Pipe ID 26](Pipe_ID_26.md) | New | Inferred | 0 |
| [Pipe ID 3](Pipe_ID_3.md) | New | Inferred | 0 |
| [Pipe ID 4](Pipe_ID_4.md) | New | Inferred | 0 |
| [Pipe ID 5](Pipe_ID_5.md) | New | Inferred | 0 |
| [Pipe ID 6](Pipe_ID_6.md) | New | Inferred | 0 |
| [Pipe ID 7](Pipe_ID_7.md) | New | Inferred | 0 |
| [Pipe ID 8](Pipe_ID_8.md) | New | Inferred | 0 |
| [Pipe ID 9](Pipe_ID_9.md) | New | Inferred | 0 |
| [SD-1](SD-1.md) | New | Unresolved | 2 |

### Valves and markers (14)

| Component | Status | Tag level | Issues |
|---|---|---|---|
| [Buried Valve ID 1](Buried_Valve_ID_1.md) | New | Inferred | 0 |
| [Buried Valve ID 10](Buried_Valve_ID_10.md) | New | Unresolved | 1 |
| [Buried Valve ID 11](Buried_Valve_ID_11.md) | New | Unresolved | 1 |
| [Buried Valve ID 12](Buried_Valve_ID_12.md) | New | Unresolved | 1 |
| [Buried Valve ID 13](Buried_Valve_ID_13.md) | New | Unresolved | 1 |
| [Buried Valve ID 2](Buried_Valve_ID_2.md) | New | Unresolved | 1 |
| [Buried Valve ID 3](Buried_Valve_ID_3.md) | New | Unresolved | 1 |
| [Buried Valve ID 4](Buried_Valve_ID_4.md) | New | Inferred | 0 |
| [Buried Valve ID 5](Buried_Valve_ID_5.md) | New | Inferred | 0 |
| [Buried Valve ID 6](Buried_Valve_ID_6.md) | New | Unresolved | 1 |
| [Buried Valve ID 7](Buried_Valve_ID_7.md) | New | Unresolved | 1 |
| [Buried Valve ID 8](Buried_Valve_ID_8.md) | New | Unresolved | 1 |
| [Buried Valve ID 9](Buried_Valve_ID_9.md) | New | Unresolved | 1 |
| [PROPOSED-Buried valve label markers](PROPOSED-Buried_valve_label_markers.md) | New | Unresolved | 2 |

### Storm drainage (13)

| Component | Status | Tag level | Issues |
|---|---|---|---|
| [PROPOSED-East trench drains](PROPOSED-East_trench_drains.md) | New | Inferred | 0 |
| [PROPOSED-Retaining wall footing drain](PROPOSED-Retaining_wall_footing_drain.md) | New | Unresolved | 1 |
| [PROPOSED-West trench drain](PROPOSED-West_trench_drain.md) | New | Inferred | 0 |
| [SDCB #10](SDCB_10.md) | New | Unresolved | 0 |
| [SDCB #2](SDCB_2.md) | New | Unresolved | 0 |
| [SDCB #3](SDCB_3.md) | New | Unresolved | 0 |
| [SDCB #4](SDCB_4.md) | New | Unresolved | 0 |
| [SDCB #5](SDCB_5.md) | New | Unresolved | 0 |
| [SDCB #6](SDCB_6.md) | New | Unresolved | 0 |
| [SDCB #7](SDCB_7.md) | New | Unresolved | 0 |
| [SDCB #8](SDCB_8.md) | New | Unresolved | 0 |
| [SDCB #9](SDCB_9.md) | New | Unresolved | 0 |
| [SDCB 1076](SDCB_1076.md) | Existing | Inferred | 0 |

### Structures and vaults (7)

| Component | Status | Tag level | Issues |
|---|---|---|---|
| [PROPOSED-Block retaining wall](PROPOSED-Block_retaining_wall.md) | New | Unresolved | 2 |
| [PROPOSED-Composite manholes, double manhole condition](PROPOSED-Composite_manholes_double_manhole_condition.md) | New | Unresolved | 0 |
| [PROPOSED-Existing slab coring and repair](PROPOSED-Existing_slab_coring_and_repair.md) | Existing | Inferred | 0 |
| [PROPOSED-Influent sample sump](PROPOSED-Influent_sample_sump.md) | New | Inferred | 0 |
| [PROPOSED-New septic tank](PROPOSED-New_septic_tank.md) | New | Inferred | 0 |
| [PROPOSED-Train 2 flow meter vault](PROPOSED-Train_2_flow_meter_vault.md) | New | Inferred | 2 |
| [PROPOSED-Train 3 flow meter vault](PROPOSED-Train_3_flow_meter_vault.md) | New | Inferred | 2 |

### Site improvements (8)

| Component | Status | Tag level | Issues |
|---|---|---|---|
| [PROPOSED-Chain link fence 126 LF](PROPOSED-Chain_link_fence_126_LF.md) | New | Inferred | 2 |
| [PROPOSED-Concrete walkway](PROPOSED-Concrete_walkway.md) | New | Inferred | 0 |
| [PROPOSED-Gravel surfacing](PROPOSED-Gravel_surfacing.md) | New | Unresolved | 0 |
| [PROPOSED-HMA pavement](PROPOSED-HMA_pavement.md) | New | Unresolved | 1 |
| [PROPOSED-Hydroseeded restoration areas](PROPOSED-Hydroseeded_restoration_areas.md) | New | Unresolved | 1 |
| [PROPOSED-Parking stall striping](PROPOSED-Parking_stall_striping.md) | New | Unresolved | 0 |
| [PROPOSED-Temporary cold-mix patches](PROPOSED-Temporary_cold-mix_patches.md) | Temporary | Inferred | 0 |
| [PROPOSED-WWTP tank and building signs](PROPOSED-WWTP_tank_and_building_signs.md) | New | Inferred | 0 |

### Erosion control (7)

| Component | Status | Tag level | Issues |
|---|---|---|---|
| [PROPOSED-Catch basin inserts](PROPOSED-Catch_basin_inserts.md) | Temporary | Inferred | 0 |
| [PROPOSED-Compost berm](PROPOSED-Compost_berm.md) | Temporary | Unresolved | 0 |
| [PROPOSED-Filter fabric fence](PROPOSED-Filter_fabric_fence.md) | Temporary | Unresolved | 0 |
| [PROPOSED-Geotextile encased check dams](PROPOSED-Geotextile_encased_check_dams.md) | Temporary | Unresolved | 0 |
| [PROPOSED-Orange barrier fence](PROPOSED-Orange_barrier_fence.md) | Temporary | Unresolved | 0 |
| [PROPOSED-Plastic covering for slopes and stockpiles](PROPOSED-Plastic_covering_for_slopes_and_stockpiles.md) | Temporary | Inferred | 0 |
| [PROPOSED-Stabilized construction entrance](PROPOSED-Stabilized_construction_entrance.md) | Temporary | Unresolved | 1 |

### Temporary works (6)

| Component | Status | Tag level | Issues |
|---|---|---|---|
| [PROPOSED-Dewatering system](PROPOSED-Dewatering_system.md) | Temporary | Inferred | 4 |
| [PROPOSED-Off-site staging area](PROPOSED-Off-site_staging_area.md) | Temporary | Inferred | 0 |
| [PROPOSED-Temporary bypass pumping system](PROPOSED-Temporary_bypass_pumping_system.md) | Temporary | Inferred | 0 |
| [PROPOSED-Temporary construction sign](PROPOSED-Temporary_construction_sign.md) | Temporary | Inferred | 0 |
| [PROPOSED-Temporary power generator](PROPOSED-Temporary_power_generator.md) | Temporary | Unresolved | 2 |
| [PROPOSED-Temporary shoring and trench safety systems](PROPOSED-Temporary_shoring_and_trench_safety_systems.md) | Temporary | Inferred | 0 |

### Equipment and instruments (8)

| Component | Status | Tag level | Issues |
|---|---|---|---|
| [Hot Box #1](Hot_Box_1.md) | New | Inferred | 1 |
| [Hot Box #2](Hot_Box_2.md) | New | Inferred | 0 |
| [PROPOSED-Floor drains](PROPOSED-Floor_drains.md) | New | Inferred | 1 |
| [PROPOSED-Hot Box #1 flow meter](PROPOSED-Hot_Box_1_flow_meter.md) | New | Inferred | 1 |
| [PROPOSED-Hot Box #1 solenoid valve](PROPOSED-Hot_Box_1_solenoid_valve.md) | New | Inferred | 1 |
| [PROPOSED-Tracer wire and locater boxes](PROPOSED-Tracer_wire_and_locater_boxes.md) | New | Unresolved | 1 |
| [PROPOSED-Train 2 flow meter](PROPOSED-Train_2_flow_meter.md) | New | Inferred | 1 |
| [PROPOSED-Train 3 flow meter](PROPOSED-Train_3_flow_meter.md) | New | Inferred | 1 |
