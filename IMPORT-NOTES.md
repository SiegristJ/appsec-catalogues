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
