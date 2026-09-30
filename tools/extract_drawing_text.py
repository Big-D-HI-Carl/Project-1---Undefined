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
        rows, cur, cur_p = [], [], None
        for w in ws:
            p = sum(along(w["bbox"], down)) / 2
            t = max(w["size"], 1.0)
            if cur and abs(p - cur_p) > 0.6 * t:
                rows.append(cur)
                cur = []
            if not cur:
                cur_p = p
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


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["pages", "all"], default="all")
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="output folder (default: derived/ocr)")
    ap.add_argument("--jobs", type=int, default=1, help="worker processes, one page each")
    ap.add_argument("--only", default="", help="comma list of page keys (e.g. 020,add4_p07); calibration only")
    ap.add_argument("--cache", default="", help="Tesseract result cache folder (development only)")
    args = ap.parse_args()
    out = Path(args.out).resolve()
    only = [k.strip() for k in args.only.split(",") if k.strip()]
    if args.stage in ("pages", "all"):
        stage_pages(out, args.jobs, only, args.cache or None)


if __name__ == "__main__":
    main()
