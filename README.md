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

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python tools/build.py
```

`tools/build.py` runs `tools/generate.py` (Markdown and AI editions in `build/md/` and
`build/ai/`), renders the catalogue with Pandoc to `build/out/catalogue.html` (with a
table of contents and an anchor on every ID, so specs can deep-link), `catalogue.pdf`
and `catalogue.docx`, builds the evidence pack (`build/out/evidence-pack.md` and
`.html`: per ID its claim record, its references with tier, URL and snapshot status,
and the change-log rows mentioning it), and assembles the published site in
`build/site/` from an explicit allowlist — catalogue content under `build/site/web/`,
landing pages at the root, and nothing from `archive/` or `data/`. Generated output is
never committed.

`tools/check.py` checks the corpus (0 errors expected; the remaining warnings are the
known import gaps listed in `IMPORT-NOTES.md`), and `tools/check.py --release
<version>` adds the release-mode rules, including the site allowlist rule.

### System dependencies

Python 3.11+, Pandoc (3.1.2 or later) and Typst. Versions used for the initial build:

| Dependency | Version used |
| --- | --- |
| Python | 3.14.6 |
| Pandoc | 3.12 |
| Typst | 0.15.1 |

The PDF renders with `--pdf-engine=typst`. CI installs the same pinned versions.

## Running an extract

```sh
.venv/bin/python tools/extract.py reviews/example-checklist.yaml
.venv/bin/python tools/extract.py reviews/example-checklist.yaml --since v1.0.0-beta.1
```

The checklist declares every feature in `data/features.yaml` present or absent;
`extract.py` errors on an undeclared feature, an unknown key, or a
`catalogue_version` that does not exactly match the build stamp (the stamp reads
"untagged" until the repository is tagged). The output (`build/out/extract-<name>.md`
and `.html`) lists the universal and feature-pulled areas, each area's threats and
baseline controls, conditional controls under "Conditional — confirm applicability",
residual-risk lines, the areas excluded by absent features, and — with `--since` —
every included record whose `last_changed` is later than that version.

## Local preview

```sh
.venv/bin/python tools/serve.py
```

Builds the site and serves `build/site/` on `http://localhost:8000/` — the way to
review rendered output before a release. `--port` chooses another port, `--no-build`
re-serves the last build. This is the local stand-in for the deployed site: the
landing page at `/`, the catalogue under `/web/`, and the 404 page for anything
outside the allowlist.

## Versioning

- **major** — changes to the ID scheme or structure that break spec citations;
- **minor** — new areas, threats or controls;
- **patch** — fact updates and wording.

## Deployment

The catalogue is published at `https://appsec.complects.com/web/` as its own
Cloudflare Worker (static assets only, no script; see `wrangler.jsonc`). A tag is a
release, and only a release is deployed: `ci.yml` builds and checks every pull
request and push to `main` without publishing, `release.yml` builds, checks in
release mode, creates the GitHub Release and deploys the tag, and `redeploy.yml`
re-deploys a chosen tag by hand (the rollback path). Generated output is never
committed, and nothing from `archive/` or `data/` is ever published.

Owner setup, done by the owner and not by the tooling:

- Create a Cloudflare API token from the "Edit Cloudflare Workers" template, scoped to the account and to the complects.com zone only, with an expiry date. If the first deploy cannot attach the custom domain, either add DNS edit on the zone or attach the domain once in the dashboard.
- In GitHub, create environment `production`. Restrict deployments to tags matching `v*`, add secret `CLOUDFLARE_API_TOKEN` and variable `CLOUDFLARE_ACCOUNT_ID`.
- Add a tag ruleset so that only the owner can create tags matching `v*`.
- In Cloudflare, check the zone's bot and AI-crawler settings, so that `llms.txt` and `ai/` are not blocked.
- Confirm nothing else is already bound to `appsec.complects.com` in the zone; the first deploy creates its DNS record.
- Record the token's expiry date in `runbook/` as a maintenance task.

The token's expiry check is the first named task in
[`runbook/maintenance-runbook.md`](runbook/maintenance-runbook.md).

## Further reading

- [`HISTORY.md`](HISTORY.md) — where the catalogue came from and what beta means
- [`register/governance.md`](register/governance.md) — evidence tiers, verification
  statuses, roles and the change procedure
- [`CHANGELOG.md`](CHANGELOG.md) — releases, linking to
  [`register/change-log.md`](register/change-log.md) for detail
- [`ROADMAP.md`](ROADMAP.md) — deferred work and the reasoning behind it
