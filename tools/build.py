#!/usr/bin/env python3
"""Build step: Pandoc render and the evidence pack (SETUP-INSTRUCTIONS 8).

Runs tools/generate.py, then renders build/md/catalogue-full.md with Pandoc to

    build/out/catalogue.html    standalone, table of contents, anchored IDs
    build/out/catalogue.pdf     --pdf-engine=typst
    build/out/catalogue.docx

and builds the evidence pack, build/out/evidence-pack.md and .html: exactly
one section per T-/C-/F-ID (128 + 166 + 53 = 347), each carrying its claim
record, its references with tier, URL and snapshot status, and every
change-log row mentioning the ID.

Anchor strategy (SETUP 8: "every ID an anchor ... so specs can deep-link").
A Lua filter, written to build/pandoc/anchors.lua at run time and passed to
Pandoc via --lua-filter, wraps the leading ID token of the first cell of
every data row in a table whose first header cell is "ID" (the area Threats
and Controls tables), "F-ID" (Appendix A) or "R-ID" (Appendix B) in a span
carrying that ID as its HTML id:

    <span id="C-A3-1">C-A3-1</span> · 1.0.0-beta.1

One anchor per ID, at its defining row. Every other occurrence of an ID
(Addresses cells, the Baseline-and-conditional summary, Compliance mapping,
Where experts differ, prose) stays plain text, so no id is duplicated and
the anchor audit is exact: 294 T/C anchors (128 + 166), 53 F anchors and
144 R anchors in the appendices. Other tables are left untouched because
their first header cell is not an ID header ("Job", "Signal", "Method",
"Feature", "Area", "Regime", "Topic"); the filter keys on the header cell,
never on cell content.

Determinism. All five outputs are pure functions of the corpus and the
stamp inputs (version, UTC build date, commit). Pandoc and Typst honour
SOURCE_DATE_EPOCH; this script derives it from the stamp's build date (UTC
midnight of that date) — the same value that already enters the outputs as
the stamp, so no new non-content input. Without it, DOCX embeds the wall
clock twice (docProps/core.xml created/modified and the zip entry times)
and Typst embeds it in the PDF CreationDate/ModDate; with it, two builds
under the same stamp are byte-identical (stage 8's determinism gate). This
is the reading of SETUP 8's build determinism recorded in IMPORT-NOTES.

Pandoc input format is markdown with the citations extension disabled
(-f markdown-citations). The corpus carries a literal @-mention (the npm
scope "@tanstack" in F-37's value and claim); the citations extension
parses it as a citation, which the typst writer then emits as #cite() and
typst rejects (no bibliography). SETUP 2 says export @-names are plain
text, so disabling the extension restores the literal reading; content is
untouched and every writer (HTML, DOCX, PDF) receives the same tokens.

Change-log "mention" rule (evidence pack and extract --since). A
change-log row mentions an ID when the ID appears as a token anywhere in
the row (all six cells joined) after expanding ranges: same-prefix
"X to Y" ranges via check.py's expand_id_ranges, plus the one mixed-prefix
range the export carries ("T-B2-1 to C-B2-6", spanning the threat and
control families of one area), which expands to that area's existing
threats numbered >= the start number and controls numbered <= the end
number. The reading is recorded in IMPORT-NOTES.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402  (tools/check.py — Corpus and ID helpers)

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
MD = BUILD / "md"
AI = BUILD / "ai"
OUT = BUILD / "out"
PANDOC_DIR = BUILD / "pandoc"

# The anchor filter body. Kept as source here and written to build/pandoc/
# at run time: stage 8's file set is exactly tools/build.py, tools/extract.py
# and reviews/example-checklist.yaml (stage-8 brief, gate 7), so no third
# helper file is shipped. cell.contents is the pandoc 3 cell accessor;
# cell.blocks is the older name, kept for the same reason the filter checks
# both body.head and body.body.
ANCHORS_LUA = r"""-- build.py anchor filter: one span#ID per defining ID cell.
-- Keys on the table's first header cell: "ID" (threats/controls tables),
-- "F-ID" (Appendix A), "R-ID" (Appendix B). Every other table is passed
-- through unchanged.
local PATTERNS = {
  ID = "^[TC]%-[ABP]%d+%-%d+$",
  ["F-ID"] = "^F%-%d+$",
  ["R-ID"] = "^R%-%d+$",
}

local function cell_blocks(cell)
  if cell.contents ~= nil then return cell.contents end
  return cell.blocks
end

local function plain_text(blocks)
  local parts = {}
  local function walk_inlines(inlines)
    for _, il in ipairs(inlines) do
      if il.t == "Str" or il.t == "Code" then
        parts[#parts + 1] = il.text
      elseif il.t == "Space" or il.t == "SoftBreak" then
        parts[#parts + 1] = " "
      end
    end
  end
  for _, b in ipairs(blocks) do
    if b.t == "Plain" or b.t == "Para" then walk_inlines(b.content) end
  end
  return table.concat(parts)
end

local function anchor_cell(cell, pattern)
  local blocks = cell_blocks(cell)
  for _, b in ipairs(blocks) do
    if b.t == "Plain" or b.t == "Para" then
      for i, il in ipairs(b.content) do
        if il.t == "Str" and il.text:find(pattern) then
          b.content[i] = pandoc.Span({ pandoc.Str(il.text) },
                                     pandoc.Attr(il.text, {}, {}))
          return true
        end
      end
    end
  end
  return false
end

local function anchor_rows(rows, pattern)
  for _, row in ipairs(rows) do
    local cell = row.cells[1]
    if cell then anchor_cell(cell, pattern) end
  end
end

function Table(el)
  local head = el.head
  if head == nil or #head.rows == 0 then return el end
  local first = head.rows[1].cells[1]
  if first == nil then return el end
  local pattern = PATTERNS[plain_text(cell_blocks(first))]
  if pattern == nil then return el end
  for _, body in ipairs(el.bodies) do
    anchor_rows(body.head or {}, pattern)
    anchor_rows(body.body or body.rows or {}, pattern)
  end
  return el
end
"""

# The mixed-prefix range the export's change log carries: "T-B2-1 to C-B2-6".
# Same area (backreference), different [TC] family.
MIXED_RANGE = re.compile(
    r"\b([TC])-([ABP]\d{1,2})-(\d+)\s+to\s+([TC])-\2-(\d+)\b"
)


# --------------------------------------------------------------------------
# small helpers (shared with extract.py by import)
# --------------------------------------------------------------------------

def cell(text) -> str:
    """A table cell must hold one line and no pipe, or it cannot be rendered
    faithfully (generate.py applies the same rule to its own cells)."""
    if text is None:
        return "—"
    text = str(text)
    if "|" in text or "\n" in text:
        raise SystemExit(
            f"cannot render faithfully: table cell contains a newline or "
            f"pipe: {text[:80]!r}")
    return text


def iso_date(value) -> str:
    return value.isoformat() if isinstance(value, (_dt.date, _dt.datetime)) else str(value)


def markdown_table(header: list, rows: list) -> str:
    """A Markdown table from header and row cell lists."""
    lines = ["| " + " | ".join(cell(c) for c in header) + " |",
             "| " + " | ".join("---" for _ in header) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(cell(c) for c in row) + " |")
    return "\n".join(lines)


def source_date_epoch(built: str) -> str:
    """SOURCE_DATE_EPOCH = UTC midnight of the stamp's build date, the same
    date that already enters every output as the stamp line."""
    day = _dt.datetime.strptime(built, "%Y-%m-%d").replace(
        tzinfo=_dt.timezone.utc)
    return str(int(day.timestamp()))


def pandoc_env(built: str) -> dict:
    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = source_date_epoch(built)
    return env


VERSION_RE = re.compile(r"^[vV]?(\d+(?:\.\d+)*)(?:-([0-9A-Za-z.-]+))?"
                        r"(?:\+[0-9A-Za-z.-]+)?$")


def _prerelease_key(pre: str) -> tuple:
    """Semver precedence for the pre-release segment: identifiers separated
    by ".", numeric identifiers compared numerically (and lower than
    alphanumeric ones), otherwise ASCII-lexically; a longer list ranks above
    its own prefix (semver §11: 1.0.0-alpha.1 > 1.0.0-alpha)."""
    parts = []
    for identifier in pre.split("."):
        if identifier.isdigit():
            parts.append((0, 0, int(identifier)))
        else:
            parts.append((1, identifier, ""))
    return tuple(parts)


def version_key(version: str) -> tuple:
    """Total order over version strings, semver precedence (SETUP 8,
    --since): numeric components compared element-wise with zero padding for
    a shorter tuple; a pre-release sorts below its own release; build
    metadata (+...) ignored; an optional leading v/V accepted. Strict
    inequality is what --since uses ("later than")."""
    match = VERSION_RE.match(version.strip())
    if not match:
        raise SystemExit(f"cannot parse version {version!r} "
                         "(expected [v]MAJOR[.MINOR[.PATCH]][-pre][+build])")
    numbers = tuple(int(n) for n in match.group(1).split("."))
    pre = match.group(2)
    # is_release sorts a plain release (1) above any pre-release (0) of the
    # same numbers; the pre key only matters between two pre-releases.
    return (numbers, 1, ()) if pre is None else (numbers, 0, _prerelease_key(pre))


def stamp_line(meta: dict) -> str:
    return (f"Catalogue version {meta['version']}, built {meta['built']} "
            f"from commit {meta['commit']}")


def load_build_meta() -> dict:
    """The version stamp of the current build (build/ai/catalogue.json meta)."""
    path = AI / "catalogue.json"
    if not path.exists():
        raise SystemExit("build/ai/catalogue.json is missing — run "
                         "tools/build.py (or tools/generate.py) first")
    return json.loads(path.read_text(encoding="utf-8"))["meta"]


def catalogue_manifest() -> dict:
    manifests = sorted((ROOT / "catalogues").glob("*.yaml"))
    if len(manifests) != 1:
        raise SystemExit(f"expected exactly one catalogue manifest, found "
                         f"{[m.name for m in manifests]}")
    return yaml.safe_load(manifests[0].read_text(encoding="utf-8"))


# -- change log ------------------------------------------------------------

def parse_change_log() -> list[list[str]]:
    """The merged change-log table as verbatim cell lists, newest first as
    stored (register/change-log.md, SETUP 4.8)."""
    rows = []
    for line in (ROOT / "register" / "change-log.md").read_text(
            encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "Date" or set(cells[0]) <= {"-", " "}:
            continue  # header or separator
        if len(cells) != 6:
            raise SystemExit(f"change-log row does not have 6 cells: {line[:80]!r}")
        rows.append(cells)
    return rows


def expand_mentions(text: str, corpus: check.Corpus) -> set:
    """Every ID token in text, with same-prefix "X to Y" ranges expanded
    (check.py's helper) and the mixed threat-to-control family range
    expanded to the area's threats numbered >= start and controls numbered
    <= end, intersected with the corpus (recorded in IMPORT-NOTES)."""

    def repl(match):
        start_kind, area, start_n, end_kind, end_n = (
            match.group(1), match.group(2), int(match.group(3)),
            match.group(4), int(match.group(5)))
        if start_kind == end_kind:
            return match.group(0)  # same-prefix; expand_id_ranges handles it
        tokens = []
        for tid, (aid, _t) in sorted(corpus.threats.items()):
            if aid == area and int(tid.rsplit("-", 1)[1]) >= start_n:
                tokens.append(tid)
        for cid, (aid, _c) in sorted(corpus.controls.items()):
            if aid == area and int(cid.rsplit("-", 1)[1]) <= end_n:
                tokens.append(cid)
        return ", ".join(tokens) if tokens else match.group(0)

    expanded = check.expand_id_ranges(text)
    expanded = MIXED_RANGE.sub(repl, expanded)
    return set(check.ANY_ID.findall(expanded))


def change_log_mentions(corpus: check.Corpus) -> tuple[list[list[str]], dict]:
    """(rows, per-ID row indexes). A row mentions an ID when the ID is a
    token anywhere in the row after range expansion."""
    rows = parse_change_log()
    mentions: dict[str, list[int]] = {}
    for index, cells in enumerate(rows):
        for token in sorted(expand_mentions(" | ".join(cells), corpus)):
            mentions.setdefault(token, []).append(index)
    return rows, mentions


# --------------------------------------------------------------------------
# evidence pack
# --------------------------------------------------------------------------

def snapshot_status(reference: dict) -> str:
    snapshot = reference.get("snapshot")
    if snapshot is None:
        return "not captured"
    if isinstance(snapshot, dict):
        pointer = snapshot.get("path") or snapshot.get("commit")
        retrieved = snapshot.get("retrieved", "")
        sha = snapshot.get("sha256", "")
        parts = [p for p in (pointer, retrieved, sha) if p]
        return " — ".join(str(p) for p in parts) if parts else "recorded"
    return str(snapshot)


def claim_table(claim: dict) -> str:
    rows = [["Claim", claim.get("claim")],
            ["Sources", ", ".join(claim.get("sources") or []) or "—"],
            ["Tier", tier_text(claim)],
            ["Verification", claim.get("verification")],
            ["Last verified", iso_date(claim.get("last_verified"))],
            ["Verified by", claim.get("verified_by")],
            ["Origin", claim.get("origin")],
            ["Decision", claim.get("decision")],
            ["Status", claim.get("status")]]
    if claim.get("split_from"):
        rows.append(["Split from", claim["split_from"]])
    return markdown_table(["Claim field", "Value"], rows)


def tier_text(record: dict) -> str:
    tier = record.get("tier")
    note = record.get("tier_text")
    base = "—" if tier is None else str(tier)
    return f"{base} ({note})" if note else base


def references_table(source_ids: list, references: dict) -> str:
    if not source_ids:
        return "_No references cited (sources “—”)._"
    rows = []
    for rid in source_ids:
        reference = references.get(rid)
        if reference is None:
            raise SystemExit(f"claim cites unknown reference {rid}")
        rows.append([rid, reference.get("title"), tier_text(reference),
                     reference.get("url") or "— (no URL)",
                     snapshot_status(reference)])
    return markdown_table(
        ["ID", "Title", "Tier", "URL", "Snapshot"], rows)


def change_log_rows_table(rows: list[list[str]], indexes: list[int]) -> str:
    return markdown_table(
        ["Date", "IDs", "Change", "Trigger", "Sources", "Approved by"],
        [rows[i] for i in indexes])


def evidence_section(kind: str, record: dict, place: str, claim: dict,
                     rows: list[list[str]], indexes: list[int]) -> str:
    """One evidence-pack section: descriptor line, claim record, references,
    change-log rows. `place` is "A3 Authorisation" for threats and controls
    and the fact's stored "Used in" text for facts."""
    rid = record["id"]
    lines = [f"### {rid} — {descriptor(kind, record, place)} {{#{rid}}}", ""]

    meta_bits = [kind, place, f"status: {record['status']}",
                 f"last changed: {record['last_changed']}"]
    lines.append("_" + " · ".join(meta_bits) + "_")
    lines.append("")

    if kind == "Threat":
        lines += [f"**Name.** {record['name']}", "",
                  f"**Mechanism.** {record['mechanism']}", ""]
    elif kind == "Control":
        trigger = (record.get("trigger") or {}).get("text")
        lines.append(f"**Statement.** {record['statement']}")
        lines.append("")
        lines.append(f"**Addresses.** "
                     f"{', '.join(record.get('addresses') or []) or '—'} · "
                     f"**ASVS.** {', '.join(record.get('asvs') or []) or '—'} · "
                     f"**Type.** {record['type_text']}"
                     + (f" · **Trigger.** {trigger}" if trigger else "")
                     + (" · **Disputed.**" if record.get("disputed") else ""))
        lines.append("")
    else:  # Fact
        lines += [f"**Fact.** {record['fact']}", "",
                  f"**Value.** {record['value']} · **As of.** {record['as_of']}",
                  ""]

    lines += ["**Claim record** (from data/claims/)", "",
              claim_table(claim), ""]

    lines += ["**References** (claim sources; tier, URL, snapshot status)", "",
              references_table(claim.get("sources") or [], REFERENCES), ""]

    if indexes:
        lines += [f"**Change-log rows mentioning {rid}** "
                  f"({len(indexes)}, newest first as stored)", "",
                  change_log_rows_table(rows, indexes)]
    else:
        lines.append(f"**No change-log row mentions {rid}.**")
    return "\n".join(lines)


def descriptor(kind: str, record: dict, place: str) -> str:
    if kind == "Threat":
        return record["name"]
    if kind == "Control":
        return f"control · {place} · {record['type_text']}"
    return record["fact"]


REFERENCES: dict = {}  # set by build_evidence_pack before sections render


def build_evidence_pack(corpus: check.Corpus, meta: dict, title: str) -> str:
    global REFERENCES
    claims = {record["id"]: record for _path, record in corpus.claims}
    REFERENCES = {r["id"]: r for r in corpus.references}
    rows, mentions = change_log_mentions(corpus)

    def hit(rid: str) -> list[int]:
        return mentions.get(rid, [])

    order = catalogue_manifest()["areas"]
    sections = {"Threat": [], "Control": [], "Fact": []}
    for aid in order:
        area = corpus.areas[aid]
        place = f"{area['id']} {area['title']}"
        for threat in area["threats"]:
            sections["Threat"].append(
                evidence_section("Threat", threat, place, claims[threat["id"]],
                                 rows, hit(threat["id"])))
        for control in area["controls"]:
            sections["Control"].append(
                evidence_section("Control", control, place,
                                 claims[control["id"]], rows, hit(control["id"])))
    for fact in corpus.facts:
        place = fact.get("used_in_text") or ", ".join(fact.get("used_in") or [])
        sections["Fact"].append(
            evidence_section("Fact", fact, place or "corpus-wide",
                             claims[fact["id"]], rows, hit(fact["id"])))

    counts = {kind: len(parts) for kind, parts in sections.items()}
    hits = {kind: sum(1 for part in parts
                      if "**Change-log rows mentioning" in part)
            for kind, parts in sections.items()}

    out = [stamp_line(meta), "",
           f"# Evidence pack — {title}", "",
           "One section per threat, control and fact ID. Each section carries "
           "the ID's claim record from `data/claims/`, its claim's references "
           "with tier, URL and snapshot status, and every change-log row in "
           "`register/change-log.md` that mentions the ID (whole-row scan, "
           "same-prefix and mixed-family \"X to Y\" ranges expanded; see "
           "IMPORT-NOTES). Generated by `tools/build.py`; never hand-edited.",
           ""]
    summary = [["Threats", counts["Threat"], hits["Threat"]],
               ["Controls", counts["Control"], hits["Control"]],
               ["Facts", counts["Fact"], hits["Fact"]],
               ["Total", sum(counts.values()), sum(hits.values())]]
    out += [markdown_table(["Kind", "IDs", "With change-log rows"], summary), ""]
    for kind, label in (("Threat", "Threats"), ("Control", "Controls"),
                        ("Fact", "Facts")):
        out += [f"## {label} ({counts[kind]})", ""]
        # every section gets a trailing blank line: a heading after a bare
        # paragraph line would be swallowed by pandoc's blank_before_header
        out += [section + "\n" for section in sections[kind]]
    return "\n".join(out).rstrip("\n") + "\n"


# --------------------------------------------------------------------------
# pandoc renders
# --------------------------------------------------------------------------

def run(cmd: list, env: dict | None = None) -> None:
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(f"command failed ({proc.returncode}): "
                         f"{' '.join(str(c) for c in cmd)}")
    if proc.stdout:
        print(proc.stdout, end="")


def write_anchor_filter() -> Path:
    PANDOC_DIR.mkdir(parents=True, exist_ok=True)
    path = PANDOC_DIR / "anchors.lua"
    path.write_text(ANCHORS_LUA, encoding="utf-8")
    return path


def base_args(markdown: Path, out: Path, title: str, meta: dict,
              extra: list) -> list:
    return (["pandoc", "-f", "markdown-citations", str(markdown),
             "--lua-filter", str(write_anchor_filter()),
             "--metadata", f"title={title}",
             "--metadata", f"subtitle={stamp_line(meta)}",
             "-o", str(out)] + extra)


def main() -> int:
    # 1. generate (deterministic; prints check warnings 1a/1b)
    run([sys.executable, str(ROOT / "tools" / "generate.py")])
    meta = load_build_meta()
    manifest = catalogue_manifest()
    title = manifest["title"]
    env = pandoc_env(meta["built"])
    source = MD / "catalogue-full.md"
    if not source.exists():
        raise SystemExit(f"{source} missing after generate.py")

    OUT.mkdir(parents=True, exist_ok=True)

    # 2. the three catalogue renders
    run(base_args(source, OUT / "catalogue.html", title, meta,
                  ["--standalone", "--toc", "--toc-depth=2"]), env)
    run(base_args(source, OUT / "catalogue.pdf", title, meta,
                  ["--pdf-engine=typst", "--toc", "--toc-depth=2"]), env)
    run(base_args(source, OUT / "catalogue.docx", title, meta, []), env)

    # 3. the evidence pack
    corpus = check.Corpus(ROOT)
    pack_md = build_evidence_pack(corpus, meta, title)
    pack_path = OUT / "evidence-pack.md"
    pack_path.write_text(pack_md, encoding="utf-8")
    run(base_args(pack_path, OUT / "evidence-pack.html",
                  f"Evidence pack — {title}", meta, ["--standalone"]), env)

    print(f"built: catalogue.html, catalogue.pdf, catalogue.docx, "
          f"evidence-pack.md, evidence-pack.html in {OUT}")
    print(f"stamp: {stamp_line(meta)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
