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
  PYTHONHASHSEED=0 OMP_THREAD_LIMIT=1 python tools/extract_drawing_text.py --stage all --jobs 4
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

REPO = Path(__file__).resolve().parent.parent
TB = REPO / "testbeds" / "eastsound"
LIB = TB / "library"
PARTS_NOTE = LIB / "Plan_Set_Parts.md"
ADD4_FILE = LIB / "addendum-no4-eswd.pdf"
BB_DIR = TB / "derived" / "bluebeam-ocr"
SHEET_INDEX = TB / "index" / "01_Sheet_Index_rev1.md"
LEDGER = TB / "project" / "02_Project_Ledger" / "Project_Ledger.csv"
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


def page_tasks(only=None):
    parts = load_parts()
    base, add4, addendum_only = load_sheet_index()
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
        cited_page = int(s["cited_page"]) if s["cited_page"].isdigit() else None
        tasks.append({
            "page_key": f"{sp:03d}", "set_page": sp, "sheet_01": s["sheet"],
            "title_01": s["title"], "discipline_01": s["discipline"],
            "native_file": str(f), "native_page": fp, "bluebeam": bb,
            "cited_as": {"file": s["cited_file"], "page": cited_page,
                         "basis": "01_Sheet_Index_rev1.md File and PDF p. columns"},
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
            "cited_as": {"file": ADD4_FILE.name, "page": n,
                         "basis": "01_Sheet_Index_rev1.md page-level log"},
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
        "script": "tools/extract_drawing_text.py",
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
            "source": {"file": rel(f), "sha256": sha256_file(f), "page": t["native_page"]},
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
NEAR_TAG_PT = 48.0      # nearest-tag search distance, edge to edge (Gate A)
SHEET_TOKEN_RE = re.compile(r"^([A-Z]{1,2}\d{1,2}\.\d{1,2}[A-Z]?)\s*(?:\(([^)]*)\))?\s*(.*)$")
SHORT_GENERIC = re.compile(r"^[A-Z]{1,3}$|^[A-Z]\d$")
LEGENDS = {  # Pipe ID and Buried Valve ID rows match a legend line that starts with the ID number
    "Pipe ID": ("PIPE IDENTIFICATION LEGEND", ("C1.3",)),
    "Buried Valve ID": ("BURIED VALVE IDENTIFICATION LEGEND", ("C1.4",)),
}
KEYED_HEAD_RE = re.compile(r"\bKEY(?:ED)?\s?NOTES?\b")
MARKER_RE = re.compile(r"^(?:=|\(?(\d{1,2})[.),]{0,2})$")
STRAY_RE = re.compile(r"^[-_\u2013\u2014|.,:;=~]+$")
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
Q_NUM = r"(?P<v>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
Q_PATTERNS = [
    ("length", "LF", re.compile(Q_NUM + r"\s?(?:L\.F\.|LF|LIN\.?\s?FT\.?)(?![A-Z])")),
    ("area", "SF", re.compile(Q_NUM + r"\s?(?:S\.F\.|SF|SQ\.?\s?FT\.?)(?![A-Z])")),
    ("area", "SY", re.compile(Q_NUM + r"\s?(?:S\.Y\.|SY|SQ\.?\s?YDS?\.?)(?![A-Z])")),
    ("volume", "CY", re.compile(Q_NUM + r"\s?(?:C\.Y\.|CY|CU\.?\s?YDS?\.?)(?![A-Z])")),
    ("count", "EA", re.compile(Q_NUM + r"\s?(?:EA\.?|EACH)(?![A-Z])")),
    ("lump sum", "LS", re.compile(Q_NUM + r"\s?(?:L\.S\.|LS)(?![A-Z])")),
    ("weight", "TON", re.compile(Q_NUM + r"\s?TONS?(?![A-Z])")),
    ("volume", "GAL", re.compile(Q_NUM + r"\s?(?:GAL\.?|GALLONS?)(?![A-Z])")),
    ("length", "LF", re.compile(r"(?<![A-Z0-9])L\s?=\s?" + Q_NUM + r"\s?(?:'|FT\.?|LF)?")),
    ("length", "FT", re.compile(Q_NUM + r"\s?(?:-\s?)?(?:FT\.?|FEET)(?![A-Z])")),
    ("size", "IN", re.compile(r"(?P<v>\d{1,2}(?:\.\d+)?(?:\s\d/\d)?|\d/\d)\s?(?:\"|''|-?IN\.?|-?INCH(?:ES)?)(?![A-Z0-9])"
                              r"(?P<rest>(?:\s?\(?[A-Z0-9./]+\)?){0,4})")),
    ("count", "EA", re.compile(r"(?<![A-Z0-9.,/-])\(?(?P<v>\d{1,3})\)?\s(?P<noun>[A-Z]{3,}S)(?![A-Z])")),
    ("slope", "%", re.compile(Q_NUM + r"\s?%")),
    ("slope", "FT/FT", re.compile(r"(?<![A-Z0-9])S\s?=\s?(?P<v>0?\.\d+)(?!\d)")),
    ("slope", "H:V", re.compile(r"(?<![0-9.])(?P<v>\d+(?:\.\d+)?\s?H\s?:\s?\d+(?:\.\d+)?\s?V)(?![A-Z])")),
    ("elevation", "FT", re.compile(r"(?<![A-Z0-9])(?P<k>RIM|I\.E\.|IE|INV(?:ERT)?\.?|ELEV\.?|EL\.?|FG|FF|FFE|TOC|TOW|BOW|TOG|GRATE)"
                                   r"\s?(?:\((?:IN|OUT|[NSEW]{1,2})\)\s?|(?:IN|OUT)\s)?[=:]?\s?(?P<v>\d{1,4}\.\d{1,2})(?!\d)")),
]


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
    t = tag
    while True:
        s = re.sub(r"\s*[\(\[][^\)\]]*[\)\]]\s*$", "", t).strip()
        if s == t:
            break
        t = s
    forms = []
    for alt in t.split("|"):
        alt = alt.strip()
        m = re.fullmatch(r"([A-Z]+)(\d+)\s*[–-]\s*(?:\1)?(\d+)", alt)
        if m:
            forms += [f"{m.group(1)}{n}" for n in range(int(m.group(2)), int(m.group(3)) + 1)]
        else:
            forms.append(alt)
    out = []
    for f in forms:
        f = norm_form(f)
        if f and f not in out:
            out.append(f)
    return out


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


def load_ledger():
    with open(LEDGER, encoding="utf-8-sig", newline="") as f:
        return [(i, r) for i, r in enumerate(csv.DictReader(f), start=2)]  # line 1 is the header


def build_forms():
    rows = []
    form_rows = defaultdict(list)
    for i, r in load_ledger():
        fam = family(r["Tag"])
        forms = printed_forms(r["Tag"]) if fam == "printed" else []
        for fm in forms:
            form_rows[fm].append(i)
        rows.append({"row": i, "tag": r["Tag"], "name": r["Name"], "family": fam, "forms": forms,
                     "sheets_field": r["Drawing Sheets"], "tokens": split_sheets(r["Drawing Sheets"]),
                     "level": r[TAG_LEVEL_COL]})
    for r in rows:
        reasons = []
        cited = [t for t in r["tokens"] if t[0]]
        if not r["tokens"]:
            reasons.append("no sheet cited")
        elif not cited:
            reasons.append("no sheet number cited: " + "; ".join(t[2] for t in r["tokens"]))
        if r["family"] == "printed":
            r["searchable"] = "Y"
            r["search"] = r["forms"]
            shared = sorted({j for fm in r["forms"] for j in form_rows[fm] if j != r["row"]})
            if shared:
                reasons.append("form shared with row(s) " + ", ".join(map(str, shared))
                               + "; hits count for every sharing row")
            if any(SHORT_GENERIC.match(fm) for fm in r["forms"]):
                reasons.append("short generic form; expect incidental hits in notes and legends")
            if any(" " in fm for fm in r["forms"]):
                reasons.append("internal space matches 0 or 1 space")
            reasons.insert(0, "printed tag; exact form in the text layer, OCR and Bluebeam; "
                              "1/I 0/O 5/S 8/B #/H swaps in OCR and Bluebeam marked fuzzy")
        elif r["family"] in LEGENDS:
            head, sheets = LEGENDS[r["family"]]
            n = r["tag"].rsplit(" ", 1)[1]
            r["searchable"] = "Y"
            r["search"] = [f"legend line starting '{n}' under '{head}' on {', '.join(sheets)} (base and Add. 4 reissue)"]
            reasons.insert(0, "ID number is not printed as a tag; matched in the legend")
        else:
            r["searchable"] = "N"
            r["search"] = [f"{t[0]} ({a})" for t in r["tokens"] if t[0] for a in (t[1] or ["sheet only"])]
            reasons.insert(0, "PROPOSED tag is not printed; the Drawing Sheets anchors are checked instead")
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


def find_tags(pg, comp, tag_of_row):
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
                                 rows=rows, ledger=[tag_of_row[x] for x in rows], bbox=union_box(ws),
                                 method=ln["method"], conf=min_conf(ws), fuzzy=fuzzy, kind="tag"))
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
                             form=f"{fam} {w['text']}", rows=[r["row"]], ledger=[r["tag"]],
                             bbox=union_box(ws), method=weakest_method(ws), conf=min_conf(ws),
                             fuzzy=False, kind="legend"))
    return dedupe_hits(hits)


METHOD_RANK = {"text-layer": 0, "ocr": 1, "bluebeam-ocr": 2}


def weakest_method(ws):
    return max((w["method"] for w in ws), key=lambda m: METHOD_RANK[m])


def keyed_notes(pg):
    """Keyed-note legend entries. Numbers sit in symbols OCR does not always read, so entries are
    split by line spacing (a gap over 1.4 x the block's 25th-percentile spacing) or a leading
    marker. An entry takes the number read in its marker when that number is 1 or 2 past the
    previous entry's; otherwise the previous number + 1 (basis "by order"; the read number is
    kept beside it)."""
    words = geo_page_words(pg)
    lines = geo_lines(words)
    heads = [ln for ln in lines if KEYED_HEAD_RE.search(norm_line(ln["text"])) and ln["dir"] == [1.0, 0.0]]
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
        med = sorted(gaps)[len(gaps) // 4] if gaps else 0
        # Entries start in the marker column (the leftmost row start); indented sub-items and
        # wrapped lines do not start an entry however they are spaced.
        firsts = [min(r, key=lambda ln: ln["bbox"][0])["words"][0] for r in text_rows]
        left = min((f["bbox"][0] for f in firsts), default=0.0)
        entries = []
        for k, r in enumerate(text_rows):
            first = firsts[k]
            in_col = first["bbox"][0] <= left + 6
            marker = MARKER_RE.match(first["text"]) if in_col else None
            start = k == 0 or (in_col and ((gaps and gaps[k - 1] > 1.4 * med) or bool(marker)))
            if start:
                entries.append({"lines": [], "top": row_y(r),
                                "read_number": marker.group(1) if marker and marker.group(1) else None})
            entries[-1]["lines"].extend(r)
        for ln in stray:  # a stray row joins the entry it sits in
            y = row_y([ln])
            host = [e for e in entries if e["top"] - 3 <= y]
            if host:
                host[-1]["lines"].append(ln)
        out = []
        n = 0
        for e in entries:
            # a read marker is trusted only when it runs on from the previous entry (misreads
            # such as "(1)" for 11 would otherwise restart the count)
            rd = int(e["read_number"]) if e["read_number"] else None
            n = rd if rd is not None and n < rd <= n + 2 else n + 1
            ws = [w for ln in e["lines"] for w in ln["words"]]
            out.append({"number": n, "read_number": e["read_number"], "bbox": union_box(ws),
                        "text": " / ".join(ln["text"] for ln in sorted(e["lines"], key=lambda ln: (ln["bbox"][1], ln["bbox"][0]))),
                        "method": weakest_method(ws)})
        blocks.append({"heading": hd["text"], "heading_bbox": hb, "heading_method": hd["method"],
                       "bbox": union_box([w for ln in block for w in ln["words"]] + hd["words"]),
                       "entries": out, "line_spacing_p25": r2(med)})
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
    """Detail title numbers: a 1-2 digit word with a SCALE line just to its right."""
    words = geo_page_words(pg)
    lines = geo_lines(words)
    scale = [ln for ln in lines if "SCALE" in norm_line(ln["text"])]
    out = []
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
        title = min(above, key=lambda ln: (sc["bbox"][1] - ln["bbox"][3], ln["bbox"]))["text"] if above else ""
        out.append({"n": w["text"], "bbox": w["bbox"], "title": title, "method": weakest_method([w] + sc["words"])})
    return out


def find_quantities(pg, tag_hits, blocks, callouts, drefs):
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
                if kind == "size":
                    rest = [t.strip("()") for t in m.group("rest").split()]
                    if not any(t in PIPE_WORDS for t in rest):
                        continue
                    b = m.start("rest") + len(m.group("rest").rstrip())
                    noun = " ".join(rest)
                if kind == "count" and "noun" in m.groupdict() and m.group("noun"):
                    noun = m.group("noun")
                if kind == "elevation":
                    noun = m.group("k")
                if kind == "slope" and unit == "%" and "SLOPE" not in s[max(0, a - 25):a] and "S=" not in s[max(0, a - 6):a]:
                    kind = "percent"
                ws = span_words(ln["words"], owner, a, b)
                if not ws:
                    continue
                taken.append((a, b))
                qs.append({"value": v.replace(",", ""), "unit": unit, "kind": kind, "item": noun,
                           "raw": s[a:b], "words": ws, "bbox": union_box(ws), "method": ln["method"],
                           "conf": min_conf(ws), "line_text": " ".join(w["text"] for w in ln["words"])})
    out = []
    for q in sorted(qs, key=lambda q: (q["bbox"], q["value"], q["unit"], q["method"], q["raw"])):
        if any(o["value"] == q["value"] and o["unit"] == q["unit"] and o["method"] == q["method"]
               and overlap_ratio(o["bbox"], q["bbox"]) >= OVERLAP for o in out[-20:]):
            continue
        near = sorted(((edge_dist(h["bbox"], q["bbox"]), h["form"], h["bbox"], h) for h in tag_hits
                       if edge_dist(h["bbox"], q["bbox"]) <= NEAR_TAG_PT), key=lambda x: x[:3])
        kn = None
        for blk in blocks:
            for e in blk["entries"]:
                cx, cy = center(q["bbox"])
                eb = e["bbox"]
                if eb[0] - 2 <= cx <= eb[2] + 2 and eb[1] - 2 <= cy <= eb[3] + 2:
                    kn = e
        co = []
        if kn:
            co = [c for c in callouts if c["n"] == str(kn["number"])]
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


TAG_HITS_HEADER = ["Tag Text", "Page Key", "Set Page", "Sheet", "BBox (pt)", "Method", "Confidence",
                   "Fuzzy (Y/N)", "Exact Ledger Match (Y/N)", "Search Form", "Ledger Rows", "Ledger Tags", "Hit Kind"]
QTY_HEADER = ["Value", "Unit", "Raw Text", "Page Key", "Set Page", "Sheet", "BBox (pt)", "Method", "Confidence",
              "Nearest Tag", "Distance (pt)", "Line Text", "Keyed Note", "Kind", "Item", "Nearest Tag Ledger Rows",
              "Keyed-Note Callouts", "Callouts Nearby", "Detail Refs Nearby", "Tag Level"]
XWALK_HEADER = ["Ledger Row", "Tag", "Family", "Searchable (Y/N)", "Ledger Drawing Sheets", "Cited Sheets",
                "Sheets Found On", "Sheets Cited but Not Found", "Sheets Found but Not Cited", "Anchor Check",
                "Quantities Seen", "Sheet Evidence Level", "Row Tag Level", "Status", "Notes"]
UNMATCHED_HEADER = ["Tag Text", "Shape", "Occurrences", "Page Keys", "Sheets", "Methods", "Max Confidence",
                    "First Page Key", "First BBox (pt)"]


def fmt_conf(c):
    return "" if c is None else f"{c:.2f}"


def sheet_pages(pages):
    by_sheet = defaultdict(list)
    for pg in pages:
        by_sheet[pg["sheet_01"]].append(pg["page_key"])
    return by_sheet


def anchor_check(sheet, anchor, pages_by_key, sheet_keys, facts):
    """One Drawing Sheets anchor on one sheet -> (result text, evidence level)."""
    keys = sheet_keys.get(sheet, [])
    if not keys:
        return f"{sheet}: sheet not in the set", "Unresolved"
    m = re.fullmatch(r"Add\. 4 p\.(\d+)", anchor)
    if m:
        k = f"add4_p{int(m.group(1)):02d}"
        pg = pages_by_key.get(k)
        if pg and pg["sheet_01"] == sheet:
            return f"{sheet} (Add. 4 p.{int(m.group(1))}): reissue page present ({k})", "Verified"
        return f"{sheet} (Add. 4 p.{int(m.group(1))}): no Add. 4 page for this sheet", "Unresolved"
    m = re.fullmatch(r"KN (\d+(?:\s*,\s*\d+)*)", anchor)
    if m:
        res, lv = [], []
        for n in [int(x) for x in re.findall(r"\d+", m.group(1))]:
            got = [(k, e, blk) for k in keys for blk in facts[k]["keyed"] for e in blk["entries"] if e["number"] == n]
            if got:
                k, e, blk = got[0]
                calls = [c for c in facts[k]["callouts"] if c["n"] == str(n)]
                res.append(f"{sheet} KN {n}: legend entry {n} of {len(blk['entries'])} by order "
                           f"({e['method']}, {k} {fmt_box(e['bbox'])}): \"{e['text'][:80]}\"; "
                           f"{len(calls)} callout(s) read")
                lv.append(method_level(e["method"]))
            else:
                n_blk = sum(len(b["entries"]) for k in keys for b in facts[k]["keyed"])
                res.append(f"{sheet} KN {n}: not found (keyed-note entries read: {n_blk})")
                lv.append("Unresolved")
        return "; ".join(res), weakest(lv)
    m = re.fullmatch(r"Det\. (\d+)(?:\s*[–-]\s*(\d+))?(?:,.*)?", anchor)
    if m:
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        nums = list(range(lo, hi + 1))
        extra = re.findall(r",\s*(\d+)$", anchor)
        nums += [int(x) for x in extra if int(x) not in nums]
        res, lv = [], []
        for n in nums:
            got = [(k, d) for k in keys for d in facts[k]["details"] if d["n"] == str(n)]
            if got:
                k, d = got[0]
                res.append(f"{sheet} Det. {n}: detail number read ({d['method']}, {k} {fmt_box(d['bbox'])})"
                           + (f" titled \"{d['title']}\"" if d["title"] else ""))
                lv.append(method_level(d["method"]))
            else:
                res.append(f"{sheet} Det. {n}: not found")
                lv.append("Unresolved")
        return "; ".join(res), weakest(lv)
    if re.fullmatch(r"[A-Z]{1,4}-\d+", anchor):
        got = [h for k in keys for h in facts[k]["tags"] if h["form"] == norm_form(anchor)]
        if got:
            h = min(got, key=lambda h: (METHOD_RANK[h["method"]], h["page_key"], h["bbox"]))
            return f"{sheet} ({anchor}): found ({h['method']}, {h['page_key']} {fmt_box(h['bbox'])})", method_level(h["method"])
        return f"{sheet} ({anchor}): not found", "Unresolved"
    return f"{sheet} ({anchor}): anchor type not machine-checkable", "Unresolved"


def crosswalk(rows, pages, facts, tag_hits, qty):
    pages_by_key = {pg["page_key"]: pg for pg in pages}
    sheet_keys = sheet_pages(pages)
    hits_by_row = defaultdict(list)
    for h in tag_hits:
        for r in h["rows"]:
            hits_by_row[r].append(h)
    q_by_row = defaultdict(list)
    for q in qty:
        if q["nearest_tag"]:
            for r in q["nearest_tag"]["rows"]:
                q_by_row[r].append(q)
    kn_q = defaultdict(list)   # (sheet, keyed note number) -> quantities in that entry
    for q in qty:
        if q["keyed_note"]:
            kn_q[(q["sheet"], q["keyed_note"]["number"])].append(q)
    out = []
    for r in rows:
        cited = []
        for s, anchors, raw in r["tokens"]:
            if s and s not in cited:
                cited.append(s)
        found = defaultdict(set)
        for h in hits_by_row[r["row"]]:
            found[h["sheet"]].add(h["method"] + (" fuzzy" if h["fuzzy"] else ""))
        anchors_txt, levels, notes = [], [], []
        qs = list(q_by_row[r["row"]])
        if r["family"] == "PROPOSED" or (r["family"] != "printed" and False):
            for s, anchors, raw in r["tokens"]:
                if not s:
                    continue
                if not anchors:
                    ok = s in sheet_keys
                    anchors_txt.append(f"{s}: sheet only; {'sheet in set' if ok else 'sheet not in set'}")
                    levels.append("Verified" if ok else "Unresolved")
                    continue
                for a in anchors:
                    txt, lv = anchor_check(s, a, pages_by_key, sheet_keys, facts)
                    anchors_txt.append(txt)
                    levels.append(lv)
                    for n in re.findall(r"\d+", a) if a.startswith("KN") else []:
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
        cited_nf = [s for s in cited if s not in found] if r["family"] != "PROPOSED" else []
        found_nc = [s for s in sorted(found, key=sheet_sort_key) if s not in cited]
        if r["family"] == "PROPOSED":
            found_txt = ""
        else:
            found_txt = "; ".join(f"{s} [{', '.join(sorted(found[s]))}]" for s in sorted(found, key=sheet_sort_key))
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
        if "form shared" in r["reason"]:
            notes.append(re.search(r"form shared with row\(s\) [\d, ]+", r["reason"]).group(0))
        out.append({"row": r["row"], "tag": r["tag"], "family": r["family"], "searchable": r["searchable"],
                    "sheets_field": r["sheets_field"], "cited": cited, "found": found_txt,
                    "cited_nf": cited_nf, "found_nc": found_nc, "anchors": anchors_txt, "qty": qtxt,
                    "sheet_level": sheet_level, "row_level": row_level, "status": status, "notes": notes})
    return out


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
    if rd and int(rd) == n:
        return f"{n} (read)"
    if rd:
        return f"{n} (by order; marker read as {rd})"
    return f"{n} (by order)"


def load_pages(out):
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted((out / "pages").glob("*.json"))]


def hit_json(h):
    return {"text": h["tag_text"], "form": h["form"], "ledger_rows": h["rows"], "bbox": h["bbox"],
            "method": h["method"], "conf": h["conf"], "fuzzy": h["fuzzy"], "kind": h["kind"],
            "tag_level": method_level(h["method"])}


def qty_json(q):
    return {"value": q["value"], "unit": q["unit"], "kind": q["kind"], "item": q["item"], "raw": q["raw"],
            "bbox": q["bbox"], "method": q["method"], "conf": q["conf"], "line_text": q["line_text"],
            "nearest_tag": q["nearest_tag"]["form"] if q["nearest_tag"] else "none",
            "nearest_tag_rows": q["nearest_tag"]["rows"] if q["nearest_tag"] else [],
            "distance": q["distance"],
            "keyed_note": q["keyed_note"]["number"] if q["keyed_note"] else None,
            "keyed_callouts": [c["bbox"] for c in q["keyed_callouts"]],
            "callouts_nearby": [[c[1], c[2], r2(c[0])] for c in q["near_callouts"]],
            "detail_refs_nearby": [[d[1], d[2], r2(d[0])] for d in q["near_detail_refs"]],
            "tag_level": "Inferred"}


def stage_hits(out):
    rows = build_forms()
    tag_of_row = {r["row"]: r["tag"] for r in rows}
    comp = compile_forms(rows)
    pages = load_pages(out)
    facts = {}
    all_tags, all_qty = [], []
    for pg in pages:
        tags = find_tags(pg, comp, tag_of_row) + find_legends(pg, rows)
        tags.sort(key=lambda h: (h["bbox"], h["form"], h["method"], h["tag_text"]))
        blocks = keyed_notes(pg)
        tb = pg.get("title_block") or {}
        exclude = [b["bbox"] for b in blocks]
        if tb.get("sheet_label_bbox"):
            lb = tb["sheet_label_bbox"]
            exclude.append([lb[0] - 20, 0.0, pg["page"]["width"], pg["page"]["height"]])
        callouts = isolated_numbers(pg, exclude)
        drefs = detail_refs(pg)
        qty = find_quantities(pg, tags, blocks, callouts, drefs)
        facts[pg["page_key"]] = {"tags": tags, "keyed": blocks, "callouts": callouts,
                                 "details": detail_titles(pg), "drefs": drefs}
        pg["tags"] = [hit_json(h) for h in tags]
        pg["quantities"] = [qty_json(q) for q in qty]
        pg["keyed_notes"] = blocks
        pg["extractor"] = extractor_info()
        write_json(out / "pages" / f"{pg['page_key']}_{pg['sheet_01']}.json", pg)
        all_tags += tags
        all_qty += qty
    write_csv(out / "Tag_Hits.csv", TAG_HITS_HEADER, [
        [h["tag_text"], h["page_key"], h["set_page"] or "", h["sheet"], fmt_box(h["bbox"]), h["method"],
         fmt_conf(h["conf"]), "Y" if h["fuzzy"] else "N", "N" if h["fuzzy"] else "Y", h["form"],
         "; ".join(map(str, h["rows"])), "; ".join(h["ledger"]), h["kind"]]
        for h in sorted(all_tags, key=lambda h: (h["page_key"], h["bbox"], h["form"], h["method"]))])
    write_csv(out / "Quantity_Hits.csv", QTY_HEADER, [
        [q["value"], q["unit"], q["raw"], q["page_key"], q["set_page"] or "", q["sheet"], fmt_box(q["bbox"]),
         q["method"], fmt_conf(q["conf"]), q["nearest_tag"]["form"] if q["nearest_tag"] else "none",
         "" if q["distance"] is None else f"{q['distance']:.2f}", q["line_text"],
         kn_label(q["keyed_note"]) if q["keyed_note"] else "",
         q["kind"], q["item"], "; ".join(map(str, q["nearest_tag"]["rows"])) if q["nearest_tag"] else "",
         "; ".join(fmt_box(c["bbox"]) for c in q["keyed_callouts"]),
         "; ".join(f"{c[1]} ({c[0]:.1f} pt)" for c in q["near_callouts"]),
         "; ".join(f"{d[1]} ({d[0]:.1f} pt)" for d in q["near_detail_refs"]), "Inferred"]
        for q in sorted(all_qty, key=lambda q: (q["page_key"], q["bbox"], q["value"], q["unit"], q["method"]))])
    xw = crosswalk(rows, pages, facts, all_tags, all_qty)
    write_csv(out / "Ledger_Crosswalk.csv", XWALK_HEADER, [
        [x["row"], x["tag"], x["family"], x["searchable"], x["sheets_field"], "; ".join(x["cited"]),
         x["found"], "; ".join(x["cited_nf"]), "; ".join(x["found_nc"]), " | ".join(x["anchors"]),
         "; ".join(x["qty"]), x["sheet_level"], x["row_level"], x["status"], "; ".join(x["notes"])]
        for x in xw])
    write_csv(out / "Unmatched_Tags.csv", UNMATCHED_HEADER, unmatched_tags(pages, comp))
    return {"rows": rows, "pages": pages, "facts": facts, "tags": all_tags, "qty": all_qty, "xwalk": xw}


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["pages", "forms", "hits", "all"], default="all")
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="output folder (default: derived/ocr)")
    ap.add_argument("--jobs", type=int, default=1, help="worker processes, one page each")
    ap.add_argument("--only", default="", help="comma list of page keys (e.g. 020,add4_p07); calibration only")
    ap.add_argument("--cache", default="", help="Tesseract result cache folder (development only)")
    args = ap.parse_args()
    out = Path(args.out).resolve()
    only = [k.strip() for k in args.only.split(",") if k.strip()]
    if args.stage in ("pages", "all"):
        stage_pages(out, args.jobs, only, args.cache or None)
    if args.stage in ("forms", "all"):
        stage_forms(out)
    if args.stage in ("hits", "all"):
        stage_hits(out)


if __name__ == "__main__":
    main()
