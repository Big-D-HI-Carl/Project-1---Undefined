# Project Known Issues — Eastsound WWTP Upgrade Phase I (five lanes combined)

Built 2026-09-29 by the Merge thread from the five lane Known Issues files (Civil & Site, Process & Mechanical, Electrical & Controls, Structural & Building, Contract & General) and the Structural & Building Issues file for its document items. Full sources stay in each lane's Issues file; cross-lane items are rows in Exception_Report; every item below points to its entry in Issues_Log.

- **Part A — method issues:** 61 lane items combined into 31 themes (every item mapped; 0 unmapped).
- **Part B — open document decisions:** 139 items (Civil & Site 23, Process & Mechanical 40, Electrical & Controls 22, Structural & Building 23, Contract & General 31); 46 are also Exception Report rows.
- **Part C — settled or record-only:** 17 items. **Part D — Electrical & Controls cross-lane carries:** 14 items, all Exception Report rows.
- **Issues Log check:** 31 of 31 themes and 139 of 139 decisions have an Issues Log entry.

## Part A — Method issues (combined themes)

| Theme | Combined issue | Lane items | Fix (proposed) | Owner | Status | Issues Log |
|---|---|---|---|---|---|---|
| T01 | Drawing images too coarse (about 80 dpi) for small text | Structural & Building:Known 1; Civil & Site:K-03 | Native PDFs via SharePoint; re-run the S/A visual pass and re-tag | SharePoint | Deferred | #10, #54 |
| T02 | S-sheet pages have no text layer | Structural & Building:Known 2 | OCR native PDFs; stage text beside each page | SharePoint | Open | #60 |
| T03 | Library files named .pdf are not PDFs | Structural & Building:Known 3; Contract & General:W10 | Open-as-bundle and split-by-header steps in the crawl prompt; detect format by content at ingest | Setup | Worked around | #61 |
| T04 | Spec text from other projects; pointers to sections, sheets and attachments that do not exist | Structural & Building:Known 4; Contract & General:W5 | Check every named structure, sheet and section against 01/02; never create rows from misses | Composer | Open | #52, #62 |
| T05 | Upstream index statement contradicted by the source (01 log #12) | Structural & Building:Known 5 | Setup amends 01; crawl rule to log index corrections | Setup | Open | #51 |
| T06 | Addendum changed drawings but not the matching spec text | Structural & Building:Known 6 | Supersession search step for every attribute Add. 4 changes | Composer | Worked around | #63 |
| T07 | Weakest-tag rule: the bid item basis pulls every row to Inferred | Structural & Building:Known 7; Contract & General:W3; Civil & Site:K-01; Process & Mechanical:Test-bed 1; Process & Mechanical:Test-bed 7 | Separate Bid Item basis / classification confidence column | Composer | Open | #12 |
| T08 | Submittal and Testing Y/N: source rule, third value, drawing-note and cross-lane requirements | Structural & Building:Known 8; Contract & General:W8; Civil & Site:CS-37; Civil & Site:K-09; Process & Mechanical:Test-bed 6; Electrical & Controls:Method 6 | Y / N / Not stated with a basis qualifier; owning lane sets the flag | Composer | Open | #13 |
| T09 | Testing/Startup column undefined | Structural & Building:Known 9 | Define the column or split it | Composer | Open | #64 |
| T10 | No quantity or unit column | Structural & Building:Known 10 | Add Qty and Unit columns | Composer | Open | #65 |
| T11 | Spec-only rows have no Drawing Sheets value | Structural & Building:Known 11 | Allow "(reference only)" sheets or a Referenced Sheets column | Composer | Open | #66 |
| T12 | Tag naming: free-text PROPOSED tags, sheet-scoped and duplicate printed IDs | Structural & Building:Known 12; Electrical & Controls:Method 3; Civil & Site:K-06; Process & Mechanical:Test-bed 4 | Naming rule or shared tag registry; tag-harvest pass; crosswalk before combining | Composer / Setup | Open | #2, #5 |
| T13 | Owning lane lives in Notes, not a column | Structural & Building:Known 13 | Add an Owning Lane column | Composer | Open | #67 |
| T14 | Row granularity uneven (components vs package rows; roll-ups; category rows) | Structural & Building:Known 14; Contract & General:W9; Electrical & Controls:Method 5 | One split rule in the schema | Composer | Open | #68 |
| T15 | Area names uncontrolled | Structural & Building:Known 15 | Controlled Area list from 01 | Setup | Open | #7 |
| T16 | Issue references by position; lane issue numbers not stable | Structural & Building:Known 16; Electrical & Controls:Method 4 | Permanent issue IDs; cite by ID and title | Composer | Open | #6, #69 |
| T17 | Wiki Tags mix printed references with by-subject links; appendices linked only by subject | Structural & Building:Known 17; Contract & General:W6 | Split Tags into Cited and Related by subject | Composer | Open | #70 |
| T18 | Notation and encoding (UTF-8 without BOM; ft/in vs marks) | Structural & Building:Known 18; Process & Mechanical:Test-bed 8 | xlsx view for people, CSV for machines; one dimension notation | Composer | Worked around | #71 |
| T19 | Per-turn tool budget ended turns before saves | Structural & Building:Known 19; Process & Mechanical:Test-bed 5 | Save first; batches of about 8 units; reserve the last calls | All threads | Worked around | #1, #72 |
| T20 | Visual pass drives the cost | Structural & Building:Known 20 | Native text layers; pre-rendered standard crops | Setup / SharePoint | Open | #73 |
| T21 | The crawl needs a code sandbox | Structural & Building:Known 21 | Setup stages splits and crops so crawl threads only read | Setup | Open | #74 |
| T22 | Existence and absence checks need a full-text search | Structural & Building:Known 22; Contract & General:W7 | Cross-reference and absence index in 02 | Setup | Open | #75 |
| T23 | Concurrent sessions wrote the same working folder | Contract & General:W1; Contract & General:W2 | One folder per session; lock with session ID, heartbeat and content hash | All threads | Worked around | #76 |
| T24 | Duplicate spec text double-counts requirements | Contract & General:W4 | Duplicate-body check; key requirements to the primary copy | Composer | Open | #77 |
| T25 | Lane-wide requirements sit as prose, not Requirements rows | Contract & General:W11 | Crawl writes Requirements rows | Composer | Open | #14 |
| T26 | Read method misses image-only content; text layer pairs tags wrongly | Electrical & Controls:Method 1; Electrical & Controls:Method 2; Civil & Site:CS-05; Civil & Site:CS-11; Process & Mechanical:Test-bed 3 | "Text + Visual" read method; image governs pairings | Setup | Open | #11 |
| T27 | Partial reads: long sections scanned by key terms; Appendix C read by section | Electrical & Controls:Method 7; Civil & Site:K-04 | Decide whether key-term scanning meets the standard | Owner (Carl) | Open — owner decision | #78 |
| T28 | Tagging conventions to ratify (conflicted-attribute placement; WSDOT tag placement) | Electrical & Controls:Method 8; Civil & Site:K-02 | Composer ratifies one convention each | Composer | Open | #79 |
| T29 | Inferred links and "New" status in the Civil & Site Ledger | Civil & Site:K-07; Civil & Site:K-08 | Confirm at Merge or by RFI where disputed | Merge | Logged | #80 |
| T30 | Cross-lane items kept in Issues, not the Ledger | Civil & Site:K-05 | Merge pulls them from Issues | Merge | Done in Merge | #23 |
| T31 | Schema column 14 name ("Tag level" in 03 vs the CSV header) | Process & Mechanical:Test-bed 2 | Align 03 with the schema file | Setup | Logged | #81 |

## Part B — Open document decisions

| # | Lane | ID | Issue | Type | Priority | Resolver | Status | Exception Report | Issues Log |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Contract & General | 1.1 | Bid deadline: 10:00 AM vs 2:00 PM PST, Feb 8, 2023 | Conflict |  | Owner | Open | — | #86 |
| 2 | Contract & General | 1.2 | Add. 4 is dated Feb 9, 2023, one day after the stated bid opening | Conflict |  | Setup / Owner | Open | — | #86 |
| 3 | Contract & General | 1.3 | Contract signing window: 10 working days vs 10 calendar days | Conflict |  | Owner/Engineer | Open | — | #86 |
| 4 | Contract & General | 1.4 | Bid hold: award within 45 days vs acceptance within 60 days | Conflict |  | Owner | Open | — | #86 |
| 5 | Contract & General | 1.5 | Subcontractor list: all within 1 hour vs steel and rebar installers within 48 hours | Conflict |  | Owner | Open | — | #86 |
| 6 | Contract & General | 1.6 | DBE forms and Bidders List: with the bid vs within 1 hour after bid time | Conflict |  | Owner | Open | — | #86 |
| 7 | Contract & General | 1.8 | Liquidated damages: General Conditions sum per calendar day vs LD = 0.15C/T per working day under WSDOT 1-08.9 | Conflict |  | Owner/Engineer | Open | — | #86 |
| 8 | Contract & General | 1.9 | County permit: approved June 2022 vs "currently processing" (Building Permit #21-0385) | Conflict |  | Owner | Open | — | #86 |
| 9 | Contract & General | 1.11 | Guarantee: one year from Substantial Completion vs one year after District acceptance of all work | Conflict |  | Owner/Engineer | Open | — | #86 |
| 10 | Contract & General | 1.14 | Contractor qualifications: with the bid vs within 24 hours of opening | Conflict |  | Owner | Open | — | #86 |
| 11 | Contract & General | 1.16 | Field office is optional, but the schedule and records must be kept there | Conflict |  | Owner | Open | — | #86 |
| 12 | Contract & General | 1.17 | Substitution requests: 10 days after the Agreement vs 30 days after the Contract Date; PDF vs six copies | Conflict |  | Owner | Open | — | #86 |
| 13 | Contract & General | 1.19 | Temporary facilities out before the Substantial Completion request vs at completion or Final Completion | Conflict |  | Owner | Open | #245 | #86 |
| 14 | Contract & General | 1.20 | Energy code: 2015 WSEC named vs the edition in effect on the bid date | Conflict |  | Engineer | Open | — | #86 |
| 15 | Contract & General | 1.21 | Dewatering start-up: "a minimum of one (2) days" per supplier | Conflict |  | Engineer | Open | #190, #246 | #86 |
| 16 | Contract & General | 1.26 | QA plan requires Ecology review of significant change orders; the contract has no such step | Conflict |  | Owner | Open | — | #86 |
| 17 | Contract & General | 1.10 | Pre-construction meeting: within 2 weeks of award notice vs after NTP | Conflict |  | Owner/Engineer | Working answer — confirm | — | #86 |
| 18 | Contract & General | 1.12 | Schedule and Schedule of Values due dates | Conflict |  | Owner/Engineer | Working answer — confirm | — | #86 |
| 19 | Contract & General | 1.15 | WSDOT and APWA standard specifications: "latest edition" vs 2022 Edition | Conflict |  | Owner/Engineer | Working answer — confirm | — | #86 |
| 20 | Contract & General | 1.23 | Progress meetings: weekly with the Owner presiding vs monthly with the Engineer conducting | Conflict |  | Owner/Engineer | Working answer — confirm | — | #86 |
| 21 | Contract & General | 1.24 | Earthwork sieve analyses: Owner's lab vs Contractor's QC lab | Conflict |  | Owner/Engineer | Working answer — confirm | — | #86 |
| 22 | Contract & General | 2.1 | Section 00 22 13 Supplemental Bidder Responsibility Criteria is cited but not in the manual | Missing information |  | Owner/Engineer | Open | — | #86 |
| 23 | Contract & General | 2.2 | DBE forms 6100-3 and 6100-4 are not bound; the pointers to Appendix G and to 00 73 00 Attachments 6–7 are wrong | Missing information |  | Owner / Setup | Open | — | #86 |
| 24 | Contract & General | 2.3 | EO 11246 "covered area" left as a placeholder | Missing information |  | Owner / Commerce | Open | — | #86 |
| 25 | Contract & General | 2.4 | Federal wage decision: Appendix E (WA20220057 Mod. 4, 12/23/2022, Heavy) is taken as the determination; whether it was current at bid opening, and whether a Building decision is also needed, are open | Missing information |  | Owner / Commerce | Open (partly closed) | — | #86 |
| 26 | Contract & General | 2.5 | Sections cited but not in the manual: 00 25 13, 00 43 36, 00 45 14, 01 30 00, 00 72 00, "00 73 00a" | Missing information |  | Engineer | Open | — | #86 |
| 27 | Contract & General | 2.6 | "General Conditions" are not in the library; the WSDOT Standard Specifications appear to serve (Inferred) | Missing information |  | Setup / Owner | Open | #248 | #86 |
| 28 | Contract & General | 2.7 | The funding inserts (00 53 00, 00 54 00) are not ranked in the SC 2 order of precedence | Missing information |  | Owner/Engineer | Open | — | #86 |
| 29 | Contract & General | 2.8 | Commissioning skips ¶1.08–1.09; no start-up paragraph for the generators, ATS, MCC, PLC panel, 480V service or influent sampler | Missing information |  | Engineer; Electrical & Controls | Open | #249 | #86 |
| 30 | Contract & General | 2.9 | Appendices D, E and I are never cited by name in Divisions 00–01; links run by subject | Missing information |  | Setup / Composer | Design note | — | #86 |
| 31 | Contract & General | 2.10 | QA plan cites WAC 173-351 for Contractor quality control, unlike its WAC 173-240 basis elsewhere | Missing information |  | Engineer | Open | — | #86 |
| 32 | Electrical & Controls | Issues #4 | Service load vs the 225 kVA utility transformer | Conflict (Engineer decision) |  | Engineer (RFI); OPALCO coordination per 26 05 00 ¶3.03 (main spec p.279) | Unresolved | — | #84 |
| 33 | Electrical & Controls | Issues #2 | Influent pump starters: IPS panel or MCC | Conflict (Engineer decision) |  | Engineer (RFI) | Unresolved | — | #84 |
| 34 | Electrical & Controls | Issues #14 | Dewatering ventilation: continuous or only during dewatering, and how the fans are controlled | Conflict (Engineer decision) |  | Engineer (RFI) | Unresolved | #26, #196, #248 | #84 |
| 35 | Electrical & Controls | Issues #7 | Level transducer ranges (0–15 psi vs 0–15 ft) and the digester intrinsic safety barrier | Conflict (Engineer decision) |  | Engineer (RFI) | Unresolved | #58 | #84 |
| 36 | Electrical & Controls | Issues #9 | Backup high-level floats start the wrong-size pumps | Conflict (Engineer decision) |  | Engineer (RFI) | Unresolved | #40 | #84 |
| 37 | Electrical & Controls | Issues #12 | Low-level float on the E10.1 detail only | Conflict (Engineer decision) |  | Engineer (RFI) | Unresolved | — | #84 |
| 38 | Electrical & Controls | Issues #13 | Effluent meter vault: Class I Div 2 or unclassified | Conflict (Engineer decision) |  | Engineer (RFI) | Unresolved | — | #84 |
| 39 | Electrical & Controls | Issues #11 | Ventilation control panel fed from LP1 or LP2 | Conflict (Engineer decision) |  | Engineer (RFI) | Unresolved | — | #84 |
| 40 | Electrical & Controls | Issues #1 | Blower Building raceway concealment in a metal building | Conflict (Engineer decision) |  | Engineer (RFI); cross-lane Structural & Building | Unresolved | #192 | #84 |
| 41 | Electrical & Controls | Issues #3 | 2W pump tags and conduit count | Conflict (Engineer decision) |  | Engineer (RFI) | Unresolved | #45, #193 | #84 |
| 42 | Electrical & Controls | Issues #10 | Influent pump 2 input list | Conflict (Engineer decision) |  | Engineer or system integrator | Unresolved | — | #84 |
| 43 | Electrical & Controls | Issues #6 | Main PLC input numbering on E7.3 | Conflict (Engineer decision) |  | Engineer or system integrator | Unresolved | — | #84 |
| 44 | Electrical & Controls | Issues #19 | Temporary generator rating | Missing information |  | Engineer (bidder question) | Unresolved | #14, #198 | #84 |
| 45 | Electrical & Controls | Issues #18 | Train 1 and 2 future provisions | Missing information |  | Engineer (bidder question) | Unresolved | #197 | #39, #84 |
| 46 | Electrical & Controls | Issues #17 | UV-area pole light has no circuit | Missing information |  | Engineer (RFI) | Unresolved | — | #84 |
| 47 | Electrical & Controls | Issues #20 | Three items with no governing Division 26 section | Missing information |  | Engineer or Merge | Unresolved | #199 | #84 |
| 48 | Electrical & Controls | Known 17 | Temporary generator bid item | Bid item flag |  | Owner and Engineer (flag already in 02 Merge item 1, 03, 04 Bid Item #18) | Unresolved | — | #84 |
| 49 | Electrical & Controls | Known 18 | Permanent generator bid item | Bid item flag |  | Owner and Engineer (flag already in 03 and 04 Other bid-item conflicts #1) | Unresolved | — | #84 |
| 50 | Electrical & Controls | Issues #22 | Generator pad: civil or structural | Cross-lane conflict |  | Merge — Civil & Site; Structural & Building | Unresolved | #201 | #84 |
| 51 | Electrical & Controls | Issues #26 | Dewatering fan airflow for 6 air changes per hour | Cross-lane conflict |  | Merge — Process & Mechanical (23 34 00) | Unresolved | #205 | #84 |
| 52 | Electrical & Controls | Issues #27 | 2W hot box re-orientation | Cross-lane conflict |  | Merge — Civil & Site | Unresolved | #206 | #84 |
| 53 | Electrical & Controls | Issues #32 | Who installs the Owner-furnished samplers | Cross-lane conflict |  | Merge — Process & Mechanical | Unresolved | #13, #211 | #84 |
| 54 | Civil & Site | CS-13 | Buried valve list doesn't agree | Conflict | High | Engineer (RFI) | Unresolved | #177 | #82 |
| 55 | Civil & Site | CS-15 | Train 2 and Train 3 flow meter isolation valves: type and count | Conflict | High | Engineer (RFI) | Unresolved | — | #82 |
| 56 | Civil & Site | CS-16 | Flow meter vault pipe labeled both force main and gravity | Conflict | High | Engineer (RFI) | Unresolved | #81 | #82 |
| 57 | Civil & Site | CS-29 | Buried pipe materials on C1.3 differ from Division 33 | Conflict | High | Engineer (RFI) | Unresolved | #85, #93, #94, #159 | #82 |
| 58 | Civil & Site | CS-35 | Storm drain SD-1 material not stated; cover looks shallow | Missing information | High | Engineer (RFI) | Unresolved | — | #82 |
| 59 | Civil & Site | CS-31 | Footing drain pipe type | Conflict | High | Engineer (RFI) | Unresolved | — | #82 |
| 60 | Civil & Site | CS-33 | Groundwater elevation in NAVD88; drawings on NGVD 1929 | Conflict | High | Engineer or surveyor (RFI) | Unresolved | — | #82 |
| 61 | Civil & Site | CS-23 | Native material in trench backfill | Conflict | High | Engineer (RFI); Contract & General for precedence (00 73 00) | Unresolved | #138, #140, #152, #248 | #82 |
| 62 | Civil & Site | CS-24 | Trench compaction targets | Conflict | High | Engineer (RFI) | Unresolved | — | #82 |
| 63 | Civil & Site | CS-25 | Pay basis for dewatering and construction stormwater | Conflict | High | Contract & General | Unresolved | #69, #153 | #82 |
| 64 | Civil & Site | CS-32 | Who provides construction staking | Conflict | High | Contract & General (00 73 00, Supplementary Conditions No. 7, cited by G0.3) | Unresolved | #154 | #49, #82 |
| 65 | Civil & Site | CS-09 | Plant drain pump station isn't defined in this lane | Missing information | High | Engineer (RFI); Process & Mechanical via Merge | Unresolved | #37, #151, #222 | #82 |
| 66 | Civil & Site | CS-27 | Stabilized construction entrance type | Conflict | Medium | Engineer (RFI) | Unresolved | — | #82 |
| 67 | Civil & Site | CS-28 | Tracer wire spec, spacing and scope | Conflict | Medium | Engineer (RFI) | Unresolved | — | #82 |
| 68 | Civil & Site | CS-19 | Yard hydrant detail and post hydrant size/location | Missing information | Medium | Engineer (RFI); C1.1 (unavailable) may show it | Unresolved | — | #82 |
| 69 | Civil & Site | CS-34 | Groundwater log has no well ID or reference elevation | Missing information | Medium | Engineer (RFI) | Unresolved | — | #82 |
| 70 | Civil & Site | CS-01 | Catch basin removed under C0.5 Keyed Note 9 not identified | Missing information | Medium | Engineer (RFI); C2.1/C2.3 (unavailable) may show it | Unresolved | — | #82 |
| 71 | Civil & Site | CS-14 | Valve schedule points to the wrong location sheets | Conflict | Low | Engineer | Unresolved | — | #82 |
| 72 | Civil & Site | CS-17 | Yard hydrant detail points to the storm sheet | Conflict | Low | Engineer | Unresolved | — | #82 |
| 73 | Civil & Site | CS-18 | 'Section 15051' cited but not in the manual | Missing information | Low | Engineer | Unresolved | — | #82 |
| 74 | Civil & Site | CS-22 | Spec cross-references to sections that don't exist | Missing information | Low | Engineer | Unresolved | — | #82 |
| 75 | Civil & Site | CS-26 | Landscaping text names features not on this project | Conflict | Low | Engineer | Unresolved | — | #82 |
| 76 | Civil & Site | CS-30 | Fire hydrant detail not in the library | Missing information | Low | Engineer / Setup | Unresolved | — | #82 |
| 77 | Process & Mechanical | Issue 1 | Anoxic basin labeled "Train #4 (Proposed)" | Conflict |  | Engineer | Unresolved | — | #83 |
| 78 | Process & Mechanical | Issue 2 | Train 3 zone volumes | Conflict |  | Engineer | Unresolved | #181, #248 | #83 |
| 79 | Process & Mechanical | Issue 3 | Recycle airlift count, location and direction | Conflict |  | Engineer | Unresolved | — | #83 |
| 80 | Process & Mechanical | Issue 4 | Clarifier side water depth | Conflict |  | Engineer | Unresolved | — | #83 |
| 81 | Process & Mechanical | Issue 5 | Wall height and freeboard (low) | Conflict | Low | Engineer | Unresolved | — | #83 |
| 82 | Process & Mechanical | Issue 6 | Air totals (low) | Conflict | Low | Engineer | Unresolved | — | #83 |
| 83 | Process & Mechanical | Issue 8 | Experience clause names the wrong aeration type | Conflict |  | Engineer | Unresolved | — | #83 |
| 84 | Process & Mechanical | Issue 9 | Stainless alternates scope (missing) | Missing information |  | Engineer | Unresolved | #182 | #83 |
| 85 | Process & Mechanical | Issue 10 | Recycle pipe size at IE 10.57 | Conflict |  | Engineer | Unresolved | — | #83 |
| 86 | Process & Mechanical | Issue 30 | Mixers specified in two sections | Conflict |  | Engineer | Unresolved | #32 | #83 |
| 87 | Process & Mechanical | Issue 7 | Splitter "3-way" vs four chambers (low) | Conflict | Low | Engineer | Unresolved (label) | — | #83 |
| 88 | Process & Mechanical | Issue 40 | Splitter has no spec section (missing) | Missing information |  | Engineer | Unresolved | #75, #103 | #83 |
| 89 | Process & Mechanical | Issue 11 | Pipe brace refers to a sheet not in the set (missing) | Missing information |  | Engineer | Unresolved | — | #83 |
| 90 | Process & Mechanical | Issue 12 | 2W air gap reference and float-controlled valve (missing) | Missing information |  | Engineer | Unresolved | #183 | #83 |
| 91 | Process & Mechanical | Issue 26 | 2W relief valves | Conflict |  | Engineer | Unresolved | — | #83 |
| 92 | Process & Mechanical | Issue 39 | 2W wet well inlet size | Conflict |  | Engineer | Unresolved | — | #83 |
| 93 | Process & Mechanical | Issue 13 | UV modules and lamps | Conflict |  | Engineer | Unresolved | — | #83 |
| 94 | Process & Mechanical | Issue 15 | Final effluent size | Conflict |  | Engineer | Unresolved | #92 | #83 |
| 95 | Process & Mechanical | Issue 17 | Digester sludge line sizes | Conflict |  | Engineer | Unresolved | #90 | #83 |
| 96 | Process & Mechanical | Issue 18 | Sludge flow meter location | Conflict |  | Engineer | Unresolved | #43, #184 | #83 |
| 97 | Process & Mechanical | Issue 32 | UV dose units (low) | Conflict | Low | Engineer | Unresolved (label) | — | #83 |
| 98 | Process & Mechanical | Issue 33 | UV monitor panel distance (low) | Conflict | Low | Engineer | Unresolved | #55 | #83 |
| 99 | Process & Mechanical | Issue 14 | C6.1 cites a spec section that does not exist | Conflict |  | Engineer | Unresolved | — | #83 |
| 100 | Process & Mechanical | Issue 16 | Dry vs emulsion polymer | Conflict |  | Engineer | Unresolved | — | #83 |
| 101 | Process & Mechanical | Issue 22 | Screw conveyor count | Conflict |  | Engineer | Unresolved | — | #83 |
| 102 | Process & Mechanical | Issue 31 | Ball valve material | Conflict |  | Engineer | Unresolved (precedence rule is in the General Conditions) | #188 | #83 |
| 103 | Process & Mechanical | Issue 36 | Who controls the digested sludge pump | Conflict |  | Engineer | Add. 4 governs VFD location; controlling PLC Unresolved | #61, #189 | #83 |
| 104 | Process & Mechanical | Issue 37 | No press field start-up or training (missing) | Missing information |  | Engineer | Unresolved | #190, #246 | #83 |
| 105 | Process & Mechanical | Issue 38 | Potable water for flocculator breather (missing) | Missing information |  | Engineer | Unresolved | #191 | #83 |
| 106 | Process & Mechanical | Issue 41 | Carbon feed location, product and storage (missing) | Missing information |  | Engineer | Unresolved | — | #83 |
| 107 | Process & Mechanical | Issue 21 | Sludge pump capacity (low) | Conflict | Low | Engineer | Unresolved | — | #83 |
| 108 | Process & Mechanical | Issue 24 | Blower design pressure (low) | Conflict | Low | Engineer | Unresolved | — | #83 |
| 109 | Process & Mechanical | Issue 25 | Wall fan control (low) | Conflict | Low | Engineer | Unresolved | #26, #186, #196 | #83 |
| 110 | Process & Mechanical | Issue 20 | Launder cover section carries sludge pump text | Conflict |  | Engineer | Add. 4 governs the VFD text (Add. 4 p.1 General, Inferred); deletion Unresolved | — | #83 |
| 111 | Process & Mechanical | Issue 23 | Wrong submittal section (low) | Conflict | Low | Engineer | Unresolved | — | #83 |
| 112 | Process & Mechanical | Issue 27 | Wrong painting section (low) | Conflict | Low | Engineer | Unresolved | #187, #244 | #83 |
| 113 | Process & Mechanical | Issue 28 | Globe valve material (low) | Conflict | Low | Engineer | Unresolved | — | #83 |
| 114 | Process & Mechanical | Issue 29 | Polymer flow units and section reference (low) | Conflict | Low | Engineer | Unresolved | — | #83 |
| 115 | Process & Mechanical | Issue 34 | Analyzer called "pumps" (low) | Conflict | Low | Engineer | Unresolved | — | #83 |
| 116 | Process & Mechanical | Issue 35 | "22 13 16" cited twice (low) | Conflict | Low | Engineer | Unresolved | — | #83 |
| 117 | Structural & Building | §1 #1 | S2.2 mat slab reinforcing: two "typical for mat slabs this plan" callouts | Conflict |  |  | Unresolved — same sheet, no addendum | — | #85 |
| 118 | Structural & Building | §1 #2 | Train 3 lap length for Grade 75 bars | Conflict |  |  | Unresolved — both base; Add. 4 reissue of S4.1 leaves Detail 3 unchanged | — | #85 |
| 119 | Structural & Building | §1 #3 | Add. 4 reissue revision entries (index vs source) | Conflict |  |  | Source governs; index statement is partly wrong for S sheets | #217 | #51, #85 |
| 120 | Structural & Building | §1 #4 | Moist-cure duration | Conflict |  |  | Unresolved — same section | — | #85 |
| 121 | Structural & Building | §1 #5 | Influent Pump Station hatch | Conflict |  |  | Unresolved — same section; station drawing C4.1 is Process & Mechanical lane | #218 | #85 |
| 122 | Structural & Building | §1 #6 | Handrail and guardrail material | Conflict |  |  | Unresolved; likely 05 52 00 as the dedicated section (Inferred) | #34, #219 | #85 |
| 123 | Structural & Building | §1 #7 | Grating type and support angles at UV basin and digester | Conflict |  |  | Unresolved | #57, #220 | #85 |
| 124 | Structural & Building | §1 #8 | Blower Building interior insulation and finish assembly | Conflict |  |  | Unresolved | — | #85 |
| 125 | Structural & Building | §1 #9 | Lockset type and keying standard | Conflict |  |  | Unresolved; Part 4 schedule likely governs as more specific (Inferred) | — | #85 |
| 126 | Structural & Building | §2 #1 | Door 101B height | Missing information |  |  | Unresolved | — | #85 |
| 127 | Structural & Building | §2 #2 | Bid Item 9 — Structural Concrete (Extra Work, approx. 10 CY) | Missing information |  |  | Unresolved | #133, #221 | #85 |
| 128 | Structural & Building | §2 #3 | Which structures are "hydraulic structures" | Missing information |  |  | Inferred | — | #85 |
| 129 | Structural & Building | §2 #4 | Identity of the "Drain Pump Station" | Missing information |  |  | Unresolved | #37, #222 | #85 |
| 130 | Structural & Building | §2 #5 | Generator on S2.4 — permanent or temporary | Missing information |  |  | Unresolved | #65, #223 | #85 |
| 131 | Structural & Building | §2 #6 | S2.3 perimeter grade beam bar size | Missing information |  |  | Unresolved | — | #85 |
| 132 | Structural & Building | §2 #7 | Structures named in 03 30 00 but not in the sheet titles | Missing information |  |  | Unresolved | #258 | #85 |
| 133 | Structural & Building | §2 #8 | Section 04 60 00 (grouting) does not exist | Missing information |  |  | Unresolved | — | #85 |
| 134 | Structural & Building | §2 #9 | No spec coverage for footing-perimeter XPS and EIFS | Missing information |  |  | Unresolved | — | #85 |
| 135 | Structural & Building | §2 #10 | WSDOT references (external, not staged) | Missing information |  |  | Unresolved: external reference, not staged | — | #85 |
| 136 | Structural & Building | §2 #11 | Door hardware group assignment | Missing information |  |  | Inferred | — | #85 |
| 137 | Structural & Building | §2 #12 | Sheet C8.1 (exterior door stop detail) | Missing information |  |  | Unresolved | — | #52, #85 |
| 138 | Structural & Building | §2 #13 | Blower Building painting reference | Missing information |  |  | Unresolved | — | #85 |
| 139 | Structural & Building | §2 #14 | Blower Building floor sealer | Missing information |  |  | Unresolved | — | #85 |

## Part C — Settled or record-only

| Lane | ID | Item | Basis |
|---|---|---|---|
| Contract & General | 1.7 | Stale page numbers in 00 43 93 for the 00 53 00 attachments; content located | Record only — Verified |
| Contract & General | 1.13 | 00 73 00 pp.98–121 repeat the 00 53 00 Ecology insert word for word (99.8% word match) | Record only — Verified |
| Contract & General | 1.18 | 01 66 00 body is the 01 60 00 text word for word | Record only — Verified |
| Contract & General | 1.22 | Clean water leakage test list is repeated with different names | Record only — Verified |
| Contract & General | 1.25 | QA plan labels the construction phase "October 2022 – April 2024"; its own list runs to Oct 16, 2024 | Record only — Verified (SC 15 governs — Inferred) |
| Electrical & Controls | Issues #16 | Existing 208V utility transformer: the Utility removes it (26 05 00 ¶3.03 F.1.a, main spec p.279) — Issues #16. | Settled (lane) |
| Electrical & Controls | — | Train 1 flow meter: "future project – not in this project"; Phase I provides transmitter space only (E10.2 item 2, plans_12 p.7). | Settled (lane) |
| Electrical & Controls | Issues #8 | MCC length: Add. 4 p.1 Clarification 4 (eight 20-in sections, 160 in) governs over the seven sections, 140 in, on E9.1; the added section contents are left to the contractor layout (E9.1 general note 1) — Issues #8. | Settled (lane) |
| Electrical & Controls | — | Flow meter model: Add. 4 p.2 (26 80 00 ¶2.04 D) Promag W400 governs over L400; E4.1, E4.3, E5.1 and E10.2 already show W400. | Settled (lane) |
| Electrical & Controls | — | Sludge and 2W pump VFDs: Add. 4 p.2 (22 13 36 and 43 22 10 ¶2.01 A) puts them in the MCC under PLC control; E6.1 and E9.1 already match. | Settled (lane) |
| Electrical & Controls | — | VFD speed control: over Ethernet, no analog speed wiring (E9.2 key note 2, plans_12 p.4); E7.7 has no analog speed outputs. | Settled (lane) |
| Electrical & Controls | Issues #15 | 26 80 00 repeats ¶2.01 and ¶2.02 after ¶2.05; cite those paragraphs by page (pp.357, 367, 370) — Issues #15. | Settled (lane) |
| Electrical & Controls | — | Running headers: 26 36 00 reads "26 30 00" (02 log item 4) and 26 80 00 reads "INSTRUMENTATION AND CONTROL" (02 log item 6); body section numbers govern. | Settled (lane) |
| Electrical & Controls | — | Sheet titles that differ from the cover index (E0.4, E1.1, E3.1, E5.1, E8.2) are carried in the 01 log; the A1.1/A1.2 relocation of the MCC and main PLC panel belongs to the Structural & Building stack (cited flags). | Settled (lane) |
| Civil & Site | CS-06 | Pipe ID 10: base 2-in Sch. 80 PVC (plans_3Part-1 p.1) changed to 3-in HDPE by Add. 4 (Add. 4 p.7). Add. 4 governs; Ledger uses the Add. 4 value. (Verified-Visual) | Closed (lane) |
| Civil & Site | CS-12 | C2.5 fence height mark reads 6" (plans_3Part-8 p.1); 02 83 00 ¶1.01 A says all chain-link fence is 6 ft plus barbed wire, 7 ft total (main spec p.163). Carried as 6 ft — Inferred; confirm on the native PDF. (Inferred) | Closed (lane) |
| Process & Mechanical | Issue 19 | Building separation | Settled: Add. 4 governs (C6.3 not reissued) |

## Part D — Electrical & Controls cross-lane carries (no conflict)

- One building, two names: "Dewatering Building" vs "Treatment Building".
- Building openings left by the demolished generator exhaust and louvers.
- Aeration blowers BL-1 to BL-4 and digester blower DB.
- Exhaust fans EF-1, EF-2, motorized louver ML-1, manual louver.
- Train No.3 control panel, clarifier drive motor, submersible mixers A and B.
- Influent, WAS, sludge and dewatering process equipment.
- 2W pumps, float tree and isolation valve solenoid.
- UV disinfection units UV1, UV2 and their control panels.
- Treatment Building exhaust fans EF-3, EF-4, EF-5.
- UV-area pole light concrete base.
- Concrete pads under the main PLC panel and the Influent Pump Station panel.
- Supplier-furnished relays installed in Electrical & Controls panels.
- Blower enclosure fans powered from the MCC.
- Flow meter sizes: E10.2 summary vs "size per civil drawings".
