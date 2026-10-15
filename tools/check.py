#!/usr/bin/env python3
"""Corpus integrity check for the web application security catalogue.

Implements SETUP-INSTRUCTIONS section 6 exactly. Run on every commit (CI):

    python tools/check.py                  # normal mode
    python tools/check.py --release 1.0.0  # adds rules 7, 8 and 9

Exits non-zero on any error. Warnings print and pass. Output is
deterministic: the same tree produces byte-identical output.

Rules (section 6 numbering):

  Errors
   1  every data file validates against its schema
   2  T-/C-IDs unique, match ^[TC]-(A|B|P)\\d{1,2}-\\d+$, area prefix matches file
   3  claims coverage is bidirectional (T/C/F <-> claims records, split_from included)
   4  every addresses ID exists (same area or cross-area)
   5  every F-/R-ID referenced anywhere exists
   6  no previously existing ID disappeared (vs previous git tag) + replaced_by validity
   7  release only: no claim whose verification starts with "Unverified"
   8  release only: normative-form claims have tier 1 and "Verified — primary"
   9  release only: per-record last_changed correct vs the previous tag
  10  manifest areas exist; every area belongs to at least one catalogue

  Warnings
   1  used_in and "Cited by" differ from the regenerated values
      (1a = used_in, 1b = Cited by; both are warning 1 in section 6.
      Expected at import: 18 used_in differences — the five facts whose
      "Used in" cells hold record IDs (F-3, F-4, F-29, F-34, F-45) plus
      thirteen whose cells name only a non-area place or fewer areas than
      the corpus cites — and 107 "Cited by" differences, because the
      export's Appendix B column predates the register.)
   2  controls with requirement: null           (expected at import: 166)
   3  conditional controls with trigger.rule: null   (expected at import: 50)
   4  references with snapshot: null            (expected at import: 144)
   5  claims whose verification contains "standard practice", "secondary"
      or "single source"                        (expected at import: 36)
   6  features with question: null              (expected at import: 22)

Warning 1's regeneration is exposed as importable functions
(regenerate_used_in, regenerate_cited_by) because stage 6's generate.py
needs the same values when it renders Appendices A and B.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_DIR = ROOT / "schema"
DATA_DIR = ROOT / "data"
AREAS_DIR = DATA_DIR / "areas"
CLAIMS_DIR = DATA_DIR / "claims"
FRONT_DIR = DATA_DIR / "front"
MANIFEST_DIR = ROOT / "catalogues"

TC_ID = re.compile(r"^[TC]-(A|B|P)\d{1,2}-\d+$")
AREA_ID = re.compile(r"^[ABP]\d{1,2}$")
F_ID = re.compile(r"\bF-\d+\b")
R_ID = re.compile(r"\bR-\d+\b")
ANY_ID = re.compile(r"\b(?:[TC]-(?:A|B|P)\d{1,2}-\d+|F-\d+|R-\d+)\b")
TCF_ID = re.compile(r"\b(?:[TC]-(?:A|B|P)\d{1,2}-\d+|F-\d+)\b")
WS = re.compile(r"\s+")

# Sections of section 6 that the repository defines but the import leaves
# unpopulated by design (ground rule 3); the warnings count them.


# --------------------------------------------------------------------------
# loading helpers
# --------------------------------------------------------------------------

def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def normalise_for_schema(obj):
    """Render YAML dates as ISO strings so JSON Schema sees strings."""
    if isinstance(obj, (_dt.date, _dt.datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: normalise_for_schema(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalise_for_schema(v) for v in obj]
    return obj


def normalise_whitespace(obj):
    """Section 6 rule 9 comparison form: all fields, whitespace collapsed."""
    if isinstance(obj, str):
        return WS.sub(" ", obj).strip()
    if isinstance(obj, dict):
        return {k: normalise_whitespace(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        return [normalise_whitespace(v) for v in obj]
    return obj


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def sorted_files(directory: Path, suffix: str):
    return sorted(p for p in directory.iterdir() if p.is_file() and p.name.endswith(suffix))


class Corpus:
    """Everything the rules need, loaded once, in deterministic order."""

    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.area_files = sorted_files(self.root / "data" / "areas", ".yaml")
        self.claim_files = sorted_files(self.root / "data" / "claims", ".yaml")
        self.facts_file = self.root / "data" / "facts.yaml"
        self.references_file = self.root / "data" / "references.yaml"
        self.features_file = self.root / "data" / "features.yaml"
        self.manifest_files = sorted_files(self.root / "catalogues", ".yaml")

        self.areas: dict[str, dict] = {}
        for path in self.area_files:
            doc = load_yaml(path)
            self.areas[doc["id"]] = doc
        self.area_ids = sorted(self.areas)

        self.facts = load_yaml(self.facts_file) or []
        self.references = load_yaml(self.references_file) or []
        self.features_doc = load_yaml(self.features_file) or {}
        self.features = self.features_doc.get("features", [])

        self.claims: list[tuple[str, dict]] = []
        for path in self.claim_files:
            for record in load_yaml(path) or []:
                self.claims.append((rel(path), record))

        self.fact_ids = sorted(r["id"] for r in self.facts)
        self.reference_ids = sorted(r["id"] for r in self.references)
        self.feature_ids = sorted(f["id"] for f in self.features)

        self.threats: dict[str, tuple[str, dict]] = {}
        self.controls: dict[str, tuple[str, dict]] = {}
        for aid in self.area_ids:
            area = self.areas[aid]
            for threat in area.get("threats") or []:
                self.threats[threat["id"]] = (aid, threat)
            for control in area.get("controls") or []:
                self.controls[control["id"]] = (aid, control)

        self.all_ids = (
            set(self.threats) | set(self.controls) | set(self.fact_ids)
            | set(self.reference_ids) | set(self.feature_ids)
        )

    # -- text scanning ----------------------------------------------------

    def scan_paths(self):
        """Files whose text is scanned for F-/R-ID references (rule 5)."""
        paths = list(self.area_files) + list(self.claim_files)
        paths += [self.facts_file, self.references_file, self.features_file]
        paths += [self.root / "data" / "disputes.yaml", self.root / "data" / "compliance.yaml"]
        front = self.root / "data" / "front"
        if front.is_dir():
            paths += sorted(p for p in front.iterdir() if p.suffix == ".md")
        maintenance = self.root / "data" / "maintenance.md"
        if maintenance.exists():
            paths.append(maintenance)
        paths += self.manifest_files
        return [p for p in paths if p.exists()]


# --------------------------------------------------------------------------
# warning 1 regeneration (importable; generate.py reuses these)
# --------------------------------------------------------------------------

def front_section_labels(root: Path | None = None) -> dict[str, str]:
    """Map each front-matter/maintenance file to its own H1 heading."""
    root = root or ROOT
    labels = {}
    candidates = sorted((root / "data" / "front").glob("*.md"))
    maintenance = root / "data" / "maintenance.md"
    if maintenance.exists():
        candidates.append(maintenance)
    for path in candidates:
        heading = ""
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("# "):
                    heading = line[2:].strip()
                    break
        labels[rel(path)] = heading or path.stem
    return labels


def regenerate_used_in(root: Path | None = None) -> dict[str, dict]:
    """Regenerate each fact's usage from the corpus text.

    Scans data/areas/, data/front/*.md and data/maintenance.md for F-IDs
    (SETUP 5.6). Returns, per fact ID::

        {"areas": [area IDs whose file mentions the fact],
         "other": [front-matter/maintenance section labels mentioning it]}

    Only area IDs can enter the used_in list itself: section 4.2 defines
    used_in as the parsed "Used in" cell, whose ID kind is the area (the
    five cells that carry record IDs are the known literal readings, kept
    verbatim under R1 and reported by warning 1a).
    """
    root = root or ROOT
    labels = front_section_labels(root)
    area_dir = root / "data" / "areas"
    result: dict[str, dict] = {}

    mentions: dict[str, set] = {}
    for path in sorted_files(area_dir, ".yaml"):
        text = path.read_text(encoding="utf-8")
        area_id = load_yaml(path)["id"]
        for match in F_ID.finditer(text):
            mentions.setdefault(match.group(0), set()).add(area_id)
    for path, label in labels.items():
        text = (root / path).read_text(encoding="utf-8")
        for match in F_ID.finditer(text):
            entry = mentions.setdefault(match.group(0), set())
            entry.add(label)

    for token, places in mentions.items():
        result[token] = {
            "areas": sorted(p for p in places if AREA_ID.fullmatch(p)),
            "other": sorted(p for p in places if not AREA_ID.fullmatch(p)),
        }
    return result


def regenerate_cited_by(corpus: Corpus) -> dict[str, list]:
    """Regenerate each reference's "Cited by" value (SETUP 5.7).

    Inputs: claims sources and fact sources give citing record IDs; area
    sources give area-level citations. A citation is reported at the finest
    granularity available: the citing record when one exists, otherwise the
    area whose sources list the reference.
    """
    citing: dict[str, set] = {}
    citing_areas: dict[str, set] = {}

    for _path, claim in corpus.claims:
        for rid in claim.get("sources") or []:
            citing.setdefault(rid, set()).add(claim["id"])
            if not claim["id"].startswith("F-"):
                citing_areas.setdefault(rid, set()).add(claim["id"].split("-")[1])
    for fact in corpus.facts:
        for rid in fact.get("sources") or []:
            citing.setdefault(rid, set()).add(fact["id"])
    for aid in corpus.area_ids:
        for rid in corpus.areas[aid].get("sources") or []:
            if aid not in citing_areas.get(rid, set()):
                citing.setdefault(rid, set()).add(aid)

    return {rid: sorted(ids) for rid, ids in citing.items()}


ID_RANGE = re.compile(
    r"\b((?:[TC]-(?:A|B|P)\d{1,2}-|F-)(\d+))\s+to\s+"
    r"((?:[TC]-(?:A|B|P)\d{1,2}-|F-)(\d+))\b"
)


def expand_id_ranges(text: str) -> str:
    """Expand the export's same-prefix "X to Y" ranges (e.g. "T-A3-1 to
    T-A3-3") into enumerated IDs, so compressed and enumerated cells
    compare equal."""
    def repl(match):
        first, second = match.group(1), match.group(3)
        prefix = first[: first.rfind("-") + 1]
        if prefix != second[: second.rfind("-") + 1]:
            return match.group(0)
        low, high = int(match.group(2)), int(match.group(4))
        if not 0 < high - low <= 200:
            return match.group(0)
        return ", ".join(f"{prefix}{n}" for n in range(low, high + 1))
    return ID_RANGE.sub(repl, text)


def parse_cited_by_text(text: str, corpus: Corpus) -> set:
    """Extract the citation tokens a stored "Cited by" cell carries.

    T-/C-/F-IDs count as citations, with "X to Y" ranges expanded; a bare
    area token counts only when it is a real area ID and not part of a
    longer ID. Anything else in the cell is prose ("ASVS column, all
    areas") and is not a citation.
    """
    text = expand_id_ranges(text)
    tokens = set()
    spans = [m.span() for m in TCF_ID.finditer(text)]
    for match in TCF_ID.finditer(text):
        tokens.add(match.group(0))
    for match in re.finditer(r"\b[ABP]\d{1,2}\b", text):
        start, end = match.span()
        if any(start >= s and end <= e for s, e in spans):
            continue
        if match.group(0) in corpus.areas:
            tokens.add(match.group(0))
    return tokens


# --------------------------------------------------------------------------
# git helpers (rules 6 and 9)
# --------------------------------------------------------------------------

def git(args: list, root: Path | None = None):
    proc = subprocess.run(
        ["git", "-C", str(root or ROOT)] + args,
        capture_output=True, text=True, check=False,
    )
    return proc


def version_key(tag: str):
    m = re.match(r"^v?(\d+(?:\.\d+)*)", tag)
    if not m:
        return ()
    return tuple(int(x) for x in m.group(1).split("."))


def previous_tag(root: Path | None = None):
    """The most recent v* tag that is an ancestor of HEAD, or None."""
    root = root or ROOT
    tags = git(["tag", "-l", "v*"], root).stdout.split()
    tags = [t for t in tags if version_key(t)]
    tags.sort(key=version_key)
    for tag in reversed(tags):
        if git(["merge-base", "--is-ancestor", tag, "HEAD"], root).returncode == 0:
            return tag
    return None


def yaml_at(tag: str, path: str, root: Path | None = None):
    proc = git(["show", f"{tag}:{path}"], root)
    if proc.returncode != 0:
        return None
    return yaml.safe_load(proc.stdout)


def paths_at(tag: str, directory: str, root: Path | None = None):
    """YAML file paths under a directory at a tag.

    -r is required: without it ls-tree lists the directory's own tree
    entry (e.g. "data/areas/") rather than the blobs inside it.
    """
    proc = git(["ls-tree", "-r", "--name-only", tag, "--", directory], root)
    if proc.returncode != 0:
        return []
    return [line for line in proc.stdout.splitlines() if line.endswith(".yaml")]


def collect_ids(doc, kinds=("threats", "controls")):
    ids = set()
    if isinstance(doc, dict):
        for kind in kinds:
            for record in doc.get(kind) or []:
                if isinstance(record, dict) and "id" in record:
                    ids.add(record["id"])
    elif isinstance(doc, list):
        for record in doc:
            if isinstance(record, dict) and "id" in record:
                ids.add(record["id"])
    return ids


# --------------------------------------------------------------------------
# error rules
# --------------------------------------------------------------------------

def rule_1_schema(corpus: Corpus) -> list[str]:
    """Every data file validates against its schema."""
    schemas = {
        "area": load_json(SCHEMA_DIR / "area.schema.json"),
        "facts": load_json(SCHEMA_DIR / "facts.schema.json"),
        "references": load_json(SCHEMA_DIR / "references.schema.json"),
        "claims": load_json(SCHEMA_DIR / "claims.schema.json"),
    }
    targets = (
        [(p, schemas["area"]) for p in corpus.area_files]
        + [(corpus.facts_file, schemas["facts"])]
        + [(corpus.references_file, schemas["references"])]
        + [(p, schemas["claims"]) for p in corpus.claim_files]
    )
    errors = []
    for path, schema in targets:
        doc = normalise_for_schema(load_yaml(path))
        validator = jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        )
        found = sorted(
            ("" if not e.absolute_path else ".".join(str(p) for p in e.absolute_path), e.message)
            for e in validator.iter_errors(doc)
        )
        for location, message in found:
            errors.append(f"{rel(path)}: {location}: {message}")
    return errors


def rule_2_ids(corpus: Corpus) -> list[str]:
    """T-/C-ID uniqueness, pattern, and area prefix matching the file."""
    errors = []
    seen: dict[str, list] = {}
    for aid in corpus.area_ids:
        area = corpus.areas[aid]
        for kind in ("threats", "controls"):
            for record in area.get(kind) or []:
                rid = record.get("id", "")
                if not TC_ID.fullmatch(rid):
                    errors.append(f"{rid or '<missing>'}: ID does not match ^[TC]-(A|B|P)\\d{{1,2}}-\\d+$")
                    continue
                if rid.split("-")[1] != aid:
                    errors.append(f"{rid}: area prefix does not match its file (area {aid})")
                seen.setdefault(rid, []).append(aid)
    for rid, areas in sorted(seen.items()):
        if len(areas) > 1:
            errors.append(f"{rid}: duplicate ID ({len(areas)} occurrences: {', '.join(areas)})")
    return errors


def rule_3_claims(corpus: Corpus) -> list[str]:
    """Every T-/C-/F-ID in the areas has exactly one claims record, and
    every claims record resolves (or its split_from does)."""
    errors = []
    wanted = set(corpus.threats) | set(corpus.controls)
    for aid in corpus.area_ids:
        wanted |= set(corpus.areas[aid].get("facts") or [])

    counts: dict[str, int] = {}
    for _path, claim in corpus.claims:
        counts[claim["id"]] = counts.get(claim["id"], 0) + 1

    for rid in sorted(wanted - set(counts)):
        errors.append(f"{rid}: no claims record")
    resolvable = wanted | set(corpus.fact_ids)
    for rid in sorted(set(counts) - resolvable):
        errors.append(f"{rid}: claims record does not resolve to an area record or fact")
    for rid, count in sorted(counts.items()):
        if count > 1:
            errors.append(f"{rid}: {count} claims records (exactly one required)")

    for path, claim in sorted(corpus.claims, key=lambda pc: (pc[0], pc[1]["id"])):
        split_from = claim.get("split_from")
        if split_from is None:
            continue
        for token in ANY_ID.findall(split_from):
            if token not in corpus.all_ids:
                errors.append(f"{path}: {claim['id']}: split_from cites unknown ID {token}")
    return errors


def rule_4_addresses(corpus: Corpus) -> list[str]:
    """Every addresses ID exists, in the same area or cross-area."""
    errors = []
    for cid in sorted(corpus.controls):
        aid, control = corpus.controls[cid]
        for target in control.get("addresses") or []:
            if target not in corpus.threats:
                errors.append(f"{cid}: addresses unknown threat {target}")
    return errors


def rule_5_references_exist(corpus: Corpus) -> list[str]:
    """Every F-/R-ID referenced anywhere exists in facts/references."""
    errors = []
    fact_ids = set(corpus.fact_ids)
    reference_ids = set(corpus.reference_ids)
    for path in corpus.scan_paths():
        text = path.read_text(encoding="utf-8")
        for token in sorted(set(F_ID.findall(text))):
            if token not in fact_ids:
                errors.append(f"{rel(path)}: references unknown fact {token}")
        for token in sorted(set(R_ID.findall(text))):
            if token not in reference_ids:
                errors.append(f"{rel(path)}: references unknown reference {token}")
    return errors


def rule_6_ids_and_replaced_by(corpus: Corpus, tag) -> tuple[list[str], list[str]]:
    """No previously existing ID disappeared (needs the previous tag);
    replaced_by validity runs whether or not a tag exists."""
    errors = []
    notices = []
    current = (
        set(corpus.threats) | set(corpus.controls) | set(corpus.fact_ids)
        | set(corpus.reference_ids) | set(corpus.feature_ids)
    )

    if tag is None:
        notices.append("no previous tag, rule 6 (disappeared IDs) skipped")
    else:
        previous = set()
        for path in paths_at(tag, "data/areas"):
            previous |= collect_ids(yaml_at(tag, path) or {})
        previous |= collect_ids(yaml_at(tag, "data/facts.yaml") or {}, kinds=())
        previous |= collect_ids(yaml_at(tag, "data/references.yaml") or {}, kinds=())
        features_doc = yaml_at(tag, "data/features.yaml") or {}
        previous |= {f["id"] for f in features_doc.get("features") or []}
        for rid in sorted(previous - current):
            errors.append(f"{rid}: existed at {tag} but has disappeared (retire in place instead)")

    records = (
        [(tid, t) for tid, (_a, t) in sorted(corpus.threats.items())]
        + [(cid, c) for cid, (_a, c) in sorted(corpus.controls.items())]
        + [(f["id"], f) for f in corpus.facts]
        + [(r["id"], r) for r in corpus.references]
        + [(f["id"], f) for f in corpus.features]
    )
    for rid, record in records:
        status = record.get("status")
        replaced_by = record.get("replaced_by") or []
        if replaced_by and status != "retired":
            errors.append(f"{rid}: replaced_by is non-empty but status is {status!r}, not retired")
        for target in replaced_by:
            if target not in corpus.all_ids:
                errors.append(f"{rid}: replaced_by cites unknown ID {target}")
    return errors, notices


def rule_7_no_unverified(corpus: Corpus) -> list[str]:
    errors = []
    for path, claim in sorted(corpus.claims, key=lambda pc: (pc[0], pc[1]["id"])):
        if str(claim.get("verification", "")).startswith("Unverified"):
            errors.append(f"{path}: {claim['id']}: verification starts with \"Unverified\"")
    return errors


NORMATIVE_WORDS = ("requires", "MUST", "mandatory")


def rule_8_normative_claims(corpus: Corpus) -> list[str]:
    errors = []
    for path, claim in sorted(corpus.claims, key=lambda pc: (pc[0], pc[1]["id"])):
        text = claim.get("claim") or ""
        if not any(word in text for word in NORMATIVE_WORDS):
            continue
        if claim.get("tier") != 1 or claim.get("verification") != "Verified — primary":
            errors.append(
                f"{path}: {claim['id']}: normative-form claim (contains "
                f"{', '.join(w for w in NORMATIVE_WORDS if w in text)}) has tier "
                f"{claim.get('tier')!r} and verification {claim.get('verification')!r}, "
                "expected tier 1 and \"Verified — primary\""
            )
    return errors


def rule_9_last_changed(corpus: Corpus, tag, version: str) -> tuple[list[str], list[str]]:
    """Release only: last_changed matches content change since the previous tag."""
    errors = []
    notices = []
    if tag is None:
        notices.append("no previous tag, rule 9 skipped")
        return errors, notices

    previous_records: dict[str, dict] = {}
    for path in paths_at(tag, "data/areas"):
        doc = yaml_at(tag, path) or {}
        for kind in ("threats", "controls"):
            for record in doc.get(kind) or []:
                previous_records[record["id"]] = record
    for record in yaml_at(tag, "data/facts.yaml") or []:
        previous_records[record["id"]] = record
    features_doc = yaml_at(tag, "data/features.yaml") or {}
    for record in features_doc.get("features") or []:
        previous_records[record["id"]] = record

    current_records: dict[str, dict] = {}
    for _aid, record in corpus.threats.values():
        current_records[record["id"]] = record
    for _aid, record in corpus.controls.values():
        current_records[record["id"]] = record
    for record in corpus.facts + corpus.features:
        current_records[record["id"]] = record

    def content(record: dict) -> dict:
        return normalise_whitespace(
            {k: v for k, v in record.items() if k != "last_changed"}
        )

    for rid in sorted(current_records):
        previous_record = previous_records.get(rid)
        if previous_record is None:
            continue  # new record; rule 9 governs changed and unchanged records
        if content(current_records[rid]) != content(previous_record):
            if current_records[rid].get("last_changed") != version:
                errors.append(
                    f"{rid}: content differs from {tag} but last_changed is "
                    f"{current_records[rid].get('last_changed')!r}, expected {version!r}"
                )
        else:
            if current_records[rid].get("last_changed") != previous_record.get("last_changed"):
                errors.append(
                    f"{rid}: content unchanged since {tag} but last_changed changed to "
                    f"{current_records[rid].get('last_changed')!r}"
                )
    return errors, notices


def rule_10_manifests(corpus: Corpus) -> list[str]:
    errors = []
    membership: dict[str, list] = {aid: [] for aid in corpus.area_ids}
    for path in corpus.manifest_files:
        manifest = load_yaml(path)
        catalogue = manifest.get("id", path.stem)
        for aid in manifest.get("areas") or []:
            if aid not in corpus.areas:
                errors.append(f"{rel(path)}: catalogue {catalogue} lists unknown area {aid}")
            else:
                membership[aid].append(catalogue)
    for aid in sorted(membership):
        if not membership[aid]:
            errors.append(f"{aid}: belongs to no catalogue")
    return errors


# --------------------------------------------------------------------------
# warning rules
# --------------------------------------------------------------------------

def warning_1_used_in(corpus: Corpus) -> list[str]:
    """Warning 1, used_in half: stored used_in differs from the regenerated value."""
    warnings = []
    regenerated = regenerate_used_in(corpus.root)
    for fact in corpus.facts:
        stored = list(fact.get("used_in") or [])
        regen = regenerated.get(fact["id"], {})
        regen_areas = list(regen.get("areas", []))
        if stored != regen_areas:
            extra = ""
            if regen.get("other"):
                extra = f"; also referenced in: {', '.join(regen['other'])}"
            warnings.append(
                f"{fact['id']}: stored used_in {stored} != regenerated {regen_areas} "
                f"(used_in_text: {fact.get('used_in_text')!r}{extra})"
            )
    return warnings


def warning_1_cited_by(corpus: Corpus) -> list[str]:
    """Warning 1, "Cited by" half: stored cited_by_text differs from the
    regenerated citation set."""
    warnings = []
    regenerated = regenerate_cited_by(corpus)
    for reference in corpus.references:
        stored = parse_cited_by_text(reference.get("cited_by_text") or "", corpus)
        regen = set(regenerated.get(reference["id"], []))
        if stored != regen:
            warnings.append(
                f"{reference['id']}: stored cited-by {sorted(stored)} != "
                f"regenerated {sorted(regen)}"
            )
    return warnings


def warning_2_requirement(corpus: Corpus) -> list[str]:
    return [
        f"{cid}: requirement is null"
        for cid in sorted(corpus.controls)
        if corpus.controls[cid][1].get("requirement") is None
    ]


def warning_3_trigger_rule(corpus: Corpus) -> list[str]:
    warnings = []
    for cid in sorted(corpus.controls):
        _aid, control = corpus.controls[cid]
        if control.get("type") != "conditional":
            continue
        trigger = control.get("trigger")
        if trigger is None or trigger.get("rule") is None:
            warnings.append(f"{cid}: conditional control has trigger.rule null")
    return warnings


def warning_4_snapshot(corpus: Corpus) -> list[str]:
    return [
        r["id"] + ": snapshot is null"
        for r in corpus.references
        if r.get("snapshot") is None
    ]


WARNING_5_MARKERS = ("standard practice", "secondary", "single source")


def warning_5_verification(corpus: Corpus) -> list[str]:
    warnings = []
    for path, claim in sorted(corpus.claims, key=lambda pc: (pc[0], pc[1]["id"])):
        verification = str(claim.get("verification") or "")
        markers = [m for m in WARNING_5_MARKERS if m in verification]
        if markers:
            warnings.append(
                f"{path}: {claim['id']}: verification contains {', '.join(markers)} "
                f"({verification!r})"
            )
    return warnings


def warning_6_question(corpus: Corpus) -> list[str]:
    return [
        f["id"] + ": question is null"
        for f in corpus.features
        if f.get("question") is None
    ]


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def run(release: str | None = None, root: Path | None = None) -> int:
    corpus = Corpus(root)

    errors: list[tuple[int, str]] = []
    warnings: list[tuple[str, str]] = []
    notices: list[str] = []

    def add_errors(rule: int, messages):
        for message in messages:
            errors.append((rule, message))

    tag = previous_tag(corpus.root)

    add_errors(1, rule_1_schema(corpus))
    add_errors(2, rule_2_ids(corpus))
    add_errors(3, rule_3_claims(corpus))
    add_errors(4, rule_4_addresses(corpus))
    add_errors(5, rule_5_references_exist(corpus))
    rule6_errors, rule6_notices = rule_6_ids_and_replaced_by(corpus, tag)
    add_errors(6, rule6_errors)
    notices.extend(rule6_notices)
    add_errors(10, rule_10_manifests(corpus))

    if release:
        add_errors(7, rule_7_no_unverified(corpus))
        add_errors(8, rule_8_normative_claims(corpus))
        rule9_errors, rule9_notices = rule_9_last_changed(corpus, tag, release)
        add_errors(9, rule9_errors)
        notices.extend(rule9_notices)

    w1a = warning_1_used_in(corpus)
    w1b = warning_1_cited_by(corpus)
    for message in w1a:
        warnings.append(("1 (used_in)", message))
    for message in w1b:
        warnings.append(("1 (cited by)", message))
    for message in warning_2_requirement(corpus):
        warnings.append(("2", message))
    for message in warning_3_trigger_rule(corpus):
        warnings.append(("3", message))
    for message in warning_4_snapshot(corpus):
        warnings.append(("4", message))
    for message in warning_5_verification(corpus):
        warnings.append(("5", message))
    for message in warning_6_question(corpus):
        warnings.append(("6", message))

    errors.sort(key=lambda e: (e[0], e[1]))
    warnings.sort(key=lambda w: (w[0], w[1]))

    mode = f"release {release}" if release else "normal"
    print(f"catalogue check ({mode}): {len(errors)} errors, {len(warnings)} warnings")

    for notice in notices:
        print(f"NOTE: {notice}")

    counts: dict[str, int] = {}
    for rule, _message in warnings:
        counts[rule] = counts.get(rule, 0) + 1
    summary = ", ".join(f"W{rule}={count}" for rule, count in sorted(counts.items()))
    if summary:
        print(f"warning counts: {summary}")

    for rule, message in errors:
        print(f"ERROR [rule {rule}] {message}")
    for rule, message in warnings:
        print(f"WARNING [rule {rule}] {message}")

    if errors:
        print(f"check failed: {len(errors)} error(s)")
        return 1
    print("check passed")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--release",
        metavar="VERSION",
        help="release mode: also apply rules 7, 8 and 9 against VERSION",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root to check (default: the repository containing this file)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root else None
    return run(release=args.release, root=root)


if __name__ == "__main__":
    sys.exit(main())
