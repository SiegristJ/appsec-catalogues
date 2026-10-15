# Disagreement decisions

## Decisions at a glance

Seven disagreements are settled by primary sources: three were edition mismatches, and four go to the Claude report. Of the four strength-of-claim disagreements, one has a material error (D9, adopting the Claude report’s position). The other three are presented as dual positions.

| # | Topic | Kind | Verdict | Merged report says |
| --- | --- | --- | --- | --- |
| D1 | Exploitation as initial access vector | Figure | Both figures right for their edition; Gemini misdates the overtaking | 20% (DBIR 2025, second to credential abuse) → 31% (DBIR 2026, top vector) |
| D2 | Third-party share | Figure | Both right for their edition | 15% (2024) → 30% (2025) → 48% (2026) |
| D3 | Ransomware | Figure | Both right for their edition | 44% / 64% unpaid (2025) → 48% / 69% (2026) |
| D4 | ASVS 5.0 chapter numbering | Standard | Claude correct; Gemini’s V1–V3 are ASVS 4.0.3 names | ASVS 5.0 chapter list as published |
| D5 | SLSA build levels | Standard | Claude correct | No SBOM at L1, no reproducibility at L3 |
| D6 | PCI DSS script integrity | Standard | Claude correct | “A method” to assure integrity; SRI is one option. Version 4.0.1 |
| D7 | IMDSv2 effectiveness | Strength of claim | No material error → dual position | Highly effective against typical SSRF; full-request SSRF can still reach it |
| D8 | Passkey protection | Strength of claim | No material error → dual position | Credential cannot be phished; account remains exposed through fallbacks and session theft |
| D9 | Broken access control remedy | Strength of claim | Material error in Gemini claim → Claude position | Per-object authorisation check is the fix; indirect IDs are defence in depth |
| D10 | Hybrid post-quantum key exchange | Strength of claim | Expert dispute → dual position | NIST and BSI favour hybrid; NSA does not require it for national security systems |
| D11 | OAuth 2.1 status | Standard | Claude correct | OAuth 2.1 is still a draft; RAR is standalone RFC 9396 |

Three rules applied:

1. **Source ranking:** standard or issuing body first, then peer-reviewed work, then reputable secondary sources. The first level that answers decides.
2. **Strength-of-claim disagreements** stand as dual positions unless one side contradicts an authoritative source or omits the operative control.
3. **Independence:** the Claude report is one of the two under review, so every verdict below links to the source that decides it and can be audited without trusting this analysis.

## Figures (D1–D3)

All three figure conflicts are edition mismatches: the Gemini report quotes DBIR 2025, the Claude report DBIR 2026, and both quote correctly. The merged report gives 2026 as the figure of record and 2025 as the trend.

**D1 · Exploitation as initial access vector.**

- *Question:* What share of breaches began with exploitation, and when did it overtake credential abuse?
- *Evidence:* Verizon’s 2025 executive summary gives 20%, up 34%, with credential abuse “still” the most common vector. The DBIR 2026 summaries give 31%, up 55%, now the top vector.
- *Verdict:* Both figures correct for their edition. The Gemini report errs in presenting exploitation as “the premier initial access vector” under a 2025/2026 label and in “specific sectors”. The 2025 report makes no sector claim; its nearest statement is that espionage-motivated breaches began with exploitation 70% of the time.
- *Merged wording:* Exploitation rose from 20% of breaches (DBIR 2025, second to credential abuse) to 31% (DBIR 2026), overtaking credential abuse for the first time.

**D2 · Third-party share.**

- *Evidence:* 30%, doubled from 15% (DBIR 2025 executive summary); 48%, up 60% (DBIR 2026 summaries).
- *Verdict:* Both correct; the figures chain (30% × 1.6 = 48%).
- *Merged wording:* Third-party involvement rose from 15% of breaches to 30% (DBIR 2025) and 48% (DBIR 2026).

**D3 · Ransomware.**

- *Evidence:* 44% of breaches, 64% of victims not paying (DBIR 2025); 48% and 69% (DBIR 2026).
- *Verdict:* Both correct.
- *Merged wording:* Ransomware featured in 48% of breaches in DBIR 2026 (44% in 2025), while the share of victims refusing to pay rose to 69% (64%).

## Standards (D4, D5, D6, D11)

The issuing bodies’ own texts settle all four, each in the Claude report’s favour. The Gemini report’s errors come from older versions (ASVS 4.0.3, PCI DSS 4.0) or from vendor summaries that add requirements the standards do not contain.

**D4 · ASVS 5.0 chapter numbering.**

- *Evidence:* The OWASP Cheat Sheet Series ASVS index, based on version 5.0.x, lists V1 Encoding and Sanitization, V2 Validation and Business Logic, V3 Web Frontend Security, V4 API and Web Service, V5 File Handling, V6 Authentication, V7 Session Management, V8 Authorization, V9 Self-contained Tokens, V10 OAuth and OIDC, V11 Cryptography, V12 Secure Communication, V13 Configuration, V14 Data Protection, V15 Secure Coding and Architecture, V16 Security Logging and Error Handling, V17 WebRTC.
- *Verdict:* Claude correct. Gemini’s V5 File Handling is right, but its V1 Architecture, V2 Authentication and V3 Session Management are ASVS 4.0.3 chapter names.
- *Merged wording:* Use the 5.0 list above. Architecture now sits in V15 and session management in V7.

**D5 · SLSA build levels.**

- *Evidence:* SLSA v1.1 levels page. L1 requires automatically generated provenance; L2 requires a hosted platform that generates and signs it; L3 requires controls that stop runs influencing one another and keep signing secrets from user build steps. SBOMs appear nowhere in the levels. Reproducible builds appear only as an optional verification route at L2 and an ecosystem choice.
- *Verdict:* Claude correct. The Gemini report adds an SBOM to L1 and reproducibility to L3, and its “guarantees” overstates what the spec promises. Its Build L0 is legitimate.
- *Merged wording:* State the three levels as the spec does; treat SBOMs as a separate inventory artefact; note that provenance records how something was built, not that its source is benign.

**D6 · PCI DSS script integrity.**

- *Evidence:* Requirement 6.4.3 reads “A method is implemented to assure the integrity of each script” (quoted in Adyen’s PCI DSS compliance guide). v4.0.1 is the current version, and its future-dated requirements became mandatory on 31 March 2025.
- *Verdict:* Claude correct. SRI is one acceptable method, not a mandate. The Gemini report’s “every script must be pinned … using SRI” misstates the requirement, and its “version 4.0” is superseded, though the requirement numbers carry over.
- *Merged wording:* PCI DSS v4.0.1 requires a method to assure each script’s integrity. SRI suits static scripts; legitimately changing third-party tags need other methods, such as CSP allow-listing with change detection.

**D11 · OAuth 2.1 status.**

- *Evidence:* IETF Datatracker shows draft-ietf-oauth-v2-1-16 (3 September 2026) as a working-group Internet-Draft, with IESG submission planned for December 2026. RFC 9396 (Rich Authorization Requests) was published separately in May 2023.
- *Verdict:* Claude correct. OAuth 2.1 neither is an RFC nor “introduces” RAR.
- *Merged wording:* OAuth 2.1 remains a draft consolidating current practice; RFC 9700 is the operative security guidance; RAR (RFC 9396) is a standalone extension usable with OAuth 2.0.

## Strength of claim (D7–D10)

The merged report presents D7, D8 and D10 as dual positions; D9 alone has a material error. The test for material error: does the claim contradict an authoritative source, or does it omit the control that source names as operative? A stronger or weaker emphasis that stays within the evidence does not qualify.

**D7 · IMDSv2 effectiveness — dual position.**

- *Positions:* The Gemini report says IMDSv2 “effectively neutralizes standard SSRF attacks” because typical SSRF cannot issue a PUT with a custom header. The Claude report treats it as one layer, alongside egress allow-lists and hop limits.
- *Material-error check:* None. AppCheck’s research calls IMDSv2 greatly effective at mitigating SSRF, and the Gemini claim is scoped to “standard” SSRF. AppCheck also shows that an SSRF controlling the full request (here, a TLS-terminating proxy on the instance that adds no `X-Forwarded-For`) still obtains a token. That supports the Claude report’s layering without falsifying the Gemini claim.
- *Merged wording:* IMDSv2 defeats SSRF that controls only a URL, which is the common case. SSRF that controls the method and headers, such as a misconfigured on-host proxy, can still reach it, so egress controls and least-privilege instance roles remain necessary.

**D8 · Passkey protection — dual position.**

- *Positions:* The Gemini report calls passkeys “immune” to credential harvesting, adversary-in-the-middle and phishing. The Claude report says they are phishing-resistant, but session cookies remain stealable by infostealers and recovery can become the effective authentication.
- *Material-error check:* None. Proofpoint’s 2025 downgrade attack (spoofing an unsupported browser so Microsoft Entra ID falls back to a phishable method, captured through Evilginx) side-steps the passkey without breaking it, and had not been seen in the wild. The Gemini claim holds for the credential; the Claude report’s caveats hold for the account.
- *Merged wording:* A passkey cannot be phished or replayed through a proxy. Accounts that keep weaker fallbacks, or whose sessions are stolen after login, stay exposed. Retire phishable fallbacks and protect sessions separately.

**D9 · Broken access control remedy — material error, Claude position adopted.**

- *Positions:* The Gemini report says broken access control “necessitat\[es\] strict RBAC and indirect object references.” The Claude report puts per-object server-side checks first, with RBAC for coarse function access and unguessable IDs as defence in depth.
- *Material-error check:* Yes. The OWASP IDOR Prevention Cheat Sheet names per-object access checks as the mitigation and random identifiers as “an additional defense-in-depth measure”, adding that “even with complex identifiers, access control checks are essential.” The Gemini prescription omits the operative control: RBAC decides what a role may do, not which objects a user owns. It also elevates a defence-in-depth measure to a necessity. Its own BOLA description elsewhere does state the per-object check, so the error is confined to this claim.
- *Merged wording:* The fix is an authorisation check on every object access, tied to the authenticated principal. RBAC covers function-level access; indirect or random identifiers add defence in depth but never replace the check.

**D10 · Hybrid post-quantum key exchange — expert dispute, dual position.**

- *Positions:* The Gemini report says TLS 1.3 “must transition” to hybrid. The Claude report records NIST and BSI favouring hybrid against the NSA’s CNSA 2.0, which does not require it.
- *Material-error check:* None. Both describe real positions; the Gemini report omits the dissent. BSI requires hybrid deployment of lattice-based PQC (except hash-based signatures) because lattice schemes have had less cryptanalytic scrutiny. The NSA targets pure CNSA 2.0 algorithms by its exclusive-use dates.
- *Merged wording:* Hybrid key exchange is the common transition path and BSI’s requirement. US national security systems follow CNSA 2.0, which targets pure ML-KEM-1024 and does not require hybrid. Organisations should follow the regime that governs them. *Sourcing (checked): the NSA’s April 2024 CNSA 2.0 update says it “will not require NSS developers to use hybrid certified products,” while allowing hybrid where CNSA 1.0 algorithms cannot yet be replaced (PQShield summary). BSI TR-02102-1 version 2026-01 recommends hybrid implementations and drops classical-only key agreement after 2031.*

## Sources

- [Verizon 2025 DBIR executive summary](https://www.verizongov.com/resources/reports/2025-dbir-executive-summary.pdf) (D1–D3)
- [SpyCloud: Top takeaways from the 2026 DBIR](https://spycloud.com/blog/top-takeaways-from-the-2026-verizon-data-breach-investigations-report/) (D1–D3)
- [Tenable: Key findings from the Verizon DBIR 2026](https://connect.tenable.com/discussions/vulnerability-watch/key-findings-from-the-verizon-dbir-2026-slower-vulnerability-remediation-meets-f/111972) (D1)
- [OWASP Cheat Sheet Series: ASVS 5.0 index](https://cheatsheetseries.owasp.org/IndexASVS.html) (D4)
- [SLSA v1.1: Security levels](https://slsa.dev/spec/v1.1/levels) (D5)
- [Adyen: PCI DSS script security (6.4.3 text)](https://docs.adyen.com/development-resources/pci-dss-compliance-guide/script-security) (D6)
- [IETF Datatracker: draft-ietf-oauth-v2-1](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) (D11)
- [AppCheck: Exploiting SNI SSRF to access AWS IMDSv2](https://appcheck-ng.com/exploiting-sni-ssrf-to-access-the-aws-idmsv2-service/) (D7)
- [SecurityBrief: Proofpoint warns FIDO authentication can be bypassed by downgrade](https://securitybrief.co.uk/story/proofpoint-warns-fido-authentication-can-be-bypassed-by-downgrade) (D8)
- [OWASP IDOR Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html) (D9)
- [PostQuantum.com: Global PQC requirements](https://postquantum.com/cnsa-2-0/global-pqc-requirements/) (D10)
