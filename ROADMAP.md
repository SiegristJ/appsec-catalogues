# Roadmap

Design notes for work that is deliberately deferred. Nothing here is built yet. The notes record what was decided and why, so the reasoning survives until the work starts.

## Principles already fixed

- **Corpus and catalogues.** `data/` is one corpus; a catalogue is a named selection of areas (`catalogues/*.yaml`). Catalogues may overlap. Further catalogues (platform, mobile) are added to this repository and published under their own paths on appsec.complects.com.
- **Global, permanent IDs.** T-, C-, F-, R- and feature IDs never change meaning, are never renumbered, and are retired in place with `replaced_by`.
- **One version for the repository.** Per-record `last_changed` gives finer detail.
- **Irreversible choices are the cited ones:** URL paths, ID stability, version semantics. Everything else can be added later from git history and release files.

## 1. Checklists per audience

A checklist is a view over `features.yaml`, filtered to the features that pull any area in a given catalogue. Audiences (for example a mobile architect or developer) get checklists for their catalogue. New audiences add features to the shared vocabulary; shared concerns such as user login keep their existing feature IDs.

Prerequisites: `question` and `guidance` written for each feature; the trigger vocabulary for conditional controls approved (see `IMPORT-NOTES.md`, "Feature vocabulary to approve").

Build step when started: generate a blank checklist per catalogue (YAML and HTML).

## 2. Assessment record

The machine-readable output of an assessment, and the primary artefact; all readable formats (HTML, PDF, DOCX) are rendered from it and print its hash. It replaces a separate checklist file: the same file is saved, resumed, compared across versions and kept in a project's repository as the review artefact.

Contents:

1. **Pinning:** catalogue version, `catalogue.json` hash, generating tool and version, `record_format` version.
2. **Answers:** each feature present, absent or unknown, with optional notes, answerer and date. Unknown is allowed and appears as an open item.
3. **Selection with reasons:** every selected ID and why (universal; feature X; follow-up question Y), plus the text of each selected item as at assessment time, so the record stands alone.
4. **Decisions:** per control, applicable or not applicable, with a justification required for not applicable.

Format rules: stable key order, one entry per line (readable diffs); a published, versioned JSON Schema.

Boundary: the record stops at applicability decisions. Implementation status, evidence links and due dates belong to a compliance-tracking tool; the record may leave room for team-defined extension fields but the catalogue does not define them.

`verify`: recompute the selection from the pinned version and the answers and confirm it matches the record. This detects hand edits and tool drift.

## 3. Moving a record between versions

Upgrade a record from version N to M by recomputing the selection under M, then classifying:

- **Unchanged items:** decision carried.
- **Changed items** (`last_changed` after N): decision carried, flagged for review, with old and new text side by side.
- **New items** (new controls in selected areas, or newly pulled areas): undecided.
- **No longer selected** (mapping changed): shown with reason; old decision kept in history.
- **Retired items:** shown with `replaced_by`; replacements undecided.
- **New features:** unanswered questions.
- **Changed features** (`last_changed` after N): answer flagged for re-answer.

Output: a new record pinned to M, plus an upgrade report. Nothing is decided for the team; every judgement the upgrade could get wrong is surfaced.

Also required:

- Host every released `catalogue.json` permanently at `/<catalogue>/versions/<version>/catalogue.json` (collected from GitHub release files by the release workflow), so `verify` and upgrades can load version N.
- Conversion steps in the tool for each `record_format` change.
- A published ID migration map with every major version.

## 4. Selection logic as data

Store feature-to-area pulls and conditional-control trigger rules in `catalogue.json`, so that every implementation (`extract.py`, the in-browser app) is a thin evaluator. Maintain a shared set of test cases (a checklist plus the exact expected ID list) and run it in CI against every implementation.

## 5. In-browser assessment app

A static page on the catalogue's site that builds the form from `catalogue.json`, asks conditional-control triggers as follow-up questions, renders the control document, and exports the assessment record plus readable formats (print stylesheet for PDF; DOCX and Markdown optional). Everything runs in the browser; answers never leave the user's machine and are not collected by analytics. Uploading an older record runs the upgrade in section 3.

Order: after items 1, 2 and 4. The app's quality depends on the feature questions and trigger vocabulary.

## 6. SQLite build output

Load the YAML corpus into SQLite during the build: one table per record type, foreign keys for every cross-reference (`addresses`, `sources`, `facts`, `pulls`, `replaced_by`), and an FTS5 full-text index over names, statements and mechanisms.

Uses:

- **Checks as queries.** Referential rules in `check.py` become foreign-key failures at load time; cross-record rules become short SQL assertions. Shape validation stays with JSON Schema.
- **Version comparison.** `ATTACH` the previous tag's database and query across both for the disappeared-ID and `last_changed` rules.
- **Maintenance queries.** For example, controls resting on tier 2 or weaker references, or areas citing a source that has a new edition (the refresh process's impact question).
- **Release download.** `catalogue.sqlite` for tools and agents; optionally a Datasette view for browsing.

Constraints: build output only, never committed or edited; exempt from byte-identical output (compare a text `.dump` instead); the in-browser app keeps using `catalogue.json`.

Priority: low. Nothing depends on it; adopt it if `check.py` rules become hard to maintain in Python, or when maintenance queries become routine.

## 7. Other deferred items

- A shared references page at `/references/`.
- Preview deployments for pull requests, if regular non-technical reviewers or many outside contributors appear.
- The emerging-items document for fast-moving issues not yet in standards, with its own evidentiary standard.
- The evidentiary boundary decision (strict tier 1, or tier 1 plus issuer-owned tier 2).
