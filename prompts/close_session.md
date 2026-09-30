# Close session

Run at the end of every session, in any runtime.

1. Stage your work. Run `python tools/checks.py --all`, then `python tools/checks.py --staged`. Both must pass; listed exceptions may warn.
2. If any Ledger CSV or a graph build script changed this session, rebuild the graph with the build step in `testbeds/eastsound/process/Graph_Transfer_Ultraplan.md` and stage the outputs.
3. Append one PROGRESS_LOG.md entry in the AGENTS.md format. Tests lists only commands you actually ran, with their results.
4. Append ISSUES_LOG.md entries for every failure this session (failure mode and fix) and every new finding. Close resolved items by appending a Closed entry that names the original.
5. Append DECISIONS.md entries only for decisions I stated this session, quoted. Your own choices go under Done in the progress entry.
6. Commit: `log: <YYYY-MM-DD> <session title>`.
7. Push the current branch to origin if every check passed and I haven't said "hold". Show `git log --oneline -5` and `git status`.
