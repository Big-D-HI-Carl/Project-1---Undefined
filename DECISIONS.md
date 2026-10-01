# Decisions

Append-only. Decisions made by a person, in the format in AGENTS.md. Never edit or delete a past entry.

## 2026-09-30 — Bluebeam OCR copies count as OCR (Inferred) and are a comparison column only
- Decided by: Carl
- Why: Stated in this session: "In Prompt 6, their text counts as OCR (Inferred), never as a text layer. Text-layer reads come only from the native files in library/. Use these copies as the comparison column only." Also chose to carry the rule into AGENTS.md (Output standards and Layout).
- Replaces: none

## 2026-09-30 — The root Library/ upload is a one-pass inbox, sorted by move only
- Decided by: Carl
- Why: Stated in this session: "Everything I just uploaded is in library/ at the repo root. Treat it as an inbox for this one pass: sort it, move only, change no file contents or names." Also chose "Map now, check 05 later", because `prompts/05_repo_cleanup.md` wasn't in the repo. This is a one-time exception to hard rule 2, and only for the files in the root `Library/` folder.
- Replaces: none

## 2026-09-30 — Restore the repo infrastructure file names
- Decided by: Carl
- Why: Stated in this session: "Yes, restore the names, in their own first commit. They're repo infrastructure, not sources." The existing root README.md (the Merge rev2 README) moves to `testbeds/eastsound/project/` first. Then README (2).md → README.md, download → .gitattributes, download (1) → .gitignore, settings.json → .claude/settings.json.
- Replaces: none

## 2026-09-30 — Unzipped lane packages go in lanes/<lane>/as-delivered/
- Decided by: Carl
- Why: Stated in this session: "Lane packages → testbeds/eastsound/lanes/<lane>/as-delivered/, keeping the dry-run structure where all 3,612 links resolve."
- Replaces: none

## 2026-09-30 — Add as-delivered/ and _unsorted/ to the AGENTS.md Layout; restore the test-bed README
- Decided by: Carl
- Why: Stated in this session: "Yes to the AGENTS.md Layout edit, as its own commit. Also restore testbeds/eastsound/README.md from 8039650:README.md in a separate commit, if that blob is the test-bed README."
- Replaces: none

## 2026-09-30 — The repo stays public
- Decided by: Carl
- Why: Stated in this session: "public repo is fine", and for the record: "The repo stays public." Prompt 1's private-repo stop is removed to match.
- Replaces: none

## 2026-09-30 — Root README is the kit's program README plus a pointer to the test bed
- Decided by: Carl
- Why: Stated in this session: "Make README (2).md the root README instead of the Step 4 rebuild. Add one line pointing to testbeds/eastsound/." Also: "Save the prompt as prompts/05_repo_cleanup.md."
- Replaces: none

## 2026-09-30 — Reorg layout conflicts settled per AGENTS.md; the rest stay open
- Decided by: Carl
- Why: Stated in this session: "Test bed tools go to testbeds/eastsound/tools/, per AGENTS.md." "Library_Fingerprint*.csv go to testbeds/eastsound/process/, per AGENTS.md." "library/ holds source documents plus .md notes beside them. AGENTS rule 2 governs; my \"source documents only\" line was wrong." "graph/ vs graphify-out/, transfer/, the separate-repo question, where the Missing_Pages PNGs go, Library_Manifest.csv: no files exist for these yet. List them as open decisions in the reorg report; don't create folders for them."
- Replaces: none

## 2026-09-30 — Restore the lane READMEs; keep the C&G duplicate and the kit test-bed README as they are
- Decided by: Carl
- Why: Stated in this session: "B–E. As recommended." (E: restore the three overwritten lane package READMEs from history.) "Leave the Contract & General duplicate where it is." "Keep the kit's text in testbeds/eastsound/README.md and append a short \"Folders\" section: one line per folder as it actually exists on main."
- Replaces: none

## 2026-09-30 — AGENTS.md: .docx reading copies in process/; owners for derived/ and _unsorted/
- Decided by: Carl
- Why: Stated in this session: "AGENTS rule 5: allow .docx only as a reading copy in process/." "AGENTS layout: derived/ is owned by the lane that writes each subfolder; _unsorted/ is owned by Carl." On the wording "each subfolder is owned by the lane that writes it; bluebeam-ocr/ is owned by Carl": "Yes, use that wording for derived/." On Prompt 1: "Yes, replace \"Repo is private\" with \"The repo stays public.\""
- Replaces: none

## 2026-09-30 — The three native plan-set parts are the library's drawing set
- Decided by: Carl
- Why: Stated in this session: "The three native parts are the library's drawing set. Don't wait for the 26 plans_N extracts." plans_N citations resolve through `testbeds/eastsound/index/Plan_Set_Crosswalk.csv`.
- Replaces: none

## 2026-09-30 — Division 26 extract not uploaded; main spec governs
- Decided by: Carl
- Why: Stated in this session: "div-26-electrical-specs.pdf: not needed. The register marks it a duplicate and lanes cite the main spec. Record in DECISIONS.md, decided by Carl: \"Division 26 extract not uploaded; main spec governs.\""
- Replaces: none

## 2026-09-30 — Library_Fingerprint.csv stays as the record of the converted copies; natives go in Library_Manifest.csv
- Decided by: Carl
- Why: Stated in this session: "Don't edit Library_Fingerprint.csv; it records the Claude Project's converted copies. Write index/Library_Manifest.csv for the natives: path, bytes, SHA-256, page count, and source URL where known."
- Replaces: none

## 2026-09-30 — Bluebeam OCR hits go into Tag_Hits and Quantity_Hits, still Inferred
- Decided by: Carl
- Why: Stated in the Prompt 7 rev1 amendments: "Bluebeam block: take the render-mode-3 text in the OCR copies, minus any word that matches a native word in the same spot. Bluebeam reads all 10 SDCB labels on C2.1, so its hits go into Tag_Hits and Quantity_Hits as method bluebeam-ocr, still Inferred. Log this as my decision; it replaces the comparison-only rule of 2026-09-30."
- Replaces: 2026-09-30 "Bluebeam OCR copies count as OCR (Inferred) and are a comparison column only". Only the comparison-only part is replaced; Bluebeam text stays Inferred and never counts as a text layer.

## 2026-09-30 — OCR lane: OCR every page; no thin-page gate
- Decided by: Carl
- Why: Stated in the Prompt 7 rev1 amendments: "Drop the thin-page gate. OCR every page and merge the result with the text layer by box overlap; the text layer wins where both exist." 01's 300-character threshold was measured on the Claude Project image bundles, not the natives. Mid-session: "keep both passes on every page and merge by overlap with the higher confidence."
- Replaces: none

## 2026-09-30 — Spot_Check.csv columns
- Decided by: Carl
- Why: Stated in this session: "Use Spot_Check_Schema's 12 columns first, in this order: Pick No., Ledger Row, Tag, Name, What to Check, Source Citation, Confidence Tag, Read Method, Human Result, Checked By, Date, Note. Then append: Set Page, BBox (pt), Word Read, Confidence, Crop Path." Also: "Human Result and Checked By stay blank."
- Replaces: none

## 2026-09-30 — OCR lane Gate A: tag search and assignment rules
- Decided by: Carl
- Why: Stated in this session:
  - "Short forms (3 characters or fewer, e.g. TS, DB, LT, L1, X1, T2) count as hits only on the row's cited sheets. Anywhere else, list them in the crosswalk as "off-citation, short form" and leave them out of the found counts."
  - "Shared forms: assign each hit to the row whose Lane matches the sheet's discipline (SD-1 on C sheets → Civil row; on E sheets → Electrical row). If that still doesn't settle it, list every candidate row and mark the hit ambiguous."
  - "Keep "(E)" as a qualifier. A hit counts for GEN (E) only when "(E)" or "EXIST" is on the same line; otherwise it counts for GEN."
  - "Ranges: a hit goes to the individual row first (F1…F4); the range row gets the rollup."
  - Unmatched-tag shapes: "OK."
- Replaces: none

## 2026-09-30 — OCR lane Gate A: quantity patterns and nearest-tag distance
- Decided by: Carl
- Why: Stated in this session:
  - "Keep FT as its own unit. Only L=nnn' converts to LF. A foot mark before a material word (6' CHAIN LINK) is a dimension, not a quantity."
  - "Count "@ n%" after an LF quantity as a slope (profiles: 39 LF @ 0.5%)."
  - "Accept units attached with no space (21LF)."
  - "Add SUMP to the elevation keywords."
  - "Nearest-tag distance: 24 pt edge to edge. OK."
- Replaces: none

## 2026-09-30 — OCR lane Gate A: keyed-note numbering levels
- Decided by: Carl
- Why: Stated in this session: "Keyed notes: OK. Every "by order" number is Inferred. If a sheet's entry count doesn't match its highest marker read, mark that sheet's by-order numbers Unresolved."
- Replaces: none

## 2026-09-30 — OCR lane Gate A: PROPOSED anchor levels and the match term
- Decided by: Carl
- Why: Stated in this session:
  - "Verified: the anchor was found in the native text layer and its text contains the row's quantity, or a key noun from the Ledger Name."
  - "Inferred: the same match, read by OCR or Bluebeam."
  - "Unresolved: the anchor wasn't found, or it was found but its text doesn't match."
  - Follow-up: "when the Ledger row has a quantity, the match needs the quantity (value + unit), not just a noun. Use a noun match only for rows with no quantity, and only with nouns that aren't generic (not PIPE, VALVE, CONCRETE, FENCE, WALL, LINE, and the like). Record the matched term in the crosswalk, and put the stopword and generic-noun lists in the README so I can review them."
- Replaces: none

## 2026-09-30 — OCR lane: sheet-only anchors are Verified only for a quantity in the text layer
- Decided by: Carl
- Why: Stated in this session: "Tighten sheet-only anchors: a row with no KN/Det/Add. anchor can be Verified only when its quantity (value + unit) is found on the cited sheet in the text layer. A noun match anywhere on the sheet is Inferred ("on sheet, location not pinned"). Report the new counts per anchor and per row."
- Replaces: the sheet-only part of 2026-09-30 "OCR lane Gate A: PROPOSED anchor levels and the match term".

## 2026-09-30 — The OCR extractor moves to testbeds/eastsound/tools/; cited_as and source checks come from index/
- Decided by: Carl
- Why: Stated in this session: "Move tools/extract_drawing_text.py to testbeds/eastsound/tools/ with git mv (DECISIONS.md puts test bed tools there) and update any path it records." And: "Take cited_as from index/Plan_Set_Crosswalk.csv. Check every source SHA-256 against index/Library_Manifest.csv and stop on a mismatch."
- Replaces: none

## 2026-09-30 — AGENTS.md: OCR copies are Inferred only and may feed tag and quantity leads
- Decided by: Carl
- Why: Stated in this session: "AGENTS.md: approved as proposed: "OCR copies are Inferred only. They may feed tag and quantity leads (method bluebeam-ocr), never a text layer or a Verified read." Update the Bluebeam README to match."
- Replaces: the AGENTS.md sentence "OCR copies are a comparison column only" (see also 2026-09-30 "Bluebeam OCR hits go into Tag_Hits and Quantity_Hits, still Inferred").

## 2026-09-30 — Only the Audit_Ledger and Spot_Check schemas are missing; Carl uploads them
- Decided by: Carl
- Why: Stated in this session: "Schemas: Ledger_Schema.csv and Requirements_Schema.csv are already in index/. Only Audit_Ledger and Spot_Check are missing; I'll upload them. Correct the ISSUES_LOG entry."
- Replaces: none

## 2026-09-30 — checks.py: the ledger check covers only Ledgers under project/ and lanes/
- Decided by: Carl
- Why: Chose "Narrow the checks.py glob" when `derived/ocr/Ledger_Crosswalk.csv` failed the ledger rule. The option read: "Change is_ledger() to cover only Ledger files under project/ and lanes/, in its own commit".
- Replaces: none

## 2026-09-30 — Replace the bad branch-update commit on the OCR lane branch
- Decided by: Carl
- Why: Stated in this session: "Let the test that's running finish, then follow the status brief and addendum to replace the bad commit on this branch and push." The commit is a8694d8, the GitHub "Update branch" merge that dropped main's log entries. It was replaced with a force-push (with lease), a one-time exception to AGENTS.md rule 8.
- Replaces: none

## 2026-09-30 — The repo stays public; public-source material and repo-work notes only until Big-D approves this host
- Decided by: Carl
- Why: Stated in `prompts/01_bootstrap_guardrails.md` §7, which Carl had this session run: "The repo stays public. Public-source material and repo-work notes only until Big-D approves this host." It restates the earlier 2026-09-30 entry "The repo stays public" and adds the data limit.
- Replaces: none

## 2026-09-30 — AGENTS.md is the canonical rulebook; CLAUDE.md imports it; Claude Code auto memory is off
- Decided by: Carl
- Why: Stated in `prompts/01_bootstrap_guardrails.md` §7, which Carl had this session run: "AGENTS.md is the canonical rulebook; CLAUDE.md imports it; Claude Code auto memory is off for this repo."
- Replaces: none

## 2026-09-30 — Enforcement lives in tools/checks.py (hook and CI), not in instruction files
- Decided by: Carl
- Why: Stated in `prompts/01_bootstrap_guardrails.md` §7, which Carl had this session run: "Enforcement lives in tools/checks.py (hook and CI), not in instruction files."
- Replaces: none

## 2026-09-30 — The graph backbone is built from the Ledger by script with no LLM; graphify's LLM pass is an optional, labeled overlay
- Decided by: Carl
- Why: Stated in `prompts/01_bootstrap_guardrails.md` §7, which Carl had this session run: "The graph backbone is built from the Ledger by script with no LLM; graphify's LLM pass is an optional, labeled overlay."
- Replaces: none

## 2026-09-30 — The Setup role creates the Audit_Ledger and Spot_Check schema CSVs
- Decided by: Carl
- Why: Stated in this session: "Create Audit_Ledger_Schema.csv and Spot_Check_Schema.csv in index/ as header-only files, matching Ledger_Schema.csv's encoding and line endings." Carl gave both column lists in the same message.
- Replaces: the upload step of "Only the Audit_Ledger and Spot_Check schemas are missing; Carl uploads them" (2026-09-30)

## 2026-09-30 — Ledger graph: Prompt 3 parsing rules approved; Lane and Bid Item are item attributes, not linked nodes
- Decided by: Carl
- Why: Carl, answering the Prompt 3 step 2 proposal: "Lane and Bid Item: keep them as item attributes, not linked nodes." and "Go ahead." The rules are listed in `testbeds/eastsound/graph/README.md`.
- Replaces: none

## 2026-09-30 — Graph build writes: outputs in graph/graphify-out/, the script edited in place, and testbeds/eastsound/.graphifyignore
- Decided by: Carl
- Why: Carl: "Writes approved (my request): outputs to testbeds/eastsound/graph/graphify-out/, edit testbeds/eastsound/tools/ledger_to_graph.py in place, and add testbeds/eastsound/.graphifyignore."
- Replaces: none

## 2026-09-30 — .graphifyignore lists library/ and derived/bluebeam-ocr/
- Decided by: Carl
- Why: Carl: ".graphifyignore: library/ and derived/bluebeam-ocr/."
- Replaces: none

## 2026-09-30 — Repeated Ledger Tags are keyed <Tag> [L<line>] until the Ledger ID column lands
- Decided by: Carl
- Why: Carl: "Repeated tags: key them as <Tag> [L<line>] for now. A permanent Ledger ID column is coming from Prompt 9; note in the README that the key switches to the ID when it lands."
- Replaces: none

## 2026-09-30 — Graph commands run under env -i; the twelve over-tagged Ledger rows are logged, not edited
- Decided by: Carl
- Why: Carl: "Running under env -i: yes. Log the 12 over-tagged rows in ISSUES_LOG; don't touch the Ledger."
- Replaces: none

## 2026-09-30 — No same_tag link between the two SD-1 rows in the Ledger graph
- Decided by: Carl
- Why: Carl: "Drop the 'same tag' link between the two SD-1 rows. It creates false path traces, and the Ledger ID from Prompt 9 will replace it."
- Replaces: the same_tag part of "Repeated Ledger Tags are keyed <Tag> [L<line>] until the Ledger ID column lands" (2026-09-30), for SD-1 only

## 2026-09-30 — Every Ledger row gets a permanent Ledger ID; everything links by ID
- Decided by: Carl
- Why: Stated in this session (Prompt 9, decision A): "Every Ledger row gets a permanent Ledger ID (L-0001 onward, in current row order). Tags stay exactly as printed. Everything links by ID. SD-1 stays two rows with two IDs."
- Replaces: none

## 2026-09-30 — The starter MTO is a civil pilot: sheets C0–C2 and C7
- Decided by: Carl
- Why: Stated in this session (Prompt 9, decision B): "Starter MTO, civil pilot only: sheets C0–C2 and C7."
- Replaces: none

## 2026-09-30 — AGENTS.md Layout lists derived/reconciliation/
- Decided by: Carl
- Why: Stated in this session: "If AGENTS.md's Layout doesn't list that folder, add one line for it in its own commit; this is my request under rule 8."
- Replaces: none

## 2026-09-30 — One total Quantity per Ledger row; segments live in the MTO
- Decided by: Carl
- Why: Stated in this session: "Quantity per row: one total Quantity per Ledger row; segments live in the MTO as separate lines (SD-1: three MTO lines, Ledger total 103 LF). Put this answer in the schema proposal."
- Replaces: none

## 2026-09-30 — The C0.2 earthwork totals go in the starter MTO and are proposed as new Ledger rows
- Decided by: Carl
- Why: Stated in this session: "Earthwork: don't hold out C0.2 cut 3,382 CY / fill 1,598 CY. Add them to Starter_MTO.csv with Ledger ID blank, the bid item, and "new row needed" in Tie Basis, Ready = N. Also add them to New_Row_Candidates.csv as proposed Ledger rows."
- Replaces: none

## 2026-09-30 — The reconciliation script lives in testbeds/eastsound/tools/
- Decided by: Carl
- Why: Stated in this session: "Put the script at testbeds/eastsound/tools/build_reconciliation.py (DECISIONS: test bed tools live there). This is my request; outputs stay in derived/reconciliation/."
- Replaces: none

## 2026-09-30 — The open-items list lives in derived/issues/, built by testbeds/eastsound/tools/build_open_items.py
- Decided by: Carl
- Why: Stated in this session: "Your folder: testbeds/eastsound/derived/issues/. Script: testbeds/eastsound/tools/build_open_items.py (my request)."
- Replaces: none

## 2026-09-30 — Open-items rules approved: RFI typing, PROPOSED approvals left out, weakest-tag confidence
- Decided by: Carl
- Why: Stated in this session: "Your three judgment calls are approved as-is (RFI typing, leaving out the 312 PROPOSED approvals, weakest-tag confidence)."
- Replaces: none

## 2026-09-30 — Graph note text is each note's full Project Wiki body, cut at the last full sentence before 2,000 characters
- Decided by: Carl
- Why: Stated in this session: "Note text: use each note's full body from Project_Wiki.md (via Heading Line), cut at the last full sentence before 2,000 characters, instead of the 600-character summary."
- Replaces: none

## 2026-09-30 — In the graph, duplicate open items and open items naming more than 15 Ledger IDs get no item links
- Decided by: Carl
- Why: Stated in this session: "Open items: duplicate-type items and any open item listing more than 15 Ledger IDs keep their node but get no item links; list the IDs on the node instead. Other open items keep their links."
- Replaces: none

## 2026-09-30 — AGENTS.md Layout lists derived/wiki/ and derived/issues/
- Decided by: Carl
- Why: Stated in this session: "Add AGENTS.md Layout lines for derived/wiki/ and derived/issues/ in their own commit (my request under rule 8)."
- Replaces: none

## 2026-10-01 — Project Ledger rev1 is the expanded MTO: one row per component, columns in bands A–I
- Decided by: Carl
- Why: Stated in this session (Prompt 10): "Project Ledger rev1, the expanded MTO. One row per component; scroll left to right from "what and where" to everything connected to it." Rules: "keep all 447. Add a new component only if it has (a) a page: read on a sheet, with set page and box; (b) a CWP, assigned by the same rule the by-CWP Ledger uses; (c) at least one connected document: spec section, register entry, or a Wiki note naming it. Everything else goes to a Candidates tab with the reason. Never add I/O points, areas, standards or drawing references." "No unexplained blanks: "None found" when searched and empty, "Not linked" when the source doesn't cover it; counts show 0." "Every link carries its basis: tag (direct), spec (applies to the section) or sheet (same sheet). Direct links first." "Quantities only from evidence-backed MTO lines … EA for each tagged component found on one of its cited sheets. No dimensions, elevations, slopes or sizes. No double counting; Add. 4 governs. Totals use Verified lines only." "Each row keeps the weakest confidence of its key facts, as today."
- Replaces: none

## 2026-10-01 — Ledger schema rev1, the checks.py Ledger ID rule and the graph rebuild are authorized
- Decided by: Carl
- Why: Stated in this session (Prompt 10): "Your folders: new files in testbeds/eastsound/project/02_Project_Ledger/ (rev0 files untouched) and the script testbeds/eastsound/tools/build_ledger_rev1.py. Also authorized, each in its own commit (my request under rule 8): add index/Ledger_Schema_rev1.csv; update checks.py so the ledger rule accepts schema rev1 and checks unique Ledger ID instead of unique Tag; rebuild the graph from rev1."
- Replaces: none
