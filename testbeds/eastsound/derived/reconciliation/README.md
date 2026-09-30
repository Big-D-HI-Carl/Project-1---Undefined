# derived/reconciliation: proposed Ledger updates and a starter civil MTO

Prompt 9, proposal mode. This folder turns the OCR lane's evidence (`derived/ocr/`) into proposals the owner approves row by row. Nothing here has been applied to the Project Ledger or an MTO. The Ledger update is a later step, on the owner's approval.

## Rebuild

```
pip install -r requirements.txt
python testbeds/eastsound/tools/build_reconciliation.py
```

- Run it from the repo root. The script imports `testbeds/eastsound/tools/extract_drawing_text.py` for its own rules, so the packages pinned in `requirements.txt` must be installed. Tesseract is not needed.
- The output is deterministic: sorted rows, boxes to 0.01 pt, LF line endings, UTF-8 without a BOM, no timestamps. Two runs on the same inputs give identical files.
- The run stops and writes nothing if any tie-out fails. The tie-outs are listed at the end of Summary.md.
- `--crops <folder>` also renders each Needs_Check crop as a PNG. Keep that folder outside the repo; PNG is not a repo file type (AGENTS.md rule 5).

## Files

| File | What it holds |
|---|---|
| Ledger_ID_Map.csv | Decision A: Ledger ID, Ledger Row (the OCR crosswalk key), Tag, Name, Lane for all 447 records |
| Ledger_Schema_rev1_Proposal.md | The 16 current columns plus Ledger ID, Quantity and Unit. A proposal only: `index/Ledger_Schema.csv` and `tools/checks.py` are unchanged |
| Ledger_Update_Proposal.csv | One row per proposed change or check. Columns: Proposal No., Category, Ledger ID, Tag, Field, Current Value, Proposed Value, then Evidence Sheet, Set Page, BBox (pt) and Method, then Confidence and Reason |
| Starter_MTO.csv | Decision B, civil pilot (C0–C2, C7): LF, EA, CY, SF and SY quantities tied to a Ledger ID, with Bid Item and Tie Basis added |
| Needs_Check.csv | Every MTO line that is not Ready, plus the panel schedules from the owner's Division 26 review. Each has a crop box and blank Human Result, Checked By and Date columns |
| New_Row_Candidates.csv | The two proposed earthwork rows, then the 401 unmatched tags, one row per tag and sheet with read counts. Candidates only |
| Summary.md | Counts, the chain link fence conflict and the generator RFI (both left for the owner), held quantities, segment sums, open decisions, tie-outs and input SHA-256 values |

## Keys and coordinates

- **Ledger ID = L-(Ledger Row − 1).** L-0001 is the first record; Ledger Row counts the header as 1, as in `derived/ocr/` and `ledger_to_graph.py`. Tags stay as printed, and SD-1 keeps two rows with two IDs.
- Boxes are PDF points on the page as displayed: origin top left, page rotation applied, as in `derived/ocr/`. Set pages and native pages come from `derived/ocr/Sheet_Map.csv`. The short names (Part 1–3, Add. 4, main spec) are those in `index/00_Document_Register_rev2.md`.

## Rules

### Ledger update proposals

- A change is proposed only on Verified evidence, meaning a read in the native text layer. Inferred evidence (OCR, Bluebeam) and absences get Confidence "needs check" and no proposed value.
- **Found, not cited:** one row per sheet in the crosswalk's "Sheets Found but Not Cited". A text-layer read adds that one sheet to Drawing Sheets. Off-citation short-form hits stay out, per the Gate A rule.
- **Cited, not found:** one row per sheet in "Sheets Cited but Not Found". Each is always "needs check", because a cite can point to a detail, schedule or note that shows the item without its tag. The row states what was searched on that sheet. When an Unmatched_Tags text with the same letters and digits was read there (for example SDCB#1076 for SDCB 1076), the row names it as a variant form.
- **PROPOSED row, printed tag found:** the row's own designation (the text after "PROPOSED-", letters and digits only) equals a printed tag read on the drawings. That tag can be a Ledger tag in Tag_Hits or a text in Unmatched_Tags. It is Verified only when read in the text layer on a sheet the row cites. A looser rule (a tag anywhere in the Name) matched area names, sizes and model numbers, so it is not used.
- **Owner's Division 26 review:** six proposals from Carl's review (2026-09-30). On every run, each evidence line is re-read from the native text layer (Part 3 pp.18, 26, 43; Add. 4 p.1; main spec p.326), and the run stops if one is missing. The lines of one drawing label must sit within 40 pt of each other. The file hashes are checked against `index/Library_Manifest.csv` first.

### Starter MTO

- **Leads:** Quantity_Hits in LF, EA, CY, SF or SY on C0.x, C1.x, C2.x and C7.x. Leads on a base page that Add. 4 supersedes are left out.
- **One callout, one line:** reads on one page with the same unit are one callout when their boxes touch or overlap, or when they carry the same value in the same keyed-note entry. OCR and Bluebeam often read the same text.
- **Tie, in this order:**
  1. The keyed note: a Ledger row whose Drawing Sheets cite "sheet (KN n)". When several rows cite it, the one whose Name holds the quantity.
  2. A Ledger Name quantity on a cited sheet. This includes each term of a written sum ("42 + 19 + 42 LF").
  3. The nearest tag within 24 pt, from Quantity_Hits.
  - If two or more rows fit, all are listed and the line is Unresolved.
- **Counts:** a count read from "N <plural noun>" is kept only when the tied Ledger Name names that noun. This drops, for example, "2 COATS" and "#3 BARS".
- **Confidence** is the weakest of three levels:
  - The best read: text layer Verified; OCR or Bluebeam Inferred; Verified-Visual once Spot_Check marks it.
  - The keyed-note number level, when the tie uses it.
  - The tie itself: distance only is Inferred; ambiguous is Unresolved.
- **Ready = Y** only for Verified or Verified-Visual.
- **Earthwork (owner's decision):** the C0.2 cut and fill totals are MTO lines with no Ledger ID. They carry Bid Item 1 (Inferred: 04 puts work not itemized elsewhere in Item 1) and the Tie Basis "new row needed". Both are also proposed rows in New_Row_Candidates.csv.
- **Held:** callouts with no tie, or with reads that disagree on the value, are listed in Summary.md and are not in the MTO. The C2.1 fence notes are held pending the owner's decision.
- **Segment sums** (Summary.md only): two callouts on a cited sheet whose values add up to a quantity the Ledger Name states. At least one must be untied. This is arithmetic, so it is Inferred, and nothing is tied by it.

### Needs_Check

- The crop box is the reads plus the keyed-note entry, or the tied tag, padded 24 pt and clipped to the page.
- **Panel schedules** (E6.2 MDP, LP1 and LP2; E2.2 LP1) are embedded images, and the text layer holds only their titles. The crop box is the image directly above the title, plus the title.
- The owner fills Human Result, Checked By and Date. Only the owner marks a read Verified-Visual.
