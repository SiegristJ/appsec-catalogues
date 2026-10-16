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
35. **Area-file slug rule and the 23 names** (2026-10-16, stage 6). The stage-6
   brief fixes "lowercase, spaces→hyphens, drop punctuation"; implemented as:
   lowercase, remove every character that is not a letter, digit or
   whitespace, then collapse whitespace runs to single hyphens — so hyphens
   survive only where a space stood ("CI/CD" → `cicd`, "AI-generated" →
   `aigenerated`). The 23 file names: `A01-authentication.md`,
   `A02-sessions-and-tokens.md`, `A03-authorisation.md`,
   `A04-input-handling-and-injection.md`, `A05-client-side-attacks.md`,
   `A06-browser-security-headers.md`, `A07-http-infrastructure.md`,
   `A08-apis.md`, `A09-cryptography-and-data-protection.md`,
   `A10-business-logic-and-automated-threats.md`, `A11-software-supply-chain.md`,
   `A12-aillm-features-and-aigenerated-code.md`,
   `A13-error-handling-security-logging-and-privacy.md`,
   `B01-hardening-misconfiguration-and-patch-management.md`, `B02-cloud.md`,
   `B03-containers-kubernetes-and-serverless.md`, `B04-network-and-edge.md`,
   `B05-data-stores-backups-and-resilience.md`,
   `B06-privileged-and-administrative-access.md`,
   `P01-secure-sdlc-and-threat-modelling.md`,
   `P02-security-testing-and-verification.md`,
   `P03-cicd-and-infrastructure-as-code.md`,
   `P04-detection-monitoring-and-incident-response.md`.
36. **Determinism reading of section 5** (2026-10-16, stage 6). "Same input,
   byte-identical output" is read as: identical corpus inputs **and**
   identical stamp inputs — the same UTC build date and the same commit. The
   stamp is the only non-content input to the output; `content_sha256` in
   `catalogue.json` is computed over the catalogue content without `meta`,
   so it is stable across days while the file bytes follow the stamp.
   Verified by hashing all 37 generated files across two consecutive runs:
   byte-identical.
37. **`last_changed` presentation — ID-cell suffix** (2026-10-16, stage 6;
   SETUP 8). Chosen over an extra column so the tables keep the export's
   column count and cell alignment: the ID cell of every Threats and
   Controls row (per-area files and `catalogue-full.md` alike) reads
   `T-A3-1 · 1.0.0-beta.1`. Stage 7 excludes it from round-trip comparison
   by stripping the ` · <version>` suffix from the first cell.
   `catalogue.json` and every `catalogue.jsonl` record carry `last_changed`
   as a field.
38. **Threat Reference-cell separator reconstructed** (2026-10-16, stage 6;
   R1 verbatim data, R4 format-only join). The stored reference list is
   joined "; " between reference families (distinct leading letter runs:
   CWE, OAT, API, A, LLM, ASI, CICD-SEC) and ", " within one — this
   reproduces the export on 24 of the 25 multi-reference cells. The single
   exception is T-A1-6 ("CWE-601; CWE-346", same family joined with "; "),
   the one cell no deterministic rule can reproduce; listed here for the
   stage-7 separator normalisation.
39. **ID ranges render expanded** (2026-10-16, stage 6; consequence of the
   stage-3 expansion). "Facts and sources" lines, Addresses cells and the
   derived tables enumerate the stored lists; the export compressed some
   runs ("R-4 to R-9", "C-A2-1 to C-A2-4") but left others uncompressed
   ("F-1, F-2, F-3, F-4"), so no deterministic rule reproduces its choices.
   Note for stage 7: `check.py`'s `expand_id_ranges` covers T-/C-/F- ranges
   but not R- ranges ("R-29 to R-36"); the round trip needs R-range
   expansion as well.
40. **Derived-section framing text lives in the templates**
   (2026-10-16, stage 6). The intro paragraphs of the Applicability index,
   Compliance mapping, Where experts differ, Baseline and conditional
   controls, Residual-risk summary and Appendices A/B are in no data file;
   they are reproduced verbatim from the export in `tools/templates/`. The
   applicability intro's leading count is derived
   (`len(universal_areas)` → "Nine"). The export's "Last reviewed · Watch"
   lines under Compliance mapping and Where experts differ exist in no data
   file and are omitted (the front-matter sections carry theirs inside the
   copied text), as is the full edition's byline
   ("Oct 12, 2026 · @John Siegrist").
41. **Derived tables use stored titles and verbatim triggers**
   (2026-10-16, stage 6). The export's summary rows carry short area labels
   ("A12 AI/LLM features", "B1 Hardening and patching", "A13 Errors,
   logging and privacy") that exist nowhere in the data; the generated
   tables use the stored full titles. Also not derivable from the data
   model, so not reproduced: the B2/B6 "— (whole area conditional on …)"
   notes; the export's grouped or shortened trigger parentheticals
   ("C-A2-5 to C-A2-7 (self-contained tokens)", C-A6-5 and C-A6-7 under one
   "(ASVS L3, …)", "delegated transactions", "search, filter or sort",
   "postMessage"); C-A11-6's dual L2/L3 listing with "(L2)"; the P1–P4
   row's "All controls except C-P4-4" phrasing; and the "(code fixes lag)"
   / "(mandatory for cardholder data)" parentheticals for C-P4-4 and
   C-B4-3, whose `trigger.text` is null (judgment call 1). The generator
   emits one entry per control with `trigger.text` verbatim, enumerates the
   P1–P4 baseline instead of "All controls except", and merges the process
   areas into a single "P1–P4 Process" row (asserting the four share rating
   and summary, per split 3). Every ID stays present; the differences are
   presentation-only and listed for stage 7.
42. **Appendix A "Used in" and Appendix B "Cited by" render from the
   regenerated values** (2026-10-16, stage 6; §5.6–5.7, R6). Used in:
   regenerated areas then non-area section labels ("Reference stack",
   "Threat evidence"), ", "-joined, "—" when empty — the front-matter
   labels appear because §5.6's scan covers them. Cited by: the
   regenerated citation set ", "-joined in plain sorted order (the export
   grouped F-ids first and used "; " between groups), "—" when empty. The
   18/107 mismatches print during generation from the same `check.py`
   functions as warning 1 and never fail the run. In `catalogue.json`,
   fact records carry the regenerated `used_in` (areas only) and
   `used_in_text` is not emitted; reference records additionally carry
   `opened` and the regenerated `cited_by`.
43. **Stamp placement per format** (2026-10-16, stage 6). Markdown and text
   outputs start with the stamp line. `catalogue.json` carries
   version/commit/built in `meta` (JSON admits no text prefix, and the
   schema's `meta` forbids extra keys). Every `catalogue.jsonl` record
   carries `catalogue_version`/`built`/`commit` keys — a text prefix would
   break the one-object-per-line format. `schema.json` carries the stamp as
   a leading `$comment` key (valid JSON Schema, no validation effect; a
   JSON file cannot start with the stamp line and remain parseable).
   `features.yaml` carries a leading `#` comment above a byte-identical
   copy of `data/features.yaml`.
44. **AGENTS.md composition, usage_contract, llms.txt** (2026-10-16,
   stage 6). §5.5 supplies the seven bullets and no framing text beyond
   "The usage contract. Write it as follows:", so `AGENTS.md` is the stamp,
   an H1 "Usage contract" (the section's own name), and the seven bullets
   verbatim. `catalogue.json`'s `usage_contract` is the AGENTS.md body
   without the stamp line (the stamp values already live in `meta`;
   embedding the dated stamp would make the contract text
   build-dependent). The `llms.txt` description paragraph is new
   connective text describing the outputs (the brief calls for one
   paragraph); no catalogue content is reworded to write it.
45. **Full-edition assembly mechanics** (2026-10-16, stage 6). Section order
   is §5.8's, fixed in `tools/templates/catalogue-full.md.j2` and verified
   programmatically. Front-matter sections and Appendix C embed with their
   stored H1 replaced by the section H2 ("How to use this catalogue" …
   "Appendix C: Maintenance procedure"), the seam blank lines normalised to
   one (stage-3 note 4 stored H1 plus two blank lines). Per-area files,
   summaries and appendices use H1 when standalone and H2 when embedded
   (one template per section kind, heading level as a parameter). The
   merged process row keeps the export's en dash ("P1–P4 Process").
46. **Appendix B link rendering** (2026-10-16, stage 6; R4). A Reference
   cell renders `[title](url)` when the stored title carries no markdown;
   the two-link titles (R-19, R-125, judgment call 7) render verbatim; R-107
   (no url) renders as plain text. Six cells whose export form placed a
   trailing qualifier outside the link ("[…](url) (Pang et al.)" — R-4,
   R-9, R-11, R-21, R-49, R-63) render with the qualifier inside the link
   text, because the qualifier is part of the stored title (judgment call
   7); no text is lost, only the link's extent — a link-syntax class for
   stage-7 normalisation.
47. **Stage-7 round trip: class (iv) = 0, no data fixes** (2026-10-16).
   `tools/roundtrip.py` compares the regenerated `build/md/catalogue-full.md`
   against `../catalogue.md`, the claims tables reconstructed from
   `data/claims/` against `../register-claims.md` (347 records re-compressed
   to the export's 329 rows via `split_from`; 24 sections, zero differences),
   and `register/change-log.md` against `../register-change-log.md` with the
   §4.8 merge reversed. Exit 0; every difference is classified and the full
   enumeration lives in `build/roundtrip-report.md` (regenerated by the tool;
   git-ignored). Counts: catalogue class (i) 2 / (ii) 125 / (iii) 62 / (iv) 0;
   claims 0/0/0/0; change log 1/0/0/0.
   - Class (i) 3: the Appendix A merge (F-18 and F-19 moved from after F-28
     into numeric order), the Appendix B merge (six tables, already ascending,
     no reorder) and the change-log addendum merge.
   - Class (ii) 125 = the 18 used_in facts plus the 107 cited-by references;
     both sets reconcile exactly with check.py warning 1 (same sets, proved
     by assertion inside the tool).
   - Class (iii) 62, by sub-class: summary-table short area labels 12 (A12,
     A13, B1, B3, B5, B6 across both summary tables); grouped ID ranges and
     shortened trigger parentheticals 10 (A1, A2, A4, A5, A6, A7, A12, A13,
     B3, B4 conditional columns); cited-by cell rendering on token-equal rows
     15 (order, grouping, or export prose such as "Principles", "Superseded
     by R-2"); used-in cell rendering on token-equal rows 8 (F-2, F-6, F-31,
     F-32, F-40, F-42, F-52, F-53 — "lead", "ASVS column", "Where experts
     differ", "Compliance mapping" qualifiers); Appendix B link-text
     qualifiers 6 (R-4, R-9, R-11, R-21, R-49, R-63, judgment call 46);
     C-A11-6 dual L2/L3 listing 2; whole-area-conditional notes 2 (B2, B6);
     "All controls except C-P4-4" phrasing 2; "Last reviewed · Watch" lines
     under Compliance mapping and Where experts differ 2; the F-26 used-in
     label half 1; the edition byline 1; the T-A1-6 separator 1. The
     residual-risk summary's collapsed "P1–P4 Process" row reproduces exactly
     and raises no difference.
   - Judgment calls inside the tool: (a) a Used-in cell lands in class (ii)
     only when the area tokens differ or the export cell carries record IDs —
     mirroring check.py warning 1a, which compares the stored list against
     the regenerated AREA set — so F-26 (whose "Reference stack" label enters
     the regenerated cell only because the §5.6 scan matches the "F-20 to
     F-26" range endpoint literally in the reference-stack table) stays a
     class (iii) scan-scope difference and the class (ii) set remains exactly
     the 18; (b) the reference-cell separator normalisation fixes spacing
     only and compares separator kinds, so T-A1-6's same-family "; " (note
     38) surfaces as a class (iii) difference instead of being normalised
     away; (c) token-equal derived-column renderings are recorded as class
     (iii) rather than silently normalised. Normalisation symmetry is proved
     by `roundtrip.py --selftest` (compressed export forms and generated
     enumerations yield equal tokens); the red-first proof seeded three
     faults in a /tmp copy (altered C-A3-1 statement, dropped T-A3-1 claims
     row, altered change-log row) and the tool exited 1 with exactly three
     class (iv) records naming each location.

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

## Notes for future round-trip runs

48. **Two export editorial asides do not render in the generated catalogue**
    (2026-10-16, stage 7 verification). R-11's aside ("The OWASP project
    page still lists 4.0.3 as latest stable and is out of date") and R-3's
    "Superseded by R-2; retained for the record" are the only export prose
    absent from the generated document; both survive verbatim in
    `data/references.yaml` `cited_by_text`. Consequence of §5.7's
    regeneration mandate on the derived column; owner informed via the
    stage digest.
49. **Classification rules broader than their labels** (2026-10-16, stage 7
    verification). In `tools/roundtrip.py`, any threat-table Reference-column
    difference is classed (iii) "separator", and any equal-URL/equal-text
    link-pairing difference is classed (iii) "qualifier". A future
    reference-*content* change arriving through those columns would
    therefore be labelled (iii) though it is class (iv) by intent. No such
    difference exists in this import (verified across all rows); future
    runs that fire these sub-classes must hand-review them before accepting
    class (iv) = 0.

## Build and extract (stage 8)

50. **Anchor strategy — one `span#ID` per defining row, via a Pandoc Lua
    filter** (2026-10-16, stage 8; R4, a format-only conversion adding no
    content). §8 requires "every ID an anchor (`id="C-A3-1"`)". The filter
    (embedded in `tools/build.py`, written to `build/pandoc/anchors.lua` at
    run time because the stage's file set is fixed) keys on a table's first
    *header* cell — `ID` (the 23 Threats and 23 Controls tables), `F-ID`
    (Appendix A), `R-ID` (Appendix B) — and wraps the leading ID token of
    each data row's first cell in a span carrying that ID as its id. Only
    the defining occurrence is anchored; every other occurrence (Addresses
    cells, the Baseline-and-conditional summary, Compliance mapping, prose)
    stays plain text, so ids are unique and the audit is exact: 294 T/C
    anchors (128 + 166), 53 F and 144 R anchors in the appendices. Evidence
    pack sections anchor via pandoc header attributes (`{#T-A3-1}`).
51. **PDF/DOCX determinism — SOURCE_DATE_EPOCH derived from the stamp
    date** (2026-10-16, stage 8; extends entry 36's determinism reading).
    Bare Pandoc/Typst output is not byte-deterministic: DOCX embeds the
    wall clock in `docProps/core.xml` (created/modified) and the zip entry
    times; the Typst PDF embeds it in `/CreationDate` and `/ModDate`. Both
    Pandoc and Typst honour `SOURCE_DATE_EPOCH`, which `build.py` derives
    from the stamp's build date (UTC midnight of that date) — a value that
    already enters every output as the stamp, so no new non-content input.
    Reading: with SDE set, all five build outputs are pure functions of the
    corpus and the stamp inputs (version, UTC date, commit). Proved at
    stage 8: two full builds byte-identical across all five outputs,
    including PDF and DOCX (no residual content-streams-only caveat).
    Extracts are unaffected (standalone HTML carries no timestamp).
52. **`--since` version comparison — semver precedence, strictly greater**
    (2026-10-16, stage 8; §8 says "semantic-ish … document the rule").
    `build.version_key`: optional leading `v`/`V` accepted; numeric
    components compared element-wise, a shorter tuple zero-padded
    (1.0 < 1.0.0); a pre-release sorts below its own release
    (1.0.0-alpha.1 < 1.0.0); pre-release identifiers compared per semver
    §11 — numeric identifiers numerically and below alphanumeric ones,
    otherwise ASCII-lexically, a longer identifier list above its own
    prefix; build metadata (`+…`) ignored. "Later than" is strict `>`, so
    `--since 1.0.0-beta.1` lists nothing at the current corpus (every
    record is exactly 1.0.0-beta.1) and `--since 1.0.0-alpha.1` lists
    everything in the extract.
53. **Pandoc reader runs with the citations extension disabled**
    (2026-10-16, stage 8; R1 + R4). F-37's value and claim carry the npm
    scope "@tanstack" verbatim from the export; §2 says export @-names are
    plain text, but pandoc's default `citations` extension parses `@token`
    as a citation, and the typst writer then emits `#cite(<tanstack>)`,
    which fails to compile (no bibliography). `-f markdown-citations`
    restores the literal reading; identical reader setting for HTML, PDF,
    DOCX and extract renders, so no writer sees different tokens. No other
    extension is modified.
54. **Change-log "mentions" rule — whole-row token scan with range
    expansion, including the mixed family range** (2026-10-16, stage 8; R5
    in spirit — mechanical expansion, nothing re-typed — but the mixed
    range needs a reading the export does not state; flagged for the
    owner). A `register/change-log.md` row mentions an ID when the ID
    appears as a token anywhere in the row (all six cells joined) after
    expanding same-prefix "X to Y" ranges (check.py's helper) and the one
    mixed-prefix range the export carries, "T-B2-1 to C-B2-6": same area,
    different family. B2 has 5 threats and 6 controls, so "threats 1–6" is
    impossible; the range is read as that area's existing threats
    numbered ≥ 1 plus controls numbered ≤ 6, i.e. all 11 B2 records —
    consistent with the row's own text ("Grouped register rows in B2 …
    split to one row per ID"). Result: 91 of 347 IDs have change-log hits
    (27 threats, 35 controls, 29 facts); the other 256 carry an explicit
    "No change-log row mentions <ID>." line. Rows naming only areas or
    sections (e.g. "A1, A2, A4 to A13 …", "A3 residual risk") are not
    per-ID mentions.
55. **Evidence pack structure decisions** (2026-10-16, stage 8; content
    fixed by §8, grouping and framing are presentation, R4). One H3
    section per T/C/F ID (347), grouped Threats (128) / Controls (166) /
    Facts (53) in corpus order; the heading carries the ID as a pandoc
    header-attribute anchor. Each section: a meta line (kind, place, status,
    last changed), the record text, the claim record table (claim, sources,
    tier + tier_text, verification, last verified, verified by, origin,
    decision, status, split_from when present), a references table for the
    claim's sources (ID, title, tier, URL — R-107 prints "— (no URL)" —
    snapshot status "not captured" while snapshot is null), and the
    verbatim six-cell change-log rows (R1). A summary table at the top
    counts sections and change-log hits. `.html` renders standalone; no
    TOC (§8 asks for a TOC on the catalogue HTML only; 347 TOC entries
    would dwarf the page).
56. **extract.py version check is exact-string; the example checklist pins
    "untagged"** (2026-10-16, stage 8; R2 — §8 "does not match the build"
    read literally, no v-stripping leniency). The build's version stamp
    (`build/ai/catalogue.json` `meta.version`) is "untagged" until the
    stage-10 tag, so `reviews/example-checklist.yaml` pins
    `catalogue_version: untagged`, not §8's illustrative `v1.0.0-beta.1`.
    Follow-up for the owner/controller: after tagging, the example
    checklist's value must become `v1.0.0-beta.1` (a one-line change;
    until then extracts from it error by design).
57. **Process areas excluded from extracts** (2026-10-16, stage 8; R2 —
    §8's extract list names only universal and feature-pulled areas; but
    flagged for the owner as a possible intent gap). §4.4 parks P1–P4 in
    `process_areas` outside the applicability index, whose own framing
    says they "always apply to the delivery organisation and are not
    selected here". The literal §8 list excludes them, so extracts do not
    include P-area threats/controls; the extract states this in one line
    under the pulled-areas table. If the owner wants process controls in
    every extract, that is a spec change (and would change gate counts:
    the example extract would go from 18 to 22 areas).
58. **extract.py errors on unknown checklist keys and shares helpers with
    build.py** (2026-10-16, stage 8; the stage-8 brief fixes the file set
    — `tools/build.py`, `tools/extract.py`,
    `reviews/example-checklist.yaml`, `IMPORT-NOTES.md` — so no third
    module ships). extract.py imports its pandoc/stamp/changelog/version
    helpers from build.py (main-guarded; importing it never builds) and
    adds a typo guard beyond §8's two named errors: a checklist key that
    is not a feature in features.yaml is a non-zero-exit error naming it,
    because a misspelled feature would otherwise silently exclude its
    areas. Red matrix proves all three error paths: undeclared feature
    (names graphql), unknown key (names graph_ql), version mismatch
    (names both values).

## Snapshot tool, published site and repository mechanics (stage 9)

59. **Site allowlist — contents, and one definition reused by the checker**
    (2026-10-16, stage 9; §10.1 "assembles `build/site/` from an explicit
    allowlist" and "Add a `check.py` release-mode error if ..."). The
    allowlist is defined once, as `site_allowlist()` in `tools/build.py`,
    and is used in three places that therefore cannot drift: `build_site()`
    assembles exactly those files and raises if the built tree differs;
    `check.py` rule 11 imports the same function and re-proves the built
    tree; and the build prints the audit line. The 20 files (plus whatever
    `build/ai/` holds, currently 6): root `index.html`, `llms.txt`,
    `robots.txt`, `404.html`, `_headers`; `web/index.html`,
    `web/catalogue.html`, `web/evidence-pack.html`, `web/history.html`,
    `web/llms.txt`, `web/AGENTS.md`, `web/downloads/catalogue.pdf`,
    `web/downloads/catalogue.docx`, `web/downloads/evidence-pack.md`, and
    `web/ai/<every file in build/ai/>`. `build_site()` deletes and rebuilds
    `build/site/` each run, so a file dropped from the allowlist cannot
    survive a rebuild. Judgment call: §10.1 names `web/llms.txt` and
    `web/AGENTS.md` as separate bullets *and* says `ai/` holds everything
    in `build/ai/` (which contains both files), so both locations are
    populated — the two root-level copies are deliberate duplicates of
    `web/ai/llms.txt` and `web/ai/AGENTS.md`. Root templates live in
    `site/root/` (five templates, one per root file, as §10.1 requires);
    the catalogue's own index template lives in `site/web/index.html.j2`,
    a second directory rather than `tools/templates/`, so catalogue and
    landing templates stay separate as §10.1 intends.
60. **check.py rule 11 — the site allowlist rule (classified:
    spec-mandated, §10.1; the one authorised change to an earlier-stage
    tool)** (2026-10-16, stage 9). Adds rule 11: any path under `archive/`
    anywhere in `build/site/` (file or directory), and any file not
    produced by the allowlist, is an **error in release mode** and a
    **warning in normal mode**; the rule is skipped with a NOTE when the
    site has not been built, because CI runs `check.py` before
    `build.py`. The allowlist is imported lazily from `tools/build.py`
    inside the rule (never at module import, so `build.py`'s own
    `import check` cannot recurse), and `site_allowlist(root, ai_names)`
    takes the root so the rule works under `--root` against a copied tree.
    `data/` leaks are caught by the allowlist clause (any file not produced
    by it), which is how §10.1 words it. Red-first proof in a `/tmp` copy:
    planted `build/site/archive/leak.html` → release ERROR (file and
    directory both named) / normal WARNING (2 warnings, exit 0); planted
    unlisted `build/site/stray-notes.txt` → release ERROR / normal
    WARNING; planted `build/site/web/data/x.json` → release ERROR via the
    allowlist clause; clean tree → 0 errors / 543 warnings, no rule-11
    output. Diff: 61 insertions, 1 deletion (the deletion is the docstring
    usage line "adds rules 7, 8 and 9" → "7, 8, 9 and 11").
61. **snapshot.py design decisions, rule-cited** (2026-10-16, stage 9;
    §7). Written, never run against the network (ground rule 5); verified
    by code review plus an offline mocked dry-run in `/tmp` (fetch and the
    clock replaced; `urllib.request.urlopen` armed to raise, so a bypass
    of the chokepoint would fail loudly). Decisions:
    (a) *Mode order* — github, then PCI SSC, then the SP 800-53 mirror
    TODO, then tier 4, then download; the GitHub rule has no licence
    exception because recording a commit copies nothing (§7 bullet 2 gives
    none).
    (b) *GitHub hosts matched exactly* (`github.com`, `www.github.com`,
    `raw.githubusercontent.com`), not by suffix, so look-alike domains are
    never treated as GitHub; `github.blog` and `docs.github.com`
    (R-33, R-109) are therefore ordinary downloads.
    (c) *A github.com URL that names no file* (R-72's security-advisory
    page) records the repository's default-branch HEAD commit via
    `/repos/{o}/{r}` + `/commits/{branch}`, and `meta.yaml` says so in
    `commit_scope`; §7 says "the current commit hash of the file", and a
    page has no file path.
    (d) *SP 800-53 detection is host-scoped to csf.tools* (§7: "currently
    cited through csf.tools"). The first draft also matched titles
    containing "SP 800-53", which wrongly parked R-16 — a direct
    `csrc.nist.gov` release-summary PDF — behind the OSCAL TODO; R-16 is
    an ordinary NIST download. The TODO text (archive from
    `usnistgov/oscal-content`, recorded by commit) is written to
    `meta.yaml`, to the `references.yaml` snapshot licence, and printed.
    (e) *Tier 4* is keyed on the reference's `tier` field (§7: "vendor
    blogs and news sites (tier 4)"); `--include-copyrighted` overrides it
    and is documented in the help and docstring as private-repository-only
    (§7's own words), with a printed reminder when used.
    (f) *Licences* — §7 requires a licence field the tool cannot read from
    pages it is told not to download. Pointer modes carry the rule's own
    note as the licence; `--licence R-<n>=<text>` records an owner-given
    licence; otherwise `licence: null` plus a TODO in `meta.yaml`. Nothing
    is invented.
    (g) *meta.yaml* always carries url, retrieved UTC, sha256-or-commit,
    content type and licence (§7 bullet 4), plus id, title, mode, rule and
    any TODO so the archive explains itself.
    (h) *references.yaml update is surgical*: the record's `snapshot` key
    is replaced in place (regex on the record block), the edited file is
    parsed back and every record compared before it is written, so the
    file's formatting and the other 143 records stay byte-identical —
    proved by the `--all` mock run (schema-valid, and identical outside
    the `snapshot` keys). The written value matches
    `schema/references.schema.json` (`{commit, retrieved, licence?}` for
    github, `{path, sha256, retrieved, licence?}` for downloads,
    `{retrieved, licence}` for pointers).
    (i) *R-107* (no URL, §12.2) fails loudly and counts as a failure, so
    `--all` exits 1 with 143 of 144 processed.
62. **README completion — judgment calls** (2026-10-16, stage 9; §10).
    The Deployment section carries the six §10.1 owner-setup bullets
    verbatim (checked word for word against the spec), preceded by three
    sentences of deployment framing (release model, the three workflows,
    nothing from `archive/` or `data/` published) and followed by a pointer
    to the runbook's token-expiry task. The system-dependency versions are
    the ones actually used: Python 3.14.6, Pandoc 3.12, Typst 0.15.1 (a
    table, since §10 asks for the versions used and the CI pins the same
    two). The extract section notes that `catalogue_version` must exactly
    match the build stamp and that the stamp reads "untagged" until the
    repository is tagged (IMPORT-NOTES 56). Beyond §10's required links,
    Further reading also links `CHANGELOG.md` and `ROADMAP.md`, both of
    which stage 9 creates. The purpose, status, three-outputs, corpus and
    versioning text is unchanged from the committed skeleton (compared
    word for word after whitespace normalisation).
63. **ROADMAP.md — byte-exact, zero normalisation** (2026-10-16, stage 9;
    Appendix R). Extracted programmatically from between
    `<!-- ROADMAP START -->` and `<!-- ROADMAP END -->` in
    `../SETUP-INSTRUCTIONS.md`, dropping only the `~~~~markdown` fence
    lines; `diff` against the extracted text is empty, so no Markdown
    normalisation was applied at all (gate 6).
64. **CHANGELOG.md** (2026-10-16, stage 9; §10). Exactly one entry with
    the required heading string `v1.0.0-beta.1 — 2026-10-12 — initial
    import` (em dashes, as in the spec), a two-sentence summary of what
    the import contains, and the link to `register/change-log.md` for
    detail. No second heading, no per-record rows.
65. **Releases URL is a placeholder until an origin remote exists**
    (2026-10-16, stage 9; §10.1 web/index.html bullet). The catalogue
    index links the GitHub releases page; the repository has no origin
    remote during import and SETUP nowhere names the repository slug, so
    `releases_url()` derives it from `git remote get-url origin` when one
    exists and otherwise emits `https://github.com/OWNER/REPOSITORY/releases`,
    with a warning printed by the build. This is the one site input that
    is a function of the remote rather than the corpus; it is deterministic
    for a given clone (proved by the two-run determinism check). Owner
    action: set the origin remote before the first release. Related: §10.1's
    version stamp says untagged builds show `<last tag>+<short sha>`;
    generate.py (read-only at this stage) stamps "untagged" plus the short
    commit, and no tag exists yet, so nothing distinguishes the two forms.
    Flagged for the owner rather than changed: making generate.py emit
    `<last tag>+<sha>` is a stage-10-or-later decision.
66. **HISTORY.md rendered for the site with repository-relative links
    de-linked** (2026-10-16, stage 9; §10.1 web/index.html bullet
    "HISTORY.md (rendered)"). HISTORY.md links `data/`, `register/`,
    `archive/origin/...`, `archive/sources/`, `emerging/` and `runbook/` —
    repository paths, and `archive/` must never be published. Rendering
    for the site keeps the link labels as text and leaves absolute
    http(s) links live; there are no http(s) links in HISTORY.md, so the
    published `web/history.html` carries no href at all. The repository's
    own HISTORY.md is untouched.
67. **Version stamp on every published HTML page** (2026-10-16, stage 9;
    §10.1 "Version stamp"). The catalogue, evidence pack and history pages
    carry the stamp as the Pandoc subtitle (the same mechanism stage 8
    used); the two index pages and the 404 page render it in a footer
    from the template. The site audit checks all 20 files' HTML pages
    contain the stamp string (pandoc wraps the subtitle line, so the
    check normalises whitespace).
68. **Workflow judgment calls** (2026-10-16, stage 9; §10.1). The deploy
    job **rebuilds from the tag** rather than downloading the `release`
    job's artifact — §10.1 allows either ("Rebuild, or download the site
    artifact from release"); rebuilding keeps "what is live is always a
    tag" true without artifact plumbing, and the same workflow already
    release-checked that tree. The AI zip is named
    `catalogue-ai-<tag>.zip`. `CLOUDFLARE_ACCOUNT_ID` is read with
    `vars.` (§10.1 owner setup calls it a *variable*; `CLOUDFLARE_API_TOKEN`
    with `secrets.`), and both appear only in the two deploy jobs (proved
    by grep with job-block attribution). The release job uses
    `secrets.GITHUB_TOKEN` to create the GitHub Release — not a Cloudflare
    secret, and `ci.yml` uses no secret at all (`permissions: contents:
    read`), so fork PRs work. Checkouts in `ci.yml` and the release job
    use `fetch-depth: 0` + `fetch-tags` so check.py rules 6 and 9 can see
    previous tags. Pandoc 3.12 and Typst 0.15.1 are pinned in workflow
    `env:` and installed from their upstream release artifacts.
69. **watch-list, emerging and runbook** (2026-10-16, stage 9; stage-9
    brief l–m). `runbook/watch-list.yaml` is generated from the 23 areas'
    `watch` lines (values verbatim, keyed by area ID, round-trip compared
    in the generator and re-proved by the gate script) and carries a
    header saying how to regenerate it, since it is a view over the corpus
    rather than a second source of truth. `emerging/emerging-threats.md`
    states both halves of its scope — fast-moving threat material *and*
    volatile or pre-standard reference sources — and leaves the
    evidentiary standard to the owner. `runbook/maintenance-runbook.md`
    names the Cloudflare API token expiry check as the first task with
    blank date fields for the owner, plus the stage-9 TODOs (run
    `tools/snapshot.py --all`, replace `@SPECIALIST_REVIEWER`, define the
    emerging evidentiary standard).
70. **robots.txt and _headers specifics** (2026-10-16, stage 9; §10.1).
    robots.txt allows `User-agent: *` and repeats `Allow: /` for the
    common AI crawlers by name, so "allow all, including AI crawlers" is
    explicit rather than implied; no sitemap is declared because none is
    built. `_headers` sets `Content-Type` for `*.jsonl`
    (`application/x-ndjson`) and for `llms.txt` at both levels where it
    exists, and `Cache-Control: public, max-age=300` for HTML at the root
    and `/web/` levels specifically — Cloudflare's `_headers` wildcard
    semantics across path levels are not relied on, so a second catalogue
    adds its own line (the file says so).
71. **Two version-stamp forms: §5 for the corpus editions, §10.1 for the
    published site pages** (2026-10-16, stage 9, follow-up; rule-classified
    — §10.1 "Version stamp": "Every HTML page ... shows the version (from
    the tag, or `<last tag>+<short sha>` for untagged builds), the commit
    and the build date"). `generate.py` is untouched, so §5's stamp still
    governs `build/md`, `build/ai` and the download files: the tag when
    `git describe --exact-match` finds one, otherwise "untagged". The site
    step computes `site_version()` in `build.py` and applies it to every
    published HTML page: the two renders copied from `build/out/`
    (`catalogue.html`, `evidence-pack.html`) are rewritten in place by a
    whitespace-tolerant replacement of the stamp's version token (pandoc
    hard-wraps the subtitle line; the rewrite raises if it matches
    nothing, so a stamp-wording change cannot silently leave a §5 version
    on a page), `history.html` is rendered with the §10.1 form directly,
    and the template pages (`web/index.html`, root `index.html`,
    `404.html`) receive it in their stamp footer — with
    `web/index.html`'s **status line** taking the same version in its
    "Status {version} — ..." slot, so the page never claims a newer
    version than it was built from. The AI edition and the downloads
    (`web/ai/*`, `web/AGENTS.md`, `evidence-pack.md`, PDF, DOCX) keep §5's
    form; the PDF and DOCX are out of scope for this follow-up (their
    first-page stamp is §5's, showing the commit), which is the one part
    of §10.1's stamp sentence not yet realised. *Ordering choice:* "last
    tag" is check.py's `previous_tag()` — the highest-version `v*` tag that
    is an ancestor of HEAD — i.e. git-describe's most-recent-reachable-tag
    semantics expressed in the version ordering the repository already
    uses for rules 6 and 9; version order rather than commit order is the
    tiebreak because in a tag-is-a-release model a lower version cannot be
    released after a higher one. Several tags on HEAD resolve to the
    highest. Red-first in three `/tmp` git fixtures, each a full
    `build.py` run asserted on all six HTML pages plus the status line:
    (a) no tags → **untagged** everywhere, §5 form identical; (b) tag
    `v0.1.0` at HEAD → **v0.1.0** everywhere; (c) tag `v0.1.0` plus one
    later commit → **v0.1.0+18065ef** on every HTML page and the status
    line, while `web/ai/llms.txt`, `web/AGENTS.md` and the downloaded
    evidence pack still say "untagged" (§5), and no §5 form remains on any
    HTML page. Gate re-runs after the change: site allowlist/link audit
    clean (now checked against the §10.1 stamp), two consecutive builds
    byte-identical, `check.py` normal 0 errors / 543 warnings,
    `generate.py` byte-identical to `HEAD`.

## Release-mode check and tag preparation (stage 10)

72. **Release-mode check passes §11.10; example checklist pinned to
    v1.0.0-beta.1; tag prepared for the controller** (2026-10-16, stage 10).
    `tools/check.py --release 1.0.0-beta.1` on the stage-10 working tree
    prints "catalogue check (release 1.0.0-beta.1): 1 errors, 543
    warnings", "NOTE: no previous tag, rule 6 (disappeared IDs) skipped",
    "NOTE: no previous tag, rule 9 skipped", the standing warning counts
    ("W1 (cited by)=107, W1 (used_in)=18, W2=166, W3=50, W4=144, W5=36,
    W6=22"), and exactly one error, verbatim:
    "ERROR [rule 8] data/claims/B04.yaml: F-53: normative-form claim
    (contains requires) has tier 4 and verification 'Verified — secondary',
    expected tier 1 and \"Verified — primary\"." F-53's claim reads
    "PCI DSS 6.4.2 requires an automated technical solution in front of
    public-facing web applications" — tier 4, verification
    "Verified — secondary". Rule 7 is clean (no verification starts
    "Unverified"; T-B6-4, the near-rule-7 shape, starts "Verified —
    primary"), and rules 6/9 print the no-previous-tag skip notices. This
    is the §11.10 allowed state — rules 7–8 failures only, each listed
    here, and the list is exactly one item (F-53) — so the tag may proceed.
    Housekeeping executed alongside (the IMPORT-NOTES 56 one-line change):
    `reviews/example-checklist.yaml` `catalogue_version:` flipped from
    "untagged" to "v1.0.0-beta.1", so a build from the tag and the
    checklist agree and `extract.py reviews/example-checklist.yaml`
    matches the tag stamp; the file's header comment documenting the
    import-era pin is untouched. Tag plan: the stage-10 executor neither
    commits nor tags; the controller commits the two stage-10 files
    ("Stage 10: release-mode check recorded, example checklist pinned to
    v1.0.0-beta.1"), re-runs `check.py --release` on the committed HEAD
    and, if the result still satisfies §11.10, creates the annotated tag
    `v1.0.0-beta.1` ("Web Application Security Reference Catalogue,
    initial import"). Nothing is pushed — pushing triggers release+deploy
    and is the owner's, after their §10.1 setup. Rules 6 and 9: their
    first real exercise is deferred to the second release; at this tag
    there is no previous tag to compare against, and both previous-tag
    code paths are fixture-proven only (IMPORT-NOTES 34, the stage-5
    tagged-fixture re-proof).

## Information-architecture pass (post-import)

73. **Orientation single source — `tools/orientation.py`** (2026-10-16, IA
    pass; ruling IA-1 — the deck is approved verbatim). All shared blocks
    (B1 full/short/one-liner, B2, B3 framing, B4) and the wrappers' copy
    live in one build-side module, consumed by generate.py (full-edition
    front section; AGENTS.md vocabulary; catalogue.json's usage_contract
    through agents_body), build.py (evidence-pack orientation, web-index
    context, the root doorway `site_line`), extract.py (preamble), check.py
    (rule 12, the README sync) and roundtrip.py (byte-verification of the
    front section). No orientation prose is duplicated in a template. The
    site URL has one build-side source: `orientation.SITE_URL`
    ("https://appsec.complects.com/", the deployment URL in the README and
    wrangler.jsonc), rendered by the front section's "Where everything
    lives" and enforced in the README by rule 12. Determinism: module
    constants plus parses of frozen files plus the stamp's version in the
    citation example — no new non-content input (entries 36/51 line). The
    web index's HTML forms (B2, the role intro, B4 with links applied — the
    deck's "links are applied by each template") are checked by an
    assertion that strips tags and compares against the canonical copy, so
    the two forms cannot drift.
74. **Governance parse — one parser, one consumer path, hard error on
    nothing found** (2026-10-16, IA pass; content freeze).
    `orientation.parse_governance()` extracts the tier table (after
    "**Evidence tiers**"), the verification-status table (after
    "**Verification statuses**") and the two numbered rules (after "Two
    rules follow:") from `register/governance.md`, captions included;
    `register/governance.md` itself is never edited. A missing marker, an
    empty table, or fewer than two rules is a SystemExit ("a parse that
    finds nothing is a hard build error"), never a silent skip. Every
    legend — evidence pack, full edition, AGENTS.md (and therefore the
    usage_contract) — renders from this one parse. At this corpus: 5 tier
    rows, 5 status rows, 2 rules, byte-verbatim including governance.md's
    curly quotes and ellipses.
75. **Reading-paths table rendered from data** (2026-10-16, IA pass; IA-1
    sub-decision 2, "render from data/front/00-how-to-use.md at build
    time"). `orientation.parse_reading_paths()` finds the table after
    "**Reading paths by role.**"; the web index renders its header and 7
    rows verbatim (frozen data, never restated). A missing marker or empty
    table is a SystemExit.
76. **Full-edition front section and its round-trip status** (2026-10-16,
    IA pass; deck W2). generate.py embeds
    `orientation.about_edition_section(version, gov)` as
    "## About this edition" between the title stamp and "How to use this
    catalogue" (`tools/templates/catalogue-full.md.j2`); HTML, PDF and DOCX
    inherit it through the existing renders. The section therefore enters
    `build/md/catalogue-full.md` by design, and `roundtrip.py` treats it as
    a **sanctioned insertion, byte-verified — never a blind skip**:
    `verify_orientation_insertion()` re-renders the expected section from
    the orientation module for the version in the generated stamp line and
    requires byte equality. A match is recorded as class (i) (catalogue
    class (i) is now 3); a mismatch or an absent section is class (iv) and
    the run exits 1. Red-first in /tmp copies with `--skip-generate`:
    corrupting one byte of the rendered section ("areas," → "areaz,") →
    exit 1 with one class (iv) "orientation section mismatch" naming the
    section; deleting the section → exit 1 with class (iv) "missing
    orientation section"; clean control → exit 0. The citation example
    renders the stamp's version ("C-A3-1, appsec-catalogues v1.0.0-beta.1"
    at this tag; "untagged" between tags).
77. **ID → evidence deep-links are HTML-only, applied to the site copy**
    (2026-10-16, IA pass; owner-ruled degradation). `build_site` wraps each
    of the 347 defining T/C/F `<span id>`s in `web/catalogue.html` with
    `<a href="evidence-pack.html#<ID>">` — plain relative links; the anchors
    already existed on both sides (entries 50, 55), so this is link
    rendering only. The rewrite runs on the site copy after the §10.1
    version rewrite; `build/out/catalogue.html`, the PDF/DOCX and
    `build/md/catalogue-full.md` stay link-free (the round trip compares
    the .md against the export; the .md gained no link markup, only the
    sanctioned section of entry 76). The rewrite raises unless it finds
    exactly the corpus's T/C/F total (128 + 166 + 53 = 347), so a change
    in the anchor rendering can never silently unlink IDs. A lone
    catalogue.html simply has non-resolving links.
78. **Evidence pack redesign** (2026-10-16, IA pass; deck W3; grouping and
    framing are presentation, R4 — the per-ID content is unchanged). New
    order: stamp; H1; the W3 orientation header (what this is; "How to
    check a claim" in three steps); the B3 legend from the governance
    parse; "## Contents" — a grouped table of contents by area (23 area
    rows plus Facts) with section counts and change-log hit counts, each
    row linked to its H2 anchor (`{#A1}` … `{#facts}`); the "Where the
    evidence is weakest" index with three linked lists; the kind summary
    table; then the body grouped **by area** (one H2 per area with
    threat/control counts, H3 per ID as before) and a Facts group. The old
    intro paragraph and the Threats/Controls/Facts H2 grouping are
    superseded. The 256 "No change-log row mentions <ID>." sentences
    collapsed to the marker "no change-log mentions" in each section's
    meta line. The build prints the weakest-index counts each run
    (deterministic text; entry 36 line).
79. **Counts recomputed, not trusted** (2026-10-16, IA pass; the counts
    are claims). Recomputed from the corpus and the build: the W5
    qualifier set **36** = 19 C- + 9 F- + 8 T-ID claims (check.py warning
    5's own set); disputed controls **5** (C-A1-2, C-A7-5, C-A9-6,
    C-B2-4, C-B4-3); IDs with change-log mentions **91** = 27 threats +
    35 controls + 29 facts (whole-row mention rule with range expansion,
    entry 54 — recomputed via `build.change_log_mentions`, identical
    split); no-change-log markers **256** = 347 − 91; total **347** =
    128 T + 166 C + 53 F. All five match the brief's expected values; none
    was silently absorbed.
80. **README sync — check.py rule 12, silent when in sync, red-first**
    (2026-10-16, IA pass; ruling IA-2 — "drift is a check error, not a
    silent divergence"). New error rule, both modes: README.md must
    contain, after whitespace collapse (the README wraps lines), the
    canonical B2 paragraph and the three-outputs lead-in from
    tools/orientation.py, and the SITE_URL. Silent when in sync — no
    output, no warning, the total stays 543; ERROR on drift. Red-first in
    a /tmp copy: one word changed in the README's beta paragraph →
    "1 errors, 543 warnings", exit 1, verbatim "ERROR [rule 12]
    README.md: beta-status paragraph (deck block B2) does not match the
    canonical orientation source (tools/orientation.py) — sync the README
    to it (rule 12, IA pass ruling IA-2)".
81. **README edits** (2026-10-16, IA pass; deck W7, ruling IA-2). Status
    de-staled: a "**Status: 1.0.0-beta.1.**" line plus the B2 paragraph
    verbatim (the README is hand-written, so the version is plain text
    maintained by hand; the B2 text is rule-12-enforced). "The three
    outputs" gains the one-line lead-in "Three ways to use it: pull a spec
    from it, read it end to end, or consume it as an agent." — assembled
    from B4's three titles, the deck's instruction being "B4's use-framing
    as a one-line lead-in". Deployment: the six owner-setup bullets and
    their lead-in were verified byte-verbatim against
    `owner-ops/deployment-owner-setup.md` (workspace; created by ruling
    IA-2 before this pass) and removed from the README, replaced by the
    approved sentence ("Deployment is owner-operated. The workflows above
    are the whole public contract; owner-side account setup is kept by the
    owner, outside this repository."); the runbook token-expiry pointer
    stays; Further reading gains the live-site URL bullet. Nothing else in
    the README changed.
82. **Site doorway and index decisions** (2026-10-16, IA pass; deck W5/
    W1). `SITE_LINE` (the `site_line` slot the brief names for the root
    index) is now `orientation.ONE_LINER`; the root llms.txt's blockquote
    renders the same slot and changes with it (single source). The
    superseded host-level line ("Version-controlled security reference
    catalogues, generated from structured data and published one per path;
    every page carries the version it was built from") is replaced while
    exactly one catalogue is hosted; the version claim it carried is
    realised by the stamp footer on every page (entry 67), and the line
    should be revisited when a second catalogue is hosted. web/index.html:
    the §10.1 status line is kept (it is the version-bearing slot, entry
    71) with B2 added under "What this is"; B4's items apply the existing
    artifact links inline (catalogue.html, PDF, DOCX, ai/*) as the means to
    each use; the artifact list below is kept unchanged (link text and
    targets unchanged) as the complete inventory; the role-table intro
    carries its own bold lead, so no duplicate H2 was added above it.
83. **Extract preamble; AGENTS.md vocabulary; catalogue.json**
    (2026-10-16, IA pass; deck W4/W6). extract.py inserts the preamble
    after the stamp and title, before the existing "Generated from …"
    sentence: B1 short form, then the two lines; the HTML output is
    pandoc's render of the .md, so both carry it. AGENTS.md is the stamp,
    "# Usage contract", the seven §5.5 bullets (unchanged), then
    "## Evidence vocabulary" (the W6 framing, the parsed legend, the
    carry-qualifiers paragraph); catalogue.json's `usage_contract` is
    agents_body minus the stamp (entry 44), so the vocabulary flows in
    automatically — the JSON was re-validated against
    `schema/catalogue.schema.json` after the change (Draft 2020-12 with
    the format checker; valid).
84. **Gates after the IA pass** (2026-10-16). `check.py` 0 errors / 543
    warnings (rule 12 silent); `roundtrip.py --exports
    ../import-2026-10/inputs` exit 0 with class (iv) empty — catalogue
    (i) 3 / (ii) 125 / (iii) 62, claims 0/0/0/0, change log 1/0/0/0; two
    consecutive full builds byte-identical across build/md, build/ai,
    build/out and build/site; site allowlist audit clean at 20 files, site
    version v1.0.0-beta.1 on every page (the tag is local-only; the known
    CI/local stamp mismatch is entry-level expected and not touched);
    `extract.py reviews/example-checklist.yaml` runs clean with the
    preamble in both outputs. OD-7 (process areas in extracts) untouched —
    only the preamble was added; no known open item from WORK-INSTRUCTIONS
    §0 was fixed.
85. **Role table hyperlinked on the web index** (2026-10-16, IA pass
    follow-up; owner ruling IA-4, click-through gate). The seven-role
    reading-paths table on `web/index.html` links per a build-side mapping,
    `orientation.ROLE_TABLE_LINKS`, placed next to the table render in
    tools/orientation.py. Cell text stays verbatim from
    data/front/00-how-to-use.md — links wrap whole cells (or, for the
    operations row's two-target "Then" cell, each comma-joined mapped
    segment, all-or-nothing per cell); nothing is reworded. Mapping: the
    five named derived sections link their catalogue.html anchors; P2/P3/P4
    link their area-heading anchors; the range "B1–B6" links its first
    member only (B1's anchor); "Audit register (claims, sources, change
    history)" links evidence-pack.html (page-level, no anchor); "Linked
    ASVS chapters" and the instructional phrases stay plain (external
    target / no single target). Area anchors use the built page's full-title
    ids (e.g. p2-security-testing-and-verification,
    b1-hardening-misconfiguration-and-patch-management). Web rendering
    only: the edition's embedded how-to-use section and build/md are
    untouched. **Target verification:** build_site proves every mapped
    anchor exists in the built page it names — mapped-but-missing is a
    SystemExit naming the cell and target (the same discipline as the
    347-anchor deep-link check); unmapped cells degrade silently to plain
    text. Red-first in a /tmp copy: one mapping anchor changed to a
    nonexistent id → SystemExit "role-table link target missing:
    'Applicability index' maps to catalogue.html#applicability-index-x …";
    clean control passes. Rendered result: **9 of 14** non-role cells
    linked (**10** links; the operations "Then" cell carries two), the
    other 5 plain per the rules; the build prints the count each run.
86. **Site-root project-level introduction** (2026-10-16, IA pass
    follow-up; owner ruling IA-5, click-through gate; owner-approved copy
    pending word-level confirm — not reworded). The root `index.html`
    doorway gains the "What this is / What it's for / One catalogue is
    published today" block, replacing the one-liner `<p>` under the title
    and preceding the Catalogues list; the page stays a single doorway (no
    new file; allowlist still exactly 20). The copy lives in
    tools/orientation.py as a site-level, catalogue-agnostic block
    (`SITE_DOORWAY_PARAGRAPHS` + `site_doorway_published_today`): the
    published-today sentence's count word and title render from the
    catalogue manifests (data, not hardcoded prose) — at one catalogue the
    owner's sentence reproduces exactly; the n>1 form is mechanical (count
    word, plural, title join) and is reviewed when a second catalogue
    lands (same revisit flag as entry 82). Root-only by construction: only
    the root index render consumes it, and the block appears in exactly
    one built file, build/site/index.html (grep-verified across build/);
    the root llms.txt keeps the orientation one-liner, and no
    catalogue-level surface or edition output changed.
87. **Site re-layer** (2026-10-16, IA pass follow-up; owner ruling IA-6,
    click-through gate; copy owner-approved pending word-level confirm —
    not reworded). Root `index.html` gains three sections after the IA-5
    block and before the Catalogues list — "How to access it", "Who it's
    for", "Where it's going" — from
    `orientation.SITE_DOORWAY_PARAGRAPHS_IA6`; the leads are bolded to
    match the IA-5 block's house style (presentation, not wording; the
    ruling's copy carried plain leads). Supersession inside IA-5: the
    published-today sentence now ends at "currently in beta." — the
    further-catalogues clause lives only in "Where it's going". The
    catalogue index (`web/index.html`) slims to: h1; the one-liner
    (`orientation.ONE_LINER`, the text formerly in the root `site_line`,
    which the root llms.txt still renders); the §10.1 version-bearing
    status line (kept by law, entry 71); a project pointer up to the root
    page ("New to the project? What it is and how to access and use it:
    start at the project page.", href="/" — navigational chrome, executor
    wording per the ruling); the hyperlinked role table (IA-4, unchanged);
    the artifacts list (unchanged, link text/targets untouched); the stamp
    footer. B1/B2/B4 retired from the web page: B1 and B2 stay in
    tools/orientation.py (the edition front section W2 and the README sync
    rule 12 consume them); **B4 is removed** — after the re-layer nothing
    renders it and its content is carried by the root "Who it's for"
    section; `README_THREE_OUTPUTS_LEAD_IN` remains (the owner-approved
    README line, rule-12-enforced). Downloadable artifacts untouched by
    construction and by proof: W2/W3/W4/W6 outputs hash-identical before
    and after the re-layer (build/md, build/ai, catalogue.html/pdf/docx,
    evidence-pack.md/html). Allowlist still exactly 20 files.
88. **Evidence-pack URL cells hyperlinked** (2026-10-16, IA pass
    follow-up; owner ruling IA-7, click-through gate). The per-ID
    reference tables' URL cell renders as a markdown link with the URL as
    both text and target — one source (references_table in build.py)
    flowing to evidence-pack.md and .html; no separate HTML handling.
    Corpus check first: no stored URL contains ")", whitespace or a
    newline, so every URL is markdown-link-safe as stored (R1 — no
    normalisation needed). Counts, stated precisely (verifier finding 1,
    corrected): **143 of 144 references carry a URL; 139 URL cells render
    in the pack** — R-3, R-27, R-28 and R-36 are cited at area level only
    (no claim section, so no references-table row), exactly like R-107's
    no-URL case (url null, judgment call 6; cited only by area P2) — and
    **every rendered cell is linked**. The "— (no URL)" code path is
    unchanged and fires if a claim ever cites R-107. The reference
    **titles** stay plain in the pack (owner
    considered and did not ask); Appendix B keeps its own linked-title
    rendering, untouched. The evidence pack is not round-trip-compared and
    build/md is untouched.
89. **Claim-record Sources cells link to Appendix B** (2026-10-16, IA pass
    follow-up; owner ruling IA-8, click-through gate). In the 347
    claim-record tables, the Sources cell's R-ID tokens render as
    [R-n](catalogue.html#R-n) — relative, markdown source flowing to both
    outputs; degradation is the established deliverable-6 model (live
    where the pair travels, non-resolving alone). Scope kept: the per-ID
    references-table ID column stays **plain** (owner considered and did
    not ask); catalogue/Appendix B rendering untouched; no roundtrip-
    compared file changes. Build-time proof: verify_pack_link_targets()
    (build.py) reads the catalogue.html rendered in step 2 and requires
    every emitted R-target's `id="R-n"` to exist — mapped-but-missing is a
    SystemExit naming the IDs (the role-table discipline); it returns the
    token count, printed each build. **Counts: 481 linked tokens** (sum of
    sources-list lengths across the 347 claim records; 139 distinct
    R-IDs, all verified present as anchors). Red-first in a /tmp copy:
    one anchor id corrupted in the built catalogue.html → SystemExit
    "… no Appendix B anchor in catalogue.html for: R-35 …"; clean control
    returns 481.
90. **References page — the third site artifact** (2026-10-16, IA pass
    follow-up; owner ruling IA-9, click-through gate).
    `web/references.html` renders Appendix B per reference as its own page,
    from `build.references_page_markdown()` through the shared Pandoc
    pipeline (scratch in build/pandoc/, §10.1 stamp as the subtitle, the
    Lua filter keying on the table's "R-ID" header so **every one of the
    144 rows anchors per R-ID** — the page is the deep-link target for
    R-IDs). Page order: the orientation line ("Every source cited by the
    catalogue, with its tier, link and citation reach — Appendix B rendered
    per reference." — the ruling's own phrasing), the evidence legend from
    the same parsed governance source as every other surface, then the
    144-row table. Title cells link exactly as Appendix B links them
    (generate.py's reference_cell, imported — one implementation; R-107
    stays plain text, no URL); tier (with tier_note) and opened as the
    appendix carries them. **Cited-by cells:** T-/C-/F-ID tokens link to
    evidence-pack.html#<ID> — **481 tokens linked** — while area tokens and
    section labels stay plain (11 tokens; the established degradation
    model). **Ruled allowlist amendment: 20 → 21 files** — site_allowlist()
    gains web/references.html (builder and checker share the one
    definition, entry 59; the ia-1 brief's gate said "exactly 20", amended
    by this ruling). **Supersessions of in-flight work:** IA-8's
    claim-record Sources cells retarget from catalogue.html#R-… to
    references.html#R-… (481 tokens, unchanged count), and the evidence
    pack's per-ID reference-table ID column — plain per IA-8's scope note —
    now links each R-ID to references.html#<ID> (481 tokens, the same
    token set). **Build-time proofs** (mapped-but-missing is a hard error):
    the rendered page must carry exactly 144 R-row anchors;
    verify_pack_link_targets now runs against the references page and
    covers both R-link surfaces (139 distinct R-IDs); and every cited-by
    T/C/F target must exist as an anchor in the built evidence-pack.html
    (294 distinct T/C plus the F set — all verified). The web index's
    artifacts list gains a References entry ("Every cited source with its
    tier, link and citation reach (Appendix B, rendered)." — the ruling's
    caption, a list caption not orientation prose). Editions keep
    Appendix B unchanged: build/md, the PDF and the DOCX are untouched
    (the page renders from a site-side scratch file, not the edition
    tree), so determinism and the round trip are unaffected by
    construction.
91. **Root page "Why this exists"** (2026-10-16, IA pass follow-up; owner
    ruling IA-10, click-through gate; owner-confirmed verbatim — not
    reworded). Four paragraphs added to the root doorway block as
    `SITE_DOORWAY_PARAGRAPHS_IA10`, placed between the IA-5 block (with
    its published-today sentence, kept in place) and "How to access it" —
    the root now reads What this is / What it's for / published-today /
    Why this exists / Expected usage (IA-11) / How to access it / Who
    it's for / Where it's going. The "Why this exists." lead is bolded
    (house style, presentation only); the three continuation paragraphs
    carry no lead. Root page only: the section renders from
    site_doorway_paragraphs_html, whose sole consumer is
    site/root/index.html.j2, and grep across build/ finds its text in
    exactly one built file (build/site/index.html). No other artifact
    changed; build/md, build/ai and the downloads are untouched.
92. **Root page "Expected usage"** (2026-10-16, IA pass follow-up;
    owner ruling IA-11, click-through gate; owner-confirmed verbatim with
    the added closing sentence — not reworded). Two paragraphs added as
    `SITE_DOORWAY_PARAGRAPHS_IA11`, placed immediately after "Why this
    exists" (IA-10). The "Expected usage." lead is bolded (house style);
    the closing sentence ("Each catalogue page carries the full
    start-here-by-role table with links.") is the owner's added text. Same
    isolation proof as IA-10: root render only, one built file, nothing
    else changed. Alongside these, verifier finding 1 was applied as a
    wording fix, no behavior change: the build print and entry 88 now
    state the IA-7 counts precisely — 143 of 144 references carry a URL;
    139 URL cells render in the pack (R-3, R-27, R-28 and R-36 are cited
    at area level only, so no pack row, exactly like R-107's no-URL case);
    every rendered cell is linked.
93. **Web page widths** (2026-10-16, IA pass follow-up; owner ruling
    IA-13, click-through gate — the "for web" read applied broadly).
    The three Pandoc-rendered pages (catalogue.html, evidence-pack.html,
    references.html) drop the default template's 36em body cap via a CSS
    override passed only to the HTML invocations
    (--include-in-header, build/pandoc/web-header.html written at run time
    from the WEB_HEADER_HTML constant — the anchors.lua pattern; static
    CSS, determinism preserved). The override is exactly `body {
    max-width: none; }` and `table { width: 100%; }`, appended after the
    template's own style block (verified: later position, equal
    specificity, so it wins); the template's padding (50px; 12px under
    the 600px media query), line-height, colours and the small-screen
    media query stand untouched. The two hand-built pages
    (site/root/index.html.j2, site/web/index.html.j2) lose their 46rem
    body cap, and the web index's 40rem prose caps on p.what/p.status go
    with it (prose width limits); padding logic unchanged. **Byte-proof:
    build/md, build/ai, catalogue.pdf and catalogue.docx hash-identical
    before and after** — the PDF and DOCX invocations carry no header
    argument, so the print editions are untouched by construction; the
    extract HTML is out of the ruling's named scope and unchanged. No new
    site files (allowlist stays 21); no markdown change (round trip
    unaffected).
94. **PDF table defects: page-boundary overlap and column widths — diagnosed, proven latent at the tag, fixed build-side** (2026-10-16, owner defect reports from the click-through gate). **Reproduction:** pdftotext -bbox geometry on the built PDF showed table rows printed on top of each other at page bottoms — page 28's T-A5-9 and T-A5-10 rows share baselines from y=705 into the margin (y~780; the text region ends near 742), pages 93/95 likewise; 29 pages carried content past the bottom margin, and Appendix B's 144-row table was compressed into roughly two unreadable pages. **Diagnosis:** a minimal generator-agnostic reproduction (a #figure-wrapped table breaking across a page boundary) reproduces the overlap with plain typst 0.15.1 — pandoc's writer is not at fault; the align(center) wrapper and the caption show-rules were each tested and exonerated. The second report (equal 33.33%/25%/20% columns cramming prose) is the writer's fixed-percentage emission. **Provenance:** rebuilt from tag v1.0.0-beta.1 in a /tmp copy (git archive, same pinned toolchain): the same defect at pages 26/91/93 — latent at the tag, surfaced to the owner only by the About-section pagination shift; not introduced by the IA pass. **Fix (no version change):** the PDF pipeline is now two-step — pandoc writes build/pandoc/catalogue.typ, postprocess_typst() (a) de-figures every table (a bare #table breaks correctly; a surviving figure-wrapped table is a hard error) and (b) rebalances each table's columns from its cells (0.45 x longest token + 0.55 x average length, clamped to [4%, 45%], normalised; header rows split per cell, hline args skipped), then typst compiles with --creation-timestamp pinned to the same SOURCE_DATE_EPOCH value (entry 51's determinism reading; proved — two consecutive full builds byte-identical including the PDF). The .typ diff is exactly the de-figure and the column tuples; DOCX and HTML renders untouched. Result: 80 pages (was 96 defective), 0 overprint words (was 7), 0 pages into the margin (was 29), Appendix B spans from page 65 readably; the defective build had been hiding text — pdftotext recovers 22,367 words after vs 19,526 before (clipped under the overlaps). **Proof:** before/after/landscape renders under build/pandoc/pdf-proof/ (before.pdf, after.pdf, PNGs; the before set is the pre-fix build), inspected visually by a vision-model subagent per the owner's environment tip: doubling confirmed on before pages 28/93/95 and absent on every after page; widths judged readable (prose 1-3 lines per row; only the intrinsically long Cited-by lists still wrap); minor cosmetics noted for the owner (a header hyphenation, an Opened/Cited-by header collision, R-ID abutment). **Landscape (owner's choice, not flipped):** an Appendix-B landscape variant (build/pandoc/pdf-proof/appendixb-landscape.pdf; one line per reference; judged the most readable form) is staged; the inspector's assessment is that portrait-after is good enough (every reference in 1-2 lines, heading and table share the page) and landscape costs a near-blank heading page plus mixed orientation — pending the owner's word per the ruling's "do not unilaterally flip". README's PDF mechanism sentence updated to the two-step truth. Gates after: check 0 errors / 543 warnings; roundtrip exit 0 (i3/ii125/iii62/iv0); double build byte-identical; allowlist 21, stamps ok; extract clean.
95. **README gains "Why this exists" and "Intended use"** (2026-10-16, IA
    pass follow-up; owner rulings IA-12, IA-14 and IA-15, click-through
    gate; owner-supplied text verbatim, with "catalog" normalized to
    "catalogue" in IA-12's last sentence per the owner's explicit word).
    Canonical in tools/orientation.py (README_WHY_PARAGRAPHS, two
    paragraphs; README_INTENDED_PARAGRAPHS, three: IA-14's lead plus
    IA-15's priors and mechanism paragraphs); rendered in README.md after
    the status paragraph and before "The three outputs", bolded leads
    matching the README's existing bold-lead style, no new headings. Rule
    12's coverage extended to every new paragraph (each checked
    whitespace-collapsed against the canonical source); red-first in a /tmp
    copy: one word changed in "Why this exists" paragraph 1 → "1 errors,
    543 warnings", exit 1, the ERROR naming the paragraph and ruling;
    clean state silent at 0/543. Isolation: the IA-12 text appears in
    README.md only ("illusion of reliability" grep across build/ and the
    repository); the root page's IA-10 "Why this exists" is its own
    owner-confirmed text and is unchanged — README and root carry their
    own altitudes, per the ruling.
96. **Root "Expected usage" rider** (2026-10-16, owner ruling IA-15 root
    rider, owner-confirmed). A third paragraph appended to the root page's
    "Expected usage" section after the by-role paragraph
    (SITE_DOORWAY_IA11_RIDER in tools/orientation.py, root render only);
    the root page's "Why this exists" is untouched. Isolation: the rider's
    text appears in exactly one built file, build/site/index.html (grep
    across build/). Gates after both entries: check 0 errors / 543
    warnings with rule 12 silent; round-trip exit 0 (catalogue i3/ii125/
    iii62/iv0); two consecutive builds byte-identical; allowlist 21 files,
    stamps v1.0.0-beta.1; extract clean; the fixed PDF still scans clean
    (80 pages, 0 overprint, 0 margin pages — entry 94 stands).
97. **Appendix B column defects fixed — header-aware sizing; entry 94's
    "cosmetics" reclassified as defects; landscape track dropped**
    (2026-10-16, owner ruling IA-17). **Reclassification:** the owner's
    inspection of the shipped portrait PDF found the R-ID column
    overlapping the Reference column and the "Opened"/"Cited By" header
    cells overlapping each other — the two items entry 94 had noted as
    "minor cosmetics for the owner". Both are owner-ruled defects (the
    owner's eyes are the final arbiter over sampled vision checks); the
    same defect class was also latent in the Issuer column
    ("PostQuantum.com", 84pt, in a 43pt column) wherever a cell's widest
    unbreakable token exceeded its column. **Fix (build.py,
    postprocess_typst):** column sizing is now header-aware and measured
    in points, not character counts — a per-character width table
    calibrated against the rendered PDF (Libertinus Serif 11pt; fitted to
    the word bboxes of a built catalogue, median error 0.07pt, p95
    0.56pt), inflated by a 1.05 safety factor. Every column's floor is
    the widest unbreakable segment it must show whole: its header label
    (one line where the text block affords it — headers wrap at word
    boundaries only where it does not; Appendix B's "Edition or date" is
    the one wrapped header) and its widest cell token (cited IDs R-100 /
    C-A12-10 stay whole; other tokens may break after a hyphen, which
    typst does). Floors carry the table insets; the remainder flexes to
    the columns by content mass, so the Reference and Cited-by columns
    absorb it. Appendix B's floors only fit at a 3.5pt gutter, so that
    one table gets an explicit `inset: (x: 3.5pt, y: 6pt)` (the
    template's 6pt everywhere else); a table whose floors cannot fit
    even at 3.5pt is a hard build error, so the collision class cannot
    recur silently. Cited IDs are additionally wrapped in `#box[…]`
    (layout-only; glyphs and extracted text unchanged) because typst's
    line breaker would otherwise split them after the hyphen, leaving
    bare "C-"/"T-" fragments at line ends (260 occurrences in the first
    fixed build; zero now). Appendix B tuple: 7.94 / 21.08 / 22.00 /
    13.28 / 11.87 / 10.98 / 12.85. **Landscape dropped:** the staged
    Appendix-B landscape variant (entry 94) is removed — the owner found
    overlap there too; the shipped PDF is portrait-rebalanced (the
    before/after proof set under build/pandoc/pdf-proof/ stands, minus
    the landscape files). **Proof (upgraded standard):** every Appendix B
    page (69–86 of 87; the verifier's independent pass extended the range
    one page past this entry's original count and found it clean) plus a
    300 dpi header-row close-up of each table
    type (threats, controls, Appendix A, Appendix B) inspected by
    vision-model subagents under the binding rule that header collisions
    and column abutment are failures, never cosmetics — all pages PASS
    (per-page results in the dispatching agent's report); corroborated
    geometrically: 0 word-bbox overlaps in the whole document
    (pdftotext -bbox pairwise intersection). Gates after: check 0 errors
    / 543 warnings; roundtrip --exports ../import-2026-10/inputs exit 0
    (i3/ii125/iii62/iv0, class (iv) empty); two consecutive full builds
    byte-identical including the PDF; allowlist 21 files; extract
    reviews/example-checklist.yaml clean.
98. **Site survives mobile — evidence-pack URL cells wrap; references
    R-table CSS-unfixable readably, escalated (IA-18)** (2026-10-16,
    owner ruling IA-18, on-device check; mid-run rescope — the owner's
    device findings: catalogue pages good, not to be churned; evidence
    pack and references fail — tables that do not compress scroll
    across). **Measurements (Playwright, 390×844 / 820×1180 /
    1440×900):** root, web index, catalogue — no page pan, prose
    reflows (catalogue keeps wide-table crush the owner has approved
    on-device). Evidence pack — 383 of 789 tables overflowed their box
    (widest 796px in 366px); diagnosis confirmed: 481 raw-URL cells
    (links whose display text is the URL — one unbreakable token
    forcing min-content past the viewport). References — the 7-column
    R-table at 535px min-content in a 362px box; diagnosis NOT
    confirmed there: zero raw-URL cells (grep), the drivers are plain
    tokens (issuer names, title words) in seven fixed columns.
    **Shipped fix (CSS-only, IA-13's include-in-header location):
    evidence pack only** — `td a[href^="http"], th a[href^="http"] {
    overflow-wrap: anywhere; }` plus a phone-width `table {
    font-size: 0.85em }` step under the template's own 600px
    breakpoint (web_header() gained a urlwrap variant writing
    build/pandoc/web-header-urlwrap.html; static CSS, determinism
    proved). `anywhere` on external-target links alone — unlike the
    body's inherited break-word it counts in min-content sizing, so
    URL tables shrink to the viewport and wrap the URL in place;
    ordinary prose never breaks mid-word. Result at 390: 780/789
    tables fit (URL cells wrap, e.g. a 73px column carrying its URL
    over ~10 lines); 9 six-column change-history tables still exceed
    their box by ≤27px and scroll within their region (the pandoc
    template's own unconditional display:block/overflow-x:auto —
    pre-existing, un-churned); page never pans. At 820: 0 over.
    Desktop unchanged: at 1440 the rule toggles 0 table widths
    (measured), no caps reintroduced. Catalogue untouched: byte-
    identical build (site diff = evidence-pack.html only) and
    pixel-identical 390px screenshots before/after (cmp).
    **References — attempted and rejected:** the prescribed wrap
    applied to all cells makes the R-table fit 390px by shattering
    every word (~50px columns; vision check FAIL: "MITR/E",
    "Securi/tyWee/k", fragments needing stitching); with hyphenation
    enabled (lang injection test) "PostQuantum.com" still shatters
    into six fragments — 7 readable columns need ~490px > 390. A
    readable CSS-only fit does not exist; the page therefore keeps
    its byte-identical approved rendering (R-table region-scrolls by
    the template's own rule) — ESCALATED for an owner decision:
    accept region scrolling, accept word-shattering, or a non-CSS
    stacked layout (needs markup). Screenshot evidence at the
    workspace root (ia18-final-*.png, ia18-*-390-*.png),
    vision-checked by a vision-model subagent. Gates after: check 0
    errors / 543 warnings; roundtrip exit 0 (i3/ii125/iii62/iv0,
    class (iv) empty); two consecutive full builds byte-identical;
    allowlist 21 files.
