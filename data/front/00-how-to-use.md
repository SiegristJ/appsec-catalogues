# How to use this catalogue


This catalogue is source material for a web application security spec. A reviewer copies the applicability index into the review, marks every feature present or absent (an explicit “absent” is a checkable claim; a blank is not), and pulls the threats and controls of matching areas into the spec by ID.

Areas fall into three groups:

- **A1–A13, application design and code:** selected by architecture features.
- **B1–B6, hosting and infrastructure:** selected by architecture features.
- **P1–P4, process:** these apply to the organisation that builds and runs the application, not its architecture, so they belong in a delivery or operations spec, whatever the application.

**Per-area template.** Every area from A1 to B8 has the same four parts:

| Part | Holds |
| --- | --- |
| Applies when | Architecture features that make the area relevant; “All” marks a universal area |
| Threats | ID, name, mechanism in one line, CWE or OWASP reference |
| Controls | ID, control, threats addressed, ASVS 5.0 chapter, baseline or conditional |
| Residual risk | What the controls leave open, and where only detection or blast-radius reduction is available |
| Facts and sources | F-IDs for any volatile fact used (Appendix A) and R-IDs for every source cited (Appendix B) |
| Last reviewed · Watch | Date of last review; events that should trigger a revision (a standard going final, a new edition) |

**IDs.** Four kinds:

- `T-<area>-<n>` for threats (T-A3-1)
- `C-<area>-<n>` for controls (C-A3-1)
- `F-<n>` for volatile facts: figures, editions, dates
- `R-<n>` for references

IDs are stable: new items are appended, and retired items stay in place marked “Retired” so spec citations keep resolving. Each threat has one home area; other areas cross-reference it by ID instead of restating it. Controls map to ASVS 5.0 at chapter level; requirement IDs are added when a spec pulls a control.

**Markers.**

- **Disputed:** experts hold different positions; the item links to “Where experts differ”.
- **Draft standard:** the item rests on a standard not yet final (OAuth 2.1, NIST SSDF v1.2, NIST IR 8547).
- **Single source:** the evidence comes from one research paper or vendor; treat it as indicative.

**Derived sections.** The applicability index, baseline and conditional controls, residual-risk summary, compliance mapping and Appendices A and B are derived from the areas. They are regenerated after area edits, never hand-edited (Appendix C).

**Provenance.** This catalogue carries IDs, not audit trails. The claim and change history behind each ID lives in a companion audit map; the initial provenance is the Web Application Security: Cross-Report Reconciliation doc.

**Reading paths by role.**

| Role | Start with | Then |
| --- | --- | --- |
| Solution or enterprise architect | Applicability index | “Applies when” and residual risk in each matched area |
| Spec writer or engineering lead | Controls in matched areas (C-IDs, ASVS chapter) | Baseline and conditional controls |
| Developer | Threats and controls in the areas the spec pulled | Linked ASVS chapters |
| Security reviewer or penetration tester | Threats and residual risk | P2 Security testing |
| Risk owner or management | Residual-risk summary | Where experts differ |
| Compliance or audit | Compliance mapping | Audit register (claims, sources, change history) |
| Operations or platform team | B1–B6 | P3 CI/CD, P4 Detection and incident response |
