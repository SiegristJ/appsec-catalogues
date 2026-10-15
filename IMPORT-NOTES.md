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

*(none yet)*

## Splits and merges

*(none yet)*

## Null fields

*(inventory due at stage 3 — `requirement`, `verify`, feature `question`/`guidance`,
`trigger.rule` are all left null per section 1 rule 3)*

## Feature vocabulary to approve

*(due at stage 3: every distinct conditional-control `trigger.text`)*
