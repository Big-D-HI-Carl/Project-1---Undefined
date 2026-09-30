@AGENTS.md

## Claude Code specifics
- Start any multi-file task in plan mode; don't edit until I approve the plan.
- `.claude/settings.json` denies edits to source files (PDFs and images) inside `library/` folders; `.md` notes beside them are allowed. Don't route around a deny rule with shell commands (cp, mv, rm, sed, git mv, git rm). If a task seems to need it, stop and ask.
- Auto memory is off for this repo so Codex and other agents work from the same rules. When I give a correction that should stick, propose the edit to AGENTS.md.
- Keep this file short. Rules belong in AGENTS.md.
