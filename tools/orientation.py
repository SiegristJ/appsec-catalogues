#!/usr/bin/env python3
"""Single source of the orientation copy (IA pass; WORK-INSTRUCTIONS section 4).

Every user-visible orientation string in the published artifacts renders from
this module, so no prose is duplicated across templates. The copy is the
owner-approved deck `briefs/ia-copy-deck.md` verbatim (ruling IA-1, recorded
in owner-decisions/digest-ia-pass.md): shared blocks B1-B4 and the wrappers'
copy. Numbers, IDs, version stamps, URLs and artifact-file lists are not copy;
they render from data/build inputs at the call sites.

Two frozen files are parsed here, never restated (content freeze; single
source, one parser, one consumer path):

  - register/governance.md — the evidence-tier table, the verification-status
    table and the two numbered rules ("Two rules follow"). Every artifact
    showing the legend renders from this extraction. A parse that finds
    nothing is a hard build error (SystemExit), never a silent skip.
  - data/front/00-how-to-use.md — the seven-role reading-paths table, rendered
    on the site index rather than restated.

The site URL also lives here (SITE_URL): the one build-side source for the
deployment URL (README "Deployment" and wrangler.jsonc name the same value);
the README is hand-written, so check.py's rule 12 enforces its orientation
text against this module instead.

Determinism: every renderer is a pure function of this file's constants and
the frozen parsed files (plus the build stamp's version, which enters the
citation example); no new non-content input exists.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The deployment URL (README "Deployment", wrangler.jsonc). The one build-side
# source; the full edition's "Where everything lives" renders it.
SITE_URL = "https://appsec.complects.com/"

# -- deck block B1: what-this-is -------------------------------------------

B1_FULL = (
    "A version-controlled corpus of web application security knowledge — areas,\n"
    "threats, controls, volatile facts and references, all carrying stable IDs —\n"
    "together with the tooling that generates every human-readable and AI-readable\n"
    "edition from it. It exists to be selected from: a reviewer declares an\n"
    "application's architecture features and pulls the applicable threats and\n"
    "controls into a security specification by ID."
)

B1_SHORT = (
    "A version-controlled corpus of web application security knowledge with stable\n"
    "IDs, built to be selected from: declare an application's architecture\n"
    "features and pull the applicable threats and controls into a security\n"
    "specification."
)

ONE_LINER = (
    "A selectable reference of web application security threats and controls, with\n"
    "stable IDs and per-item evidence."
)

# -- deck block B2: beta-status ---------------------------------------------

B2 = (
    "**Beta.** Every claim in this catalogue has been verified against its cited\n"
    "sources, but the catalogue has not yet had independent review or specialist\n"
    "sign-off. It is not yet suitable for risk acceptance or compliance assertions.\n"
    "The evidence behind every claim — sources, tiers, verification status, change\n"
    "history — is recorded and open to inspection."
)

# -- deck block B3: evidence-model framing ----------------------------------
# The tier table, status table and the two rules are parsed from
# register/governance.md (see parse_governance); this is only the framing.

B3_FRAMING = (
    "Every threat, control and fact carries a stable ID, and every ID carries\n"
    "evidence: the sources behind it, how strong each source is (its evidence\n"
    "tier), whether it has been verified and how, and every change made to it.\n"
    "Tier and status together decide how strongly the catalogue may state a claim\n"
    "— a normative claim needs a tier-1 source verified first-hand; commentary\n"
    "never supports a claim on its own."
)

# -- deck block B4: three-ways-to-use ---------------------------------------
# Retired from the web by IA-6 (the site re-layer): the catalogue index
# slims to the one-liner, status, project pointer, role table and
# artifacts, and the block's content is carried by the root page's
# "Who it's for" section (owner copy). Nothing renders B4 any more, so the
# block itself is removed (recorded in IMPORT-NOTES); the README lead-in
# below remains — it is the owner-approved README line, rule-12-enforced.

# The README's one-line lead-in for "The three outputs" (deck W7: the table
# "gains B4's use-framing as a one-line lead-in"): assembled from B4's three
# titles, no other words.
README_THREE_OUTPUTS_LEAD_IN = (
    "Three ways to use it: pull a spec from it, read it end to end, or consume it\n"
    "as an agent."
)

# -- deck W2: the full edition's "About this edition" ------------------------

ABOUT_HEADING = "About this edition"

# The citation example's version renders from the build stamp (deck W2: "Site
# URL and the example version render from build inputs, not copy").


def citing_paragraph(version: str) -> str:
    return (f"**Citing.** Cite items by ID together with the catalogue version, e.g.\n"
            f"\"C-A3-1, appsec-catalogues {version}\". IDs are stable: retired items keep\n"
            f"their ID, so citations keep resolving.")


WHERE_EVERYTHING_LIVES = (
    "**Where everything lives.** The evidence behind every ID is published in the\n"
    "evidence pack; machine-readable editions and the AI usage contract are\n"
    f"published alongside this edition at the catalogue's site, <{SITE_URL}>."
)

# -- deck W3: the evidence pack's orientation --------------------------------

EVIDENCE_PACK_HEADER = (
    "This is the audit register rendered per ID: for every threat, control and\n"
    "fact — its claim, the sources behind it with tier and URL, its verification\n"
    "status, and every change-log row that mentions it. The catalogue carries IDs;\n"
    "the evidence lives here."
)

EVIDENCE_PACK_HOW_TO_CHECK = (
    "**How to check a claim.** (1) Find the ID's section — grouped by area, every\n"
    "section listed in the index below. (2) Read its sources with their tiers and\n"
    "its verification status against the legend. (3) Read the change-log rows for\n"
    "anything that has changed since the version you rely on."
)

EVIDENCE_PACK_WEAKEST = (
    "**Where the evidence is weakest.** The claims listed here carry qualifiers —\n"
    "secondary verification, single sources, standard-practice grounding — or are\n"
    "disputed; treat them as indicative and check before relying on them."
)

# -- deck W4: the extract preamble -------------------------------------------

EXTRACT_PREAMBLE_LINES = (
    "Baseline controls apply unconditionally; conditional controls are listed for\n"
    "applicability confirmation. Cite items by ID together with the version shown\n"
    "in the stamp."
)

# -- deck W1: the web index's reading-paths intro ----------------------------

ROLE_INTRO = (
    "**Start here by role** — what to read first, from the catalogue's own\n"
    "reading-paths table:"
)

# -- deck W6: AGENTS.md evidence vocabulary ----------------------------------

AGENTS_VOCABULARY_HEADING = "Evidence vocabulary"

AGENTS_VOCABULARY_FRAMING = (
    "These definitions are the catalogue's own governance vocabulary, rendered\n"
    "from its audit register. Every record you consume carries evidence: tiers\n"
    "say how strong a source is; statuses say what has been verified."
)

AGENTS_VOCABULARY_CARRY = (
    "When you restate a catalogue item, carry its qualifiers: state\n"
    "secondary-verified and single-source items as indicative, mark disputed items\n"
    "as disputed, and never present a commentary-tier source as support on its own."
)

# -- deck W7: the README's deployment sentence --------------------------------

README_DEPLOYMENT_SENTENCE = (
    "Deployment is owner-operated. The workflows above are the whole public\n"
    "contract; owner-side account setup is kept by the owner, outside this\n"
    "repository."
)


# --------------------------------------------------------------------------
# parsing the frozen files (hard error when a parse finds nothing)
# --------------------------------------------------------------------------

def _table_block_after(lines: list[str], marker: str, source: Path) -> list[list[str]]:
    """The pipe table that follows a marker line, as a list of cell lists
    (header first). A missing marker or an empty table is a hard error."""
    for index, line in enumerate(lines):
        if line.strip() == marker:
            j = index + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            rows: list[list[str]] = []
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                if all(set(c) <= {"-", " ", ":"} for c in cells):
                    j += 1
                    continue  # delimiter row
                rows.append(cells)
                j += 1
            if not rows:
                raise SystemExit(f"{source}: no table found after {marker!r} — "
                                 "the orientation parse refuses to render an "
                                 "empty legend (hard error, never a silent skip)")
            return rows
    raise SystemExit(f"{source}: marker {marker!r} not found — the orientation "
                     "parse refuses to render an empty legend (hard error, "
                     "never a silent skip)")


def _numbered_rules_after(lines: list[str], marker: str, source: Path,
                          minimum: int) -> list[str]:
    """The numbered rule lines that follow a marker line, verbatim including
    their numbers. Fewer than `minimum` rules is a hard error."""
    for index, line in enumerate(lines):
        if line.strip() == marker:
            rules: list[str] = []
            j = index + 1
            while j < len(lines):
                stripped = lines[j].strip()
                if not stripped and not rules:
                    j += 1
                    continue
                match = re.match(r"^(\d+\.\s+.*)$", stripped)
                if match:
                    rules.append(match.group(1))
                    j += 1
                    continue
                break
            if len(rules) < minimum:
                raise SystemExit(f"{source}: expected at least {minimum} numbered "
                                 f"rules after {marker!r}, found {len(rules)} — "
                                 "hard error, never a silent skip")
            return rules
    raise SystemExit(f"{source}: marker {marker!r} not found — the orientation "
                     "parse refuses to skip the rules (hard error, never a "
                     "silent skip)")


TIER_CAPTION = "**Evidence tiers**"
STATUS_CAPTION = "**Verification statuses**"
RULES_CAPTION = "Two rules follow:"


def parse_governance(root: Path | None = None) -> dict:
    """The evidence legend from register/governance.md: the tier table, the
    verification-status table and the two numbered rules, with their captions.
    governance.md itself is never edited (content freeze); this parse is the
    one consumer path every legend-rendering artifact shares."""
    root = root or ROOT
    source = root / "register" / "governance.md"
    lines = source.read_text(encoding="utf-8").splitlines()
    tiers = _table_block_after(lines, TIER_CAPTION, source)
    statuses = _table_block_after(lines, STATUS_CAPTION, source)
    rules = _numbered_rules_after(lines, RULES_CAPTION, source, 2)
    return {
        "tier_caption": TIER_CAPTION,
        "tier_header": tiers[0],
        "tier_rows": tiers[1:],
        "status_caption": STATUS_CAPTION,
        "status_header": statuses[0],
        "status_rows": statuses[1:],
        "rules_caption": RULES_CAPTION,
        "rules": rules,
    }


READING_PATHS_CAPTION = "**Reading paths by role.**"


def parse_reading_paths(root: Path | None = None) -> dict:
    """The seven-role reading-paths table from data/front/00-how-to-use.md
    (frozen data; the site index renders it, never restates it)."""
    root = root or ROOT
    source = root / "data" / "front" / "00-how-to-use.md"
    lines = source.read_text(encoding="utf-8").splitlines()
    table = _table_block_after(lines, READING_PATHS_CAPTION, source)
    if len(table[0]) != 3:
        raise SystemExit(f"{source}: reading-paths table does not have 3 columns "
                         f"({table[0]!r}) — hard error, never a silent skip")
    return {"caption": READING_PATHS_CAPTION,
            "header": table[0], "rows": table[1:]}


# --------------------------------------------------------------------------
# markdown renderers (consumed by generate.py, build.py, extract.py,
# roundtrip.py's byte verification)
# --------------------------------------------------------------------------

def _md_table(header: list[str], rows: list[list[str]]) -> str:
    for cells in [header] + rows:
        for c in cells:
            if "|" in c or "\n" in c:
                raise SystemExit(f"cannot render faithfully: legend table cell "
                                 f"contains a newline or pipe: {c[:80]!r}")
    lines = ["| " + " | ".join(header) + " |",
             "| " + " | ".join("---" for _ in header) + " |"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(lines)


def legend_markdown(gov: dict) -> str:
    """The parsed legend alone (captions and tables and rules, governance.md's
    own words)."""
    return "\n\n".join([
        gov["tier_caption"],
        _md_table(gov["tier_header"], gov["tier_rows"]),
        gov["status_caption"],
        _md_table(gov["status_header"], gov["status_rows"]),
        gov["rules_caption"],
        "\n".join(gov["rules"]),
    ])


def legend_block(gov: dict) -> str:
    """B3's framing paragraph plus the parsed legend (deck W2/W3: 'B3 with the
    parsed legend')."""
    return B3_FRAMING + "\n\n" + legend_markdown(gov)


def about_edition_body(version: str, gov: dict) -> str:
    """The body under '## About this edition' (deck W2): B1, B2, B3 with the
    parsed legend, the citation convention, where everything lives."""
    return "\n\n".join([
        B1_FULL,
        B2,
        legend_block(gov),
        citing_paragraph(version),
        WHERE_EVERYTHING_LIVES,
    ])


def about_edition_section(version: str, gov: dict) -> str:
    """The complete '## About this edition' section as generate.py embeds it
    in build/md/catalogue-full.md. roundtrip.py byte-verifies the generated
    document's section against exactly this render."""
    return f"## {ABOUT_HEADING}\n\n{about_edition_body(version, gov)}"


def agents_evidence_vocabulary(gov: dict) -> str:
    """The '## Evidence vocabulary' section of AGENTS.md (deck W6), appended
    after the seven usage-contract bullets; flows into catalogue.json's
    usage_contract automatically."""
    return "\n\n".join([
        f"## {AGENTS_VOCABULARY_HEADING}",
        AGENTS_VOCABULARY_FRAMING,
        legend_markdown(gov),
        AGENTS_VOCABULARY_CARRY,
    ])


def evidence_pack_orientation(gov: dict) -> str:
    """The evidence pack's orientation header (deck W3): what this is, how to
    check a claim, then the B3 legend."""
    return "\n\n".join([
        EVIDENCE_PACK_HEADER,
        EVIDENCE_PACK_HOW_TO_CHECK,
        legend_block(gov),
    ])


def extract_preamble_paragraphs() -> list[str]:
    """The extract preamble after the stamp (deck W4): B1 short form, then the
    two lines."""
    return [B1_SHORT, EXTRACT_PREAMBLE_LINES]


# --------------------------------------------------------------------------
# HTML pieces for the site templates (deck: links are applied by each
# template; these are the applied forms, checked against the canonical copy)
# --------------------------------------------------------------------------

def _assert_html_matches(html: str, markdown: str, label: str) -> None:
    """The HTML form must carry exactly the canonical copy: strip tags and
    code markers, collapse whitespace (the copy is hard-wrapped) and compare,
    so the two forms cannot drift silently."""
    def flat(text: str) -> str:
        return re.sub(r"\s+", " ",
                      text.replace("`", "").replace("**", "")).strip()
    if flat(re.sub(r"<[^>]+>", "", html)) != flat(markdown):
        raise SystemExit(f"orientation HTML form of {label} diverges from the "
                         f"canonical copy: {html!r} vs {markdown!r}")


def role_intro_html() -> str:
    html = "<strong>Start here by role</strong>" + ROLE_INTRO[len("**Start here by role**"):]
    _assert_html_matches(html, ROLE_INTRO, "role intro")
    return html


def web_context(root: Path | None = None) -> dict:
    """The orientation context for site/web/index.html.j2 after the IA-6
    re-layer: the catalogue one-liner, the reading-paths intro and the
    parsed table (IA-4: cells link per ROLE_TABLE_LINKS; build.py verifies
    every mapped anchor exists in the built page). The B1/B2/B4 blocks were
    retired from this page by IA-6; the §10.1 status line stays by law and
    the template adds the project pointer up to the root page."""
    paths = parse_reading_paths(root)
    rows_html = [[cell if index == 0 else _role_cell_html(cell)
                  for index, cell in enumerate(row)]
                 for row in paths["rows"]]
    return {
        "one_liner": ONE_LINER,
        "role_intro_html": role_intro_html(),
        "role_table_header": paths["header"],
        "role_table_rows": paths["rows"],
        "role_table_rows_html": rows_html,
    }


# IA-4 (owner ruling, click-through gate): hyperlink the role table on the
# web index. Web rendering only — the edition's embedded how-to-use section
# and build/md are untouched. Cell text stays verbatim from
# data/front/00-how-to-use.md; links wrap text, never reword it. Named
# sections map to their anchors in catalogue.html; the audit-register cell
# maps to the evidence pack (page-level, no anchor); "Linked ASVS chapters"
# stays plain (external target, outside the site's link policy); the range
# "B1–B6" links its first member only. Anchors are the built page's ids;
# build.py proves each one exists at build time (mapped-but-missing is a
# hard error); unmapped cells degrade silently to plain text.
ROLE_TABLE_LINKS = {
    "Applicability index": ("catalogue.html", "applicability-index"),
    "Baseline and conditional controls":
        ("catalogue.html", "baseline-and-conditional-controls"),
    "Residual-risk summary": ("catalogue.html", "residual-risk-summary"),
    "Compliance mapping": ("catalogue.html", "compliance-mapping"),
    "Where experts differ": ("catalogue.html", "where-experts-differ"),
    "P2 Security testing":
        ("catalogue.html", "p2-security-testing-and-verification"),
    "P3 CI/CD": ("catalogue.html", "p3-cicd-and-infrastructure-as-code"),
    "P4 Detection and incident response":
        ("catalogue.html", "p4-detection-monitoring-and-incident-response"),
    "B1–B6": ("catalogue.html",
              "b1-hardening-misconfiguration-and-patch-management"),
    "Audit register (claims, sources, change history)":
        ("evidence-pack.html", None),
}


def _role_cell_html(cell: str) -> str:
    """One role-table cell with its link applied, or the verbatim text when
    no mapping covers it (silent degradation). A cell links whole when it
    matches a mapping key; a cell that is entirely comma-joined mapped
    segments links each segment (the operations row's two targets);
    instructional phrases with no single target stay plain."""
    if cell in ROLE_TABLE_LINKS:
        page, anchor = ROLE_TABLE_LINKS[cell]
        href = page if anchor is None else f"{page}#{anchor}"
        html = f'<a href="{href}">{cell}</a>'
        _assert_html_matches(html, cell, "role-table cell")
        return html
    segments = cell.split(", ")
    if len(segments) > 1 and all(s in ROLE_TABLE_LINKS for s in segments):
        html = ", ".join(_role_cell_html(s) for s in segments)
        _assert_html_matches(html, cell, "role-table cell")
        return html
    return cell


# -- IA-5 (owner ruling, click-through gate): the site root's project-level
# introductory block. Owner-approved copy, pending the owner's word-level
# confirm — do not reword. Site-level and catalogue-agnostic: the only
# catalogue-specific fact is the published-today sentence, whose count and
# title render from the catalogue manifests (data, not hardcoded prose).
# Root index only: this block must not leak into catalogue-level surfaces
# or the edition (enforced by review; nothing else consumes it).

SITE_DOORWAY_PARAGRAPHS = (
    "**What this is.** A project maintaining version-controlled security "
    "reference catalogues: structured corpora of threats, controls, volatile "
    "facts and sources, every item carrying a stable ID and recorded "
    "evidence. Build tooling generates every edition from each corpus — "
    "human-readable (HTML, PDF, DOCX, Markdown) and machine-readable (JSON, "
    "JSONL, `llms.txt`) under a usage contract for agents.",
    "**What it's for.** A catalogue exists to be selected from: declare an "
    "application's architecture features and pull the applicable threats and "
    "controls into a security specification by ID, with the evidence behind "
    "every item open to inspection.",
)

# IA-10 (owner ruling, click-through gate; owner-confirmed verbatim):
# "Why this exists", four paragraphs, placed between "What it's for" (with
# its published-today sentence) and "How to access it". Root page only.
SITE_DOORWAY_PARAGRAPHS_IA10 = (
    "**Why this exists.** Building a knowledge asset is intensive; using one "
    "is comparatively cheap — and the cost of building it is amortized across "
    "every application that uses it. In the age of AI agents, that asymmetry "
    "has a new consequence: knowledge assets are plentiful — and plentiful "
    "makes them hard to trust. This project takes the other path: the asset "
    "is constructed so that verifying its contents against primary sources "
    "is cheap, computationally and in human effort.",
    "Application security is a demanding instance of the problem. The domain "
    "moves fast, its information surface is enormous — standards, primary "
    "research, advisories and vendor material of widely varying reputation — "
    "and no one can fully absorb it. Yet the economics of developing "
    "applications securely depend on that knowledge being usable.",
    "So the catalogue is assembled with AI processing under a documented, "
    "reproducible process, and published so that every claim can be checked "
    "against the sources it cites. The aim: lower the economic cost of "
    "developing applications securely, with a reference that is trusted not "
    "because an authority issued it, but because its claims can be reviewed "
    "— cheaply.",
    "The process itself is published too, with full transparency and "
    "provenance tracking from each claim to its sources — so others who are "
    "interested in participating can improve the process, not just use its "
    "output.",
)

# IA-11 (owner ruling, click-through gate; owner-confirmed verbatim, with
# the added closing sentence): "Expected usage", two paragraphs, placed
# immediately after "Why this exists". Root page only.
SITE_DOORWAY_PARAGRAPHS_IA11 = (
    "**Expected usage.** Security references fail a familiar way: long lists "
    "of controls are hard to consume, and harder still to relate to your own "
    "situation. This catalogue organizes content by functional use instead. "
    "It is built around a kind of reference architecture for different "
    "application types, with every control grouped by the application "
    "feature it relates to — you declare the features your application has, "
    "and the catalogue returns the areas, threats and controls that apply, "
    "rather than the whole surface. Web applications are the first domain "
    "considered under this model.",
    "Broadly, by role: an architect locates the application type in the "
    "applicability index and reads what applies and what remains risky; a "
    "spec writer or engineer pulls controls by ID into a security "
    "specification; a developer works from the threats and controls that "
    "spec selected; a security reviewer starts from threats and residual "
    "risk; a risk owner reads what the controls leave open; an auditor or "
    "compliance function follows any ID to its recorded evidence. Each "
    "catalogue page carries the full start-here-by-role table with links.",
)

# IA-6 (owner ruling, click-through gate): three more root sections, copy
# verbatim, owner-approved pending word-level confirm — do not reword. The
# leads are bolded to match the IA-5 block's house style (presentation, not
# wording). "Where it's going" carries the statement IA-5's published-today
# sentence used to end with (supersession recorded in IMPORT-NOTES).
SITE_DOORWAY_PARAGRAPHS_IA6 = (
    "**How to access it.** Everything is generated from one version-controlled "
    "corpus per catalogue and published in three forms: this browsable site; "
    "downloadable editions (PDF, DOCX, Markdown) with the evidence behind "
    "every ID in a companion evidence pack; and machine-readable files (JSON, "
    "JSONL, `llms.txt`) published under a usage contract (`AGENTS.md`). "
    "Releases are tagged and archived; every item is citable by its stable ID "
    "and the catalogue version.",
    "**Who it's for.** Human reviewers and spec writers, who select threats "
    "and controls into security specifications; human readers, who want the "
    "full reference with its evidence; and AI agents, which consume the "
    "machine-readable editions under the usage contract and carry the "
    "evidence qualifiers with what they restate.",
    "**Where it's going.** Beta today: verified against cited sources, "
    "awaiting independent review and specialist sign-off before 1.0. The "
    "corpus model is built for further catalogues beyond web application "
    "security.",
)

_COUNT_WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
                6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
                11: "Eleven", 12: "Twelve"}


def site_doorway_published_today(catalogues: list) -> str:
    """The published-today sentence with the catalogue count and title(s)
    rendered from the manifests. IA-6 supersession: the sentence ends at
    "currently in beta." — the further-catalogues clause moved to the root
    page's "Where it's going" section. At one catalogue this reproduces the
    owner's sentence exactly; the n>1 form is mechanical (count word,
    plural, title join) and gets reviewed when a second catalogue lands."""
    count = len(catalogues)
    word = _COUNT_WORDS.get(count, str(count))
    titles = [entry["title"] for entry in catalogues]
    names = titles[0] if count == 1 else " and ".join(titles)
    return (f"{word} catalogue{'s' if count != 1 else ''} "
            f"{'are' if count != 1 else 'is'} published today — the {names}, "
            "currently in beta.")


# IA-12 (owner ruling; owner-supplied text, "catalog" normalized to
# "catalogue" per the owner's word): the README's "Why this exists" block,
# placed after the status paragraph. README-only; rule-12-enforced.
README_WHY_PARAGRAPHS = (
    "**Why this exists.** Building a reliable knowledge asset is intensive; "
    "using one is cheap. However, in the age of AI agents, knowledge assets "
    "can be easily and inexpensively built that provide only an illusion of "
    "reliability but in reality are unable to be trusted.",
    "This security catalogue is designed to make the knowledge asset reliable "
    "not because it is published by a trusted authority but because of how it "
    "is constructed with its contents able to be easily verified against "
    "primary sources. This construction is further carried out by AI "
    "processing through a documented, reproducible process, and the corpus "
    "and provenance information are published along with the catalogue so that "
    "this construction process may also be reviewed, used and improved upon.",
)

# IA-14 and IA-15 (owner rulings; owner-supplied text): the README's
# "Intended use" section — the lead paragraph after "Why this exists" and
# before "The three outputs", plus IA-15's two closing paragraphs.
# README-only; rule-12-enforced.
README_INTENDED_PARAGRAPHS = (
    "**Intended use.** The catalogue is expected to be accessed as an "
    "anchoring resource for design and development activities, either by "
    "human architects and engineers or directly by AI agents. Right now, the "
    "contents are organised functionally, based on where they may surface in "
    "the design and security conversations about an application.",
    "There is a reason anchors matter here. AI coding agents draw on priors "
    "formed from internet code, and those priors are not necessarily strong "
    "on security. But when a specification carries good anchors — controls "
    "and requirements cited by ID — the agent knows enough about secure "
    "coding practices to integrate them effectively into the system. The "
    "catalogue's job is to make those anchors precise, applicable and "
    "evidence-backed.",
    "The mechanism is the prompt: what it contains is what pulls out the "
    "agent's general knowledge. Ask only for a behavior, and you get code "
    "that implements the behavior — the security edge cases go unconsidered "
    "until the process makes the agent handle them. An anchored specification "
    "is that process: it puts the controls in the prompt's path, where the "
    "agent has to work with them.",
)

# IA-15 root rider (owner-confirmed): a third paragraph of the root page's
# "Expected usage" section, after the by-role paragraph. Root render only.
SITE_DOORWAY_IA11_RIDER = (
    "Anchored specifications are also how AI agents apply secure practice "
    "effectively. Their priors are not necessarily strong on security, and "
    "it is what a prompt contains that draws an agent's knowledge out — the "
    "controls a specification pins down are the ones that get integrated."
)


def _md_inline_html(text: str) -> str:
    """Bold leads and code spans to HTML; nothing else is markup in the
    doorway copy."""
    html = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)
    return html


def site_doorway_paragraphs_html(catalogues: list) -> list[str]:
    """The root index's introductory block as HTML paragraphs: the IA-5
    block (What this is / What it's for / published-today sentence), then
    "Why this exists" (IA-10, four paragraphs) and "Expected usage" (IA-11,
    two paragraphs), then the IA-6 sections (How to access it / Who it's
    for / Where it's going), before the Catalogues list."""
    paragraphs = (list(SITE_DOORWAY_PARAGRAPHS)
                  + [site_doorway_published_today(catalogues)]
                  + list(SITE_DOORWAY_PARAGRAPHS_IA10)
                  + list(SITE_DOORWAY_PARAGRAPHS_IA11)
                  + [SITE_DOORWAY_IA11_RIDER]
                  + list(SITE_DOORWAY_PARAGRAPHS_IA6))
    out = []
    for markdown in paragraphs:
        html = _md_inline_html(markdown)
        _assert_html_matches(html, markdown, "site doorway paragraph")
        out.append(html)
    return out


if __name__ == "__main__":  # pragma: no cover - developer smoke check
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    gov = parse_governance()
    print(about_edition_section("v1.0.0-beta.1", gov))
    print()
    print(agents_evidence_vocabulary(gov))
