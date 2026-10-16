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

IA pass (WORK-INSTRUCTIONS section 4): every published artifact is
self-describing. The orientation copy renders from tools/orientation.py (the
owner-approved deck, single source): the evidence pack opens with the
orientation header, the "how to check a claim" steps and the evidence legend
parsed from register/governance.md, then a grouped table of contents by area
and the "where the evidence is weakest" index (check.py's warning-5 qualifier
set, disputed controls, IDs with change-log mentions); sections with no
change-log rows carry a marker in the meta line instead of a sentence. The
published catalogue HTML gains ID -> evidence-pack deep links (HTML-only);
the site index and doorway render the orientation blocks; check.py rule 12
keeps the README in sync with the same source.

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

Site step (SETUP-INSTRUCTIONS 10.1 "Site assembly"). Step 4 below
assembles build/site/ from an explicit allowlist, defined once in
site_allowlist() and re-used by check.py's release-mode rule 11, so the
builder and the checker cannot drift. Catalogue content lives under
build/site/web/; the landing files (index.html, llms.txt, robots.txt,
404.html, _headers) are generated from templates in site/root/, kept
separate from the catalogue templates in tools/templates/ (SETUP 10.1:
"Generate the root files from a small template in site/root/"); the
catalogue's own index page comes from site/web/index.html.j2. Nothing
outside the allowlist is copied — archive/ and data/ are never published
(build_site raises if either name appears anywhere in the tree, and
check.py rule 11 re-proves it against the allowlist on its own).

Two inputs are new relative to stage 8, both recorded in IMPORT-NOTES:
the hosted-catalogue list for the landing page, read from catalogues/*.yaml
(the manifests are already corpus inputs), and the GitHub releases URL for
web/index.html, derived from the origin remote (no remote is configured
yet, so the URL is a documented placeholder until the owner sets one).
HISTORY.md renders through the same Pandoc pipeline, with its repository
relative links (data/, register/, archive/...) de-linked, because those
paths exist in the repository, not on the published site.

Version stamp, two forms. §5's stamp (generate.py, untouched) governs
build/md, build/ai and the download files: the tag when HEAD is exactly at
one, otherwise "untagged". §10.1 asks the published pages for more — the
tag, or "<last tag>+<short sha>" between tags — so the site step computes
site_version() and applies it to every published HTML page (the two
rendered copies from build/out/ are rewritten, history.html is rendered
with it directly, and the template pages get it in their stamp and status
line). The two forms coexist on purpose: the corpus editions keep the §5
form, the site shows what a spec author should cite for a live page.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402  (tools/check.py — Corpus and ID helpers)
import orientation  # noqa: E402  (tools/orientation.py — single source of orientation copy, IA pass)

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
MD = BUILD / "md"
AI = BUILD / "ai"
OUT = BUILD / "out"
PANDOC_DIR = BUILD / "pandoc"
SITE = BUILD / "site"
SITE_ROOT_TEMPLATES = ROOT / "site" / "root"
SITE_WEB_TEMPLATES = ROOT / "site" / "web"

# The published site's own framing (SETUP 10.1): the hostname hosts several
# catalogues; this repository is that host. The doorway line is the
# orientation one-liner (IA pass, deck B1/W5): the root index and the root
# llms.txt render it from the single orientation source, so the doorway and
# the artifacts cannot drift.
SITE_TITLE = "appsec.complects.com — security reference catalogues"
SITE_LINE = orientation.ONE_LINER
# web/index.html's status line (SETUP 10.1). Same statement as the README's
# Status paragraph; kept here so the page is generated, not hand-edited.
# The version slot is filled with the §10.1 site version (site_version),
# so the status line never shows a newer version than the page was built
# from: 1.0.0-beta.1 once tagged, "<last tag>+<sha>" between tags,
# "untagged" before the first tag.
SITE_STATUS = ("Status {version} — verified against its cited sources "
               "but not yet independently reviewed or specialist-signed-off; "
               "not suitable for risk acceptance or compliance assertions.")
# web/index.html links the GitHub releases page (SETUP 10.1). No origin
# remote is configured during import, so this stands in until the owner
# sets one; build_site prints a warning while it is in use.
RELEASES_FALLBACK = "https://github.com/OWNER/REPOSITORY/releases"

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
    # IA-8 (owner ruling, click-through gate), retargeted by IA-9: the
    # Sources cell's R-ID tokens link to the reference's row on the
    # references page — markdown source flowing to both .md and .html;
    # degradation is the established one (live where the pair travels,
    # non-resolving alone). verify_pack_link_targets proves every emitted
    # target anchor exists in the built page.
    sources = ", ".join(f"[{rid}](references.html#{rid})"
                        for rid in claim.get("sources") or []) or "—"
    rows = [["Claim", claim.get("claim")],
            ["Sources", sources],
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
    # IA-7 (owner ruling, click-through gate): the URL cell renders as a
    # markdown link with the URL as both text and target — one source
    # flowing to evidence-pack.md and .html. IA-9: the ID column links each
    # R-ID to its row on the references page (with the dedicated page, that
    # column earns links); R-107 (no URL) keeps its marker.
    if not source_ids:
        return "_No references cited (sources “—”)._"
    rows = []
    for rid in source_ids:
        reference = references.get(rid)
        if reference is None:
            raise SystemExit(f"claim cites unknown reference {rid}")
        url = reference.get("url")
        rows.append([f"[{rid}](references.html#{rid})",
                     reference.get("title"), tier_text(reference),
                     f"[{url}]({url})" if url else "— (no URL)",
                     snapshot_status(reference)])
    return markdown_table(
        ["ID", "Title", "Tier", "URL", "Snapshot"], rows)


def verify_pack_link_targets(corpus: check.Corpus, references_html: str) -> int:
    """IA-8 (retargeted by IA-9): every R-ID linked from the evidence
    pack — the claim-record Sources cells and the per-ID reference-table
    ID column, which emit the same token set — must have its row anchor on
    the built references page. Mapped-but-missing is a hard error (the
    role-table discipline); the links themselves degrade only when the
    pack travels without the page (owner-ruled). Returns the token count."""
    linked_rids = sorted({rid for _path, claim in corpus.claims
                          for rid in claim.get("sources") or []})
    missing = [rid for rid in linked_rids
               if f'id="{rid}"' not in references_html]
    if missing:
        raise SystemExit("evidence-pack R-links: no row anchor on "
                         f"references.html for: {', '.join(missing)} — "
                         "every emitted link target must exist (IA-8/IA-9)")
    return sum(len(claim.get("sources") or [])
               for _path, claim in corpus.claims)


def references_page_markdown(corpus: check.Corpus, title: str) -> tuple[str, int, int]:
    """IA-9 (owner ruling, click-through gate): the source markdown for
    /web/references.html — Appendix B rendered per reference as its own
    page. Orientation line (the ruling's own phrasing), the evidence
    legend from the same parsed governance source as every other surface,
    then the 144-reference table: title cells linked as Appendix B links
    them (generate.py's reference_cell, one implementation), tier and
    opened as the appendix carries them, cited-by tokens linked to the
    evidence pack for T-/C-/F-IDs and plain for area tokens and section
    labels (the established degradation model). Rows anchor per R-ID via
    the shared Lua filter (first header cell "R-ID")."""
    import generate  # tools/generate.py — reference_cell, the Appendix B title rule

    gov = orientation.parse_governance(ROOT)
    cited_by = check.regenerate_cited_by(corpus)
    rows = []
    linked_cited = 0
    plain_cited = 0
    for reference in corpus.references:
        rid = reference["id"]
        cells = []
        for token in cited_by.get(rid, []):
            if check.TCF_ID.fullmatch(token):
                cells.append(f"[{token}](evidence-pack.html#{token})")
                linked_cited += 1
            else:
                cells.append(token)  # area token or section label: plain
                plain_cited += 1
        tier = (f"{reference['tier']} {reference['tier_note']}"
                if reference.get("tier_note") else str(reference["tier"]))
        rows.append([rid, generate.reference_cell(reference),
                     reference["issuer"], reference["edition"], tier,
                     reference["opened"], ", ".join(cells) or "—"])
    lines = [f"# References — {title}", "",
             "Every source cited by the catalogue, with its tier, link and "
             "citation reach — Appendix B rendered per reference.", "",
             orientation.legend_markdown(gov), "",
             markdown_table(["R-ID", "Reference", "Issuer", "Edition",
                             "Tier", "Opened", "Cited by"], rows), ""]
    return "\n".join(lines), linked_cited, plain_cited


def change_log_rows_table(rows: list[list[str]], indexes: list[int]) -> str:
    return markdown_table(
        ["Date", "IDs", "Change", "Trigger", "Sources", "Approved by"],
        [rows[i] for i in indexes])


def evidence_section(kind: str, record: dict, place: str, claim: dict,
                     rows: list[list[str]], indexes: list[int]) -> str:
    """One evidence-pack section: descriptor line, claim record, references,
    change-log rows. `place` is "A3 Authorisation" for threats and controls
    and the fact's stored "Used in" text for facts. Sections with no
    change-log rows carry the marker "no change-log mentions" in the meta
    line (IA pass: the 256 "No change-log row mentions <ID>." sentences
    collapsed to a marker) instead of a sentence of their own."""
    rid = record["id"]
    lines = [f"### {rid} — {descriptor(kind, record, place)} {{#{rid}}}", ""]

    meta_bits = [kind, place, f"status: {record['status']}",
                 f"last changed: {record['last_changed']}"]
    if not indexes:
        meta_bits.append("no change-log mentions")
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
    gov = orientation.parse_governance(ROOT)

    def hit(rid: str) -> list[int]:
        return mentions.get(rid, [])

    # -- body: one H3 section per T/C/F ID, grouped by area (IA pass) -------
    order = catalogue_manifest()["areas"]
    groups: list[tuple[dict, list[str]]] = []
    all_sections: list[str] = []
    for aid in order:
        area = corpus.areas[aid]
        place = f"{area['id']} {area['title']}"
        parts = []
        for threat in area["threats"]:
            parts.append(evidence_section("Threat", threat, place,
                                          claims[threat["id"]],
                                          rows, hit(threat["id"])))
        for control in area["controls"]:
            parts.append(evidence_section("Control", control, place,
                                          claims[control["id"]],
                                          rows, hit(control["id"])))
        groups.append((area, parts))
        all_sections += parts
    fact_parts = []
    for fact in corpus.facts:
        place = fact.get("used_in_text") or ", ".join(fact.get("used_in") or [])
        fact_parts.append(evidence_section("Fact", fact, place or "corpus-wide",
                                           claims[fact["id"]],
                                           rows, hit(fact["id"])))
    all_sections += fact_parts

    counts = {"Threat": sum(len(corpus.areas[a]["threats"]) for a in order),
              "Control": sum(len(corpus.areas[a]["controls"]) for a in order),
              "Fact": len(corpus.facts)}
    section_prefix = {"Threat": "### T-", "Control": "### C-", "Fact": "### F-"}
    hits = {kind: sum(1 for section in all_sections
                      if section.startswith(section_prefix[kind])
                      and "**Change-log rows mentioning" in section)
            for kind in ("Threat", "Control", "Fact")}

    # -- the "where the evidence is weakest" index (IA pass) ----------------
    # Three lists rendered from data, each entry linking to its section:
    # check.py's warning-5 qualifier set; disputed controls; IDs with
    # change-log mentions (the whole-row rule, IMPORT-NOTES 54).
    qualified = sorted(
        message.split(":")[1].strip()
        for message in check.warning_5_verification(corpus))
    disputed = sorted(cid for cid in corpus.controls
                      if corpus.controls[cid][1].get("disputed"))
    tcf_ids = set(corpus.threats) | set(corpus.controls) | set(corpus.fact_ids)
    with_history = sorted(rid for rid in tcf_ids if mentions.get(rid))

    def id_links(ids: list) -> str:
        return ", ".join(f"[{rid}](#{rid})" for rid in ids)

    # -- the grouped table of contents, by area with counts -----------------
    toc_rows = []
    for area, parts in groups:
        threats = sum(1 for p in parts if p.startswith("### T-"))
        controls = sum(1 for p in parts if p.startswith("### C-"))
        area_hits = sum(1 for record in list(area["threats"]) + list(area["controls"])
                        if mentions.get(record["id"]))
        toc_rows.append([f"[{area['id']} {area['title']}](#{area['id']})",
                         f"{threats} threats · {controls} controls",
                         str(area_hits)])
    fact_hits = sum(1 for fact in corpus.facts if mentions.get(fact["id"]))
    toc_rows.append(["[Facts](#facts)", f"{counts['Fact']} facts",
                     str(fact_hits)])

    out = [stamp_line(meta), "",
           f"# Evidence pack — {title}", "",
           orientation.evidence_pack_orientation(gov), "",
           "## Contents", "",
           markdown_table(["Area", "Sections", "With change-log rows"], toc_rows),
           "",
           orientation.EVIDENCE_PACK_WEAKEST, "",
           f"- Claims carrying qualifiers ({len(qualified)}): "
           f"{id_links(qualified)}",
           f"- Disputed controls ({len(disputed)}): {id_links(disputed)}",
           f"- IDs with change-log history ({len(with_history)}): "
           f"{id_links(with_history)}",
           ""]
    summary = [["Threats", counts["Threat"], hits["Threat"]],
               ["Controls", counts["Control"], hits["Control"]],
               ["Facts", counts["Fact"], hits["Fact"]],
               ["Total", sum(counts.values()), sum(hits.values())]]
    out += [markdown_table(["Kind", "IDs", "With change-log rows"], summary), ""]
    for area, parts in groups:
        threats = sum(1 for p in parts if p.startswith("### T-"))
        controls = sum(1 for p in parts if p.startswith("### C-"))
        out += [f"## {area['id']} {area['title']} — {threats} threats, "
                f"{controls} controls {{#{area['id']}}}", ""]
        # every section gets a trailing blank line: a heading after a bare
        # paragraph line would be swallowed by pandoc's blank_before_header
        out += [section + "\n" for section in parts]
    out += [f"## Facts ({counts['Fact']}) {{#facts}}", ""]
    out += [section + "\n" for section in fact_parts]

    print(f"evidence pack: weakest index — {len(qualified)} qualified, "
          f"{len(disputed)} disputed, {len(with_history)} with change-log "
          f"history; {len(tcf_ids) - len(with_history)} no-change-log markers")
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


# --------------------------------------------------------------------------
# site step (SETUP-INSTRUCTIONS 10.1)
# --------------------------------------------------------------------------

def site_catalogues(root: Path | None = None) -> list:
    """The hosted catalogues for the landing pages: every manifest in
    catalogues/*.yaml (SETUP 10.1: "The root lists every manifest in
    catalogues/"), as {id, title, path, href}, sorted by manifest name."""
    root = root or ROOT
    entries = []
    for path in sorted((root / "catalogues").glob("*.yaml")):
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
        entries.append({
            "id": manifest.get("id", path.stem),
            "title": manifest["title"],
            "path": manifest["path"],           # the published path, "/web/"
            "href": manifest["path"].lstrip("/"),  # the relative link, "web/"
        })
    if not entries:
        raise SystemExit("no catalogue manifests in catalogues/")
    return entries


def site_version(root: Path | None = None) -> str:
    """The version a published page displays (SETUP 10.1 "Version stamp").

      HEAD tagged      -> that tag (the highest, by version ordering, if
                          several point at HEAD);
      untagged, tags   -> "<last tag>+<short sha>";
      exist
      no tags at all   -> "untagged" (the commit is already in the stamp).

    "Last tag" is check.py's previous_tag(): the highest-version v* tag
    that is an ancestor of HEAD. That is git-describe's semantics — the
    most recent reachable tag — expressed in the version ordering this
    repository already uses for check.py rules 6 and 9, and it is a
    release ordering (v0.9.0 released after v0.10.0 cannot happen in a
    tag-is-a-release model), so version order is the right tiebreak rather
    than commit topology.

    §5's stamp (generate.py, untouched) governs build/md and build/ai and
    shows "untagged" whenever HEAD is not exactly at a tag; this §10.1
    form is applied to the published pages only, in the site step."""
    root = root or ROOT
    head_tags = sorted(
        (tag for tag in check.git(["tag", "--points-at", "HEAD"], root)
         .stdout.split() if check.version_key(tag)),
        key=check.version_key)
    if head_tags:
        return head_tags[-1]
    tag = check.previous_tag(root)
    if tag is None:
        return "untagged"
    commit = check.git(["rev-parse", "--short", "HEAD"], root).stdout.strip()
    return f"{tag}+{commit}"


def site_stamp_line(meta: dict, version: str) -> str:
    """stamp_line with the §10.1 site version instead of §5's."""
    return (f"Catalogue version {version}, built {meta['built']} "
            f"from commit {meta['commit']}")


def rewrite_site_version(text: str, old_version: str, new_version: str) -> str:
    """Swap the §5 stamp's version token for the §10.1 site version in a
    rendered page. Whitespace-tolerant because pandoc hard-wraps the
    subtitle line at ~72 columns; HTML collapses that whitespace when
    rendered, and pandoc never inserts a tag inside the paragraph. Every
    occurrence is replaced (subtitle and any body stamp line). Raises if
    nothing matched, so a change in the stamp wording cannot silently
    leave a §5 version on a published page."""
    pattern = re.compile(r"Catalogue\s+version\s+" + re.escape(old_version)
                         + r"\b")
    replaced, count = pattern.subn(
        lambda _match: f"Catalogue version {new_version}", text)
    if count == 0:
        raise SystemExit(f"site version rewrite found no "
                         f"'Catalogue version {old_version}' to replace — "
                         f"the stamp wording changed; update the rewrite")
    return replaced


def releases_url() -> tuple:
    """(url, is_placeholder) for the GitHub releases page (SETUP 10.1).
    Derived from the origin remote so the published page links this
    repository's releases without a hard-coded slug; a repository with no
    remote gets the documented placeholder and a printed warning."""
    proc = subprocess.run(["git", "remote", "get-url", "origin"],
                          capture_output=True, text=True, check=False)
    remote = proc.stdout.strip() if proc.returncode == 0 else ""
    match = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", remote) if remote else None
    if match:
        return f"https://github.com/{match.group(1)}/releases", False
    return RELEASES_FALLBACK, True


def site_allowlist(root: Path | None = None, ai_names: list | None = None) -> list:
    """Every file the site step may write, relative to build/site/. This is
    the single definition of the allowlist: build_site assembles exactly
    these files and check.py's site rule (SETUP 10.1, release-mode error)
    compares build/site/ against this list. `ai_names` lets a caller pass
    the build/ai file names instead of reading them from disk (check.py
    does, when it runs with --root against a copied tree)."""
    root = root or ROOT
    if ai_names is None:
        ai_dir = root / "build" / "ai"
        if not ai_dir.is_dir():
            raise SystemExit("build/ai is missing; the site copies everything "
                             "in it (run tools/generate.py first)")
        ai_names = [p.name for p in sorted(ai_dir.iterdir()) if p.is_file()]
    files = [
        # landing files at the site root, from site/root/ templates
        "404.html", "_headers", "index.html", "llms.txt", "robots.txt",
        # catalogue pages under web/ (web/references.html added by IA-9,
        # a ruled allowlist amendment: 20 -> 21 files)
        "web/AGENTS.md", "web/catalogue.html", "web/evidence-pack.html",
        "web/history.html", "web/index.html", "web/llms.txt",
        "web/references.html",
        "web/downloads/catalogue.docx", "web/downloads/catalogue.pdf",
        "web/downloads/evidence-pack.md",
    ] + [f"web/ai/{name}" for name in ai_names]
    return sorted(files)


def site_env(directory: Path) -> Environment:
    """A Jinja environment over one site template directory. Root and
    catalogue templates are separate directories (SETUP 10.1), each with
    its own environment so an index.html.j2 in one can never shadow the
    other's."""
    return Environment(loader=FileSystemLoader(str(directory)),
                       undefined=StrictUndefined, trim_blocks=True,
                       lstrip_blocks=True, keep_trailing_newline=True)


def render_site(env: Environment, template: str, target: Path, **context) -> None:
    text = env.get_template(template).render(**context)
    if not text.endswith("\n"):
        text += "\n"
    target.write_text(text, encoding="utf-8")


# HISTORY.md links repository paths (data/, register/, archive/origin/...)
# that exist in the repository, not on the published site (archive/ is
# never published). Repository-relative links render as their label text;
# absolute http(s) links and in-page anchors stay links.
MD_LINK = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<target>[^)\s]+)(?:#[^)]*)?\)")
ABSOLUTE_TARGET = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def publish_history_text(text: str) -> str:
    def repl(match):
        if ABSOLUTE_TARGET.match(match.group("target")):
            return match.group(0)
        return match.group("label")
    return MD_LINK.sub(repl, text)


# IA-13 (owner ruling, click-through gate): the three web pages rendered by
# Pandoc (catalogue, evidence pack, references) drop the default template's
# 36em body cap — full-width reflow, tables at 100%; line-height, colours,
# padding and the small-screen media query stay the template's own. Applied
# only to the HTML invocations via --include-in-header (a later stylesheet
# wins at equal specificity); the PDF and DOCX invocations are separate and
# byte-unchanged. Static CSS, written to build/pandoc/ at run time like the
# anchor filter (no new source files, no new site files).
WEB_HEADER_HTML = """<style>
/* IA-13 web width override: no body cap, tables full width. The template's
   padding, line-height, colours and max-width:600px media query stand. */
body { max-width: none; }
table { width: 100%; }
</style>
"""


# IA-18 (owner ruling, on-device check): the catalogue pages look good
# on a real phone (approved, not churned); the evidence pack and the
# references page FAIL — tables that do not compress scroll across,
# ruled a mobile platform failure. Diagnosis (Playwright, 390px): the
# evidence pack alone carries raw-URL table cells (481 links whose
# display text is the URL itself; a URL is one unbreakable token, so
# 383 of 789 tables had min-content widths past the viewport, widest
# 796px in a 366px box). Two page-appropriate rules, both CSS-only and
# both dormant at desktop widths:
#
# evidence pack — URL cells wrap in place: overflow-wrap: anywhere on
# external-target links only (a[href^="http"]; the pack's other links
# are in-page anchors), which unlike the body's inherited break-word
# counts in min-content sizing, so the table shrinks to the viewport
# and wraps the URL instead of forcing its width. Ordinary prose never
# breaks mid-word. A phone-width scroll fallback covers any table that
# still cannot fit (none measured).
#
# references — no raw URLs (its long tokens are plain issuer names and
# linked titles); its 7-column R-table either shatters every word to
# fit 390px (a first attempt, vision-ruled unreadable: "MITR/E",
# "Securi/tyWee/k") or keeps readable columns and scrolls within its
# own region. The region-scroll pattern (display: block; overflow-x:
# auto, under the template's own 600px breakpoint) is the ruled IA-18
# mobile shape: the page never pans, the table is inspected by
# scrolling inside its box, and at >=601px nothing changes at all.
#
# Catalogue-unchanged rule: both ride only their own invocations; the
# catalogue keeps exactly the IA-13 header, whose rendering the owner
# approved on-device.
URLWRAP_CSS = """<style>
/* IA-18 mobile (evidence pack): raw-URL table cells wrap in place —
   overflow-wrap: anywhere on external-target links only (the pack's
   other links are in-page anchors), which unlike the body's inherited
   break-word counts in min-content sizing, so the table shrinks to the
   viewport instead of forcing its width past it. Ordinary prose never
   breaks mid-word. A gentle phone-width table font step (the template
   already steps the body to 0.9em here) pulls the six-column
   change-history tables under the viewport as well. Dormant at desktop
   widths. */
td a[href^="http"], th a[href^="http"] { overflow-wrap: anywhere; }
@media (max-width: 600px) {
  table { font-size: 0.85em; }
}
</style>
"""

_WEB_HEADERS = {"": ("web-header.html", ""),
                "urlwrap": ("web-header-urlwrap.html", URLWRAP_CSS)}


def web_header(variant: str = "") -> Path:
    """The runtime-written header include (IA-13's override location).
    IA-18 variants: 'urlwrap' (evidence pack) and 'tablescroll'
    (references); the catalogue keeps the plain IA-13 header."""
    name, extra = _WEB_HEADERS[variant]
    PANDOC_DIR.mkdir(parents=True, exist_ok=True)
    path = PANDOC_DIR / name
    path.write_text(WEB_HEADER_HTML + extra, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# typst post-process (owner defect report, PDF workstream)
#
# Typst 0.15.1 mis-lays-out a table that breaks across a page boundary
# inside a #figure: the rows that should move to the next page are drawn
# overlapping each other, running into the bottom margin (reproduced
# minimally with plain typst, no pandoc involved; latent at tag
# v1.0.0-beta.1 — pages 26/91/93 there, 28/93/95 after the About-section
# pagination shift — and, at Appendix B scale, the whole 144-row table
# compressed into two unreadable pages). The writer's equal-percentage
# columns are the second half of the same report ("bulk of the prose in
# very narrow columns").
#
# Fix, build-side (no pandoc/typst version change): the PDF renders in two
# steps — pandoc writes the typst source, this post-process de-figures
# every table (a bare #table breaks correctly) and rebalances each table's
# columns header-aware (IA-17: every column at least wide enough for its
# header label and its widest unbreakable cell segment, measured in
# points; the remainder flexes to the prose columns), then typst
# compiles with the creation timestamp pinned to the same SOURCE_DATE_EPOCH
# value, so the output stays a pure function of the inputs.
# --------------------------------------------------------------------------

# IA-17 (owner ruling, 2026-10-16): the first rebalance sized columns by
# character counts against a 4%-of-table-width floor — narrower than the
# rendered glyphs of "R-100" or "Opened", so the text overflowed its
# column: Appendix B's R-ID column abutted the Reference column, and the
# "Opened" and "Cited By" header cells overlapped each other. The owner
# ruled both defects, reclassifying the "minor cosmetics" grading the
# sampled vision checks had given them. The rule now: a column is never
# narrower than what it must show whole — the widest unbreakable segment
# of its header label (headers wrap at word boundaries, and only where
# the text block leaves no room for the one-line form) and the widest
# unbreakable segment of its cells — measured in points, with the
# table's own insets and a safety factor, so abutment is impossible by
# construction rather than by luck. What remains flexes to the columns
# in proportion to their content mass, so the title and cited-by
# columns absorb the remainder. Applied to every table this pass
# rebuilds (threats, controls, Appendix A, Appendix B); a table whose
# hard floors cannot fit the text block even at the tightest gutter
# fails the build, so the collision class cannot recur silently.
#
# Measurement is calibrated against the rendered page (Libertinus Serif
# 11pt, the template default): a per-character table fitted to the word
# bounding boxes of a built catalogue (median error 0.07pt, p95 0.56pt),
# inflated by a 1.05 safety factor. Static data — the build stays a pure
# function of its inputs.
_CHAR_PT = {
    " ": 3.5, "(": 3.2, ")": 3.2, ",": 2.4, "-": 3.5, ".": 2.5, "/": 4.2,
    ":": 2.9, ";": 2.4,
    "0": 5.2, "1": 5.2, "2": 5.1, "3": 5.1, "4": 5.1, "5": 5.0, "6": 5.2,
    "7": 5.0, "8": 5.1, "9": 5.0,
    "A": 7.6, "B": 6.6, "C": 7.4, "D": 7.8, "E": 6.2, "F": 5.3, "G": 7.3,
    "H": 8.6, "I": 3.2, "J": 3.7, "K": 6.7, "L": 6.1, "M": 9.1, "N": 7.8,
    "O": 7.5, "P": 6.1, "Q": 7.5, "R": 6.7, "S": 5.2, "T": 6.3, "U": 7.2,
    "V": 7.0, "W": 10.3, "X": 7.5, "Y": 5.5, "Z": 7.2,
    "a": 5.1, "b": 5.3, "c": 4.8, "d": 5.6, "e": 5.0, "f": 3.3, "g": 5.6,
    "h": 5.9, "i": 3.1, "j": 3.0, "k": 5.7, "l": 3.0, "m": 8.6, "n": 6.0,
    "o": 5.5, "p": 5.8, "q": 5.3, "r": 4.2, "s": 4.3, "t": 3.5, "u": 6.0,
    "v": 5.4, "w": 8.3, "x": 5.4, "y": 5.7, "z": 4.2,
}
_TEXT_WIDTH_PT = 432.0    # us-letter text block: 8.5in - 2 x 1.25in margins
_SAFETY = 1.05            # model error (p95 0.56pt) + bold header set
# cited IDs stay whole — a hyphen-broken "C-A12-10" reads as two IDs
_CITE_ID = re.compile(r"^[A-Z]-[A-Za-z0-9-]*[0-9],?$")
_CITE_ID_BOX = re.compile(r"(?<![\\#\w])([A-Z]-[A-Za-z0-9-]*[0-9])(?![\w])")

def _typ_split_args(body: str) -> list:
    """A table body's top-level comma-separated arguments, bracket-aware
    (a ')' inside a [...] cell must not end the argument list)."""
    parts, current = [], []
    square = paren = 0
    i = 0
    while i < len(body):
        c = body[i]
        if c == "\\":
            current.append(body[i:i + 2])
            i += 2
            continue
        if c == "[":
            square += 1
        elif c == "]":
            square -= 1
        elif c == "(" and square == 0:
            paren += 1
        elif c == ")" and square == 0:
            paren -= 1
        if c == "," and square == 0 and paren == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(c)
        i += 1
    if current:
        parts.append("".join(current))
    return parts


def _typ_cell_groups(arg: str) -> list:
    """The top-level [...] contents of one table argument."""
    groups, depth, start = [], 0, 0
    i = 0
    while i < len(arg):
        c = arg[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            depth += 1
            if depth == 1:
                start = i + 1
        elif c == "]":
            if depth == 1:
                groups.append(arg[start:i])
            depth -= 1
        i += 1
    return groups


def _typ_plain(cell: str) -> str:
    text = re.sub(r"#[A-Za-z]+", "", cell)
    return text.replace("\\[", "[").replace("\\]", "]")


def _typ_text_pt(text: str) -> float:
    """Rendered width of a string, points (the calibrated table above)."""
    return sum(_CHAR_PT.get(c, 5.6) for c in text)


def _typ_cell_text(cell: str) -> str:
    """A cell's plain text for measurement: typst function names, link
    targets (quoted strings) and bracket syntax are not rendered text;
    pandoc's source line wraps and ~ non-breaking spaces read as spaces."""
    text = re.sub(r"#[A-Za-z]+", "", cell)
    text = re.sub(r'"[^"]*"', "", text)
    text = text.replace("\\[", "[").replace("\\]", "]")
    text = text.replace("[", " ").replace("]", " ").replace("~", " ")
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()


def _typ_token_pt(token: str) -> float:
    """The width a token needs before it overflows: cited IDs stay whole;
    anything else may break after a hyphen (typst breaks lines there), so
    its floor is the widest hyphen-separated segment."""
    if _CITE_ID.match(token):
        return _typ_text_pt(token)
    return max((_typ_text_pt(seg) for seg in re.split(r"(?<=-)", token)
                if seg), default=0.0)


def _typ_column_widths(ncols: int, headers: list, cells: list):
    """Header-aware column widths in points (IA-17). Each column is at
    least wide enough for its header label (one line where the text block
    affords it, word-wrapped where it does not) and its widest
    unbreakable cell segment, both plus the table insets and a safety
    factor; the remaining width flexes to the columns in proportion to
    their content mass. Returns (widths, inset_x): the template's 6pt
    gutter unless the floors only fit with a tighter one."""
    header_line = [0.0] * ncols
    header_word = [0.0] * ncols
    token_floor = [0.0] * ncols
    score = [0.0] * ncols
    counts = [0] * ncols
    for c, label in enumerate(headers[:ncols]):
        text = _typ_cell_text(label)
        header_line[c] = _typ_text_pt(text)
        header_word[c] = max((_typ_text_pt(w) for w in text.split()),
                             default=0.0)
    # cells[] opens with the ncols header groups (the caller extends it
    # with them), so the body — the only mass that should flex — starts
    # at ncols
    for r, cell in enumerate(cells[ncols:] if len(cells) >= ncols else []):
        c = r % ncols
        text = _typ_cell_text(cell)
        score[c] += _typ_text_pt(text)
        counts[c] += 1
        for token in text.split():
            token_floor[c] = max(token_floor[c], _typ_token_pt(token))
    for c, label in enumerate(headers[:ncols]):
        for token in _typ_cell_text(label).split():
            token_floor[c] = max(token_floor[c], _typ_token_pt(token))
    score = [s / n if n else 0.0 for s, n in zip(score, counts)]
    for inset in (6.0, 5.0, 4.5, 4.0, 3.5):
        pad = 2.0 * inset
        hard = [max(token_floor[c], header_word[c]) * _SAFETY + pad
                for c in range(ncols)]
        if sum(hard) <= _TEXT_WIDTH_PT:
            break
    else:
        raise SystemExit("typst post-process: table columns cannot fit the "
                         "text block even at a 3.5pt gutter — header-aware "
                         "floors exceed the page (IA-17); widen the page or "
                         "shorten the cells")
    preferred = [max(hard[c], header_line[c] * _SAFETY + pad)
                 for c in range(ncols)]
    base = list(hard)
    if sum(preferred) <= _TEXT_WIDTH_PT:
        base = preferred
    else:
        # keep as many headers on one line as the text block affords:
        # cheapest upgrades first
        for c in sorted(range(ncols),
                        key=lambda c: (preferred[c] - hard[c], c)):
            if sum(base) + preferred[c] - hard[c] <= _TEXT_WIDTH_PT:
                base[c] = preferred[c]
    flex = _TEXT_WIDTH_PT - sum(base)
    if flex > 0 and sum(score) > 0:
        base = [b + flex * s / sum(score) for b, s in zip(base, score)]
    return base, inset


def postprocess_typst(text: str) -> str:
    """De-figure and rebalance the pandoc typst writer's tables."""
    defigured = text.replace("#figure(\n  align(center)[#table(", "#table(")
    defigured = defigured.replace(")]\n  , kind: table\n  )", ")")
    if "#figure(\n  align(center)[#table(" in defigured:
        raise SystemExit("typst post-process: a figure-wrapped table "
                         "survived the de-figure rewrite — the writer's "
                         "emission changed; update the transform")

    out = []
    pos = 0
    count = 0
    while True:
        j = defigured.find("\n#table(", pos)
        if j < 0:
            out.append(defigured[pos:])
            break
        j += 1
        p = j + len("#table(")
        square = 0
        paren = 1
        while p < len(defigured):
            c = defigured[p]
            if c == "\\":
                p += 2
                continue
            if c == "[":
                square += 1
            elif c == "]":
                square -= 1
            elif c == "(" and square == 0:
                paren += 1
            elif c == ")" and square == 0:
                paren -= 1
                if paren == 0:
                    break
            p += 1
        body = defigured[j + len("#table("):p]
        match = re.search(r"columns: \(([^)]*)\)", body, re.S)
        if match:
            ncols = len([x for x in match.group(1).split(",") if x.strip()])
            headers = []
            cells = []
            for arg in _typ_split_args(body[match.end():]):
                stripped = arg.strip()
                if stripped.startswith("table.header"):
                    headers = _typ_cell_groups(arg)
                    cells.extend(headers)
                elif stripped.startswith("table.hline"):
                    continue
                elif " ".join(_typ_cell_groups(arg)).strip():
                    cells.append(" ".join(_typ_cell_groups(arg)))
            widths, inset_x = _typ_column_widths(ncols, headers, cells)
            hundredths = [int(round(10000.0 * w / sum(widths)))
                          for w in widths]
            hundredths[hundredths.index(max(hundredths))] += \
                10000 - sum(hundredths)
            new_columns = ("columns: ("
                           + ", ".join(f"{h / 100:.2f}%" for h in hundredths))
            body = (body[:match.start()] + new_columns
                    + body[match.end() - 1:])
            if inset_x != 6.0:
                # the header-aware floors only fit with a tighter gutter
                # (the template sets inset: 6pt); y stays the template's
                body = f"\n    inset: (x: {inset_x}pt, y: 6pt)," + body
            # cited IDs render unbreakable: typst's line breaker will
            # otherwise split "C-A12-10" after its hyphen, leaving a bare
            # "C-" at a line end that reads as a truncated ID. #box is
            # layout-only — the glyphs, and so the extracted text, are
            # unchanged. Quoted link targets are left alone.
            parts = re.split(r'("[^"]*")', body)
            body = "".join(p if p.startswith('"')
                           else _CITE_ID_BOX.sub(r"#box[\1]", p)
                           for p in parts)
        out.append(defigured[pos:j])
        out.append("#table(")
        out.append(body)
        out.append(")")
        pos = p + 1
        count += 1
    if count == 0:
        raise SystemExit("typst post-process: no tables found — the writer's "
                         "emission changed; refusing to emit an unprocessed PDF")
    return "".join(out)


# Deliverable 6 (IA pass): every T/C/F row ID in the published catalogue
# links to its evidence-pack section. The defining anchors are the spans the
# Lua filter emits; this wraps each in a plain relative link. HTML-only by
# owner ruling: build/out and the downloads stay link-free, and
# build/md/catalogue-full.md must not gain link markup (the round trip
# compares it to the original export). The links work on the site and
# wherever the pair travels together; a lone catalogue.html has
# non-resolving links (owner-ruled degradation).
EVIDENCE_LINK_SPAN = re.compile(
    r'<span id="((?:[TC]-(?:A|B|P)\d{1,2}-\d+|F-\d+))">([^<]*)</span>')


def add_evidence_links(html: str, expected: int) -> str:
    """Wrap every defining T/C/F span anchor in a relative link to its
    evidence-pack section. Raises when the anchor count is not the corpus's
    T/C/F total, so a change in the anchor rendering can never silently
    leave IDs unlinked (or link the wrong thing)."""

    def repl(match: "re.Match") -> str:
        rid, text = match.group(1), match.group(2)
        return (f'<a href="evidence-pack.html#{rid}">'
                f'<span id="{rid}">{text}</span></a>')

    replaced, count = EVIDENCE_LINK_SPAN.subn(repl, html)
    if count != expected:
        raise SystemExit(f"evidence deep-links: found {count} T/C/F span "
                         f"anchors, expected {expected} (the corpus total) — "
                         "the anchor rendering changed; update the rewrite")
    return replaced


def build_site(meta: dict, corpus: check.Corpus | None = None) -> None:
    """Assemble build/site/ from the allowlist (SETUP 10.1). The directory
    is rebuilt from scratch every run, so a stale file can never survive a
    change to the allowlist."""
    if SITE.exists():
        shutil.rmtree(SITE)
    web = SITE / "web"
    (web / "downloads").mkdir(parents=True)
    (web / "ai").mkdir(parents=True)

    # the §10.1 site version (tag / <last tag>+<sha> / untagged); §5's
    # stamp in meta['version'] stays on build/md, build/ai and the
    # download files, which generate.py and the renders own
    version = site_version()
    stamp = site_stamp_line(meta, version)

    # web/: the catalogue renders and the evidence pack, from build/out/,
    # with their existing relative links (pandoc anchors are in-page), the
    # stamp's version swapped for the §10.1 form; the published catalogue
    # additionally gains the ID -> evidence-pack deep links (HTML-only)
    if corpus is None:
        corpus = check.Corpus(ROOT)
    n_tcf = (len(corpus.threats) + len(corpus.controls)
             + len(corpus.fact_ids))
    for name in ("catalogue.html", "evidence-pack.html"):
        page = rewrite_site_version((OUT / name).read_text(encoding="utf-8"),
                                    meta["version"], version)
        if name == "catalogue.html":
            page = add_evidence_links(page, n_tcf)
        (web / name).write_text(page, encoding="utf-8")

    # IA-4 (owner ruling, click-through gate): every mapped role-table
    # target anchor must exist in the built page it points at —
    # mapped-but-missing is a hard error (the same discipline as the
    # deep-link count check). Page-level mappings carry no anchor to check;
    # unmapped cells degrade silently to plain text.
    for cell_text, (page_name, anchor) in orientation.ROLE_TABLE_LINKS.items():
        if anchor is None:
            continue
        if f'id="{anchor}"' not in (web / page_name).read_text(encoding="utf-8"):
            raise SystemExit(f"role-table link target missing: {cell_text!r} "
                             f"maps to {page_name}#{anchor}, but the built "
                             "page carries no such id — fix the mapping in "
                             "tools/orientation.py (IA-4)")
    shutil.copy2(OUT / "catalogue.pdf", web / "downloads" / "catalogue.pdf")
    shutil.copy2(OUT / "catalogue.docx", web / "downloads" / "catalogue.docx")
    shutil.copy2(OUT / "evidence-pack.md",
                 web / "downloads" / "evidence-pack.md")

    # web/ai/: everything in build/ai/ ...
    for path in sorted(AI.iterdir()):
        if path.is_file():
            shutil.copy2(path, web / "ai" / path.name)
    # ... and web/llms.txt and web/AGENTS.md, named separately by SETUP 10.1
    # as the catalogue's AI entry points (the same files as ai/llms.txt and
    # ai/AGENTS.md; the spec lists both locations)
    shutil.copy2(AI / "llms.txt", web / "llms.txt")
    shutil.copy2(AI / "AGENTS.md", web / "AGENTS.md")

    # web/history.html: HISTORY.md rendered through the same pipeline
    scratch = PANDOC_DIR / "history-for-site.md"
    scratch.write_text(publish_history_text(
        (ROOT / "HISTORY.md").read_text(encoding="utf-8")), encoding="utf-8")
    run(["pandoc", "-f", "markdown-citations", str(scratch),
         "--standalone", "--metadata", "title=History and provenance",
         "--metadata", f"subtitle={site_stamp_line(meta, version)}",
         "-o", str(web / "history.html")], pandoc_env(meta["built"]))

    # web/references.html (IA-9): Appendix B as its own page — the deep-link
    # target for R-IDs. Rendered from markdown through the shared pipeline
    # (Lua filter on: the table's first header cell is "R-ID", so every row
    # anchors per R-ID), then audited: all 144 rows anchored, every R-link
    # the evidence pack emits resolves here, and every cited-by T/C/F link
    # resolves in the built evidence pack (mapped-but-missing is a hard
    # error; area tokens and labels degrade to plain text).
    refs_md, linked_cited, plain_cited = references_page_markdown(
        corpus, catalogue_manifest()["title"])
    refs_scratch = PANDOC_DIR / "references-for-site.md"
    refs_scratch.write_text(refs_md, encoding="utf-8")
    run(["pandoc", "-f", "markdown-citations", str(refs_scratch),
         "--standalone", "--lua-filter", str(write_anchor_filter()),
         "--include-in-header", str(web_header()),
         "--metadata", f"title=References — {catalogue_manifest()['title']}",
         "--metadata", f"subtitle={site_stamp_line(meta, version)}",
         "-o", str(web / "references.html")], pandoc_env(meta["built"]))
    refs_html = (web / "references.html").read_text(encoding="utf-8")
    row_anchors = refs_html.count('<span id="R-')
    if row_anchors != len(corpus.references):
        raise SystemExit(f"references page: expected "
                         f"{len(corpus.references)} anchored reference rows, "
                         f"found {row_anchors} — the anchor rendering changed "
                         "(IA-9)")
    pack_tokens = verify_pack_link_targets(corpus, refs_html)
    pack_html = (web / "evidence-pack.html").read_text(encoding="utf-8")
    cited_map = check.regenerate_cited_by(corpus)
    cited_targets = sorted({token for ids in cited_map.values()
                            for token in ids
                            if check.TCF_ID.fullmatch(token)})
    missing_cited = [token for token in cited_targets
                     if f'id="{token}"' not in pack_html]
    if missing_cited:
        raise SystemExit("references page cited-by links: no evidence-pack "
                         f"anchor for: {', '.join(missing_cited)} — every "
                         "emitted link target must exist (IA-9)")
    print(f"references page: {row_anchors} anchored reference rows; "
          f"cited-by — {linked_cited} T/C/F tokens linked (all targets "
          f"verified), {plain_cited} area/label tokens plain; evidence "
          f"pack R-links retargeted here: {pack_tokens} tokens")

    # web/index.html and the landing files, from the site templates
    manifest = catalogue_manifest()
    catalogues = site_catalogues()
    releases, placeholder = releases_url()
    env = site_env(SITE_ROOT_TEMPLATES)
    common = {"site_title": SITE_TITLE, "site_line": SITE_LINE,
              "catalogues": catalogues, "stamp": stamp}
    # IA-5: the root index's project-level doorway block (root-only; the
    # llms.txt doorway keeps the orientation one-liner).
    render_site(env, "index.html.j2", SITE / "index.html",
                doorway_paragraphs_html=(
                    orientation.site_doorway_paragraphs_html(catalogues)),
                **common)
    render_site(env, "llms.txt.j2", SITE / "llms.txt", **common)
    render_site(env, "robots.txt.j2", SITE / "robots.txt", **common)
    render_site(env, "404.html.j2", SITE / "404.html", **common)
    render_site(env, "_headers.j2", SITE / "_headers", **common)
    web_ctx = orientation.web_context()
    role_rows = web_ctx["role_table_rows_html"]
    linked_cells = sum(1 for row in role_rows for cell in row[1:]
                       if "<a " in cell)
    link_count = sum(cell.count("<a ") for row in role_rows
                     for cell in row[1:])
    print(f"web index: role table — {linked_cells} of "
          f"{sum(len(row) - 1 for row in role_rows)} cells linked "
          f"({link_count} links), the rest plain (IA-4)")
    render_site(site_env(SITE_WEB_TEMPLATES), "index.html.j2",
                web / "index.html", title=manifest["title"],
                status_line=SITE_STATUS.format(version=version), stamp=stamp,
                releases_url=releases,
                ai_files=sorted(p.name for p in AI.iterdir() if p.is_file()),
                **web_ctx)

    # allowlist audit: the built tree is exactly the allowlist, and no
    # archive/ or data/ path exists anywhere in it (SETUP 10.1). check.py
    # rule 11 re-proves this independently in release mode.
    built = sorted(str(path.relative_to(SITE)) for path in SITE.rglob("*")
                   if path.is_file())
    expected = site_allowlist()
    if built != expected:
        extra = sorted(set(built) - set(expected))
        missing = sorted(set(expected) - set(built))
        raise SystemExit(f"site allowlist violated: extra={extra} "
                         f"missing={missing}")
    for path in built:
        if "archive" in Path(path).parts or "data" in Path(path).parts:
            raise SystemExit(f"site contains {path}: archive/ and data/ are "
                             "never published (SETUP 10.1)")
    print(f"site: {len(built)} files in {SITE} (allowlist audit clean), "
          f"site version {version}"
          + (" (§5 stamp: " + meta["version"] + ")"
             if version != meta["version"] else ""))
    if placeholder:
        print(f"site: WARNING releases link is the placeholder "
              f"{RELEASES_FALLBACK} — set an origin remote so web/index.html "
              f"links this repository's releases (IMPORT-NOTES, stage 9)")


def site_tree(site: Path | None = None) -> str:
    """The site directory as an indented listing, for reports and CI logs."""
    site = site or SITE
    if not site.is_dir():
        return f"(no site at {site})"

    def walk(directory: Path, prefix: str, lines: list) -> None:
        for path in sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name)):
            if path.is_dir():
                lines.append(f"{prefix}{path.name}/")
                walk(path, prefix + "  ", lines)
            else:
                lines.append(f"{prefix}{path.name}")

    lines: list = []
    walk(site, "", lines)
    return "\n".join(lines)


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

    # 2. the three catalogue renders. The HTML render alone carries the
    # IA-13 width override; the DOCX render is a plain pandoc call. The
    # PDF renders in two steps (pandoc -> typst source -> post-process ->
    # typst compile) per the owner defect report: see postprocess_typst.
    web_header_arg = ["--include-in-header", str(web_header())]
    run(base_args(source, OUT / "catalogue.html", title, meta,
                  ["--standalone", "--toc", "--toc-depth=2"]
                  + web_header_arg), env)
    typ_path = PANDOC_DIR / "catalogue.typ"
    run(["pandoc", "-f", "markdown-citations", str(source),
         "--standalone", "--toc", "--toc-depth=2",
         "--metadata", f"title={title}",
         "--metadata", f"subtitle={stamp_line(meta)}",
         "-t", "typst", "-o", str(typ_path)], env)
    typ_path.write_text(postprocess_typst(typ_path.read_text(encoding="utf-8")),
                        encoding="utf-8")
    run(["typst", "compile",
         "--creation-timestamp", source_date_epoch(meta["built"]),
         str(typ_path), str(OUT / "catalogue.pdf")], env)
    run(base_args(source, OUT / "catalogue.docx", title, meta, []), env)

    # 3. the evidence pack
    corpus = check.Corpus(ROOT)
    pack_md = build_evidence_pack(corpus, meta, title)
    pack_path = OUT / "evidence-pack.md"
    pack_path.write_text(pack_md, encoding="utf-8")
    run(base_args(pack_path, OUT / "evidence-pack.html",
                  f"Evidence pack — {title}", meta,
                  ["--standalone", "--include-in-header",
                   str(web_header("urlwrap"))]),
        env)

    # IA-7 link audit: URL cells linked (the IA-8/IA-9 R-link audit runs in
    # the site step against the built references page). Counts stated
    # precisely (verifier finding 1): how many references carry a URL, how
    # many URL cells actually render in the pack (references cited only at
    # area level have no claim section, so no row), and that every rendered
    # cell is linked.
    in_claims = {rid for _path, claim in corpus.claims
                 for rid in claim.get("sources") or []}
    url_refs = {r["id"] for r in corpus.references if r.get("url")}
    rendered = sorted(url_refs & in_claims)
    unrendered = sorted(url_refs - in_claims)
    no_url = sorted({r["id"] for r in corpus.references} - url_refs)
    print(f"evidence pack: URL cells — {len(url_refs)} of "
          f"{len(corpus.references)} references carry a URL; {len(rendered)} "
          f"URL cells render in the pack ({', '.join(unrendered)} cited at "
          f"area level only, no pack row; {', '.join(no_url)} has no URL); "
          "every rendered cell is linked")

    # 4. the site step: build/site from the allowlist (SETUP 10.1)
    build_site(meta, corpus)
    print(site_tree())

    print(f"built: catalogue.html, catalogue.pdf, catalogue.docx, "
          f"evidence-pack.md, evidence-pack.html in {OUT}")
    print(f"stamp: {stamp_line(meta)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
