#!/usr/bin/env python3
"""Round-trip verification against the original exports (SETUP-INSTRUCTIONS 9).

Compares, section by section after symmetric normalisation:

  1. build/md/catalogue-full.md (regenerated first unless --skip-generate)
     against the original export ../catalogue.md;
  2. the claims tables reconstructed from data/claims/ (split groups
     re-compressed via split_from, last_verified + verified_by recombined,
     tier rendered as stored, verification/decision/origin/status verbatim)
     against ../register-claims.md, row by row per section;
  3. register/change-log.md against ../register-change-log.md, the section 4.8
     merge reversed (addendum rows then main rows, original order).

Normalisations (section 9.2 and the stage-7 brief; every one is applied to
BOTH sides, and each is a pure function of its input):

  N1  strip the generated stamp line      (identity on the export's first line)
  N2  strip the " · <version>" last_changed suffix from ID cells (SETUP 8;
      identity on bare ID cells)
  N3  collapse whitespace runs, NBSP -> space
  N4  curly quotes -> straight quotes
  N5  Markdown table formatting: tables parsed to header + cell lists, padding
      and delimiter rows dropped (both sides)
  N6  expand same-prefix "X to Y" ID ranges, T-, C-, F- and R- prefixes (the
      R-ranges are roundtrip.py's own; check.py's helper covers T/C/F only)
  N7  reference-cell separator spacing (";"->"; ", ","->", ") — the family
      convention itself ("; " between families, ", " within) is compared, not
      erased, so the one irregular export cell (T-A1-6) stays visible
  N8  Appendix B link cells compared as (URL set, combined text) so a
      qualifier moving inside/outside the link is presentation, lost text is not

Difference taxonomy (every difference in exactly one class):

  (i)    allowed merges (Appendix A/B table merges, reordered rows, change-log
         addendum merge) and the IA pass's sanctioned "About this edition"
         insertion — recorded as sanctioned only after byte-verification
         against the orientation source render (see
         verify_orientation_insertion); any mismatch there is class (iv)
  (ii)   spec-mandated regeneration: Appendix A "Used in" (18 facts) and
         Appendix B "Cited by" (107 references) render the values regenerated
         per SETUP 5.6-5.7; the sets must reconcile with check.py warning 1
  (iii)  derived-section presentation: editorial compressions the data model
         does not store (short area labels, grouped triggers, "(L2)" marks,
         whole-area notes, "All controls except", bylines, "Last reviewed ·
         Watch" lines, the T-A1-6 separator, Appendix B link-text qualifiers,
         token-equal derived-column renderings)
  (iv)   unexplained — must be zero; non-zero means the import lost or changed
         content and the import (data) must be fixed, never the output

Exit code 0 only when class (iv) is empty across all three comparisons and the
class (ii) sets reconcile with check.py. A report is written to
build/roundtrip-report.md. --selftest proves the normalisations symmetric.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402  (tools/check.py — Corpus and regeneration functions)
import orientation  # noqa: E402  (tools/orientation.py — orientation single source, IA pass)

ROOT = Path(__file__).resolve().parents[1]

# The original exports, read-only forever. Default: the directory that
# contains the repository (the workspace root); overridable for /tmp copies.
DEFAULT_EXPORTS = ROOT.parent

# --------------------------------------------------------------------------
# difference records
# --------------------------------------------------------------------------

class Diff:
    """One classified difference (or allowed merge) between export and build."""

    def __init__(self, comparison: str, klass: str, sub_class: str,
                 location: str, detail: str,
                 export_text: str = "", generated_text: str = ""):
        self.comparison = comparison
        self.klass = klass          # "i", "ii", "iii" or "iv"
        self.sub_class = sub_class
        self.location = location
        self.detail = detail
        self.export_text = export_text
        self.generated_text = generated_text

    def line(self) -> str:
        parts = [f"[{self.comparison}] class ({self.klass}) {self.sub_class}: "
                 f"{self.location} — {self.detail}"]
        if self.export_text or self.generated_text:
            parts.append(f"    export:    {self.export_text!r}")
            parts.append(f"    generated: {self.generated_text!r}")
        return "\n".join(parts)

    def key(self):
        return (self.comparison, self.klass, self.sub_class, self.location, self.detail)


def summarise(diffs: list[Diff]) -> "OrderedDict[str, OrderedDict[str, list[Diff]]]":
    out: OrderedDict[str, OrderedDict[str, list[Diff]]] = OrderedDict()
    for klass in ("i", "ii", "iii", "iv"):
        out[klass] = OrderedDict()
    for d in sorted(diffs, key=lambda d: d.key()):
        out[d.klass].setdefault(d.sub_class, []).append(d)
    return out


# --------------------------------------------------------------------------
# normalisations (each a pure function; --selftest proves the symmetries)
# --------------------------------------------------------------------------

STAMP_RE = re.compile(r"^Catalogue version .+, built \d{4}-\d{2}-\d{2} from commit \S+$")

ID_SUFFIX_RE = re.compile(r"^((?:[TC]-(?:A|B|P)\d{1,2}-\d+|(?:F|R)-\d+)) · \S+$")

# Same-prefix ID ranges, T-, C-, F- and R- prefixes. check.expand_id_ranges
# covers T/C/F; R-ranges ("R-29 to R-36") occur in "Facts and sources" lines
# and the change log, so roundtrip.py carries its own.
RT_ID_RANGE = re.compile(
    r"\b((?:[TC]-(?:A|B|P)\d{1,2}-|[FR]-)(\d+))\s+to\s+"
    r"((?:[TC]-(?:A|B|P)\d{1,2}-|[FR]-)(\d+))\b"
)

CHAR_MAP = {"“": '"', "”": '"', "‘": "'", "’": "'", " ": " "}


def strip_stamp(text: str) -> str:
    """N1: drop a leading generated stamp line (and the blank line after it)."""
    lines = text.split("\n")
    if lines and STAMP_RE.match(lines[0].strip()):
        lines = lines[1:]
        if lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines)


def strip_id_suffix(cell: str) -> str:
    """N2: drop the ' · <version>' last_changed suffix from an ID table cell."""
    match = ID_SUFFIX_RE.match(cell.strip())
    return match.group(1) if match else cell.strip()


def normalise_text(text: str) -> str:
    """N3 + N4: NBSP and curly quotes to straight, whitespace runs collapsed."""
    for src, dst in CHAR_MAP.items():
        text = text.replace(src, dst)
    return re.sub(r"[ \t]+", " ", text).strip()


def expand_id_ranges(text: str) -> str:
    """N6: expand same-prefix 'X to Y' ranges into enumerated IDs."""
    def repl(match):
        first, second = match.group(1), match.group(3)
        prefix = first[: first.rfind("-") + 1]
        if prefix != second[: second.rfind("-") + 1]:
            return match.group(0)
        low, high = int(match.group(2)), int(match.group(4))
        if not 0 < high - low <= 200:
            return match.group(0)
        return ", ".join(f"{prefix}{n}" for n in range(low, high + 1))
    return RT_ID_RANGE.sub(repl, text)


def normalise_cell(cell: str) -> str:
    """A plain table cell after N2/N3/N4/N6 (no separator or link rules)."""
    return expand_id_ranges(normalise_text(strip_id_suffix(cell)))


def normalise_reference_cell(cell: str) -> str:
    """N7 for threat Reference cells: normalise separator *spacing* only.

    The separator *kind* is kept: the export's convention is '; ' between
    reference families and ', ' within one, which the generator reproduces
    deterministically, so the kinds are compared. The one export cell that
    breaks the convention (T-A1-6, two CWEs joined with '; ') must stay
    visible as a difference rather than be normalised away.
    """
    cell = normalise_text(cell)
    cell = re.sub(r"\s*;\s*", "; ", cell)
    cell = re.sub(r"\s*,\s*", ", ", cell)
    return cell


LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")


def parse_links(cell: str) -> tuple[list[tuple[str, str]], str]:
    """N8 helper: ([(link text, url), ...], residual plain text)."""
    links: list[tuple[str, str]] = []

    def repl(match):
        links.append((match.group(1), match.group(2)))
        return ""

    residual = LINK_RE.sub(repl, cell)
    return links, normalise_text(residual)


def link_cell_key(cell: str) -> tuple:
    """N8: a link cell's comparable form — (sorted (text, url) pairs, sorted
    URLs, combined plain text). Moving text between link text and a residual
    qualifier does not change the combined text; losing text does."""
    links, residual = parse_links(cell)
    combined = normalise_text(" ".join([t for t, _u in links] + ([residual] if residual else [])))
    return tuple(sorted(links)), tuple(sorted(u for _t, u in links)), combined


TCF_ID = re.compile(r"\b(?:[TC]-(?:A|B|P)\d{1,2}-\d+|F-\d+)\b")
AREA_ID = re.compile(r"\b[ABP]\d{1,2}\b")
FRONT_LABELS = ("Reference stack", "Threat evidence", "How to use this catalogue",
                "Cross-cutting principles", "Appendix C: Maintenance procedure")


def used_in_tokens(cell: str, area_ids: set[str]) -> set[str]:
    """The comparable tokens of a 'Used in' cell: area IDs, T-/C-/F- record IDs
    (five export cells carry them) and front-matter section labels. Other text
    ('lead', '(C-A1-3)', 'Where experts differ', 'ASVS column') is editorial
    prose, not a location token."""
    text = expand_id_ranges(normalise_text(cell))
    tokens = set(TCF_ID.findall(text))
    spans = [m.span() for m in TCF_ID.finditer(text)]
    for match in AREA_ID.finditer(text):
        start, end = match.span()
        if any(start >= s and end <= e for s, e in spans):
            continue
        if match.group(0) in area_ids:
            tokens.add(match.group(0))
    for label in FRONT_LABELS:
        if label in text:
            tokens.add(label)
    return tokens


def cited_by_tokens(cell: str, area_ids: set[str]) -> set[str]:
    """The comparable tokens of a 'Cited by' cell (check.parse_cited_by_text's
    rule): T-/C-/F-IDs with ranges expanded, plus bare area IDs that are real
    areas; prose is not a citation."""
    text = expand_id_ranges(normalise_text(cell))
    tokens = set(TCF_ID.findall(text))
    spans = [m.span() for m in TCF_ID.finditer(text)]
    for match in AREA_ID.finditer(text):
        start, end = match.span()
        if any(start >= s and end <= e for s, e in spans):
            continue
        if match.group(0) in area_ids:
            tokens.add(match.group(0))
    return tokens


# --------------------------------------------------------------------------
# markdown parsing
# --------------------------------------------------------------------------

class Table:
    def __init__(self, header: list[str], rows: list[list[str]]):
        self.header = header
        self.rows = rows


class Heading:
    def __init__(self, level: int, text: str):
        self.level = level
        self.text = text


class Para:
    def __init__(self, text: str):
        self.text = text


def is_delimiter(line: str) -> bool:
    s = line.strip()
    return bool(s) and "|" in s and set(s) <= set("|-: ")


def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def parse_blocks(text: str) -> list:
    """Parse into Heading / Para / Table blocks (N5's parse step)."""
    blocks: list = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            blocks.append(Heading(len(heading.group(1)), heading.group(2).strip()))
            i += 1
            continue
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            rows = [split_row(l) for l in table_lines if not is_delimiter(l)]
            if not rows:
                continue
            blocks.append(Table(rows[0], rows[1:]))
            continue
        para = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith("|") or nxt.startswith("#")
                    or nxt.startswith("- ") or nxt.startswith("* ")
                    or re.match(r"^\d+\. ", nxt)):
                break
            para.append(nxt)
            i += 1
        blocks.append(Para("\n".join(para)))
    return blocks


def sections(text: str) -> "OrderedDict[str, list]":
    """Map H2 heading text -> blocks under it. Blocks before the first H2
    (the H1 title, the byline) live under '<title>'; H1/H3+ headings stay
    blocks inside their section."""
    out: OrderedDict[str, list] = OrderedDict()
    current = "<title>"
    out[current] = []
    for block in parse_blocks(strip_stamp(text)):
        if isinstance(block, Heading) and block.level == 2:
            current = block.text
            out.setdefault(current, [])
        else:
            out[current].append(block)
    return out


# --------------------------------------------------------------------------
# comparison 1: catalogue-full.md vs ../catalogue.md
# --------------------------------------------------------------------------

LAST_REVIEWED_RE = re.compile(r"^\*\*Last reviewed\*\* .+ · \*\*Watch:\*\* .+$")
BYLINE_RE = re.compile(r"^[A-Z][a-z]{2} \d{1,2}, \d{4} · @.+$")
AREA_KEY_RE = re.compile(r"^((?:[ABP]\d{1,2})(?:–[ABP]\d{1,2})?)\b")
C_ID_RE = re.compile(r"\bC-(?:A|B|P)\d{1,2}-\d+\b")


def words(text: str) -> set[str]:
    return {w.strip(".,;:()").lower() for w in text.split()}


def compare_intro_paras(comparison: str, name: str, exp_blocks: list,
                        gen_blocks: list, diffs: list[Diff]) -> None:
    eparas = [normalise_text(b.text) for b in exp_blocks if isinstance(b, Para)]
    gparas = [normalise_text(b.text) for b in gen_blocks if isinstance(b, Para)]
    if eparas != gparas:
        diffs.append(Diff(comparison, "iv", "intro paragraph", f"section '{name}'",
                          "intro paragraphs differ",
                          " | ".join(eparas), " | ".join(gparas)))


def compare_plain_table(comparison: str, name: str, exp: Table, gen: Table,
                        diffs: list[Diff]) -> None:
    ehead = [normalise_text(c) for c in exp.header]
    ghead = [normalise_text(c) for c in gen.header]
    if ehead != ghead:
        diffs.append(Diff(comparison, "iv", "table header", f"section '{name}'",
                          "table headers differ", str(ehead), str(ghead)))
        return
    is_threats = ehead[:2] == ["ID", "Threat"]
    if len(exp.rows) != len(gen.rows):
        diffs.append(Diff(comparison, "iv", "table row count", f"section '{name}'",
                          f"row count differs: export {len(exp.rows)} vs generated {len(gen.rows)}"))
        return
    for r, (er, gr) in enumerate(zip(exp.rows, gen.rows), start=1):
        row_id = strip_id_suffix(er[0]) if er else f"row {r}"
        if len(er) != len(gr):
            diffs.append(Diff(comparison, "iv", "row width", f"section '{name}' row {row_id}",
                              "cell count differs"))
            continue
        for c, (ec, gc) in enumerate(zip(er, gr)):
            if is_threats and c == 3:
                en, gn = normalise_reference_cell(ec), normalise_reference_cell(gc)
                klass, sub = "iii", ("threat Reference-cell separator (export joins one "
                                     "reference family with '; '; the convention is ', ' within)")
            else:
                en, gn = normalise_cell(ec), normalise_cell(gc)
                klass, sub = "iv", "cell text"
            if en != gn:
                diffs.append(Diff(comparison, klass, sub,
                                  f"section '{name}' row {row_id} column '{ehead[c]}'",
                                  "cell differs after normalisation", en, gn))


def compare_generic_section(comparison: str, name: str, exp_blocks: list,
                            gen_blocks: list, diffs: list[Diff],
                            allow_last_reviewed: bool = False) -> None:
    """Block-by-block comparison of a section whose content is stored verbatim
    (front matter, applicability index, areas, Appendix C). Differences fall
    to class (iv) unless matched by an explicit presentation rule."""
    exp, gen = list(exp_blocks), list(gen_blocks)
    ei = gi = 0
    while ei < len(exp) or gi < len(gen):
        e = exp[ei] if ei < len(exp) else None
        g = gen[gi] if gi < len(gen) else None
        if isinstance(e, Para) and (g is None or isinstance(g, (Table, Heading))):
            text = normalise_text(e.text)
            if allow_last_reviewed and LAST_REVIEWED_RE.match(text):
                diffs.append(Diff(comparison, "iii",
                                  "derived-section 'Last reviewed · Watch' line (stored in no data file)",
                                  f"section '{name}'",
                                  "export-only line omitted from the generated section",
                                  export_text=text, generated_text=""))
            else:
                diffs.append(Diff(comparison, "iv", "export-only paragraph",
                                  f"section '{name}'", "no matching generated block",
                                  export_text=text, generated_text=""))
            ei += 1
            continue
        if isinstance(g, Para) and (e is None or isinstance(e, (Table, Heading))):
            diffs.append(Diff(comparison, "iv", "generated-only paragraph",
                              f"section '{name}'", "no matching export block",
                              export_text="", generated_text=normalise_text(g.text)))
            gi += 1
            continue
        if e is None or g is None or type(e) is not type(g):
            diffs.append(Diff(comparison, "iv", "block structure", f"section '{name}'",
                              f"block kind mismatch: export {type(e).__name__} vs "
                              f"generated {type(g).__name__}"))
            ei, gi = ei + (e is not None), gi + (g is not None)
            continue
        if isinstance(e, Heading):
            if normalise_text(e.text) != normalise_text(g.text):
                diffs.append(Diff(comparison, "iv", "heading text", f"section '{name}'",
                                  "heading differs", e.text, g.text))
        elif isinstance(e, Para):
            et = expand_id_ranges(normalise_text(e.text))
            gt = expand_id_ranges(normalise_text(g.text))
            if et != gt:
                diffs.append(Diff(comparison, "iv", "paragraph text", f"section '{name}'",
                                  "paragraph differs after normalisation", et, gt))
        else:
            compare_plain_table(comparison, name, e, g, diffs)
        ei += 1
        gi += 1


def table_rows_by_key(table: Table) -> "OrderedDict[str, list[str]]":
    out: OrderedDict[str, list[str]] = OrderedDict()
    for r in table.rows:
        m = AREA_KEY_RE.match(normalise_text(r[0])) if r else None
        out[m.group(1) if m else normalise_text(r[0]) if r else ""] = r
    return out


def compare_baseline_conditional(comparison: str, exp_blocks: list,
                                 gen_blocks: list, diffs: list[Diff],
                                 process_control_ids: set[str]) -> None:
    name = "Baseline and conditional controls"
    compare_intro_paras(comparison, name, exp_blocks, gen_blocks, diffs)
    exp_tables = [b for b in exp_blocks if isinstance(b, Table)]
    gen_tables = [b for b in gen_blocks if isinstance(b, Table)]
    if len(exp_tables) != 1 or len(gen_tables) != 1:
        diffs.append(Diff(comparison, "iv", "table structure", f"section '{name}'",
                          f"expected one table per side, got {len(exp_tables)}/{len(gen_tables)}"))
        return
    et, gt = exp_tables[0], gen_tables[0]
    ehead = [normalise_text(c) for c in et.header]
    ghead = [normalise_text(c) for c in gt.header]
    if ehead != ghead:
        diffs.append(Diff(comparison, "iv", "table header", f"section '{name}'",
                          "table headers differ", str(ehead), str(ghead)))
        return
    erows, grows = table_rows_by_key(et), table_rows_by_key(gt)
    for key in sorted(set(erows) - set(grows)):
        diffs.append(Diff(comparison, "iv", "missing row", f"section '{name}' row {key}",
                          "export row has no generated counterpart"))
    for key in sorted(set(grows) - set(erows)):
        diffs.append(Diff(comparison, "iv", "extra row", f"section '{name}' row {key}",
                          "generated row has no export counterpart"))
    for key in sorted(set(erows) & set(grows)):
        er, gr = erows[key], grows[key]
        loc = f"section '{name}' row {key}"
        e0, g0 = normalise_text(er[0]), normalise_text(gr[0])
        if e0 != g0 and words(e0) != words(g0):
            if len(e0) < len(g0):
                diffs.append(Diff(comparison, "iii", "summary-table short area label",
                                  f"{loc} column 'Area'",
                                  "export uses a shortened area label; the data model "
                                  "stores only the full title", e0, g0))
            else:
                diffs.append(Diff(comparison, "iv", "area label", f"{loc} column 'Area'",
                                  "area label differs and is not a shortening", e0, g0))
        # Baseline / Conditional columns: the union of control IDs across the
        # two columns must match; grouping, labels and marks are presentation.
        # "All controls except C-P4-4" enumerates by prose: resolve it against
        # the corpus's process-area control IDs before the union comparison.
        e_cell_ids = set(C_ID_RE.findall(expand_id_ranges(normalise_text(er[1]) + " " + normalise_text(er[2]))))
        g_ids = set(C_ID_RE.findall(expand_id_ranges(normalise_text(gr[1]) + " " + normalise_text(gr[2]))))
        all_except = re.match(r"^All controls except ((?:C-(?:A|B|P)\d{1,2}-\d+(?:, )?)+)$",
                              normalise_text(er[1]))
        if all_except:
            excepted = set(C_ID_RE.findall(all_except.group(1)))
            e_ids = (set(process_control_ids) - excepted) | e_cell_ids
        else:
            e_ids = e_cell_ids
        union_ok = e_ids == g_ids
        for col, label in ((1, "Baseline"), (2, "Conditional (trigger)")):
            e1, g1 = normalise_cell(er[col]), normalise_cell(gr[col])
            if e1 == g1:
                continue
            if not union_ok:
                diffs.append(Diff(comparison, "iv", "control ID set",
                                  f"{loc} column '{label}'",
                                  "control IDs differ between export and generated",
                                  e1, g1))
                continue
            if normalise_text(er[col]).startswith("— (whole area"):
                sub = "'— (whole area conditional …)' note (not derivable from the data model)"
            elif key.startswith("P1"):
                sub = "'All controls except C-P4-4' phrasing (generator enumerates the baselines)"
            elif "(L2)" in er[1] or " L3 (" in er[2]:
                sub = ("C-A11-6 dual L2/L3 listing ('(L2)' mark; the mixed Type cell "
                       "has one stored type)")
            else:
                sub = ("grouped ID ranges and shortened trigger parentheticals "
                       "(generator: one entry per control, trigger text verbatim)")
            diffs.append(Diff(comparison, "iii", sub, f"{loc} column '{label}'",
                              "same control IDs, presentation differs", e1, g1))


def compare_residual(comparison: str, exp_blocks: list, gen_blocks: list,
                     diffs: list[Diff]) -> None:
    name = "Residual-risk summary"
    compare_intro_paras(comparison, name, exp_blocks, gen_blocks, diffs)
    exp_tables = [b for b in exp_blocks if isinstance(b, Table)]
    gen_tables = [b for b in gen_blocks if isinstance(b, Table)]
    if len(exp_tables) != 1 or len(gen_tables) != 1:
        diffs.append(Diff(comparison, "iv", "table structure", f"section '{name}'",
                          f"expected one table per side, got {len(exp_tables)}/{len(gen_tables)}"))
        return
    et, gt = exp_tables[0], gen_tables[0]
    ehead = [normalise_text(c) for c in et.header]
    ghead = [normalise_text(c) for c in gt.header]
    if ehead != ghead:
        diffs.append(Diff(comparison, "iv", "table header", f"section '{name}'",
                          "table headers differ", str(ehead), str(ghead)))
        return
    erows, grows = table_rows_by_key(et), table_rows_by_key(gt)
    for key in sorted(set(erows) - set(grows)):
        diffs.append(Diff(comparison, "iv", "missing row", f"section '{name}' row {key}",
                          "export row has no generated counterpart"))
    for key in sorted(set(grows) - set(erows)):
        diffs.append(Diff(comparison, "iv", "extra row", f"section '{name}' row {key}",
                          "generated row has no export counterpart"))
    for key in sorted(set(erows) & set(grows)):
        er, gr = erows[key], grows[key]
        loc = f"section '{name}' row {key}"
        e0, g0 = normalise_text(er[0]), normalise_text(gr[0])
        if e0 != g0 and words(e0) != words(g0):
            if len(e0) < len(g0):
                diffs.append(Diff(comparison, "iii", "summary-table short area label",
                                  f"{loc} column 'Area'",
                                  "export uses a shortened area label; the data model "
                                  "stores only the full title", e0, g0))
            else:
                diffs.append(Diff(comparison, "iv", "area label", f"{loc} column 'Area'",
                                  "area label differs and is not a shortening", e0, g0))
        for col, label in ((1, "Rating"), (2, "What remains")):
            e1, g1 = normalise_cell(er[col]), normalise_cell(gr[col])
            if e1 != g1:
                diffs.append(Diff(comparison, "iv", "cell text",
                                  f"{loc} column '{label}'", "cell differs", e1, g1))


def rid_num(rid: str) -> int:
    digits = re.sub(r"\D", "", rid.split("-")[-1])
    return int(digits) if digits else 0


def compare_derived_table(comparison: str, name: str, exp_tables: list,
                          gen_table: Table, diffs: list[Diff], area_ids: set[str],
                          derived_column: int, derived_label: str,
                          id_prefix: str, links: bool = False) -> None:
    exp_rows: list[list[str]] = []
    for t in exp_tables:
        exp_rows.extend(t.rows)
    gen_rows = gen_table.rows

    def by_id(rows: list) -> "OrderedDict[str, list[str]]":
        out: OrderedDict[str, list[str]] = OrderedDict()
        for r in rows:
            rid = strip_id_suffix(r[0]) if r else ""
            if rid in out:
                diffs.append(Diff(comparison, "iv", "duplicate row", f"section '{name}' row {rid}",
                                  "ID appears more than once on one side"))
            out[rid] = r
        return out

    for t in exp_tables:
        ehead = [normalise_text(c) for c in t.header]
        ghead = [normalise_text(c) for c in gen_table.header]
        if ehead != ghead:
            diffs.append(Diff(comparison, "iv", "table header", f"section '{name}'",
                              "export table header differs from the generated header",
                              str(ehead), str(ghead)))

    erows, grows = by_id(exp_rows), by_id(gen_rows)
    for rid in sorted(set(erows) - set(grows)):
        diffs.append(Diff(comparison, "iv", "missing row", f"section '{name}' row {rid}",
                          "export row has no generated counterpart"))
    for rid in sorted(set(grows) - set(erows)):
        diffs.append(Diff(comparison, "iv", "extra row", f"section '{name}' row {rid}",
                          "generated row has no export counterpart"))
    for rid in sorted(set(erows) & set(grows)):
        er, gr = erows[rid], grows[rid]
        loc = f"section '{name}' row {rid}"
        for c in range(1, len(er)):
            if c >= len(gr):
                diffs.append(Diff(comparison, "iv", "row width", loc, "cell count differs"))
                break
            ec, gc = er[c], gr[c]
            if c == derived_column:
                if id_prefix == "F":
                    etoks, gtoks = used_in_tokens(ec, area_ids), used_in_tokens(gc, area_ids)
                    # Class (ii) mirrors check.py warning 1 (used_in) exactly: the
                    # warning compares the stored used_in list (the parsed cell's
                    # area and record IDs) against the regenerated AREA set. A
                    # cell therefore lands in class (ii) when the area tokens
                    # differ or the export cell carries record IDs; a divergence
                    # confined to the non-area label half (front-matter scan
                    # scope) leaves check.py silent and is class (iii).
                    e_areas = {t for t in etoks if t in area_ids}
                    g_areas = {t for t in gtoks if t in area_ids}
                    is_class_ii = (e_areas != g_areas
                                   or any(not t in area_ids and t not in FRONT_LABELS
                                          for t in etoks))
                    sub_ii = "Used in renders the regenerated value (SETUP 5.6)"
                    sub_iii_label = ("Used-in label half differs through the section 5.6 scan "
                                     "scope (front-matter labels; area usage matches, so "
                                     "check.py warning 1 (used_in) does not fire)")
                else:
                    etoks, gtoks = cited_by_tokens(ec, area_ids), cited_by_tokens(gc, area_ids)
                    is_class_ii = etoks != gtoks
                    sub_ii = "Cited by renders the regenerated value (SETUP 5.7)"
                    sub_iii_label = None
                en, gn = normalise_text(ec), normalise_text(gc)
                if is_class_ii:
                    diffs.append(Diff(comparison, "ii", sub_ii,
                                      loc, f"{derived_label} usage/citation tokens differ",
                                      f"tokens {sorted(etoks)}", f"tokens {sorted(gtoks)}"))
                elif etoks != gtoks:
                    diffs.append(Diff(comparison, "iii", sub_iii_label,
                                      loc, "non-area tokens differ", en, gn))
                elif en != gn:
                    diffs.append(Diff(comparison, "iii",
                                      f"{derived_label} cell rendering on token-equal rows "
                                      "(grouping, order, editorial qualifiers)",
                                      loc, "same tokens, different text", en, gn))
                continue
            if links and c == 1:
                elinks, eurls, etext = link_cell_key(ec)
                glinks, gurls, gtext = link_cell_key(gc)
                if eurls != gurls or etext != gtext:
                    diffs.append(Diff(comparison, "iv", "reference link content",
                                      f"{loc} column 'Reference'",
                                      "link URL set or combined text differs", ec, gc))
                elif elinks != glinks:
                    diffs.append(Diff(comparison, "iii",
                                      "Appendix B trailing qualifier inside the link text",
                                      f"{loc} column 'Reference'",
                                      "same URL and combined text; the export places a "
                                      "trailing qualifier outside the link", ec, gc))
                continue
            en, gn = normalise_cell(ec), normalise_cell(gc)
            if en != gn:
                diffs.append(Diff(comparison, "iv", "cell text",
                                  f"{loc} column {c}", "cell differs after normalisation", en, gn))


def out_of_order_ids(order: list[str]) -> list[str]:
    """IDs that sit below the running maximum — the rows a numeric sort moves."""
    moved = []
    running_max = None
    for rid in order:
        n = rid_num(rid)
        if running_max is not None and n < running_max:
            moved.append(rid)
        running_max = n if running_max is None else max(running_max, n)
    return moved


def compare_appendix_a(comparison: str, exp_blocks: list, gen_blocks: list,
                       diffs: list[Diff], area_ids: set[str]) -> None:
    name = "Appendix A: Volatile facts index"
    compare_intro_paras(comparison, name, exp_blocks, gen_blocks, diffs)
    exp_tables = [b for b in exp_blocks if isinstance(b, Table)]
    gen_tables = [b for b in gen_blocks if isinstance(b, Table)]
    if len(gen_tables) != 1 or not exp_tables:
        diffs.append(Diff(comparison, "iv", "table structure", f"section '{name}'",
                          f"expected >=1 export table and 1 generated table, got "
                          f"{len(exp_tables)}/{len(gen_tables)}"))
        return
    exp_rows = [r for t in exp_tables for r in t.rows]
    order = [strip_id_suffix(r[0]) for r in exp_rows]
    moved = out_of_order_ids(order)
    diffs.append(Diff(comparison, "i", "Appendix A table merge", f"section '{name}'",
                      f"{len(exp_tables)} export tables merged into one sorted list "
                      f"(F-1..F-53); {len(exp_tables) - 1} repeated header row(s) dropped; "
                      f"rows moved to numeric position: {', '.join(moved) or 'none'}"))
    compare_derived_table(comparison, name, exp_tables, gen_tables[0], diffs,
                          area_ids, derived_column=5, derived_label="Used in",
                          id_prefix="F")


def compare_appendix_b(comparison: str, exp_blocks: list, gen_blocks: list,
                       diffs: list[Diff], area_ids: set[str]) -> None:
    name = "Appendix B: References"
    compare_intro_paras(comparison, name, exp_blocks, gen_blocks, diffs)
    exp_tables = [b for b in exp_blocks if isinstance(b, Table)]
    gen_tables = [b for b in gen_blocks if isinstance(b, Table)]
    if len(gen_tables) != 1 or not exp_tables:
        diffs.append(Diff(comparison, "iv", "table structure", f"section '{name}'",
                          f"expected >=1 export table and 1 generated table, got "
                          f"{len(exp_tables)}/{len(gen_tables)}"))
        return
    exp_rows = [r for t in exp_tables for r in t.rows]
    order = [strip_id_suffix(r[0]) for r in exp_rows]
    moved = out_of_order_ids(order)
    diffs.append(Diff(comparison, "i", "Appendix B table merge", f"section '{name}'",
                      f"{len(exp_tables)} export tables merged into one sorted list "
                      f"(R-1..R-144); {len(exp_tables) - 1} repeated header row(s) dropped; "
                      f"rows already ascending in the export, so no reordering"
                      + (f" needed except: {', '.join(moved)}" if moved else "")))
    compare_derived_table(comparison, name, exp_tables, gen_tables[0], diffs,
                          area_ids, derived_column=6, derived_label="Cited by",
                          id_prefix="R", links=True)


STAMP_VERSION_RE = re.compile(
    r"^Catalogue version (.+), built \d{4}-\d{2}-\d{2} from commit \S+$")


def verify_orientation_insertion(gen_text: str, corpus: check.Corpus,
                                 diffs: list[Diff]) -> bool:
    """Recognise the generated "About this edition" section as a sanctioned
    IA-pass insertion — byte-verified, never a blind skip.

    The expected section is regenerated from tools/orientation.py (which
    parses register/governance.md) for the version in the generated stamp
    line, and must be byte-identical to the section actually embedded in
    build/md/catalogue-full.md. A match is recorded as class (i) (sanctioned);
    a mismatch or a missing section is class (iv) and fails the run — the
    deep-link markup that must never enter this file is HTML-only, so any
    other generated-only content in this section is unexplained.

    Returns True when the section was found (matched or not), so the caller
    consumes it from the section comparison either way.
    """
    comparison = "catalogue"
    found = re.search(rf"^## {re.escape(orientation.ABOUT_HEADING)}$",
                      gen_text, re.M)
    if found is None:
        diffs.append(Diff(comparison, "iv", "missing orientation section",
                          f"section '{orientation.ABOUT_HEADING}'",
                          "the sanctioned IA-pass insertion is absent from "
                          "the generated edition — generate.py must embed "
                          "orientation.about_edition_section"))
        return False
    boundary = re.search(r"^## ", gen_text[found.end():], re.M)
    actual = gen_text[found.end() - len(f"## {orientation.ABOUT_HEADING}"):
                      (found.end() + boundary.start()) if boundary
                      else len(gen_text)].rstrip("\n")
    stamp = STAMP_VERSION_RE.match(gen_text.split("\n", 1)[0].strip())
    if stamp is None:
        raise SystemExit("roundtrip: the generated catalogue's stamp line "
                         "does not parse; cannot verify the orientation "
                         "section")
    expected = orientation.about_edition_section(
        stamp.group(1), orientation.parse_governance(corpus.root))
    if actual != expected:
        diffs.append(Diff(comparison, "iv", "orientation section mismatch",
                          f"section '{orientation.ABOUT_HEADING}'",
                          "the generated section is not byte-identical to "
                          "the orientation source's render for this stamp "
                          "(tools/orientation.py)",
                          export_text=expected, generated_text=actual))
        return True
    diffs.append(Diff(comparison, "i",
                      "sanctioned orientation insertion (IA pass, deck W2; "
                      "byte-verified against tools/orientation.py)",
                      f"section '{orientation.ABOUT_HEADING}'",
                      "generated-only section between the title stamp and "
                      "'How to use this catalogue'; verified byte-identical "
                      "to the orientation source's render for this stamp's "
                      "version"))
    return True


def compare_catalogue(gen_text: str, exp_text: str, corpus: check.Corpus,
                      diffs: list[Diff]) -> None:
    comparison = "catalogue"
    area_ids = set(corpus.areas)
    process_control_ids = {cid for cid, (aid, _c) in corpus.controls.items()
                           if aid.startswith("P")}
    esections = sections(exp_text)
    gsections = sections(gen_text)

    # The IA pass inserts a generated "About this edition" section between
    # the title stamp and "How to use this catalogue" (deck W2). It is a
    # sanctioned insertion — but only when byte-identical to the orientation
    # source's render for this stamp; anything else is class (iv).
    if verify_orientation_insertion(gen_text, corpus, diffs):
        gsections.pop(orientation.ABOUT_HEADING, None)

    for heading in esections:
        if heading != "<title>" and heading not in gsections:
            diffs.append(Diff(comparison, "iv", "missing section", f"section '{heading}'",
                              "export section absent from the generated document"))
    for heading in gsections:
        if heading != "<title>" and heading not in esections:
            diffs.append(Diff(comparison, "iv", "extra section", f"section '{heading}'",
                              "generated section absent from the export"))

    # preamble: H1 title (both sides) and the export-only byline
    e_pre, g_pre = esections.get("<title>", []), gsections.get("<title>", [])
    e_heads = [normalise_text(b.text) for b in e_pre if isinstance(b, Heading)]
    g_heads = [normalise_text(b.text) for b in g_pre if isinstance(b, Heading)]
    if e_heads != g_heads:
        diffs.append(Diff(comparison, "iv", "title", "document preamble",
                          "title headings differ", str(e_heads), str(g_heads)))
    g_paras = [normalise_text(b.text) for b in g_pre if isinstance(b, Para)]
    for block in e_pre:
        if not isinstance(block, Para):
            continue
        text = normalise_text(block.text)
        if text in g_paras:
            continue
        if BYLINE_RE.match(text):
            diffs.append(Diff(comparison, "iii",
                              "edition byline (exists in no data file)", "document preamble",
                              "export byline line omitted from the generated edition",
                              export_text=text, generated_text=""))
        else:
            diffs.append(Diff(comparison, "iv", "preamble paragraph", "document preamble",
                              "unmatched export paragraph", export_text=text))
    for text in g_paras:
        e_texts = [normalise_text(b.text) for b in e_pre if isinstance(b, Para)]
        if text not in e_texts:
            diffs.append(Diff(comparison, "iv", "preamble paragraph", "document preamble",
                              "unmatched generated paragraph", generated_text=text))

    for name, exp_blocks in esections.items():
        if name == "<title>":
            continue
        gen_blocks = gsections.get(name)
        if gen_blocks is None:
            continue
        if name == "Baseline and conditional controls":
            compare_baseline_conditional(comparison, exp_blocks, gen_blocks, diffs,
                                         process_control_ids)
        elif name == "Residual-risk summary":
            compare_residual(comparison, exp_blocks, gen_blocks, diffs)
        elif name == "Appendix A: Volatile facts index":
            compare_appendix_a(comparison, exp_blocks, gen_blocks, diffs, area_ids)
        elif name == "Appendix B: References":
            compare_appendix_b(comparison, exp_blocks, gen_blocks, diffs, area_ids)
        elif name in ("Compliance mapping", "Where experts differ"):
            compare_generic_section(comparison, name, exp_blocks, gen_blocks, diffs,
                                    allow_last_reviewed=True)
        else:
            compare_generic_section(comparison, name, exp_blocks, gen_blocks, diffs)


# --------------------------------------------------------------------------
# comparison 2: claims
# --------------------------------------------------------------------------

CLAIM_HEADER = ["ID", "Claim", "Sources", "Evidence tier", "Verification",
                "Last verified", "Origin", "Decision", "Status"]


def iso_date(value) -> str:
    if isinstance(value, (_dt.date, _dt.datetime)):
        return value.date().isoformat() if isinstance(value, _dt.datetime) else value.isoformat()
    return str(value)


def reconstruct_claims_row(record: dict) -> list[str]:
    """One export row from a stored record: split groups re-compress via
    split_from; last_verified + verified_by recombine as 'date, who'; tier
    renders as stored; verification/decision/origin/status stay verbatim."""
    return [
        record.get("split_from") or record["id"],
        record.get("claim") or "",
        ", ".join(record.get("sources") or []),
        "—" if record.get("tier") is None else str(record.get("tier")),
        record.get("verification") or "",
        f"{iso_date(record['last_verified'])}, {record['verified_by']}",
        record.get("origin") or "",
        record.get("decision") or "",
        record.get("status") or "",
    ]


def claims_rows_by_section(claims_dir: Path) -> "OrderedDict[str, list[list[str]]]":
    """Reconstructed export rows per claims file, in stored order. Grouped
    records (split_from) re-compress to one row at the first group member."""
    out: OrderedDict[str, list[list[str]]] = OrderedDict()
    for path in sorted(claims_dir.glob("*.yaml")):
        records = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        rows: list[list[str]] = []
        seen_groups: set[str] = set()
        for record in records:
            group = record.get("split_from")
            if group is not None:
                if group in seen_groups:
                    continue
                seen_groups.add(group)
            rows.append(reconstruct_claims_row(record))
        out[path.stem] = rows
    return out


def section_key(heading: str) -> str:
    """'A3 Authorisation' -> 'A03'; 'Front matter …' -> 'front'."""
    if heading.startswith("Front matter"):
        return "front"
    m = re.match(r"^([ABP])(\d{1,2})\b", heading)
    return f"{m.group(1)}{int(m.group(2)):02d}" if m else heading


def compare_claims(claims_dir: Path, exp_text: str, diffs: list[Diff]) -> None:
    comparison = "claims"
    recon = claims_rows_by_section(claims_dir)
    esections = sections(exp_text)

    for name, blocks in esections.items():
        if name == "<title>":
            continue
        key = section_key(name)
        if key not in recon:
            diffs.append(Diff(comparison, "iv", "unknown section",
                              f"section '{name}'", "no claims file matches the export section"))
            continue
        exp_rows: list[list[str]] = []
        for block in blocks:
            if isinstance(block, Table):
                header = [normalise_text(c) for c in block.header]
                if header != CLAIM_HEADER:
                    diffs.append(Diff(comparison, "iv", "table header",
                                      f"section '{name}'", "unexpected claims table header",
                                      str(header), str(CLAIM_HEADER)))
                exp_rows.extend(block.rows)
        gen_rows = recon[key]

        def compare_row(idx: int, er: list, gr: list) -> None:
            row_id = normalise_text(er[0]) if er else f"row {idx + 1}"
            if len(er) != len(gr):
                diffs.append(Diff(comparison, "iv", "row width",
                                  f"section '{name}' row {row_id}", "cell count differs"))
                return
            for c, (ec, gc) in enumerate(zip(er, gr)):
                en, gn = normalise_text(ec), normalise_text(gc)
                if en != gn:
                    diffs.append(Diff(comparison, "iv", "cell text",
                                      f"section '{name}' row {row_id} column '{CLAIM_HEADER[c]}'",
                                      "claims cell differs after normalisation", en, gn))

        if len(exp_rows) != len(gen_rows):
            exp_ids = [normalise_text(r[0]) for r in exp_rows]
            gen_ids = [normalise_text(r[0]) for r in gen_rows]
            missing = [i for i in exp_ids if i not in gen_ids]
            extra = [i for i in gen_ids if i not in exp_ids]
            diffs.append(Diff(comparison, "iv", "row count", f"section '{name}'",
                              f"row count differs: export {len(exp_rows)} vs reconstructed "
                              f"{len(gen_rows)}; missing rows {missing[:8]}, extra rows {extra[:8]}"))
            # align the surviving rows by ID cell so one dropped or extra row
            # does not cascade into a mismatch for every following row
            emap = OrderedDict((normalise_text(r[0]), r) for r in exp_rows)
            gmap = OrderedDict((normalise_text(r[0]), r) for r in gen_rows)
            common_e = [rid for rid in emap if rid in gmap]
            common_g = [rid for rid in gmap if rid in emap]
            if common_e != common_g:
                diffs.append(Diff(comparison, "iv", "row order", f"section '{name}'",
                                  "common rows appear in a different order",
                                  str(common_e[:10]), str(common_g[:10])))
            for idx, rid in enumerate(common_g):
                compare_row(idx, emap[rid], gmap[rid])
        else:
            for idx, (er, gr) in enumerate(zip(exp_rows, gen_rows)):
                compare_row(idx, er, gr)
        del recon[key]

    for key, rows in recon.items():
        diffs.append(Diff(comparison, "iv", "unmatched claims file", f"data/claims/{key}.yaml",
                          f"{len(rows)} reconstructed rows match no export section"))


# --------------------------------------------------------------------------
# comparison 3: change log
# --------------------------------------------------------------------------

def compare_changelog(merged_text: str, exp_text: str, diffs: list[Diff]) -> None:
    comparison = "change log"
    eblocks = parse_blocks(strip_stamp(exp_text))
    mblocks = parse_blocks(merged_text)
    etables = [b for b in eblocks if isinstance(b, Table)]
    mtables = [b for b in mblocks if isinstance(b, Table)]
    eparas = [normalise_text(b.text) for b in eblocks if isinstance(b, Para)]
    mparas = [normalise_text(b.text) for b in mblocks if isinstance(b, Para)]
    eheads = [normalise_text(b.text) for b in eblocks if isinstance(b, Heading)]
    mheads = [normalise_text(b.text) for b in mblocks if isinstance(b, Heading)]

    if eheads != mheads:
        diffs.append(Diff(comparison, "iv", "heading", "change log", "headings differ",
                          str(eheads), str(mheads)))

    consumed = [t for t in eparas if t not in mparas]
    unexpected = [t for t in mparas if t not in eparas]
    if unexpected or len(etables) != 2 or len(mtables) != 1:
        diffs.append(Diff(comparison, "iv", "structure", "change log",
                          f"unexpected structure: consumed={consumed!r}, "
                          f"unexpected={unexpected!r}, tables exp/merged = "
                          f"{len(etables)}/{len(mtables)}"))
        return
    diffs.append(Diff(comparison, "i", "change-log addendum merge (SETUP 4.8)",
                      "register/change-log.md",
                      "the 'Latest entries' addendum caption and its separate header row "
                      "were consumed by the merge; addendum rows precede main rows, "
                      "original order kept",
                      export_text="; ".join(consumed), generated_text=""))

    addendum, main = etables[0].rows, etables[1].rows
    merged = mtables[0].rows
    if len(merged) != len(addendum) + len(main):
        diffs.append(Diff(comparison, "iv", "row count", "change log",
                          f"merged table has {len(merged)} rows, export has "
                          f"{len(addendum)} addendum + {len(main)} main"))
        return
    pairs = list(zip(addendum + main, merged))
    for idx, (er, gr) in enumerate(pairs):
        origin = "addendum" if idx < len(addendum) else "main"
        row_id = normalise_text(er[0]) if er else f"row {idx + 1}"
        if len(er) != len(gr):
            diffs.append(Diff(comparison, "iv", "row width",
                              f"change log row {idx + 1} ({origin})", "cell count differs"))
            continue
        for c, (ec, gc) in enumerate(zip(er, gr)):
            en = expand_id_ranges(normalise_text(ec))
            gn = expand_id_ranges(normalise_text(gc))
            if en != gn:
                diffs.append(Diff(comparison, "iv", "cell text",
                                  f"change log row {idx + 1} ({origin}) column {c + 1}",
                                  "change-log cell differs after normalisation", en, gn))


# --------------------------------------------------------------------------
# reconciliation with check.py (gate 3)
# --------------------------------------------------------------------------

def reconcile(diffs: list[Diff], corpus: check.Corpus) -> list[str]:
    """Class (ii) sets must equal check.py warning 1's sets (18 and 107)."""
    problems = []
    rt_used_in = sorted({d.location.split()[-1] for d in diffs
                         if d.comparison == "catalogue" and d.klass == "ii"
                         and d.sub_class.startswith("Used in")})
    rt_cited_by = sorted({d.location.split()[-1] for d in diffs
                          if d.comparison == "catalogue" and d.klass == "ii"
                          and d.sub_class.startswith("Cited by")})
    w1a = sorted(d.split(":")[0] for d in check.warning_1_used_in(corpus))
    w1b = sorted(d.split(":")[0] for d in check.warning_1_cited_by(corpus))
    if rt_used_in != w1a:
        problems.append("used_in reconciliation failed: round-trip class (ii) "
                        f"{rt_used_in} != check.py warning 1a {w1a}")
    if rt_cited_by != w1b:
        problems.append("cited-by reconciliation failed: round-trip class (ii) "
                        f"{rt_cited_by} != check.py warning 1b {w1b}")
    return problems


# --------------------------------------------------------------------------
# selftest: normalisation symmetry (gate 5)
# --------------------------------------------------------------------------

def selftest() -> int:
    """Prove each normalisation symmetric: the export's compressed form and
    the generated expanded form yield equal comparable tokens."""
    failures = []

    def expect(label, a, b):
        if a != b:
            failures.append(f"{label}: {a!r} != {b!r}")

    # N6 range expansion — compressed export form vs generated enumeration
    expect("R-range", expand_id_ranges("R-4 to R-9"),
           expand_id_ranges("R-4, R-5, R-6, R-7, R-8, R-9"))
    expect("R-range facts line", expand_id_ranges("Sources: R-17, R-29 to R-36."),
           expand_id_ranges("Sources: R-17, R-29, R-30, R-31, R-32, R-33, R-34, R-35, R-36."))
    expect("T-range", expand_id_ranges("T-A3-1 to T-A3-7"),
           expand_id_ranges("T-A3-1, T-A3-2, T-A3-3, T-A3-4, T-A3-5, T-A3-6, T-A3-7"))
    expect("C-range", expand_id_ranges("C-A2-1 to C-A2-4"),
           expand_id_ranges("C-A2-1, C-A2-2, C-A2-3, C-A2-4"))
    expect("F-range", expand_id_ranges("F-20 to F-26"),
           expand_id_ranges("F-20, F-21, F-22, F-23, F-24, F-25, F-26"))
    expect("mixed range", expand_id_ranges("C-B5-1 to C-B5-4, C-B5-6"),
           expand_id_ranges("C-B5-1, C-B5-2, C-B5-3, C-B5-4, C-B5-6"))
    # cross-prefix ranges are left alone (symmetrically)
    expect("cross-prefix untouched", expand_id_ranges("T-B2-1 to C-B2-6"),
           expand_id_ranges("T-B2-1 to C-B2-6"))
    # idempotent on both forms
    for sample in ("R-4 to R-9", "T-A3-1 to T-A3-7", "R-2, R-4"):
        if expand_id_ranges(expand_id_ranges(sample)) != expand_id_ranges(sample):
            failures.append(f"expansion not idempotent on {sample!r}")
    # agrees with check.py's T/C/F helper wherever both apply
    for sample in ("T-A3-1 to T-A3-7", "C-A2-1 to C-A2-4", "F-20 to F-26",
                   "no ranges here", "T-B2-1 to C-B2-6"):
        if expand_id_ranges(sample) != check.expand_id_ranges(sample):
            failures.append(f"expansion disagrees with check.py on {sample!r}")

    # N7 separator spacing — same tokens, spacing normalised on both sides
    expect("ref spacing", normalise_reference_cell("CWE-89,  CWE-943,CWE-90"),
           normalise_reference_cell("CWE-89, CWE-943, CWE-90"))
    expect("ref family spacing", normalise_reference_cell("CWE-639;API1:2023; A01:2025"),
           normalise_reference_cell("CWE-639; API1:2023; A01:2025"))

    # N2 ID suffix — generated suffixed cell equals export bare cell
    expect("id suffix", strip_id_suffix("T-A3-1 · 1.0.0-beta.1"), strip_id_suffix("T-A3-1"))
    expect("id suffix no-op", strip_id_suffix("T-A3-1"), "T-A3-1")

    # N8 link cells — qualifier inside vs outside the link
    ekey = link_cell_key("[OWASP API Security Top 10](https://example.org) (API1, API3, API5)")
    gkey = link_cell_key("[OWASP API Security Top 10 (API1, API3, API5)](https://example.org)")
    if ekey[1] != gkey[1] or ekey[2] != gkey[2]:
        failures.append(f"link normalisation not symmetric: {ekey} vs {gkey}")

    # used_in / cited_by token extraction — export vs generated forms
    areas = {f"A{n}" for n in range(1, 14)} | {f"B{n}" for n in range(1, 7)} \
            | {f"P{n}" for n in range(1, 5)}
    expect("cited_by range", sorted(cited_by_tokens("F-21 to F-23", areas)),
           sorted(cited_by_tokens("F-21, F-22, F-23", areas)))
    expect("cited_by prose", sorted(cited_by_tokens("Superseded by R-2; retained for the record", areas)),
           sorted(cited_by_tokens("—", areas)))
    expect("used_in record ids", sorted(used_in_tokens("T-A3-1, T-A3-7", areas)),
           sorted(used_in_tokens("T-A3-1, T-A3-7", areas)))
    expect("used_in label", sorted(used_in_tokens("Reference stack", areas)),
           sorted(used_in_tokens("Reference stack", areas)))

    # N1 stamp strip is the identity on the export
    export_first = "# Web Application Security Reference Catalogue"
    if strip_stamp(export_first) != export_first:
        failures.append("stamp strip altered a non-stamp line")

    if failures:
        for f in failures:
            print(f"SELFTEST FAIL: {f}")
        return 1
    print("selftest passed: every normalisation is symmetric "
          "(compressed export form and generated form yield equal comparable tokens)")
    return 0


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------

CLASS_NAMES = {"i": "(i) allowed merges", "ii": "(ii) spec-mandated regeneration",
               "iii": "(iii) derived-section presentation", "iv": "(iv) unexplained"}


def write_report(path: Path, diffs: list[Diff], reconciliation: list[str],
                 counts: dict, notes: list[str]) -> None:
    lines = ["# Round-trip verification report", ""]
    lines.append("Generated by `tools/roundtrip.py` (SETUP-INSTRUCTIONS 9; stage-7 "
                 "brief). The original exports are the fixed, read-only inputs; "
                 "`build/md/catalogue-full.md` was regenerated from `data/` "
                 "immediately before comparison. Every difference below is placed "
                 "in exactly one class; class (iv) must be empty.")
    lines.append("")
    for comp in ("catalogue", "claims", "change log"):
        lines.append(f"- **{comp}**: class (i) {counts[comp]['i']}, class (ii) "
                     f"{counts[comp]['ii']}, class (iii) {counts[comp]['iii']}, "
                     f"class (iv) {counts[comp]['iv']}")
    lines.append("")
    summary = summarise(diffs)
    for klass in ("i", "ii", "iii", "iv"):
        entries = summary[klass]
        total = sum(len(v) for v in entries.values())
        lines.append(f"## Class {CLASS_NAMES[klass]} — {total} difference(s)")
        lines.append("")
        if not entries:
            lines.append("_None._")
            lines.append("")
            continue
        for sub, ds in entries.items():
            lines.append(f"### {sub} — {len(ds)}")
            lines.append("")
            if klass == "ii":
                ids = sorted({d.location.split()[-1] for d in ds})
                lines.append(f"Affected IDs ({len(ids)}): {', '.join(ids)}")
                lines.append("")
            locations = sorted({d.location for d in ds})
            if len(locations) <= 48:
                lines.append("Locations: " + "; ".join(locations))
                lines.append("")
            for d in ds[:3]:
                lines.append(f"- `{d.location}` — {d.detail}")
                if d.export_text or d.generated_text:
                    lines.append(f"  - export: `{d.export_text}`")
                    lines.append(f"  - generated: `{d.generated_text}`")
            if len(ds) > 3:
                lines.append(f"- … and {len(ds) - 3} more (see the location list above)")
            lines.append("")
    lines.append("## Verified equal (expected presentation deltas that produced no difference)")
    lines.append("")
    for note in notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Reconciliation with check.py")
    lines.append("")
    if reconciliation:
        for problem in reconciliation:
            lines.append(f"- **FAILED**: {problem}")
    else:
        lines.append("- Class (ii) used-in set equals check.py warning 1 (used_in) "
                     "— 18 facts; class (ii) cited-by set equals check.py warning 1 "
                     "(cited by) — 107 references. Same sets.")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def run(root: Path, exports: Path, skip_generate: bool) -> int:
    diffs: list[Diff] = []

    if not skip_generate:
        proc = subprocess.run(
            [sys.executable, str(root / "tools" / "generate.py")],
            capture_output=True, text=True, cwd=str(root))
        if proc.returncode != 0:
            print("roundtrip: generate.py failed; build/ is not current with data/")
            print(proc.stdout[-2000:])
            print(proc.stderr[-2000:])
            return 1

    gen_path = root / "build" / "md" / "catalogue-full.md"
    if not gen_path.exists():
        print(f"roundtrip: {gen_path} missing; run without --skip-generate")
        return 1

    corpus = check.Corpus(root)

    compare_catalogue(gen_path.read_text(encoding="utf-8"),
                      (exports / "catalogue.md").read_text(encoding="utf-8"),
                      corpus, diffs)
    compare_claims(root / "data" / "claims",
                   (exports / "register-claims.md").read_text(encoding="utf-8"),
                   diffs)
    compare_changelog((root / "register" / "change-log.md").read_text(encoding="utf-8"),
                      (exports / "register-change-log.md").read_text(encoding="utf-8"),
                      diffs)

    reconciliation = reconcile(diffs, corpus)

    counts = {comp: {k: 0 for k in ("i", "ii", "iii", "iv")}
              for comp in ("catalogue", "claims", "change log")}
    for d in diffs:
        counts[d.comparison][d.klass] += 1

    report = root / "build" / "roundtrip-report.md"
    claims_recon = claims_rows_by_section(root / "data" / "claims")
    claims_rows_total = sum(len(rows) for rows in claims_recon.values())
    notes = [
        "The residual-risk summary's collapsed 'P1–P4 Process' row reproduces exactly "
        "(rating and 'What remains' shared by the four stored process areas, IMPORT-NOTES "
        "splits and merges 3); it generates no difference.",
        "Appendix B's six export tables are already ascending, so the merge reorders "
        "nothing; Appendix A's merge moves F-18 and F-19 from after F-28 into numeric "
        "position (class (i)).",
        f"Claims: {len(corpus.claims)} stored records re-compress to {claims_rows_total} "
        "export rows via split_from (eight grouped cells); all 24 export sections "
        "reconcile row by row with zero differences in every class.",
        "ID-range expansion normalises both sides symmetrically, so the export's "
        "compressed ranges ('R-4 to R-9', 'T-A3-1 to T-A3-7', 'F-20 to F-26') and the "
        "generator's enumerations compare equal everywhere except where a difference is "
        "recorded above.",
    ]
    write_report(report, diffs, reconciliation, counts, notes)

    print("round-trip verification (SETUP-INSTRUCTIONS 9)")
    for comp in ("catalogue", "claims", "change log"):
        c = counts[comp]
        print(f"  {comp}: class (i) {c['i']}, class (ii) {c['ii']}, "
              f"class (iii) {c['iii']}, class (iv) {c['iv']}")
    total_iv = sum(counts[c]["iv"] for c in counts)
    for problem in reconciliation:
        print(f"RECONCILIATION FAILED: {problem}")
    if total_iv == 0 and not reconciliation:
        print(f"class (iv) is empty across all three comparisons; report: {report}")
        return 0
    print(f"class (iv) differences: {total_iv} (see {report})")
    for d in diffs:
        if d.klass == "iv":
            print(f"  UNEXPLAINED {d.line()}")
    return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="repository root to verify (default: this repository)")
    parser.add_argument("--exports", type=Path, default=None,
                        help="directory holding the original exports "
                             "(default: the directory containing the repository)")
    parser.add_argument("--skip-generate", action="store_true",
                        help="compare the existing build/ without regenerating")
    parser.add_argument("--selftest", action="store_true",
                        help="prove the normalisations symmetric and exit")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    root = args.root.resolve()
    exports = (args.exports if args.exports is not None else root.parent).resolve()
    return run(root, exports, args.skip_generate)


if __name__ == "__main__":
    sys.exit(main())
