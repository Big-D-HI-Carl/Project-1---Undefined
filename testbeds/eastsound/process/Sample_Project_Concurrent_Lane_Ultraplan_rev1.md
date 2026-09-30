# Sample Project — Concurrent Lane Ultraplan

- **Version:** rev1, issued 2026-09-30 · **Owner:** Carl Schaefbauer · **Supersedes:** Sample_Project_Concurrent_Lane_Ultraplan.docx (original)
- **Controlled copy:** this Markdown file. It goes in the repo's `process/` folder beside the companion plan. The Word file is a reading copy generated from it.
- **Companion plan:** Graph_Transfer_Ultraplan.md, rev0 (Transfer thread, draft for approval, 2026-09-30). It details the move to GitHub, the script-built graph and the first proof run. This plan is the master: it sets the sequence, the decisions and the exit criteria, and hands the steps it names to the companion.
- **Basis:** the Setup record (03 Coverage Gate rev1), the Composer thread's reconciliation of the original plan, the five lane outputs, and the Merge outputs through 2026-09-30.
- **Not reconciled:** sections 1, 4, 6, 8 and 11 of the original weren't available when rev1 was written. Unresolved: check them against this revision before rev2.
- **Tags:** Verified = read in the named record · Inferred = derived, reasoning stated · Unresolved = conflict or gap, need stated. Items marked "proposed" need Carl's approval.

## 1. Purpose and bar

Prove three things on a public bid set before asking for the SharePoint connection:

1. **The schema** carries what the Phase 1 workflows need.
2. **The crawl prompts** produce cited, tagged Wiki notes, Ledger rows and requirement rows that pass a spot-check.
3. **Two Phase 1 workflows**, the Submittal Register and the Inspection & Test Plan, come from the Wiki and Ledger without rereading the library.

- **Test bed:** Eastsound Sewer and Water District WWTP Upgrade Phase I, Wilson Engineering job 2020-070. Bid set dated Nov 2, 2022 (97 sheets); project manual dated Dec 30, 2022 (645 pages); Addendum No. 4 dated Feb 9, 2023 (13 pages); CQA plan dated Dec 1, 2022. Source: 00 Document Register rev1; Merge drawing controls register.
- **Bar:** proof-of-concept output, not full coverage. There is no material takeoff; everything comes from scanning.
- **Policy:** no Big-D, client or employee data anywhere in this project.

## 2. Design rules

- Outputs are plain files (.md, .csv, .xlsx) that run the same in ChatGPT as in Claude. No Claude-only features.
- Retrieval goes through the Wiki notes, the Ledger and the graph built from them. An answer that needs the whole library is logged as a design gap.
- The library folder structure is fixed. Notes go beside documents; source files are never renamed, moved or edited.
- Every factual claim cites its source (sheet; spec section and paragraph; addendum number and item) and carries a tag: Verified, Verified-Visual, Inferred or Unresolved.
- Addendum 4 governs over base documents; cite both. The body section number governs over running headers. Claims that defer to WSDOT are tagged "Unresolved: external reference, not staged."
- A Ledger row's tag is the weakest tag of its facts. Rev1 gives the bid item its own tag (Step 5).
- When a prompt or workflow fails a test, log the failure mode and the fix before rerunning.

## 3. Status at rev1

| Stage | Result | Record |
|---|---|---|
| Setup | Index files 00–04 at rev1: register, sheet index, spec index, coverage gate, bid item spine. Gate PASS on 2026-09-29 with eight decisions logged (Section 10). | 03 Coverage Gate rev1 |
| Composer | One prompt per lane plus the Merge prompt. When the prompts were simplified, the formal sample grading was replaced by a 5-row check on the first lane. | Composer thread |
| Lanes | Five lanes crawled. Ledger rows: Civil & Site 115, Process & Mechanical 114, Electrical & Controls 126, Structural & Building 45, Contract & General 49. | Lane files; Merge thread |
| Merge | Project Wiki: 202 notes. Project Ledger: 449 lane rows combined to 441, then 447 after the resplit pass, with 123 Unresolved. Exception Report: 571 rows. Issues Log: 87 entries. Project Known Issues: 31 method themes, 139 open document decisions. | Merge thread |
| Phase 1 workflows | Submittal Register (145 lines) and Inspection & Test Plan (103 lines) at first build, from the Wiki and Ledger with no library reads. Timing, acceptance criteria and hold/witness points are missing because the notes summarize instead of capturing paragraphs. | Merge workflow test log |
| Extra outputs | CWP views (19 packages), schedule by CWP, installation tracker, QC requirements page, drawing controls register. Built beyond the plan; not part of the proof. | Merge README |
| Inventory | Resplit sheets C0.3, C2.1, C2.3 and C2.6 read. Still missing: C0.7, C1.1, C1.2, C7.7, C7.8, C7.9 and Addenda 1–3. | Merge thread |
| Companion plan | Graph Transfer Ultraplan rev0 drafted, with library fingerprints (Library_Fingerprint.csv, Library_Fingerprint_Pages.csv). Its counts predate the resplit pass: it uses 441 Ledger rows and 10 missing sheets, now 447 and 6. | Transfer thread files |
| Repo | Claude Code starter kit ready for Big-D-HI-Carl/Project-1---Undefined. The repo read Public on 2026-09-30. | Repo kit |

All rows are Verified in the named records except the Contract & General row count, which is derived: 449 total minus the other four lanes (Inferred).

**Proven so far**

- Five lanes, one merge and two registers ran end to end, with no library reads during the register build (Verified).
- One retrieval question has been tested: drawing-vs-spec precedence (Verified).
- Not yet tested: ChatGPT parity, and the concurrency metric from section 10 of the original plan. No lane wrote a manifest, so there are no run times (Verified).

## 4. Roles and ownership

| Role | Owns (single writer) | Reads |
|---|---|---|
| Carl | Decisions, Exception Report dispositions, PROPOSED tag approvals, GitHub releases | Everything |
| Setup thread | Index files 00–04, resplit list | Library |
| Composer thread | Lane prompts, Merge and workflow prompts, both schemas | Index files, lane outputs |
| Lane threads (5) | Their own Wiki, Ledger, Requirements and Issues files | Their own stack in 01 and 02, plus the Addendum 4 pages 03 cites |
| Merge thread | Project Wiki, Project Ledger, Exception Report, registers | Lane files and index files; the library only to check one disagreement |
| Build session: the Transfer thread or one Claude Code session (Step 1) | The repo's `transfer/`, `tools/` and `graph/` folders and the notes beside source files | Everything it moves; it never edits content it didn't produce |
| Proof thread | Proof reports | Graph, Wiki, Ledger; the library only to verify one page |

## 5. Operating rules

- **Handoff:** only Project files and the repo cross threads. Chat attachments don't.
- **Read check first:** a thread opens every file in its scope before working, and stops if one fails.
- **One writer per file.** Every file names its owner and version in the header.
- **One build session at a time:** a single Transfer thread or Claude Code session writes the repo's build folders.
- **Move first, fix later:** nothing is corrected on the way into the repo. Fixes land afterward as revisions, so the history shows each one (companion rule).
- **Inventory changes route to Setup:** new uploads, corrected sheets, resplits.
- **Save cadence:** write outputs after every 4 documents or every 2 long spec sections.
- **One session per working folder.** In the repo, each concurrent thread works on its own branch and merges by pull request.
- **Issue IDs are lane-prefixed and never reused,** so a re-sent file can't renumber cross-lane items.
- **Logs are append-only:** progress log, decisions, issues log.
- **Manifest per run:** start and end time, documents and pages opened, rows written. It feeds the concurrency and routing metrics.

## 6. Remaining work

Step 1 gates the later steps through its Unblocks column. Steps 2 and 3 measure the system as built; Steps 4–7 fix it and measure again. The inventory track doesn't block the proof.

### Step 1 — Carl's decisions

| Decision | Options | Unblocks |
|---|---|---|
| Companion plan | Approve the Graph Transfer Ultraplan to govern Steps 2 and 3 | Steps 2–3 |
| Repo | The program repo (Big-D-HI-Carl/Project-1---Undefined, made private, test bed in its own folder), or a separate private eastsound-testbed repo in a free organization (the companion's choice). Either works once private. | Step 2 |
| Where the build runs | Claude Code on a local clone (recommended below), or a claude.ai Transfer thread (the companion's choice) | Step 2 |
| PROPOSED tags | Approve the 312 PROPOSED tags (309 at merge plus 3 from the resplit pass, Inferred). Use the printed tag for the 4 that already have one. Re-tag SD-1 and the dewatering tag, which each name two items. | Step 4 |
| Combine rule | Keep it literal, or combine the 77 same-item groups | Step 4 |
| Precedence | Drawings over specs for exception calls (00 73 00, SC 2) | Exception Report dispositions |
| PROPOSED naming rule | One rule for all lanes; the Composer drafts the options | Step 6 |
| Negative checks | Allow a logged keyword search over the text layers for "nothing like X exists" checks, or log each one as a design gap | Steps 3 and 6 |
| Schema changes | Approve Step 5 | Step 5 |
| Pass marks | Proof v1: 8 of 10 (companion). Proof v2: no regression on those 10, plus 5 of 6 on Appendix B (proposed). | Steps 3 and 7 |

**Why Claude Code for the build (Inferred):** threads in this Project share one outputs folder. The Transfer thread's files landed in another thread's outputs on 2026-09-30, the same hazard that split issue numbers in Contract & General (Verified). A local clone gives one writer, commits land directly, and the kit's hooks enforce read-only sources and append-only logs. The companion's case for claude.ai, nothing to install, still holds.

**If Claude Code runs the build:**

- Run kit Prompt 1 (guardrails) first.
- Paste the companion's Transfer thread prompt (its Appendix C) in place of kit Prompts 2 and 3, and its Proof thread prompt (its Appendix D) in place of kit Prompt 4.
- Use the companion's folder names (`graph/`, `process/`, `transfer/`). The kit's `tools/ledger_to_graph.py` seeds the companion's `tools/build_graph.py`.
- Kit fix, done 2026-09-30: the first kit blocked all agent writes inside `library/`, which contradicted "notes beside documents." Agents may now add and edit `.md` notes beside sources; source files stay read-only.

Engineer and owner questions stay logged, not resolved, in a bid-set test bed: Bid Item #18, the permanent generator bid item, the geotech report date, instruments specified in two sections, the 360-working-day limit against the planned schedule, and drawing-vs-drawing conflicts such as the WAS line (3 in vs 2 in) and the chain link fence (149 and 134 LF on C2.1 vs 126 LF on C2.5).

### Step 2 — Transfer and graph v1 (companion Steps 1–7)

- Freeze the Sample Project as the crawl record, collect every thread output, and load the repo exactly as-is, line-ending guard first. Release: transfer-baseline.
- Check the baseline, key every Ledger row, check every reference against the index files, and split the Wiki into one note per file beside its source.
- Build the graph by script with no LLM calls and check it against source counts. Release: graph-v1.
- Refresh the companion's counts at its Step 4: 447 Ledger rows, not 441, and 6 missing sheets, not 10, after the resplit pass. The expected counts in its question set may shift too.
- Pass: the companion's "what done looks like" (its section 2), with the refreshed counts.

### Step 3 — Proof v1 (companion Step 8)

- Rebuild the Submittal Register and Inspection & Test Plan through graph, Wiki and Ledger, and compare them with the Merge baseline of 145 and 103 lines.
- Answer the companion's 10 questions (its Appendix E). Score each on four points: answered from graph, Wiki and Ledger (yes, partly or no); a citation on every fact; library pages opened; whether a bulk read was needed.
- ChatGPT check: the same package and questions in ChatGPT, or Codex on the repo.
- Pass: registers match or every difference is explained, with zero library opens; at least 8 of 10 questions fully answered with citations and no bulk reads; ChatGPT returns the same items, sheets, sections and counts.
- This run is the baseline. Timing, acceptance and hold/witness gaps are expected here; Steps 5–7 close them.

### Step 4 — Tag crosswalk

- Apply the Step 1 tag decisions and combine rule. Each "possible same item" pair becomes one node; rebuild the graph.
- Pass: zero double-counted items (244 today), and every combined item traces to both source rows.

### Step 5 — Schema rev1 (Composer; the companion calls it schema v2)

Ledger schema:

- Add **Quantity** and **Unit**. "Not stated" is allowed; this bid set has no takeoff.
- Add **Bid Item Tag**. Bid items are assigned from the 04 spine; where that link is Inferred (Bid Item 1, for example), the weakest-tag rule kept the whole row off Verified (Process & Mechanical finding). The row tag becomes the weakest of the other facts.
- Define **Testing/Startup Req (Y/N)**: Y = the documents require a test, inspection or start-up for the item (cite it); N = checked, none required; Not stated = not checked. Proposed definition.
- **Area/Building** values come from a fixed list that Setup publishes in 01.

Requirements schema:

- Add **Hold/Witness Point**. Timing/Frequency, Acceptance Criteria and Responsible Party stay as they are.
- Lanes write Requirements rows during the crawl: one per submittal, test, inspection, start-up or training item, linked to Ledger tags. The Ledger's Y/N flags come from these rows.

Migration: add the new columns to the 447-row Ledger as "Not stated", with no rereading. The sample re-test in Step 6 proves the prompts fill them.

Pass: both schemas frozen at rev1, and the repo checks validate the new headers.

### Step 6 — Prompts rev1 and sample re-test (Composer writes; five lane threads run)

Prompt fixes, drawn from the 31 method themes:

- Use the fixed Area/Building list and one PROPOSED naming rule.
- Harvest printed tags from every sheet in scope before assigning a PROPOSED tag.
- Write Requirements rows during the crawl, cited to the paragraph, with timing, acceptance criteria and hold/witness points.
- Read sample sections in full; no key-term scanning.
- Lane-prefixed issue IDs; a manifest for every run.
- Keep what worked: read methods from 01, Addendum 4 governs, body section governs, the WSDOT tag, the weakest-tag rule.

Sample units are in Appendix A. Run all five lanes at the same time and record start and end times for the concurrency metric.

Pass, per lane:

1. The pre-flight read check passes.
2. Headers match the rev1 schemas exactly.
3. One Wiki note per unit, in the note format.
4. Every Ledger and Requirements row is cited and tagged.
5. Requirements rows carry timing, acceptance criteria and hold/witness points where the source states them, and "Not stated" where it doesn't.
6. Items already logged in 01–04 are cited, not raised again.
7. Documents opened are limited to the units' pages plus the Addendum 4 pages 03 cites.
8. Spot-check: 5 random rows checked against source, 5 of 5 correct.

On a fail: log the failure mode and the fix, revise the prompt, and rerun that lane's sample in a new thread. A full rerun of all five lanes isn't needed for the proof (Inferred: the bar is proof-of-concept output).

### Step 7 — Proof v2

- Rebuild both registers from the rev1 data at sample scope. Pass: timing, acceptance criteria and hold/witness points filled from Requirements rows, and zero library reads.
- Rerun the companion's 10 questions (no regression allowed) and the 6 in Appendix B, which test the rev1 fields and conflict handling.
- Repeat the ChatGPT check.

### Step 8 — Close-out

- **Results memo, one page:** what was proven, the Section 8 metrics, and the fixes needed before SharePoint.
- **README and FAQ update:** tags, the weakest-tag rule, the Y/N conventions, how to query.
- **Ultraplan rev2:** mark the proof complete, or list what failed and the plan to fix it.

### Parallel track — inventory (Setup thread)

- Add C0.3, C2.1, C2.3 and C2.6 to the sheet index (01 rev2) and correct its read-method flags.
- Obtain C0.7, C1.1, C1.2, C7.7, C7.8, C7.9 and Addenda 1–3.
- Obtain a native copy of C0.3 (silt fence and check dams) and native copies for the 10 values the drawing controls register says need one.
- The 14 blank spec pages stay deferred (Setup decision).

### Optional, after Step 3 — LLM overlay

- Run graphify's LLM extraction over the notes once in Claude Code and once in Codex, and save each result to `graph/overlay/`. The difference between the two measures how far the runtimes disagree (companion, after v1).
- Overlay links are labeled as model output and never written back to the Ledger.

## 7. Exit criteria

The SharePoint request goes forward when all of these hold:

1. The repo is private, holds the transfer-baseline and graph-v1 releases, and passes its checks.
2. Proof v1 is recorded as the baseline.
3. The tag crosswalk is done: zero double-counted items.
4. Both schemas are frozen at rev1.
5. All five lanes pass the sample re-test.
6. Proof v2 meets its pass marks: the rebuilt registers carry timing, acceptance criteria and hold/witness points, with zero bulk reads.
7. ChatGPT returns the same items, sheets, sections and counts on every question.
8. The results memo is issued.

Engineer questions, missing sheets and Exception Report dispositions don't gate the proof.

## 8. Metrics

| Metric | Definition | Now | Target |
|---|---|---|---|
| Retrieval, proof v1 | Questions fully answered with citations | 1 question tested | 8 of 10 (companion) |
| Retrieval, proof v2 | The same 10, plus Appendix B | Not run | No regression; 5 of 6 on Appendix B (proposed) |
| Library pages opened | Pages opened per question; bulk reads | Not measured | Only to verify one page; 0 bulk reads |
| Library reads in register builds | Library pages opened while building registers | 0 in the first build (Verified) | 0 |
| Spot-check accuracy | Random rows that match source | Not measured | 5 of 5 per lane |
| Concurrency | Sum of lane run times divided by wall-clock time for the five-lane run (proposed definition) | Not measured | Report it |
| Routing efficiency | Pages opened divided by pages in the units' scope | Not measured | Report it |
| Sheet coverage | Sheets read out of 97 | 91 of 97 (Inferred: 6 still missing) | Report it |
| Unresolved rows | Unresolved rows out of Ledger rows | 123 of 447 | Report each with its need |
| Double counting | Items on more than one lane's row without a crosswalk | 244 | 0 |
| Runtime parity | Questions where ChatGPT returns the same items, sheets, sections and counts | Not measured | All |

## 9. Failure modes from the first run

| Failure | Where | Rev1 fix |
|---|---|---|
| Handoff files not found: chat attachments don't cross threads | Composer, first run | Only Project files and the repo cross threads; read check first |
| Project files changed mid-chat, and an inference was stated as fact | Setup | Inventory changes route to Setup; file status stated only as verified |
| Too much read before writing; turns saved nothing | Process & Mechanical | Write after every 4 documents or 2 long spec sections |
| Two sessions wrote one working folder: duplicate tags, split issue numbers. Seen again on 2026-09-30, when another thread's files appeared in a shared outputs folder | Contract & General; Transfer thread | Build on a local clone, or one build thread at a time; a branch per thread |
| A re-sent lane file renumbered 17 cross-lane items | Merge | Lane-prefixed issue IDs, never reused |
| Library .pdf files are zip bundles; S sheets have no text layer | Lanes | Read method from 01; re-check extraction on the original files in the repo |
| Long spec sections scanned by key terms | Lanes | Sample units read in full; requirement rows cite the paragraph |
| "Nothing like X exists" checks need full-text search | Lanes | Logged keyword search, or a design gap (Step 1 decision) |
| Summaries dropped timing, acceptance criteria and hold points | Merge workflow test | Requirements rows written during the crawl |
| The weakest-tag rule plus an Inferred bid item kept rows off Verified | Process & Mechanical | Separate Bid Item Tag |
| The same item under different tags in different lanes: 244 double counts | Merge | Tag crosswalk (Step 4) |
| The first prompt set was overbuilt: grading logs and extra files | Composer | One plain prompt per lane; test plans stay out of Project files |
| Two plans written for the same steps in parallel threads | Transfer thread and this thread | This plan is the master; the companion governs only Steps 2 and 3 |

## 10. Decision register

**Made**

| Decision | Record |
|---|---|
| Fifth lane, Contract & General: Divisions 00 and 01, Appendices D, E and I, and the QA plan | 03 Coverage Gate rev1 |
| Ledger schema: 16 columns, as in Ledger_Schema.csv | 03 Coverage Gate rev1 |
| Read method threshold of 300 body characters; 20 sheets re-flagged Visual | 03 Coverage Gate rev1 |
| The six spec lane judgment calls in 02 accepted | 03 Coverage Gate rev1 |
| 01 11 10 / 01 11 00 alias accepted; it stays Unresolved | 03 Coverage Gate rev1 |
| Claims that defer to WSDOT tagged "Unresolved: external reference, not staged" | 03 Coverage Gate rev1 |
| The 14 blank spec pages deferred; they don't block | 03 Coverage Gate rev1 |
| "Thread" means a chat; "lane" means a crawl scope only | 03 Coverage Gate rev1 |
| Phase 1 pair: the Submittal Register and the Inspection & Test Plan | Merge thread (Issues Log entry closed) |
| Proof-of-concept bar: scanning only, no material takeoff | Merge thread |

**Pending:** the ten items in Step 1.

## Appendix A — Sample units for the re-test

| Lane | Text sheet | Visual sheet | Addendum 4 case | Requirements unit | Rule under test |
|---|---|---|---|---|---|
| Civil & Site | C1.4 | C0.2 (notes sheet, almost no text) | C1.3 reissue | 33 41 00 | C2.1 cites C7.7 and C7.8, which are missing: record the gap, don't infer (updated in rev1; C2.6 is now read) |
| Process & Mechanical | G0.7 | C3.3 (image only) | C6.4 reissue | 43 22 10, plus 22 13 36 | The Addendum 4 drive change appears in both sections: find both, and log the VFDs to Electrical & Controls |
| Electrical & Controls | E4.1 | E6.2 (schedule tables) | E9.1 with Addendum 4 Clarification 4 | 26 29 23 | Cite main spec pages, never the Division 26 file |
| Structural & Building | A1.3 | S2.1 (image only) | S2.3 reissue (image only) | 07 92 00 | The running header reads 13 12 20: the body governs |
| Contract & General | 00 21 13 | none | 00 41 00, Bid Item #18 | 01 45 00 | #18 is cited, not raised again; the 01 11 10 alias holds; bid-phase and post-award items are split (00 21 13 p.14) |

Full-run spot-checks carried from the Composer test plan:

- **26 80 00 ¶2.04 D:** the base names the Promag L400; Addendum 4 p.2 replaces it with the W400. The row shows W400 as governing and flags as Unresolved whether the L400 remains acceptable.
- **Generator rows:** they cite both generator flags in 03.

Source: Composer test plan (Verified in the Composer thread record), except the Civil & Site rule under test, which is updated.

## Appendix B — Six questions added for proof v2

They cover the rev1 requirement fields and conflict handling, which the companion's 10 questions don't. Carl confirms or swaps them before Step 7. Expected behavior comes from the Merge records.

| # | Question | Expected behavior |
|---|---|---|
| 1 | What submittals do the 22 13 36 pumps need, and when are they due? | Submittals with timing from requirement rows |
| 2 | What are the hold or witness points for concrete placement? | Hold/witness points from requirement rows; before rev1 this was a design gap |
| 3 | Which structures get a leakage test, who performs it, and who pays? | From 01 45 00 and the ITP, with the responsible party |
| 4 | How much 6-ft chain link fence is shown, and where do the sheets disagree? | 149 and 134 LF on C2.1 vs 126 LF on C2.5, both cited |
| 5 | Which section covers joint sealants, and what's wrong with its header? | 07 92 00; the running header reads 13 12 20 and the body governs |
| 6 | Is the service load within the 225 kVA utility transformer? | Unresolved, with what's needed to close it |

## Appendix C — Changes from the original

| Original (section) | Rev1 | Why |
|---|---|---|
| Status: planned, nothing run; next step is the spine (12) | Build complete; proof and close-out remain | Setup, lanes and Merge are done |
| Cowork tasks write to `_Lanes/<Lane>/` (3, 9) | Chat threads with file-name prefixes; the repo is the system of record | Project files are flat and read-only; attachments don't cross threads |
| Template points to `_Wiki/03_Bid_Item_Spine.md` (9) | 03 is the Coverage Gate; the spine is 04 | Rev1 file names |
| Four discipline lanes plus four cross-cutting lanes (5) | Five crawl lanes; submittal and testing outputs built at Merge from the Ledger | The cross-cutting lanes read every spec section, the whole-set read this design avoids |
| Addendum 4 as its own lane (5) | Applied row by row in each lane; Merge checks for Addendum 4 items no lane recorded | Addendum 4 p.2 alone spans four lanes |
| Lane outputs: notes, rows, showcase output, manifest (9) | Notes, rows, requirement rows, issues and a manifest; showcase outputs built at Merge | The manifest returns to feed the metrics |
| Tags: Verified, Inferred, Unresolved (9) | Adds Verified-Visual, the WSDOT tag and a separate Bid Item Tag | Setup decisions; Process & Mechanical finding |
| Bid Item #18 as proof the spine ties to the change record (2) | #18 is an open conflict between Addendum 4 and the bid form | Setup found the conflict; other addendum-to-bid-item links are Inferred from 00 24 13 |
| Exception Report as .docx (7) | .md and .xlsx with a Disposition column | Plain-file design rule |
| Phase 1 pair left open | Submittal Register and Inspection & Test Plan | Chosen at Merge |
| Concurrency metric (10) | Kept; measured on the sample re-test | The first run wrote no manifests |
| None | Repo, checks, a script-built Ledger graph, and the companion plan for the transfer | Enforcement, retrieval and a single system of record |
