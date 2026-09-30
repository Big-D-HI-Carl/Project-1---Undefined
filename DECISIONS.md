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
