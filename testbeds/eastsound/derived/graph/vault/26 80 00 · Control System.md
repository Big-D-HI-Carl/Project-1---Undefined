# 26 80 00 · Control System

- **Node ID:** Spec 26 80 00
- **Node type:** Spec section
- **Lane:** Electrical & Controls
- **Discipline:** Controls
- **Status:** Main spec pp.352–381 · Addendum 4: Add. 4 p.2, ¶2.04 D — Add. 4 governs · Header title differs — see conflict log
- **Confidence:** Verified
- **Wiki note:** 26 80 00
- **Open:** [source page](../../../library/eswd-wwtp-upgrade-phase-i-specs.pdf#page=352)

## Summary

Responsibilities: a system integrator (UL508A panel shop, AVEVA-registered, Allen-Bradley experience) designs, builds, programs and commissions the PLC panels and SCADA; equipment suppliers furnish packaged equipment for installation by the electrical contractor, program and commission it, give PLC tags and IP addresses to the Programmer, and supply UL or ETL labels per Washington L&I (¶1.04–1.05, pp.353–356) [Verified; pages read by key terms]. Major equipment (¶2.02, pp.357–358): MCC with VFDs; PLC panels — main PLC panel with operator interface, influent control panel, effluent flow meter panel, ventilation control panel; four floats each at the 2W and influent pump stations; level and pressure transducers; flow meters matching the E10.2 summary; DO meters; H2S and methane sensors; one heat/smoke detector in the Blower Building [Verified]. Instruments (¶2.04, pp.361–365): Orenco MF or Anchor Eco-Float floats; submersible level transducers; ASCO G2 pressure transducers; Promag L400 in ¶2.04 D, replaced by Promag W400 in Add. 4 p.2 (Add. 4 governs; the E sheets already show W400); Hach LDO probes with SC200 controllers; Sierra Monitor electrochemical H2S sensors; combustible gas detector; combination smoke/heat detector; door intrusion switch [Verified]. PLC and SCADA: Allen-Bradley CompactLogix, PanelView Plus 7 (2711P-T9W22D9P), DC UPS 1606-XLS240-UPS with a 26 Ah battery on every PLC panel, SCADA computer with a 750 VA UPS; after ¶2.05 the numbering restarts at ¶2.01 "SCADA Computer System and Equipment" (p.367) and ¶2.02 "Spare Parts" (p.370), so those are cited by page (pp.365–370) [Verified]. Execution: factory simulation witnessed by the Engineer and Owner before shipment, field acceptance test and operator training by the system integrator, then programming, start-up and commissioning; the description of operation sets sampler flow pace, the UV interface, generator and ATS status, and ventilation control, whose fan logic differs from E9.3 and E8.4 — see Issues (¶3.03–3.04, ¶3.08–3.09, pp.371–381) [Verified].

## Source citation

02 Spec Index rev1 (line 123), main spec pp.352–381; Wiki note 26 80 00 (Project_Wiki.md line 2171)

## Wiki note 26 80 00

- **Type:** Specification section
- **Discipline:** Controls
- **Revision/Date:** Project manual cover dated Dec. 30, 2022 (p.1); Division 26 TOC dated 09/12/2022 (p.268) — per 00 register; section pages 1–30 of 30 = main spec pp.352–381 (Verified). Running header reads "INSTRUMENTATION AND CONTROL"; body SECTION 26 80 00 "CONTROL SYSTEM" governs — 02 log item 6. Add. 4 p.2 revises ¶2.04 D
- **Tags:** control system; system integrator; equipment suppliers; Programmer; MCP; IPS; effluent flow meter panel; ventilation control panel; floats; level and pressure transducers; Promag L400 → W400 (Add. 4); Hach LDO/SC200; H2S sensor; methane sensor; smoke/heat detector; door switch; CompactLogix; PanelView Plus 7; DC UPS; SCADA; system simulation; field acceptance test; description of operation; E7.0–E8.6; E9.3; E10.2; Add. 4 p.2 26 80 00 ¶2.04 D; 02 log item 6
- **Related documents:** E0.3; E2.1; E3.1; E4.1–E4.3; E5.1; E7.0–E7.7; E8.1–E8.6; E9.1–E9.3; E10.2; Add. 4 p.2; 04 Bid Item 17 (SCADA/PLC programmer); 46 66 00 UV (Process & Mechanical stack)
- **Where it lives:** main spec pp.352–381
- **Project Wiki line:** 2165 ([Project_Wiki.md](../../../project/01_Project_Wiki/Project_Wiki.md))

## Neighbours

### Related to

- [[C7.10 · Flow Meter & Valve Vault Details]] (Verified)
- [[E0.3 · Overall Electrical Site Plan]] (Verified)
- [[E4.1 · Influent Pump Station, WAS, Dewatering Electrical Plan]] (Verified)
- [[E4.2 · Influent Pump Station Electrical Plan and Elevation]] (Verified)
- [[E5.1 · UV Disinfection Chamber & Digester Electrical Plan and Elevation]] (Verified)
- [[E7.0 · Control System Overview]] (Verified)
- [[E7.1 · Main PLC Control Panel Elevation]] (Verified)
- [[E7.2 · Main PLC Control Panel — Power Wiring Diagram]] (Verified)
- [[E7.3 · Main PLC Control Panel — Digital Inputs]] (Verified)
- [[E7.4 · Main PLC Control Panel — Digital Outputs]] (Verified)
- [[E7.5 · Main PLC Control Panel — Analog Inputs — Sheet 1]] (Verified)
- [[E7.6 · Main PLC Control Panel — Analog Inputs — Sheet 2]] (Verified)
- [[E7.7 · Main PLC Control Panel — Analog Outputs]] (Verified)
- [[E8.3 · Influent Pump Station Control Panel — Digital Inputs]] (Verified)
- [[E8.4 · Influent Pump Station Control Panel — Digital Outputs]] (Verified)
- [[E8.5 · Influent Pump Station Control Panel — Analog Inputs]] (Verified)
- [[E8.6 · Influent Pump Station Control Panel — Analog Outputs]] (Verified)
- [[E9.3 · Ventilation Control Panel Elevation and Wiring Diagram]] (Verified)
- [[E10.2 · Electrical Details — Sheet 2]] (Verified)

### Specifies

- [[Plant drain flow meter, 4-inch electromagnetic, 0-200 gpm · G0.5 (no tag)]] (Inferred)
- [[DO -1 - DO-1 · Dissolved oxygen - pH sensor, Train 3 Aeration Zone -1]] — also in Wiki note (Unresolved)
- [[DO -2 - DO-2 · Dissolved oxygen - pH sensor, Train 3 Aeration Zone -2]] — also in Wiki note (Unresolved)
- [[MCP · Main Control Panel (PLC), Blower Building]] — also in Wiki note (Unresolved)
- [[Ceiling smoke-heat detector, System Sensor 4WTAR-B · E2.1 (no tag)]] — also in Wiki note (Verified)
- [[Door intrusion switch, magnetic reed SPDT · E2.1 (no tag)]] — also in Wiki note (Verified)
- [[2W system pressure transducer, 0–150 psi, 4–20 mA · E2.1 (no tag)]] — 2 citations; also in Wiki note (Verified)
- [[SCADA computer system with Cat 6 network junction box · E0.3 (no tag)]] (Verified-Visual)
- [[F1 (Influent Pump Station) · Float switch F1, Eco-Float GP60NONC, non-mercury NO-NC]] (Inferred)
- [[F2 (Influent Pump Station) · Float switch F2, Eco-Float GP60NONC, non-mercury NO-NC]] (Inferred)
- [[F3 (Influent Pump Station) · Float switch F3, Eco-Float GP60NONC, non-mercury NO-NC]] (Inferred)
- [[F4 (Influent Pump Station) · Float switch F4, Eco-Float GP60NONC, non-mercury NO-NC]] (Inferred)
- [[LT (Influent Pump Station) · Submersible level transducer- WIKA pressure transmitter]] (Unresolved)
- [[IPS · Influent Pump Station control panel, 480 V 3-ph 3-W]] — also in Wiki note (Unresolved)
- [[Influent magnetic flow meter, Endress+Hauser Promag W400 · E4.1 (no tag)]] (Inferred)
- [[Plant 2 magnetic flow meter, Promag W400 · E4.1 (no tag)]] (Inferred)
- [[Plant 3 magnetic flow meter, Promag W400 · E4.1 (no tag)]] (Inferred)
- [[Dewatering flow meter, Promag W400 with local display · E4.1 (no tag)]] (Inferred)
- [[Effluent magnetic flow meter in vault, Promag W400 · E5.1 (no tag)]] (Inferred)
- [[Effluent flow meter transmitter panel- stainless local… · E5.1 (no tag)]] — also in Wiki note (Verified)
- [[2W flow meter, 1-in Promag W400, 24 VAC-DC, EtherNet-IP · E4.3 (no tag)]] (Inferred)
- [[Ventilation control panel, Treatment Building · E4.1 (no tag)]] — also in Wiki note (Unresolved)
- [[Methane gas sensor, Treatment Building, circuit LP2-4 · E4.1 (no tag)]] — also in Wiki note (Verified-Visual)
- [[Hydrogen sulfide sensor, Treatment Building, circuit LP2-2 · E4.1 (no tag)]] — also in Wiki note (Verified-Visual)
- [[Local alarm light and horn for ventilation and gas… · E4.1 (no tag)]] — also in Wiki note (Verified-Visual)
- [[LSH-111 · 2W float F1- high level alarm and redundant valve close at…]] (Verified-Visual)
- [[F2 (2W Pump Station) · 2W float F2- valve close at 20.00 (factory float tree)]] (Verified-Visual)
- [[F3 (2W Pump Station) · 2W float F3- valve open at 19.00 (factory float tree)]] (Verified-Visual)
- [[LSL-111 · 2W float F4- low level alarm and pumps off at 15.00]] (Verified-Visual)
- [[Digester level transducer- WIKA submersible, 316 SS · E5.1 (no tag)]] (Unresolved)

### Describes

- [[Influent sampler (Owner-furnished, contractor-installed) · E4.1 (no tag)]] — Wiki note 26 80 00 (Verified-Visual)
- [[Effluent sampler (Owner-furnished, contractor-installed) · E2.2 (no tag)]] — Wiki note 26 80 00 (Verified-Visual)
- [[UV1 · UV disinfection unit No.1]] — Wiki note 26 80 00 (Inferred)
- [[UV2 · UV disinfection unit No.2]] — Wiki note 26 80 00 (Inferred)

### Paragraphs cited

- [[26 80 00 ¶1.06 · Control System]] (Inferred)
- [[26 80 00 ¶2.02 · Control System]] (Inferred)
- [[26 80 00 ¶2.02 A.3 · Control System]] (Inferred)
- [[26 80 00 ¶2.04 C · Control System]] (Inferred)
- [[26 80 00 ¶2.04 E · Control System]] (Inferred)
- [[26 80 00 ¶2.04 F · Control System]] (Inferred)
- [[26 80 00 ¶2.04 G · Control System]] (Inferred)
- [[26 80 00 ¶2.04 H · Control System]] (Inferred)
- [[26 80 00 ¶2.04 I · Control System]] (Inferred)
- [[26 80 00 ¶2.05 · Control System]] (Inferred)
- [[26 80 00 ¶3.03–3.04 · Control System]] (Inferred)
- [[26 80 00 ¶3.08 · Control System]] (Inferred)
- [[26 80 00 ¶3.09 C · Control System]] (Inferred)
- [[26 80 00 ¶3.09 D · Control System]] (Inferred)
- [[26 80 00 ¶3.09 E · Control System]] (Inferred)
- [[26 80 00 ¶3.09 J.2 · Control System]] (Inferred)
- [[26 80 00 ¶3.09 K · Control System]] (Inferred)
