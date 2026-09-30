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
