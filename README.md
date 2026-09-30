# Project-1---Undefined

This will be a secure online codebase to push updates and keep a general log of progress for the Heavy Industrial AI Implementation Program

- **Rules for any person or agent:** AGENTS.md. Claude Code reads it through CLAUDE.md.
- **First workstream:** the Eastsound test bed in `testbeds/eastsound/`, a public bid set used to prove the Project Wiki + Project Ledger design. Its plans are in `testbeds/eastsound/process/`.
- **Logs (append-only):** PROGRESS_LOG.md, DECISIONS.md, ISSUES_LOG.md.
- **Next step:** run `prompts/01_bootstrap_guardrails.md` in Claude Code. It adds the checks, the git hook and CI.
- **Per clone, once, after that:** `git config core.hooksPath .githooks`
- **Checks:** `python tools/checks.py --all` (whole tree), `--staged` (what the hook runs), `--range BASE..HEAD` (what CI runs). On Windows use `py -3` if `python` isn't found.
- **Data:** no Big-D, client or employee data in this repo until Big-D approves the host.
- **Eastsound test bed:** everything for it lives in `testbeds/eastsound/`; start with `testbeds/eastsound/README.md`.
