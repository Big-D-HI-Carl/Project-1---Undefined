# Ledger schema rev1: proposal

Status: **proposal only.** `testbeds/eastsound/index/Ledger_Schema.csv` (Setup role) and `tools/checks.py` are unchanged. This file sets out what rev1 would be. It covers owner decision A (permanent Ledger IDs) and the owner's quantity-per-row answer (2026-09-30), and lists what else would change once rev1 is approved.

## Header

Current (rev0, 16 columns, `index/Ledger_Schema.csv`):

```
Tag,Name,Bid Item,Lane,Area/Building,Discipline,Drawing Sheets,Spec Sections,Addenda,Submittal Req (Y/N),Testing/Startup Req (Y/N),Wiki Note(s),Status,Verified/Verified-Visual/Inferred/Unresolved,Source Citation,Notes
```

Proposed (rev1, 19 columns): Ledger ID first, the 16 unchanged in their current order, then Quantity and Unit.

```
Ledger ID,Tag,Name,Bid Item,Lane,Area/Building,Discipline,Drawing Sheets,Spec Sections,Addenda,Submittal Req (Y/N),Testing/Startup Req (Y/N),Wiki Note(s),Status,Verified/Verified-Visual/Inferred/Unresolved,Source Citation,Notes,Quantity,Unit
```

## New columns

| Column | Content | Rules |
|---|---|---|
| Ledger ID | `L-` and four digits, e.g. `L-0073` | Required and unique. Assigned once and never reused or renumbered. It is the key every other file links by. |
| Quantity | One total for the row, as a plain number (`103`, `3382`, `0.5`) | No units, commas or ranges. Blank when the documents give no quantity. |
| Unit | One of LF, EA, CY, SF, SY, FT, GAL, TON, LS | Required when Quantity is set; blank when it is blank. FT is its own unit (Gate A: only `L=nnn'` converts to LF). |

## Rules

- **Ledger ID assignment (decision A).** The first issue numbers the current 447 records L-0001 to L-0447 in current row order (`Ledger_ID_Map.csv`).
  - L-0001 is the first record. The OCR crosswalk and `ledger_to_graph.py` call it Ledger Row 2, so Ledger ID = L-(Ledger Row − 1).
  - A new row takes the next unused number.
  - A row that is merged or withdrawn keeps its ID. Its Status records what happened, and the ID is never given to another row.
  - Sorting or re-grouping rows never changes an ID.
- **The key is the Ledger ID, not the Tag.** Tags stay exactly as printed, so two rows may share a Tag when the drawings use one tag for two items. SD-1 stays two rows: L-0073 (storm drain alignment) and L-0315 (3 HP sludge pump). A PROPOSED- tag stays until a printed tag is found. Then the Tag changes and the ID does not.
- **One total Quantity per row (owner's answer).** The Ledger row holds the item's total. Segments live in the MTO as separate lines, each keyed to the row's Ledger ID.
  - Example: SD-1 (L-0073) is three MTO lines, 42 + 19 + 42 LF on C2.2. The Ledger Quantity is 103 LF.
  - The Source Citation names the MTO lines, or the drawing callout when the drawings print the total.
- **Tag level.** A row's tag stays the weakest tag of its facts, and the quantity is one of those facts. A total the drawings print takes the level of that read. A total summed from MTO lines is derived, so it is Inferred, and the reasoning names the lines (AGENTS.md, Output standards). The owner may set a different rule for sums of Verified lines.
- **Encoding** is unchanged: UTF-8 without a BOM, one header row, every row the full width.

## What else changes when rev1 is approved (none of it done here)

| Where | Change | Owner |
|---|---|---|
| `index/Ledger_Schema.csv` | Issue the 19-column header as rev1 | Setup |
| `project/02_Project_Ledger/Project_Ledger.csv` | New revision. Take the IDs from `Ledger_ID_Map.csv`. Start Quantity and Unit blank; fill them only from approved MTO lines or printed totals. | Merge |
| `tools/checks.py` ledger rule | Check the rev1 header. The "unique non-empty Tag" check becomes "unique Ledger ID in the L-NNNN form, non-empty Tag". Also: Quantity numeric when set; Unit from the list and set exactly when Quantity is. In its own commit, only when a person asks (AGENTS.md rule 8). | Build session, on request |
| `tools/check_exceptions.csv` | Remove the Project_Ledger.csv duplicate-Tag row once the rule keys on Ledger ID. The duplicate SD-1 Tag becomes allowed, and the two influent-sampler rows stay a Merge item. | Build session |
| `testbeds/eastsound/tools/ledger_to_graph.py` | Its node ID is the Tag today, so the two SD-1 rows collapse into one node. Key nodes on Ledger ID and keep the Tag in the label. Edges already carry `ledger_line`. | Build session |
| `derived/ocr/` crosswalk and Tag_Hits | These are keyed on Ledger Row. `Ledger_ID_Map.csv` maps each row to its ID until the next OCR run writes the ID too. | OCR lane |
| `*_by_CWP` views | Carry Ledger ID as the first column after the CWP columns | Merge |

## Open questions for the owner

1. Four digits (`L-0001`) leave room for 9,999 rows. Keep four digits, or use five now?
2. Should lump-sum items carry `1` / `LS`, or stay blank?
3. Should a total summed from Verified MTO lines be Verified or Inferred? This file proposes Inferred, per the "derived" rule.
