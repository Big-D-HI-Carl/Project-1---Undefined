#!/usr/bin/env python3
"""Build the Project Wiki graph from the Project Ledger, the index files and the Wiki notes.

Owner: Graph lane (branch graph-lane-ledger-build). Writes only into testbeds/eastsound/derived/graph/ (or --out):

  nodes.csv            one row per node: Node ID, Label, Node Type, Lane, Area/Building, Discipline, Summary,
                       Bid Item, Status, Confidence, Source Citation, Open Link, Ledger Row, Wiki Note ID
  edges.csv            one row per edge: From, To, Edge Type, Label, Source Citation, Confidence
  Findings.md          every Ledger gap the build hit (logged, never fixed)
  Project_Graph.html   one self-contained viewer; D3 is inlined, so it opens with the network off
  vault/               one Markdown note per node, named by its Label, with [[wikilinks]] to every neighbour
  graph.json           the same graph in the field names of graph/graphify-out/graph.json
  Spot_Check.csv       20 nodes for a person to check (seed 20261002), in index/Spot_Check_Schema.csv columns
  README.md            inputs, counts, the edge map, rebuild steps

Inputs (read-only): the Ledger (Project_Ledger.csv, 447 rows) and its Ledger ID map; index files 01 rev2 (rev1 is
read to confirm the titles match), 02, 03, 04 and Ledger_Schema.csv / Spot_Check_Schema.csv; Plan_Set_Parts.md;
the Wiki notes (Wiki_Notes.csv, Wiki_Links.csv and Project_Wiki.md, parsed with tools/parse_wiki.py). No library
PDF is opened and no LLM is called.

Deterministic: no timestamps (the build date is a constant), every list sorted, UTF-8 without a BOM, LF line
endings, PYTHONHASHSEED=0 (the script re-runs itself with it). Two runs on the same inputs give identical bytes.

D3 7.9.0 is inlined into the viewer. The build downloads the npm tarball and checks it against the pinned sha512;
with no network it reuses the D3 block of an existing Project_Graph.html, checked against the pinned sha256.

Run from anywhere (standard library only):
  python testbeds/eastsound/derived/graph/build/build_graph.py [--out <folder>]
"""

import argparse
import base64
import csv
import hashlib
import importlib.util
import io
import json
import os
import random
import re
import subprocess
import sys
import tarfile
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

if os.environ.get("PYTHONHASHSEED") != "0":
    sys.exit(subprocess.run([sys.executable] + sys.argv, env=dict(os.environ, PYTHONHASHSEED="0")).returncode)

HERE = Path(__file__).resolve().parent                    # testbeds/eastsound/derived/graph/build
OUT_DEFAULT = HERE.parent                                  # testbeds/eastsound/derived/graph
TB = HERE.parents[2]                                       # testbeds/eastsound
REPO = HERE.parents[4]

LEDGER = TB / "project" / "02_Project_Ledger" / "Project_Ledger.csv"
LEDGER_SCHEMA = TB / "index" / "Ledger_Schema.csv"
ID_MAP = TB / "derived" / "reconciliation" / "Ledger_ID_Map.csv"
SHEET_INDEX = TB / "index" / "01_Sheet_Index_rev2.md"
SHEET_INDEX_REV1 = TB / "index" / "01_Sheet_Index_rev1.md"
SPEC_INDEX = TB / "index" / "02_Spec_Index_rev1.md"
GATE = TB / "index" / "03_Coverage_Gate_rev1.md"
SPINE = TB / "index" / "04_Bid_Item_Spine.md"
SPOT_SCHEMA = TB / "index" / "Spot_Check_Schema.csv"
PARTS = TB / "library" / "Plan_Set_Parts.md"
WIKI = TB / "project" / "01_Project_Wiki" / "Project_Wiki.md"
WIKI_NOTES = TB / "derived" / "wiki" / "Wiki_Notes.csv"
WIKI_LINKS = TB / "derived" / "wiki" / "Wiki_Links.csv"
PARSE_WIKI = TB / "tools" / "parse_wiki.py"
LIBRARY = TB / "library"
INPUTS = (LEDGER, LEDGER_SCHEMA, ID_MAP, SHEET_INDEX, SHEET_INDEX_REV1, SPEC_INDEX, GATE, SPINE, SPOT_SCHEMA,
          PARTS, WIKI, WIKI_NOTES, WIKI_LINKS, PARSE_WIKI)

SPEC_FILE = "eswd-wwtp-upgrade-phase-i-specs.pdf"
ADD4_FILE = "addendum-no4-eswd.pdf"
BUILD_DATE = "2026-10-02"
SPOT_SEED = 20261002
SPOT_COUNT = 20

D3_VERSION = "7.9.0"
D3_TARBALL = "https://registry.npmjs.org/d3/-/d3-7.9.0.tgz"
D3_TARBALL_SHA512 = "sha512-e1U46jVP+w7Iut8Jt8ri1YsPOvFpg46k+K8TpCb0P+zjCkjkPnV7WzfDJzMHy1LnA+wj5pLT1wjO901gLXeEhA=="
D3_MIN_SHA256 = "f2094bbf6141b359722c4fe454eb6c4b0f0e42cc10cc7af921fc158fceb86539"
D3_BEGIN = "/* d3 7.9.0 begin */"
D3_END = "/* d3 7.9.0 end */"

TAGS = ("Verified", "Verified-Visual", "Inferred", "Unresolved")
RANK = {t: i for i, t in enumerate(TAGS)}
TAG_RE = re.compile(r"\b(Verified-Visual|Verified|Inferred|Unresolved)\b")
TAG_COLUMN = "Verified/Verified-Visual/Inferred/Unresolved"
GRAPHIFY = {"Verified": ("EXTRACTED", 1.0), "Verified-Visual": ("EXTRACTED", 1.0),
            "Inferred": ("INFERRED", 0.55), "Unresolved": ("AMBIGUOUS", 0.2)}

LANES = ("Civil & Site", "Process & Mechanical", "Electrical & Controls", "Structural & Building",
         "Contract & General")

COMPONENT, SHEET, SPEC, PARA, ADDENDUM, BID, AREA = (
    "Component", "Sheet", "Spec section", "Spec paragraph", "Addendum item", "Bid item", "Area/Building")
NODE_TYPES = (COMPONENT, SHEET, SPEC, PARA, ADDENDUM, BID, AREA)
SHOWN, SPECIFIED, MODIFIED, PAID, LOCATED, DESCRIBED, RELATED, PART = (
    "shown on", "specified by", "modified by", "paid under", "located in", "described by", "related to",
    "part of")
EDGE_TYPES = (SHOWN, SPECIFIED, MODIFIED, PAID, LOCATED, DESCRIBED, RELATED, PART)

NODE_HEADER = ["Node ID", "Label", "Node Type", "Lane", "Area/Building", "Discipline", "Summary", "Bid Item",
               "Status", "Confidence", "Source Citation", "Open Link", "Ledger Row", "Wiki Note ID"]
EDGE_HEADER = ["From", "To", "Edge Type", "Label", "Source Citation", "Confidence"]

SHEET_RE = re.compile(r"^([A-Z]\d{1,2}\.\d{1,2}A?)(?![\d.A-Za-z])\s*(.*)$", re.S)
SHEET_ANY_RE = re.compile(r"(?<![A-Za-z0-9.])([GCSAE]\d{1,2}\.\d{1,2}A?)(?![\d.A-Za-z])")
SPEC_RE = re.compile(r"^(\d\d \d\d \d\d|Appendix [A-I])(?![\d])\s*(.*)$", re.S)
SPEC_ANY_RE = re.compile(r"(?<![\d])(\d\d \d\d \d\d)(?![\d])")
PARA_TOKEN_RE = re.compile(
    r"(?P<sec>(?<![\d])\d\d \d\d \d\d(?![\d]))"
    r"|¶\s?(?P<para>\d+(?:\.\d+)*(?:\s?[–-]\s?\d+(?:\.\d+)*)?(?:\s[A-Z](?:\.\d+)*(?![A-Za-z]))?)")
PARA_PAGE_RE = re.compile(r"\s*,?\s*\(?\s*(?:main spec\s+)?pp?\.\s?(\d+)")
PARA_ODD_RE = re.compile(r"\.\d{3}|^\d+\.0\b")      # three-digit decimals (3.025, 1.012) and N.0
SPEC_ALIASES = {"01 11 00": "01 11 10"}          # 02 decision E: alias accepted, stays Unresolved
DASHES = {"—", "–", "-"}
LABEL_MAX = 60


# ------------------------------------------------------------------ small helpers
def fail(msg):
    sys.stderr.write(f"build_graph: STOP — {msg}\n")
    sys.exit(2)


def rel(path):
    return Path(path).resolve().relative_to(REPO).as_posix()


def read_text(path):
    if not Path(path).exists():
        fail(f"input missing: {rel(path)}")
    return Path(path).read_bytes().decode("utf-8-sig").replace("\r\n", "\n")


def read_csv(path):
    return list(csv.DictReader(io.StringIO(read_text(path), newline="")))


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def weakest(*tags):
    found = [t for t in tags if t]
    return max(found, key=RANK.__getitem__) if found else ""


def strongest(*tags):
    found = [t for t in tags if t]
    return min(found, key=RANK.__getitem__) if found else ""


def tag_words(text):
    return TAG_RE.findall(text or "")


def nat_key(s):
    return [(0, int(p), "") if p.isdigit() else (1, 0, p.casefold()) for p in re.split(r"(\d+)", s)]


def split_top(text, seps=";"):
    """Split on any character in seps that sits outside parentheses and brackets."""
    out, depth, cur = [], 0, []
    for ch in text or "":
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch in seps and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur).strip())
    return [p for p in out if p]


def strip_outer_parens(s):
    s = s.strip()
    if s.startswith("(") and s.endswith(")"):
        depth = 0
        for i, ch in enumerate(s):
            depth += ch == "("
            depth -= ch == ")"
            if depth == 0 and i < len(s) - 1:
                return s
        return s[1:-1].strip()
    return s


def drop_parens(s):
    prev = None
    while prev != s:
        prev, s = s, re.sub(r"\s*\([^()]*\)", "", s)
    return s.strip()


def md_table(lines, heading, name):
    """Rows of the first pipe table after the line equal to `heading`, as dicts keyed by the header cells."""
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == heading)
    except StopIteration:
        fail(f"{name}: heading '{heading}' not found")
    i = start + 1
    while i < len(lines) and not lines[i].startswith("|"):
        i += 1
    if i + 1 >= len(lines):
        fail(f"{name}: no table under '{heading}'")

    def cells(ln):
        return [c.strip() for c in re.split(r"(?<!\\)\|", ln.strip()[1:-1])]

    header = cells(lines[i])
    rows = []
    for j in range(i + 2, len(lines)):
        ln = lines[j]
        if not ln.startswith("|"):
            break
        c = cells(ln)
        if len(c) != len(header):
            fail(f"{name} line {j + 1}: {len(c)} cells, header has {len(header)}")
        rows.append(dict(zip(header, c), _line=j + 1))
    return rows


def short_file(name):
    """Plans file names as the index files abbreviate them (plans_N, Part N)."""
    m = re.match(r"Pages_from_eswd-wwtp-upgrade-ph1-11x17-(plans_\w+?)\.pdf$", name)
    if m:
        return m.group(1)
    m = re.match(r"Pages from eswd-wwtp-upgrade-ph1-11x17-plans(?: -)? (Part \d)\.pdf$", name)
    if m:
        return m.group(1)
    if name == ADD4_FILE:
        return "Add. 4"
    return name


def lib_link(filename, page):
    return f"../../library/{quote(filename)}#page={page}"


def lanes_of(text):
    return [ln for ln in LANES if ln in (text or "")]


# ------------------------------------------------------------------ findings
class Findings:
    def __init__(self):
        self.sections = defaultdict(list)     # title -> rows (tuple of cells)
        self.headers = {}
        self.notes = {}

    def add(self, section, header, row, note=""):
        self.headers.setdefault(section, header)
        if note:
            self.notes.setdefault(section, note)
        self.sections[section].append(tuple(str(c) for c in row))

    def count(self, section):
        return len(set(self.sections.get(section, [])))


# ------------------------------------------------------------------ inputs
def load_ledger(fx):
    schema = next(csv.reader(io.StringIO(read_text(LEDGER_SCHEMA))))
    text = read_text(LEDGER)
    reader = csv.reader(io.StringIO(text, newline=""))
    header = next(reader)
    if header != schema:
        fail("Project_Ledger.csv header differs from index/Ledger_Schema.csv")
    rows = []
    for n, cells in enumerate(reader, 2):
        if len(cells) != len(header):
            fail(f"Project_Ledger.csv line {n}: {len(cells)} fields")
        r = dict(zip(header, cells))
        r["_row"] = n
        tags = tag_words(r[TAG_COLUMN])
        if not tags:
            fail(f"Project_Ledger.csv line {n}: no tag word in the tag column")
        r["_tag"] = tags[0]
        rows.append(r)
    idmap = read_csv(ID_MAP)
    if len(idmap) != len(rows):
        fail(f"Ledger_ID_Map.csv has {len(idmap)} rows, the Ledger {len(rows)}")
    for r, m in zip(rows, idmap):
        if int(m["Ledger Row"]) != r["_row"] or m["Tag"] != r["Tag"]:
            fail(f"Ledger_ID_Map.csv is stale at Ledger row {r['_row']} ({m['Ledger ID']})")
        r["_id"] = m["Ledger ID"]
    counts = Counter(r["Tag"] for r in rows)
    for r in rows:
        if counts[r["Tag"]] > 1:
            fx.add("Duplicate Tags (two Ledger rows, one Tag)", ("Tag", "Ledger row", "Ledger ID", "Name", "Tag level"),
                   (r["Tag"], r["_row"], r["_id"], r["Name"], "Unresolved"),
                   "Keyed by Ledger row, so each row is its own node; nothing is merged (Graph_Transfer_Ultraplan §5).")
    return rows


def load_parts():
    lines = read_text(PARTS).split("\n")
    files = {}
    for ln in lines:
        m = re.match(r"^- \*\*(Part \d)\*\* = `(.+)`$", ln)
        if m:
            files[m.group(1)] = m.group(2)
    out = {}
    for part in ("Part 1", "Part 2", "Part 3"):
        if part not in files or not (LIBRARY / files[part]).exists():
            fail(f"Plan_Set_Parts.md: {part} file not found in library/")
        for r in md_table(lines, f"### {part}", "Plan_Set_Parts.md"):
            out[r["Sheet"]] = {"part": part, "file": files[part], "page": int(r["File p."]),
                               "set": int(r["Set p."]), "how": r["How the sheet is known"], "line": r["_line"]}
    return out


def load_sheets(fx):
    lines = read_text(SHEET_INDEX).split("\n")
    main = md_table(lines, "## Sheet table (cover-index order)", "01 rev2")
    addonly = md_table(lines, "## Sheets issued by addendum only", "01 rev2")
    log = md_table(lines, "## Page-level text extraction log", "01 rev2")
    sheets = {}
    for r in main:
        r["_set"] = r["Set p."]
        sheets[r["Sheet"]] = r
    for r in addonly:
        r["_set"] = ""
        r["Addendum 4"] = "—"
        sheets[r["Sheet"]] = r
    add4 = {}
    for r in log:
        if r["File"] == ADD4_FILE and r["Indexed"].startswith("Yes (addendum)"):
            add4[r["Sheet"]] = int(r["PDF p."])
    rev1 = read_text(SHEET_INDEX_REV1).split("\n")
    titles1 = {r["Sheet"]: r["Title (title block)"] for r in md_table(rev1, "## Sheet table (cover-index order)",
                                                                       "01 rev1")}
    titles1.update({r["Sheet"]: r["Title (title block)"] for r in md_table(rev1, "## Sheets issued by addendum only",
                                                                            "01 rev1")})
    for sid in sorted(set(titles1) | set(sheets), key=nat_key):
        if titles1.get(sid) != sheets.get(sid, {}).get("Title (title block)"):
            fx.add("01 rev1 and rev2 disagree on a sheet title", ("Sheet", "rev1", "rev2", "Tag level"),
                   (sid, titles1.get(sid, "(none)"), sheets.get(sid, {}).get("Title (title block)", "(none)"),
                    "Unresolved"))
    return sheets, add4


def load_specs():
    lines = read_text(SPEC_INDEX).split("\n")
    out = {}
    for r in md_table(lines, "## Section table (document order)", "02"):
        if re.match(r"^(\d\d \d\d \d\d|Appendix [A-I])$", r["Section (body)"]):
            out[r["Section (body)"]] = r
    return out


def load_addenda():
    lines = read_text(GATE).split("\n")
    items = []
    for r in md_table(lines, "## Addendum 4 item map", "03"):
        text = r["Item"]
        pages = []
        for a, b in re.findall(r"(\d+)(?:\s*[–-]\s*(\d+))?", r["Add. 4 p."]):
            pages.extend(range(int(a), int(b or a) + 1))
        it = {"text": text, "pages": pages, "touches": r["Touches"], "lane": r["Primary lane"],
              "also": r["Also affects"], "pcol": r["Add. 4 p."], "line": r["_line"], "row": r,
              "clar": None, "section": None, "sheets": []}
        m = re.match(r"^Clarification (\d+)\b", text)
        if m:
            it["clar"] = int(m.group(1))
            it["id"] = f"Add. 4 Clarification {it['clar']}"
        elif text.startswith("Specifications"):
            m = re.search(r"(\d\d \d\d \d\d) ¶(\S+(?: [A-Z])?)", text)
            if not m:
                fail(f"03 line {r['_line']}: no section in '{text}'")
            it["section"] = m.group(1)
            it["id"] = f"Add. 4 Specifications {m.group(1)} ¶{m.group(2)}"
        elif text.startswith("Drawings"):
            it["sheets"] = SHEET_ANY_RE.findall(r["Touches"])
            it["id"] = "Add. 4 Drawings " + ", ".join(it["sheets"])
        else:
            fail(f"03 line {r['_line']}: unknown item form '{text}'")
        items.append(it)
    if len({i["id"] for i in items}) != len(items):
        fail("03 item map: two items share an ID")
    return items


def load_bids():
    lines = read_text(SPINE).split("\n")
    out = []
    for r in md_table(lines, "## Bid items (bid form order)", "04"):
        out.append({"id": f"Bid Item {r['Item']}", "key": r["Item"], "desc": r["Description (bid form)"],
                    "row": r, "page": int(re.search(r"\d+", r["Bid form p."]).group()), "kind": "item"})
    text = "\n".join(lines)
    m = re.search(r"A–D on p\.(\d+) and E on p\.(\d+)", text)
    if not m:
        fail("04: alternate pages sentence ('A–D on p.N and E on p.M') not found")
    for r in md_table(lines, "## Equipment alternates (deductive)", "04"):
        letter = r["Alternate"].split()[-1]
        out.append({"id": r["Alternate"], "key": letter, "desc": r["Description (bid form)"], "row": r,
                    "page": int(m.group(2) if letter == "E" else m.group(1)), "kind": "alternate"})
    return out


def load_wiki(fx):
    """Wiki notes keyed by Note ID, with the full Summary, Tags and Related documents from Project_Wiki.md."""
    rows = read_csv(WIKI_NOTES)
    spec = importlib.util.spec_from_file_location("parse_wiki", PARSE_WIKI)
    pw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pw)
    lines = read_text(WIKI).split("\n")
    blocks = {b["line"]: pw.parse_note(b) for b in pw.note_blocks(lines)}
    notes = {}
    for r in rows:
        line = int(r["Heading Line"])
        b = blocks.get(line)
        if b is None or b["id"] != r["Note ID"]:
            fail(f"Wiki_Notes.csv: note {r['Note ID']} is not at Project_Wiki.md line {line}")
        f = b["fields"]
        full = f.get("Summary", (r["Summary (first 600 characters)"], line))
        if "Summary" not in f:
            fx.add("Wiki notes whose full text did not parse", ("Note ID", "Project_Wiki.md line", "Tag level"),
                   (r["Note ID"], line, "Unresolved"), "The 600-character summary from Wiki_Notes.csv is used.")
        notes[r["Note ID"]] = {
            "id": r["Note ID"], "title": r["Title"], "lane": r["Lane"], "type": r["Type"],
            "discipline": r["Discipline"], "revision": r["Revision/Date"], "summary": full[0],
            "summary_line": full[1], "tags": f.get("Tags", ("", 0))[0],
            "related": f.get("Related documents", ("", 0))[0], "where": r["Where It Lives"], "line": line}
    return notes


def load_related():
    out = []
    for n, r in enumerate(read_csv(WIKI_LINKS), 2):
        if r["Source"] == "related documents" and r["Target Type"] in ("sheet", "spec section"):
            out.append(dict(r, _line=n))
    return out


# ------------------------------------------------------------------ the graph
class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}                      # (from, to, type) -> edge

    def node(self, nid, **kw):
        if nid in self.nodes:
            fail(f"duplicate node ID {nid}")
        n = {h: "" for h in NODE_HEADER}
        n.update({"Node ID": nid, "_extra": {}})
        n.update(kw)
        self.nodes[nid] = n
        return n

    def edge(self, a, b, etype, label, cite, conf, combine="weakest"):
        key = (a, b, etype)
        e = self.edges.get(key)
        if e is None:
            e = self.edges[key] = {"From": a, "To": b, "Edge Type": etype, "_labels": [], "_cites": [],
                                   "_confs": [], "_count": 0, "_wiki": False, "_combine": combine, "_rows": []}
        e["_count"] += 1
        if label and label not in e["_labels"]:
            e["_labels"].append(label)
        if cite and cite not in e["_cites"]:
            e["_cites"].append(cite)
        e["_confs"].append(conf)
        return e

    def finish(self):
        for e in self.edges.values():
            parts = list(e["_labels"])
            if e["_count"] > 1:
                parts.insert(0, f"{e['_count']} citations")
            if e["_wiki"]:
                parts.append("also in Wiki note")
            e["Label"] = "; ".join(parts)
            e["Source Citation"] = " | ".join(e["_cites"])
            e["Confidence"] = (strongest if e["_combine"] == "strongest" else weakest)(*e["_confs"])


def component_label(r):
    name = head_top(r["Name"], (" — ", " | ", "; "))
    if len(name) > LABEL_MAX:
        name = drop_parens(name)
    if len(name) > LABEL_MAX:
        cut = [m.start() for m in re.finditer(r", ", name) if m.start() <= LABEL_MAX]
        if cut:
            name = name[:cut[-1]]
        else:
            sp = name.rfind(" ", 0, LABEL_MAX)
            name = name[:sp if sp > 0 else LABEL_MAX].rstrip(" ,;:") + "…"
    if r["Tag"].startswith("PROPOSED-"):
        first = next((m.group(1) for t in split_top(r["Drawing Sheets"]) for m in [SHEET_RE.match(t)] if m), None)
        return f"{name} · {first} (no tag)" if first else f"{name} · no sheet (no tag)"
    return f"{r['Tag']} · {name}"


def head_top(text, seps):
    """Text before the first separator that sits outside brackets."""
    depth = 0
    for i, ch in enumerate(text):
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        elif depth == 0 and any(text.startswith(sp, i) for sp in seps):
            return text[:i].strip()
    return text.strip()


def find_fragments(citation, key):
    pat = re.compile(r"(?<![A-Za-z0-9.])" + re.escape(key) + r"(?![\d.A-Za-z])")
    return [s for s in split_top(citation) if pat.search(s)]


def paragraphs(text):
    """(section, paragraph, page or None) for every ¶ in a Source Citation, in order; plus unattached ¶ tokens."""
    seg_of, seg, depth = [], 0, 0
    for ch in text:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch == ";" and depth == 0:
            seg += 1
        seg_of.append(seg)
    found, loose, cur = [], [], None
    for m in PARA_TOKEN_RE.finditer(text):
        if m.group("sec"):
            cur = (m.group("sec"), seg_of[m.start()])
            continue
        para = re.sub(r"\s+", " ", m.group("para")).strip()
        pm = PARA_PAGE_RE.match(text, m.end())
        page = int(pm.group(1)) if pm else None
        if cur and cur[1] == seg_of[m.start()]:
            found.append((cur[0], para, page))
        else:
            loose.append(para)
    return found, loose


def build(out_dir):
    fx = Findings()
    ledger = load_ledger(fx)
    parts = load_parts()
    sheets, add4_pages = load_sheets(fx)
    specs = load_specs()
    add_items = load_addenda()
    bids = load_bids()
    notes = load_wiki(fx)
    related = load_related()
    g = Graph()

    # ---------------------------------------------------------------- sheet nodes (01 rev2: 96 + C1.6A)
    for sid in sorted(sheets, key=nat_key):
        r = sheets[sid]
        note = notes.get(sid)
        title = note["title"] if note else r["Title (title block)"].replace(" (cover index)", "")
        p = parts.get(sid)
        if p:
            link = lib_link(p["file"], p["page"])
            where = f"Plan_Set_Parts.md {p['part']} p.{p['page']} (set p.{p['set']})"
        elif (LIBRARY / r["File"]).exists():
            link = lib_link(r["File"], r["PDF p."])
            where = f"{short_file(r['File'])} p.{r['PDF p.']} (01 File and PDF p.)"
        else:
            link, where = "", "no library file"
            fx.add("Sheets with no Open Link", ("Sheet", "01 File", "Tag level"), (sid, r["File"], "Unresolved"))
        status = r["Status"]
        if r.get("Read Method"):
            status += f" · Read method {r['Read Method']}"
        if r["Addendum 4"] not in DASHES:
            status += f" · Addendum 4: {r['Addendum 4']}"
        cite = f"01 Sheet Index rev2, {'set p.' + r['_set'] if r['_set'] else 'addendum-only sheet'} " \
               f"({short_file(r['File'])} p.{r['PDF p.']}); {where}"
        if note:
            cite += f"; Wiki note {sid} (Project_Wiki.md line {note['summary_line']})"
        else:
            fx.add("Sheets with no Wiki note", ("Sheet", "Title (01)", "Tag level"), (sid, title, "Unresolved"))
        n = g.node(f"Sheet {sid}", **{
            "Label": f"{sid} · {title}", "Node Type": SHEET, "Lane": r["Lane"], "Discipline": r["Discipline"],
            "Summary": note["summary"] if note else "", "Status": status,
            "Confidence": weakest(*tag_words(r["ID source"])) or "Unresolved", "Source Citation": cite,
            "Open Link": link, "Wiki Note ID": sid if note else ""})
        n["_extra"]["key"] = sid
        n["_extra"]["read_method"] = r.get("Read Method", "")
        if p:
            n["_extra"]["native"] = f"{p['part']} p.{p['page']} (set p.{p['set']})"
        if sid in add4_pages and sid != "C1.6A":
            n["_extra"]["link2"] = lib_link(ADD4_FILE, add4_pages[sid])
            n["_extra"]["link2_label"] = f"Add. 4 p.{add4_pages[sid]} reissue (governs)"
        if note and "unavailable" in note["type"].lower() and r["Status"].startswith("Available"):
            fx.add("Wiki note and 01 rev2 disagree on whether a sheet is in the library",
                   ("Sheet", "Wiki note Type", "01 rev2 Status", "Tag level"),
                   (sid, note["type"], r["Status"], "Unresolved"),
                   "01 rev2 found these sheets in the native parts after the Wiki note was written; the note "
                   "summary still describes the sheet as unavailable. Needs a Wiki note revision (not done here).")

    # ---------------------------------------------------------------- addendum item nodes (03)
    add_by_id = {}
    for it in add_items:
        conf = weakest(*tag_words(" ".join(v for k, v in it["row"].items() if k != "_line"))) or "Verified"
        g.node(it["id"], **{
            "Label": f"Add. 4 · {it['text']}", "Node Type": ADDENDUM, "Lane": it["lane"],
            "Summary": f"{it['text']}. Touches: {it['touches']}. Also affects: {it['also']}.",
            "Status": "Add. 4 governs over base documents" if "conflict" not in it["touches"]
            else "Conflict — see 04 Bid Item Spine",
            "Confidence": conf,
            "Source Citation": f"03 Coverage Gate rev1, Addendum 4 item map (line {it['line']}); Add. 4 {it['pcol']}",
            "Open Link": lib_link(ADD4_FILE, it["pages"][0])})
        add_by_id[it["id"]] = it
    page_items = defaultdict(list)
    for it in add_items:
        for pg in it["pages"]:
            page_items[pg].append(it["id"])
    clar_item = {it["clar"]: it["id"] for it in add_items if it["clar"]}
    spec_item = {it["section"]: it["id"] for it in add_items if it["section"]}
    drawing_items = [it for it in add_items if it["sheets"]]

    # ---------------------------------------------------------------- bid item nodes (04)
    bid_by_key = {}
    for b in bids:
        r = b["row"]
        if b["kind"] == "item":
            summary = (f"{b['desc']}: approx. qty {r['Approx. qty']} {r['Unit']}; {r['Group (as printed)']}; "
                       f"{r['Base / Alternate']}; bid form p.{b['page']}; scope 00 24 13 {r['Scope (00 24 13)']}; "
                       f"references: {r['References in scope']}; addenda: {r['Addenda referencing']}")
            lane = r["Lane (Inferred)"]
            cite = f"04 Bid Item Spine (line {r['_line']}); 00 41 00 bid form p.{b['page']}; 00 24 13 {r['Scope (00 24 13)']}"
            bid_by_key[b["key"]] = b["id"]
        else:
            summary = (f"{b['desc']}: base-bid manufacturer(s) {r['Base-bid manufacturer(s)']}; {r['Pricing']}; "
                       f"tied to {r['Tied to']}; spec {r['Spec section']}; bid form p.{b['page']}; "
                       f"addenda: {r['Addenda referencing']}")
            lane = r["Lane (Inferred)"]
            cite = f"04 Bid Item Spine, equipment alternates (line {r['_line']}); 00 41 00 bid form p.{b['page']}"
            bid_by_key["Alt " + b["key"]] = b["id"]
        cells = " ".join(v for k, v in r.items() if k != "_line")
        g.node(b["id"], **{
            "Label": f"{b['id']} · {b['desc']}", "Node Type": BID, "Lane": lane, "Summary": summary,
            "Status": "" if r["Status"] in DASHES else r["Status"],
            "Confidence": weakest("Inferred", *tag_words(cells)), "Source Citation": cite,
            "Open Link": lib_link(SPEC_FILE, b["page"])})

    # ---------------------------------------------------------------- components and their Ledger edges
    spec_used = defaultdict(set)              # section -> how it entered (column names)
    para_cites = defaultdict(list)            # (section, para) -> [(row, page)]
    area_rows = defaultdict(list)
    comp_of_row = {}
    labels = Counter(component_label(r) for r in ledger)
    for r in ledger:
        lid, row, tag = r["_id"], r["_row"], r["_tag"]
        nid = f"{lid} {r['Tag']}"
        label = component_label(r)
        if labels[label] > 1:
            fx.add("Component labels made unique with the Ledger row", ("Ledger row", "Label", "Tag level"),
                   (row, label, "Verified"))
            label = f"{label} (row {row})"
        n = g.node(nid, **{
            "Label": label, "Node Type": COMPONENT, "Lane": r["Lane"], "Area/Building": r["Area/Building"],
            "Discipline": r["Discipline"], "Summary": r["Name"], "Bid Item": r["Bid Item"], "Status": r["Status"],
            "Confidence": tag, "Source Citation": r["Source Citation"], "Ledger Row": str(row),
            "Wiki Note ID": r["Wiki Note(s)"]})
        n["_extra"].update({"ledger_id": lid, "tag": r["Tag"], "name": r["Name"],
                            "Drawing Sheets": r["Drawing Sheets"], "Spec Sections": r["Spec Sections"],
                            "Addenda": r["Addenda"], "Submittal Req (Y/N)": r["Submittal Req (Y/N)"],
                            "Testing/Startup Req (Y/N)": r["Testing/Startup Req (Y/N)"], "Notes": r["Notes"]})
        comp_of_row[row] = nid
        who = f"Ledger row {row} ({lid})"

        def ledger_cite(column, key=None):
            frag = find_fragments(r["Source Citation"], key) if key else []
            return f"Project_Ledger.csv row {row}, {column}" + (f": {'; '.join(frag)}" if frag else "")

        # Drawing Sheets -> shown on
        sheet_order = []
        cell = r["Drawing Sheets"].strip()
        if not cell:
            fx.add("Drawing Sheets blank (no sheet cited)", ("Ledger row", "Node ID", "Name", "Tag level"),
                   (row, nid, r["Name"], "Unresolved"),
                   "No shown-on edge; the component's Status carries 'no sheet cited'.")
        for t in split_top(cell):
            m = SHEET_RE.match(t)
            if not m:
                fx.add("Drawing Sheets values that are not a sheet number", ("Ledger row", "Node ID", "Value", "Tag level"),
                       (row, nid, t, "Unresolved"), "No edge made.")
                continue
            sid, anchor = m.group(1), strip_outer_parens(m.group(2))
            if sid not in sheets:
                fx.add("Drawing Sheets values not in 01", ("Ledger row", "Node ID", "Sheet", "Tag level"),
                       (row, nid, sid, "Unresolved"), "No edge made.")
                continue
            g.edge(nid, f"Sheet {sid}", SHOWN, anchor, ledger_cite("Drawing Sheets", sid),
                   weakest(tag, *tag_words(t)))
            if sid not in sheet_order:
                sheet_order.append(sid)
        if not sheet_order:
            n["Status"] = (n["Status"] + " · no sheet cited").strip(" ·")
        n["_extra"]["sheets"] = sheet_order

        # Spec Sections -> specified by
        spec_order = []
        cell = r["Spec Sections"].strip()
        if not cell:
            fx.add("Spec Sections blank", ("Ledger row", "Node ID", "Name", "Tag level"),
                   (row, nid, r["Name"], "Unresolved"))
        for t in split_top(cell):
            m = SPEC_RE.match(t)
            sec = m.group(1) if m else None
            alias = sec in SPEC_ALIASES if sec else False
            if alias:
                sec = SPEC_ALIASES[sec]
            if not sec or sec not in specs:
                fx.add("Spec Sections values that don't match 02", ("Ledger row", "Node ID", "Value", "Tag level"),
                       (row, nid, t, "Unresolved"), "No edge made.")
                continue
            anchor = strip_outer_parens(m.group(2))
            if alias:
                anchor = (anchor + "; " if anchor else "") + f"cited as {m.group(1)} (02 alias, decision E)"
            g.edge(nid, f"Spec {sec}", SPECIFIED, anchor, ledger_cite("Spec Sections", sec),
                   weakest(tag, *tag_words(t), "Unresolved" if alias else ""))
            spec_used[sec].add("Spec Sections")
            if sec not in spec_order:
                spec_order.append(sec)

        # Source Citation paragraphs -> specified by (paragraph nodes)
        found, loose = paragraphs(r["Source Citation"])
        for sec, para, page in found:
            sec = SPEC_ALIASES.get(sec, sec)
            if sec not in specs:
                fx.add("Paragraph citations whose section is not in 02", ("Ledger row", "Node ID", "Paragraph", "Tag level"),
                       (row, nid, f"{sec} ¶{para}", "Unresolved"), "No paragraph node made.")
                continue
            para_cites[(sec, para)].append((row, page))
            spec_used[sec].add("Source Citation")
            g.edge(nid, f"Spec {sec} ¶{para}", SPECIFIED, f"p.{page}" if page else "",
                   f"Project_Ledger.csv row {row}, Source Citation: {sec} ¶{para}", tag)
        for para in loose:
            fx.add("Paragraph citations with no section number beside them", ("Ledger row", "Node ID", "Paragraph", "Tag level"),
                   (row, nid, f"¶{para}", "Unresolved"), "No paragraph node made; the section is not stated in the "
                   "same citation segment.")

        # Addenda -> modified by
        prev = None
        for seg in split_top(r["Addenda"], ";|"):
            s = seg.strip()
            if not s or s in DASHES:
                continue
            label = re.sub(r"\s*—\s*Add\. 4 governs\s*$", "", s).strip()
            if re.search(r"\bAdd(?:\.|endum)\s*(?:No\.\s*)?[123]\b", s):
                fx.add("Addenda values citing Addenda 1–3 (not in the library)", ("Ledger row", "Node ID", "Value", "Tag level"),
                       (row, nid, s, "Unresolved"))
            items, inferred, why = set(), False, ""
            for m2 in re.finditer(r"Clarifications?\s+(\d+)((?:\s*(?:,|and)\s*\d+)*)", s):
                for num in [m2.group(1)] + re.findall(r"\d+", m2.group(2)):
                    if int(num) in clar_item:
                        items.add(clar_item[int(num)])
            if re.search(r"exhibit", s, re.I):
                items.add(clar_item[5])
            for m2 in re.finditer(r"(\d\d \d\d \d\d)\s*¶", s):
                if m2.group(1) in spec_item:
                    items.add(spec_item[m2.group(1)])
            pages = set()
            for a, b in re.findall(r"\bpp?\.\s?(\d+)(?:\s*[–-]\s*(\d+))?", s):
                pages.update(range(int(a), int(b or a) + 1))
            pages.update(int(x) for x in re.findall(r"\band p\.(\d+)", s))
            for pg in sorted(pages):
                if len(page_items.get(pg, [])) == 1:
                    items.add(page_items[pg][0])
            named = set(SHEET_ANY_RE.findall(s))
            drawn = {it["id"] for it in drawing_items if named & set(it["sheets"])}
            if 3 in pages and not (items & {it["id"] for it in drawing_items}):
                if drawn:
                    items |= drawn
                else:
                    cand = {it["id"] for it in drawing_items if set(sheet_order) & set(it["sheets"])}
                    if len(cand) == 1:
                        items |= cand
                        inferred, why = True, "p.3 item matched by the row's Drawing Sheets"
                    else:
                        fx.add("Addenda values not matched to one 03 item", ("Ledger row", "Node ID", "Value", "Tag level"),
                               (row, nid, s, "Unresolved"), "Add. 4 p.3 lists five drawing items; the value names "
                               "none and the row's sheets don't settle it, so no edge was made.")
            if 1 in pages and not any(add_by_id[i]["clar"] for i in items) and not re.search("exhibit", s, re.I):
                fx.add("Addenda values not matched to one 03 item", ("Ledger row", "Node ID", "Value", "Tag level"),
                       (row, nid, s, "Unresolved"), "Add. 4 p.1 holds Clarifications 1–5; the value names none.")
            if 2 in pages and not any(add_by_id[i]["section"] for i in items):
                fx.add("Addenda values not matched to one 03 item", ("Ledger row", "Node ID", "Value", "Tag level"),
                       (row, nid, s, "Unresolved"), "Add. 4 p.2 holds five spec items; the value names no section.")
            has_ref = bool(pages or re.search(r"Clarification|exhibit|¶", s, re.I))
            if not has_ref:
                if prev is not None:
                    prev["_labels"].append(label)
                else:
                    fx.add("Addenda values not matched to one 03 item", ("Ledger row", "Node ID", "Value", "Tag level"),
                           (row, nid, s, "Unresolved"), "Text with no Add. 4 page or item.")
                continue
            for iid in sorted(items, key=nat_key):
                conf = weakest(tag, *tag_words(s), "Inferred" if inferred else "")
                cite = f"Project_Ledger.csv row {row}, Addenda: {s}; 03 item map line {add_by_id[iid]['line']}"
                if why:
                    cite += f" ({why})"
                prev = g.edge(nid, iid, MODIFIED, label, cite, conf)

        # Bid Item -> paid under
        for seg in split_top(r["Bid Item"], ";|"):
            s = seg.strip()
            if not s or s in DASHES:
                continue
            if s.lower().startswith("not stated"):
                fx.add("Bid Item not stated", ("Ledger row", "Node ID", "Value", "Tag level"), (row, nid, s, "Unresolved"))
                continue
            core = drop_parens(s)
            if ":" in core:
                core = core.split(":", 1)[1]
            keys = ["Alt " + x for x in re.findall(r"Equipment Alternate ([A-E])\b", core)]
            core = re.sub(r"Equipment Alternate [A-E]\b", " ", core)
            keys += [x for x in re.findall(r"(?<![\w.#])(\d{1,2})(?![\w.])", core)]
            if not keys:
                fx.add("Bid Item text with no item number", ("Ledger row", "Node ID", "Value", "Tag level"),
                       (row, nid, s, "Inferred"), "Kept in the component's Bid Item field; no edge.")
            for k in keys:
                if k not in bid_by_key:
                    fx.add("Bid Item numbers not in 04", ("Ledger row", "Node ID", "Value", "Tag level"),
                           (row, nid, s, "Unresolved"))
                    continue
                g.edge(nid, bid_by_key[k], PAID, s, f"Project_Ledger.csv row {row}, Bid Item: {s}",
                       weakest(tag, *tag_words(s)))

        # Area/Building -> located in
        for seg in split_top(r["Area/Building"], ";|"):
            s = seg.strip()
            name = drop_parens(s).split(" — ")[0].strip()
            if not name or name.lower().startswith("not stated"):
                fx.add("Area/Building not stated", ("Ledger row", "Node ID", "Value", "Tag level"),
                       (row, nid, s, "Unresolved"))
                continue
            area_rows[name].append(row)
            g.edge(nid, f"Area {name}", LOCATED, s if s != name else "",
                   f"Project_Ledger.csv row {row}, Area/Building: {s}", tag)
        n["_extra"]["specs"] = spec_order

    # ---------------------------------------------------------------- Wiki Note(s) -> described by (or mark)
    wiki_cited = Counter()
    for r in ledger:
        nid, row, tag = comp_of_row[r["_row"]], r["_row"], r["_tag"]
        for t in split_top(r["Wiki Note(s)"]):
            target, key, conf_extra = None, None, ""
            m = SHEET_RE.match(t) or SPEC_RE.match(t)
            if m:
                key = m.group(1)
                target = f"Sheet {key}" if SHEET_RE.match(t) else f"Spec {SPEC_ALIASES.get(key, key)}"
            elif re.search(r"generator exhibit", t, re.I):
                key, target, conf_extra = "Add. 4 Generator Exhibit", clar_item[5], "Inferred"
            if key is None or (key not in notes):
                fx.add("Wiki Note(s) values with no Wiki note", ("Ledger row", "Node ID", "Value", "Tag level"),
                       (row, nid, t, "Unresolved"),
                       "No described-by edge. The Project Wiki's note for the CQA plan is titled 'QA plan'.")
                continue
            wiki_cited[key] += 1
            if target.startswith("Spec ") and target[5:] not in specs:
                fx.add("Wiki Note(s) values with no Wiki note", ("Ledger row", "Node ID", "Value", "Tag level"),
                       (row, nid, t, "Unresolved"), "Section not in 02; no edge.")
                continue
            if target.startswith("Spec "):
                spec_used[target[5:]].add("Wiki Note(s)")
            existing = [g.edges.get((nid, target, et)) for et in (SHOWN, SPECIFIED, MODIFIED)]
            existing = [e for e in existing if e]
            if existing:
                for e in existing:
                    e["_wiki"] = True
                    e["_cites"].append(f"Project_Ledger.csv row {row}, Wiki Note(s): {t}")
            else:
                note = notes[key]
                g.edge(nid, target, DESCRIBED, f"Wiki note {key}",
                       f"Project_Ledger.csv row {row}, Wiki Note(s): {t}; Wiki note {key} "
                       f"(Project_Wiki.md line {note['line']})"
                       + ("; 03 places the generator exhibit (Add. 4 pp.11–13) under Clarification 5"
                          if conf_extra else ""),
                       weakest(tag, conf_extra))

    # ---------------------------------------------------------------- spec section and paragraph nodes
    for sec in sorted(spec_used, key=nat_key):
        r = specs[sec]
        note = notes.get(sec)
        title = drop_parens(r["Title (TOC)"])
        status = [f"Main spec pp.{r['Start p.']}–{r['End p.']}"]
        if r["Addendum 4"] not in DASHES:
            status.append(f"Addendum 4: {r['Addendum 4']}")
        if r["Notes"]:
            status.append(r["Notes"])
        cite = f"02 Spec Index rev1 (line {r['_line']}), main spec pp.{r['Start p.']}–{r['End p.']}"
        if note:
            cite += f"; Wiki note {sec} (Project_Wiki.md line {note['summary_line']})"
        else:
            fx.add("Spec sections with no Wiki note", ("Section", "Title (02)", "Tag level"), (sec, title, "Unresolved"))
        n = g.node(f"Spec {sec}", **{
            "Label": f"{sec} · {title}", "Node Type": SPEC, "Lane": r["Lane"],
            "Discipline": note["discipline"] if note else "", "Summary": note["summary"] if note else "",
            "Status": " · ".join(status), "Confidence": weakest(*tag_words(r["Tag"])) or "Unresolved",
            "Source Citation": cite, "Open Link": lib_link(SPEC_FILE, r["Start p."]),
            "Wiki Note ID": sec if note else ""})
        n["_extra"]["key"] = sec
        n["_extra"]["entered_by"] = ", ".join(sorted(spec_used[sec]))
    for (sec, para) in sorted(para_cites, key=lambda k: (nat_key(k[0]), nat_key(k[1]))):
        cites = para_cites[(sec, para)]
        r = specs[sec]
        title = drop_parens(r["Title (TOC)"])
        pages = sorted({p for _, p in cites if p})
        rows = sorted({rw for rw, _ in cites})
        if PARA_ODD_RE.search(para):
            fx.add("Paragraph numbers in an unusual form", ("Paragraph", "Ledger rows", "Tag level"),
                   (f"{sec} ¶{para}", ", ".join(map(str, rows)), "Unresolved"),
                   "Written as in the Ledger Source Citation; may be a typo (e.g. 3.025, 1.012). Not corrected.")
        g.node(f"Spec {sec} ¶{para}", **{
            "Label": f"{sec} ¶{para} · {title}", "Node Type": PARA, "Lane": r["Lane"],
            "Summary": f"Paragraph {para} of {sec} {title}, cited in the Source Citation of Ledger rows "
                       f"{', '.join(map(str, rows))}" + (f" at main spec p.{', p.'.join(map(str, pages))}" if pages else "") + ".",
            "Confidence": "Inferred",
            "Source Citation": f"Project_Ledger.csv Source Citation, rows {', '.join(map(str, rows))}; "
                               f"02 Spec Index rev1: {sec} main spec pp.{r['Start p.']}–{r['End p.']}",
            "Open Link": lib_link(SPEC_FILE, pages[0] if pages else r["Start p."])})
        g.edge(f"Spec {sec} ¶{para}", f"Spec {sec}", PART, "",
               f"Paragraph number written with section {sec} in the Ledger Source Citation; 02 Spec Index rev1 "
               f"line {r['_line']}", "Inferred")

    # ---------------------------------------------------------------- area nodes
    for name in sorted(area_rows, key=nat_key):
        rows = sorted(set(area_rows[name]))
        g.node(f"Area {name}", **{
            "Label": name, "Node Type": AREA,
            "Summary": f"Area/Building '{name}' as written in the Ledger on {len(rows)} rows.",
            "Confidence": "Inferred",
            "Source Citation": f"Project_Ledger.csv Area/Building, rows {', '.join(map(str, rows))} "
                               f"(split on ';' and '|'; bracketed text and text after ' — ' dropped)"})
    variants = defaultdict(set)
    names = sorted(area_rows, key=nat_key)
    for a in names:
        variants[re.sub(r"[^a-z0-9]", "", a.lower().replace("no.", ""))].add(a)
    groups = [sorted(v, key=nat_key) for v in variants.values() if len(v) > 1]
    for a in names:
        wa = set(re.findall(r"[a-z0-9]+", a.lower()))
        for b in names:
            wb = set(re.findall(r"[a-z0-9]+", b.lower()))
            if a != b and len(wa) > 1 and wa < wb:
                groups.append([a, b])
    for grp in sorted({tuple(x) for x in groups}, key=lambda x: [nat_key(y) for y in x]):
        fx.add("Area/Building names that may be the same place (not merged)", ("Names", "Ledger rows", "Tag level"),
               (" / ".join(grp), "; ".join(f"{x}: {len(area_rows[x])}" for x in grp), "Inferred"),
               "Kept as separate areas; merging them is a person's call.")

    # ---------------------------------------------------------------- related to (Wiki note Related documents)
    for r in related:
        a = f"Sheet {r['Note ID']}"
        if a not in g.nodes:
            continue
        b = f"Sheet {r['Target']}" if r["Target Type"] == "sheet" else f"Spec {r['Target']}"
        if b not in g.nodes:
            fx.add("Related documents skipped (target is not a node)", ("Wiki note", "Target", "Wiki_Links.csv line", "Tag level"),
                   (r["Note ID"], r["Target"], r["_line"], "Unresolved"),
                   "Spec targets become nodes only when the Ledger cites the section.")
            continue
        if a == b:
            fx.add("Related documents that point to the note's own sheet", ("Wiki note", "Wiki_Links.csv line", "Tag level"),
                   (r["Note ID"], r["_line"], "Verified"))
            continue
        frm, to = (a, b)
        if b.startswith("Sheet ") and nat_key(b) < nat_key(a):
            frm, to = b, a
        label = f"written as {r['Written As']}" if r["Written As"] != r["Target"] else ""
        cite = f"Wiki note {r['Note ID']}, Related documents (Project_Wiki.md line {r['Wiki Line']})"
        if r["Basis"]:
            cite += f" — {r['Basis']}"
        e = g.edge(frm, to, RELATED, label, cite, r["Confidence"], combine="strongest")
        e["_rows"].append(r["Note ID"])
    for e in g.edges.values():
        if e["Edge Type"] == RELATED and len(set(e["_rows"])) > 1:
            e["_labels"].insert(0, "listed in both notes")

    # ---------------------------------------------------------------- Wiki notes with no node, sheets with no components
    for nid_ in sorted(notes, key=nat_key):
        if f"Sheet {nid_}" in g.nodes or f"Spec {nid_}" in g.nodes:
            continue
        nt = notes[nid_]
        how = ("not a sheet or spec section" if not (SHEET_RE.match(nid_) or SPEC_RE.match(nid_))
               else "spec section the Ledger does not cite")
        if nid_ == "Add. 4 Generator Exhibit":
            how = "carried on Add. 4 Clarification 5 (03: exhibit pp.11–13)"
        fx.add("Wiki notes with no sheet or spec node", ("Note ID", "Title", "Why", "Ledger rows citing it", "Tag level"),
               (nid_, nt["title"], how, wiki_cited.get(nid_, 0), "Unresolved"))
    g.finish()
    shown_to = Counter(e["To"] for e in g.edges.values() if e["Edge Type"] == SHOWN)
    for nid_, n in g.nodes.items():
        if n["Node Type"] == SHEET and not shown_to[nid_]:
            fx.add("Sheets with no components (no Ledger row cites them)", ("Sheet", "Title", "Tag level"),
                   (nid_[6:], n["Label"].split(" · ", 1)[1], "Verified"))

    # ---------------------------------------------------------------- component Open Link
    for n in g.nodes.values():
        if n["Node Type"] != COMPONENT:
            continue
        for sid in n["_extra"].get("sheets", []):
            link = g.nodes[f"Sheet {sid}"]["Open Link"]
            if link:
                n["Open Link"] = link
                n["_extra"]["link_note"] = f"first cited sheet, {sid}"
                break
        else:
            for sec in n["_extra"].get("specs", []):
                n["Open Link"] = g.nodes[f"Spec {sec}"]["Open Link"]
                n["_extra"]["link_note"] = f"first cited spec section, {sec}"
                break
    return g, fx, notes, ledger, sheets, specs


# ------------------------------------------------------------------ writers
def write_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_text(path, text):
    if not text.endswith("\n"):
        text += "\n"
    write_bytes(path, text.encode("utf-8"))


def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow([r.get(h, "") for h in header])
    return buf.getvalue()


def node_order(g):
    order = {t: i for i, t in enumerate(NODE_TYPES)}
    return sorted(g.nodes.values(), key=lambda n: (order[n["Node Type"]], nat_key(n["Node ID"])))


def edge_order(g):
    order = {t: i for i, t in enumerate(EDGE_TYPES)}
    return sorted(g.edges.values(), key=lambda e: (order[e["Edge Type"]], nat_key(e["From"]), nat_key(e["To"])))


def neighbours(g):
    nb = defaultdict(list)
    for e in edge_order(g):
        nb[e["From"]].append(("out", e))
        nb[e["To"]].append(("in", e))
    return nb


OUT_PHRASE = {SHOWN: "Shown on", SPECIFIED: "Specified by", MODIFIED: "Modified by", PAID: "Paid under",
              LOCATED: "Located in", DESCRIBED: "Described by Wiki note", RELATED: "Related to", PART: "Part of"}
IN_PHRASE = {SHOWN: "Shows", SPECIFIED: "Specifies", MODIFIED: "Modifies", PAID: "Pays for", LOCATED: "Contains",
             DESCRIBED: "Describes", RELATED: "Related to", PART: "Paragraphs cited"}


def safe_name(label):
    s = re.sub(r'[\\/:*?"<>|#^\[\]]', "-", label)
    s = re.sub(r"\s+", " ", s).strip().rstrip(". ")
    return s[:150]


def vault_names(g):
    names, seen = {}, Counter()
    for n in node_order(g):
        base = safe_name(n["Label"])
        k = base.casefold()
        seen[k] += 1
        names[n["Node ID"]] = base if seen[k] == 1 else f"{base} ({seen[k]})"
    return names


def write_vault(g, notes, out):
    vdir = out / "vault"
    names = vault_names(g)
    if vdir.exists():
        for p in sorted(vdir.glob("*.md")):
            p.unlink()
    nb = neighbours(g)
    for n in node_order(g):
        x = n["_extra"]
        lines = [f"# {n['Label']}", ""]
        fields = [("Node ID", n["Node ID"]), ("Node type", n["Node Type"]), ("Lane", n["Lane"]),
                  ("Area/Building", n["Area/Building"]), ("Discipline", n["Discipline"]),
                  ("Bid Item", n["Bid Item"]), ("Status", n["Status"]), ("Confidence", n["Confidence"]),
                  ("Ledger row", n["Ledger Row"]), ("Wiki note", n["Wiki Note ID"])]
        for k, v in fields:
            if v:
                lines.append(f"- **{k}:** {v}")
        if n["Open Link"]:
            lines.append(f"- **Open:** [{x.get('native') or x.get('link_note') or 'source page'}](../{n['Open Link']})")
        if x.get("link2"):
            lines.append(f"- **Open {x['link2_label']}:** [Add. 4](../{x['link2']})")
        lines += ["", "## Summary", "", n["Summary"] or "Not stated.", "", "## Source citation", "",
                  n["Source Citation"] or "Not stated."]
        if n["Node Type"] == COMPONENT:
            lines += ["", "## Ledger fields", ""]
            for k in ("tag", "name", "Drawing Sheets", "Spec Sections", "Addenda", "Submittal Req (Y/N)",
                      "Testing/Startup Req (Y/N)", "Notes"):
                lines.append(f"- **{k[0].upper() + k[1:]}:** {x.get(k) or '(blank)'}")
        note = notes.get(n["Wiki Note ID"]) if n["Node Type"] in (SHEET, SPEC) else None
        if note:
            lines += ["", f"## Wiki note {note['id']}", "",
                      f"- **Type:** {note['type']}", f"- **Discipline:** {note['discipline']}",
                      f"- **Revision/Date:** {note['revision']}", f"- **Tags:** {note['tags']}",
                      f"- **Related documents:** {note['related']}", f"- **Where it lives:** {note['where']}",
                      f"- **Project Wiki line:** {note['line']} "
                      f"([Project_Wiki.md](../../../project/01_Project_Wiki/Project_Wiki.md))"]
        lines += ["", "## Neighbours", ""]
        groups = defaultdict(list)
        for d, e in nb[n["Node ID"]]:
            other = e["To"] if d == "out" else e["From"]
            phrase = (OUT_PHRASE if d == "out" else IN_PHRASE)[e["Edge Type"]]
            groups[phrase].append((other, e))
        if not groups:
            lines.append("None.")
        for phrase in sorted(groups, key=lambda p: list(OUT_PHRASE.values()).index(p) if p in OUT_PHRASE.values()
                             else 10 + list(IN_PHRASE.values()).index(p)):
            lines += [f"### {phrase}", ""]
            for other, e in sorted(groups[phrase], key=lambda t: nat_key(t[0])):
                tail = f" — {e['Label']}" if e["Label"] else ""
                lines.append(f"- [[{names[other]}]]{tail} ({e['Confidence']})")
            lines.append("")
        write_text(vdir / f"{names[n['Node ID']]}.md", "\n".join(lines).rstrip("\n"))
    return names


def write_graph_json(g, out):
    nodes = []
    for n in node_order(g):
        lvl = n["Confidence"]
        d = {"id": n["Node ID"], "label": n["Label"], "norm_label": n["Label"].casefold(),
             "node_type": n["Node Type"], "file_type": "concept" if n["Node Type"] in (COMPONENT, BID, AREA)
             else "document", "lane": n["Lane"], "area": n["Area/Building"], "discipline": n["Discipline"],
             "summary": n["Summary"], "bid_item": n["Bid Item"], "status": n["Status"], "ledger_level": lvl,
             "confidence": GRAPHIFY.get(lvl, ("AMBIGUOUS", 0.2))[0], "citation": n["Source Citation"],
             "open_link": n["Open Link"], "ledger_line": int(n["Ledger Row"]) if n["Ledger Row"] else None,
             "wiki_note_id": n["Wiki Note ID"],
             "source_file": rel(LEDGER) if n["Node Type"] == COMPONENT else "",
             "source_location": f"L{n['Ledger Row']}" if n["Ledger Row"] else ""}
        nodes.append(d)
    links = []
    for e in edge_order(g):
        lvl = e["Confidence"]
        conf, score = GRAPHIFY.get(lvl, ("AMBIGUOUS", 0.2))
        frm = g.nodes[e["From"]]
        links.append({"source": e["From"], "target": e["To"], "relation": e["Edge Type"].replace(" ", "_"),
                      "value": e["Label"], "citation": e["Source Citation"], "confidence": conf,
                      "confidence_score": score, "link_level": lvl,
                      "ledger_line": int(frm["Ledger Row"]) if frm["Ledger Row"] else None,
                      "source_file": rel(LEDGER) if frm["Ledger Row"] else rel(WIKI_LINKS)
                      if e["Edge Type"] == RELATED else "",
                      "source_location": f"L{frm['Ledger Row']}" if frm["Ledger Row"] else ""})
    doc = {"directed": True, "multigraph": False, "graph": {}, "nodes": nodes, "links": links, "hyperedges": []}
    write_text(out / "graph.json", json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True))


def write_spot_check(g, sheets, out):
    header = next(csv.reader(io.StringIO(read_text(SPOT_SCHEMA))))
    ids = sorted(g.nodes, key=nat_key)
    picks = random.Random(SPOT_SEED).sample(ids, SPOT_COUNT)
    rows = []
    for i, nid in enumerate(picks, 1):
        n = g.nodes[nid]
        x = n["_extra"]
        t = n["Node Type"]
        if t == COMPONENT:
            first = (x.get("sheets") or [None])[0]
            what = (f"Open {first} (Open Link) and confirm {x['tag']} — {x['name']} is shown as cited"
                    if first else f"No sheet cited; confirm the cited source shows {x['tag']} — {x['name']}")
            method = sheets[first].get("Read Method", "") if first else "Text (spec)"
            tag, name = x["tag"], x["name"]
        elif t == SHEET:
            what = (f"Open Link lands on {x.get('native', 'the cited page')} and the title block reads "
                    f"{x['key']}; Summary matches the sheet")
            method, tag, name = x.get("read_method", ""), nid, n["Label"]
        elif t in (SPEC, PARA):
            what = f"Open Link lands on the cited main spec page and the page carries {n['Label'].split(' · ')[0]}"
            method, tag, name = "Text", nid, n["Label"]
        elif t == ADDENDUM:
            what = f"Open Link lands on the Add. 4 page that carries '{n['Label'][9:]}'"
            method, tag, name = "Text", nid, n["Label"]
        elif t == BID:
            what = f"Open Link lands on the bid form page that lists {n['Label']}"
            method, tag, name = "Text", nid, n["Label"]
        else:
            what = f"The Ledger rows listed carry Area/Building '{n['Label']}'"
            method, tag, name = "Ledger", nid, n["Label"]
        rows.append({"Pick No.": str(i), "Ledger Row": n["Ledger Row"], "Tag": tag, "Name": name,
                     "What to Check": what, "Source Citation": n["Source Citation"],
                     "Confidence Tag": n["Confidence"], "Read Method": method, "Human Result": "",
                     "Checked By": "", "Date": "", "Note": f"Node ID: {nid}; Open Link: {n['Open Link']}"})
    write_text(out / "Spot_Check.csv", csv_text(header, rows))
    return picks


def write_findings(fx, g, out):
    lines = ["# Findings — Ledger gaps hit by the graph build", "",
             f"Built {BUILD_DATE} by `build/build_graph.py`. Every gap is logged here; the Ledger and the index files "
             "are not changed. Tags: Unresolved = a gap or conflict, with the need stated; Inferred = a possible "
             "match a person should confirm; Verified = read as written in the named file.", "",
             "## Summary", "", "| Finding | Count |", "|---|---|"]
    order = sorted(fx.sections)
    for s in order:
        lines.append(f"| {s} | {fx.count(s)} |")
    for s in order:
        rows = sorted(set(fx.sections[s]), key=lambda r: [nat_key(c) for c in r])
        lines += ["", f"## {s} ({len(rows)})", ""]
        if s in fx.notes:
            lines += [fx.notes[s], ""]
        lines += ["| " + " | ".join(fx.headers[s]) + " |", "|" + "---|" * len(fx.headers[s])]
        for r in rows:
            lines.append("| " + " | ".join(c.replace("|", "\\|").replace("\n", " ") for c in r) + " |")
    write_text(out / "Findings.md", "\n".join(lines))


def d3_source(out):
    """d3.min.js 7.9.0: from the npm tarball (sha512-checked), else from an existing Project_Graph.html."""
    try:
        with urllib.request.urlopen(D3_TARBALL, timeout=30) as resp:
            tgz = resp.read()
        got = "sha512-" + base64.b64encode(hashlib.sha512(tgz).digest()).decode()
        if got != D3_TARBALL_SHA512:
            fail("d3 tarball checksum differs from the pinned sha512")
        js = tarfile.open(fileobj=io.BytesIO(tgz)).extractfile("package/dist/d3.min.js").read().decode("utf-8")
        source = "npm registry tarball"
    except (OSError, ValueError) as err:
        page = next((p for p in (out / "Project_Graph.html", OUT_DEFAULT / "Project_Graph.html") if p.exists()), None)
        if page is None:
            fail(f"d3 download failed ({err}) and no earlier Project_Graph.html to reuse")
        text = page.read_bytes().decode("utf-8")
        a, b = text.find(D3_BEGIN), text.find(D3_END)
        if a < 0 or b < 0:
            fail("d3 download failed and the earlier Project_Graph.html has no d3 block")
        js = text[a + len(D3_BEGIN) + 1:b - 1]
        source = "the d3 block of the earlier Project_Graph.html"
    if sha256_bytes(js.encode("utf-8")) != D3_MIN_SHA256:
        fail(f"d3.min.js from {source} differs from the pinned sha256")
    if "</script" in js.lower():
        fail("d3.min.js contains '</script'; it can't be inlined as is")
    return js


def lane_key(text):
    found = lanes_of(text)
    return found[0] if found else "No lane"


def write_viewer(g, notes, out, d3js):
    sys.path.insert(0, str(HERE))
    from viewer_template import TEMPLATE, LICENSE
    nodes, index = [], {}
    for i, n in enumerate(node_order(g)):
        index[n["Node ID"]] = i
        x = n["_extra"]
        d = {"id": n["Node ID"], "label": n["Label"], "type": n["Node Type"], "lane": n["Lane"],
             "lanes": lanes_of(n["Lane"]) or ["No lane"], "area": n["Area/Building"], "disc": n["Discipline"],
             "summary": n["Summary"], "bid": n["Bid Item"], "status": n["Status"], "conf": n["Confidence"],
             "cite": n["Source Citation"], "link": n["Open Link"], "row": n["Ledger Row"], "wiki": n["Wiki Note ID"]}
        if x.get("link2"):
            d["link2"], d["link2Label"] = x["link2"], x["link2_label"]
        if x.get("native"):
            d["native"] = x["native"]
        if x.get("link_note"):
            d["linkNote"] = x["link_note"]
        if n["Node Type"] == COMPONENT:
            d["ledger"] = {k: x[k] for k in ("ledger_id", "tag", "name", "Drawing Sheets", "Spec Sections", "Addenda",
                                             "Submittal Req (Y/N)", "Testing/Startup Req (Y/N)", "Notes")}
        if n["Node Type"] in (SHEET, SPEC) and n["Wiki Note ID"] in notes:
            nt = notes[n["Wiki Note ID"]]
            d["note"] = {k: nt[k] for k in ("id", "type", "discipline", "revision", "summary", "tags", "related",
                                             "where", "line")}
        nodes.append(d)
    edges = [{"s": index[e["From"]], "t": index[e["To"]], "type": e["Edge Type"], "label": e["Label"],
              "cite": e["Source Citation"], "conf": e["Confidence"]} for e in edge_order(g)]
    counts = Counter(n["Node Type"] for n in g.nodes.values())
    data = {"nodes": nodes, "edges": edges, "nodeTypes": list(NODE_TYPES), "edgeTypes": list(EDGE_TYPES),
            "lanes": list(LANES) + ["No lane"], "buildDate": BUILD_DATE,
            "counts": {t: counts[t] for t in NODE_TYPES}, "outPhrase": OUT_PHRASE, "inPhrase": IN_PHRASE,
            "areas": sorted({n["Label"] for n in g.nodes.values() if n["Node Type"] == AREA}, key=nat_key)}
    blob = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")
    html = (TEMPLATE.replace("__D3_LICENSE__", LICENSE)
            .replace("__D3__", f"{D3_BEGIN}\n{d3js}\n{D3_END}")
            .replace("__DATA__", blob))
    write_text(out / "Project_Graph.html", html)


def write_readme(g, fx, out, picks):
    counts = Counter(n["Node Type"] for n in g.nodes.values())
    ecounts = Counter(e["Edge Type"] for e in g.edges.values())
    inputs = "\n".join(f"| `{rel(p)}` | {sha256_bytes(read_text(p).encode('utf-8'))[:16]} |" for p in INPUTS)
    lines = [
        "# derived/graph — Project Wiki graph built from the Ledger", "",
        f"Build date: {BUILD_DATE}. Owner: Graph lane. Built by `build/build_graph.py` with no LLM calls; the "
        "library PDFs are not read. The graph is a map, not a source: cite the Ledger row, the Wiki note or the "
        "document page, never the graph.", "",
        "**Superseded:** the 2026-09-30 extraction graph in `testbeds/eastsound/graph/graphify-out/` (1,386 nodes, "
        "7,284 edges, 85 communities) and its 2026-10-01 rebuild (1,636 nodes) are superseded by this build. "
        "They stay in place, unchanged, as history.", "",
        "## Files", "",
        "| File | What it holds |", "|---|---|",
        "| `Project_Graph.html` | The viewer. One self-contained file with D3 7.9.0 inlined; open it in a browser "
        "with the network off. Color = lane, shape = node type, size = edge count, dashed outline = Unresolved. |",
        "| `nodes.csv` | One row per node (columns in the order below) |",
        "| `edges.csv` | One row per edge: From, To, Edge Type, Label, Source Citation, Confidence |",
        "| `Findings.md` | Every Ledger gap the build hit, logged and not fixed |",
        "| `vault/` | One Markdown note per node, named by its Label, with [[wikilinks]] to every neighbour (opens as an Obsidian vault) |",
        "| `graph.json` | The same graph in the field names of `graph/graphify-out/graph.json` |",
        "| `Spot_Check.csv` | 20 nodes picked with seed 20261002, in `index/Spot_Check_Schema.csv` columns; Human Result is blank for a person to fill. Only a person marks Verified-Visual. |",
        "| `Test_Report.md` | Results of `build/test_graph.py` |",
        "| `build/` | `build_graph.py`, `viewer_template.py`, `test_graph.py` |", "",
        "## Counts", "", "| Node type | Count |", "|---|---|"]
    lines += [f"| {t} | {counts[t]} |" for t in NODE_TYPES]
    lines += [f"| **Total** | **{sum(counts.values())}** |", "", "| Edge type | Count |", "|---|---|"]
    lines += [f"| {t} | {ecounts[t]} |" for t in EDGE_TYPES]
    lines += [f"| **Total** | **{sum(ecounts.values())}** |", "",
              f"Findings: {len(fx.sections)} kinds, {sum(fx.count(s) for s in fx.sections)} rows (`Findings.md`).", "",
              "## Edge map", "",
              "| Ledger column or source | Edge | From → To | Label |", "|---|---|---|---|",
              "| `Drawing Sheets` | shown on | Component → Sheet | the anchor in brackets (KN 16, Det. 3, Add. 4 p.7) |",
              "| `Spec Sections` | specified by | Component → Spec section | the anchor in brackets, if any |",
              "| `Source Citation` (¶ cites) | specified by | Component → Spec paragraph | the main spec page cited, if any |",
              "| `Addenda` | modified by | Component → Addendum item | the Ledger text, less \"— Add. 4 governs\" |",
              "| `Bid Item` | paid under | Component → Bid item | the Ledger text |",
              "| `Area/Building` | located in | Component → Area/Building | the Ledger text, when it adds to the area name |",
              "| `Wiki Note(s)` | described by | Component → Sheet, Spec section or Addendum item | only where no shown-on, specified-by or modified-by edge joins the pair; otherwise that edge's Label ends \"also in Wiki note\" (decision 2A) |",
              "| Wiki note Related documents (`derived/wiki/Wiki_Links.csv`) | related to | Sheet → Sheet or Spec section | \"listed in both notes\" when each note lists the other |",
              "| Paragraph number | part of | Spec paragraph → Spec section | — |", "",
              "- One edge per citation. A pair cited twice keeps one edge and its Label starts \"N citations\".",
              "- Every edge carries the Confidence of the Ledger row it came from, made weaker by any tag word in "
              "the cell (e.g. \"1 (Inferred per 04)\"). Related-to edges carry the Wiki link's Confidence, the "
              "stronger of the two notes when both list each other.",
              "- Never invented: a value that doesn't match 01–04 or the Wiki makes no edge and goes to Findings.",
              "- Not yet: \"I/O point\" edges (E7.4 → BL-1, OUT 0) come in a later pass from the OCR lane's Tag_Hits.",
              "", "## Node rules", "",
              "| Node type | One per | ID | Label | Open Link |", "|---|---|---|---|---|",
              "| Component | Ledger row (447) | Ledger ID + Tag, e.g. `L-0256 BL-1` (permanent IDs from `derived/reconciliation/Ledger_ID_Map.csv`) | Tag · name; untagged PROPOSED rows: name · first sheet (no tag) | the first cited sheet, else the first cited spec section |",
              "| Sheet | 01 rev2 row (96 + C1.6A) | `Sheet E7.4` | sheet · Wiki note title | native part and page from `library/Plan_Set_Parts.md`; C1.6A: Add. 4 p.8. Add. 4 reissues also carry the reissue page |",
              "| Spec section | 02 section the Ledger cites | `Spec 26 80 00` | section · 02 title (the body governs, so 26 80 00 reads Control System) | main spec start page from 02 |",
              "| Spec paragraph | ¶ cited in a Ledger Source Citation | `Spec 26 80 00 ¶3.09 C` | section ¶paragraph · title | the cited main spec page, else the section start |",
              "| Addendum item | 03 Addendum 4 item-map row | `Add. 4 Clarification 4` | Add. 4 · item as written in 03 | Add. 4 page from 03 |",
              "| Bid item | 04 bid item or equipment alternate | `Bid Item 6` | Bid Item 6 · description | bid form page in the main spec |",
              "| Area/Building | name in the Ledger column | `Area Blower Building` | the name | — |", "",
              "Open Links are relative to this folder (`../../library/<file>#page=N`), so they work from any clone.", "",
              "## Decisions recorded (Carl, 2026-10-02, Step 0)", "",
              "Carl answered \"OK, all A (Recommended)\" to the five Step 0 options:", "",
              "1. A — build from `Project_Ledger.csv` (447 rows), keyed on the permanent Ledger ID.",
              "2. A — draw a described-by edge only where it adds a link; elsewhere mark the existing edge \"also in Wiki note\".",
              "3. A — paragraph nodes from the Ledger Source Citation, joined to their section by part of.",
              "4. A — also append PROGRESS_LOG.md and ISSUES_LOG.md entries; the build script lives in `build/`.",
              "5. A — sheet Status from 01 rev2.", "",
              "## Rebuild", "",
              "From the repo root, with any Python 3.10+ (standard library only):", "",
              "```", "python testbeds/eastsound/derived/graph/build/build_graph.py",
              "python testbeds/eastsound/derived/graph/build/test_graph.py", "```", "",
              "On Windows use `py -3`. The build sets PYTHONHASHSEED=0 itself. Two builds of the same inputs give "
              "byte-identical files. D3 comes from the npm tarball (sha512 pinned) or, offline, from the D3 block "
              "of the existing `Project_Graph.html` (sha256 pinned). D3 is © 2010-2023 Mike Bostock, ISC licence "
              "(the licence text is in the viewer).", "",
              f"Spot check picks (seed {SPOT_SEED}): {', '.join(picks)}.", "",
              "## Inputs", "", "| File | SHA-256 (first 16) |", "|---|---|", inputs]
    write_text(out / "README.md", "\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="output folder (default: derived/graph)")
    args = ap.parse_args(argv)
    out = Path(args.out).resolve()
    g, fx, notes, ledger, sheets, specs = build(out)
    d3js = d3_source(out)
    out.mkdir(parents=True, exist_ok=True)
    nodes = node_order(g)
    write_text(out / "nodes.csv", csv_text(NODE_HEADER, nodes))
    write_text(out / "edges.csv", csv_text(EDGE_HEADER, edge_order(g)))
    write_findings(fx, g, out)
    write_viewer(g, notes, out, d3js)
    write_vault(g, notes, out)
    write_graph_json(g, out)
    picks = write_spot_check(g, sheets, out)
    write_readme(g, fx, out, picks)
    counts = Counter(n["Node Type"] for n in nodes)
    print("nodes " + ", ".join(f"{t} {counts[t]}" for t in NODE_TYPES) + f"; total {len(nodes)}")
    ec = Counter(e["Edge Type"] for e in g.edges.values())
    print("edges " + ", ".join(f"{t} {ec[t]}" for t in EDGE_TYPES) + f"; total {len(g.edges)}")
    print(f"findings {sum(fx.count(s) for s in fx.sections)} rows in {len(fx.sections)} kinds")


if __name__ == "__main__":
    main()
