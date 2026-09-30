# Prompt 1 — Bootstrap and guardrails

Run from the repo root. Claude Code: put /plan in front of this prompt, review the plan, then approve. Other agents: ask for a plan first.

Read AGENTS.md in full before planning. Goal: stand up the repo so every rule marked (checked) in AGENTS.md is enforced by code. No project content this session.

## 1. Confirm state — stop on any surprise
- Run `git status`, `git remote -v`, `git log --oneline -5`. Expect branch `main`, remote `origin` pointing at Big-D-HI-Carl/Project-1---Undefined, and the baseline already committed (by Prompt 0 or a web upload).
- Check visibility with an unauthenticated GET to `https://api.github.com/repos/Big-D-HI-Carl/Project-1---Undefined` (Python urllib, no token). 404 means private: continue. 200 means public: stop and tell me. 403 means rate-limited: ask me to confirm the repo shows Private in its settings. Commit nothing while it's public.

## 2. Layout and logs
- The baseline already has the layout, the three logs, `.gitignore`, `.gitattributes` and both READMEs. Create only what's missing from the AGENTS.md layout, and don't change any baseline file.
- `.gitattributes`: keep the byte guard exactly as it is. If the line `.githooks/* text eol=lf` is missing, append it.

## 3. tools/checks.py — Python 3.10+, stdlib only
Modes: `--staged` (hook; read staged content with `git show :<path>`, not the working copy), `--range BASE..HEAD` (CI), `--all` (whole tree, file-level checks only). One output line per violation: rule, path, reason. Exit 1 on any violation.

Checks:
- **Read-only sources:** any modified, deleted, renamed, copied or type-changed path under a `library/` folder fails, except `.md` notes. Added files pass.
- **Append-only logs:** any removed or changed line in the three log files fails. Pure additions pass.
- **Ledgers** (`*Ledger*.csv`, except `Ledger_Schema.csv`): UTF-8 with no BOM; header identical to `testbeds/eastsound/index/Ledger_Schema.csv`; every row has the header's field count; `Tag` non-empty and unique within the file; the `Verified/Verified-Visual/Inferred/Unresolved` column starts with one of those four words. If the schema file isn't in the repo yet, skip ledger checks with one warning.
- **Unsafe files:** over 50 MB; names matching `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa*`, `*credential*`; anything under `_inbox/`.
- **Data gate:** if `.datagate/blocklist.txt` exists (one term per line, local only), scan staged text files (`.md .csv .txt .json .py .yml .yaml`) case-insensitively. A hit fails with path and line number. Never print the matched term: hook output lands in the agent's context. No blocklist: one warning, pass. CI skips this check.
- **Known exceptions:** `tools/check_exceptions.csv` (path, rule, ISSUES_LOG entry title). A listed path + rule warns instead of failing. Adding a row requires the matching ISSUES_LOG.md entry in the same commit.

## 4. Hook and CI
- `.githooks/pre-commit`: short sh shim that finds a working Python (`python3`, then `python`, then `py -3`) and runs `tools/checks.py --staged`. Run `git config core.hooksPath .githooks` and mark the hook executable in git (`git update-index --chmod=+x`).
- `.github/workflows/checks.yml`: on push and pull request, full-history checkout, run `--range` over the pushed commits (first push: the before-SHA is all zeros, so run `--all` only), then `--all`.

## 5. README.md
README.md is in the baseline. Leave it, unless the lines about running checks or setting `core.hooksPath` are missing; then add only those.

## 6. Acceptance tests
Run in a throwaway clone under the system temp folder, never in this repo. Report a table: test | expected | actual.
1. Edit a file under `testbeds/eastsound/library/` → blocked
2. Delete a file there → blocked; add a new file there → passes; add, then edit, a `.md` note beside a source → passes
3. Change an old line in PROGRESS_LOG.md → blocked; append a line → passes
4. Ledger with a BOM → blocked; wrong header → blocked; duplicate Tag → blocked; tag column "Maybe" → blocked; "Unresolved: external reference, not staged" → passes; valid 2-row ledger → passes
5. 60 MB file → blocked; `.env` → blocked; file under `_inbox/` staged with `git add -f` → blocked
6. Blocklist containing TESTTERM; staged .md containing it → blocked, and TESTTERM does not appear in the output
7. A library edit committed with `--no-verify` (test clone only) → caught by `--range HEAD~1..HEAD`
8. An exceptions row for test 4's BOM file, with its ISSUES_LOG entry → warns, passes
9. Run `--all` on the committed baseline in this repo. A failure in a baseline file is a finding: don't edit the file; add an exceptions row with an ISSUES_LOG.md entry and list it for me.

Any failure: append the failure mode and fix to ISSUES_LOG.md, fix, rerun all tests.

## 7. Record, then stop before the push
- Append to DECISIONS.md, decided by Carl:
  - Repo is private. Public-source material and repo-work notes only until Big-D approves this host.
  - AGENTS.md is the canonical rulebook; CLAUDE.md imports it; Claude Code auto memory is off for this repo.
  - Enforcement lives in tools/checks.py (hook and CI), not in instruction files.
  - The graph backbone is built from the Ledger by script with no LLM; graphify's LLM pass is an optional, labeled overlay.
- Commits in this order: checks and hook; CI; baseline exceptions, if any; anything else this session added.
- Run prompts/close_session.md but stop before the push. Show `git log --oneline` and `git diff --stat origin/main`. I'll reply "push".
