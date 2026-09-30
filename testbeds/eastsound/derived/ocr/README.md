# derived/ocr: drawing text for the Ledger and MTO cross-reference

Schema version 1.0. Machine-read words, tags and quantities from the native Eastsound plan set (set pages 1–96) and the Addendum 4 reissue pages (pp.4–10), keyed so they can be cross-referenced into the Project Ledger and a master MTO later. Built by `testbeds/eastsound/tools/extract_drawing_text.py` with no LLM calls. This folder is data only: nothing here has been entered in the Ledger or an MTO.

## Confidence rule

- A text-layer word from a native PDF counts as Verified.
- A Tesseract or Bluebeam word is Inferred until confirmed on the page image, when it becomes Verified-Visual.
- Nothing from this folder enters the Ledger or MTO without that confirmation and the owner's approval.
- Every quantity is tagged Inferred (machine-read). It is a lead to check, not a takeoff.

## Rebuild

```
apt-get install -y tesseract-ocr
pip install -r requirements.txt
PYTHONHASHSEED=0 OMP_THREAD_LIMIT=1 python testbeds/eastsound/tools/extract_drawing_text.py --stage all --jobs 4
```

- The script sets both variables itself if they are missing. `--jobs` runs pages in parallel worker processes; outputs are sorted, so any job count gives the same bytes.
- There are no timestamps, lists are sorted, boxes are rounded to 0.01 pt, JSON keys are sorted and line endings are LF. Byte-identical output also needs the same Tesseract build, `eng.traineddata` and CPU SIMD path. Each page file's `extractor` block records them.
- Stages: `pages` (Step 1: words and title blocks, the slow part), `forms` (Tag_Search_Forms.csv), `hits` (Step 2), `report` (Findings.md, Spot_Check.csv, this README). `--crops <folder>` with `report` writes the spot-check crops. Keep that folder outside the repo: PNG is not a repo file type (AGENTS.md rule 5).

Recorded for this build: Python 3.11.15, PyMuPDF 1.28.2, pytesseract 0.3.13, Pillow 12.3.0, tesseract 5.3.4; leptonica-1.82.0; Found AVX512BW; Found AVX512F; Found AVX512VNNI; Found AVX2; Found AVX; Found FMA; Found SSE4.1; Found OpenMP 201511; Found libarchive 3.7.2 zlib/1.3 liblzma/5.4.5 bz2lib/1.0.8 liblz4/1.9.4 libzstd/1.5.5; Found libcurl/8.5.0 OpenSSL/3.0.13 zlib/1.3 brotli/1.1.0 zstd/1.5.5 libidn2/2.3.7 libpsl/0.21.2 (+libidn2/2.3.7) libssh/0.10.6/openssl/zlib nghttp2/1.59.0 librtmp/2.3 OpenLDAP/2.6.10, eng.traineddata SHA-256 7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2.

## Files

| File | What it holds |
|---|---|
| pages/NNN_<sheet>.json, pages/add4_pNN_<sheet>.json | One per page: source file, SHA-256 and page, set page, 01 sheet and title, cited_as (plans_N copy from index/Plan_Set_Crosswalk.csv), governed_by / governs (Addendum 4), page size and rotation, counts, title block, words, bluebeam block, tags, quantities, keyed notes, extractor versions |
| Sheet_Map.csv | One row per page: 01 sheet vs title-block sheet read, titles, page N OF M, split-part file and page, native file and page, Addendum 4 links, text-layer and OCR counts, mean confidence |
| Tag_Search_Forms.csv | One row per Ledger row: search forms, family, searchable, and the reasons and rules |
| Tag_Hits.csv | One row per tag occurrence, with its assignment under the Gate A rules |
| Quantity_Hits.csv | One row per quantity lead: value and unit as separate fields, nearest tag, keyed note |
| Ledger_Crosswalk.csv | One row per Ledger row (447), keyed on Ledger Row |
| Unmatched_Tags.csv | Tag-shaped text with no Ledger row: candidates for the PROPOSED-tag crosswalk, not Ledger items |
| Findings.md | Title mismatches, sheets found, known values, fence rows, crosswalk gaps, anchor levels, keyed notes |
| Spot_Check.csv | 25 random words (5 each C, E, S, A, G) for a person to check on the page image |

## Keys and coordinates

- Join keys for the later Ledger and MTO step: Ledger Row, then sheet number, then set page. Ledger Row is the Project_Ledger.csv record number with the header as 1 (the same numbering as `ledger_to_graph.py`). The crosswalk is keyed on it, not on Tag, because "SD-1" and "PROPOSED-Influent-Sampler" each name two rows.
- Quantities carry Value and Unit as separate fields, matching the Quantity and Unit columns proposed for Ledger schema rev1.
- Boxes are PDF points on the page as displayed: origin top left, page rotation applied (set pp.62–96 are /Rotate 270), rounded to 0.01 pt.
- Set page to native part comes from `library/Plan_Set_Parts.md`. cited_as (the plans_N copy the index files cite, with duplicate extracts listed) comes from `index/Plan_Set_Crosswalk.csv`; the run stops if the crosswalk's native part, page or sheet disagrees. The 01 sheet, title and Addendum 4 supersession come from `index/01_Sheet_Index_rev1.md`; Add. 4 pages cite the 01 page-level log.
- Every native source's SHA-256 is checked against `index/Library_Manifest.csv` before any stage runs, and the run stops on a mismatch or a missing row.

## How a page is read

- Text layer: PyMuPDF `get_text("words")`. The render mode comes from the character flags (neither filled nor stroked means mode 3, AutoCAD's overlay for text drawn as geometry). Mode-3 words count as text layer. Words under 1 pt in both directions are dropped and counted per page.
- OCR: every page is rendered at 400 dpi and read by Tesseract (`--oem 1 --psm 3`, one thread), upright and rotated 90° with the boxes mapped back. Where the two passes read the same spot (overlap ≥ 0.5 of the smaller box), the higher confidence is kept. Every word keeps its confidence; ≥ 60 is a flag, not a filter. An OCR word on a text-layer word's spot is dropped: the text layer wins.
- Bluebeam: the render-mode-3 words in the Bluebeam OCR copies, minus any word that matches a native word at the same spot. These go into Tag_Hits and Quantity_Hits as method `bluebeam-ocr`, Inferred (owner's decision, 2026-09-30).
- Title block: the sheet-number word nearest the SHEET label closest to the bottom-right corner, with the page N OF M, date, title and revision read around it (no fixed coordinates, no assumed page total). Where the text layer has no title block, a rotated title-strip OCR pass (psm 11, 200 and 300 dpi, higher confidence per field) reads it instead, at any confidence.

## Tag search and assignment (Gate A, 2026-09-30)

- Search forms: trailing (...) and [...] are stripped, "|" aliases split and ranges expanded (F1–F4). Quotes and the spaces around # and - are dropped, word boundaries are kept, and an internal space matches 0 or 1 space. Matching is case-insensitive. An OCR or Bluebeam match made through a 1/I, 0/O, 5/S, 8/B or #/H swap is marked fuzzy.
- "(E)" is kept as a qualifier: a hit counts for an "(E)" row only when "(E)" or "EXIST" is on the same line; otherwise it counts for the unqualified row, or is not counted.
- Short forms (3 characters or fewer) count only on the row's cited sheets. Elsewhere they are listed as "off-citation, short form" and left out of the found counts.
- A range row and its individual rows: the individual row takes the hit first, and the range row gets the rollup.
- Shared forms: a hit goes to the row whose Lane matches the sheet's lane in 01, falling back to the discipline letter. If that doesn't settle it, every candidate row is listed and the hit is marked ambiguous.
- PROPOSED rows are not searched by tag. Their Drawing Sheets anchors are checked instead (below). Pipe ID and Buried Valve ID rows match the legend line that starts with the ID number on C1.3 (base and Add. 4 p.7) and C1.4.

## Quantities

- Units: LF, SF, SY, CY, EA, LS, TON, GAL; FT is its own unit. Only L=nnn' converts to LF. Units may follow the number with no space (21LF).
- A foot value followed by a material word is a dimension, not a quantity (6' CHAIN LINK). The material words are: ALUM, ALUMINUM, ASPHALT, BLOCK, BRICK, CEDAR, CHAIN, CMP, CMU, CONC, CONC., CONCRETE, DI, DIP, FENCE, FRP, GALV, GALV., GRAVEL, HDPE, HMA, LINK, PVC, RCP, ROCK, SS, STEEL, TIMBER, VINYL, WOOD.
- Sizes: `8"`, `12-in` and the like count only when a pipe, valve or conduit word follows within 4 words: 2W, AIR, BALL, C, C900, CHECK, CI, CMP, CONDUIT, COPPER, CPVC, CU, CULVERT, DI, DIA, DIA., DIP, DRAIN, EFFLUENT, EMT, FM, FORCE, GATE, GRAV, GRAV., HDPE, HYDRANT, INFLUENT, LINE, MAIN, PIPE, PLUG, PVC, RCP, RGS, ROOF, SANITARY, SCH, SCH., SD, SDR, SEPTIC, SEWER, SLUDGE, SS, STEEL, STORM, SUPERNATANT, VALVE, VENT, W, WAS, WATER.
- Counts: a number followed by a plural noun (12 BOLLARDS, (3) LOCATIONS), unit EA.
- Slopes: n% counts as a slope after SLOPE or S=, or as "@ n%" after an LF quantity (39 LF @ 0.5%). Otherwise it is kind "percent". Also S=0.005 (FT/FT) and 2H:1V.
- Elevations: RIM, SUMP, IE, INV, EL, ELEV, FG, FF, FFE, TOC, TOW, BOW, TOG, GRATE.
- Nearest tag: the nearest tag hit (assigned or ambiguous) within 24 pt, edge to edge, or "none". Calibration: every SDCB label on C2.1–C2.4 sits 0–13.1 pt from its RIM value.
- Keyed notes: a quantity inside a keyed-note entry carries that entry's number, and the callouts of that number read on the plan.

## Keyed notes

- The block sits under a KEYED NOTES / KEY NOTES heading. Entries split on line spacing (a gap over 1.4 × the block's 25th-percentile spacing) or on a leading marker in the marker column.
- A marker read by OCR sets the number when it is 1 or 2 past the previous entry's number (tagged at the marker's read level). Otherwise the entry takes the previous number + 1 ("by order", Inferred).
- If a block's entry count differs from its highest marker read, its by-order numbers are Unresolved. A block with no marker read keeps Inferred and is flagged in Findings.

## PROPOSED anchors

- Verified: the anchor was found in the native text layer and its text holds the row's quantity, or a key noun from the Ledger Name. Inferred: the same match read by OCR or Bluebeam. Unresolved: the anchor was not found, or its text doesn't match. A row's level is its weakest anchor.
- Sheet-only anchors (owner, 2026-09-30): a cited sheet with no KN, Det. or Add. anchor is Verified only when the row's quantity (value and unit) is read on that sheet in the text layer. A noun match anywhere on the sheet is Inferred, marked "on sheet, location not pinned".
- Match term: when the Ledger Name has a quantity (value and unit, e.g. 149 LF, 7 ft), the anchor must hold that quantity; a noun is not enough. Only rows with no quantity use a noun, and only a specific one. The matched term is recorded in the crosswalk's Anchor Check column.
- Anchor text by type: KN n → that keyed-note entry. Det. n → the detail's region, from its SCALE line up to the title row above and across to the next detail. Add. 4 p.N → that page. A sheet with no anchor → the whole sheet. Other anchors (Demo Schedule n, Item n, …) are Unresolved as not machine-checkable.
- Key nouns: words of 4+ letters in the Ledger Name, plurals folded (a trailing S dropped), words ending in -ED dropped, and minus the two lists below. Please review both.

Stopwords (never nouns): ABANDON, ABOUT, ABOVE, ADDENDUM, ALSO, AREA, AREAS, BASE, BELOW, BOTH, CLEAR, COMPONENT, COMPONENTS, CONSTRUCTION, CONTRACTOR, DETAIL, DETAILS, DURING, EACH, EAST, ENGINEER, EQUAL, EQUIPMENT, ESWD, EXISTING, FROM, INCH, INCHES, INSTALL, INSTALLED, INTO, ITEM, ITEMS, LOCAL, LOCATION, LOCATIONS, MAXIMUM, MIN., MINIMUM, NORTH, NOTE, NOTES, ONLY, ONTO, OTHER, OWNER, PART, PARTS, PHASE, PLAN, PLANS, PLUS, PROJECT, PROPOSED, PROVIDE, PROVIDED, QUANTITY, RELOCATE, REMOVAL, REMOVE, REMOVED, REQUIRED, ROWS, SAME, SECTION, SHALL, SHEET, SHEETS, SITE, SIZE, SIZES, SOUTH, SPEC, SPECIFICATIONS, STATED, SYSTEM, TEMPORARY, THAT, THEN, THESE, THIS, THOSE, TYPE, TYPICAL, UNDER, WEST, WHEN, WHERE, WILL, WITH, WORK, WWTP.

Generic nouns (too common here to anchor a row): ASPHALT, BACKFILL, BASIN, BLOCK, BOTTOM, BUILDING, CABLE, CELL, CIRCUIT, CONCRETE, CONDUIT, CONNECTION, CONTROL, COVER, CURB, DOOR, DRAIN, DRAINAGE, EFFLUENT, ELECTRICAL, EXCAVATION, EXTERIOR, FENCE, FLOOR, FLOW, FOOTING, FOUNDATION, FRAME, GRADE, GRADING, GRAVEL, HIGH, INFLUENT, INLET, INSTALLATION, INTERIOR, LEVEL, LIGHT, LIGHTING, LINE, MAIN, MECHANICAL, METER, MOTOR, OPENING, OUTLET, PANEL, PAVEMENT, PIPE, PIPING, PLANT, PLATE, POWER, PRECAST, PUMP, ROOF, SANITARY, SERVICE, SEWER, SLAB, SLUDGE, STAINLESS, STATION, STEEL, STORM, STRUCTURE, SUPPORT, SURFACE, SWITCH, TANK, TRAIN, TREATMENT, TRENCH, UNIT, UNITS, VALVE, WALL, WATER, WIRE, WIRING.

## Unmatched_Tags

- Tag-shaped text that matches no Ledger form, exact or fuzzy, sheet numbers excluded. Shapes: letters-dash-number `(?<![A-Z0-9#-])[A-Z]{1,5}-\d{1,4}[A-Z]?(?![A-Z0-9-])`; letters-hash-number `(?<![A-Z0-9#-])[A-Z]{2,5}#\d{1,4}(?![A-Z0-9])`; structure-number `(?<![A-Z0-9#-])(?:SSMH|SDMH|SDCB|MH|CB)\s?\d{2,5}(?![A-Z0-9])`; letters-number `(?<![A-Z0-9#.-])[A-Z]{1,4}\d{1,3}[A-Z]?(?![A-Z0-9.#-])`.

## Spot check

- Seed 20260930. 5 random words per discipline (C, E, S, A, G), drawn from each discipline's pages. The pool is every kept word of 2+ letters or digits: text layer, OCR and Bluebeam.
- Columns follow Spot_Check_Schema (Pick No. to Note), then Set Page, BBox (pt), Word Read, Confidence and Crop Path. Ledger Row, Tag and Name are filled only when the word is part of an assigned tag hit.
- Human Result, Checked By and Date stay blank. Only the owner marks a read Verified-Visual.
- Crop Path is relative to the `--crops` folder. The crops are 400 dpi renders with the word boxed, and they are not committed.

## Size

- Largest file: pages/056_S1.1.json (2.0 MB). No file passes 25 MB, so nothing is split.
