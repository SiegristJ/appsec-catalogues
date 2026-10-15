# Cross-cutting principles


Nine principles recur across every area; individual controls are applications of them.

1. **Deny by default.** Every request to every resource is authorised on the server, and the absence of a rule means refusal.
2. **Least privilege.** Users, services, pipelines, cloud roles and AI agents hold only the permissions their task needs; for agents this extends to the tools and actions they may invoke.
3. **Defence in depth.** Layers fail independently. A compensating control (a WAF, unguessable identifiers) never stands in for fixing the underlying flaw.
4. **Separate code from data.** Parameterised interfaces close injection structurally. Where separation is impossible, as with LLM prompts, the response is to bound impact rather than expect prevention.
5. **Fail closed.** Errors and exceptional conditions end in refusal, not in an unchecked path.
6. **Zero trust.** No request is trusted for its network location or device ownership; each hop, service-to-service included, is authenticated and authorised against policy (NIST SP 800-207).
7. **Minimise surface and data.** Unused features, endpoints, ports and stored data are removed rather than protected.
8. **Parser consistency.** When two components interpret the same bytes differently, attackers exploit the gap: request smuggling, WAF bypass, Unicode normalisation, SAML signature confusion. Use one canonical parser, normalise before validating, and reject ambiguous input.
9. **Verifiability.** Requirements are testable, build artefacts attestable and controls observable, so each claim of protection can be checked.

**Facts and sources.** Sources: R-6, R-10, R-13, R-26, R-27.

**Last reviewed** Oct 12, 2026 · **Watch:** NIST SP 800-207 revision.
