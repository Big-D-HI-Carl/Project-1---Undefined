# PROPOSED-DIGESTED-SLUDGE-PUMP — Digested sludge pump, packaged sludge pump, 3 HP

Component ID: PROPOSED-DIGESTED-SLUDGE-PUMP | Type: Equipment (derived from name) | Discipline: Process-Mechanical | Revision/Date: Add. 4 p.2, 22 13 36 ¶2.01 A (pumps powered from VFDs in the MCC, controlled by the PLC in the Main Control Panel; no local speed dial) — Add. 4 governs

Summary: Digested sludge pump, packaged sludge pump, 3 HP. New · Equipment · Sludge Pump and Valving Area · Process-Mechanical. Shown on G0.5, G0.6, G0.7, C6.2; specified in 22 13 36, 46 76 26. Bid Item 1; 6; submittal required; testing/start-up required; Add. 4 p.2, 22 13 36 ¶2.01 A (pumps powered from VFDs in the MCC, controlled by the PLC in the Main Control Panel; no local speed dial) — Add. 4 governs. Ledger tag Unresolved (driver: Issue 36); open issues #21, #36.

Tags: Area — Sludge Pump and Valving Area · Status — New · Bid Item — 1; 6 · Sheets — G0.5, G0.6, G0.7, C6.2 · Spec sections — 22 13 36; 46 76 26 · Addenda — Add. 4 p.2, 22 13 36 ¶2.01 A (pumps powered from VFDs in the MCC, controlled by the PLC in the Main Control Panel; no local speed dial) — Add. 4 governs

Related documents: Wiki notes C6.2; G0.7; 22 13 36; 46 76 26 (Process_and_Mechanical_Wiki.md); page files sheets/G0.5_Process_Schematic.md, sheets/G0.6_Hydraulic_Profile.md, sheets/G0.7_Design_Criteria.md, sheets/C6.2_Sludge_Pump_and_Valving_Area.md, spec_sections/22_13_36_Packaged_Sludge_Pumps.md, spec_sections/46_76_26_Rotary_Fan_Press_System.md (Process_and_Mechanical_Components_by_Page.zip)

Where it lives: Ledger row "PROPOSED-DIGESTED-SLUDGE-PUMP" in Process_and_Mechanical_Ledger.csv · Ledger tag Unresolved

## Where it appears

| Page | Title | Citation on that page |
|---|---|---|
| G0.5 | Process Schematic | see Sources |
| G0.6 | Hydraulic Profile | plans_1 p.6 (G0.6 proposed WAS and sludge pump equipment) |
| G0.7 | Design Criteria | plans_1 p.7 (G0.7 hose pumps, 1 duty + 1 swing standby each for WAS and digester, 0-40 gpm) |
| C6.2 | Sludge Pump and Valving Area | plans_5 p.7 (C6.2, keyed note 8, per 22 13 36; pump labels 3HP) |
| 22 13 36 | Packaged Sludge Pumps | main spec pp.263-264 (22 13 36 ¶1.01 A, ¶1.02 A, ¶2.01 A base, ¶2.02, ¶2.03, ¶3.02) |
| 46 76 26 | Rotary Fan Press System | main spec pp.510-531 (46 76 26 ¶1.7; ¶4.1) |
| Other | Addenda and cross-references | Add. 4 p.2 |

## Lifecycle checklist

| Stage | What the documents say |
|---|---|
| Procure | Spec: 22 13 36, 46 76 26; submittal Y; Bid Item 1; 6 |
| Install | Area: Sludge Pump and Valving Area; sheets: G0.5, G0.6, G0.7, C6.2; status: New |
| Test and start-up | Testing/start-up Y (P&M stack) |
| Governing addendum | Add. 4 p.2, 22 13 36 ¶2.01 A (pumps powered from VFDs in the MCC, controlled by the PLC in the Main Control Panel; no local speed dial) — Add. 4 governs |

## Requirements and notes (sentences from the Ledger Notes, grouped by keyword)

**Open items and conflicts**
- 22 13 36: Edson Platinum peristaltic or equal, 3 HP 460 V 3-phase, 0-43 gpm (G0.7 says 0-40, Issue 21), set point 10-30 gpm; 304 SS enclosure about 40x40x40 in. per pump; 3 sets of wear parts; 2 days start-up and field testing; 1 day training; controls per 26 80 00 ¶3.09 A and H.
- 46 76 26 has the press control system set this pump's speed to hold flocculator inlet pressure (Issue 36).

**Controls and electrical interface**
- Bid Item 1 pumps and 6 VFDs in the MCC per 04 Add. 4 table.
- Base ¶2.01 A "Each pump is to include a VFD" replaced by Add. 4 p.2.

**Description and design data**
- Role: duty digested sludge.

## Open items

- Issue 21 — Sludge pump capacity 0–40 vs 0–43 gpm (low) · Governs: Unresolved (low impact; set points 10–30 gpm fall inside both). · Needed: None unless the pump selection is at its limit.
- Issue 36 — Who sets the digested sludge pump speed · Governs: Add. 4 governs the VFD location (MCC); which PLC commands the digested sludge pump speed is Unresolved. · Needed: Electrical & Controls to confirm the control interface between the press PLC and the main PLC (26 80 00 ¶3.09 H, not in this stack).
- Ledger tag driver: Issue 36.

## Cross-lane

- Cross-lane: Electrical & Controls (VFDs, MCC, PLC).

## Related components (Inferred: same area plus a shared spec section or detail sheet)

- [PROPOSED-SWING-SLUDGE-PUMP](../Sludge_Pump_and_Valving_Area/PROPOSED_SWING_SLUDGE_PUMP.md)
- [PROPOSED-WAS-PUMP](../Sludge_Pump_and_Valving_Area/PROPOSED_WAS_PUMP.md)
- [PROPOSED-SLUDGE-PUMP-LOCAL-PANELS](../Sludge_Pump_and_Valving_Area/PROPOSED_SLUDGE_PUMP_LOCAL_PANELS.md)
- [PROPOSED-SLUDGE-MANIFOLD-PIPING](../Sludge_Pump_and_Valving_Area/PROPOSED_SLUDGE_MANIFOLD_PIPING.md)
- [PROPOSED-WAS-FLOW-METER](../Sludge_Pump_and_Valving_Area/PROPOSED_WAS_FLOW_METER.md)
- [PROPOSED-WAS-SOLENOID-VALVES](../Sludge_Pump_and_Valving_Area/PROPOSED_WAS_SOLENOID_VALVES.md)

## Sources

- plans_5 p.7 (C6.2, keyed note 8, per 22 13 36; pump labels 3HP)
- plans_1 p.7 (G0.7 hose pumps, 1 duty + 1 swing standby each for WAS and digester, 0-40 gpm)
- plans_1 p.6 (G0.6 proposed WAS and sludge pump equipment)
- Add. 4 p.2
- main spec pp.263-264 (22 13 36 ¶1.01 A, ¶1.02 A, ¶2.01 A base, ¶2.02, ¶2.03, ¶3.02)
- main spec pp.510-531 (46 76 26 ¶1.7; ¶4.1)
