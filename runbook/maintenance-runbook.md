# Maintenance runbook

Planned; the procedures below are named and TODO.

The maintenance procedure itself (Appendix C of the catalogue, refresh
cadence, signal triage, the promotion rule for emerging material) lives in
`data/maintenance.md` and is rendered into every edition. This runbook
holds the operational tasks around it — the things an owner must do on a
schedule that the repository cannot do for itself.

## Named maintenance tasks

- [ ] **Check the Cloudflare API token expiry date** (owner setup,
  SETUP-INSTRUCTIONS 10.1 "Deployment"): the token used by the deploy jobs
  was created from the "Edit Cloudflare Workers" template **with an expiry
  date**. Record the date here when the token is created, and renew it
  before it expires — a failed deploy on a tag is a failed release.

  - Token created: ____________ (owner fills in)
  - Token expires: ____________ (owner fills in)
  - Check before: ____________ (owner fills in; suggest 30 days ahead)

- [ ] **TODO (owner)**: define the emerging-items evidentiary standard
  (`emerging/emerging-threats.md`) and the promotion rule from that
  document into the corpus.
- [ ] **TODO (owner)**: schedule the watch list — each area's `watch` line
  is collected in `watch-list.yaml`; review it against new editions of the
  cited sources (see `data/maintenance.md`).
- [ ] **TODO (owner)**: run `tools/snapshot.py --all` to capture source
  snapshots (written at stage 9, deliberately not run during import), then
  work down `check.py` warning 4 (`snapshot: null`).
- [ ] **TODO (owner)**: replace `@SPECIALIST_REVIEWER` in
  `.github/CODEOWNERS` once roles are assigned.
