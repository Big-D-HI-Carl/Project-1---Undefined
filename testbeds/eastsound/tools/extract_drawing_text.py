#!/usr/bin/env python3
"""Read every word, tag and quantity off the Eastsound native plan set (Prompt 7, OCR lane).

Inputs (read-only):
  testbeds/eastsound/library/          the three native plan-set parts and addendum-no4-eswd.pdf
  testbeds/eastsound/library/Plan_Set_Parts.md            set page -> part file and page
  testbeds/eastsound/index/01_Sheet_Index_rev1.md         sheet, title, cited file, Add. 4 status
  testbeds/eastsound/derived/bluebeam-ocr/                Bluebeam OCR copies (bluebeam-ocr block)
  testbeds/eastsound/project/02_Project_Ledger/Project_Ledger.csv

Outputs: testbeds/eastsound/derived/ocr/ only (see README.md there).

No LLM calls. Every list is sorted, boxes are rounded to 0.01 pt, JSON keys are sorted,
line endings are LF and there are no timestamps, so two clean runs give identical bytes.

Run from the repo root:
  PYTHONHASHSEED=0 OMP_THREAD_LIMIT=1 python testbeds/eastsound/tools/extract_drawing_text.py --stage all --jobs 4
"""

import os
import sys

# Tesseract must run single-threaded for repeatable output, and the hash seed is pinned
# so nothing can depend on set or dict ordering. Re-exec once if the caller didn't set them.
if os.environ.get("PYTHONHASHSEED") != "0" or os.environ.get("OMP_THREAD_LIMIT") != "1":
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["OMP_THREAD_LIMIT"] = "1"
    os.execv(sys.executable, [sys.executable] + sys.argv)

import argparse
import csv
import difflib
import hashlib
import json
import math
import random
import re
import subprocess
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image

SCHEMA_VERSION = "1.0"

REPO = Path(__file__).resolve().parents[3]   # this file: testbeds/eastsound/tools/
TB = REPO / "testbeds" / "eastsound"
SCRIPT_REL = Path(__file__).resolve().relative_to(REPO).as_posix()
LIB = TB / "library"
PARTS_NOTE = LIB / "Plan_Set_Parts.md"
ADD4_FILE = LIB / "addendum-no4-eswd.pdf"
BB_DIR = TB / "derived" / "bluebeam-ocr"
SHEET_INDEX = TB / "index" / "01_Sheet_Index_rev1.md"
LEDGER = TB / "project" / "02_Project_Ledger" / "Project_Ledger.csv"
CROSSWALK = TB / "index" / "Plan_Set_Crosswalk.csv"      # cited_as (plans_N copy) per set page
MANIFEST = TB / "index" / "Library_Manifest.csv"         # SHA-256 of every native library file
OUT_DEFAULT = TB / "derived" / "ocr"

# Bluebeam OCR copies: set pages covered by each file (derived/bluebeam-ocr/README.md, Parts table).
BB_PARTS = [
    ("Pages from eswd-wwtp-upgrade-ph1-11x17-plans - OCR - Part 1.pdf", 1, 48),
    ("Pages from eswd-wwtp-upgrade-ph1-11x17-plans - OCR - Part 2.pdf", 49, 96),
]
ADD4_PAGES = range(4, 11)  # Add. 4 reissue pages pp.4-10 (01 page-level log)

DPI = 400
OEM = 1
PSM = 3
CONF_FLAG = 60          # a flag, not a filter
SUB_PT = 1.0            # text-layer words under 1 pt in both directions are dropped
OVERLAP = 0.5           # intersection / smaller box area that counts as "the same spot"
TB_RADIUS = 300.0       # title-block lines must sit within this many pt of the SHEET label
BOILERPLATE_PAGES = 20  # a title-block line on this many pages is template text, not a title

TEXT_FLAGS = (pymupdf.TEXT_PRESERVE_LIGATURES | pymupdf.TEXT_PRESERVE_WHITESPACE
              | pymupdf.TEXT_MEDIABOX_CLIP)
VISIBLE_CHAR = 16 | 32  # MuPDF char flags: filled | stroked. Neither = render mode 3.

SHEET_RE = re.compile(r"^[A-Z]{1,2}\d{1,2}\.\d{1,2}[A-Z]?$")
INT_RE = re.compile(r"^\d{1,3}$")
MONTHS = "JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC"
DATE_RE = re.compile(rf"\b(?:(?:{MONTHS})[A-Z]*\.?\s+\d{{1,2}},?\s+\d{{4}}|\d{{1,2}}[-/]\d{{1,2}}[-/]\d{{2,4}})\b")
PAGE_OF_RE = re.compile(r"\b(\d{1,3}|XX)\s*[O0]F\s*(\d{1,3})\b")
TB_LABELS = ("DATE", "SCALE", "SHEET", "PAGE", "JOB", "NUMBER", "CHECKED", "DESIGNED", "DRAWN")
STRIP_PSM = 11          # sparse-text mode for the title-strip pass
STRIP_DPIS = (200, 300) # title-block text is 10-15 pt; at 400 dpi it is too tall for Tesseract
STRIP_MARGIN = 60.0     # pt kept on the plan side of the title-block label that anchors the strip
OCR_SHEET_FIX = {"$": "S", "5": "S"}  # OCR confusables for a sheet number's discipline letter


# ---------------------------------------------------------------- small helpers

def rel(path):
    return Path(path).resolve().relative_to(REPO).as_posix()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def r2(v):
    """Round to 0.01 and normalise -0.0."""
    v = round(float(v), 2)
    return 0.0 if v == 0 else v


def box(rect):
    return [r2(rect.x0), r2(rect.y0), r2(rect.x1), r2(rect.y1)]


def area(b):
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def overlap_ratio(a, b):
    """Intersection area over the smaller box's area."""
    ix = min(a[2], b[2]) - max(a[0], b[0])
    iy = min(a[3], b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    small = min(area(a), area(b))
    return (ix * iy) / small if small > 0 else 0.0


def edge_dist(a, b):
    """Edge-to-edge distance between two boxes (0 if they touch or overlap)."""
    dx = max(0.0, max(a[0], b[0]) - min(a[2], b[2]))
    dy = max(0.0, max(a[1], b[1]) - min(a[3], b[3]))
    return math.hypot(dx, dy)


def center(b):
    return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)


def norm_word(t):
    return re.sub(r"[^A-Z0-9#.\-/]", "", t.upper())


def norm_line(t):
    t = t.upper().replace("–", "-").replace("—", "-")
    t = re.sub(r"[\"'“”‘’]", "", t)
    t = re.sub(r"\s*-\s*", "-", t)
    return re.sub(r"\s+", " ", t).strip()


def title_match(read, title_01):
    """01 marks titles it had only from the G0.1 cover index with "(cover index)"."""
    base = re.sub(r"\s*\(cover index\)\s*$", "", title_01)
    return bool(read) and norm_line(read) == norm_line(base)


def word_sort_key(w):
    return (w["bbox"][1], w["bbox"][0], w["bbox"][3], w["bbox"][2], w["text"], w["method"],
            w.get("pass", ""), w.get("line", ""))


class Grid:
    """Bucket boxes by 50-pt cells so overlap searches stay fast on 2,000-word pages."""

    def __init__(self, items, cell=50.0):
        self.cell = cell
        self.items = items
        self.cells = defaultdict(list)
        for i, it in enumerate(items):
            for key in self._keys(it["bbox"]):
                self.cells[key].append(i)

    def _keys(self, b):
        c = self.cell
        for gx in range(int(b[0] // c), int(b[2] // c) + 1):
            for gy in range(int(b[1] // c), int(b[3] // c) + 1):
                yield (gx, gy)

    def near(self, b):
        seen = set()
        for key in self._keys(b):
            for i in self.cells.get(key, ()):
                if i not in seen:
                    seen.add(i)
        return [self.items[i] for i in sorted(seen)]


# ---------------------------------------------------------------- inputs

def md_tables(path):
    """Every pipe table in a markdown file, as (header, rows-as-dicts)."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    tables = []
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith("|") and re.match(r"^\|\s*:?-{3,}", lines[i + 1]):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                rows.append(dict(zip(header, cells)))
                j += 1
            tables.append((header, rows))
            i = j
        else:
            i += 1
    return tables


def load_parts():
    """Set page -> (native file, file page), from the Parts table in Plan_Set_Parts.md."""
    text = PARTS_NOTE.read_text(encoding="utf-8")
    names = dict(re.findall(r"\*\*(Part \d)\*\* = `([^`]+)`", text))
    out = {}
    for header, rows in md_tables(PARTS_NOTE):
        if header[:3] != ["Part", "Pages", "Set pages"]:
            continue
        for row in rows:
            lo, hi = [int(x) for x in re.split(r"[–-]", row["Set pages"])]
            f = LIB / names[row["Part"]]
            for sp in range(lo, hi + 1):
                out[sp] = (f, sp - lo + 1)
    if sorted(out) != list(range(1, 97)):
        raise SystemExit("Plan_Set_Parts.md does not map set pages 1-96")
    return out


def load_sheet_index():
    """Base set pages and Add. 4 reissue pages as 01 lists them."""
    base, add4, addendum_only = {}, {}, {}
    for header, rows in md_tables(SHEET_INDEX):
        if header[:3] == ["Set p.", "Sheet", "Title (title block)"]:
            for r in rows:
                sp = int(r["Set p."])
                m = re.search(r"Add\. 4 p\.(\d+) governs", r["Addendum 4"])
                base[sp] = {
                    "sheet": r["Sheet"], "title": r["Title (title block)"],
                    "discipline": r["Discipline"], "lane": r["Lane"],
                    "cited_file": r["File"], "cited_page": r["PDF p."],
                    "status": r["Status"], "addendum_4": r["Addendum 4"],
                    "governed_by_add4_page": int(m.group(1)) if m else None,
                }
        elif header[:2] == ["Sheet", "Title (title block)"]:
            for r in rows:
                addendum_only[r["Sheet"]] = r
        elif header[:3] == ["File", "PDF p.", "Sheet"]:
            for r in rows:
                if r["File"] == ADD4_FILE.name:
                    add4[int(r["PDF p."])] = {"sheet": r["Sheet"], "note": r["Note"]}
    if sorted(base) != list(range(1, 97)):
        raise SystemExit("01 sheet table does not list set pages 1-96")
    return base, add4, addendum_only


def load_crosswalk(parts, base):
    """Set page -> cited_as from index/Plan_Set_Crosswalk.csv: the plans_N copy 01 indexes, with
    any duplicate extract listed beside it. Stops if the crosswalk's native part and page, or its
    sheet, disagree with Plan_Set_Parts.md and 01."""
    with open(CROSSWALK, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    by_sp = defaultdict(list)
    for r in rows:
        by_sp[int(r["Set Page"])].append(r)
    out, problems = {}, []
    for sp in range(1, 97):
        rs = by_sp.get(sp, [])
        if not rs:
            problems.append(f"set p.{sp}: no row")
            continue
        f, fp = parts[sp]
        for r in rs:
            if r["Native Part File"] != f.name or r["Native Part Page"] != str(fp):
                problems.append(f"set p.{sp}: native {r['Native Part File']} p.{r['Native Part Page']}, "
                                f"Plan_Set_Parts.md has {f.name} p.{fp}")
            if r["Sheet"] != base[sp]["sheet"]:
                problems.append(f"set p.{sp}: sheet {r['Sheet']}, 01 has {base[sp]['sheet']}")
        primary = [r for r in rs if r["Indexed in 01"] == "Yes"] or rs
        if len(primary) != 1:
            problems.append(f"set p.{sp}: {len(primary)} rows indexed in 01")
            continue
        pr = primary[0]

        def page_of(r):
            return int(r["plans_N PDF Page"]) if r["plans_N PDF Page"].isdigit() else None
        out[sp] = {"file": pr["plans_N File"], "page": page_of(pr), "short_name": pr["plans_N Short Name"],
                   "indexed_in_01": pr["Indexed in 01"],
                   "duplicates": [{"file": r["plans_N File"], "page": page_of(r), "indexed_in_01": r["Indexed in 01"]}
                                  for r in rs if r is not pr],
                   "basis": rel(CROSSWALK)}
    if problems:
        raise SystemExit("Stopped: Plan_Set_Crosswalk.csv disagrees with Plan_Set_Parts.md or 01:\n  "
                         + "\n  ".join(problems))
    return out


def verify_sources():
    """Every native library file this script reads must match its SHA-256 row in
    index/Library_Manifest.csv; stop on a mismatch or a missing row."""
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        manifest = {r["Path"]: r["SHA-256"] for r in csv.DictReader(f)}
    files = sorted({f for f, _ in load_parts().values()} | {ADD4_FILE})
    bad = []
    for f in files:
        want, got = manifest.get(rel(f)), sha256_file(f)
        if want is None:
            bad.append(f"{rel(f)}: no row in Library_Manifest.csv")
        elif want != got:
            bad.append(f"{rel(f)}: SHA-256 {got}, Library_Manifest.csv has {want}")
    if bad:
        raise SystemExit("Stopped: source files do not match index/Library_Manifest.csv:\n  " + "\n  ".join(bad))


def page_tasks(only=None):
    parts = load_parts()
    base, add4, addendum_only = load_sheet_index()
    cited = load_crosswalk(parts, base)
    titles = {v["sheet"]: v for v in base.values()}
    tasks = []
    for sp in range(1, 97):
        f, fp = parts[sp]
        s = base[sp]
        gov = None
        if s["governed_by_add4_page"]:
            n = s["governed_by_add4_page"]
            gov = {"file": rel(ADD4_FILE), "page": n, "page_key": f"add4_p{n:02d}",
                   "basis": f"01 Addendum 4 column: {s['addendum_4']}"}
        bb = None
        for name, lo, hi in BB_PARTS:
            if lo <= sp <= hi:
                bb = (str(BB_DIR / name), sp - lo + 1)
        tasks.append({
            "page_key": f"{sp:03d}", "set_page": sp, "sheet_01": s["sheet"],
            "title_01": s["title"], "discipline_01": s["discipline"],
            "native_file": str(f), "native_page": fp, "bluebeam": bb,
            "cited_as": cited[sp],
            "governed_by": gov, "governs": None,
        })
    for n in ADD4_PAGES:
        a = add4[n]
        sheet = a["sheet"]
        governs, status = None, None
        hit = [sp for sp, s in base.items() if s["governed_by_add4_page"] == n]
        if hit and base[hit[0]]["sheet"] == sheet:
            governs = {"set_page": hit[0], "page_key": f"{hit[0]:03d}",
                       "basis": f"01 Addendum 4 column: {base[hit[0]]['addendum_4']}"}
        else:
            status = ("Unresolved: no base page in the 96-sheet set; 01 lists " + sheet
                      + " as issued by addendum only (base issue cites Addendum 3, not in library)")
        info = titles.get(sheet) or {}
        extra = addendum_only.get(sheet, {})
        tasks.append({
            "page_key": f"add4_p{n:02d}", "set_page": None, "sheet_01": sheet,
            "title_01": info.get("title") or extra.get("Title (title block)", ""),
            "discipline_01": info.get("discipline") or extra.get("Discipline", ""),
            "native_file": str(ADD4_FILE), "native_page": n, "bluebeam": None,
            "cited_as": {"file": ADD4_FILE.name, "page": n, "short_name": "Add. 4", "duplicates": [],
                         "indexed_in_01": "Yes (page-level log)",
                         "basis": rel(SHEET_INDEX) + " page-level log (Plan_Set_Crosswalk.csv covers set pages only)"},
            "governed_by": None, "governs": governs, "governs_status": status,
        })
    if only:
        keep = set(only)
        tasks = [t for t in tasks if t["page_key"] in keep]
    return tasks


# ---------------------------------------------------------------- page extraction (worker)

def pdf_words(page):
    """Text-layer words in displayed coordinates, with render mode, line id, direction, size."""
    M = page.rotation_matrix
    raw = page.get_text("rawdict", flags=TEXT_FLAGS)
    chars = defaultdict(list)   # (block, line) -> [(center, visible, size)]
    line_dir = {}
    for b in raw["blocks"]:
        if b.get("type", 0) != 0:
            continue
        for li, ln in enumerate(b["lines"]):
            line_dir[(b["number"], li)] = ln["dir"]
            for sp in ln["spans"]:
                vis = bool(sp["char_flags"] & VISIBLE_CHAR)
                for ch in sp["chars"]:
                    r = pymupdf.Rect(ch["bbox"])
                    chars[(b["number"], li)].append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2, vis, sp["size"]))
    out = []
    unmatched = 0
    for x0, y0, x1, y1, text, bno, lno, wno in page.get_text("words", flags=TEXT_FLAGS):
        own = [c for c in chars.get((bno, lno), ())
               if x0 - 0.01 <= c[0] <= x1 + 0.01 and y0 - 0.01 <= c[1] <= y1 + 0.01]
        if not own:
            unmatched += 1
        vis = any(c[2] for c in own)
        size = max((c[3] for c in own), default=0.0)
        d = line_dir.get((bno, lno), (1.0, 0.0))
        dv = pymupdf.Point(d) * M - pymupdf.Point(0, 0) * M
        out.append({
            "text": text, "bbox": box(pymupdf.Rect(x0, y0, x1, y1) * M),
            "render_mode": 0 if vis else 3, "line": f"t{bno}.{lno}",
            "dir": [r2(dv.x), r2(dv.y)], "size": r2(size), "word_no": wno,
        })
    return out, unmatched


def tesseract_pass(page, rot, cache_dir, clip=None, psm=PSM, tag=None, dpi=DPI):
    z = dpi / 72.0
    M = pymupdf.Matrix(z, z)
    if rot:
        M = M.prerotate(rot)
    pix = page.get_pixmap(matrix=M, colorspace=pymupdf.csGRAY, alpha=False, clip=clip)
    config = f"--oem {OEM} --psm {psm}"
    data = None
    cache_file = None
    if cache_dir:
        key = hashlib.sha256(pix.samples + f"{pix.width}x{pix.height}|{config}|{tesseract_version()}".encode()).hexdigest()
        cache_file = Path(cache_dir) / f"{key}.json"
        if cache_file.exists():
            data = json.loads(cache_file.read_text(encoding="utf-8"))
    if data is None:
        img = Image.frombytes("L", (pix.width, pix.height), pix.samples)
        data = pytesseract.image_to_data(img, lang="eng", config=config, output_type=pytesseract.Output.DICT)
        if cache_file:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps(data), encoding="utf-8")
    inv = ~M
    dv = pymupdf.Point(1, 0) * inv - pymupdf.Point(0, 0) * inv
    ln = math.hypot(dv.x, dv.y) or 1.0
    direction = [r2(dv.x / ln), r2(dv.y / ln)]
    pass_name = tag or ("rot90" if rot else "upright")
    tag = {"upright": "up", "rot90": "r90"}.get(pass_name, pass_name)
    out = []
    for i, text in enumerate(data["text"]):
        conf = float(data["conf"][i])
        if conf < 0 or not text.strip():
            continue
        x0 = data["left"][i] + pix.x
        y0 = data["top"][i] + pix.y
        r = pymupdf.Rect(x0, y0, x0 + data["width"][i], y0 + data["height"][i]) * inv
        b = box(r)
        out.append({
            "text": text.strip(), "bbox": b, "method": "ocr", "conf": r2(conf),
            "conf_ge_60": conf >= CONF_FLAG, "pass": pass_name,
            "line": f"{tag}{data['block_num'][i]}.{data['par_num'][i]}.{data['line_num'][i]}",
            "word_no": data["word_num"][i], "dir": direction,
            "size": r2(min(b[2] - b[0], b[3] - b[1])),
        })
    return out


def dedupe_passes(upright, rot90):
    """Same spot in both passes: keep the higher confidence (tie: upright)."""
    grid = Grid(upright)
    drop_up = set()
    keep_rot = []
    for w in rot90:
        clash = [u for u in grid.near(w["bbox"]) if overlap_ratio(u["bbox"], w["bbox"]) >= OVERLAP]
        if not clash:
            keep_rot.append(w)
            continue
        best = max(u["conf"] for u in clash)
        if w["conf"] > best:
            keep_rot.append(w)
            for u in clash:
                drop_up.add(id(u))
    kept = [u for u in upright if id(u) not in drop_up] + keep_rot
    return kept, len(upright) + len(rot90) - len(kept)


def strip_pass(page, ocr_words, cache_dir):
    """Rotated sparse-text OCR of the title strip, for pages whose text layer has no title block.

    The strip runs from the title-block label nearest the bottom-right corner to the right
    page edge, full height; it is found per page from the full-page OCR, not from fixed
    coordinates. It is read at each of STRIP_DPIS; the parent keeps, per field, the read with
    the higher confidence.
    """
    W, H = page.rect.width, page.rect.height
    corner = [W, H, W, H]
    labels = [w for w in ocr_words if w["text"].strip(".:") in TB_LABELS
              and edge_dist(w["bbox"], corner) <= TB_RADIUS]
    if labels:
        a = min(labels, key=lambda w: (edge_dist(w["bbox"], corner), w["bbox"]))
        x0 = max(0.0, a["bbox"][0] - STRIP_MARGIN)
        basis = f"anchor {a['text']!r} at {fmt_box(a['bbox'])} ({a['pass']} pass), minus {STRIP_MARGIN:.0f} pt"
    else:
        x0 = W * 0.85
        basis = "no title-block label read within 300 pt of the corner; right 15% of the page"
    clip = pymupdf.Rect(x0, 0, W, H)  # get_pixmap clips in displayed coordinates
    passes = []
    for dpi in STRIP_DPIS:
        words = tesseract_pass(page, 90, cache_dir, clip=clip, psm=STRIP_PSM,
                               tag=f"title-strip-{dpi}", dpi=dpi)
        passes.append({"dpi": dpi, "psm": STRIP_PSM, "rotation": 90,
                       "words": sorted(words, key=word_sort_key)})
    return passes, {"rect": [r2(x0), 0.0, r2(W), r2(H)], "basis": basis}


def extract_page(task):
    """Worker: all words for one page. Title block and tags are added by the parent."""
    t0 = time.time()
    doc = pymupdf.open(task["native_file"])
    page = doc[task["native_page"] - 1]
    rect = page.rect
    all_text, unmatched = pdf_words(page)
    kept_text, dropped = [], []
    for w in all_text:
        b = w["bbox"]
        (dropped if (b[2] - b[0]) < SUB_PT and (b[3] - b[1]) < SUB_PT else kept_text).append(w)
    for w in kept_text:
        w["method"] = "text-layer"
        w["conf"] = None
    upright = tesseract_pass(page, 0, task.get("cache"))
    rot90 = tesseract_pass(page, 90, task.get("cache"))
    ocr, pass_dupes = dedupe_passes(upright, rot90)
    grid = Grid(kept_text)
    merged_ocr, suppressed = [], 0
    for w in ocr:
        if any(overlap_ratio(t["bbox"], w["bbox"]) >= OVERLAP for t in grid.near(w["bbox"])):
            suppressed += 1
        else:
            merged_ocr.append(w)
    ocr_confs = [w["conf"] for w in ocr]

    strip_passes, strip_info = [], None
    if not has_text_title_block(kept_text, rect.width, rect.height):
        strip_passes, strip_info = strip_pass(page, ocr, task.get("cache"))

    bb_block = None
    if task["bluebeam"]:
        bf, bp = task["bluebeam"]
        bdoc = pymupdf.open(bf)
        bpage = bdoc[bp - 1]
        sx = rect.width / bpage.rect.width
        sy = rect.height / bpage.rect.height
        bwords, _ = pdf_words(bpage)
        mode3 = [w for w in bwords if w["render_mode"] == 3]
        big = []
        for w in mode3:
            b = w["bbox"]
            w["bbox"] = [r2(b[0] * sx), r2(b[1] * sy), r2(b[2] * sx), r2(b[3] * sy)]
            if not ((b[2] - b[0]) < SUB_PT and (b[3] - b[1]) < SUB_PT):
                big.append(w)
        ngrid = Grid(all_text)
        kept_bb, matched = [], 0
        for w in big:
            nt = norm_word(w["text"])
            if any(norm_word(t["text"]) == nt and overlap_ratio(t["bbox"], w["bbox"]) >= OVERLAP
                   for t in ngrid.near(w["bbox"])):
                matched += 1
                continue
            kept_bb.append({"text": w["text"], "bbox": w["bbox"], "method": "bluebeam-ocr",
                            "conf": None, "line": "b" + w["line"][1:], "dir": w["dir"],
                            "size": w["size"], "word_no": w["word_no"]})
        bb_block = {
            "source": {"file": rel(bf), "sha256": sha256_file(bf), "page": bp},
            "transform_scale": [r2(sx), r2(sy)],
            "counts": {"mode3_words": len(mode3), "sub1pt_dropped": len(mode3) - len(big),
                       "matched_native": matched, "kept": len(kept_bb)},
            "rule": "render-mode-3 words in the OCR copy, minus words matching a native word "
                    "(same normalised text, overlap >= 0.5 of the smaller box); Inferred",
            "words": sorted(kept_bb, key=word_sort_key),
        }
    return {
        "page_key": task["page_key"],
        "page": {"width": r2(rect.width), "height": r2(rect.height), "rotation": page.rotation,
                 "mediabox": box(page.mediabox)},
        "text_all": all_text,
        "words": sorted(kept_text + merged_ocr, key=word_sort_key),
        "ocr_all": sorted(ocr, key=word_sort_key),
        "counts": {
            "text_layer_words": len(all_text),
            "text_layer_chars": sum(len(w["text"]) for w in all_text),
            "text_layer_words_kept": len(kept_text),
            "mode3_chars_kept": sum(len(w["text"]) for w in kept_text if w["render_mode"] == 3),
            "sub1pt_dropped_words": len(dropped),
            "sub1pt_dropped_chars": sum(len(w["text"]) for w in dropped),
            "text_words_without_chars": unmatched,
            "ocr_upright_words": len(upright), "ocr_rot90_words": len(rot90),
            "ocr_pass_duplicates_dropped": pass_dupes, "ocr_words": len(ocr),
            "ocr_words_ge_60": sum(1 for c in ocr_confs if c >= CONF_FLAG),
            "ocr_suppressed_by_text_layer": suppressed, "ocr_words_merged": len(merged_ocr),
            "ocr_mean_conf": r2(sum(ocr_confs) / len(ocr_confs)) if ocr_confs else None,
        },
        "bluebeam": bb_block,
        "strip_passes": strip_passes,
        "strip_info": strip_info,
        "seconds": time.time() - t0,
    }


# ---------------------------------------------------------------- title block

def along(b, d):
    """Extent of a box projected on direction d."""
    xs = (b[0], b[2])
    ys = (b[1], b[3])
    vals = [x * d[0] + y * d[1] for x in xs for y in ys]
    return min(vals), max(vals)


def make_line(ws, d):
    ws = sorted(ws, key=lambda w: (along(w["bbox"], d)[0], w["bbox"]))
    b = [min(w["bbox"][0] for w in ws), min(w["bbox"][1] for w in ws),
         max(w["bbox"][2] for w in ws), max(w["bbox"][3] for w in ws)]
    return {"text": " ".join(w["text"] for w in ws), "bbox": b, "dir": d,
            "size": max(w["size"] for w in ws), "words": ws, "method": ws[0]["method"],
            "conf": min((w["conf"] for w in ws if w["conf"] is not None), default=None)}


def group_lines(words):
    """Lines as the extractor reported them (PDF line, or Tesseract block.par.line)."""
    lines = defaultdict(list)
    for w in words:
        lines[(w["method"], w.get("pass", ""), w["line"])].append(w)
    return [make_line(lines[k], lines[k][0]["dir"]) for k in sorted(lines)]


def geo_lines(words):
    """Lines rebuilt from position: same direction, same baseline band, small gaps."""
    by_dir = defaultdict(list)
    for w in words:
        by_dir[tuple(w["dir"])].append(w)
    out = []
    for d in sorted(by_dir):
        down = (-d[1], d[0])
        ws = sorted(by_dir[d], key=lambda w: (sum(along(w["bbox"], down)) / 2, along(w["bbox"], d)[0], w["bbox"]))
        rows, cur, cur_p, cur_t = [], [], None, None
        for w in ws:
            p = sum(along(w["bbox"], down)) / 2
            t = max(w["size"], 1.0)
            if cur and abs(p - cur_p) > 0.6 * min(t, cur_t):
                rows.append(cur)
                cur = []
            if not cur:
                cur_p, cur_t = p, t
            cur.append(w)
        if cur:
            rows.append(cur)
        for row in rows:
            row.sort(key=lambda w: (along(w["bbox"], d)[0], w["bbox"]))
            seg = [row[0]]
            for w in row[1:]:
                gap = along(w["bbox"], d)[0] - along(seg[-1]["bbox"], d)[1]
                if gap > 2.5 * max(w["size"], seg[-1]["size"], 1.0):
                    out.append(make_line(seg, list(d)))
                    seg = []
                seg.append(w)
            out.append(make_line(seg, list(d)))
    return out


def sheet_value(w):
    """Sheet number read from a word; OCR reads may carry a $ or 5 for the S discipline letter."""
    raw = re.sub(r"[^A-Z0-9$.]", "", w["text"].upper()).strip(".")
    if SHEET_RE.match(raw):
        return raw, None
    if w["method"] != "text-layer" and raw[:1] in OCR_SHEET_FIX:
        fixed = OCR_SHEET_FIX[raw[0]] + raw[1:]
        if SHEET_RE.match(fixed):
            return fixed, f"OCR read {w['text']!r}; {raw[0]} taken as {OCR_SHEET_FIX[raw[0]]}"
    return None, None


def is_boilerplate(text, boiler):
    """Template text: an exact template line, or (for OCR reads) most of one."""
    n = norm_line(text)
    if n in boiler:
        return True
    c = re.sub(r"[^A-Z0-9]", "", n)
    if len(c) < 6:
        return False
    for b in boiler:
        cb = re.sub(r"[^A-Z0-9]", "", b)
        m = difflib.SequenceMatcher(None, c, cb, autojunk=False).find_longest_match(0, len(c), 0, len(cb))
        if m.size >= 0.8 * len(c):
            return True
    return False


def not_title(text):
    n = norm_line(text)
    if not re.search(r"[A-Z]{3,}", n):
        return True
    if DATE_RE.search(n) or PAGE_OF_RE.search(n) or SHEET_RE.match(n.replace(" ", "")):
        return True
    if re.fullmatch(r"[A-Z]{2,4}", n):          # initials: JGC, BZ, AWL
        return True
    if "=" in n or n in ("AS SHOWN", "NTS", "NONE", "BID SET"):
        return True
    return False


def nearest(items, anchor):
    return min(items, key=lambda it: (edge_dist(it["bbox"], anchor), it["bbox"]))


def sheet_label(words, W, H):
    labels = [w for w in words if norm_word(w["text"]).strip(".:") == "SHEET"]
    return nearest(labels, [W, H, W, H]) if labels else None


def has_text_title_block(words, W, H):
    """True when the text layer holds a SHEET label with a sheet number beside it."""
    label = sheet_label(words, W, H)
    if not label:
        return False
    sheets = [w for w in words if sheet_value(w)[0]]
    return bool(sheets) and edge_dist(nearest(sheets, label["bbox"])["bbox"], label["bbox"]) <= 30


def read_title_block(words, W, H, boiler, rev_words, geometric):
    """Fields found from the SHEET label nearest the displayed bottom-right corner."""
    label = sheet_label(words, W, H)
    if not label:
        return None
    lb = label["bbox"]
    res = {"sheet_label_bbox": lb}
    sheets = [w for w in words if sheet_value(w)[0]]
    if sheets:
        s = nearest(sheets, lb)
        value, note = sheet_value(s)
        res["sheet"] = {"value": value, "raw": s["text"], "bbox": s["bbox"], "method": s["method"],
                        "conf": s["conf"], "dist_to_label": r2(edge_dist(s["bbox"], lb))}
        if note:
            res["sheet"]["note"] = note
    lines = geo_lines(words) if geometric else group_lines(words)
    # Page number: "N OF M" on one line, or N, OF and M as three words along the OF word's direction.
    pl = [ln for ln in lines if PAGE_OF_RE.search(norm_line(ln["text"])) and edge_dist(ln["bbox"], lb) <= TB_RADIUS]
    if pl:
        ln = nearest(pl, lb)
        m = PAGE_OF_RE.search(norm_line(ln["text"]))
        res["page_of"] = {"page": m.group(1), "of": m.group(2), "bbox": ln["bbox"],
                          "method": ln["method"], "conf": ln["conf"]}
    else:
        ofs = [w for w in words if norm_word(w["text"]) in ("OF", "0F") and edge_dist(w["bbox"], lb) <= 60]
        if ofs:
            of = nearest(ofs, lb)
            oc = center(of["bbox"])
            d = of["dir"]
            before, after = [], []
            for w in words:
                if w is of or not (INT_RE.match(w["text"]) or w["text"] == "XX"):
                    continue
                c = center(w["bbox"])
                if math.hypot(c[0] - oc[0], c[1] - oc[1]) > 30:
                    continue
                t = (c[0] - oc[0]) * d[0] + (c[1] - oc[1]) * d[1]
                (before if t < 0 else after).append((abs(t), w["bbox"], w))
            if before and after:
                n, m = min(before, key=lambda x: x[:2])[2], min(after, key=lambda x: x[:2])[2]
                trio = (n, of, m)
                res["page_of"] = {"page": n["text"], "of": m["text"],
                                  "bbox": [min(x["bbox"][0] for x in trio), min(x["bbox"][1] for x in trio),
                                           max(x["bbox"][2] for x in trio), max(x["bbox"][3] for x in trio)],
                                  "method": of["method"],
                                  "conf": min((x["conf"] for x in trio if x["conf"] is not None), default=None)}
    dates = [w for w in words if norm_word(w["text"]).strip(".:") == "DATE" and edge_dist(w["bbox"], lb) <= TB_RADIUS]
    anchor = nearest(dates, lb)["bbox"] if dates else lb
    dl = [ln for ln in lines if DATE_RE.search(norm_line(ln["text"])) and edge_dist(ln["bbox"], lb) <= TB_RADIUS]
    if dl:
        d = nearest(dl, anchor)
        res["date"] = {"value": DATE_RE.search(norm_line(d["text"])).group(0), "bbox": d["bbox"],
                       "method": d["method"], "conf": d["conf"]}
    ld = label["dir"]
    cands = [ln for ln in lines
             if abs(ln["dir"][0] * ld[0] + ln["dir"][1] * ld[1]) >= 0.9
             and edge_dist(ln["bbox"], lb) <= TB_RADIUS
             and not not_title(ln["text"]) and not is_boilerplate(ln["text"], boiler)]
    if cands:
        top = max(cands, key=lambda ln: (ln["size"], len(ln["text"]), [-v for v in ln["bbox"]]))
        # A title can wrap: join same-size parallel lines stacked right against it.
        down = (-ld[1], ld[0])
        group = [top] + [ln for ln in cands if ln is not top and abs(ln["size"] - top["size"]) <= 0.6
                         and edge_dist(ln["bbox"], top["bbox"]) <= 2.0 * max(top["size"], 1.0)]
        group.sort(key=lambda ln: (center(ln["bbox"])[0] * down[0] + center(ln["bbox"])[1] * down[1], ln["bbox"]))
        res["title"] = {"value": " ".join(ln["text"] for ln in group),
                        "bbox": [min(ln["bbox"][0] for ln in group), min(ln["bbox"][1] for ln in group),
                                 max(ln["bbox"][2] for ln in group), max(ln["bbox"][3] for ln in group)],
                        "method": top["method"],
                        "conf": min((ln["conf"] for ln in group if ln["conf"] is not None), default=None)}
    revs = [w for w in rev_words if norm_word(w["text"]).strip(".:") in ("REVISION", "REVISIONS")]
    if revs:
        rv = nearest(revs, lb)
        header = {"BY", "DATE", "NO", "NO.", "DESCRIPTION", "REVISION", "REVISIONS", "REV", "REV."}
        close = [w for w in rev_words if edge_dist(w["bbox"], rv["bbox"]) <= 60]
        near = [ln for ln in geo_lines(close)
                if edge_dist(ln["bbox"], rv["bbox"]) <= 40 and ln["bbox"][1] >= rv["bbox"][1]
                and not all(norm_word(w["text"]).strip(".:|") in header for w in ln["words"])
                and abs(ln["dir"][0] * rv["dir"][0] + ln["dir"][1] * rv["dir"][1]) >= 0.9]
        near.sort(key=lambda ln: (ln["bbox"][1], ln["bbox"][0]))
        res["revision"] = {"label_bbox": rv["bbox"], "label_method": rv["method"],
                           "entries": [{"text": ln["text"], "bbox": ln["bbox"], "method": ln["method"],
                                        "conf": ln["conf"]} for ln in near]}
    else:
        res["revision"] = {"entries": [], "note": "no REVISIONS label read"}
    return res


def learn_boilerplate():
    """Text-layer lines repeated on BOILERPLATE_PAGES or more of the 96 base pages."""
    per_page = defaultdict(set)
    for sp, (f, fp) in load_parts().items():
        page = pymupdf.open(f)[fp - 1]
        words, _ = pdf_words(page)
        for w in words:
            w["method"], w["conf"] = "text-layer", None
        for ln in group_lines(words):
            per_page[norm_line(ln["text"])].add(sp)
    return {t for t, pages in per_page.items() if len(pages) >= BOILERPLATE_PAGES}


def title_blocks(results, tasks):
    """Read every page's title block; template lines are learned across the whole set."""
    boiler = learn_boilerplate()
    out = {}
    for t in tasks:
        r = results[t["page_key"]]
        W, H = r["page"]["width"], r["page"]["height"]
        text_words = [w for w in r["words"] if w["method"] == "text-layer"]
        if r["strip_info"] is None:
            tb = read_title_block(text_words, W, H, boiler, r["words"], geometric=False) or {}
            tb["source"] = "text-layer"
        else:
            reads = [(p["dpi"], read_title_block(p["words"], W, H, boiler, r["words"], geometric=True) or {})
                     for p in r["strip_passes"]]
            tb = {}
            for field in ("sheet", "page_of", "date", "title"):
                got = [(rd[field].get("conf") or 0.0, -i, dpi, rd[field])
                       for i, (dpi, rd) in enumerate(reads) if field in rd]
                if got:
                    best = max(got, key=lambda g: g[:2])
                    tb[field] = dict(best[3], strip_dpi=best[2])
            for dpi, rd in reads:
                if "revision" in rd:
                    tb["revision"] = rd["revision"]
                    break
            if reads and "sheet_label_bbox" in reads[0][1]:
                tb["sheet_label_bbox"] = reads[0][1]["sheet_label_bbox"]
            tb["source"] = ("ocr title-strip pass (no SHEET label and sheet number in the text layer; "
                            "any confidence accepted)")
            tb["strip"] = dict(r["strip_info"], passes=r["strip_passes"])
        out[t["page_key"]] = tb
    return out, sorted(boiler)


# ---------------------------------------------------------------- versions

_TV = None


def tesseract_version():
    global _TV
    if _TV is None:
        v = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
        _TV = [ln.strip() for ln in (v.stdout + v.stderr).splitlines()
               if ln.strip().startswith(("tesseract ", "leptonica-", "Found "))]
    return _TV


def traineddata():
    v = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True)
    m = re.search(r'"([^"]+)"', v.stdout + v.stderr)
    path = Path(os.environ.get("TESSDATA_PREFIX") or (m.group(1) if m else "")) / "eng.traineddata"
    return sha256_file(path) if path.exists() else "not found"


def extractor_info():
    import PIL
    return {
        "script": SCRIPT_REL,
        "script_sha256": sha256_file(Path(__file__)),
        "schema_version": SCHEMA_VERSION,
        "python": sys.version.split()[0],
        "pymupdf": pymupdf.pymupdf_version, "mupdf": pymupdf.mupdf_version,
        "pytesseract": pytesseract.__version__, "pillow": PIL.__version__,
        "tesseract": tesseract_version(), "eng_traineddata_sha256": traineddata(),
        "dpi": DPI, "oem": OEM, "psm": PSM, "passes": ["upright", "rot90"],
        "conf_flag": CONF_FLAG, "sub_pt_drop": SUB_PT, "overlap_rule": OVERLAP,
        "env": {"OMP_THREAD_LIMIT": os.environ.get("OMP_THREAD_LIMIT"),
                "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED")},
    }


# ---------------------------------------------------------------- writers

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False))
        f.write("\n")


def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def page_file_name(t):
    return f"{t['page_key']}_{t['sheet_01']}.json"


def fmt_box(b):
    return "" if not b else f"{b[0]:.2f},{b[1]:.2f},{b[2]:.2f},{b[3]:.2f}"


SHEET_MAP_HEADER = [
    "Page Key", "Set Page", "01 Sheet", "Title-Block Sheet Read", "Match (Y/N)", "01 Title",
    "Title Read", "Title Match (Y/N)", "Page Read (N OF M)", "Split-Part File and Page",
    "Native File", "Native Page", "Governed By", "Governs", "Text-Layer Characters",
    "Mode-3 Characters", "Sub-1pt Words Dropped", "OCR Words", "OCR Words Merged",
    "Mean Confidence", "Bluebeam Words", "Title-Block Source",
]


def stage_pages(out, jobs, only, cache):
    tasks = page_tasks(only)
    for t in tasks:
        t["cache"] = cache
    start = time.time()
    results = {}
    if jobs > 1:
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            for r in ex.map(extract_page, tasks):
                results[r["page_key"]] = r
                print(f"  {r['page_key']}: {r['counts']['text_layer_words']} text, "
                      f"{r['counts']['ocr_words']} ocr, {r['seconds']:.0f}s", file=sys.stderr)
    else:
        for t in tasks:
            r = extract_page(t)
            results[r["page_key"]] = r
            print(f"  {r['page_key']}: {r['counts']['text_layer_words']} text, "
                  f"{r['counts']['ocr_words']} ocr, {r['seconds']:.0f}s", file=sys.stderr)
    tbs, boiler = title_blocks(results, tasks)
    info = extractor_info()
    pages_dir = out / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    if not only:
        for old in pages_dir.glob("*.json"):
            old.unlink()
    rows = []
    for t in tasks:
        r = results[t["page_key"]]
        tb = tbs[t["page_key"]]
        f = Path(t["native_file"])
        doc = {
            "schema_version": SCHEMA_VERSION,
            "page_key": t["page_key"], "set_page": t["set_page"],
            "sheet_01": t["sheet_01"], "title_01": t["title_01"], "discipline_01": t["discipline_01"],
            "source": {"file": rel(f), "sha256": sha256_file(f), "page": t["native_page"],
                       "sha256_checked_against": rel(MANIFEST)},
            "cited_as": t["cited_as"], "governed_by": t["governed_by"], "governs": t["governs"],
            "page": r["page"], "counts": r["counts"], "title_block": tb,
            "words": r["words"], "bluebeam": r["bluebeam"],
            "extractor": info,
        }
        if t["page_key"].startswith("add4"):
            doc["governs_status"] = t.get("governs_status")
            doc["bluebeam"] = {"note": "no Bluebeam OCR copy covers Addendum 4", "words": []}
        write_json(pages_dir / page_file_name(t), doc)
        sheet_read = tb.get("sheet", {}).get("value", "")
        title_read = tb.get("title", {}).get("value", "")
        po = tb.get("page_of")
        c = r["counts"]
        gov = t["governed_by"]
        rows.append([
            t["page_key"], t["set_page"] if t["set_page"] else "", t["sheet_01"], sheet_read,
            "Y" if sheet_read == t["sheet_01"] else "N", t["title_01"], title_read,
            "Y" if title_match(title_read, t["title_01"]) else "N",
            f"{po['page']} OF {po['of']}" if po else "",
            f"{t['cited_as']['file']} p.{t['cited_as']['page']}" if t["cited_as"]["page"] else t["cited_as"]["file"],
            f.name, t["native_page"],
            f"{Path(gov['file']).name} p.{gov['page']}" if gov else "",
            (f"set p.{t['governs']['set_page']}" if t["governs"] else (t.get("governs_status") or "")),
            c["text_layer_chars"], c["mode3_chars_kept"], c["sub1pt_dropped_words"],
            c["ocr_words"], c["ocr_words_merged"],
            "" if c["ocr_mean_conf"] is None else f"{c['ocr_mean_conf']:.2f}",
            (r["bluebeam"] or {}).get("counts", {}).get("kept", "") if r["bluebeam"] else "",
            tb.get("source", ""),
        ])
    if not only:
        write_csv(out / "Sheet_Map.csv", SHEET_MAP_HEADER, rows)
    wall = time.time() - start
    print(f"pages stage: {len(tasks)} pages in {wall:.0f} s wall, jobs={jobs}", file=sys.stderr)
    print(f"template lines learned: {len(boiler)}", file=sys.stderr)
    return rows


# ---------------------------------------------------------------- Step 2: forms, tags, quantities

TAG_LEVEL_COL = "Verified/Verified-Visual/Inferred/Unresolved"
LEVELS = ["Verified", "Verified-Visual", "Inferred", "Unresolved"]
CONFUSE = str.maketrans({"I": "1", "O": "0", "S": "5", "B": "8", "H": "#"})
# Gate A rules (owner, 2026-09-30); see README.md.
NEAR_TAG_PT = 24.0      # nearest-tag search distance, edge to edge
SHORT_FORM_LEN = 3      # forms this short count only on the row's cited sheets
QUALIFIER_RE = re.compile(r"\(E\)|\bEXIST")  # an "(E)" row needs this on the hit's line
SHEET_TOKEN_RE = re.compile(r"^([A-Z]{1,2}\d{1,2}\.\d{1,2}[A-Z]?)\s*(?:\(([^)]*)\))?\s*(.*)$")
LEGENDS = {  # Pipe ID and Buried Valve ID rows match a legend line that starts with the ID number
    "Pipe ID": ("PIPE IDENTIFICATION LEGEND", ("C1.3",)),
    "Buried Valve ID": ("BURIED VALVE IDENTIFICATION LEGEND", ("C1.4",)),
}
DISCIPLINE_LANE = {"C": "Civil & Site", "E": "Electrical & Controls", "S": "Structural & Building",
                   "A": "Structural & Building", "G": "Civil & Site"}
KEYED_HEAD_RE = re.compile(r"^\W*KEY(?:ED)?\s?NOTES?\W*$")  # the heading alone, not a sentence naming it
MARKER_RE = re.compile(r"^(?:=|\(?(\d{1,2})[.),]{0,2})$")
STRAY_RE = re.compile(r"^[-_–—|.,:;=~]+$")
UNMATCHED_SHAPES = [
    ("letters-dash-number", re.compile(r"(?<![A-Z0-9#-])[A-Z]{1,5}-\d{1,4}[A-Z]?(?![A-Z0-9-])")),
    ("letters-hash-number", re.compile(r"(?<![A-Z0-9#-])[A-Z]{2,5}#\d{1,4}(?![A-Z0-9])")),
    ("structure-number", re.compile(r"(?<![A-Z0-9#-])(?:SSMH|SDMH|SDCB|MH|CB)\s?\d{2,5}(?![A-Z0-9])")),
    ("letters-number", re.compile(r"(?<![A-Z0-9#.-])[A-Z]{1,4}\d{1,3}[A-Z]?(?![A-Z0-9.#-])")),
]
PIPE_WORDS = {"DI", "DIP", "HDPE", "PVC", "C900", "SS", "CPVC", "CI", "RCP", "CMP", "STEEL", "CU", "COPPER",
              "SDR", "FM", "GRAV", "GRAV.", "SD", "W", "2W", "WATER", "SEWER", "DRAIN", "INFLUENT", "EFFLUENT",
              "AIR", "VENT", "SLUDGE", "WAS", "PIPE", "LINE", "MAIN", "CONDUIT", "C", "RGS", "EMT", "GATE",
              "PLUG", "VALVE", "BALL", "CHECK", "ROOF", "STORM", "SANITARY", "FORCE", "SEPTIC", "SCH", "SCH.",
              "DIA", "DIA.", "CULVERT", "HYDRANT", "SUPERNATANT"}
# A foot value right before one of these is a dimension (6' CHAIN LINK), not a quantity.
DIM_MATERIAL = {"CHAIN", "LINK", "FENCE", "CONC", "CONC.", "CONCRETE", "ASPHALT", "HMA", "GRAVEL", "ROCK",
                "BLOCK", "CMU", "WOOD", "TIMBER", "ALUM", "ALUMINUM", "BRICK", "STEEL", "GALV", "GALV.",
                "SS", "PVC", "DI", "DIP", "HDPE", "RCP", "CMP", "FRP", "CEDAR", "VINYL"}
NUM_BOUND = r"(?<![A-Z0-9.,/])"
Q_NUM = NUM_BOUND + r"(?P<v>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
Q_PATTERNS = [
    ("length", "LF", re.compile(Q_NUM + r"\s?(?:L\.F\.|LF|LIN\.?\s?FT\.?)(?![A-Z])")),
    ("area", "SF", re.compile(Q_NUM + r"\s?(?:S\.F\.|SF|SQ\.?\s?FT\.?)(?![A-Z])")),
    ("area", "SY", re.compile(Q_NUM + r"\s?(?:S\.Y\.|SY|SQ\.?\s?YDS?\.?)(?![A-Z])")),
    ("volume", "CY", re.compile(Q_NUM + r"\s?(?:C\.Y\.|CY|CU\.?\s?YDS?\.?)(?![A-Z])")),
    ("count", "EA", re.compile(Q_NUM + r"\s?(?:EA\.?|EACH)(?![A-Z])")),
    ("lump sum", "LS", re.compile(Q_NUM + r"\s?(?:L\.S\.|LS)(?![A-Z])")),
    ("weight", "TON", re.compile(Q_NUM + r"\s?TONS?(?![A-Z])")),
    ("volume", "GAL", re.compile(Q_NUM + r"\s?(?:GAL\.?|GALLONS?)(?![A-Z])")),
    ("length", "LF", re.compile(r"(?<![A-Z0-9])L\s?=\s?(?P<v>\d+(?:\.\d+)?)\s?(?:'|FT\.?|LF)?")),
    ("length", "FT", re.compile(Q_NUM + r"\s?(?:-\s?)?(?:FT\.?|FEET)(?![A-Z])")),
    ("length", "FT", re.compile(Q_NUM + r"'(?![-\d\"'])")),
    ("size", "IN", re.compile(NUM_BOUND + r"(?P<v>\d{1,2}(?:\.\d+)?(?:\s\d/\d)?|\d/\d)\s?(?:\"|''|-?IN\.?|-?INCH(?:ES)?)(?![A-Z0-9])"
                              r"(?P<rest>(?:\s?\(?[A-Z0-9./]+\)?){0,4})")),
    ("count", "EA", re.compile(r"(?<![A-Z0-9.,/-])\(?(?P<v>\d{1,3})\)?\s(?P<noun>[A-Z]{3,}S)(?![A-Z])")),
    ("slope", "%", re.compile(Q_NUM + r"\s?%")),
    ("slope", "FT/FT", re.compile(r"(?<![A-Z0-9])S\s?=\s?(?P<v>0?\.\d+)(?!\d)")),
    ("slope", "H:V", re.compile(r"(?<![0-9.])(?P<v>\d+(?:\.\d+)?\s?H\s?:\s?\d+(?:\.\d+)?\s?V)(?![A-Z])")),
    ("elevation", "FT", re.compile(r"(?<![A-Z0-9])(?P<k>RIM|SUMP|I\.E\.|IE|INV(?:ERT)?\.?|ELEV\.?|EL\.?|FG|FF|FFE|TOC|TOW|BOW|TOG|GRATE)"
                                   r"\s?(?:\((?:IN|OUT|[NSEW]{1,2})\)\s?|(?:IN|OUT)\s)?(?:(?:EL|ELEV)\.?\s?)?[=:]?\s?"
                                   r"(?P<v>\d{1,4}\.\d{1,2})(?!\d)")),
]
LF_AT_RE = re.compile(r"(?:LF|L\.F\.)\s?@\s?$")
NAME_QTY_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s?(LF|FT|ft|SF|SY|CY|EA|GAL|gal|gallons|TONS?)\b")
QTY_UNIT_FORMS = {"LF": r"(?:LF|L\.F\.)", "FT": r"(?:'|FT\.?|FEET|-FT)", "SF": r"(?:SF|S\.F\.)",
                  "SY": r"(?:SY|S\.Y\.)", "CY": r"(?:CY|C\.Y\.)", "EA": r"(?:EA\.?|EACH)",
                  "GAL": r"(?:GAL\.?|GALLONS?)", "TON": r"TONS?"}
NOUN_STOP = {
    "INCH", "INCHES", "EXISTING", "WITH", "SYSTEM", "TEMPORARY", "REMOVE", "REMOVED", "REMOVAL", "LOCAL",
    "EQUAL", "CONTRACTOR", "CONSTRUCTION", "TYPICAL", "STATED", "QUANTITY", "LOCATION", "LOCATIONS",
    "ABOUT", "BELOW", "ABOVE", "CLEAR", "THEN", "DURING", "ABANDON", "RELOCATE", "PROVIDE", "PROVIDED",
    "INSTALL", "INSTALLED", "UNDER", "FROM", "INTO", "ONTO", "COMPONENTS", "COMPONENT", "NORTH", "SOUTH",
    "EAST", "WEST", "BASE", "ADDENDUM", "NOTE", "NOTES", "SHEET", "SHEETS", "DETAIL", "DETAILS", "EACH",
    "BOTH", "THAT", "THIS", "THESE", "THOSE", "WHEN", "WHERE", "WILL", "SHALL", "ALSO", "ONLY", "PLAN",
    "PLANS", "ITEM", "ITEMS", "WORK", "AREA", "AREAS", "SITE", "WWTP", "ESWD", "PHASE", "REQUIRED",
    "OTHER", "SAME", "ROWS", "PROPOSED", "PLUS", "PART", "PARTS", "TYPE", "SIZE", "SIZES", "MIN.", "MINIMUM",
    "MAXIMUM", "EQUIPMENT", "PROJECT", "OWNER", "ENGINEER", "SPECIFICATIONS", "SPEC", "SECTION",
}
# Nouns too common on these sheets to anchor a row on their own (owner, Gate A: "not PIPE, VALVE,
# CONCRETE, FENCE, WALL, LINE, and the like"). Compared after plural folding.
GENERIC_NOUNS = {
    "PIPE", "PIPING", "VALVE", "CONCRETE", "FENCE", "WALL", "LINE", "DRAIN", "DRAINAGE", "WATER", "PUMP",
    "TANK", "SLAB", "BASIN", "STATION", "BUILDING", "FLOW", "METER", "TRAIN", "POWER", "CONTROL", "PANEL",
    "STEEL", "STAINLESS", "FLOOR", "INLET", "OUTLET", "STRUCTURE", "SUPPORT", "CONDUIT", "CABLE", "WIRE",
    "WIRING", "DOOR", "ROOF", "PLATE", "FRAME", "COVER", "MOTOR", "LIGHT", "LIGHTING", "CIRCUIT", "SWITCH",
    "STORM", "SEWER", "SANITARY", "TRENCH", "GRADE", "GRADING", "PAVEMENT", "ASPHALT", "GRAVEL", "CURB",
    "EXCAVATION", "BACKFILL", "SURFACE", "BLOCK", "FOOTING", "FOUNDATION", "ELECTRICAL", "MECHANICAL",
    "INFLUENT", "EFFLUENT", "SLUDGE", "TREATMENT", "PLANT", "CELL", "UNIT", "UNITS", "SERVICE", "CONNECTION",
    "BOTTOM", "HIGH", "LEVEL", "OPENING", "PRECAST", "INSTALLATION", "EXTERIOR", "INTERIOR", "MAIN",
}


def weakest(levels):
    levels = [lv for lv in levels if lv]
    return max(levels, key=LEVELS.index) if levels else "Unresolved"


def method_level(method):
    return "Verified" if method == "text-layer" else "Inferred"


def word_dir(w):
    """Reading direction for grouping: OCR passes also read text at the other angle, so use box shape."""
    if w["method"] == "ocr" and len(w["text"]) >= 2:
        b = w["bbox"]
        return [1.0, 0.0] if (b[2] - b[0]) >= (b[3] - b[1]) else [0.0, -1.0]
    return w["dir"]


def family(tag):
    if tag.startswith("PROPOSED"):
        return "PROPOSED"
    for fam in LEGENDS:
        if re.fullmatch(fam + r" \d+", tag):
            return fam
    return "printed"


def norm_form(t):
    t = t.upper().replace("–", "-").replace("—", "-")
    t = re.sub(r"[\"'“”‘’]", "", t)
    t = re.sub(r"\s*([#-])\s*", r"\1", t)
    return re.sub(r"\s+", " ", t).strip()


def printed_forms(tag):
    """Search forms for a printed tag: trailing (...) and [...] stripped ("(E)" kept as a
    qualifier), "|" aliases split, ranges expanded. Returns (forms, qualified, is_range)."""
    t = tag
    qualified = False
    while True:
        m = re.search(r"\s*([\(\[][^\)\]]*[\)\]])\s*$", t)
        if not m:
            break
        if m.group(1).upper() == "(E)":
            qualified = True
        t = t[:m.start()].strip()
    forms, is_range = [], False
    for alt in t.split("|"):
        alt = alt.strip()
        m = re.fullmatch(r"([A-Z]+)(\d+)\s*[–-]\s*(?:\1)?(\d+)", alt)
        if m:
            is_range = True
            forms += [f"{m.group(1)}{n}" for n in range(int(m.group(2)), int(m.group(3)) + 1)]
        else:
            forms.append(alt)
    out = []
    for f in forms:
        f = norm_form(f)
        if f and f not in out:
            out.append(f)
    return out, qualified, is_range


def split_sheets(field):
    """Drawing Sheets -> [(sheet, [anchors], raw token)]; the leading token is the sheet."""
    toks = []
    for raw in [x.strip() for x in field.split(";") if x.strip()]:
        m = SHEET_TOKEN_RE.match(raw)
        if m:
            anchors = [a.strip() for a in (m.group(2) or "", m.group(3) or "") if a.strip()]
            toks.append((m.group(1), anchors, raw))
        else:
            toks.append(("", [raw], raw))
    return toks


def stem(u):
    return u[:-1] if len(u) > 4 and u.endswith("S") and not u.endswith("SS") else u


def key_nouns(name):
    """Words of 4+ letters from the Ledger Name, generic words dropped, plurals folded."""
    out = []
    for t in re.findall(r"[A-Za-z]{4,}", name.replace("-", " ")):
        u = t.upper()
        if u in NOUN_STOP or u.endswith("ED"):   # -ED words are participles, not nouns
            continue
        s = stem(u)
        if s not in out:
            out.append(s)
    return out


def name_quantities(name):
    out = []
    for v, u in NAME_QTY_RE.findall(name):
        u = u.upper()
        u = {"GALLONS": "GAL", "TONS": "TON"}.get(u, u)
        if (v, u) not in out:
            out.append((v, u))
    return out


def load_ledger():
    with open(LEDGER, encoding="utf-8-sig", newline="") as f:
        return [(i, r) for i, r in enumerate(csv.DictReader(f), start=2)]  # line 1 is the header


def build_forms():
    rows = []
    form_rows = defaultdict(list)
    for i, r in load_ledger():
        fam = family(r["Tag"])
        forms, qualified, is_range = printed_forms(r["Tag"]) if fam == "printed" else ([], False, False)
        for fm in forms:
            form_rows[fm].append(i)
        toks = split_sheets(r["Drawing Sheets"])
        cited = []
        for s, _, _ in toks:
            if s and s not in cited:
                cited.append(s)
        rows.append({"row": i, "tag": r["Tag"], "name": r["Name"], "family": fam, "forms": forms,
                     "qualified": qualified, "range": is_range,
                     "lanes": [x.strip() for x in r["Lane"].split(";") if x.strip()],
                     "sheets_field": r["Drawing Sheets"], "tokens": toks, "cited": cited,
                     "nouns": [n for n in key_nouns(r["Name"]) if n not in GENERIC_NOUNS],
                     "qty": name_quantities(r["Name"]),
                     "level": r[TAG_LEVEL_COL]})
    by_row = {r["row"]: r for r in rows}
    for r in rows:
        reasons = []
        if not r["tokens"]:
            reasons.append("no sheet cited")
        elif not r["cited"]:
            reasons.append("no sheet number cited: " + "; ".join(t[2] for t in r["tokens"]))
        if r["family"] == "printed":
            r["searchable"] = "Y"
            r["search"] = [fm + (" [with (E) or EXIST on the same line]" if r["qualified"] else "")
                           for fm in r["forms"]]
            reasons.insert(0, "printed tag; exact form in the text layer, OCR and Bluebeam; "
                              "1/I 0/O 5/S 8/B #/H swaps in OCR and Bluebeam marked fuzzy")
            if any(len(fm) <= SHORT_FORM_LEN for fm in r["forms"]):
                reasons.append("short form (3 characters or fewer): counts only on this row's cited sheets; "
                               "elsewhere listed as off-citation, short form")
            shared = sorted({j for fm in r["forms"] for j in form_rows[fm] if j != r["row"]})
            if shared:
                reasons.append("form shared with row(s) " + ", ".join(map(str, shared))
                               + ": a hit goes to the row whose Lane matches the sheet's lane in 01, "
                                 "otherwise it is marked ambiguous")
                rng = [j for j in shared if by_row[j]["range"]]
                ind = [j for j in shared if not by_row[j]["range"]]
                if r["range"] and ind:
                    reasons.append("range row: individual row(s) " + ", ".join(map(str, ind))
                                   + " take the hit first; this row gets the rollup")
                elif not r["range"] and rng:
                    reasons.append("individual row: takes the hit before range row(s) "
                                   + ", ".join(map(str, rng)))
            if r["qualified"]:
                reasons.append("(E) qualifier: counts only with (E) or EXIST on the hit's line; "
                               "otherwise the hit goes to the unqualified row, or is not counted")
            if any(" " in fm for fm in r["forms"]):
                reasons.append("internal space matches 0 or 1 space")
        elif r["family"] in LEGENDS:
            head, sheets = LEGENDS[r["family"]]
            n = r["tag"].rsplit(" ", 1)[1]
            r["searchable"] = "Y"
            r["search"] = [f"legend line starting '{n}' under '{head}' on {', '.join(sheets)} (base and Add. 4 reissue)"]
            reasons.insert(0, "ID number is not printed as a tag; matched in the legend")
        else:
            r["searchable"] = "N"
            anchors = [f"{t[0]} ({a})" for t in r["tokens"] if t[0] for a in (t[1] or ["sheet only"])]
            if r["qty"]:
                match = "match: quantity " + " or ".join(f"{v} {u}" for v, u in r["qty"]) + " (value and unit)"
            elif r["nouns"]:
                match = "match: noun " + ", ".join(r["nouns"])
            else:
                match = "match: none possible (no quantity and no specific noun in the Ledger Name)"
            r["search"] = anchors + [match]
            reasons.insert(0, "PROPOSED tag is not printed; each Drawing Sheets anchor is checked for the row's "
                              "quantity (value and unit) when the Ledger Name has one, otherwise for a "
                              "specific noun from the Name (generic nouns excluded); Verified in the text "
                              "layer, Inferred by OCR or Bluebeam, Unresolved if not found or not matching; "
                              "a sheet-only anchor is Verified only for the quantity in the text layer, and a "
                              "noun on the sheet is Inferred (on sheet, location not pinned)")
        r["reason"] = "; ".join(reasons)
    return rows


FORMS_HEADER = ["Ledger Row", "Tag", "Search Forms", "Family", "Searchable (Y/N)", "Reason"]


def stage_forms(out):
    rows = build_forms()
    write_csv(out / "Tag_Search_Forms.csv", FORMS_HEADER,
              [[r["row"], r["tag"], " | ".join(r["search"]), r["family"], r["searchable"], r["reason"]] for r in rows])
    return rows


# ---- matching helpers

def norm_token(t, keep_quotes=False):
    t = t.upper().replace("–", "-").replace("—", "-")
    if keep_quotes:
        t = t.replace("“", '"').replace("”", '"').replace("″", '"')
        return t.replace("‘", "'").replace("’", "'").replace("′", "'")
    return re.sub(r"[\"'“”‘’′″]", "", t)


def line_string(words, keep_quotes=False):
    """Normalised line text plus the word index behind each character."""
    s, owner = "", []
    for i, w in enumerate(words):
        t = norm_token(w["text"], keep_quotes)
        if not t:
            continue
        if s and not (s.endswith(("#", "-")) or t.startswith(("#", "-"))):
            s += " "
            owner.append(None)
        s += t
        owner.extend([i] * len(t))
    return s, owner


def span_words(words, owner, a, b):
    idx = sorted({i for i in owner[a:b] if i is not None})
    return [words[i] for i in idx]


def union_box(ws):
    return [min(w["bbox"][0] for w in ws), min(w["bbox"][1] for w in ws),
            max(w["bbox"][2] for w in ws), max(w["bbox"][3] for w in ws)]


def min_conf(ws):
    return min((w["conf"] for w in ws if w["conf"] is not None), default=None)


METHOD_RANK = {"text-layer": 0, "ocr": 1, "bluebeam-ocr": 2}


def weakest_method(ws):
    return max((w["method"] for w in ws), key=lambda m: METHOD_RANK[m])


def page_lines(pg):
    """Search lines: PDF lines for the text layer and Bluebeam; for OCR, lines rebuilt by position,
    because the upright and rotated passes each hold part of a line."""
    words = list(pg["words"]) + list((pg.get("bluebeam") or {}).get("words", []))
    lines = defaultdict(list)
    ocr = []
    for w in words:
        if w["method"] == "ocr":
            ocr.append(dict(w, dir=word_dir(w)))
        else:
            lines[(w["method"], w["line"])].append(w)
    out = []
    for k in sorted(lines):
        ws = sorted(lines[k], key=lambda w: (w.get("word_no", 0), w["bbox"]))
        out.append({"method": k[0], "words": ws})
    for ln in geo_lines(ocr):
        out.append({"method": "ocr", "words": ln["words"]})
    return out


def compile_forms(rows):
    by_form = defaultdict(list)
    for r in rows:
        if r["family"] == "printed":
            for fm in r["forms"]:
                by_form[fm].append(r["row"])
    comp = []
    for fm in sorted(by_form):
        parts = fm.split(" ")
        strict = re.compile(r"(?<![A-Z0-9])" + r"\s?".join(re.escape(p) for p in parts) + r"(?![A-Z0-9])")
        cparts = [p.translate(CONFUSE) for p in parts]
        canon = re.compile(r"(?<![A-Z0-9#])" + r"\s?".join(re.escape(p) for p in cparts) + r"(?![A-Z0-9#])")
        comp.append((fm, strict, canon, by_form[fm]))
    return comp


def page_ref(pg):
    return {"page_key": pg["page_key"], "set_page": pg["set_page"], "sheet": pg["sheet_01"]}


def find_tags(pg, comp):
    hits = []
    for ln in page_lines(pg):
        s, owner = line_string(ln["words"])
        if not s:
            continue
        cs = s.translate(CONFUSE)
        for fm, strict, canon, rows in comp:
            spans = [(m.start(), m.end()) for m in strict.finditer(s)]
            found = [(a, b, False) for a, b in spans]
            if ln["method"] != "text-layer":
                for m in canon.finditer(cs):
                    if not any(m.start() < b and a < m.end() for a, b in spans):
                        found.append((m.start(), m.end(), True))
            for a, b, fuzzy in found:
                ws = span_words(ln["words"], owner, a, b)
                if not ws:
                    continue
                hits.append(dict(page_ref(pg), tag_text=" ".join(w["text"] for w in ws), form=fm,
                                 candidates=list(rows), bbox=union_box(ws), method=ln["method"],
                                 conf=min_conf(ws), fuzzy=fuzzy, kind="tag", line_norm=s))
    return dedupe_hits(hits)


def dedupe_hits(hits):
    """One hit per spot, form and method (Bluebeam and PDF lines can repeat a word)."""
    hits.sort(key=lambda h: (h["form"], h["method"], h["fuzzy"], h["bbox"], h["tag_text"]))
    out = []
    for h in hits:
        if any(o["form"] == h["form"] and o["method"] == h["method"]
               and overlap_ratio(o["bbox"], h["bbox"]) >= OVERLAP for o in out[-20:]):
            continue
        out.append(h)
    return out


def assign_hit(h, by_row, sheet_lane):
    """Gate A rules, in order: (E) qualifier; short forms only on cited sheets; individual rows
    before range rows (ranges get the rollup); Lane against the sheet's lane; else ambiguous."""
    cands = list(h["candidates"])
    qual = [r for r in cands if by_row[r]["qualified"]]
    if qual:
        if QUALIFIER_RE.search(h["line_norm"]):
            cands = qual
        else:
            cands = [r for r in cands if not by_row[r]["qualified"]]
            if not cands:
                return "qualifier (E) not on line", [], [], qual
    if len(h["form"]) <= SHORT_FORM_LEN:
        cited = [r for r in cands if h["sheet"] in by_row[r]["cited"]]
        if not cited:
            return "off-citation, short form", [], [], cands
        cands = cited
    indiv = [r for r in cands if not by_row[r]["range"]]
    ranges = [r for r in cands if by_row[r]["range"]]
    primary, rollup = (indiv, ranges) if indiv else (ranges, [])

    def by_lane(rs):
        for lane in (sheet_lane.get(h["sheet"], ""), DISCIPLINE_LANE.get(h["sheet"][:1], "")):
            m = [r for r in rs if lane and lane in by_row[r]["lanes"]]
            if m:
                return m
        return rs
    if len(primary) > 1:
        primary = by_lane(primary)
    if len(rollup) > 1:
        rollup = by_lane(rollup)
    if len(primary) == 1:
        return "assigned", primary, rollup, cands
    return "ambiguous", [], [], primary


def geo_page_words(pg):
    """All words once: text layer over OCR over Bluebeam where they share a spot."""
    tiers = [[w for w in pg["words"] if w["method"] == "text-layer"],
             [w for w in pg["words"] if w["method"] == "ocr"],
             list((pg.get("bluebeam") or {}).get("words", []))]
    kept = []
    for tier in tiers:
        grid = Grid(kept) if kept else None
        add = []
        for w in tier:
            if grid and any(overlap_ratio(k["bbox"], w["bbox"]) >= OVERLAP for k in grid.near(w["bbox"])):
                continue
            add.append(w)
        kept += add
    return [dict(w, dir=word_dir(w)) for w in kept]


def find_legends(pg, rows):
    """Pipe ID / Buried Valve ID legend entries: the ID number in the column under the heading,
    and the words to its right within that number's row band."""
    hits = []
    words = geo_page_words(pg)
    lines = geo_lines(words)
    tb = pg.get("title_block") or {}
    right = (tb.get("sheet_label_bbox") or [pg["page"]["width"]])[0] - 10
    for fam, (head, sheets) in LEGENDS.items():
        if pg["sheet_01"] not in sheets:
            continue
        heads = [ln for ln in lines if head in norm_line(ln["text"])]
        if not heads:
            continue
        hd = min(heads, key=lambda ln: (METHOD_RANK[ln["method"]], ln["bbox"]))
        hb = hd["bbox"]
        nums = sorted((w for w in words if re.fullmatch(r"\d{1,2}", w["text"])
                       and hb[0] - 5 <= w["bbox"][0] <= hb[0] + 25 and w["bbox"][1] > hb[3] - 1),
                      key=lambda w: (w["bbox"][1], w["bbox"][0]))
        by_id = {r["tag"].rsplit(" ", 1)[1]: r for r in rows if r["family"] == fam}
        for k, w in enumerate(nums):
            r = by_id.get(w["text"])
            if not r:
                continue
            top = (nums[k - 1]["bbox"][3] + w["bbox"][1]) / 2 if k else w["bbox"][1] - 8
            bot = (w["bbox"][3] + nums[k + 1]["bbox"][1]) / 2 if k + 1 < len(nums) else w["bbox"][3] + 8
            desc = [x for x in words if w["bbox"][2] < x["bbox"][0] < min(w["bbox"][2] + 300, right)
                    and top <= center(x["bbox"])[1] <= bot and not STRAY_RE.match(x["text"])]
            if not desc:
                continue
            dl = sorted(geo_lines(desc), key=lambda ln: (center(ln["bbox"])[1], ln["bbox"][0]))
            ws = [w] + desc
            hits.append(dict(page_ref(pg), tag_text=f"{w['text']}: " + " ".join(ln["text"] for ln in dl),
                             form=f"{fam} {w['text']}", candidates=[r["row"]], bbox=union_box(ws),
                             method=weakest_method(ws), conf=min_conf(ws), fuzzy=False, kind="legend",
                             line_norm="", assignment="assigned", rows=[r["row"]], rollup=[],
                             lines=[ln["words"] for ln in dl]))
    return dedupe_hits(hits)


def keyed_notes(pg):
    """Keyed-note legend entries. Numbers sit in symbols OCR does not always read, so entries are
    split by line spacing (a gap over 1.4 x the block's 25th-percentile spacing) or a leading
    marker. An entry takes the number read in its marker when that number is 1 or 2 past the
    previous entry's; otherwise the previous number + 1 ("by order", Inferred). If the block's
    entry count differs from the highest marker read, its by-order numbers are Unresolved."""
    words = geo_page_words(pg)
    lines = geo_lines(words)
    heads = [ln for ln in lines if KEYED_HEAD_RE.match(norm_line(ln["text"])) and ln["dir"] == [1.0, 0.0]]
    blocks = []
    used = []
    for hd in sorted(heads, key=lambda ln: (METHOD_RANK[ln["method"]], ln["bbox"])):
        hb = hd["bbox"]
        if any(overlap_ratio(hb, u) >= OVERLAP for u in used):
            continue
        used.append(hb)
        col = [ln for ln in lines if ln["dir"] == [1.0, 0.0] and hb[0] - 30 <= ln["bbox"][0] <= hb[0] + 20
               and center(ln["bbox"])[1] > hb[3] and ln is not hd]
        col.sort(key=lambda ln: (ln["bbox"][1], ln["bbox"][0]))
        block, last = [], hb[3]
        for ln in col:
            if ln["bbox"][1] - last > 25:
                break
            block.append(ln)
            last = max(last, ln["bbox"][3])
        if not block:
            continue

        # Rows: lines at the same height (a line split by a gap or by method). A row's height is
        # the median word centre, markers left out (a symbol box can be taller than the text).
        def row_y(lns):
            ws = [w for ln in lns for w in ln["words"]]
            txt = [w for w in ws if not MARKER_RE.match(w["text"])] or ws
            cs = sorted(center(w["bbox"])[1] for w in txt)
            return cs[len(cs) // 2]
        text_rows, stray = [], []
        for ln in sorted(block, key=lambda ln: (row_y([ln]), ln["bbox"][0])):
            if all(STRAY_RE.match(w["text"]) or SHEET_RE.match(norm_word(w["text"]).rstrip("."))
                   for w in ln["words"]):
                stray.append(ln)        # detail bubbles and symbol fragments inside the notes
                continue
            if text_rows and abs(row_y([ln]) - row_y(text_rows[-1])) <= 2.0:
                text_rows[-1].append(ln)
            else:
                text_rows.append([ln])
        ys = [row_y(r) for r in text_rows]
        gaps = [b - a for a, b in zip(ys, ys[1:])]
        p25 = sorted(gaps)[len(gaps) // 4] if gaps else 0
        # Entries start in the marker column (the leftmost row start); indented sub-items and
        # wrapped lines do not start an entry however they are spaced.
        firsts = [min(r, key=lambda ln: ln["bbox"][0])["words"][0] for r in text_rows]
        left = min((f["bbox"][0] for f in firsts), default=0.0)
        entries = []
        for k, r in enumerate(text_rows):
            first = firsts[k]
            in_col = first["bbox"][0] <= left + 6
            marker = MARKER_RE.match(first["text"]) if in_col else None
            start = k == 0 or (in_col and ((gaps and gaps[k - 1] > 1.4 * p25) or bool(marker)))
            if start:
                rd = marker.group(1) if marker and marker.group(1) else None
                entries.append({"lines": [], "top": row_y(r), "read_number": rd,
                                "marker_method": first["method"] if rd else None})
            entries[-1]["lines"].extend(r)
        for ln in stray:  # a stray row joins the entry it sits in
            y = row_y([ln])
            host = [e for e in entries if e["top"] - 3 <= y]
            if host:
                host[-1]["lines"].append(ln)
        reads = [int(e["read_number"]) for e in entries if e["read_number"]]
        highest = max(reads) if reads else None
        count_ok = highest is not None and highest == len(entries)
        out = []
        n = 0
        for e in entries:
            # a read marker is trusted only when it runs on from the previous entry (misreads
            # such as "(1)" for 11 would otherwise restart the count)
            rd = int(e["read_number"]) if e["read_number"] else None
            if rd is not None and n < rd <= n + 2:
                n, basis, level = rd, "read", method_level(e["marker_method"])
            else:
                n, basis = n + 1, "by order"
                level = "Inferred" if count_ok or highest is None else "Unresolved"
            ls = sorted(e["lines"], key=lambda ln: (ln["bbox"][1], ln["bbox"][0]))
            ws = [w for ln in ls for w in ln["words"]]
            out.append({"number": n, "read_number": e["read_number"], "basis": basis, "number_level": level,
                        "bbox": union_box(ws), "text": " / ".join(ln["text"] for ln in ls),
                        "method": weakest_method(ws), "lines": [ln["words"] for ln in ls]})
        if highest is None:
            check = "no marker read; by-order numbers cannot be checked against a marker"
        elif count_ok:
            check = f"entry count {len(entries)} matches the highest marker read"
        else:
            check = (f"entry count {len(entries)} does not match the highest marker read ({highest}); "
                     "by-order numbers Unresolved")
        blocks.append({"heading": hd["text"], "heading_bbox": hb, "heading_method": hd["method"],
                       "bbox": union_box([w for ln in block for w in ln["words"]] + hd["words"]),
                       "entries": out, "line_spacing_p25": r2(p25), "highest_marker_read": highest,
                       "count_check": check})
    return blocks


def isolated_numbers(pg, exclude):
    """Single-word lines holding a 1-2 digit number: keyed-note and detail callout candidates."""
    words = geo_page_words(pg)
    out = []
    for ln in geo_lines(words):
        if len(ln["words"]) != 1:
            continue
        w = ln["words"][0]
        m = re.fullmatch(r"\(?(\d{1,2})\)?", w["text"])
        if not m or any(overlap_ratio(w["bbox"], b) > 0 for b in exclude):
            continue
        out.append({"n": m.group(1), "bbox": w["bbox"], "method": w["method"], "conf": w["conf"]})
    return out


def detail_refs(pg):
    """n over SHEET (a detail or section bubble): number word just above a sheet-number word."""
    words = geo_page_words(pg)
    sheets = [w for w in words if SHEET_RE.match(norm_word(w["text"]).rstrip("."))]
    nums = [w for w in words if re.fullmatch(r"\d{1,2}", w["text"])]
    out = []
    for s in sheets:
        cands = [n for n in nums if 0 <= s["bbox"][1] - n["bbox"][3] <= 6
                 and n["bbox"][0] < s["bbox"][2] and s["bbox"][0] < n["bbox"][2]]
        if cands:
            n = min(cands, key=lambda n: (s["bbox"][1] - n["bbox"][3], n["bbox"]))
            out.append({"ref": f"{n['text']}/{norm_word(s['text']).rstrip('.')}", "bbox": union_box([n, s]),
                        "method": weakest_method([n, s])})
    return out


def detail_titles(pg):
    """Detail titles: a 1-2 digit word with a SCALE line just to its right. Each detail's region
    runs up from its SCALE line to the title row above it, and across to the next detail number
    on the same row (or the title block); its words are the anchor text for a Det. n citation."""
    words = geo_page_words(pg)
    lines = geo_lines(words)
    scale = [ln for ln in lines if "SCALE" in norm_line(ln["text"])]
    found = []
    for w in words:
        if not re.fullmatch(r"\d{1,2}", w["text"]):
            continue
        c = center(w["bbox"])
        near = [ln for ln in scale if abs(center(ln["bbox"])[1] - c[1]) <= 12 and 0 < ln["bbox"][0] - w["bbox"][2] <= 300]
        if not near:
            continue
        sc = min(near, key=lambda ln: (ln["bbox"][0] - w["bbox"][2], ln["bbox"]))
        above = [ln for ln in lines if ln is not sc and 0 <= sc["bbox"][1] - ln["bbox"][3] <= 14
                 and ln["bbox"][0] < sc["bbox"][2] + 150 and sc["bbox"][0] - 150 < ln["bbox"][2]]
        tl = min(above, key=lambda ln: (sc["bbox"][1] - ln["bbox"][3], ln["bbox"])) if above else None
        found.append((w, sc, tl))
    tb = pg.get("title_block") or {}
    right_edge = (tb.get("sheet_label_bbox") or [pg["page"]["width"]])[0] - 20
    out = []
    for w, sc, tl in found:
        wb = w["bbox"]
        same_row = [o for o, _, _ in found if o is not w and abs(center(o["bbox"])[1] - center(wb)[1]) <= 20]
        right = min([o["bbox"][0] - 5 for o in same_row if o["bbox"][0] > wb[0]] + [right_edge])
        left = max([o["bbox"][0] for o in same_row if o["bbox"][0] < wb[0]] + [wb[0] - 20])
        above_rows = [s2["bbox"][3] for o, s2, _ in found if o is not w and center(o["bbox"])[1] < wb[1] - 20
                      and o["bbox"][0] < right and left < s2["bbox"][2]]
        top = max(above_rows + [0.0]) + 2
        region = [left, top, right, sc["bbox"][3] + 2]
        inside = [x for x in words if region[0] <= center(x["bbox"])[0] <= region[2]
                  and region[1] <= center(x["bbox"])[1] <= region[3]]
        out.append({"n": w["text"], "bbox": wb, "title": tl["text"] if tl else "", "region": [r2(v) for v in region],
                    "method": weakest_method([w] + sc["words"]), "number_method": w["method"],
                    "lines": [ln["words"] for ln in geo_lines(inside)]})
    return out


def next_word_right(q_bbox, words):
    """Nearest word starting just right of a box on the same row, any read method."""
    h = max(q_bbox[3] - q_bbox[1], 1.0)
    cands = [w for w in words if q_bbox[2] - 1 <= w["bbox"][0] <= q_bbox[2] + 3 * h
             and min(q_bbox[3], w["bbox"][3]) - max(q_bbox[1], w["bbox"][1]) >= 0.5 * h]
    return min(cands, key=lambda w: (w["bbox"][0], w["bbox"])) if cands else None


def find_quantities(pg, tag_hits, blocks, callouts, drefs):
    page_words = geo_page_words(pg)
    qs = []
    for ln in page_lines(pg):
        s, owner = line_string(ln["words"], keep_quotes=True)
        if not s:
            continue
        taken = []
        for kind, unit, rx in Q_PATTERNS:
            for m in rx.finditer(s):
                a, b = m.span()
                if any(a < tb and ta < b for ta, tb in taken):
                    continue
                v = m.group("v")
                noun = ""
                qkind = kind
                if kind == "size":
                    rest = [t.strip("()") for t in m.group("rest").split()]
                    if not any(t in PIPE_WORDS for t in rest):
                        continue
                    b = m.start("rest") + len(m.group("rest").rstrip())
                    noun = " ".join(rest)
                if kind == "length" and unit == "FT":
                    nxt = s[b:].split()
                    if nxt and nxt[0].strip("(),.") in DIM_MATERIAL:
                        continue  # a dimension before a material word, not a quantity
                    fw = span_words(ln["words"], owner, a, b)
                    nw = next_word_right(union_box(fw), page_words) if fw else None
                    if not nxt and nw and norm_word(nw["text"]).strip(".") in DIM_MATERIAL:
                        continue  # same rule when the material word sits on another read's line
                if kind == "count" and m.groupdict().get("noun"):
                    noun = m.group("noun")
                if kind == "elevation":
                    noun = m.group("k")
                if kind == "slope" and unit == "%":
                    before = s[max(0, a - 25):a]
                    if not ("SLOPE" in before or "S=" in s[max(0, a - 6):a] or LF_AT_RE.search(s[:a])):
                        qkind = "percent"
                ws = span_words(ln["words"], owner, a, b)
                if not ws:
                    continue
                taken.append((a, b))
                qs.append({"value": v.replace(",", ""), "unit": unit, "kind": qkind, "item": noun,
                           "raw": s[a:b], "words": ws, "bbox": union_box(ws), "method": ln["method"],
                           "conf": min_conf(ws), "line_text": " ".join(w["text"] for w in ln["words"])})
    near_pool = [h for h in tag_hits if h["assignment"] in ("assigned", "ambiguous")]
    out = []
    for q in sorted(qs, key=lambda q: (q["bbox"], q["value"], q["unit"], q["method"], q["raw"])):
        if any(o["value"] == q["value"] and o["unit"] == q["unit"] and o["method"] == q["method"]
               and overlap_ratio(o["bbox"], q["bbox"]) >= OVERLAP for o in out[-20:]):
            continue
        near = sorted(((edge_dist(h["bbox"], q["bbox"]), h["form"], h["bbox"], h) for h in near_pool
                       if edge_dist(h["bbox"], q["bbox"]) <= NEAR_TAG_PT), key=lambda x: x[:3])
        kn = None
        cx, cy = center(q["bbox"])
        for blk in blocks:
            for e in blk["entries"]:
                eb = e["bbox"]
                if eb[0] - 2 <= cx <= eb[2] + 2 and eb[1] - 2 <= cy <= eb[3] + 2:
                    kn = e
        co = [c for c in callouts if c["n"] == str(kn["number"])] if kn else []
        near_co = sorted(((edge_dist(c["bbox"], q["bbox"]), c["n"], c["bbox"]) for c in callouts
                          if not kn and edge_dist(c["bbox"], q["bbox"]) <= NEAR_TAG_PT))[:3]
        near_dr = sorted(((edge_dist(d["bbox"], q["bbox"]), d["ref"], d["bbox"]) for d in drefs
                          if edge_dist(d["bbox"], q["bbox"]) <= NEAR_TAG_PT))[:3]
        out.append(dict(page_ref(pg), value=q["value"], unit=q["unit"], kind=q["kind"], item=q["item"],
                        raw=q["raw"], bbox=q["bbox"], method=q["method"], conf=q["conf"],
                        nearest_tag=near[0][3] if near else None, distance=r2(near[0][0]) if near else None,
                        line_text=q["line_text"], keyed_note=kn, keyed_callouts=co,
                        near_callouts=near_co, near_detail_refs=near_dr))
    return out


# ---------------------------------------------------------------- Step 2: anchors and crosswalk

TAG_HITS_HEADER = ["Tag Text", "Page Key", "Set Page", "Sheet", "BBox (pt)", "Method", "Confidence",
                   "Fuzzy (Y/N)", "Exact Ledger Match (Y/N)", "Search Form", "Assignment", "Ledger Rows",
                   "Ledger Tags", "Rollup Rows", "Candidate Rows", "Hit Kind", "Tag Level"]
QTY_HEADER = ["Value", "Unit", "Raw Text", "Page Key", "Set Page", "Sheet", "BBox (pt)", "Method", "Confidence",
              "Nearest Tag", "Distance (pt)", "Line Text", "Keyed Note", "Kind", "Item", "Nearest Tag Ledger Rows",
              "Keyed-Note Callouts", "Callouts Nearby", "Detail Refs Nearby", "Tag Level"]
XWALK_HEADER = ["Ledger Row", "Tag", "Family", "Searchable (Y/N)", "Ledger Drawing Sheets", "Cited Sheets",
                "Sheets Found On", "Sheets Cited but Not Found", "Sheets Found but Not Cited",
                "Hits Not Counted", "Anchor Check", "Quantities Seen", "Sheet Evidence Level",
                "Row Tag Level", "Status", "Notes"]
UNMATCHED_HEADER = ["Tag Text", "Shape", "Occurrences", "Page Keys", "Sheets", "Methods", "Max Confidence",
                    "First Page Key", "First BBox (pt)"]


def fmt_conf(c):
    return "" if c is None else f"{c:.2f}"


def sheet_pages(pages):
    by_sheet = defaultdict(list)
    for pg in pages:
        by_sheet[pg["sheet_01"]].append(pg["page_key"])
    return by_sheet


def content_match(line_groups, r):
    """Does the anchor text hold the row's quantity (value and unit) or, for a row whose Ledger
    Name has no quantity, a specific noun from the Name? -> ("matched: ...", level) or (None, None)."""
    best = None
    for words in line_groups:
        if not words:
            continue
        s, owner = line_string(words, keep_quotes=True)
        for v, u in r["qty"]:
            for m in re.finditer(r"(?<![\d.])" + re.escape(v) + r"\s?" + QTY_UNIT_FORMS[u], s):
                ws = span_words(words, owner, m.start(), m.end())
                if ws:
                    cand = (method_level(weakest_method(ws)), f"matched: quantity {v} {u}")
                    best = min(best, cand, key=lambda c: LEVELS.index(c[0])) if best else cand
        for m in re.finditer(r"[A-Z]{4,}", s) if not r["qty"] else ():
            if stem(m.group(0)) in r["nouns"]:
                ws = span_words(words, owner, m.start(), m.end())
                if ws:
                    cand = (method_level(weakest_method(ws)), f"matched: noun {stem(m.group(0))}")
                    best = min(best, cand, key=lambda c: LEVELS.index(c[0])) if best else cand
        if best and best[0] == "Verified":
            break
    return (best[1], best[0]) if best else (None, None)


def page_line_groups(pg):
    return [ln["words"] for ln in page_lines(pg)]


def anchor_check(r, sheet, anchor, pages_by_key, sheet_keys, facts):
    """One Drawing Sheets anchor -> (kind, result text, level). Gate A rule: Verified when the
    anchor is found in the native text layer and its text holds the row's quantity (or, for a row
    with no quantity, a specific noun from the Ledger Name); Inferred for the same match by OCR or
    Bluebeam; Unresolved when the anchor is not found or its text does not match."""
    keys = sheet_keys.get(sheet, [])
    if not keys:
        return "sheet", f"{sheet}: sheet not in the set", "Unresolved"
    m = re.fullmatch(r"Add\. 4 p\.(\d+)", anchor)
    if m:
        k = f"add4_p{int(m.group(1)):02d}"
        pg = pages_by_key.get(k)
        if not pg or pg["sheet_01"] != sheet:
            return "Add. 4 page", f"{sheet} (Add. 4 p.{int(m.group(1))}): no Add. 4 page for this sheet", "Unresolved"
        what, lv = content_match(page_line_groups(pg), r)
        if not what:
            return "Add. 4 page", f"{sheet} (Add. 4 p.{int(m.group(1))}): page present ({k}); no match for the row's quantity or specific noun", "Unresolved"
        return "Add. 4 page", f"{sheet} (Add. 4 p.{int(m.group(1))}): {what} ({lv}, {k})", lv
    m = re.fullmatch(r"KN (\d+(?:\s*,\s*\d+)*)", anchor)
    if m:
        res, lvs = [], []
        for n in [int(x) for x in re.findall(r"\d+", m.group(1))]:
            got = [(k, e, blk) for k in keys for blk in facts[k]["keyed"] for e in blk["entries"] if e["number"] == n]
            if not got:
                n_blk = sum(len(b["entries"]) for k in keys for b in facts[k]["keyed"])
                res.append(f"{sheet} KN {n}: not found (keyed-note entries read: {n_blk})")
                lvs.append("Unresolved")
                continue
            k, e, blk = got[0]
            what, lv = content_match(e["lines"], r)
            num = f"number {e['basis']} ({e['number_level']})"
            if not what:
                res.append(f"{sheet} KN {n}: entry found, {num}, {k} {fmt_box(e['bbox'])}; text does not hold the "
                           f"row's quantity or specific noun: \"{e['text'][:70]}\"")
                lvs.append("Unresolved")
            else:
                lvl = weakest([lv, e["number_level"]])
                res.append(f"{sheet} KN {n}: {what} ({lv}); {num}; {k} {fmt_box(e['bbox'])}")
                lvs.append(lvl)
        return "keyed note", "; ".join(res), weakest(lvs)
    m = re.fullmatch(r"Det\. (\d+)(?:\s*[–-]\s*(\d+))?(?:,.*)?", anchor)
    if m:
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        nums = list(range(lo, hi + 1))
        nums += [int(x) for x in re.findall(r",\s*(\d+)$", anchor) if int(x) not in nums]
        res, lvs = [], []
        for n in nums:
            got = [(k, d) for k in keys for d in facts[k]["details"] if d["n"] == str(n)]
            if not got:
                res.append(f"{sheet} Det. {n}: not found")
                lvs.append("Unresolved")
                continue
            k, d = min(got, key=lambda g: (METHOD_RANK[g[1]["number_method"]], g[0], g[1]["bbox"]))
            what, lv = content_match(d["lines"], r)
            if not what:
                res.append(f"{sheet} Det. {n}: detail found ({k} {fmt_box(d['bbox'])}) titled \"{d['title'][:60]}\"; "
                           f"detail region {fmt_box(d['region'])} does not hold the row's quantity or specific noun")
                lvs.append("Unresolved")
            else:
                lvl = weakest([lv, method_level(d["number_method"])])
                res.append(f"{sheet} Det. {n}: {what} ({lv}) in detail \"{d['title'][:60]}\"; {k} {fmt_box(d['bbox'])}")
                lvs.append(lvl)
        return "detail", "; ".join(res), weakest(lvs)
    if re.fullmatch(r"[A-Z]{1,4}-\d+", anchor):
        got = [h for k in keys for h in facts[k]["tags"] if h["form"] == norm_form(anchor)
               and h["assignment"] in ("assigned", "ambiguous")]
        if not got:
            return "tag", f"{sheet} ({anchor}): not found", "Unresolved"
        h = min(got, key=lambda h: (METHOD_RANK[h["method"]], h["page_key"], h["bbox"]))
        what, lv = content_match([facts[h["page_key"]]["line_of"][id(h)]], r)
        if not what:
            return "tag", f"{sheet} ({anchor}): found ({h['method']}, {h['page_key']} {fmt_box(h['bbox'])}); line does not hold the row's quantity or specific noun", "Unresolved"
        return "tag", f"{sheet} ({anchor}): {what} ({lv}) on the tag's line; {h['page_key']} {fmt_box(h['bbox'])}", weakest([lv, method_level(h["method"])])
    if anchor == "sheet only":
        # Owner's rule: only the row's quantity read in the text layer makes a sheet-only anchor
        # Verified; a noun anywhere on the sheet is Inferred (location not pinned).
        best = None
        for k in keys:
            what, lv = content_match(page_line_groups(pages_by_key[k]), r)
            if what and what.startswith("matched: noun"):
                what, lv = what + " (on sheet, location not pinned)", "Inferred"
            if what and (best is None or LEVELS.index(lv) < LEVELS.index(best[1])):
                best = (what, lv, k)
        if not best:
            return "sheet only", f"{sheet}: no match for the row's quantity or specific noun on the sheet", "Unresolved"
        return "sheet only", f"{sheet}: {best[0]} ({best[1]}, {best[2]})", best[1]
    return "other", f"{sheet} ({anchor}): anchor type not machine-checkable", "Unresolved"


def crosswalk(rows, pages, facts, tag_hits, qty):
    pages_by_key = {pg["page_key"]: pg for pg in pages}
    sheet_keys = sheet_pages(pages)
    counted = defaultdict(list)     # row -> [(hit, "assigned" | "rollup")]
    not_counted = defaultdict(list)
    for h in tag_hits:
        if h["assignment"] == "assigned":
            for r in h["rows"]:
                counted[r].append((h, "assigned"))
            for r in h["rollup"]:
                counted[r].append((h, "rollup"))
        else:
            for r in h["candidate_rows"]:
                not_counted[r].append(h)
    q_by_row = defaultdict(list)
    for q in qty:
        h = q["nearest_tag"]
        if h and h["assignment"] == "assigned":
            for r in h["rows"]:
                q_by_row[r].append(q)
    kn_q = defaultdict(list)   # (sheet, keyed note number) -> quantities in that entry
    for q in qty:
        if q["keyed_note"]:
            kn_q[(q["sheet"], q["keyed_note"]["number"])].append(q)
    out, anchor_stats, anchor_terms = [], Counter(), Counter()
    for r in rows:
        found = defaultdict(set)
        for h, how in counted[r["row"]]:
            found[h["sheet"]].add(h["method"] + (" fuzzy" if h["fuzzy"] else "") + (" rollup" if how == "rollup" else ""))
        anchors_txt, levels, notes = [], [], []
        qs = list(q_by_row[r["row"]])
        if r["family"] == "PROPOSED":
            for s, anchors, raw in r["tokens"]:
                if not s:
                    continue
                for a in (anchors or ["sheet only"]):
                    kind, txt, lv = anchor_check(r, s, a, pages_by_key, sheet_keys, facts)
                    anchors_txt.append(txt)
                    levels.append(lv)
                    anchor_stats[(kind, lv)] += 1
                    m = re.search(r"matched: (quantity|noun)", txt)
                    anchor_terms[(kind, m.group(1) if m else "no match", lv)] += 1
                    if a.startswith("KN"):
                        for n in re.findall(r"\d+", a):
                            qs += kn_q.get((s, int(n)), [])
            sheet_level = weakest(levels) if levels else "Unresolved"
        else:
            for s, anchors, raw in r["tokens"]:
                for a in anchors:
                    if a.startswith("KN"):
                        for n in re.findall(r"\d+", a):
                            qs += kn_q.get((s, int(n)), [])
            per_sheet = [("Verified" if any(m == "text-layer" for m in ms) else "Inferred") for ms in found.values()]
            sheet_level = weakest(per_sheet) if found else "Unresolved"
        cited = r["cited"]
        cited_nf = [s for s in cited if s not in found] if r["family"] != "PROPOSED" else []
        found_nc = [s for s in sorted(found, key=sheet_sort_key) if s not in cited]
        found_txt = "" if r["family"] == "PROPOSED" else "; ".join(
            f"{s} [{', '.join(sorted(found[s]))}]" for s in sorted(found, key=sheet_sort_key))
        nc = defaultdict(set)
        for h in not_counted[r["row"]]:
            reason = h["assignment"] if h["assignment"] != "ambiguous" else \
                "ambiguous with rows " + ", ".join(map(str, h["candidate_rows"]))
            nc[(h["sheet"], reason)].add(h["method"])
        nc_txt = "; ".join(f"{s} [{', '.join(sorted(ms))}; {reason}]"
                           for (s, reason), ms in sorted(nc.items(), key=lambda kv: (sheet_sort_key(kv[0][0]), kv[0][1])))
        seen, qtxt = set(), []
        for q in sorted(qs, key=lambda q: (sheet_sort_key(q["sheet"]), q["page_key"], q["bbox"], q["value"], q["unit"], q["method"])):
            key = (q["page_key"], q["value"], q["unit"], tuple(q["bbox"]), q["method"])
            if key in seen:
                continue
            seen.add(key)
            qtxt.append(f"{q['value']} {q['unit']} ({q['sheet']}, {q['method']})")
        row_level = weakest([sheet_level] + (["Inferred"] if qtxt else []))
        if not r["tokens"]:
            status = "no sheet cited"
        elif not cited:
            status = "no sheet number cited"
        elif r["family"] == "PROPOSED":
            status = "anchors checked"
        elif not found:
            status = "not found on any page"
        elif cited_nf:
            status = "found; some cited sheets not found"
        else:
            status = "found on every cited sheet"
        m = re.search(r"form shared with row\(s\) [\d, ]+", r["reason"])
        if m:
            notes.append(m.group(0))
        out.append({"row": r["row"], "tag": r["tag"], "family": r["family"], "searchable": r["searchable"],
                    "sheets_field": r["sheets_field"], "cited": cited, "found": found_txt,
                    "cited_nf": cited_nf, "found_nc": found_nc, "not_counted": nc_txt, "anchors": anchors_txt,
                    "qty": qtxt, "sheet_level": sheet_level, "row_level": row_level, "status": status,
                    "notes": notes})
    return out, (anchor_stats, anchor_terms)


def sheet_sort_key(s):
    m = re.match(r"([A-Z]+)(\d+)\.(\d+)([A-Z]?)", s or "")
    order = {"G": 0, "C": 1, "A": 2, "S": 3, "E": 4}
    if not m:
        return (9, 0, 0, s or "")
    return (order.get(m.group(1), 8), int(m.group(2)), int(m.group(3)), m.group(4))


def unmatched_tags(pages, comp):
    strict_forms = [c[1] for c in comp]
    canon_forms = [c[2] for c in comp]
    agg = {}
    for pg in pages:
        for ln in page_lines(pg):
            s, owner = line_string(ln["words"])
            cs = s.translate(CONFUSE)
            for shape, rx in UNMATCHED_SHAPES:
                for m in rx.finditer(s):
                    t = m.group(0)
                    if SHEET_RE.match(t.replace(" ", "")):
                        continue
                    a, b = m.span()
                    if any(f.fullmatch(t) for f in strict_forms) or any(f.fullmatch(cs[a:b]) for f in canon_forms):
                        continue
                    ws = span_words(ln["words"], owner, a, b)
                    if not ws:
                        continue
                    key = t.replace(" ", "")
                    e = agg.setdefault(key, {"text": t, "shape": shape, "n": 0, "keys": set(), "sheets": set(),
                                             "methods": set(), "conf": None, "first": None})
                    e["n"] += 1
                    e["keys"].add(pg["page_key"])
                    e["sheets"].add(pg["sheet_01"])
                    e["methods"].add(ln["method"])
                    c = min_conf(ws)
                    if c is not None:
                        e["conf"] = c if e["conf"] is None else max(e["conf"], c)
                    first = (pg["page_key"], union_box(ws))
                    if e["first"] is None or first < e["first"]:
                        e["first"] = first
    rows = []
    for key in sorted(agg, key=lambda k: (-agg[k]["n"], k)):
        e = agg[key]
        rows.append([e["text"], e["shape"], e["n"], "; ".join(sorted(e["keys"])),
                     "; ".join(sorted(e["sheets"], key=sheet_sort_key)), "; ".join(sorted(e["methods"])),
                     fmt_conf(e["conf"]), e["first"][0], fmt_box(e["first"][1])])
    return rows


def kn_label(e):
    n, rd = e["number"], e["read_number"]
    if e["basis"] == "read":
        return f"{n} (read; {e['number_level']})"
    if rd:
        return f"{n} (by order; marker read as {rd}; {e['number_level']})"
    return f"{n} (by order; {e['number_level']})"


def load_pages(out):
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted((out / "pages").glob("*.json"))]


def hit_json(h):
    return {"text": h["tag_text"], "form": h["form"], "assignment": h["assignment"], "ledger_rows": h["rows"],
            "rollup_rows": h["rollup"], "candidate_rows": h["candidate_rows"], "bbox": h["bbox"],
            "method": h["method"], "conf": h["conf"], "fuzzy": h["fuzzy"], "kind": h["kind"],
            "tag_level": method_level(h["method"])}


def qty_json(q):
    return {"value": q["value"], "unit": q["unit"], "kind": q["kind"], "item": q["item"], "raw": q["raw"],
            "bbox": q["bbox"], "method": q["method"], "conf": q["conf"], "line_text": q["line_text"],
            "nearest_tag": q["nearest_tag"]["form"] if q["nearest_tag"] else "none",
            "nearest_tag_rows": q["nearest_tag"]["rows"] if q["nearest_tag"] else [],
            "distance": q["distance"],
            "keyed_note": kn_label(q["keyed_note"]) if q["keyed_note"] else None,
            "keyed_callouts": [c["bbox"] for c in q["keyed_callouts"]],
            "callouts_nearby": [[c[1], c[2], r2(c[0])] for c in q["near_callouts"]],
            "detail_refs_nearby": [[d[1], d[2], r2(d[0])] for d in q["near_detail_refs"]],
            "tag_level": "Inferred"}


def block_json(b):
    return dict({k: v for k, v in b.items() if k != "entries"},
                entries=[{k: v for k, v in e.items() if k != "lines"} for e in b["entries"]])


def sheet_lanes():
    base, _, addendum_only = load_sheet_index()
    lanes = {}
    for s in base.values():
        lanes[s["sheet"]] = re.sub(r"\s*\(adj\.\)\s*$", "", s["lane"])
    for sheet, r in addendum_only.items():
        lanes.setdefault(sheet, re.sub(r"\s*\(adj\.\)\s*$", "", r.get("Lane", "")))
    return lanes


def stage_hits(out):
    rows = build_forms()
    by_row = {r["row"]: r for r in rows}
    lanes = sheet_lanes()
    comp = compile_forms(rows)
    pages = load_pages(out)
    info = extractor_info()
    facts = {}
    all_tags, all_qty = [], []
    for pg in pages:
        tags = find_tags(pg, comp)
        for h in tags:
            h["assignment"], h["rows"], h["rollup"], h["candidate_rows"] = assign_hit(h, by_row, lanes)
        legends = find_legends(pg, rows)
        for h in legends:
            h["candidate_rows"] = list(h["rows"])
        tags = sorted(tags + legends, key=lambda h: (h["bbox"], h["form"], h["method"], h["tag_text"]))
        blocks = keyed_notes(pg)
        tb = pg.get("title_block") or {}
        exclude = [b["bbox"] for b in blocks]
        if tb.get("sheet_label_bbox"):
            lb = tb["sheet_label_bbox"]
            exclude.append([lb[0] - 20, 0.0, pg["page"]["width"], pg["page"]["height"]])
        callouts = isolated_numbers(pg, exclude)
        drefs = detail_refs(pg)
        qty = find_quantities(pg, tags, blocks, callouts, drefs)
        line_of = {}
        lines = page_lines(pg)
        for h in tags:
            if h["kind"] == "tag":
                line_of[id(h)] = next((ln["words"] for ln in lines if ln["method"] == h["method"]
                                       and any(overlap_ratio(w["bbox"], h["bbox"]) > 0 for w in ln["words"])), [])
        facts[pg["page_key"]] = {"tags": tags, "keyed": blocks, "callouts": callouts,
                                 "details": detail_titles(pg), "drefs": drefs, "line_of": line_of}
        pg["tags"] = [hit_json(h) for h in tags]
        pg["quantities"] = [qty_json(q) for q in qty]
        pg["keyed_notes"] = [block_json(b) for b in blocks]
        pg["extractor"] = info
        write_json(out / "pages" / f"{pg['page_key']}_{pg['sheet_01']}.json", pg)
        all_tags += tags
        all_qty += qty
    write_csv(out / "Tag_Hits.csv", TAG_HITS_HEADER, [
        [h["tag_text"], h["page_key"], h["set_page"] or "", h["sheet"], fmt_box(h["bbox"]), h["method"],
         fmt_conf(h["conf"]), "Y" if h["fuzzy"] else "N", "N" if h["fuzzy"] else "Y", h["form"], h["assignment"],
         "; ".join(map(str, h["rows"])), "; ".join(by_row[x]["tag"] for x in h["rows"]),
         "; ".join(map(str, h["rollup"])), "; ".join(map(str, h["candidate_rows"])), h["kind"],
         method_level(h["method"])]
        for h in sorted(all_tags, key=lambda h: (h["page_key"], h["bbox"], h["form"], h["method"]))])
    write_csv(out / "Quantity_Hits.csv", QTY_HEADER, [
        [q["value"], q["unit"], q["raw"], q["page_key"], q["set_page"] or "", q["sheet"], fmt_box(q["bbox"]),
         q["method"], fmt_conf(q["conf"]), q["nearest_tag"]["form"] if q["nearest_tag"] else "none",
         "" if q["distance"] is None else f"{q['distance']:.2f}", q["line_text"],
         kn_label(q["keyed_note"]) if q["keyed_note"] else "",
         q["kind"], q["item"],
         ("; ".join(map(str, q["nearest_tag"]["rows"])) or ("ambiguous: " + "; ".join(map(str, q["nearest_tag"]["candidate_rows"]))))
         if q["nearest_tag"] else "",
         "; ".join(fmt_box(c["bbox"]) for c in q["keyed_callouts"]),
         "; ".join(f"{c[1]} ({c[0]:.1f} pt)" for c in q["near_callouts"]),
         "; ".join(f"{d[1]} ({d[0]:.1f} pt)" for d in q["near_detail_refs"]), "Inferred"]
        for q in sorted(all_qty, key=lambda q: (q["page_key"], q["bbox"], q["value"], q["unit"], q["method"]))])
    xw, (anchor_stats, anchor_terms) = crosswalk(rows, pages, facts, all_tags, all_qty)
    write_csv(out / "Ledger_Crosswalk.csv", XWALK_HEADER, [
        [x["row"], x["tag"], x["family"], x["searchable"], x["sheets_field"], "; ".join(x["cited"]),
         x["found"], "; ".join(x["cited_nf"]), "; ".join(x["found_nc"]), x["not_counted"],
         " | ".join(x["anchors"]), "; ".join(x["qty"]), x["sheet_level"], x["row_level"], x["status"],
         "; ".join(x["notes"])]
        for x in xw])
    write_csv(out / "Unmatched_Tags.csv", UNMATCHED_HEADER, unmatched_tags(pages, comp))
    return {"rows": rows, "pages": pages, "facts": facts, "tags": all_tags, "qty": all_qty, "xwalk": xw,
            "anchor_stats": anchor_stats, "anchor_terms": anchor_terms}


# ---------------------------------------------------------------- reports: Findings, Spot_Check, README

SPOT_SEED = 20260930
SPOT_DISCIPLINES = ["C", "E", "S", "A", "G"]
SPOT_PER = 5
SPOT_HEADER = ["Pick No.", "Ledger Row", "Tag", "Name", "What to Check", "Source Citation", "Confidence Tag",
               "Read Method", "Human Result", "Checked By", "Date", "Note", "Set Page", "BBox (pt)", "Word Read",
               "Confidence", "Crop Path"]
PART_SHORT = {  # short names from library/Plan_Set_Parts.md and 01
    "Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 1.pdf": "Part 1",
    "Pages from eswd-wwtp-upgrade-ph1-11x17-plans Part 2.pdf": "Part 2",
    "Pages from eswd-wwtp-upgrade-ph1-11x17-plans - Part 3.pdf": "Part 3",
    "addendum-no4-eswd.pdf": "Add. 4",
}


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def cite(pg):
    return f"{pg['sheet_01']}, {PART_SHORT[Path(pg['source']['file']).name]} p.{pg['source']['page']}"


def where(pg):
    return f"set p.{pg['set_page']}" if pg["set_page"] else f"Add. 4 p.{pg['source']['page']}"


def spot_check(pages, by_row, crops):
    rng = random.Random(SPOT_SEED)
    rows = []
    pick = 0
    for disc in SPOT_DISCIPLINES:
        pop = []
        for pg in pages:
            if not pg["sheet_01"].startswith(disc):
                continue
            for w in list(pg["words"]) + list((pg.get("bluebeam") or {}).get("words", [])):
                if len(re.findall(r"[A-Za-z0-9]", w["text"])) >= 2:
                    pop.append((pg["page_key"], w["bbox"], w["text"], w["method"], pg, w))
        pop.sort(key=lambda x: x[:4])
        for key, bb, text, method, pg, w in rng.sample(pop, SPOT_PER):
            pick += 1
            hit = next((h for h in pg.get("tags", []) if h["assignment"] == "assigned"
                        and overlap_ratio(h["bbox"], bb) >= OVERLAP), None)
            rws = hit["ledger_rows"] if hit else []
            crop = f"crops/spot_{pick:02d}_{pg['sheet_01']}_{key}.png"
            note = []
            if w["conf"] is not None:
                note.append(f"Tesseract confidence {w['conf']:.2f}" + ("" if w["conf"] >= CONF_FLAG else " (below 60)"))
            if hit:
                note.append(f"part of tag hit {hit['form']!r}")
            rows.append([pick, "; ".join(map(str, rws)), "; ".join(by_row[x]["tag"] for x in rws),
                         "; ".join(by_row[x]["name"] for x in rws),
                         f"Does the 400 dpi render show \"{text}\" at this box on {pg['sheet_01']} ({where(pg)})?",
                         cite(pg), method_level(method), method, "", "", "", "; ".join(note),
                         pg["set_page"] or "", fmt_box(bb), text, fmt_conf(w["conf"]), crop])
            if crops:
                save_crop(pg, bb, Path(crops) / crop)
    return rows


def save_crop(pg, bb, dest):
    from PIL import ImageDraw
    doc = pymupdf.open(REPO / pg["source"]["file"])
    page = doc[pg["source"]["page"] - 1]
    clip = pymupdf.Rect(bb[0] - 30, bb[1] - 30, bb[2] + 30, bb[3] + 30) & page.rect
    z = DPI / 72.0
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    d = ImageDraw.Draw(img)
    x0, y0 = (bb[0] - clip.x0) * z, (bb[1] - clip.y0) * z
    x1, y1 = (bb[2] - clip.x0) * z, (bb[3] - clip.y0) * z
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], outline=(220, 0, 0), width=4)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest)


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "/") for c in r) + " |")
    return out


def findings(out, pages, res):
    sm = read_csv(out / "Sheet_Map.csv")
    th = read_csv(out / "Tag_Hits.csv")
    qh = read_csv(out / "Quantity_Hits.csv")
    xw = read_csv(out / "Ledger_Crosswalk.csv")
    um = read_csv(out / "Unmatched_Tags.csv")
    by_key = {pg["page_key"]: pg for pg in pages}
    base = [r for r in sm if not r["Page Key"].startswith("add4")]
    add4 = [r for r in sm if r["Page Key"].startswith("add4")]
    L = ["# OCR lane findings", "",
         f"Machine reads from `{SCRIPT_REL}`. Text-layer reads are Verified; every OCR and "
         "Bluebeam read is Inferred until checked on the page image; every quantity is a lead, not a takeoff "
         "(README.md, confidence rule). Nothing here is in the Ledger or the MTO. Page and box cites use "
         "`Page Key` and PDF points (origin top left, rotation applied).", ""]
    n_words = Counter()
    for pg in pages:
        for w in pg["words"]:
            n_words[w["method"]] += 1
        n_words["bluebeam-ocr"] += len((pg.get("bluebeam") or {}).get("words", []))
    L += ["## Summary", "",
          f"- Pages: {len(base)} set pages and {len(add4)} Addendum 4 reissue pages (`Sheet_Map.csv`).",
          f"- Words kept: {n_words['text-layer']} text layer, {n_words['ocr']} OCR (Tesseract, not under a "
          f"text-layer word), {n_words['bluebeam-ocr']} Bluebeam.",
          f"- Tag hits: {len(th)} ({', '.join(f'{v} {k}' for k, v in sorted(Counter(t['Assignment'] for t in th).items()))}).",
          f"- Quantity leads: {len(qh)}; in a keyed note: {sum(1 for q in qh if q['Keyed Note'])}; "
          f"with a tag within {NEAR_TAG_PT:.0f} pt: {sum(1 for q in qh if q['Nearest Tag'] != 'none')}.",
          f"- Ledger rows in the crosswalk: {len(xw)}. Tag-shaped text with no Ledger row: {len(um)} distinct.", ""]
    # title blocks
    mism = [r for r in sm if r["Match (Y/N)"] != "Y"]
    tmis = [r for r in sm if r["Title Match (Y/N)"] != "Y"]
    L += ["## Title blocks", "",
          f"- Sheet number read in the title block matches 01 on {sum(r['Match (Y/N)'] == 'Y' for r in base)} of "
          f"{len(base)} set pages and {sum(r['Match (Y/N)'] == 'Y' for r in add4)} of {len(add4)} Addendum 4 pages."]
    if mism:
        for r in mism:
            pg = by_key[r["Page Key"]]
            sh = (pg["title_block"].get("sheet") or {})
            L.append(f"  - Mismatch: {r['Page Key']} ({cite(pg)}): 01 {r['01 Sheet']}, read "
                     f"{r['Title-Block Sheet Read'] or 'nothing'} {fmt_box(sh.get('bbox'))}.")
    else:
        L.append("  - Mismatches: none.")
    L.append(f"- Title read matches 01 on {len(sm) - len(tmis)} of {len(sm)} pages (01's \"(cover index)\" marker ignored).")
    for r in tmis:
        pg = by_key[r["Page Key"]]
        tt = (pg["title_block"].get("title") or {})
        L.append(f"  - {r['Page Key']} ({cite(pg)}): 01 \"{r['01 Title']}\", read \"{r['Title Read']}\" {fmt_box(tt.get('bbox'))}.")
    ocr_pages = [r for r in sm if r["Title-Block Source"].startswith("ocr")]
    L.append(f"- {len(ocr_pages)} pages have no title block in the text layer and were read by the rotated title-strip "
             "OCR pass (Inferred): " + ", ".join(f"{r['Page Key']} {r['01 Sheet']}" for r in ocr_pages) + ". "
             "They are vector drawings without a text layer, not raster images.")
    s_pages = [r for r in base if r["01 Sheet"].startswith("S")]
    L.append("- S-sheet page totals: " + ", ".join(f"{r['01 Sheet']} \"{r['Page Read (N OF M)']}\"" for r in s_pages)
             + ". 01 item 10 logged \"OF 98\" at stored image resolution; the native pages read OF 96 (OCR, Inferred): "
             + "; ".join(f"{r['Page Key']} {fmt_box((by_key[r['Page Key']]['title_block'].get('page_of') or {}).get('bbox'))}" for r in s_pages) + ".")
    c16 = next((r for r in add4 if r["01 Sheet"] == "C1.6A"), None)
    if c16:
        pg = by_key[c16["Page Key"]]
        L.append(f"- C1.6A (Add. 4 p.{pg['source']['page']}) reads \"{c16['Page Read (N OF M)']}\" "
                 f"{fmt_box((pg['title_block'].get('page_of') or {}).get('bbox'))}. It reissues no page of the 96-sheet set, "
                 "so it governs nothing here (Unresolved: the base issue cites Addendum 3, not in the library).")
    L.append("- Addendum 4 supersession is taken from 01, not from title-block dates (the reissues keep the base dates): "
             + "; ".join(f"{r['Page Key']} {r['01 Sheet']} governs {r['Governs']}" for r in add4 if r["Governs"].startswith("set")) + ".")
    L.append("")
    # missing sheets
    miss = [r for r in base if "not in library" in r["Split-Part File and Page"]]
    L += ["## Sheets 01 lists as not in library, found", "",
          f"01 lists {len(miss)} sheets as not in library. All {len(miss)} are in the native parts and read in their title blocks:", ""]
    trs = []
    for r in miss:
        pg = by_key[r["Page Key"]]
        sh = pg["title_block"].get("sheet") or {}
        trs.append([r["Set Page"], r["01 Sheet"], r["Title-Block Sheet Read"], sh.get("method", ""),
                    fmt_box(sh.get("bbox")), f"{PART_SHORT[r['Native File']]} p.{r['Native Page']}"])
    L += md_table(["Set p.", "01 sheet", "Read", "Method", "BBox (pt)", "Native page"], trs) + [""]
    # known values
    L += ["## Known values (Test 5)", ""]
    for q in qh:
        if q["Sheet"] == "C2.1" and q["Unit"] == "LF" and q["Value"] in ("149", "134"):
            L.append(f"- C2.1 {q['Value']} LF: {q['Method']}, {q['Page Key']} {q['BBox (pt)']}, keyed note {q['Keyed Note']}: "
                     f"\"{q['Line Text']}\" (Inferred).")
    for t in th:
        if t["Sheet"] == "C2.3" and t["Search Form"] == "SD-3" and t["Method"] == "text-layer":
            L.append(f"- SD-3 on C2.3: text layer, {t['Page Key']} {t['BBox (pt)']} (Verified).")
    L.append("")
    # fence rows
    xr = {x["Ledger Row"]: x for x in xw}
    L += ["## Chain link fence rows: stated, not reconciled", "",
          "- C2.1 keyed notes 6 and 8 read 149 LF and 134 LF of 6' chain link fence, each connected to existing. "
          "Both are OCR and Bluebeam reads only (Inferred; boxes above).",
          f"- Ledger row 89 \"{xr['89']['Tag']}\" ({xr['89']['Ledger Drawing Sheets']}) carries the C2.1 values only in its "
          f"Notes. Its anchor check: {xr['89']['Anchor Check']}.",
          f"- Ledger row 19 \"{xr['19']['Tag']}\" is a different fence: {xr['19']['Ledger Drawing Sheets']}, existing, "
          f"to be removed. Its anchor check: {xr['19']['Anchor Check']}.",
          "- This lane does not reconcile them. The fence count and lengths need a person's check against C2.1, C2.5 "
          "and C0.5.", ""]
    # crosswalk gaps
    pr = [x for x in xw if x["Family"] == "printed"]
    L += ["## Biggest crosswalk gaps", "",
          "Printed tags not found on any page:", ""]
    L += md_table(["Ledger row", "Tag", "Cited sheets", "Hits not counted"],
                  [[x["Ledger Row"], x["Tag"], x["Cited Sheets"] or "none", x["Hits Not Counted"] or ""]
                   for x in pr if x["Status"] == "not found on any page"]) + [""]
    gaps = sorted((x for x in pr if x["Sheets Cited but Not Found"]),
                  key=lambda x: (-len(x["Sheets Cited but Not Found"].split("; ")), int(x["Ledger Row"])))
    L += ["Printed tags with the most cited sheets where the tag was not read (top 15):", ""]
    L += md_table(["Ledger row", "Tag", "Cited but not found", "Found on"],
                  [[x["Ledger Row"], x["Tag"], x["Sheets Cited but Not Found"], x["Sheets Found On"]] for x in gaps[:15]]) + [""]
    fnc = [x for x in pr if x["Sheets Found but Not Cited"]]
    L += [f"Printed tags found on sheets the row does not cite: {len(fnc)} rows.", ""]
    L += md_table(["Ledger row", "Tag", "Found but not cited"],
                  [[x["Ledger Row"], x["Tag"], x["Sheets Found but Not Cited"]] for x in fnc]) + [""]
    for pgk in sorted({t["Page Key"] for t in th}):
        pass
    # tag hits not counted
    nc = Counter(t["Assignment"] for t in th if t["Assignment"] not in ("assigned",))
    L += ["Tag hits not counted as found (Gate A rules): "
          + ", ".join(f"{v} {k}" for k, v in sorted(nc.items())) + ". Each is listed under its candidate rows in the "
          "crosswalk's \"Hits Not Counted\" column.", ""]
    # PROPOSED anchors
    st = res["anchor_stats"]
    kinds = sorted({k for k, _ in st})
    L += ["## PROPOSED anchors (Gate A rule)", "",
          "Verified: the anchor was found in the native text layer and its text holds the row's quantity (value and "
          "unit), or, for a row whose Ledger Name has no quantity, a specific noun from the Name. Inferred: the same "
          "match read by OCR or Bluebeam. Unresolved: the anchor was not found, or its text does not match. A keyed "
          "note numbered by order is at best Inferred, and Unresolved where its block's entry count and highest "
          "marker read disagree. A sheet-only anchor (a cited sheet with no KN, Det. or Add. anchor) is Verified only "
          "when the row's quantity (value and unit) is read on that sheet in the text layer; a noun match anywhere on "
          "the sheet is Inferred (\"on sheet, location not pinned\").", ""]
    L += md_table(["Anchor type", "Verified", "Inferred", "Unresolved", "Total"],
                  [[k, st[(k, "Verified")], st[(k, "Inferred")], st[(k, "Unresolved")],
                    sum(st[(k, lv)] for lv in LEVELS)] for k in kinds]
                  + [["all", sum(v for (k, lv), v in st.items() if lv == "Verified"),
                      sum(v for (k, lv), v in st.items() if lv == "Inferred"),
                      sum(v for (k, lv), v in st.items() if lv == "Unresolved"), sum(st.values())]]) + [""]
    tm = res["anchor_terms"]
    L += ["Anchors by match term:", ""]
    L += md_table(["Anchor type", "Match term", "Verified", "Inferred", "Unresolved"],
                  [[k, t, tm[(k, t, "Verified")], tm[(k, t, "Inferred")], tm[(k, t, "Unresolved")]]
                   for k, t in sorted({(k, t) for k, t, _ in tm})]) + [""]
    pp = [x for x in xw if x["Family"] == "PROPOSED"]
    L.append("PROPOSED rows by weakest anchor (the row's sheet evidence level): "
             + ", ".join(f"{v} {k}" for k, v in sorted(Counter(x["Sheet Evidence Level"] for x in pp).items()))
             + f"; {sum(1 for x in pp if x['Status'] != 'anchors checked')} rows cite no sheet number.")
    L += [""]
    # keyed notes
    L += ["## Keyed-note blocks", ""]
    krows = []
    for pg in pages:
        for b in pg.get("keyed_notes", []):
            by_order = sum(1 for e in b["entries"] if e["basis"] == "by order")
            krows.append([pg["page_key"], pg["sheet_01"], b["heading"], len(b["entries"]),
                          sum(1 for e in b["entries"] if e["read_number"]), b["highest_marker_read"] or "",
                          by_order, b["count_check"]])
    L += md_table(["Page", "Sheet", "Heading read", "Entries", "Markers read", "Highest marker", "By order", "Count check"], krows) + [""]
    # S2.1
    s21 = next(r for r in sm if r["Page Key"] == "057")
    L += ["## S2.1, set p.57 (Test 4)", "",
          f"- No text layer. Tesseract words (both passes, deduplicated): {s21['OCR Words']}. Bluebeam words: {s21['Bluebeam Words']}.", ""]
    return L


def readme(out, pages, res):
    sizes = sorted(((f.stat().st_size, f.relative_to(out).as_posix()) for f in out.rglob("*") if f.is_file()
                    and f.name != "README.md"), reverse=True)
    info = extractor_info()
    L = ["# derived/ocr: drawing text for the Ledger and MTO cross-reference", "",
         f"Schema version {SCHEMA_VERSION}. Machine-read words, tags and quantities from the native Eastsound plan set "
         "(set pages 1–96) and the Addendum 4 reissue pages (pp.4–10), keyed so they can be cross-referenced into the "
         f"Project Ledger and a master MTO later. Built by `{SCRIPT_REL}` with no LLM calls. This "
         "folder is data only: nothing here has been entered in the Ledger or an MTO.", "",
         "## Confidence rule", "",
         "- A text-layer word from a native PDF counts as Verified.",
         "- A Tesseract or Bluebeam word is Inferred until confirmed on the page image, when it becomes Verified-Visual.",
         "- Nothing from this folder enters the Ledger or MTO without that confirmation and the owner's approval.",
         "- Every quantity is tagged Inferred (machine-read). It is a lead to check, not a takeoff.", "",
         "## Rebuild", "",
         "```",
         "apt-get install -y tesseract-ocr",
         "pip install -r requirements.txt",
         f"PYTHONHASHSEED=0 OMP_THREAD_LIMIT=1 python {SCRIPT_REL} --stage all --jobs 4",
         "```", "",
         "- The script sets both variables itself if they are missing. `--jobs` runs pages in parallel worker "
         "processes; outputs are sorted, so any job count gives the same bytes.",
         "- There are no timestamps, lists are sorted, boxes are rounded to 0.01 pt, JSON keys are sorted and line "
         "endings are LF. Byte-identical output also needs the same Tesseract build, `eng.traineddata` and CPU SIMD "
         "path. Each page file's `extractor` block records them.",
         "- Stages: `pages` (Step 1: words and title blocks, the slow part), `forms` (Tag_Search_Forms.csv), `hits` "
         "(Step 2), `report` (Findings.md, Spot_Check.csv, this README). `--crops <folder>` with `report` writes the "
         "spot-check crops. Keep that folder outside the repo: PNG is not a repo file type (AGENTS.md rule 5).", "",
         f"Recorded for this build: Python {info['python']}, PyMuPDF {info['pymupdf']}, pytesseract {info['pytesseract']}, "
         f"Pillow {info['pillow']}, {'; '.join(info['tesseract'])}, eng.traineddata SHA-256 {info['eng_traineddata_sha256']}.", "",
         "## Files", ""]
    L += md_table(["File", "What it holds"], [
        ["pages/NNN_<sheet>.json, pages/add4_pNN_<sheet>.json",
         "One per page: source file, SHA-256 and page, set page, 01 sheet and title, cited_as (plans_N copy from index/Plan_Set_Crosswalk.csv), "
         "governed_by / governs (Addendum 4), page size and rotation, counts, title block, words, bluebeam block, tags, "
         "quantities, keyed notes, extractor versions"],
        ["Sheet_Map.csv", "One row per page: 01 sheet vs title-block sheet read, titles, page N OF M, split-part file and "
                          "page, native file and page, Addendum 4 links, text-layer and OCR counts, mean confidence"],
        ["Tag_Search_Forms.csv", "One row per Ledger row: search forms, family, searchable, and the reasons and rules"],
        ["Tag_Hits.csv", "One row per tag occurrence, with its assignment under the Gate A rules"],
        ["Quantity_Hits.csv", "One row per quantity lead: value and unit as separate fields, nearest tag, keyed note"],
        ["Ledger_Crosswalk.csv", "One row per Ledger row (447), keyed on Ledger Row"],
        ["Unmatched_Tags.csv", "Tag-shaped text with no Ledger row: candidates for the PROPOSED-tag crosswalk, not Ledger items"],
        ["Findings.md", "Title mismatches, sheets found, known values, fence rows, crosswalk gaps, anchor levels, keyed notes"],
        ["Spot_Check.csv", "25 random words (5 each C, E, S, A, G) for a person to check on the page image"],
    ]) + [""]
    L += ["## Keys and coordinates", "",
          "- Join keys for the later Ledger and MTO step: Ledger Row, then sheet number, then set page. Ledger Row is the "
          "Project_Ledger.csv record number with the header as 1 (the same numbering as `ledger_to_graph.py`). The "
          "crosswalk is keyed on it, not on Tag, because \"SD-1\" and \"PROPOSED-Influent-Sampler\" each name two rows.",
          "- Quantities carry Value and Unit as separate fields, matching the Quantity and Unit columns proposed for "
          "Ledger schema rev1.",
          "- Boxes are PDF points on the page as displayed: origin top left, page rotation applied (set pp.62–96 are "
          "/Rotate 270), rounded to 0.01 pt.",
          "- Set page to native part comes from `library/Plan_Set_Parts.md`. cited_as (the plans_N copy the index files "
          "cite, with duplicate extracts listed) comes from `index/Plan_Set_Crosswalk.csv`; the run stops if the "
          "crosswalk's native part, page or sheet disagrees. The 01 sheet, title and Addendum 4 supersession come from "
          "`index/01_Sheet_Index_rev1.md`; Add. 4 pages cite the 01 page-level log.",
          "- Every native source's SHA-256 is checked against `index/Library_Manifest.csv` before any stage runs, "
          "and the run stops on a mismatch or a missing row.", "",
          "## How a page is read", "",
          "- Text layer: PyMuPDF `get_text(\"words\")`. The render mode comes from the character flags (neither filled "
          "nor stroked means mode 3, AutoCAD's overlay for text drawn as geometry). Mode-3 words count as text layer. "
          f"Words under {SUB_PT:.0f} pt in both directions are dropped and counted per page.",
          f"- OCR: every page is rendered at {DPI} dpi and read by Tesseract (`--oem {OEM} --psm {PSM}`, one thread), "
          "upright and rotated 90° with the boxes mapped back. Where the two passes read the same spot (overlap ≥ 0.5 "
          f"of the smaller box), the higher confidence is kept. Every word keeps its confidence; ≥ {CONF_FLAG} is a "
          "flag, not a filter. An OCR word on a text-layer word's spot is dropped: the text layer wins.",
          "- Bluebeam: the render-mode-3 words in the Bluebeam OCR copies, minus any word that matches a native word "
          "at the same spot. These go into Tag_Hits and Quantity_Hits as method `bluebeam-ocr`, Inferred (owner's "
          "decision, 2026-09-30).",
          "- Title block: the sheet-number word nearest the SHEET label closest to the bottom-right corner, with the "
          "page N OF M, date, title and revision read around it (no fixed coordinates, no assumed page total). Where "
          "the text layer has no title block, a rotated title-strip OCR pass (psm 11, 200 and 300 dpi, higher "
          "confidence per field) reads it instead, at any confidence.", "",
          "## Tag search and assignment (Gate A, 2026-09-30)", "",
          "- Search forms: trailing (...) and [...] are stripped, \"|\" aliases split and ranges expanded (F1–F4). "
          "Quotes and the spaces around # and - are dropped, word boundaries are kept, and an internal space matches "
          "0 or 1 space. Matching is case-insensitive. An OCR or Bluebeam match made through a 1/I, 0/O, 5/S, 8/B or "
          "#/H swap is marked fuzzy.",
          "- \"(E)\" is kept as a qualifier: a hit counts for an \"(E)\" row only when \"(E)\" or \"EXIST\" is on the "
          "same line; otherwise it counts for the unqualified row, or is not counted.",
          f"- Short forms ({SHORT_FORM_LEN} characters or fewer) count only on the row's cited sheets. Elsewhere they "
          "are listed as \"off-citation, short form\" and left out of the found counts.",
          "- A range row and its individual rows: the individual row takes the hit first, and the range row gets the "
          "rollup.",
          "- Shared forms: a hit goes to the row whose Lane matches the sheet's lane in 01, falling back to the "
          "discipline letter. If that doesn't settle it, every candidate row is listed and the hit is marked ambiguous.",
          "- PROPOSED rows are not searched by tag. Their Drawing Sheets anchors are checked instead (below). Pipe ID "
          "and Buried Valve ID rows match the legend line that starts with the ID number on C1.3 (base and Add. 4 "
          "p.7) and C1.4.", "",
          "## Quantities", "",
          "- Units: LF, SF, SY, CY, EA, LS, TON, GAL; FT is its own unit. Only L=nnn' converts to LF. Units may "
          "follow the number with no space (21LF).",
          "- A foot value followed by a material word is a dimension, not a quantity (6' CHAIN LINK). The material "
          "words are: " + ", ".join(sorted(DIM_MATERIAL)) + ".",
          "- Sizes: `8\"`, `12-in` and the like count only when a pipe, valve or conduit word follows within 4 words: "
          + ", ".join(sorted(PIPE_WORDS)) + ".",
          "- Counts: a number followed by a plural noun (12 BOLLARDS, (3) LOCATIONS), unit EA.",
          "- Slopes: n% counts as a slope after SLOPE or S=, or as \"@ n%\" after an LF quantity (39 LF @ 0.5%). "
          "Otherwise it is kind \"percent\". Also S=0.005 (FT/FT) and 2H:1V.",
          "- Elevations: RIM, SUMP, IE, INV, EL, ELEV, FG, FF, FFE, TOC, TOW, BOW, TOG, GRATE.",
          f"- Nearest tag: the nearest tag hit (assigned or ambiguous) within {NEAR_TAG_PT:.0f} pt, edge to edge, or "
          "\"none\". Calibration: every SDCB label on C2.1–C2.4 sits 0–13.1 pt from its RIM value.",
          "- Keyed notes: a quantity inside a keyed-note entry carries that entry's number, and the callouts of that "
          "number read on the plan.", "",
          "## Keyed notes", "",
          "- The block sits under a KEYED NOTES / KEY NOTES heading. Entries split on line spacing (a gap over 1.4 × "
          "the block's 25th-percentile spacing) or on a leading marker in the marker column.",
          "- A marker read by OCR sets the number when it is 1 or 2 past the previous entry's number (tagged at the "
          "marker's read level). Otherwise the entry takes the previous number + 1 (\"by order\", Inferred).",
          "- If a block's entry count differs from its highest marker read, its by-order numbers are Unresolved. A "
          "block with no marker read keeps Inferred and is flagged in Findings.", "",
          "## PROPOSED anchors", "",
          "- Verified: the anchor was found in the native text layer and its text holds the row's quantity, or a key "
          "noun from the Ledger Name. Inferred: the same match read by OCR or Bluebeam. Unresolved: the anchor was "
          "not found, or its text doesn't match. A row's level is its weakest anchor.",
          "- Sheet-only anchors (owner, 2026-09-30): a cited sheet with no KN, Det. or Add. anchor is Verified only "
          "when the row's quantity (value and unit) is read on that sheet in the text layer. A noun match anywhere on "
          "the sheet is Inferred, marked \"on sheet, location not pinned\".",
          "- Match term: when the Ledger Name has a quantity (value and unit, e.g. 149 LF, 7 ft), the anchor must "
          "hold that quantity; a noun is not enough. Only rows with no quantity use a noun, and only a specific one. "
          "The matched term is recorded in the crosswalk's Anchor Check column.",
          "- Anchor text by type: KN n → that keyed-note entry. Det. n → the detail's region, from its SCALE line up "
          "to the title row above and across to the next detail. Add. 4 p.N → that page. A sheet with no anchor → "
          "the whole sheet. Other anchors (Demo Schedule n, Item n, …) are Unresolved as not machine-checkable.",
          "- Key nouns: words of 4+ letters in the Ledger Name, plurals folded (a trailing S dropped), words ending "
          "in -ED dropped, and minus the two lists below. Please review both.",
          "", "Stopwords (never nouns): " + ", ".join(sorted(NOUN_STOP)) + ".", "",
          "Generic nouns (too common here to anchor a row): " + ", ".join(sorted(GENERIC_NOUNS)) + ".", "",
          "## Unmatched_Tags", "",
          "- Tag-shaped text that matches no Ledger form, exact or fuzzy, sheet numbers excluded. Shapes: "
          + "; ".join(f"{name} `{rx.pattern}`" for name, rx in UNMATCHED_SHAPES) + ".", "",
          "## Spot check", "",
          f"- Seed {SPOT_SEED}. {SPOT_PER} random words per discipline ({', '.join(SPOT_DISCIPLINES)}), drawn from each "
          "discipline's pages. The pool is every kept word of 2+ letters or digits: text layer, OCR and Bluebeam.",
          "- Columns follow Spot_Check_Schema (Pick No. to Note), then Set Page, BBox (pt), Word Read, Confidence and "
          "Crop Path. Ledger Row, Tag and Name are filled only when the word is part of an assigned tag hit.",
          "- Human Result, Checked By and Date stay blank. Only the owner marks a read Verified-Visual.",
          "- Crop Path is relative to the `--crops` folder. The crops are 400 dpi renders with the word boxed, and "
          "they are not committed.", "",
          "## Size", "",
          f"- Largest file: {sizes[0][1]} ({sizes[0][0] / 1e6:.1f} MB). No file passes 25 MB, so nothing is split.", ""]
    return L


def stage_report(out, res=None, crops=None):
    if res is None:
        res = stage_hits(out)
    pages = res["pages"]
    by_row = {r["row"]: r for r in res["rows"]}
    write_csv(out / "Spot_Check.csv", SPOT_HEADER, spot_check(pages, by_row, crops))
    for name, lines in (("Findings.md", findings(out, pages, res)), ("README.md", readme(out, pages, res))):
        with open(out / name, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines).rstrip("\n") + "\n")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["pages", "forms", "hits", "report", "all"], default="all")
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="output folder (default: derived/ocr)")
    ap.add_argument("--jobs", type=int, default=1, help="worker processes, one page each")
    ap.add_argument("--only", default="", help="comma list of page keys (e.g. 020,add4_p07); calibration only")
    ap.add_argument("--cache", default="", help="Tesseract result cache folder (development only)")
    ap.add_argument("--crops", default="", help="with --stage report or all: write spot-check crops here (outside the repo)")
    args = ap.parse_args()
    out = Path(args.out).resolve()
    only = [k.strip() for k in args.only.split(",") if k.strip()]
    verify_sources()
    if args.stage in ("pages", "all"):
        stage_pages(out, args.jobs, only, args.cache or None)
    if args.stage in ("forms", "all"):
        stage_forms(out)
    res = None
    if args.stage in ("hits", "all"):
        res = stage_hits(out)
    if args.stage in ("report", "all"):
        stage_report(out, res, args.crops or None)


if __name__ == "__main__":
    main()
