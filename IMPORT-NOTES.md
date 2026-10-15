# Import notes

The importing agent's record of ambiguities, deviations, splits, merges, null fields
and open items, kept per SETUP-INSTRUCTIONS section 1 rules 3–4. Entries are appended
as they arise, one numbered item per decision, most recent last.

## Deviations from SETUP-INSTRUCTIONS

1. **Input file locations and names** (2026-10-15). Section 2 fixes input names next
   to SETUP-INSTRUCTIONS.md; the actual inputs deviate:
   - The ten register/catalogue/reconciliation/history exports are at the workspace
     root under their fixed names, as specified.
   - The two source reports live under `Source/2026-10-12/` with export names, not
     `source-report-claude.md` / `source-report-gemini.docx`:
     - `Web_Application_Security_Overview_Claude_2026-10-12.md` (identity confirmed:
       title, ~25-area breadth-first shape and exactly 88 citations match the
       reconciliation accounting)
     - `Web_Application_Security_Overview_Gemini_2026-10-12.md` (identity confirmed:
       title, ten-section depth-first shape, exactly 110 citations, all nine
       Gemini-only topic clusters present, and the documented errors still in place)
     - `Web Application Security Overview.docx` — a docx export of the Gemini report;
       the owner confirmed (2026-10-15) the docx and md are identical content from the
       identical Google Docs source file. Both will be archived (stage 2), the docx
       under the canonical name `source-report-gemini.docx`.
   - The copies are renamed to the canonical `archive/origin/source-reports/` names at
     stage 2; content is copied byte-for-byte, never edited.
2. **Repository location** (2026-10-15). `appsec-catalogues/` was created inside the
   `WebAppSec` workspace as a subdirectory, exports and `Source/` remaining outside
   the repository, untouched (owner-confirmed).
3. **`.gitignore` includes `.DS_Store`** (2026-10-16) beyond the section 10 list
   (`build/`, `__pycache__/`, `.venv/`) — macOS housekeeping; no content impact.
4. **Empty-directory handling in the scaffold** (2026-10-16). Directories that stay
   empty by design are tracked via `.gitkeep` (`archive/sources/`); all other
   directories materialise in git as their stages land.
5. **Typst installed during setup** (2026-10-16). Ground rule 5's network exception
   names pip and pandoc only; the owner approved `brew install typst` (0.15.1) for
   the stage 8 PDF engine.
6. **HISTORY.md references point into the repository** (owner direction, 2026-10-16).
   The export's document-status table linked claude.ai artifact URLs; the repo's
   HISTORY.md may only refer to files in the repository. The table's link targets
   were replaced with repo-relative paths (catalogue → `data/`, register → `register/`,
   reconciliation and source reports → `archive/origin/`, provenance archive →
   `archive/sources/`, emerging → `emerging/`, runbook → `runbook/`), the unlinked
   source-reports row gained its `archive/origin/source-reports/` link, and the two
   "Frozen; to be archived" states were updated to "Frozen; archived" (the archiving
   has happened, in this repository). All other HISTORY.md text is the verbatim
   export. The frozen archive copies under `archive/origin/` keep their original
   external references unchanged, as part of the frozen record.

## Ambiguities and judgment calls

1. **Mixed and special Type cells** (2026-10-16, stage 3; SETUP 4.1 "choose
   the first type, log the choice"; `type_text` always verbatim):
   - `C-A11-6` "Baseline (L2); Conditional (L3)" → `type: baseline`.
   - `C-A11-8` "Conditional: third-party scripts; mandatory on payment pages
     under PCI DSS v4.0.1 6.4.3 and 11.6.1" → `type: conditional`;
     `trigger.text` is everything after "Conditional:" verbatim, i.e.
     "third-party scripts; mandatory on payment pages under PCI DSS v4.0.1
     6.4.3 and 11.6.1" — the PCI clause stays in `trigger.text` because it
     follows the colon in the export (the derived baseline/conditional table
     carries the same parenthetical).
   - `C-B4-3` "Conditional; mandatory for cardholder-data applications under
     PCI DSS v4.0.1 6.4.2 (F-53). Disputed: WAF value (see Where experts
     differ)" → `type: conditional`, `disputed: true`, `trigger.text: null`
     (the export has no "Conditional: X" form to read a trigger from).
   - `C-P4-4` "Conditional" → `type: conditional`, `trigger.text: null`
     (no trigger stated in the export).
2. **Disputed marker split from trigger text** (2026-10-16). `disputed: true`
   is set on the five Type cells containing "Disputed" (C-A1-2, C-A7-5,
   C-A9-6, C-B2-4, C-B4-3). For the two "Conditional: X. Disputed (…)" cells
   the marker sentence is excluded from `trigger.text` (C-A1-2 → "passkeys
   deployed", C-A7-5 → "intermediaries"); the marker remains in `type_text`
   and is carried by the flag.
3. **P-area `applies_when`** (2026-10-16). P1–P3 say "Always, to the delivery
   organisation" and P4 "Always, to the operating organisation" — not
   architecture features. Stored verbatim in `applies_when.text` with
   `universal: false` and `features: []`; the four areas are listed in
   `features.yaml` `process_areas` instead (SETUP 4.4).
4. **Heading demotions** (2026-10-16). In `data/front/00-how-to-use.md`,
   `02-reference-stack.md`, `03-principles.md`, `04-threat-evidence.md` and
   `data/maintenance.md` the section `##` heading was demoted to `#` and followed
   by one blank line; every other byte is verbatim from the export
   (diff-verified), including each section's "Facts and sources" and
   "Last reviewed · Watch" lines.
5. **Non-area pulls rows** (2026-10-16). The applicability-index rows
   "Payments or cardholder data…" and "Personal data" name non-area targets
   ("Compliance mapping (PCI DSS)" / "(GDPR)"): `pulls` keeps only the area
   IDs (A11; A13, A9), `pulls_text` keeps the verbatim cell.
6. **R-107 has no URL** in the export (plain-text Reference cell) →
   `url: null`, title verbatim (SETUP 4.3).
7. **Appendix B title cells contain markdown links** (2026-10-16). For
   single-link cells the link is reduced to its link text and the URL moved
   to `url` (trailing qualifiers such as "(Pang et al.)" kept in `title`).
   Two cells contain two links (R-19, R-125): their `title` is kept verbatim
   with the markdown so the second URL is not lost; `url` holds the first
   link's URL.
8. **Tier qualifiers** (2026-10-16). "2 (product-specific)" (R-125, R-129,
   R-130, R-131, R-137) → `tier: 2`, `tier_note: "(product-specific)"`
   verbatim including parentheses.
9. **Edition cells "—"** (R-50, R-93) stored verbatim as "—" rather than
   null; SETUP states no rule for this column and the em dash is the
   export's text.
10. **Disputes `ids` cells can contain area references** (2026-10-16):
    "Passkey protection" → "C-A1-1, C-A1-2, A2"; "Prompt injection
    prevention" → "A12". Kept verbatim as list items, not expanded or
    dropped (the "Disputed" markers on controls cover only the five Type
    cells above; the disputes table's own ID column is the authoritative
    link list).
11. **Compliance `controls` mixed cells** (2026-10-16). "P1 to P4" and
    "ASVS column in every area" contain no control IDs and are kept as
    single verbatim list elements (area references kept as-is per SETUP
    4.6); "P1, P2" splits on the comma into two area references;
    "C-A13-6, C-A13-7, A9" splits into the control IDs plus the area
    reference A9 kept as-is. No control-ID ranges occur in these cells, so
    none were expanded. The `status` column is imported per SETUP 4.6
    although the stage-3 brief's deliverable list omits it (the spec is
    authoritative; the brief never overrides it).
12. **P2's testing-method table** (SETUP 12 item 8) stored in `extra_tables`
    as one entry `{title: null, rows: [[…], …]}` with the header row and all
    data rows verbatim; only cell padding was trimmed (table-syntax
    normalisation, §1 rule 1).
13. **`last_reviewed` "Oct 12, 2026"** stored as the YAML date `2026-10-12`
    (the form shown in SETUP 4.1); identical on all 23 areas.
14. **Verbatim bytes preserved** (2026-10-16): em dashes, curly quotes,
    "·", "×", "→", "≥" pass through unmodified in stored text; the en dash
    in "P1–P4" was normalised to a hyphen for parsing the residual-risk
    summary row only.
15. **`used_in` cells containing record IDs** (2026-10-16; found by the stage-3
    verifier). Five Appendix A "Used in" cells name record IDs rather than — or
    mixed with — areas: F-3 → `T-A3-1, T-A3-7`; F-4 → `T-A3-1 to T-A3-3`;
    F-29 → `C-A1-3, A1`; F-34 → `C-A5-4, A5`; F-45 → `C-A9-3, A9`. Section 4.2's
    example implies area IDs; the literal cell contents were kept in `used_in`
    (so the lists mix ID kinds) with the verbatim text in `used_in_text`.
    `check.py` warning 1 (regenerated `used_in` mismatch) is expected to fire on
    these at stage 5; normalising to area IDs is an owner call at that review.
16. **"Last verified" split convention** (2026-10-16, stage 4). Every cell
    combines date and verifier ("2026-10-12, Claude"); imported as
    `last_verified: 2026-10-12` (YAML date) plus `verified_by: Claude`. The
    split is mechanical (first comma in the cell); all 347 rows carry the
    same pair, so no variant arises.
17. **Tier and sources conventions never triggered** (2026-10-16, stage 4).
    SETUP 4.5 defines "—" → `tier: null`, "—" → `sources: []`,
    non-numeric tier content → `tier_text`, and R-ID range expansion in
    Sources; none occurs: all 347 Evidence tier cells are bare integers
    1–4 (no `tier_text` field was emitted), every Sources cell is a plain
    comma-separated R-ID list with no ranges, and neither column contains
    "—".
18. **Decision "—" kept verbatim** (2026-10-16, stage 4). 18 rows carry an
    em dash in Decision (C-A2-4, C-A6-4, C-A7-4, C-A10-6, T-A10-5, C-A11-9,
    T-A11-6, C-A12-4, C-B3-4, T-B5-5, C-B5-7, C-B6-3, C-P3-7, F-30, F-34,
    F-40, F-49, F-51); stored as the string "—" following the stage-3
    precedent for edition cells (ambiguity 9) — SETUP states no rule for
    this column, and the em dash is the export's text.
19. **Markdown backslash escapes kept verbatim** (2026-10-16, stage 4). Two
    claim cells contain export escapes: C-A2-2 "\_\_Host- prefix" and
    C-A6-4 "Sec-Fetch-\* validation". Stored byte-for-byte; unescaping is a
    normalisation the rules do not authorise (stage 3 likewise kept
    markdown backticks in stored text). Regeneration must re-escape these
    two cells when rendering the register.
20. **Extra claims-field placement** (2026-10-16, stage 4). §4.5 fixes the
    order of the ten base fields; `split_from` sits immediately after `id`
    and `tier_text` would sit immediately after `tier` —
    companion-next-to-primary, matching stage 3's `type_text`,
    `used_in_text`, `pulls_text` and `cited_by_text`. `tier_text` is in
    fact never emitted (see 17).
21. **C-A3-4 ASVS chapter mismatch — for the owner** (2026-10-16, stage 4;
    SETUP 12 item 5, flagged by the stage-3 verifier). The catalogue maps
    C-A3-4 to ASVS V15 (`data/areas/A03.yaml`, the drafting correction in
    the change-log row "Principles (least privilege), C-A3-4, C-A5-9, A7
    ASVS column" remapped mass assignment to V15), but its claims row
    still cites only V8-era sources: R-4 (OWASP API Security Top 10, 2023)
    and R-8 (OWASP Mass Assignment Cheat Sheet). Both sides imported as-is
    per SETUP; the owner should re-source the claim against V15-era
    material or re-map the sources.
22. **Change-log merge mechanics** (2026-10-16, stage 4). The addendum
    caption "**Latest entries** (to be merged into the table below at the
    next regeneration)" was consumed by the merge — it described a table
    that no longer exists. The "# Change log" heading and "Newest first."
    line are kept verbatim, the header and separator appear once, and all
    13 rows are byte-identical export rows (2 addendum + 11 main, all dated
    2026-10-12: addendum rows first, then main rows in export order).
23. **considered-not-included.md wording** (2026-10-16, stage 4). SETUP 4.8
    fixes the structure but not the header text; "# Considered and not
    included" was chosen from the filename, with element order following
    the spec sentence: header, then the empty four-column table
    (`Item | Source | Reason excluded | Reference`), then the TODO line
    verbatim.
24. **Claims record order = export row order** (2026-10-16, stage 4). Files
    are not re-sorted: A3's "A3 facts" rows follow the A3 threats/controls
    rows in `A03.yaml`, and A09 keeps the export's F-18, F-19, F-45, F-46
    order. The export's sections arrive in a non-numeric order (A3, front
    matter, A1, A4, A5, A11, …); each row lands in its area's file
    regardless.
25. **No annotated or unparseable ID cells** (2026-10-16, stage 4). Every
    ID cell matched the pure grammar (single ID, comma list, or
    same-prefix "to" range): the B2, B3, B4 and B6 tables are already one
    row per ID (the change log records that split), no annotated cell
    remains, and nothing outside the eight logged groups needed splitting.
    The parser rejects any deviation, so a future remnant cannot pass
    silently.
26. **Warning 1 has two halves; both are implemented** (2026-10-16,
    stage 5). §6 warning 1 reads "`used_in` and 'Cited by' values differ
    from the regenerated values"; the stage-5 brief's summary lists only
    `used_in`. §6 is the law for this stage, so `check.py` reports both,
    labelled `1 (used_in)` and `1 (cited by)`. Rule-classified by R6
    (fidelity-over-tidiness: the divergence is the register recording
    stale derived columns) and, for the five literal facts, R1.
27. **`used_in` regeneration and comparison** (2026-10-16, stage 5).
    Regeneration scans `data/areas/`, `data/front/*.md` and
    `data/maintenance.md` for F-IDs (§5.6). Only area IDs enter the
    regenerated `used_in` list; front-matter and maintenance sections are
    reported in the warning text ("also referenced in: …"), because §4.2
    defines `used_in` as the parsed "Used in" cell, whose ID kind is the
    area. The comparison is against the whole stored list, so the five
    record-ID cells fire (F-3, F-4, F-29, F-34, F-45 — R1 verbatim, R6
    warns). **18 facts differ in total**: those five, F-1 (A7 cites it
    too), and twelve whose cells name only "Reference stack"/"Threat
    evidence" while areas also list them in Facts and sources (F-5, F-8,
    F-9, F-11, F-12, F-20, F-22, F-23, F-24, F-25, F-27, F-28). Not an
    import error: the stored values are the export's cells verbatim (R1);
    §5.6 makes the regenerated value the forward truth and the mismatch a
    reportable signal (R6). The comparison is order-sensitive (regenerated
    values are sorted); no stored list is unsorted. Text mentions and
    `facts:`-list membership give identical regenerated sets (checked both
    ways), so the count does not depend on that choice.
28. **"Cited by" regeneration granularity** (2026-10-16, stage 5). §5.7
    fixes the inputs (area `sources`, claims `sources`, fact `sources`)
    but not the output form. Regeneration reports each citation at the
    finest granularity available: the citing record when one exists,
    otherwise the area whose `sources` list the reference. Stored cells
    are parsed into citation tokens with same-prefix "X to Y" ranges
    expanded (three cells use ranges: R-4, R-6, R-22); prose ("ASVS
    column, all areas", "Principles", "Superseded by R-2") is not a
    citation token; a bare area token counts only when it is a real area
    ID and not part of a longer ID. **107 of 144 references differ**: the
    export's Appendix B column compresses citations to area tokens
    (R-31 "A1" for T-A1-6; C-A1-6), omits citing records (R-115, R-118,
    R-121, R-129, R-134), and names records that no longer cite them
    (R-126, R-140, R-143). Kept verbatim (R1); reported, not fixed (R6).
29. **Retirement with an empty `replaced_by` is not an error**
    (2026-10-16, stage 5). §6 rule 6 constrains `replaced_by` one way
    ("non-empty only on retired records") and §4.1 says "empty if none",
    so `status: retired` with `replaced_by: []` passes. The stage-5
    brief's red-first seed list includes that case; it is recorded here as
    deliberately not firing. Both clauses that §6 does state fire and are
    proved in the red matrix (a live record carrying `replaced_by`; a
    `replaced_by` citing an unknown ID).
30. **Rule 8 keywords are literal, case-sensitive substrings**
    (2026-10-16, stage 5). §6 rule 8 names "requires", "MUST",
    "mandatory"; matched as case-sensitive substrings of the claim text
    ("MUST" in the RFC 2119 sense; no claim contains "must" or "MUST", so
    nothing turns on that today). Consequence of the literal reading: two
    claims using "required" (C-A1-1, C-B2-4) do not fire, because §6 names
    "requires". On the imported data rule 8 flags one claim, F-53 (tier 4,
    "Verified — secondary"); rule 7 flags none. At the stage-10 tag this
    is the §11.10 release-mode failure class (rules 7–8 only).
31. **Rule 5 scan scope** (2026-10-16, stage 5). §6 says "referenced
    anywhere" without a scope. `check.py` scans everything under `data/`
    (areas, claims, facts, references, features, disputes, compliance,
    front matter, maintenance) plus `catalogues/*.yaml`. `register/` and
    `archive/` are excluded: they are imported register text and the
    frozen origin, not corpus cross-references. A one-off sweep at stage 5
    found no unknown F-/R-ID token anywhere else in the repository either.
32. **Schema judgments** (2026-10-16, stage 5; R2 where §4 fixes the
    form, R4 for format-only conversions):
    - `area.schema.json` requires every §4.1 field except
      `cross_references` (the spec marks it optional; 15 areas carry
      `null`); threats use `^T-` and controls `^C-` patterns (the union is
      §6 rule 2's `^[TC]-…`); a control of `type: conditional` must carry
      a `trigger` key (structural consequence of §4.1 — C-B4-3 and C-P4-4
      keep `text: null`, which stays valid); `residual_rating` is a free
      string, not an enum, because §4.1 fixes no closed set (the export
      uses "Strong if verified", "Partial", "Closable").
    - `references.schema.json`: `tier` integer 1–5 (1–4 occur; §7 speaks
      of tiers 4 and 5); `url` string-or-null (R-107); `snapshot` null or
      the object §4.3 describes (`path`/`commit`, `retrieved`, `sha256`,
      `licence`).
    - `claims.schema.json`: `tier` integer-or-null (§4.5 "—" → null);
      `tier_text` and `split_from` optional.
    - `facts.schema.json`: `used_in` accepts area IDs and T-/C- record IDs
      (the five literal cells, R1).
    - `catalogue.schema.json` fixes key names §5.1 describes but does not
      name (`area_title`, `claim_verification`, `evidence_tier`,
      `source_urls`, `control_type`); `additionalProperties` stay open in
      its record types so stage 6 can extend records but not drop these
      fields. It is validated as a draft 2020-12 schema and smoke-tested
      against a minimal satisfiable `catalogue.json`.
    - YAML dates (`last_reviewed`, `last_verified`) are normalised to ISO
      strings before validation (R4: format conversion, no content
      change); rule 1 reports file, path and message, sorted, so output is
      deterministic.
33. **No data fixes at stage 5** (2026-10-16). `check.py` reports 0 errors
    in normal mode against the committed `data/` and `register/` trees;
    nothing under them was modified at this stage, and no import error
    arose. The findings in 26–28 are divergences the warnings exist to
    report, not faults to repair.
34. **Two check.py bugs found by the stage-5 verifier's tagged fixture**
    (2026-10-16, fixed the same day). The repository has no previous tag,
    so the previous-tag code paths (rules 6 and 9) were first proved with
    stubbed git readers; the verifier re-proved them against a real tagged
    fixture and found both stubs had missed real faults:
    - **Rule 9 false-positived on every unchanged record once a tag
      exists.** `previous` was rebound to the dict with `last_changed`
      stripped before the unchanged branch compared
      `current_records[rid]["last_changed"] != previous["last_changed"]`,
      which is always None — 75 false positives on the untouched fixture
      (the 53 facts plus 22 features then loaded; the threat/control
      history was not loaded at all, see next). Restructured so the
      content comparison uses a `content()` helper on stripped copies
      while the `last_changed` comparison reads the original records.
    - **`paths_at()` never returned the area files.** `git ls-tree
      --name-only <tag> data/areas` without `-r` lists the directory's
      own tree entry (`data/areas/`), which the `.yaml` filter dropped —
      so no previous-tag threats or controls were ever loaded. Rule 6's
      disappeared-ID clause was therefore unenforced for T-/C-IDs and
      rule 9 skipped all 294 threat/control records. Fixed with
      `git ls-tree -r --name-only <tag> -- <dir>`.
    Also fixed while there: rule 9's dead load of `data/references.yaml`
    (§6.9 governs threats, controls, facts and features, not references),
    and rule 2's ID check now uses `fullmatch` rather than a `^…$`
    `re.match`, which would admit a trailing newline. Normal-mode output
    is byte-identical before and after (the fixed paths are dormant while
    no tag exists): 0 errors, warnings 18 + 107 + 166 + 50 + 144 + 36 + 22.
    Re-proved on a real tagged fixture (git init, commit, tag
    `v1.0.0-beta.1` in a /tmp copy): pre-fix 75 rule-9 false positives on
    the untouched tree and silence on a deleted T-/C-ID; post-fix zero
    rule-6/rule-9 errors on the untouched tree, rule 6 firing on deleted
    T-A3-1 and C-A3-1, rule 9 firing on a changed statement with stale
    `last_changed` and on an unchanged record with a bumped one.

## Splits and merges

1. **Appendix A merged** (2026-10-16). Two tables in the export (F-1–F-17 and
   F-20–F-28, then F-18, F-19 and F-29–F-53) merged into one list sorted
   numerically, F-1..F-53, no gaps (SETUP 12 item 1).
2. **Appendix B merged** (2026-10-16). Six tables (R-1–R-27, R-28–R-110,
   R-111–R-114, R-115–R-122, R-123–R-141, R-142–R-144) merged into one list
   sorted numerically, R-1..R-144, no gaps (SETUP 12 item 2).
3. **Residual-risk summary "P1–P4 Process" row collapse** (2026-10-16). The
   summary table has one row for all four process areas; its rating ("Strong
   if verified") and "What remains" text ("Practices that lapse; detection
   tuning") were applied to each of P1, P2, P3 and P4.
4. **Claims split: "T-B5-1, T-B5-2, T-B5-4"** (2026-10-16, stage 4) → three
   records (T-B5-1, T-B5-2, T-B5-4), identical fields, each carrying
   `split_from: "T-B5-1, T-B5-2, T-B5-4"` verbatim (SETUP 4.5, 12 item 4).
5. **Claims split: "C-B5-1 to C-B5-4, C-B5-6"** (2026-10-16, stage 4) → five
   records (C-B5-1 to C-B5-4, C-B5-6), identical fields, `split_from` verbatim.
6. **Claims split: "T-P1-1, T-P1-2"** (2026-10-16, stage 4) → two records,
   identical fields, `split_from` verbatim.
7. **Claims split: "C-P2-2 to C-P2-4"** (2026-10-16, stage 4) → three records
   (C-P2-2 to C-P2-4), identical fields, `split_from` verbatim.
8. **Claims split: "T-P3-1 to T-P3-5"** (2026-10-16, stage 4) → five records
   (T-P3-1 to T-P3-5), identical fields, `split_from` verbatim.
9. **Claims split: "C-P3-1 to C-P3-4"** (2026-10-16, stage 4) → four records
   (C-P3-1 to C-P3-4), identical fields, `split_from` verbatim.
10. **Claims split: "C-P3-5, C-P3-6"** (2026-10-16, stage 4) → two records,
    identical fields, `split_from` verbatim.
11. **Claims split: "T-P4-2, T-P4-3"** (2026-10-16, stage 4) → two records,
    identical fields, `split_from` verbatim. Eight grouped cells in total
    (entries 4–11), expanding to 26 records; no other grouped cell exists in
    the export.

## Null fields

Stage-3 inventory (2026-10-16); all left null per section 1 rule 3, never drafted:

- Controls `requirement`: **166/166** null (every control, all 23 areas).
- Controls `verify`: **166/166** null.
- Features `question`: **22/22** null; `guidance`: **22/22** null.
- Conditional controls: **50** of 166 controls are `conditional`;
  `trigger.rule` null on **50/50**. `trigger.text` null on **2**
  (C-B4-3, C-P4-4 — no trigger stated in the export; see judgment call 1).
- References `snapshot`: **144/144** null (filled by `snapshot.py`, stage 7+).
- `R-107` `url`: null (no URL in the export; judgment call 6).
- Areas `cross_references`: null on the 15 areas with no cross-reference
  paragraph after the threats table (present on A1, A3, A4, A5, A7, A10,
  A11, B6).
- Areas `notes: []` on the 18 areas without note paragraphs (present on A1,
  A8, A9, A10, A13).

## Feature vocabulary to approve

Every distinct conditional-control `trigger.text` in the corpus (41 values,
stage 3, 2026-10-16). The owner must map these to features.yaml vocabulary
before `trigger.rule` expressions can be written (SETUP 4.4; none written at
import):

1. passkeys deployed
2. OAuth or OIDC
3. SAML
4. delegated transactions such as payments
5. self-contained tokens
6. high-value APIs
7. multi-tenant
8. contextual, sharing or multi-tenant rules
9. search, filter or sort features
10. XML parsing
11. uploads
12. rich text
13. cross-origin API
14. `postMessage`
15. ASVS L3 or sensitive resources
16. ASVS L3 or third-party hosted assets
17. outbound fetches
18. intermediaries
19. cache or CDN
20. GraphQL
21. WebSockets
22. stored passwords
23. high-sensitivity data
24. sensitive flows
25. high-value transactions
26. publishes packages
27. third-party scripts; mandatory on payment pages under PCI DSS v4.0.1 6.4.3 and 11.6.1
28. agents with tools
29. retrieval or agent memory
30. third-party models or tools
31. code execution
32. AI coding assistants
33. personal data
34. personal data under regulation
35. WAF in place
36. containers
37. Kubernetes
38. untrusted workloads
39. serverless
40. CDN or WAF
41. availability obligations

Plus two conditional controls with no trigger text in the export (C-B4-3,
C-P4-4) needing vocabulary when the owner adds one.
