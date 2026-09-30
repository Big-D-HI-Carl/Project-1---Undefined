# Prompt 4 — Retrieval test: Wiki, Ledger and graph only

Before sending this, I will create `.claude/settings.local.json` containing:

    {"permissions": {"deny": ["Read(./testbeds/eastsound/library/**)"]}}

Other agents: treat that rule as an instruction.

Goal: prove Phase 1 questions can be answered without opening the library, and find exactly where they can't.

1. Use the test cases in the workflow test log in `testbeds/eastsound/project/`. List them back to me before starting.
2. For each case, graph first: answer with citations and tags; list the files and graph queries used; compare with the Merge thread's result (better, same or worse, and why).
3. If a case needs the library, don't work around it; no shell reads of library files either. Stop that case and log a design gap in ISSUES_LOG.md: what's missing and where it should live (for example paragraph-level capture of timing, acceptance criteria, and hold and witness points, the gap the Merge thread found).
4. Write `testbeds/eastsound/project/Retrieval_Test_<YYYY-MM-DD>.md`: a summary table (case | answered from | result vs Merge | gap), then one section per case.
5. Remind me to delete `.claude/settings.local.json`, then run prompts/close_session.md.
