#!/usr/bin/env python3
"""Repo checks: enforce the rules marked (checked) in AGENTS.md.

  python tools/checks.py --staged             staged changes (the pre-commit hook)
  python tools/checks.py --range BASE..HEAD   each commit in the range (CI)
  python tools/checks.py --all                whole tree, file-level checks only
  add --ci in CI: the data gate then reads only DATAGATE_TERMS (the repo secret)

Rules:
  read-only-sources  no change to a source under any library/ folder except .md
                     notes; a new source needs its Library_Manifest.csv row in
                     the same commit
  append-only-logs   PROGRESS_LOG.md, DECISIONS.md, ISSUES_LOG.md: additions only
  ledger             *Ledger*.csv under a test bed's project/ or lanes/ folder,
                     except Ledger_Schema.csv and *_by_CWP* views:
                     UTF-8 without BOM, the Ledger_Schema.csv (rev0) or
                     Ledger_Schema_rev1.csv header, full rows, non-empty Tag,
                     a valid tag word; with the rev1 header also a unique
                     Ledger ID in the L-NNNN form (Tags may repeat)
  unsafe-file        over 50 MB, secret-like names, anything under _inbox/ or
                     .datagate/
  data-gate          text files against the |-separated terms in DATAGATE_TERMS,
                     else the local .datagate/blocklist.txt (one term per line)
  exceptions         tools/check_exceptions.csv (Path, Rule, Issues Log Entry)
                     turns a listed path + rule into a warning; a new row needs
                     its ISSUES_LOG.md entry in the same commit

Output is one line per finding, "FAIL | rule | path | reason" or "WARN | ...",
then a summary line. Exit 1 on any FAIL, 2 on a usage or git error.
Findings never quote file contents, only line and column numbers: hook output
lands in the agent's context, and the data gate must never print a term.

Python 3.10+, standard library only.
"""

from __future__ import annotations

import argparse
import collections
import csv
import difflib
import fnmatch
import io
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
ZERO_OID = "0" * 40
LOGS = ("PROGRESS_LOG.md", "DECISIONS.md", "ISSUES_LOG.md")
ISSUES_LOG = "ISSUES_LOG.md"
MANIFEST = "testbeds/eastsound/index/Library_Manifest.csv"
SCHEMA = "testbeds/eastsound/index/Ledger_Schema.csv"
SCHEMA_REV1 = "testbeds/eastsound/index/Ledger_Schema_rev1.csv"
EXCEPTIONS = "tools/check_exceptions.csv"
EXCEPTIONS_HEADER = ["Path", "Rule", "Issues Log Entry"]
BLOCKLIST = ".datagate/blocklist.txt"
TERMS_VAR = "DATAGATE_TERMS"
MAX_BYTES = 50 * 1024 * 1024
UNSAFE_NAMES = (".env", ".env.*", "*.pem", "*.key", "id_rsa*", "*credential*")
UNSAFE_DIRS = ("_inbox", ".datagate")
TEXT_EXTS = (".md", ".csv", ".txt", ".json", ".py", ".yml", ".yaml")
LEDGER_SKIP = ("ledger_schema.csv", "*_by_cwp*.csv")  # the schema, and CWP views of a Ledger
TAG_COLUMN = "Verified/Verified-Visual/Inferred/Unresolved"
TAG_COLUMN_REV1 = "Confidence"
ID_COLUMN = "Ledger ID"
LEDGER_ID = re.compile(r"L-\d{4}")
TAG_WORD = re.compile(r"(Verified-Visual|Verified|Inferred|Unresolved)\b")
ISSUE_HEADING = re.compile(r"## \d{4}-\d{2}-\d{2} — (.+) — (?:Open|Closed)\s*")
RULES = ("read-only-sources", "append-only-logs", "ledger", "unsafe-file", "data-gate", "exceptions")
MAX_PER_FILE = 20  # findings of one rule shown per file; the rest are counted


class GitError(Exception):
    pass


class Git:
    """git plumbing, plus one long-running cat-file process for blob reads."""

    def __init__(self) -> None:
        self._cat: subprocess.Popen | None = None

    def run(self, *args: str, stdin: bytes | None = None) -> bytes:
        r = subprocess.run(["git", *args], input=stdin, capture_output=True)
        if r.returncode:
            msg = r.stderr.decode("utf-8", "replace").strip()
            raise GitError(f"git {' '.join(args)}: {msg}")
        return r.stdout

    def ok(self, *args: str) -> bool:
        return subprocess.run(["git", *args], capture_output=True).returncode == 0

    def read(self, name: str) -> bytes | None:
        """Blob content for an object name (id, 'rev:path' or ':path'); None if absent."""
        if self._cat is None:
            self._cat = subprocess.Popen(
                ["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE
            )
        assert self._cat.stdin and self._cat.stdout
        self._cat.stdin.write(name.encode("utf-8", "surrogateescape") + b"\n")
        self._cat.stdin.flush()
        parts = self._cat.stdout.readline().rstrip(b"\n").split(b" ")
        if len(parts) != 3 or not parts[2].isdigit():
            return None  # "<name> missing" or "<name> ambiguous"
        data = self._cat.stdout.read(int(parts[2]) + 1)[:-1]
        return data if parts[1] == b"blob" else None

    def sizes(self, oids: list[str]) -> dict[str, int]:
        if not oids:
            return {}
        out = self.run("cat-file", "--batch-check", stdin="".join(o + "\n" for o in oids).encode())
        result = {}
        for line in out.decode("ascii", "replace").splitlines():
            parts = line.split()
            if len(parts) == 3 and parts[2].isdigit():
                result[parts[0]] = int(parts[2])
        return result

    def close(self) -> None:
        if self._cat is not None:
            self._cat.stdin.close()  # type: ignore[union-attr]
            self._cat.wait()


class Report:
    def __init__(self) -> None:
        self.fails = 0
        self.warns = 0

    def line(self, level: str, rule: str, path: str, reason: str) -> None:
        print(f"{level} | {rule} | {path} | {reason}")

    def fail(self, rule: str, path: str, reason: str) -> None:
        self.fails += 1
        self.line("FAIL", rule, path, reason)

    def warn(self, rule: str, path: str, reason: str) -> None:
        self.warns += 1
        self.line("WARN", rule, path, reason)


@dataclass
class Change:
    status: str  # first letter of git's status: A C D M R T U X
    path: str  # the new path, or the removed path for D
    old_path: str | None  # the source path for R and C
    new_oid: str
    new_mode: str


@dataclass
class Unit:
    """One set of changes: the staged index, or one commit against its first parent."""

    label: str  # "" for staged, else a short commit id
    old_rev: str | None  # commit or tree to read old content from; None = nothing before
    new_rev: str  # ":" for the index, else a commit id
    changes: list[Change]


Finding = tuple[str, str, str]  # rule, path, reason


def decode_path(raw: bytes) -> str:
    return raw.decode("utf-8", "surrogateescape")


def parse_raw_diff(out: bytes) -> list[Change]:
    """Parse `git diff-* --raw -z` output."""
    parts = out.split(b"\0")
    changes = []
    i = 0
    while i < len(parts) and parts[i].startswith(b":"):
        _, new_mode, _, new_oid, status = parts[i][1:].decode("ascii").split(" ")
        letter = status[0]
        if letter in "RC":
            changes.append(Change(letter, decode_path(parts[i + 2]), decode_path(parts[i + 1]), new_oid, new_mode))
            i += 3
        else:
            changes.append(Change(letter, decode_path(parts[i + 1]), None, new_oid, new_mode))
            i += 2
    return changes


def read_at(git: Git, rev: str | None, path: str) -> bytes | None:
    if rev is None:
        return None
    return git.read(f":{path}" if rev == ":" else f"{rev}:{path}")


def new_content(git: Git, unit: Unit, change: Change) -> bytes:
    if change.new_oid != ZERO_OID:
        data = git.read(change.new_oid)
    else:
        data = read_at(git, unit.new_rev, change.path)
    return data or b""


def text_lines(data: bytes | None) -> list[str]:
    if not data:
        return []
    return [line.rstrip("\r") for line in data.decode("utf-8-sig", "replace").split("\n")]


def capped(findings: list[Finding]) -> list[Finding]:
    if len(findings) <= MAX_PER_FILE:
        return findings
    rule, path, _ = findings[0]
    more = len(findings) - MAX_PER_FILE
    return findings[:MAX_PER_FILE] + [(rule, path, f"{more} more findings of this kind not shown")]


# --- read-only-sources -------------------------------------------------------


def in_library(path: str) -> bool:
    return any(part.lower() == "library" for part in path.split("/")[:-1])


def is_source(path: str | None) -> bool:
    """A file under a library/ folder that is not a .md note."""
    return path is not None and in_library(path) and not path.lower().endswith(".md")


def manifest_paths(data: bytes | None) -> set[str]:
    if not data:
        return set()
    rows = csv.DictReader(io.StringIO(data.decode("utf-8-sig", "replace"), newline=""))
    return {(row.get("Path") or "").strip() for row in rows} - {""}


def check_read_only_sources(git: Git, unit: Unit) -> list[Finding]:
    rule = "read-only-sources"
    verbs = {"M": "modified", "D": "deleted", "T": "type changed", "U": "unmerged"}
    out: list[Finding] = []
    new_rows: set[str] | None = None
    for c in unit.changes:
        if c.status == "A":
            if is_source(c.path):
                if new_rows is None:
                    new_rows = manifest_paths(read_at(git, unit.new_rev, MANIFEST)) - manifest_paths(
                        read_at(git, unit.old_rev, MANIFEST)
                    )
                if c.path not in new_rows:
                    out.append((rule, c.path, f"new source without its row in {MANIFEST} in the same commit"))
        elif c.status == "R":
            if is_source(c.old_path):
                out.append((rule, str(c.old_path), f"renamed to {c.path}; library sources are read-only"))
            elif is_source(c.path):
                out.append((rule, c.path, f"renamed from {c.old_path}; add a source as a new file with its manifest row"))
        elif c.status == "C":
            if is_source(c.path):
                out.append((rule, c.path, f"copied from {c.old_path}; add a source as a new file with its manifest row"))
        elif is_source(c.path):
            out.append((rule, c.path, f"{verbs.get(c.status, 'changed')}; library sources are read-only"))
    return out


# --- append-only-logs --------------------------------------------------------


def first_removed_line(old: bytes, new: bytes) -> int | None:
    """1-based old line number of the first removed or changed line; None if new only adds lines."""
    old_lines = old.split(b"\n")
    new_lines = new.split(b"\n")
    j = 0
    for line in old_lines:  # greedy: is old a subsequence of new?
        try:
            j = new_lines.index(line, j) + 1
        except ValueError:
            break
    else:
        return None
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    for tag, i1, _, _, _ in matcher.get_opcodes():
        if tag in ("replace", "delete"):
            return i1 + 1
    return 1


def check_append_only_logs(git: Git, unit: Unit) -> list[Finding]:
    rule = "append-only-logs"
    out: list[Finding] = []
    for c in unit.changes:
        if c.status == "D" and c.path in LOGS:
            out.append((rule, c.path, "deleted; logs are append-only"))
        elif c.status == "R" and c.old_path in LOGS:
            out.append((rule, str(c.old_path), f"renamed to {c.path}; logs are append-only"))
        if c.path in LOGS and c.status in "AMTRC":
            old = read_at(git, unit.old_rev, c.path)
            if old is None:
                continue
            line = first_removed_line(old, new_content(git, unit, c))
            if line:
                out.append((rule, c.path, f"line {line} was removed or changed; add new entries at the end"))
    return out


# --- ledger ------------------------------------------------------------------


def is_ledger(path: str) -> bool:
    """A Project or lane Ledger: *ledger*.csv under testbeds/<bed>/project/ or lanes/,
    except the LEDGER_SKIP names. Other files that carry "Ledger" in their name (a
    crosswalk keyed on Ledger rows, for example) are not Ledgers."""
    parts = path.lower().split("/")
    if len(parts) < 4 or parts[0] != "testbeds" or parts[2] not in ("project", "lanes"):
        return False
    name = parts[-1]
    return fnmatch.fnmatchcase(name, "*ledger*.csv") and not any(fnmatch.fnmatchcase(name, p) for p in LEDGER_SKIP)


def schema_header(data: bytes | None) -> list[str] | None:
    if data is None:
        return None
    return next(csv.reader(io.StringIO(data.decode("utf-8-sig", "replace"), newline="")), [])


def header_difference(header: list[str], schema: list[str], name: str = "Ledger_Schema.csv") -> str:
    column = next((i for i, (a, b) in enumerate(zip(header, schema)) if a != b), min(len(header), len(schema)))
    expected = f"'{schema[column]}'" if column < len(schema) else "no column"
    counts = f"{len(header)} columns vs {len(schema)}, " if len(header) != len(schema) else ""
    return f"header differs from {name}: {counts}first difference at column {column + 1} (schema has {expected})"


def check_ledger(path: str, data: bytes, schema: list[str], schema_rev1: list[str] | None = None) -> list[Finding]:
    """rev0 header: non-empty Tag. rev1 header: unique Ledger ID (L-NNNN) and non-empty Tag; Tags may repeat
    (decision A: everything links by Ledger ID)."""
    rule = "ledger"
    out: list[Finding] = []
    if data.startswith(b"\xef\xbb\xbf"):
        out.append((rule, path, "starts with a UTF-8 BOM; save as UTF-8 without BOM"))
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        return out + [(rule, path, f"not valid UTF-8 (byte {e.start})")]
    reader = csv.reader(io.StringIO(text, newline=""))
    rows: list[Finding] = []
    try:
        header = next(reader, None)
        if header is None:
            return out + [(rule, path, "empty; needs the Ledger_Schema.csv header")]
        rev1 = schema_rev1 is not None and header == schema_rev1
        if header != schema and not rev1:
            if schema_rev1 is not None and header[:1] == [ID_COLUMN]:
                out.append((rule, path, header_difference(header, schema_rev1, "Ledger_Schema_rev1.csv")))
            else:
                out.append((rule, path, header_difference(header, schema)))
        width = len(header)
        tag_i = header.index("Tag") if "Tag" in header else None
        word_col = TAG_COLUMN_REV1 if rev1 else TAG_COLUMN
        word_i = header.index(word_col) if word_col in header else None
        id_i = header.index(ID_COLUMN) if rev1 else None
        seen: dict[str, int] = {}
        start = reader.line_num + 1
        for row in reader:
            line, start = start, reader.line_num + 1
            if len(row) != width:
                rows.append((rule, path, f"line {line}: {len(row)} fields, header has {width}"))
                continue
            if tag_i is not None and not row[tag_i].strip():
                rows.append((rule, path, f"line {line}: Tag is empty"))
            if id_i is not None:
                lid = row[id_i].strip()
                if not LEDGER_ID.fullmatch(lid):
                    rows.append((rule, path, f"line {line}: Ledger ID must be L- and four digits"))
                elif lid in seen:
                    rows.append((rule, path, f"line {line}: Ledger ID duplicates line {seen[lid]}"))
                else:
                    seen[lid] = line
            if word_i is not None and not TAG_WORD.match(row[word_i].strip()):
                rows.append((rule, path, f"line {line}: tag column must start with Verified, Verified-Visual, Inferred or Unresolved"))
    except csv.Error:
        rows.append((rule, path, f"line {reader.line_num}: CSV parse error"))
    return out + capped(rows)


# --- unsafe-file -------------------------------------------------------------


def check_unsafe_file(path: str, size: int | None) -> list[Finding]:
    rule = "unsafe-file"
    out: list[Finding] = []
    parts = path.split("/")
    folder = next((p for p in parts[:-1] if p.lower() in UNSAFE_DIRS), None)
    if folder:
        out.append((rule, path, f"under {folder}/, which is never committed"))
    name = parts[-1].lower()
    pattern = next((p for p in UNSAFE_NAMES if fnmatch.fnmatchcase(name, p)), None)
    if pattern:
        out.append((rule, path, f"name matches '{pattern}'; no credentials or keys in the repo"))
    if size is not None and size > MAX_BYTES:
        out.append((rule, path, f"{size / 1024 / 1024:.1f} MB; the limit is 50 MB"))
    return out


# --- data-gate ---------------------------------------------------------------


def load_terms(ci: bool, report: Report) -> list[tuple[str, str]]:
    """(entry label, casefolded term) pairs; terms are never printed.

    DATAGATE_TERMS wins; the local blocklist file is the fallback. In CI (--ci)
    only the variable counts, set from the repository secret.
    """
    value = os.environ.get(TERMS_VAR, "")
    if value.strip():
        source, entries = TERMS_VAR, list(enumerate(value.split("|"), 1))
    elif ci:
        report.warn("data-gate", TERMS_VAR, "secret not set for this run; data gate not run")
        return []
    else:
        try:
            with open(BLOCKLIST, "rb") as f:
                lines = f.read().decode("utf-8-sig", "replace").splitlines()
        except FileNotFoundError:
            report.warn("data-gate", BLOCKLIST, f"no {TERMS_VAR} and no blocklist file; data gate not run")
            return []
        source = BLOCKLIST
        entries = [(n, s) for n, s in enumerate(lines, 1) if not s.strip().startswith("#")]
    terms = [(f"{source} entry {n}", s.strip().casefold()) for n, s in entries if s.strip()]
    if not terms:
        report.warn("data-gate", source, "no terms; data gate not run")
    return terms


def is_text(path: str) -> bool:
    return path.lower().endswith(TEXT_EXTS)


def check_data_gate(path: str, data: bytes, terms: list[tuple[str, str]]) -> list[Finding]:
    out: list[Finding] = []
    for n, line in enumerate(data.decode("utf-8", "replace").casefold().split("\n"), 1):
        entry = next((label for label, term in terms if term in line), None)
        if entry is not None:
            out.append(("data-gate", path, f"line {n} matches {entry} (term not shown)"))
    return capped(out)


# --- exceptions --------------------------------------------------------------


def parse_exceptions(data: bytes | None) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Valid (path, rule, title) rows, and format problems."""
    if data is None:
        return [], []
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return [], ["not valid UTF-8"]
    reader = csv.reader(io.StringIO(text, newline=""))
    if next(reader, None) != EXCEPTIONS_HEADER:
        return [], [f"header must be {','.join(EXCEPTIONS_HEADER)}"]
    rows, problems = [], []
    allowed = [r for r in RULES if r != "exceptions"]
    for row in reader:
        n = reader.line_num
        if len(row) != 3:
            problems.append(f"line {n}: {len(row)} fields, expected 3")
            continue
        path, rule, title = (cell.strip() for cell in row)
        if rule not in allowed:
            problems.append(f"line {n}: rule must be one of {', '.join(allowed)}")
        elif not path or not title:
            problems.append(f"line {n}: Path and Issues Log Entry are required")
        else:
            rows.append((path, rule, title))
    return rows, problems


def issue_titles(lines) -> set[str]:
    """Titles of ISSUES_LOG.md headings; the full heading text also counts."""
    titles = set()
    for line in lines:
        m = ISSUE_HEADING.fullmatch(line)
        if m:
            titles.update({m.group(1).strip(), line[3:].strip()})
    return titles


def check_exceptions_added(git: Git, unit: Unit) -> list[Finding]:
    rule = "exceptions"
    if not any(c.path == EXCEPTIONS and c.status != "D" for c in unit.changes):
        return []
    new_rows, problems = parse_exceptions(read_at(git, unit.new_rev, EXCEPTIONS))
    out: list[Finding] = [(rule, EXCEPTIONS, p) for p in problems]
    old_rows = set(parse_exceptions(read_at(git, unit.old_rev, EXCEPTIONS))[0])
    added = [row for row in new_rows if row not in old_rows]
    if added:
        old_log = collections.Counter(text_lines(read_at(git, unit.old_rev, ISSUES_LOG)))
        new_log = collections.Counter(text_lines(read_at(git, unit.new_rev, ISSUES_LOG)))
        titles = issue_titles((new_log - old_log).elements())
        for path, excepted, title in added:
            if title not in titles:
                out.append((rule, EXCEPTIONS, f"row for {path} ({excepted}) needs the ISSUES_LOG.md entry '{title}' added in the same commit"))
    return out


def emit(findings: list[Finding], excepted: set[tuple[str, str]], report: Report, where: str = "") -> None:
    for rule, path, reason in findings:
        if where:
            reason = f"{reason} [commit {where}]"
        if rule != "exceptions" and (path, rule) in excepted:
            report.warn(rule, path, f"listed in {EXCEPTIONS}: {reason}")
        else:
            report.fail(rule, path, reason)


# --- modes -------------------------------------------------------------------


def check_unit(git: Git, unit: Unit, terms: list[tuple[str, str]], report: Report) -> None:
    findings = check_read_only_sources(git, unit) + check_append_only_logs(git, unit)
    touched = [c for c in unit.changes if c.status not in "DU" and c.new_mode != "160000"]
    sizes = git.sizes([c.new_oid for c in touched if c.new_oid != ZERO_OID])
    schema: list[str] | None = None
    schema_rev1: list[str] | None = None
    schema_read = False
    for c in touched:
        findings += check_unsafe_file(c.path, sizes.get(c.new_oid))
        if c.new_mode == "120000":
            continue  # symlink: the blob is a link target, not file content
        if is_ledger(c.path):
            if not schema_read:
                schema, schema_read = schema_header(read_at(git, unit.new_rev, SCHEMA)), True
                schema_rev1 = schema_header(read_at(git, unit.new_rev, SCHEMA_REV1))
                if schema is None:
                    report.warn("ledger", SCHEMA, "schema not in the repo; ledger checks skipped")
            if schema is not None:
                findings += check_ledger(c.path, new_content(git, unit, c), schema, schema_rev1)
        if terms and is_text(c.path):
            findings += check_data_gate(c.path, new_content(git, unit, c), terms)
    findings += check_exceptions_added(git, unit)
    rows, _ = parse_exceptions(read_at(git, unit.new_rev, EXCEPTIONS))
    emit(findings, {(path, rule) for path, rule, _ in rows}, report, unit.label)


def staged_unit(git: Git) -> Unit:
    head = None
    if git.ok("rev-parse", "--verify", "-q", "HEAD"):  # no HEAD before the first commit
        head = git.run("rev-parse", "HEAD").decode().strip()
    out = git.run("diff-index", "--cached", "--raw", "-z", "-M", "-C", "--no-abbrev", head or EMPTY_TREE)
    return Unit("", head, ":", parse_raw_diff(out))


def range_units(git: Git, spec: str):
    base, sep, head = spec.partition("..")
    if not sep or not base or not head or head.startswith("."):
        raise GitError(f"--range needs BASE..HEAD, got '{spec}'")
    for commit in git.run("rev-list", "--reverse", f"{base}..{head}").decode().split():
        parents = git.run("rev-list", "--parents", "-n", "1", commit).decode().split()[1:]
        parent = parents[0] if parents else None
        out = git.run("diff-tree", "-r", "--raw", "-z", "-M", "-C", "--no-abbrev", parent or EMPTY_TREE, commit)
        yield Unit(commit[:7], parent, commit, parse_raw_diff(out))


def check_all(git: Git, terms: list[tuple[str, str]], report: Report) -> None:
    findings: list[Finding] = []
    paths = dict.fromkeys(p for p in decode_path(git.run("ls-files", "-z")).split("\0") if p)
    try:
        with open(SCHEMA, "rb") as f:
            schema = schema_header(f.read())
    except FileNotFoundError:
        schema = None
        report.warn("ledger", SCHEMA, "schema not in the repo; ledger checks skipped")
    try:
        with open(SCHEMA_REV1, "rb") as f:
            schema_rev1 = schema_header(f.read())
    except FileNotFoundError:
        schema_rev1 = None
    for path in paths:
        try:
            st = os.lstat(path)
        except FileNotFoundError:
            continue  # tracked but deleted in the working copy
        findings += check_unsafe_file(path, st.st_size)
        want_ledger = schema is not None and is_ledger(path)
        want_gate = bool(terms) and is_text(path)
        if not stat.S_ISREG(st.st_mode) or not (want_ledger or want_gate):
            continue
        with open(path, "rb") as f:
            data = f.read()
        if want_ledger:
            findings += check_ledger(path, data, schema, schema_rev1)  # type: ignore[arg-type]
        if want_gate:
            findings += check_data_gate(path, data, terms)
    try:
        with open(EXCEPTIONS, "rb") as f:
            rows, problems = parse_exceptions(f.read())
    except FileNotFoundError:
        rows, problems = [], []
    findings += [("exceptions", EXCEPTIONS, p) for p in problems]
    try:
        with open(ISSUES_LOG, "rb") as f:
            titles = issue_titles(text_lines(f.read()))
    except FileNotFoundError:
        titles = set()
    for path, rule, title in rows:
        if title not in titles:
            findings.append(("exceptions", EXCEPTIONS, f"row for {path} ({rule}): no ISSUES_LOG.md entry '{title}'"))
    emit(findings, {(path, rule) for path, rule, _ in rows}, report)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Enforce the rules marked (checked) in AGENTS.md.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--staged", action="store_true", help="staged changes (pre-commit hook)")
    mode.add_argument("--range", metavar="BASE..HEAD", help="each commit in the range (CI)")
    mode.add_argument("--all", action="store_true", help="whole tree, file-level checks only")
    parser.add_argument("--ci", action="store_true", help="CI: the data gate reads only DATAGATE_TERMS")
    args = parser.parse_args(argv)
    try:
        sys.stdout.reconfigure(errors="backslashreplace")  # type: ignore[union-attr]
    except AttributeError:
        pass

    git = Git()
    report = Report()
    label = "--all" if args.all else "--staged" if args.staged else f"--range {args.range}"
    try:
        os.chdir(git.run("rev-parse", "--show-toplevel").decode().strip())
        terms = load_terms(args.ci, report)
        if args.all:
            check_all(git, terms, report)
        elif args.staged:
            check_unit(git, staged_unit(git), terms, report)
        else:
            units = 0
            for unit in range_units(git, args.range):
                units += 1
                check_unit(git, unit, terms, report)
            if not units:
                report.line("NOTE", "range", "-", "no commits in range")
    except GitError as e:
        print(f"ERROR | git | - | {e}")
        return 2
    finally:
        git.close()
    print(f"checks.py {label}: {report.fails} FAIL, {report.warns} WARN")
    return 1 if report.fails else 0


if __name__ == "__main__":
    sys.exit(main())
