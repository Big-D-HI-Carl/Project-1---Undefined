# Graph Transfer Ultraplan — Eastsound Test Bed

- **Version:** rev0 · 2026-09-30 · **Status:** draft for Carl's approval
- **Follows:** Sample_Project_Concurrent_Lane_Ultraplan.docx (lane crawl → Merge → Phase 1 workflows)
- **Single writer for the build:** the Transfer thread (Step 4 onward)
- **Purpose:** Move everything this test bed produced into a private GitHub repo. Build a graphify knowledge graph from it without an LLM. Stand up a new Claude Project that answers through the graph. The same files must work in ChatGPT.
- **Tags:** Verified = read directly in the named source, or tested · Inferred = derived, basis stated · Unresolved = open, need stated.
- **Source names:** Setup thread = chat "Lane 1: Library inventory and document register" · Composer thread = chat "Composer thread prompt generation setup" · lane threads = chats "1" Civil & Site, "2" Process & Mechanical, "3" Electrical & Controls, "4" Structural & Building, "5" Contract & General · Merge thread = chat now titled "combined" · 00–04 = index files rev1 · Graph test = graphify 0.9.72 run in the Sample Project sandbox on 2026-09-30.
- **Terms:** node = one thing in the graph (an item, a sheet, a spec section) · link = a named connection between two nodes · thread = a chat · lane = a crawl scope.

---

## 1. The short version

1. Freeze the Sample Project. It becomes the record of the crawl.
2. Download every thread output into one folder on your PC.
3. Load it all into a private GitHub repo exactly as-is: line-ending guard first, then the files. Pin it as release **transfer-baseline**.
4. Create a new Claude Project, "Eastsound Graph". Load the same library and index files, and connect the repo.
5. A Transfer thread checks the baseline, keys every Ledger row, checks every reference against the index files, and splits the Wiki into one note per file beside its source document.
6. The Transfer thread builds the graph by script, with no LLM, and checks it against the source counts.
7. You load the build into GitHub as release **graph-v1**. Nothing from the baseline may change.
8. A Proof thread reruns the two Phase 1 workflows and 10 standard questions through the graph. You then run the same 10 questions in ChatGPT.

## 2. What done looks like

- A private repo holds every file the test bed produced, byte-for-byte, with two releases: transfer-baseline and graph-v1.
- `graph/graph.json` holds a node for every Ledger row (441), sheet (97), spec section (98), Addendum 4 item (15), bid item and alternate (18 + 5), Wiki note (202) and requirement row (248), joined by named links. Every link carries the tag and citation of the row that created it.
- `graph/wiki/` holds the same graph as plain Markdown pages, so any AI can read it without running graphify.
- The new Project answers the question set through graph → Wiki → Ledger. It opens a library page only to verify one.
- ChatGPT, or Codex on the same repo, returns the same items, sheets, sections and counts.

Counts: 441, 202 and 248 come from the Merge thread; 97, 98, 15 and 18 + 5 come from 01–04. All are Verified in those sources and rechecked in Step 4.

## 3. Ground rules

1. **Move first, fix later.** Nothing is corrected on the way in. Known problems ride along and show in the graph. Fixes come afterward as normal revisions, so the history shows each one.
2. **Library bytes never change.** No re-exporting, re-splitting or renaming. The fingerprint check enforces it.
3. **The graph is a map, not a source.** Answers cite the Wiki note, Ledger row or document page, never "the graph".
4. **Core graph built by script, no LLM.** Same output in any runtime. Links an LLM finds later go in a separate, labeled file and never write back to the Ledger.
5. **No guessing.** Every link comes from a named column or line. A value that doesn't match the index files is listed Unresolved, not matched by eye.
6. **Duplicates stop the build.** Two rows with the same key never merge silently.
7. **Single writer.** The Transfer thread is the only writer for `transfer/`, `tools/`, `graph/` and the split notes. Only one Transfer thread is open at a time.
8. **Log before rerun.** Every failed check goes in the Issues Log with its failure mode and fix before the rerun. Continue the log's numbering.

## 4. What moves

| Group | Files | Expected count | Get it from | Repo folder |
|---|---|---|---|---|
| Library | The 30 source files plus Missing_Pages_Page_001–004.png, exactly as you uploaded them | 34 files, 22.6 MB | Your PC | `library/` |
| Index and schemas | 00–04 rev1, Ledger_Schema.csv, Requirements_Schema.csv | 7 files | Sample Project files | `index/` |
| Civil & Site | Civil_and_Site_Wiki.md, _Ledger.csv, _Issues.md, _Known_Issues.md | 56 notes, 115 rows | Chat "1" | `lanes/civil-and-site/` |
| Process & Mechanical | Same 4 files | 37 notes, 114 rows | Chat "2" | `lanes/process-and-mechanical/` |
| Electrical & Controls | Same 4 files | 50 notes, 126 rows | Chat "3" | `lanes/electrical-and-controls/` |
| Structural & Building | Same 4 files | 25 notes, 45 rows | Chat "4" | `lanes/structural-and-building/` |
| Contract & General | Same 4 files | 34 notes, 49 rows (by subtraction, Inferred) | Chat "5" | `lanes/contract-and-general/` |
| Merge | Project_Wiki.md · Project_Ledger.csv and .xlsx · Exception_Report.md and .xlsx · Submittal_Register.csv · Inspection_Test_Plan.csv · Phase1_Workflows.xlsx · Phase1_Workflow_Test.md · Project_Ledger_by_CWP.xlsx · Issues_Log.md and .csv | 202 notes · 441 rows · 567 exceptions · 145 + 103 register rows · 19 CWPs · 32+ log entries | Chat "combined" | `project/` |
| Process record | Prompt_1 to Prompt_6 .md · Sample_Project_Concurrent_Lane_Ultraplan.docx · this plan · Library_Fingerprint.csv and _Pages.csv | 10 files | Composer chat, your PC, the chat that issued this plan | `process/` |

- **Total:** 83 files, plus `.gitattributes`.
- **Latest versions only:** the lanes saved after every batch, so take the last download in each chat. The Issues Log may have grown past 32 entries; take the latest.
- **Leave out** the rev0 index files and Setup's resplit list. Both are superseded.
- **Library = your originals.** The Sample Project holds Claude's converted copies: 28 page bundles, 2 text-only files and 4 PNGs (Verified, 00 register and Graph test). GitHub gets the original files you uploaded, with the same names. If an original is missing from your PC, stop and log it. Don't re-export it.

## 5. Repo layout

```
eastsound-testbed/               private
├── .gitattributes               first commit; stops line-ending changes
├── README.md                    what this is, the rules, how to rebuild (Step 6)
├── library/                     34 source files as uploaded; split notes land beside them (Step 5)
├── index/                       00–04 rev1, Ledger_Schema.csv, Requirements_Schema.csv
├── lanes/
│   ├── civil-and-site/          Wiki, Ledger, Issues, Known Issues
│   ├── process-and-mechanical/
│   ├── electrical-and-controls/
│   ├── structural-and-building/
│   └── contract-and-general/
├── project/                     Merge outputs
├── process/                     prompts, lane Ultraplan, this plan, library fingerprints
├── transfer/                    Baseline Report, Item Keys, Reference Check (Steps 4–5)
├── tools/                       build and check scripts, requirements.txt (graphifyy==0.9.72)
└── graph/                       graph.json, GRAPH_REPORT.md, graph.html, wiki/, Graph_Check.md, Proof_Report.md
```

`library/` keeps the flat structure of the Project files. Nothing inside it is renamed or moved.

## 6. Steps

### Step 1 — Freeze and collect
**Who:** Carl · **Time:** about 30–45 min (Inferred)
- Stop writing in the Sample Project's threads. All new work happens in the new Project.
- Make one folder on your PC with the Section 5 layout. Keep it outside OneDrive, or set it to always stay on the device, so no file is a cloud-only placeholder.
- Download each file in Section 4 into its folder and tick it off.
- **Check:** 83 files in the right folders.

### Step 2 — Load the GitHub baseline
**Who:** Carl · **Time:** about 20–30 min (Inferred)
1. Create a free GitHub organization for test beds, and a private repository in it (suggested name: eastsound-testbed). Keep it separate from your other repos.
2. **First file: `.gitattributes`.** Use Add file → Create new file, name it `.gitattributes`, paste Appendix A and commit. It must exist before anything else is uploaded.
3. Upload one folder per commit, with no edits, in this order: library → index → lanes → project → process. Use plain commit messages, such as "Baseline: library, unchanged".
4. Create a release (GitHub's pinned snapshot) called transfer-baseline.
- **Why the guard comes first:** the two spec files are text with CRLF line breaks. Pages are separated by bare blank lines: 23,145 CRLF breaks and 1,288 bare breaks in the main spec. The 645-page split depends on that difference. A simulated Windows-style line-ending conversion collapsed the split to 1 piece (Verified, simulation 2026-09-30).
- **Size limits:** GitHub's browser upload takes files up to 25 MB and GitHub Desktop takes up to 100 MB (GitHub's documented limits). The Project copies top out at 2.9 MB, but your originals may be larger. Use GitHub Desktop for anything over 25 MB.
- **Check:** the repo shows 83 files plus `.gitattributes`, and every library file size matches your PC.

### Step 3 — Set up the new Project
**Who:** Carl · **Time:** about 15 min (Inferred)
1. Create a Claude Project named "Eastsound Graph".
2. Paste the Sample Project's instructions unchanged, then add the Appendix B block.
3. Upload to Project files:
   - the same 34 library originals and the 7 index and schema files;
   - this plan;
   - both fingerprint files.
4. Connect the repo: Project knowledge → GitHub.
   - For a private repo, grant the Claude GitHub App access to this repo only.
   - Select `lanes/`, `project/` and `process/`.
   - Source: Claude Help Center, "Use the GitHub integration" (Verified).
5. Start a new chat and paste Appendix C. That chat is the Transfer thread.

### Step 4 — Baseline check
**Who:** Transfer thread · **Output:** `transfer/Baseline_Report.md`
- **Fingerprint:**
  - Recompute the new Project's library fingerprint page by page and compare it with Library_Fingerprint_Pages.csv (888 pages).
  - Text must match on every page.
  - Image differences are listed, and 3 Visual pages are spot-checked.
  - A text mismatch means the new conversion differs from the one the citations were made on. Stop.
- **Sync test:**
  - Can bash see the synced repo files in `/mnt/project`? Record yes or no, with the listing.
  - If no, attach a zip of `lanes/`, `project/` and `process/` to the thread. Attachments are the proven path (Composer thread). Unresolved until run.
- **Counts:** every expected count in Section 4. On a mismatch: stop, log it, ask Carl.
- **Schema:**
  - All six Ledger CSVs match Ledger_Schema.csv exactly: 16 columns, UTF-8, no BOM.
  - Both registers match Requirements_Schema.csv.
- **Note format:** sample 3 notes per lane. Record the exact ID, Tags and Related lines that the split and the build will key on. Lanes that differ each get their own rule.
- **Pass:** every check green, or every failure logged with its fix.

### Step 5 — Prepare
**Who:** Transfer thread · **Output:** `transfer/Item_Keys.csv`, `transfer/Reference_Check.csv`, split notes
- **Item keys:**
  - Give every Project_Ledger row a key: lane + tag + row number. Project_Ledger.csv is never edited.
  - Why: tag SD-1 is two different items, the Civil & Site storm drain alignment and the Electrical & Controls sludge pump (Merge thread, Issues Log).
  - graphify keeps one node per ID. Tested with those two rows, it kept one node named after the second row and hung the first item's sheet link on it (Verified, Graph test).
- **Reference check:**
  - Resolve every sheet, spec section, addendum and bid item value against 01–04. Sources: the Ledger, the Wiki notes' Tags and Related lines, and both registers.
  - Record for each: value · where found · resolved to · rule used · status.
  - Unknown values stay Unresolved.
  - Expected rules:
    - "Sheet C1.3" → C1.3.
    - Section titles are trimmed to the section number.
    - 01 11 10 and 01 11 00 stay two sections joined by a "possible same section" link (accepted as Unresolved in the Setup thread).
- **Lane issue numbers:** "Issue 18" becomes "Civil & Site Issue 18". Merged numbers are ambiguous; Issue 18 means different things in two lanes (Merge thread, Issues Log).
- **Wiki split:**
  - Project_Wiki.md becomes one file per note, saved in `library/` beside its source file, named `<source file name> - <Document ID>.md`.
  - Sheet notes sit beside the file named in 01's File column; spec notes sit beside the main spec.
  - Notes for the 10 sheets not in the library are named `Not in library - <sheet>.md`.
- **Checks:**
  - 202 notes in, 202 files out.
  - Joining the pieces back reproduces Project_Wiki.md exactly.
  - The reference check has no unexplained unknowns.

### Step 6 — Build and check the graph
**Who:** Transfer thread · **Output:** `graph/`, `tools/`, package zip
- **Build:**
  - Inputs:
    - 01–04;
    - Project_Ledger.csv and Item_Keys.csv;
    - the split notes and both registers;
    - the Exception Report's same-item groups;
    - CWP assignments from Project_Ledger_by_CWP.xlsx.
  - The build is done by script with no LLM, following the Section 7 rules.
  - graphify 0.9.72 then clusters the graph and writes graph.json, GRAPH_REPORT.md, graph.html and `wiki/`. All four ran with zero LLM calls in the Graph test (Verified).
- **Graph check** → `graph/Graph_Check.md`, PASS or FAIL for each line:
  - 441 item nodes = 441 Ledger rows; no duplicate keys; SD-1 appears twice.
  - 97 sheets (86 available, 10 not in library, C1.6A); 98 spec sections; 15 Addendum 4 items; 18 bid items and 5 alternates; Bid Item 1 held as an attribute.
  - 202 note nodes; 248 requirement nodes.
  - Link tags add up to the Ledger's tag counts.
  - The not-in-library sheets match 01's list of 10.
  - Items with no sheet link and no spec link are listed.
  - The 10 biggest hubs are listed with their link counts.
  - Unresolved references are counted and listed.
  - No group is named "Community N".
- **Tools and package:**
  - `tools/` holds the scripts, a requirements.txt pinning graphifyy==0.9.72, and a README with the rebuild steps.
  - `graph/Query_Cheat_Sheet.md` explains in plain English how to ask the graph with explain, path --undirected and query.
  - Everything added in Steps 4–6 goes into one zip in the repo layout.

### Step 7 — Load the build into GitHub
**Who:** Carl · **Time:** about 10 min (Inferred)
- Unzip the package into your repo folder and upload it as one commit, "graph-v1 build". Create release graph-v1.
- **Check:** GitHub lists every file in that commit as added and none as changed. If anything shows as changed, stop: something in the baseline was touched.
- In the new Project, sync the repo and add `graph/` to the selection. If Step 4 found that synced files don't reach bash, also upload `graph/graph.json` and `project/Project_Ledger.csv` directly to Project files.
- Start a new chat for Step 8. A thread sees Project files as they were when it started (Composer thread, Inferred).

### Step 8 — Prove it
**Who:** Proof thread, then Carl
- Paste Appendix D into the new chat. The Proof thread:
  1. rebuilds the Submittal Register and Inspection & Test Plan through graph → Wiki → Ledger, and compares them with the Merge baseline of 145 rows (139 + 6 gap) and 103 rows (92 + 11 gap);
  2. answers the 10 questions in Appendix E with citations, files opened, library pages opened and whether a bulk read was needed;
  3. writes `graph/Proof_Report.md`.
- **ChatGPT check (Carl):**
  - Give ChatGPT the same package and the same 10 questions, or give Codex the repo. Record differences in the Proof Report.
  - In ChatGPT chat, point it at `graph/wiki/` and GRAPH_REPORT.md, which need no install. Codex can run graphify itself (Inferred).
  - ChatGPT extracts PDF text its own way, so expect page-text differences on library checks. The 00 register already flags this.
- **Pass criteria** (proposed; adjust before running):
  - **Registers:** same row counts, or every difference explained; zero library opens.
  - **Questions:** at least 8 of 10 fully answered with citations; no bulk reads; every library open logged.
  - **ChatGPT check:** same items, sheets, sections and counts on all 10 questions; wording may differ.

## 7. How the graph is built

### Nodes
| Node | Built from | Count | Where it lives (shown with every answer) |
|---|---|---|---|
| Item | Project_Ledger.csv, one per row | 441 | Ledger row and its Source Citation |
| Sheet | 01 sheet table and addendum-only table | 97 | File and PDF page from 01 |
| Spec section | 02 section table | 98 | Main spec start and end page from 02 |
| Addendum 4 item | 03 Addendum 4 item map | 15 | Add. 4 page from 03 |
| Bid item / alternate | 04 | 18 + 5 | Bid form page from 04 |
| Wiki note | Split notes | 202 | The note file |
| Requirement | Submittal_Register.csv, Inspection_Test_Plan.csv | 248 | Register row |

**Held as attributes, not nodes:** lane, discipline, area/building, status, CWP, PROPOSED flag, submittal Y/N, testing Y/N and Bid Item 1. Each of these touches a large share of items. As nodes, they would connect nearly everything in two steps and make path answers meaningless (Inferred). Bid Item 1 is the lump-sum base bid assigned to all lanes (04 row 1, Verified).

**Group names:** each group is named in plain English from its most common CWP and lane, for example "33 Yard Piping & Utilities — Civil & Site".

### Links
| Link | From → to | Built from | Tag carried |
|---|---|---|---|
| shown on | Item → Sheet | Ledger "Drawing Sheets" | Row's tag |
| specified in | Item → Spec section | Ledger "Spec Sections" | Row's tag |
| changed by | Item → Addendum 4 item | Ledger "Addenda". When a row says only "Add. 4", link to the Addendum 4 item that touches the same sheet or section | Row's tag; rule-based links are Inferred, with the rule named |
| paid under | Item → Bid item | Ledger "Bid Item" (except #1) | Row's tag |
| described in | Item → Wiki note | Ledger "Wiki Note(s)" | Row's tag |
| possible same item | Item ↔ Item | Exception Report same-item groups | Unresolved until the tag crosswalk is approved |
| changes | Addendum 4 item → Sheet or Spec | 03 "Touches" | 03's tag |
| covers | Wiki note → Sheet or Spec | The note's Document ID | Verified (read in the note) |
| mentions | Wiki note → Item, Sheet, Spec or Addendum | The note's Tags line | Verified (read in the note) |
| related to | Wiki note → Wiki note | The note's Related documents line | Verified (read in the note) |
| requires | Requirement → Item, Spec or Sheet | Register columns | Register row's tag |
| alternate for | Alternate → Spec section | 04 alternates table | 04's tag |

- **Tag translation:** Verified and Verified-Visual → EXTRACTED · Inferred → INFERRED · Unresolved → AMBIGUOUS. The original tag and the Source Citation ride on every link, so nothing is lost when graphify shows three levels instead of four. In the Graph test, both fields came through into graph.json (Verified).
- **Ambiguous tags:** when a register or note names a tag that matches two items (for example SD-1), it links to both, the links are tagged Unresolved, and the case is listed in the Graph Check.

## 8. Known issues carried as-is

None of these are fixed during the move. The graph shows each one.

- **441 rows are not 441 unique items.** 77 same-item groups carry different tags, and 11 same-name PROPOSED pairs split only on Area/Building wording (Merge thread, Issues Log). In the graph these become "possible same item" links.
- **Tags and names reused for different items.** SD-1 is two items, and the "Dewatering system" PROPOSED name is used for two items. In the graph these become separate nodes by key.
- **309 PROPOSED tags await approval.** 4 of them already have printed tags: TCP-3, PIT-620, Hot Box #1 and Hot Box #2 (Merge thread).
- **24 items land in two CWPs** (Merge thread).
- **Missing documents.**
  - 10 sheets and Addenda 1–3 are not in the library (Merge thread).
  - C2.1, C2.3 and C2.6 turned up as page images after rev1 and are not indexed. Project files hold 4 page images, so the fourth is unidentified (Unresolved; needs 01 rev2).
  - Until 01 rev2, the graph shows all 10 sheets as not in library.
- **One tag per row.** Links inherit the row's weakest tag. Process & Mechanical has 0 Verified rows out of 114, because Bid Item 1's Inferred assignment caps every row (Lane 2 thread).
- **Registers aren't issuable yet** (Merge thread):
  - timing is missing on 123 of 139 submittals and 77 of 92 tests;
  - acceptance values are missing on 70 of 92 tests;
  - there is no hold/witness column.
- **Bid Item #18 conflict** (04).

## 9. Traps and how the plan handles them

| Trap | What goes wrong | How the plan prevents it | Basis |
|---|---|---|---|
| Line endings | A Windows-style conversion turns the spec's bare blank lines into CRLF, and the 645-page split becomes 1 piece | `.gitattributes` before any upload; text fingerprint check | Verified (simulation) |
| Same ID, two items | graphify keeps one node, named after the last row, and moves the first item's links onto it | Keys by row; a duplicate key stops the build | Verified (Graph test, SD-1 rows) |
| Library files | graphify's PDF reader rejects them ("invalid pdf header"), because they're page bundles and text saved as .pdf | Library left out of the graph; locations come from 01/02 | Verified (Graph test) |
| CSV | graphify skips CSV files | The script reads the CSV; graphify only clusters and exports | Verified (Graph test) |
| Markdown | graphify's extract won't run on Markdown without an LLM key | The script parses the notes' fixed lines | Verified (Graph test) |
| Path direction | Item-to-item path questions return nothing unless direction is ignored | Use path --undirected; it's in the cheat sheet | Verified (Graph test) |
| Hubs | Bid Item 1, or a lane as a node, links everything in two steps | Held as attributes; Graph Check lists the 10 biggest hubs | Inferred (basis: 04 row 1) |
| Spelling variants | "C1.3" and "Sheet C1.3" become two nodes | Reference check against 01–04 | Inferred |
| Sync reach | Synced repo files may not be visible to bash | Step 4 test; direct upload as fallback | Unresolved |
| Stale thread view | A thread sees Project files as they were when it started | New chat after each upload | Inferred (Composer thread) |
| Two writers | Two sessions in one folder created duplicate tags and split issue numbers | One Transfer thread at a time | Verified (Lane 5 thread) |
| Version drift | graphify releases often, and output can change between versions | Pin graphifyy==0.9.72 | Inferred |

## 10. Decisions needed

| Decision | Recommended | Why |
|---|---|---|
| Repo | Free organization, private repo "eastsound-testbed" | The drawings are Wilson Engineering's work product; this also keeps the test bed separate |
| Library in GitHub | The original files you uploaded | They're the real sources; the Project copies are Claude's internal conversion |
| Sample Project | Freeze it as the crawl record | A clean single-writer line between phases |
| Duplicate items | One node per row now, plus "possible same item" links; merge after the tag crosswalk | The transfer doesn't wait on owner decisions |
| Hubs | Hold Bid Item 1, lane, discipline, area, status and CWP as attributes | Keeps path answers meaningful |
| Note location | Beside the source files in `library/` | Matches "add notes beside documents" |
| LLM layer | Only after v1 passes | Prove the core first |
| Where the build runs | A claude.ai Transfer thread for v1; Claude Code or Codex later | Proven path, nothing to install |

## 11. After v1

1. **Tag crosswalk approved:** rebuild, and each "possible same item" pair becomes one node.
2. **01 rev2:** index the found page images, with notes beside them.
3. **Schema v2:**
   - a separate tag for the Bid Item column, or a tag per field;
   - a hold/witness column;
   - requirement rows written at crawl time (Merge thread finding).
4. **LLM layer:** run /graphify over the notes once in Claude Code and once in Codex, and save each result to `graph/overlay/`. The difference between the two measures how much the runtimes disagree.
5. **Automate:** rebuild on every push, with a GitHub Action or commit hook running `tools/build_graph.py`. graphify's own commit hook rebuilds code only, not this script-built graph (Inferred).
6. **SharePoint:** when the connection is approved, the same layout maps onto a document library.

---

## Appendix A — .gitattributes

Paste exactly, as the first file in the repo.

```
# Eastsound test bed: never change bytes or line endings.
* -text
*.pdf binary
*.png binary
*.xlsx binary
*.docx binary
```

## Appendix B — New Project instructions (add below the existing blocks)

```
GRAPH PHASE (PURPOSE, DESIGN RULES, OUTPUT STANDARDS and WORKING STYLE above stay as-is)
- This Project is the graph phase of the Eastsound test bed. The Sample Project is frozen as the crawl record.
- Repo: <org>/eastsound-testbed. Releases: transfer-baseline, graph-v1. Every thread states which release it read.
- Retrieval order: 1) the graph (graph/GRAPH_REPORT.md, graph/wiki/, or graphify explain / path --undirected on graph/graph.json); 2) the Wiki note; 3) the Ledger row; 4) one library page, only to verify a cited page. Log every library open with the question it served. An answer that needs a bulk read is a design gap: stop and log it.
- The graph is a map, not a source. Cite the note, row or page, never "the graph".
- Graph tags: EXTRACTED = Verified or Verified-Visual; INFERRED = Inferred; AMBIGUOUS = Unresolved. Use the original tag carried on each link.
- 441 Ledger rows are not 441 unique items. "Possible same item" links mark known duplicates until the tag crosswalk is approved.
- Single writer: the Transfer thread owns transfer/, tools/, graph/ and the split notes. All other threads only read.
- Failed checks go in the Issues Log (failure mode and fix) before any rerun. Continue its numbering.
```

## Appendix C — Transfer thread prompt

```
You are the Transfer thread for the Eastsound Graph project. Read Graph_Transfer_Ultraplan.md in Project files first, then do Steps 4, 5 and 6 in order. You are the only writer for transfer/, tools/, graph/ and the split Wiki notes. Plain English; cite every fact; tag Verified / Verified-Visual / Inferred / Unresolved. Save after each step with present_files. If a check fails, add the failure mode and fix to the Issues Log (continue its numbering) before rerunning.

Setup
- pip install graphifyy==0.9.72 --break-system-packages
- The library, index files, schemas, fingerprints and plan are in /mnt/project. Lane, Merge and process files come from the GitHub sync if bash can see them in /mnt/project; otherwise from the zip I attach.

Step 4 — Baseline check → transfer/Baseline_Report.md
1. Recompute the library fingerprint page by page and compare it with Library_Fingerprint_Pages.csv. Text must match on all 888 pages. List any image differences and spot-check 3 Visual pages.
2. Record whether bash can see the synced repo files, with the listing as proof.
3. Check every expected count in plan Section 4. On a mismatch: stop, log it, ask me.
4. Check that all six Ledger CSV headers match Ledger_Schema.csv exactly (16 columns, UTF-8, no BOM) and both registers match Requirements_Schema.csv.
5. Sample 3 Wiki notes per lane and record the exact ID, Tags and Related lines the split and build will key on.

Step 5 — Prepare → transfer/Item_Keys.csv, transfer/Reference_Check.csv, split notes
1. Give every Project_Ledger row a key (lane + tag + row number). Never edit Project_Ledger.csv.
2. Resolve every sheet, spec section, addendum and bid item value in the Ledger, the notes' Tags and Related lines, and both registers against 01–04. Record value, where found, resolved to, rule and status. Never guess; unknowns stay Unresolved.
3. Prefix lane issue numbers with their lane ("Civil & Site Issue 18").
4. Split Project_Wiki.md into one file per note in library/, beside its source file, named "<source file name> - <Document ID>.md". Notes for sheets not in the library: "Not in library - <sheet>.md". Check 202 in = 202 out, and that joining the pieces reproduces Project_Wiki.md exactly.

Step 6 — Build and check → graph/
1. Build the graph by script with no LLM, following plan Section 7 exactly. Use graphify's build_from_json, cluster and to_json, then write GRAPH_REPORT.md, graph.html and the wiki/ export. Name groups in plain English from their most common CWP and lane; no "Community N".
2. Tested behavior to respect: graphify can't read the library files, skips CSV, needs an LLM for Markdown, and merges two nodes with the same ID without warning. So keys come from Item_Keys.csv and any duplicate key stops the build. Item-to-item paths need --undirected.
3. Write graph/Graph_Check.md with PASS/FAIL for every check in plan Step 6.
4. Write tools/ (scripts, requirements.txt pinning graphifyy==0.9.72, README with rebuild steps) and graph/Query_Cheat_Sheet.md.
5. Zip everything added in Steps 4–6 in the repo layout. Nothing already in the baseline may change.
```

## Appendix D — Proof thread prompt

```
You are the Proof thread for the Eastsound Graph project. Read only. Read Graph_Transfer_Ultraplan.md Step 8 and Appendix E first, and state the release you are reading (graph-v1).
Retrieval order: 1) the graph (graph/GRAPH_REPORT.md, graph/wiki/, or graphify explain / path --undirected on graph/graph.json; pip install graphifyy==0.9.72 --break-system-packages); 2) the Wiki note; 3) the Ledger row; 4) one library page, only to verify a cited page. Log every library open with the question it served. If an answer needs a bulk read, stop and log it as a design gap.
1. Rebuild the Submittal Register and Inspection & Test Plan with the Requirements_Schema.csv columns. Compare with the Merge baseline (145 rows including 6 gap rows; 103 rows including 11 gap rows) and explain every difference.
2. Answer the 10 questions in Appendix E. For each: the answer with citations, the files opened, the library pages opened, and whether a bulk read would have been needed.
3. Write graph/Proof_Report.md with pass/fail against Step 8's criteria. Log failures in the Issues Log before any rerun.
```

## Appendix E — Question set

| # | Question | What a good answer uses |
|---|---|---|
| 1 | What does Addendum 4 change, item by item, and which Ledger items does each change touch? | The 15 Addendum 4 item nodes; "changes" and "changed by" links |
| 2 | What's shown on sheet C1.3, and where do I verify each item? | The C1.3 node (base sheet and Add. 4 reissue); "shown on" links; file and page |
| 3 | Which Division 46 items need startup testing, and which spec paragraph requires it? | Division 46 section nodes; the testing attribute; ITP requirement nodes |
| 4 | What is paid under Bid Item 18, and what conflict does the Bid Item Spine flag? | The Bid Item 18 node; "paid under" links; the 04 conflict section |
| 5 | Which items show up in two lanes under different tags? | "Possible same item" links (77 groups expected) |
| 6 | Which Ledger items point to sheets that aren't in the library? | The 10 not-in-library sheet nodes |
| 7 | Trace the generator from bid item to spec section to sheet to Addendum 4. | Add. 4 Clarification 5 and exhibit; Alternate E; the generator item; ITP rows |
| 8 | Which sheets and spec sections have no Ledger items? | Sheet and spec nodes with no item links |
| 9 | List the Unresolved items in CWP 33 Yard Piping & Utilities and what each needs to close. | CWP attribute plus tag (84 rows, 33 Unresolved expected) |
| 10 | What's still missing before the ITP can be issued? | Phase1_Workflow_Test.md findings; requirement nodes |

**Score each question on four points:**
- answered from graph + Wiki + Ledger (Yes / Partly / No);
- a citation on every fact (Y/N);
- number of library pages opened;
- whether a bulk read was needed (Y/N).

## Appendix F — Issues Log entries to add now

Columns match the Issues Log: #, Date, Area, Issue, Impact, Status, Next step / owner, Reference. Number them with the log's next numbers.

| Date | Area | Issue | Impact | Status | Next step / owner | Reference |
|---|---|---|---|---|---|---|
| 2026-09-30 | Graph transfer | graphify's PDF reader rejects the library files ("invalid pdf header"); they're page bundles and text saved as .pdf | Library can't be graphed directly | Closed — by design | Library left out of the graph; locations come from 01/02 | Graph test |
| 2026-09-30 | Graph transfer | graphify skips CSV files | graphify can't load the Ledger itself | Closed — by design | Build script reads the CSV | Graph test |
| 2026-09-30 | Graph transfer | graphify needs an LLM key to extract Markdown | No-LLM Wiki build impossible through graphify | Closed — by design | Script parses the notes' fixed lines; LLM layer after v1 | Graph test |
| 2026-09-30 | Graph transfer | Two nodes with the same ID merge without warning (tested with the two SD-1 rows) | Links land on the wrong item | Open | Keys by row; a duplicate key stops the build (Step 5) — Transfer thread | Graph test |
| 2026-09-30 | Graph transfer | A Windows-style line-ending change collapses the spec's 645-page split to 1 piece | Page citations break | Open | .gitattributes before any upload; fingerprint check (Steps 2 and 4) — Carl, Transfer thread | Simulation 2026-09-30 |
| 2026-09-30 | Graph transfer | Unknown whether GitHub-synced files reach bash in /mnt/project | Decides sync versus direct upload | Open | Test in Step 4 — Transfer thread | Plan Step 4 |
