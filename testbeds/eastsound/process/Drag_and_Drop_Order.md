# Drag-and-drop order — Project-1---Undefined

## 1. Make the repo private first
At 15:42 UTC on 2026-09-30 it still showed as Public. Settings → General → Danger Zone → Change repository visibility → Private.

## 2. On your PC, fill the empty folders
Unzip this first. Then put your files in:

- `testbeds/eastsound/library/` → all 34 source files, originals with their exact names: the drawing PDFs, both spec PDFs, Addendum 4, the CQA plan, and Missing_Pages_Page_001–004.png.
- `testbeds/eastsound/lanes/<lane>/` → each lane's Wiki, Ledger, Issues and Known Issues files, 4 per lane.
- `testbeds/eastsound/project/` → the Merge outputs; unzip the Merge zip here as-is.
- `testbeds/eastsound/process/` → your two Ultraplan rev1 files (.md and .docx), plus Prompt_1 to Prompt_6 and the original Ultraplan .docx if you have them.

Don't upload claude-code-kit.zip. GitHub stores a zip as one file and doesn't unpack it, and everything from the kit that's still in use is in here, updated.

## 3. On GitHub, in this order
The web uploader takes up to 100 files and 25 MiB per file per upload.

1. Add file → Create new file. Name it `.gitattributes`, paste this zip's `.gitattributes`, and commit.
2. On the repo's main page, drag in everything from `Project-1---Undefined/` except the `testbeds` folder. Commit: "Baseline: rules, prompts, logs". Check that `.gitignore` and `.claude/settings.json` came through.
3. Add file → Create new file. Name it `testbeds/eastsound/README.md`, paste this zip's copy, and commit. That creates the folder.
4. Open `testbeds/eastsound/` and drag in one folder per commit: `library`, `index`, `lanes`, `project`, `process`, `tools`. Commit messages like "Baseline: library, unchanged".
5. Anything over 25 MiB won't upload this way; use GitHub Desktop for those files.

## 4. Check and pin
- Library file sizes on GitHub match your PC.
- Releases → Draft a new release → create the tag `transfer-baseline` → Publish.

## 5. Next
In Claude Code, run `prompts/01_bootstrap_guardrails.md`.
