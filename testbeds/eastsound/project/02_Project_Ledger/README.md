# 02_Project_Ledger — Project Ledger

**Current Ledger: `Project_Ledger_rev2.csv` and `Project_Ledger_rev2.xlsx`** (Prompt 11, 2026-10-01). Use rev2 for lookups, the MTO and the graph. rev0 and rev1 stay here, unchanged, as history.

## Current: rev2

| File | What it holds |
|---|---|
| Project_Ledger_rev2.csv | 529 rows × 39 columns in `index/Ledger_Schema_rev1.csv` order. UTF-8 without a BOM; open it in Excel through Data > From Text/CSV, or use the .xlsx |
| Project_Ledger_rev2.xlsx | Tabs Ledger, MTO Lines, Totals, Coverage, Candidates, Column Guide, Links. The Ledger tab adds "Total incl. reads to verify" beside Quantity |
| MTO_Lines_rev2.csv | 190 MTO lines (machine copy of the MTO Lines tab; the graph build reads it) |
| Ledger_rev2_Summary.md | Changes applied, fill rate per band rev0 → rev1 → rev2, rows added, both totals, tie-outs, input SHA-256 values |

- **Rows:** the 449 rev1 rows in rev1 order, plus the 80 conduit and feeder runs from the E6.3 schedules (L-0450 to L-0529). Ledger IDs are permanent.
- **Totals:** Verified-only is the headline, in the Quantity column: 150 EA. The total incl. reads to verify (168 EA, 949 LF) adds the lines held back only because their read is Inferred or Unresolved. A person confirms those reads on the page image.
- **Not counted in any total:**
  - L-0337 and L-0338 are duplicates of L-0057 and L-0058. Status says so, and their links are on the twin.
  - L-0448 and L-0449 (earthwork) are reference only (C0.2: not for bidding or take-off).
- **Rebuild:** `python testbeds/eastsound/tools/build_ledger_rev2.py` from the repo root, with the packages in `requirements.txt` installed. No LLM calls, and two runs give identical files. The run stops without writing if a tie-out fails.

## History

| Revision | Files | Built by | Notes |
|---|---|---|---|
| rev1 (Prompt 10) | Project_Ledger_rev1.csv, .xlsx, MTO_Lines_rev1.csv, Ledger_rev1_Summary.md | `tools/build_ledger_rev1.py` | The expanded MTO: 449 rows, columns in bands A–I |
| rev0 (Merge rev2) | Project_Ledger.csv, .xlsx | Merge thread | 447 rows in `index/Ledger_Schema.csv` columns |
| rev0 by CWP | Project_Ledger_by_CWP.csv, .xlsx | Merge thread | rev0 divided into 19 CWPs; its CWP rules still assign CWPs to new rows |

Don't edit these files by hand. Changes come in as a new revision built by script, so the history shows each one.
