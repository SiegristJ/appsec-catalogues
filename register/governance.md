# Web Application Security Catalogue: Audit Register

Oct 12, 2026 · @John Siegrist

## Purpose and audiences

This register lets someone who took no part in building the Web Application Security Reference Catalogue check any of its claims. For each threat, control, fact and reference ID, it records:

- the source behind it;
- how strong that source is;
- when it was last verified, and by whom;
- every change made to it since.

The catalogue carries only IDs; the evidence lives here.

| Audience | Question the register answers |
| --- | --- |
| Auditors and compliance | What supports this control, and has it changed since we relied on it? |
| Risk owners | How strong is the evidence behind a residual-risk statement, and is the item disputed? |
| Security specialists | Which areas have had specialist review, and which claims rest on single or secondary sources? |
| Spec writers | Is the control I am citing current, retired or superseded? |
| Maintainers | What must be rechecked when a standard or dataset changes? |

## Register schema

The register has three tables, each in its own tab: claims (one row per catalogue ID), change log (one row per change), and area reviews (one row per area per review). Rows are keyed by catalogue ID, so the register survives any restructuring of the catalogue.

**Claims register**

| Column | Content |
| --- | --- |
| ID | Catalogue ID: T-, C- or F-. R-IDs are recorded in the catalogue’s Appendix B (issuer, edition, tier, opened), not here |
| Claim | The assertion the item makes, in one line |
| Sources | R-IDs supporting it |
| Evidence tier | Strongest tier among its sources (see Evidence tiers) |
| Verification | Status (see Verification statuses) |
| Last verified | Date, and who verified |
| Origin | Claude report, Gemini report, both, or new research |
| Decision | Link to the reconciliation entry that settled it (CL-, GE-, C- or D-number), if any |
| Status | Current, superseded (with successor ID) or retired |

**Change log**

| Column | Content |
| --- | --- |
| Date | When the change was made |
| IDs | Every catalogue ID touched |
| Change | What changed, in one line |
| Trigger | Why: watch-list event, new evidence, review finding, error report |
| Sources | R-IDs for the new evidence |
| Approved by | Approver (see Governance) |

**Area reviews**

| Column | Content |
| --- | --- |
| Area | A1–A13, B1–B6, P1–P4 |
| Review type | Drafting check, specialist review, scheduled re-review |
| Reviewer | Person or independent agent |
| Date | When reviewed |
| Outcome | Accepted, accepted with changes (change-log reference), or rejected |

## Evidence tiers and verification statuses

A claim’s tier and status together decide how strongly the catalogue may state it. A claim that a standard requires something needs a normative source checked first-hand; a claim about attacker behaviour needs primary research or data.

**Evidence tiers**

| Tier | Source type | Examples |
| --- | --- | --- |
| 1 Normative | The standard, specification or regulation itself | ASVS 5.0, RFCs, NIST SPs, PCI DSS v4.0.1, SLSA spec |
| 2 Issuing-body guidance | Official guidance, FAQs and advisories from the issuer or a government security agency | OWASP cheat sheets, CISA and NCSC advisories, AWS docs on AWS behaviour, a project’s own CVE advisory |
| 3 Primary research or data | Peer-reviewed papers, original datasets, original disclosures | Verizon DBIR, CWE Top 25 data, PortSwigger research, ACSAC and CCS papers |
| 4 Reputable secondary | Trade press or analyst summaries of tiers 1–3 | SecurityWeek, Tenable or SpyCloud DBIR summaries |
| 5 Commentary | Vendor marketing, personal blogs, Medium | Supporting explanation only |

**Verification statuses**

| Status | Meaning | What the catalogue may do |
| --- | --- | --- |
| Verified — primary | Checked against an opened tier 1–3 source | State without qualification |
| Verified — secondary | Checked only against a tier 4 source | State it, and mark “Single source” if only one supports it; upgrade when possible |
| Unverified | Carried from a source report, not yet checked | Appear in drafts only, never in a released version |
| Disputed | Credible sources disagree | Mark “Disputed” and present the positions in Where experts differ |
| Recheck due | A cited source has a newer edition or the watch list fired | Remain, flagged, until rechecked |

Two rules follow:

1. A normative claim (“PCI DSS requires …”, “ASVS L2 includes …”) needs tier 1 at Verified — primary before release.
2. A tier 5 source never supports a claim on its own.

## Governance

No change reaches a released version of the catalogue without a register row, an approver and, for a new or changed area, a specialist review. Who holds each role is an open question for the owner to settle.

**Roles**

| Role | Responsibility |
| --- | --- |
| Owner | Accountable for the catalogue; approves releases; assigns the other roles |
| Maintainer | Drafts changes, updates register rows, runs consistency checks; may be a person or Claude |
| Specialist reviewer | Security practitioner independent of the drafting; signs off areas |
| Approver | Accepts individual changes; the owner, or a delegate for routine fact updates |

**Change procedure**

1. A trigger fires: a watch-list event, new evidence, a review finding or an error report.
2. The maintainer verifies the new evidence and records it as R-IDs in the catalogue’s Appendix B.
3. The maintainer edits the affected areas and F-ID rows, then regenerates the derived sections.
4. The maintainer adds or updates claims-register rows and writes the change-log entry.
5. The approver accepts the change; changes to controls or residual risk also need specialist review of the area.
6. The owner releases a new version: dated, numbered, and listed in the change log.

**Specialist sign-off.** Every area needs one specialist review before the first released version (1.0), and again after any change to its threats, controls or residual risk. Fact-only updates (a new DBIR figure, an edition change) need approval but not re-review.

**Cadence**

- **Quarterly:** check every area’s watch list against the issuing bodies (OWASP, NIST, IETF, PCI SSC, SLSA, CISA, Verizon DBIR). This can run as a scheduled task that leaves proposed edits as comments.
- **Annually:** full re-review of every area, and every F-ID rechecked.
- **On event:** a critical disclosure or standard release affecting a control triggers the change procedure immediately.

**Consistency check, before every release**

- Every catalogue ID has a claims-register row, and every row has a catalogue ID.
- Every F- and R-ID cited in an area exists in Appendices A and B, and each appendix’s “used in” list matches.
- No area cites a retired or superseded ID as current.
- No released item is Unverified, and every normative claim is tier 1 at Verified — primary.

## Baseline provenance

Version 1 provenance is the Web Application Security: Cross-Report Reconciliation doc, which compared two source reports (one by Claude, one by Gemini) and settled their differences against primary sources. Its four tabs map into this register as follows:

| Reconciliation tab | Becomes |
| --- | --- |
| Accounting (C-, D-, CL-, GE-numbers) | The Origin column of each claims row |
| Inclusion review (CL1–CL26, GE1–GE19 verdicts) | Initial Verification status; excluded items get no row |
| Harmonised consensus (C1–C25) | Claim text for agreed items; Decision column links the C-number |
| Disagreement decisions (D1–D11) | Claim text, Disputed status for D7, D8 and D10; Decision column links the D-number |

The reconciliation doc stays frozen as a record of how version 1 was built. Later evidence goes into this register, not back into that doc.

The claims register, change log and area reviews tabs are added as the catalogue’s areas are drafted, with rows filled area by area. The first change-log entry records the catalogue’s creation on 12 October 2026.
