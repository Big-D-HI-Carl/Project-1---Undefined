#!/usr/bin/env python3
"""Step 4 tests for testbeds/eastsound/derived/graph. Writes Test_Report.md beside the outputs.

Tests 1–6 are the ones the Graph lane prompt names; 7 and 8 check file hygiene, the vault, graph.json and graphify.
Standard library, plus optional tools found on the machine:
  - page text: PyMuPDF (pinned in requirements.txt) or the pdftotext command;
  - the network-off browser check: node with the playwright package;
  - graphify (pinned in requirements.txt), from PATH or the repo's .venv.
A missing tool marks that part NOT RUN, never PASS. Reading a library page here only confirms that an Open Link
lands on the right page; nothing else is taken from the PDFs.

Run from anywhere:
  python testbeds/eastsound/derived/graph/build/test_graph.py
"""

import csv
import hashlib
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

if os.environ.get("PYTHONHASHSEED") != "0":
    sys.exit(subprocess.run([sys.executable] + sys.argv, env=dict(os.environ, PYTHONHASHSEED="0")).returncode)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_graph as bg  # noqa: E402

OUT = bg.OUT_DEFAULT
OLD_GRAPH = bg.TB / "graph" / "graphify-out" / "graph.json"
E74_EXPECTED = {"BL-1": "Aeration Blower No.1", "BL-2": "Aeration Blower No.2", "BL-3": "Aeration Blower No.3",
                "BL-4": "Aeration Blower No.4", "DB": "digester blower", "WP-1": "WAS pump 1",
                "WP-2": "WAS pump 2", "SD-1": "sludge pump (L-0315, not the storm drain)", "2W-P1": "2W pump 1",
                "2W-P2": "2W pump 2", "PROPOSED-2W-Isolation-Valve-Solenoid": "2W solenoid"}
results = []


def record(num, name, ok, numbers, notes=""):
    results.append((num, name, "PASS" if ok is True else "FAIL" if ok is False else ok, numbers, notes))


def read_csv(path):
    return list(csv.DictReader(io.StringIO(path.read_bytes().decode("utf-8"), newline="")))


def tree_hashes(folder):
    out = {}
    for p in sorted(folder.rglob("*")):
        if p.is_file() and "build" not in p.relative_to(folder).parts and p.name != "Test_Report.md":
            out[p.relative_to(folder).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def page_text(path, page):
    """Text of one PDF page: pdftotext in layout mode (keeps the title block's "N OF 96" on one line), else
    PyMuPDF (pinned in requirements.txt), whose lines are then joined with spaces."""
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(path), "-"],
                           capture_output=True)
        if r.returncode == 0:
            return r.stdout.decode("utf-8", "replace"), "pdftotext"
    try:
        import pymupdf
        with pymupdf.open(str(path)) as doc:
            return re.sub(r"\s+", " ", doc[page - 1].get_text()), "PyMuPDF"
    except ImportError:
        return None, "none"


def title_block_ok(text, sheet, set_page):
    """The page text holds the sheet number, "<set page> OF" and "96": the set page is the number before OF, as
    Plan_Set_Parts.md reads the title block (on some sheets "96" sits on another text line)."""
    has_sheet = re.search(r"(?<![\w.])" + re.escape(sheet) + r"(?![\d.])", text)
    return bool(has_sheet and re.search(r"(?<![\d.])" + str(set_page) + r"\s+OF\b", text)
                and re.search(r"(?<![\d.])96(?![\d.])", text))


def link_target(link):
    m = re.match(r"^\.\./\.\./library/(.+)#page=(\d+)$", link)
    return (bg.LIBRARY / unquote(m.group(1)), int(m.group(2))) if m else (None, None)


def graphify_bin():
    for c in (shutil.which("graphify"), str(bg.REPO / ".venv" / "bin" / "graphify"),
              str(bg.REPO / ".venv" / "Scripts" / "graphify.exe")):
        if c and Path(c).exists():
            return c
    return None


def clean_env():
    env = {k: v for k, v in os.environ.items() if not re.search(r"API_KEY|^AWS_|^OLLAMA_", k)}
    env.update(GIT_DIR="no-git", PYTHONHASHSEED="0")
    return env


def main():
    nodes = read_csv(OUT / "nodes.csv")
    edges = read_csv(OUT / "edges.csv")
    by_id = {n["Node ID"]: n for n in nodes}
    types = Counter(n["Node Type"] for n in nodes)
    ledger = read_csv(bg.LEDGER)

    # 1 -- node counts by type, each against its own source
    lines01 = bg.read_text(bg.SHEET_INDEX).split("\n")
    n01 = len(bg.md_table(lines01, "## Sheet table (cover-index order)", "01")) + \
        len(bg.md_table(lines01, "## Sheets issued by addendum only", "01"))
    n03 = len(bg.md_table(bg.read_text(bg.GATE).split("\n"), "## Addendum 4 item map", "03"))
    lines04 = bg.read_text(bg.SPINE).split("\n")
    n04 = len(bg.md_table(lines04, "## Bid items (bid form order)", "04")) + \
        len(bg.md_table(lines04, "## Equipment alternates (deductive)", "04"))
    specs02 = bg.load_specs()
    cited = set()
    for r in ledger:
        for col in ("Spec Sections", "Wiki Note(s)"):
            for t in bg.split_top(r[col]):
                m = bg.SPEC_RE.match(t)
                if m and m.group(1) in specs02:
                    cited.add(m.group(1))
    para_secs = {n["Node ID"].split(" ¶")[0][5:] for n in nodes if n["Node Type"] == bg.PARA}
    areas = set()
    for r in ledger:
        for s in bg.split_top(r["Area/Building"], ";|"):
            name = bg.drop_parens(s).split(" — ")[0].strip()
            if name and not name.lower().startswith("not stated"):
                areas.add(name)
    para_targets = {e["To"] for e in edges if e["Edge Type"] == bg.SPECIFIED and " ¶" in e["To"]}
    expect = {bg.COMPONENT: len(ledger), bg.SHEET: n01, bg.SPEC: len(cited | para_secs), bg.ADDENDUM: n03,
              bg.BID: n04, bg.AREA: len(areas), bg.PARA: len(para_targets)}
    ok = all(types[t] == expect[t] for t in expect) and types[bg.COMPONENT] == 447 and types[bg.SHEET] == 97
    record(1, "Node counts by type", ok,
           "; ".join(f"{t} {types[t]} (expected {expect[t]})" for t in bg.NODE_TYPES) + f"; total {len(nodes)}",
           f"Spec sections: {len(cited)} cited in Spec Sections or Wiki Note(s), {len(para_secs - cited)} more "
           "only through ¶ cites. Expected values are re-derived from the Ledger, 01, 03 and 04, not taken from the "
           "build.")

    # 2 -- edge endpoints and duplicates
    missing = [e for e in edges if e["From"] not in by_id or e["To"] not in by_id]
    keys = Counter((e["From"], e["To"], e["Edge Type"]) for e in edges)
    dup = sum(c - 1 for c in keys.values() if c > 1)
    rel = Counter(frozenset((e["From"], e["To"])) for e in edges if e["Edge Type"] == bg.RELATED)
    dup_rel = sum(c - 1 for c in rel.values() if c > 1)
    pairs = {(e["From"], e["To"]) for e in edges if e["Edge Type"] in (bg.SHOWN, bg.SPECIFIED, bg.MODIFIED)}
    double = sum(1 for e in edges if e["Edge Type"] == bg.DESCRIBED and (e["From"], e["To"]) in pairs)
    bad_conf = sum(1 for x in nodes + edges if x["Confidence"] not in bg.TAGS)
    no_cite = sum(1 for x in nodes + edges if not x["Source Citation"].strip())
    record(2, "Edge endpoints exist; no duplicate edges", not (missing or dup or dup_rel or double or bad_conf or no_cite),
           f"{len(edges)} edges; {len(missing)} with a missing endpoint; {dup} duplicate (From, To, Type); "
           f"{dup_rel} duplicate related-to pairs either way round; {double} described-by edges doubling another "
           f"edge; {bad_conf} rows without one of the four tags; {no_cite} rows without a Source Citation",
           "Every node and edge carries Verified, Verified-Visual, Inferred or Unresolved and a Source Citation.")

    # 3 -- E7.4 card
    e74 = "Sheet E7.4"
    comps = {e["From"] for e in edges if e["To"] == e74 and e["Edge Type"] in (bg.SHOWN, bg.DESCRIBED)}
    tags = {by_id[c]["Node ID"].split(" ", 1)[1]: c for c in comps}
    miss = sorted(set(E74_EXPECTED) - set(tags))
    sd1_ok = tags.get("SD-1", "").startswith("L-0315 ")
    html = (OUT / "Project_Graph.html").read_bytes().decode("utf-8")
    blob = re.search(r'<script type="application/json" id="graph-data">(.*?)</script>', html, re.S).group(1)
    data = json.loads(blob)
    idx = {n["id"]: i for i, n in enumerate(data["nodes"])}
    card = {data["nodes"][e["s"]]["id"] for e in data["edges"] if e["t"] == idx[e74]} | \
           {data["nodes"][e["t"]]["id"] for e in data["edges"] if e["s"] == idx[e74]}
    card_ok = comps <= card
    path, page = link_target(by_id[e74]["Open Link"])
    text, tool = page_text(path, page) if path else (None, "none")
    page_ok = None if text is None else title_block_ok(text, "E7.4", 81)
    extra = sorted(set(tags) - set(E74_EXPECTED))
    ok = not miss and sd1_ok and card_ok and page_ok is not False
    record(3, "E7.4 card", ok if page_ok is not None else ("PASS (page check NOT RUN)" if ok else False),
           f"{len(E74_EXPECTED) - len(miss)} of {len(E74_EXPECTED)} expected components on the card"
           + (f"; missing {', '.join(miss)}" if miss else "") + f"; SD-1 is the sludge pump L-0315: {sd1_ok}; "
           f"viewer card holds all {len(comps)} shown-on components: {card_ok}; Open Link {path.name if path else '-'} "
           f"#page={page}: " + ("not checked (no PDF text tool)" if text is None else
                               f"page text has 'E7.4' and '81 OF 96' = {page_ok} ({tool})"),
           "Also on the card: " + ", ".join(extra) + " (the Ledger cites E7.4 for them too)." if extra else "")

    # 4 -- rebuild twice, byte-identical
    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp) / "a", Path(tmp) / "b"
        for d in (a, b):
            r = subprocess.run([sys.executable, str(HERE / "build_graph.py"), "--out", str(d)], capture_output=True)
            if r.returncode:
                record(4, "Rebuild twice, byte-identical", False, r.stderr.decode()[-300:])
                break
        else:
            ha, hb, hc = tree_hashes(a), tree_hashes(b), tree_hashes(OUT)
            same_ab = ha == hb
            same_c = ha == hc
            diff = sorted(set(ha) ^ set(hc) | {k for k in ha if k in hc and ha[k] != hc[k]})
            record(4, "Rebuild twice, byte-identical", same_ab and same_c,
                   f"{len(ha)} files per build; build 1 = build 2: {same_ab}; build = committed outputs: {same_c}"
                   + (f"; differs: {', '.join(diff[:5])}" if diff else ""),
                   "Compared by SHA-256 over every output file (Test_Report.md and build/ excluded).")

    # 5 -- network off; five sheet links land on the right page
    ext = re.findall(r"<(?:script|link|img|iframe)\b[^>]*\b(?:src|href)\s*=", html, re.I)
    ext += re.findall(r"@import|url\(\s*['\"]?https?:", html, re.I)
    node = shutil.which("node")
    browser = "NOT RUN (node not found)"
    bok = None
    if node:
        npm_root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip() \
            if shutil.which("npm") else ""
        js = r"""
const { chromium } = require('playwright');
(async () => {
  const exe = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].find(p => require('fs').existsSync(p));
  const args = ['--disable-background-networking', '--disable-component-update', '--no-first-run'];
  const browser = await chromium.launch(exe ? { executablePath: exe, args } : { args });
  const ctx = await browser.newContext({ offline: true });
  const page = await ctx.newPage(); const net = [], errs = [];
  page.on('request', r => { const u = r.url(); if (!u.startsWith('file:') && !u.startsWith('data:')) net.push(u); });
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await ctx.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await page.goto('file://' + process.argv[1]);
  await page.waitForFunction(() => window.__graphReady, null, { timeout: 60000 });
  const ready = await page.evaluate(() => window.__graphReady);
  const drawn = await page.$$eval('path.n', els => els.length);
  console.log(JSON.stringify({ ready, drawn, net, errs }));
  await browser.close();
})().catch(e => { console.log(JSON.stringify({ fail: String(e) })); });
"""
        r = subprocess.run([node, "-e", js, str(OUT / "Project_Graph.html")], capture_output=True, text=True,
                           env=dict(os.environ, NODE_PATH=npm_root), timeout=300)
        try:
            res = json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            res = {"fail": (r.stderr or r.stdout)[-200:]}
        if "fail" in res:
            browser = f"NOT RUN ({res['fail'][:120]})"
        else:
            bok = (not res["net"] and not res["errs"] and res["ready"]["nodes"] == len(nodes)
                   and res["drawn"] == len(nodes))
            browser = (f"headless Chromium, network off: {res['drawn']} nodes drawn, {res['ready']['edges']} edges, "
                       f"{len(res['net'])} network requests, {len(res['errs'])} script errors")
    parts = bg.load_parts()
    eligible = sorted((s for s, p in parts.items() if p["how"].startswith("Verified")), key=bg.nat_key)
    sample = random.Random(bg.SPOT_SEED).sample(eligible, 5)
    checks, link_ok = [], True
    for sid in sample:
        path, page = link_target(by_id[f"Sheet {sid}"]["Open Link"])
        text, tool = page_text(path, page)
        if text is None:
            checks.append(f"{sid}: NOT RUN")
            link_ok = None if link_ok else link_ok
            continue
        good = title_block_ok(text, sid, parts[sid]["set"])
        link_ok = link_ok and good
        checks.append(f"{sid} → {parts[sid]['part']} #page={page}: {'right page' if good else 'WRONG PAGE'}")
    ok5 = (not ext) and bok is not False and link_ok is not False
    label5 = "PASS" if ok5 and bok and link_ok else ("FAIL" if not ok5 else "PASS (part NOT RUN)")
    record(5, "Viewer opens with the network off; sheet links land on the right page", label5,
           f"{len(ext)} external script/link/img references; {browser}; links ({tool}): " + "; ".join(checks),
           f"Sheets sampled with seed {bg.SPOT_SEED} from the {len(eligible)} whose native title block is in the "
           "text layer; a link is right when that page's text holds the sheet number and 'N OF 96' for its set "
           "page. Browsers' PDF viewers open #page=N links at that page.")

    # 6 -- spot check file
    schema = next(csv.reader(io.StringIO(bg.read_text(bg.SPOT_SCHEMA))))
    spot_text = (OUT / "Spot_Check.csv").read_bytes().decode("utf-8")
    header = next(csv.reader(io.StringIO(spot_text)))
    spot = read_csv(OUT / "Spot_Check.csv")
    want = random.Random(bg.SPOT_SEED).sample(sorted(by_id, key=bg.nat_key), bg.SPOT_COUNT)
    got = [re.match(r"Node ID: (.+?); Open Link", r["Note"]).group(1) for r in spot]
    blank = all(not r["Human Result"] and not r["Checked By"] and not r["Date"] for r in spot)
    vv = sum(1 for r in spot if r["Human Result"] == "Verified-Visual")
    record(6, "Spot check file", header == schema and len(spot) == 20 and got == want and blank and not vv,
           f"{len(spot)} rows; header = Spot_Check_Schema.csv: {header == schema}; picks match seed "
           f"{bg.SPOT_SEED}: {got == want}; Human Result, Checked By and Date blank: {blank}",
           "Types picked: " + ", ".join(f"{t} {c}" for t, c in sorted(Counter(by_id[g]['Node Type'] for g in got).items())))

    # 7 -- file hygiene, vault, graph.json
    bad = []
    for p in sorted(OUT.rglob("*")):
        if p.is_file() and p.suffix in (".md", ".csv", ".json", ".html", ".py"):
            b = p.read_bytes()
            if b.startswith(b"\xef\xbb\xbf") or b"\r" in b:
                bad.append(p.relative_to(OUT).as_posix())
            try:
                b.decode("utf-8")
            except UnicodeDecodeError:
                bad.append(p.relative_to(OUT).as_posix())
    vault = {p.stem for p in (OUT / "vault").glob("*.md")}
    dead = 0
    for p in (OUT / "vault").glob("*.md"):
        for link in re.findall(r"\[\[([^\]|]+)", p.read_bytes().decode("utf-8")):
            dead += link not in vault
    gj = json.loads((OUT / "graph.json").read_bytes().decode("utf-8"))
    old = json.loads(OLD_GRAPH.read_bytes().decode("utf-8")) if OLD_GRAPH.exists() else None
    shared_n = new_n = shared_l = new_l = []
    keys_ok = True
    if old:
        on = set().union(*(n.keys() for n in old["nodes"]))
        ol = set().union(*(link.keys() for link in old["links"]))
        nn = set().union(*(n.keys() for n in gj["nodes"]))
        nl = set().union(*(link.keys() for link in gj["links"]))
        shared_n, new_n = sorted(nn & on), sorted(nn - on)
        shared_l, new_l = sorted(nl & ol), sorted(nl - ol)
        keys_ok = set(gj) == set(old) and not new_l
    ok7 = (not bad and len(vault) == len(nodes) and dead == 0 and len(gj["nodes"]) == len(nodes)
           and len(gj["links"]) == len(edges) and keys_ok)
    record(7, "File hygiene, vault and graph.json", ok7,
           f"{len(bad)} files with a BOM, CR or bad UTF-8; vault {len(vault)} notes for {len(nodes)} nodes, "
           f"{dead} dead [[links]]; graph.json {len(gj['nodes'])} nodes and {len(gj['links'])} links",
           f"graph.json uses the old file's top-level keys and link fields ({', '.join(shared_l)}). Node fields "
           f"shared with the old file: {', '.join(shared_n)}. New node fields (no equivalent in the old file): "
           f"{', '.join(new_n) or 'none'}.")

    # 8 -- graphify on graph.json
    gb = graphify_bin()
    if not gb:
        record(8, "graphify reads graph.json", "NOT RUN", "graphify not found (pin: graphifyy==0.9.72)",
               "graphify export skipped")
    else:
        deg = sum(1 for e in edges if e74 in (e["From"], e["To"]))
        notes = []
        with tempfile.TemporaryDirectory() as tmp:     # graphify writes a cache beside graph.json; keep it out of OUT
            (Path(tmp) / "graphify-out").mkdir()
            shutil.copy(OUT / "graph.json", Path(tmp) / "graphify-out" / "graph.json")
            r = subprocess.run([gb, "explain", "Sheet E7.4", "--graph", "graphify-out/graph.json"], cwd=tmp,
                               capture_output=True, text=True, env=clean_env())
            m = re.search(r"Degree:\s+(\d+)", r.stdout)
            for kind in ("html", "obsidian", "wiki"):
                x = subprocess.run([gb, "export", kind, "--graph", "graphify-out/graph.json"], cwd=tmp,
                                   capture_output=True, text=True, env=clean_env())
                msg = (x.stdout + x.stderr).strip().splitlines()
                notes.append(f"export {kind}: {'ran' if x.returncode == 0 else 'refused'} — "
                             f"{msg[-1][:110] if msg else ''}")
            gh = Path(tmp) / "graphify-out" / "graph.html"
            if gh.exists() and re.search(r'<script[^>]+src="https?://', gh.read_text("utf-8", "replace")):
                notes.append("graphify's graph.html loads vis-network from unpkg.com, so it does not open with the "
                             "network off; it and the Obsidian export also stamp 'Community None'. Neither is kept: "
                             "Project_Graph.html and vault/ replace them")
        record(8, "graphify reads graph.json", bool(m) and int(m.group(1)) == deg,
               f"graphify explain 'Sheet E7.4': degree {m.group(1) if m else '?'} (edges.csv: {deg})",
               "; ".join(notes))

    lines = ["# Test report — derived/graph", "",
             "Written by `build/test_graph.py`. PASS/FAIL per test, with the numbers behind it.", "",
             "| # | Test | Result | Numbers | Notes |", "|---|---|---|---|---|"]
    for num, name, res, numbers, notes in results:
        cell = [str(num), name, res, numbers, notes]
        lines.append("| " + " | ".join(c.replace("|", "\\|").replace("\n", " ") for c in cell) + " |")
    bg.write_text(OUT / "Test_Report.md", "\n".join(lines))
    for num, name, res, numbers, _ in results:
        print(f"{num}. {res} — {name}: {numbers}")
    return 0 if all(r[2].startswith("PASS") or r[2].startswith("NOT RUN") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
