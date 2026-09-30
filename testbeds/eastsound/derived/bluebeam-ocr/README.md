# Bluebeam OCR copies — 11x17 plan set

Derived copies, not sources. A person ran Bluebeam OCR over page extracts of the 11x17 bid plan set and added the results here. Prompt 6 uses them for the comparison column and nothing else.

Short names used below: **OCR Part 1** = `Pages from eswd-wwtp-upgrade-ph1-11x17-plans - OCR - Part 1.pdf` · **OCR Part 2** = `Pages from eswd-wwtp-upgrade-ph1-11x17-plans - OCR - Part 2.pdf` · Sheet Index = `01_Sheet_Index_rev1.md`. For the plans_N short names, see `00_Document_Register_rev1.md`.

## Rule (stated by a person, 2026-09-30)

- Text read from these files counts as OCR and is tagged **Inferred**. It is never a text layer, and it never earns Verified.
- Text-layer reads come only from the native files in `testbeds/eastsound/library/`.
- In Prompt 6 these copies fill the comparison column only.

## Source file

- **Source:** `eswd-wwtp-upgrade-ph1-11x17-plans.pdf`, the full 96-sheet 11x17 bid set (Inferred). Basis: the "Pages from" prefix is the name Bluebeam and Acrobat give to extracted pages, and the two parts' title blocks run "1 OF 96" to "96 OF 96" with no gap (see Parts).
- **Library status:** the full set file isn't in `Library_Fingerprint.csv`. The library holds this set only as the plans_1 to plans_12 extracts (`00_Document_Register_rev1.md` rows 5–30) (Verified).
- **Carried metadata**, the same in both files: Creator "Autodesk Civil 3D 2022", Producer "pdfplot16.hdi 16.01.173.00000" (Verified, PDF Info dictionary). Bluebeam didn't overwrite either field.

## Bluebeam OCR settings

- **Not stated.** Neither file records the OCR settings; there are no OCR parameters in the Info dictionary or XMP metadata (Verified). Still to be supplied by the person who ran the OCR: Revu version, language, resolution (DPI), page range, Detect Vector Text, Auto-Rotate/Deskew.
- **Observed in the files** (Inferred; basis: Bluebeam's object naming and invisible render mode, found on every page):
  - All 96 pages carry a hidden text layer (text render mode 3) inside a form object named `BBL`. That layer is taken to be Bluebeam's OCR output.
  - The original plotted CAD text (render mode 0) is still there next to it. A text search or extraction returns both mixed together, which is why every read from these files counts as OCR under the rule above.

## Date

- OCR run 2026-09-30, as stated by the person who ran it. This matches the ModDate in both files: OCR Part 1 at 2026-09-30 09:26:29 -07:00, OCR Part 2 at 09:26:45 -07:00 (Verified, PDF Info dictionary).

## Parts

Page counts are from each file's page tree (Verified). Title-block values are read from these copies, so they're Inferred under the rule; the Sheet Index cross-check is in the last column.

| Part | Pages | First page (title block) | Last page (title block) | Set pages | Sheet Index cross-check |
|---|---|---|---|---|---|
| OCR Part 1 | 48 | p.1: G0.1, "1 OF 96", NOV 2, 2022 | p.48: C7.6, "48 OF 96", NOV 2, 2022 | 1–48 (set p. = file p.) | Set p.1 G0.1 and set p.48 C7.6, both Verified there |
| OCR Part 2 | 48 | p.1: C7.7, "49 OF 96", NOV 2, 2022 | p.48: E10.3, "96 OF 96", 09-12-2022, STANDBY DIESEL GENERATOR ELEVATIONS | 49–96 (set p. = file p. + 48) | Set p.49 C7.7 is "Verified (cover index only)" there; set p.96 E10.3 is Verified there |

## Pages to watch in the comparison

- **OCR text only, with no plotted text:** set pp.28 (C3.3), 29 (C3.4), 45 (C7.3) and 56–61 (S1.1, S2.1–S2.4, S4.1). These are the same 9 sheets the Sheet Index marks as having no text layer (Text = N). On these pages the comparison column has nothing native to compare against. S-sheet reads therefore still top out at Verified-Visual from the page image (Merge Issues Log #60).
- **Not in library/:** C0.7, C1.1, C1.2 (OCR Part 1 pp.14–16) and C7.7, C7.8, C7.9 (OCR Part 2 pp.1–3). These sheets exist only here, so anything read from them stays Inferred until a native copy is in `library/` (Merge README, "Still open").

## Fingerprint

| File | Bytes | SHA-256 |
|---|---|---|
| OCR Part 1 | 20,526,290 | 33569b9e5a301092f9d834e5c96a01ad0ab1475fa5a6d0ecc683808d4cef34d3 |
| OCR Part 2 | 16,242,340 | 128d830cfeb2069728a5857e8d6caa190a290dcdf8016c1a19b0a7a38017ceb6 |

Added to the repo 2026-09-30 at the root (commits b5fe630, 3f060d1) and moved here unchanged the same day.
