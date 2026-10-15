# Web Application Security Catalogue: History and Provenance

Oct 12, 2026 · @John Siegrist

## Status

The document set is at version 1.0-beta-1 (12 October 2026). Every threat, control and fact ID in the catalogue cites a source other than the AI reports it grew from. It has not yet had a coverage check against independent frameworks, an independent review or specialist sign-off. Use it as background material and candidate controls for a spec, checking each pulled clause against its cited source; do not use it to accept risk or assert compliance.

| Document | Role | State |
| --- | --- | --- |
| [Web Application Security Reference Catalogue](data/) | Threats, controls, residual risk, facts and references, by area | Live; beta-1 |
| [Audit Register](register/) | Claim, source, tier and verification status per ID; change log; area reviews; governance | Live |
| History and Provenance (this document) | Where the set came from and what beta means | Live |
| [Cross-Report Reconciliation](archive/origin/reconciliation/) | How the two source reports were compared and settled | Frozen; archived |
| [Source reports](archive/origin/source-reports/) (Claude and Gemini) | The two AI deep-research reports the work started from | Frozen; archived |
| [Provenance archive](archive/sources/) | Snapshots of cited sources | Planned |
| [Emerging-threats document](emerging/) | Fast-moving material not yet in standards | Planned |
| [Maintenance runbook](runbook/) | Baseline refresh, signal triage, promotion rule | Planned |

## Origin

The set began as two AI deep-research reports on web application security, produced independently in October 2026:

- **Claude report:** “Web Application Security: A Vendor-Neutral Taxonomy of Requirements, Threats and Mitigations (October 2026)”. Breadth-first: about 25 control areas, 88 citations, recommendations and caveats.
- **Gemini report:** “The Architecture of Web Application Security: A Comprehensive Analysis of Threats, Vulnerabilities, and Mitigations”. Depth-first: ten narrative sections with deep dives on selected mechanisms, 110 citations.

Neither was usable directly. They disagreed on figures, standards and how far controls protect, each covered topics the other omitted, and both leaned on vendor blogs and secondary summaries. The intended use was foundational material for web application specs, matched against proposed architectures, so the content had to be reconciled, verified against primary sources and restructured into a citable catalogue.

## How the catalogue was built

All stages took place on 12 October 2026, with the owner directing each step and Claude doing the research and drafting.

1. **Accounting.** The two reports were compared claim by claim without judging correctness: 25 points of agreement, 11 disagreements, 26 Claude-only areas and 19 Gemini-only topics.
2. **Inclusion review.** Each single-source item was tested for accuracy, scope and sourcing: 27 included, 15 included with correction, 2 excluded, 1 rebuilt.
3. **Harmonised consensus.** Each agreed point became one merged statement, carrying corrections and dropping unsupported absolutes (“immune”, “neutralizes”).
4. **Disagreement decisions.** Primary sources settled seven disagreements: three were edition mismatches in Verizon DBIR figures, and four went to the Claude report. Of four strength-of-claim disputes, one had a material error and three stand as dual positions.
5. **Catalogue design.** The narrative report format gave way to a catalogue matched to architecture features. Each area uses one template (Applies when, Threats, Controls, Residual risk), and stable IDs serve spec citation.
6. **Audit register design.** Claims, changes and reviews were recorded per ID, with evidence tiers, verification statuses and governance.
7. **Drafting.** A pilot area (A3 Authorisation) was approved by the owner. The other 22 areas, the front matter and the summary sections followed, each drafted in separate content, claim-check and style passes.
8. **Unverified sweep.** Every ID left Unverified after drafting was traced to a tier 1 or tier 2 source, and several controls were reworded to their sources’ outcome language.

Verification caught more than ten errors along the way. Most were inherited from the reports: a CWE rank, a misattributed PortSwigger entry, a false claim about XSS in exploited-vulnerability data, an unsupported OWASP term. Some were the drafter’s own, such as four wrong ASVS chapter mappings. Each is recorded in the register’s change log.

## Design decisions

**Taken**

- A catalogue to select from, not a narrative report. Reviewers mark architecture features present or absent and pull matching areas by ID.
- Three groups of areas: application (A1–A13), hosting (B1–B6) and process (P1–P4). Process areas apply to the delivery organisation, not the architecture.
- Stable IDs for threats, controls, facts and references. They are never renumbered, and retired items stay in place.
- Each volatile fact has one home (Appendix A) and each source one record (Appendix B). Summary sections are derived and regenerated, never hand-edited.
- Provenance is kept outside the catalogue, in a register keyed by ID, not inline or in a mirror document.
- Controls map to ASVS 5.0 at chapter level, with requirement IDs added when a spec pulls a control.
- Disputed items appear as dual positions unless one side has a material error.

**Deferred**

- **The evidentiary boundary for the catalogue.** Undecided between tier 1 only and tier 1 plus issuer-owned tier 2, and whether product-specific vendor documentation counts. Fast-moving material goes to a separate document with its own standard.
- **Splitting off platform material.** Deferred until another type of application that needs it, other than a web app, is being built.
- **Roles in the register’s governance** (owner, maintainer, specialist reviewer, approver). Not yet assigned.

## Known limitations and exit criteria for 1.0

**Limitations of beta-1**

- **Scope is inherited from the source reports.** Verification confirmed what is present but could not reveal what both reports missed; WebRTC (ASVS V17) is one known gap.
- **Drafting and verification were done by one model**, which also wrote one of the two source reports. Only A3 has had the owner’s review.
- **Quotes passed through a page-summarisation tool**, not raw text, and NIST SP 800-53 was read through a third-party mirror. Paraphrase errors may remain.
- **Some judgement is untracked:** the residual-risk ratings, some prose, and clause-level “standard practice” leftovers inside verified rows.
- **Some facts rest on secondary sources**, notably several DBIR 2026 figures.
- **Summary sections and appendices are partly stale**, with addendum tables awaiting regeneration.

**Exit criteria for 1.0**

- [ ] Coverage check against ASVS 5.0, the OWASP Top 10 and API Top 10, and the SSDF practices; every gap homed or explicitly excluded
- [ ] Exclusions and rejected claims recorded in the register
- [ ] Evidentiary boundary decided; fast-moving items moved to the emerging-threats document
- [ ] Unsourced judgement prose and clauses given IDs and sources, or removed
- [ ] Summary sections, appendices and change log regenerated
- [ ] Independent review by an agent that has seen neither source report nor the reconciliation
- [ ] Human spot-check of a sample of quotes against archived source text
- [ ] Specialist security review of every area
- [ ] Governance roles assigned

## Status of the source reports and reconciliation

The two source reports and the reconciliation are superseded and not authoritative: nothing in the catalogue depends on them as evidence. They are kept, frozen and read-only, in the provenance archive for three reasons:

1. They are the only record of what was considered and excluded, and why (for example zero-knowledge proofs and WAFBooster), until the register records exclusions itself.
2. The register’s Origin and Decision columns cite them, so a reader can trace any item back to where it entered.
3. They document the errors both reports contained, which is the case for verifying AI-generated research before relying on it.

Neither report should be cited, quoted or used as a source for future work. Questions about current content go to the catalogue and register; questions about how version 1 was assembled go to the archive.
