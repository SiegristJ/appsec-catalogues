# AppSec Catalogues

A version-controlled corpus of web application security knowledge — areas, threats,
controls, volatile facts and references, all carrying stable IDs — together with the
tooling that generates every human-readable and AI-readable edition from it. The
structured data under `data/` is the single source of truth; every document is built,
never hand-edited. The catalogue exists to be selected from: a reviewer declares an
application's architecture features and pulls the applicable threats and controls into
a specification by ID.

**Status: 1.0.0-beta.1 (import in progress).** This is beta material: it has been
verified against its cited sources but has not yet had independent review or specialist
sign-off. It is not yet suitable for risk acceptance or compliance assertions; the
evidence status of every claim is recorded in the audit register.

## The three outputs

| Output | Serves |
| --- | --- |
| Architecture-review extracts (`tools/extract.py`) | Reviewers and spec writers pulling applicable controls into a security specification |
| Full reference edition (Markdown, HTML, PDF, DOCX) | Architects and security specialists reading end to end |
| AI-optimised edition (`catalogue.json`, `catalogue.jsonl`, `llms.txt`, `AGENTS.md`) | Agents that draft specifications or check designs and code against the controls |

## Corpus and catalogues

`data/` is one corpus: areas, threats, controls, facts and references with global,
permanent IDs. A **catalogue** is a named selection of areas from that corpus plus its
own front matter and URL path (see `catalogues/*.yaml`); catalogues may overlap, and an
ID means the same thing in every catalogue that includes it. One version number covers
the whole repository; per-record `last_changed` gives finer detail.

## Building

*(To be completed with the generator and build tooling — stages 5–9.)*

System dependencies: Python 3.11+, Pandoc (3.1.2 or later) and Typst, with the versions
used for the initial build recorded here at first release.

## Running an extract

*(To be completed with `tools/extract.py` and the example checklist — stage 8.)*

## Versioning

- **major** — changes to the ID scheme or structure that break spec citations;
- **minor** — new areas, threats or controls;
- **patch** — fact updates and wording.

## Deployment

*(Owner setup steps for the Cloudflare Worker at `appsec.complects.com` — to be
completed at stage 9.)*

## Further reading

- [`HISTORY.md`](HISTORY.md) — where the catalogue came from and what beta means
- [`register/governance.md`](register/governance.md) — evidence tiers, verification
  statuses, roles and the change procedure
