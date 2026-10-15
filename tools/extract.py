#!/usr/bin/env python3
"""Architecture review extract (SETUP-INSTRUCTIONS 8, extract.py half).

    python tools/extract.py reviews/<name>.yaml [--since <version>]

reads a review checklist, checks it against the current build, and writes
build/out/extract-<name>.md and .html (standalone, same Pandoc pipeline and
anchor strategy as build.py — every Threats/Controls table ID cell carries
its ID as an anchor, so a spec can deep-link the records it pulled in).

The extract contains (SETUP 8, verbatim requirements):

  - the stamp and the checklist itself (the feature table with each label
    and answer);
  - the universal areas (data/features.yaml `universal_areas`, 9 today);
  - the areas pulled by present features;
  - each included area's threats, baseline controls (type baseline or
    defence_in_depth, the catalogue's own Baseline summary grouping),
    residual-risk line and Facts and sources line;
  - conditional controls: whose trigger.text relates to a present feature
    where a trigger.rule exists — while rules are null, EVERY conditional
    control in included areas, under "Conditional — confirm applicability"
    with its trigger text so the reviewer confirms applicability by hand;
  - the features declared absent and the areas they excluded (areas the
    feature pulls that no present feature or universality includes).

Process areas P1–P4 are not included: SETUP 4.4 parks them in
`process_areas` outside the applicability index, whose own framing says
they "always apply to the delivery organisation and are not selected
here", and SETUP 8's extract list names only universal and feature-pulled
areas. One line in the output says so. Recorded in IMPORT-NOTES.

The area list and its order come from catalogues/web.yaml (SETUP 4.9),
never hard-coded.

Errors (non-zero exit, each offender named):

  - any feature in data/features.yaml not declared in the checklist;
  - a checklist key that is not a feature in features.yaml (typo guard:
    otherwise a misspelled feature silently excludes its areas);
  - an answer that is not `present` or `absent`;
  - `catalogue_version` not exactly matching the build's version stamp
    (build/ai/catalogue.json meta.version — "untagged" until the stage-10
    tag; the check is exact-string, SETUP 8 "does not match the build").

`--since <version>` adds a "Changed since <version>" section: every
threat, control and fact in the extract whose `last_changed` is strictly
later than <version>, each with its `last_changed` and the change-log rows
mentioning the ID (build.py's whole-row mention rule). "Later than" uses
semver precedence: numeric components compared element-wise, zero-padded
when shorter; a pre-release sorts below its own release; pre-release
identifiers compared per semver §11 (numeric identifiers numerically and
below alphanumeric ones, otherwise ASCII-lexically, longer lists above
their prefixes); build metadata ignored; optional leading v/V. If nothing
changed, a single line says so.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402  (tools/build.py — shared build/pandoc/changelog helpers)
import check  # noqa: E402  (tools/check.py — Corpus)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "out"

PRESENT, ABSENT = "present", "absent"


def id_cell(record: dict) -> str:
    """ID cell with the per-record version suffix, generate.py's own
    presentation (SETUP 8, "Per-record version in outputs"; suffix form)."""
    return f"{record['id']} · {record['last_changed']}"


def threats_table(area: dict) -> str:
    rows = []
    for threat in area["threats"]:
        rows.append([id_cell(threat), threat["name"], threat["mechanism"],
                     "; ".join(threat.get("references") or []) or "—"])
    return build.markdown_table(
        ["ID", "Threat", "Mechanism", "Reference"], rows)


def controls_rows(controls: list, with_trigger: bool) -> list:
    rows = []
    for control in controls:
        row = [id_cell(control), control["statement"]]
        if with_trigger:
            trigger = (control.get("trigger") or {}).get("text")
            rows.append(row + [trigger or "— (no trigger text)",
                               ", ".join(control.get("addresses") or []) or "—",
                               ", ".join(control.get("asvs") or []) or "—"])
        else:
            rows.append(row + [", ".join(control.get("addresses") or []) or "—",
                               ", ".join(control.get("asvs") or []) or "—",
                               control["type_text"]])
    return rows


def area_section(area: dict, reasons: dict) -> str:
    baseline = [c for c in area["controls"]
                if c["type"] in ("baseline", "defence_in_depth")]
    conditional = [c for c in area["controls"] if c["type"] == "conditional"]
    lines = [f"## {area['id']} {area['title']}", ""]
    lines.append(f"**Applies when.** {area['applies_when']['text']}")
    lines.append("")
    lines.append(f"**Included because.** {reasons[area['id']]}")
    lines.append("")
    lines += ["**Threats**", "", threats_table(area), ""]
    lines += [f"**Baseline controls** ({len(baseline)})", "",
              build.markdown_table(
                  ["ID", "Control", "Addresses", "ASVS 5.0", "Type"],
                  controls_rows(baseline, with_trigger=False)), ""]
    lines += [f"**Conditional — confirm applicability** ({len(conditional)})",
              "",
              build.markdown_table(
                  ["ID", "Control", "Trigger", "Addresses", "ASVS 5.0"],
                  controls_rows(conditional, with_trigger=True)), ""]
    lines.append(f"**Residual risk.** {area['residual_risk']} "
                 f"({area['residual_rating']}; remains: "
                 f"{area['residual_summary']})")
    lines.append("")
    facts = ", ".join(area.get("facts") or []) or "—"
    sources = ", ".join(area.get("sources") or []) or "—"
    lines.append(f"**Facts and sources.** Facts: {facts}. Sources: {sources}.")
    return lines


def changed_since_section(since: str, records: list, rows: list,
                          mentions: dict) -> list:
    try:
        since_key = build.version_key(since)
    except SystemExit as exc:
        raise SystemExit(f"--since {since!r}: {exc}") from None
    changed = [record for record in records
               if build.version_key(record["last_changed"]) > since_key]
    lines = [f"## Changed since {since}", ""]
    if not changed:
        lines.append(f"No threat, control or fact in this extract has "
                     f"last_changed later than {since}.")
        return lines
    lines.append(f"{len(changed)} of {len(records)} threats, controls and "
                 f"facts in this extract have last_changed later than "
                 f"{since}.")
    lines.append("")
    for record in changed:
        rid = record["id"]
        area = record.get("area", "")
        where = f" ({area})" if area else ""
        lines.append(f"- **{rid}**{where} — last changed "
                     f"{record['last_changed']}.")
        row_indexes = mentions.get(rid, [])
        if not row_indexes:
            lines.append(f"  - No change-log row mentions {rid}.")
        for index in row_indexes:
            date, _ids, change, trigger = rows[index][:4]
            lines.append(f"  - {date} · {trigger} · {change}")
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Architecture review extract (SETUP-INSTRUCTIONS 8)")
    parser.add_argument("checklist", type=Path,
                        help="review checklist, conventionally reviews/<name>.yaml")
    parser.add_argument("--since", metavar="VERSION", default=None,
                        help="add a 'Changed since VERSION' section")
    args = parser.parse_args(argv)

    if not args.checklist.exists():
        print(f"ERROR: checklist not found: {args.checklist}", file=sys.stderr)
        return 1
    doc = yaml.safe_load(args.checklist.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        print(f"ERROR: {args.checklist} is not a YAML mapping", file=sys.stderr)
        return 1

    meta = build.load_build_meta()  # SystemExit if no build exists

    corpus = check.Corpus(ROOT)
    manifest = build.catalogue_manifest()
    features_doc = corpus.features_doc
    features = corpus.features
    feature_by_id = {f["id"]: f for f in features}
    universal = list(features_doc["universal_areas"])

    review = str(doc.get("review") or args.checklist.stem)
    declared = doc.get("features")
    errors = []
    if not isinstance(declared, dict):
        errors.append(f"{args.checklist}: 'features' must be a mapping of "
                      "feature ID -> present|absent")
        declared = {}
    unknown = sorted(k for k in declared if k not in feature_by_id)
    for fid in unknown:
        errors.append(f"undeclared feature name in checklist (not in "
                      f"data/features.yaml): {fid}")
    undeclared = sorted(fid for fid in feature_by_id if fid not in declared)
    for fid in undeclared:
        errors.append(f"feature not declared in checklist: {fid} "
                      f"({feature_by_id[fid]['label']})")
    for fid in sorted(declared):
        answer = declared[fid]
        if fid in feature_by_id and answer not in (PRESENT, ABSENT):
            errors.append(f"feature {fid}: answer must be 'present' or "
                          f"'absent', got {answer!r}")
    checklist_version = doc.get("catalogue_version")
    if checklist_version != meta["version"]:
        errors.append(f"catalogue_version mismatch: checklist says "
                      f"{checklist_version!r}, build stamp is "
                      f"{meta['version']!r} — rebuild or fix the checklist")
    if errors:
        return fail(errors)

    # -- selection ---------------------------------------------------------
    present = [f for f in features if declared[f["id"]] == PRESENT]
    absent = [f for f in features if declared[f["id"]] == ABSENT]
    present_ids = [f["id"] for f in present]

    pulls: dict[str, list[str]] = {}
    for feature in present:
        for aid in feature["pulls"]:
            pulls.setdefault(aid, []).append(feature["id"])

    included, reasons = [], {}
    for aid in manifest["areas"]:
        why = []
        if aid in universal:
            why.append("universal")
        for fid in pulls.get(aid, []):
            why.append(f"feature {fid}")
        if why:
            included.append(aid)
            reasons[aid] = "; ".join(why)

    excluded_by = {}
    for feature in absent:
        excluded = [aid for aid in feature["pulls"] if aid not in reasons]
        excluded_by[feature["id"]] = excluded

    # -- markdown ----------------------------------------------------------
    lines = [build.stamp_line(meta), "",
             f"# Architecture review extract — {review}", ""]
    lines.append(f"Generated from the {manifest['title']} "
                 f"(`catalogues/{manifest['id']}.yaml`). Conditional "
                 "controls are listed with their trigger text for manual "
                 "confirmation while trigger rules are not yet approved.")
    lines.append("")

    lines += ["## Checklist", "",
              build.markdown_table(
                  ["Feature", "Label", "Answer"],
                  [[f["id"], f["label"], declared[f["id"]]] for f in features]),
              ""]

    lines += [f"## Universal areas ({len(universal)})", "",
              build.markdown_table(
                  ["Area", "Title"],
                  [[aid, corpus.areas[aid]["title"]] for aid in universal]),
              ""]

    pulled_rows = [[aid, corpus.areas[aid]["title"],
                    ", ".join(pulls[aid])]
                   for aid in manifest["areas"]
                   if aid in pulls and aid not in universal]
    lines += ["## Areas pulled by present features", "",
              build.markdown_table(["Area", "Title", "Pulled by"], pulled_rows),
              ""]
    process = [aid for aid in manifest["areas"]
               if aid in features_doc.get("process_areas", [])]
    if process:
        lines.append(f"Process areas {', '.join(process)} apply to the "
                     "delivery organisation rather than the application "
                     "architecture and are outside this extract's scope "
                     "(applicability index: \"not selected here\").")
        lines.append("")

    for aid in included:
        lines += area_section(corpus.areas[aid], reasons)
        lines.append("")

    lines += ["## Features declared absent and the areas they excluded", "",
              build.markdown_table(
                  ["Feature", "Label", "Areas excluded"],
                  [[f["id"], f["label"],
                    ", ".join(excluded_by[f["id"]]) or "— (none excluded)"]
                   for f in absent]),
              ""]

    # -- --since -----------------------------------------------------------
    if args.since:
        rows, mentions = build.change_log_mentions(corpus)
        records = []
        for aid in included:
            area = corpus.areas[aid]
            for threat in area["threats"]:
                records.append({"id": threat["id"],
                                "last_changed": threat["last_changed"],
                                "area": aid})
            for control in area["controls"]:
                records.append({"id": control["id"],
                                "last_changed": control["last_changed"],
                                "area": aid})
        seen = set()
        for aid in included:
            for fid in corpus.areas[aid].get("facts") or []:
                if fid not in seen:
                    seen.add(fid)
                    fact = next(f for f in corpus.facts if f["id"] == fid)
                    records.append({"id": fid,
                                    "last_changed": fact["last_changed"],
                                    "area": None})
        lines += changed_since_section(args.since, records, rows, mentions)

    text = "\n".join(lines).rstrip("\n") + "\n"
    OUT.mkdir(parents=True, exist_ok=True)
    md_path = OUT / f"extract-{args.checklist.stem}.md"
    md_path.write_text(text, encoding="utf-8")

    html_path = OUT / f"extract-{args.checklist.stem}.html"
    build.run(build.base_args(
        md_path, html_path, f"Architecture review extract — {review}",
        meta, ["--standalone"]), build.pandoc_env(meta["built"]))

    print(f"wrote {md_path} and {html_path}")
    print(f"stamp: {build.stamp_line(meta)}")
    return 0


def fail(messages: list[str]) -> int:
    for message in messages:
        print(f"ERROR: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
