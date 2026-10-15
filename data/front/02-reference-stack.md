# Reference stack


The standards behind this catalogue do different jobs, and confusing them is a common architectural error. A risk list sets priorities; a verification standard states testable requirements; a process framework governs how the organisation builds software. Editions below are the only place in the catalogue where they are stated.

| Job | Standard | Use it for | Not for | Current edition | Fact |
| --- | --- | --- | --- | --- | --- |
| Weakness taxonomy | MITRE CWE, CWE Top 25 | Naming root-cause defect classes | Controls | Top 25: 2025 list | F-17 |
| Risk ranking | OWASP Top 10 | Awareness and prioritisation | Testable requirements | 2025 | F-5 |
| Domain risk lists | OWASP API Security Top 10; Top 10 for LLM Applications; Top 10 for Agentic Applications | Risks specific to APIs, LLM features and agents | Substitutes for ASVS | API 2023; LLM 2025; Agentic 2026 | F-7, F-8, F-9 |
| Verifiable requirements | OWASP ASVS | Requirements a spec can cite and a tester can verify, by level L1–L3 | Process; infrastructure | 5.0.0 | F-6 |
| Secure development process | NIST SSDF (SP 800-218); OWASP SAMM | Organisational SDLC practice (P1–P4) | Application-level controls | SSDF v1.1, v1.2 in draft | F-11 |
| Enterprise controls | NIST SP 800-53; ISO/IEC 27001 | Organisation-wide control catalogues and audit | Web-specific detail | 800-53 Release 5.2.0; ISO/IEC 27001:2022 | F-12 |
| Identity assurance | NIST SP 800-63 | Authenticator and federation assurance levels (A1) | Authorisation | 800-63-4 | F-10 |
| Protocol specifications | IETF RFCs (OAuth, HTTP, TLS); W3C and WHATWG (CSP, Fetch, WebAuthn) | Normative protocol behaviour | Threat models | OAuth security: RFC 9700; OAuth 2.1 in draft | F-13, F-14 |
| Supply-chain integrity | SLSA | Build and source provenance levels (A11) | Proof that source is benign | v1.2 | F-15 |
| Payment card security | PCI DSS | Mandatory controls for cardholder-data environments | Non-payment scope | v4.0.1 | F-16 |
| Exploitation evidence | CISA KEV; Verizon DBIR; PortSwigger research | What is being exploited and how | Exhaustive coverage | Continuous; annual | F-20 to F-26 |

The path from defect to assurance runs through these layers:

1. CWE names the defect.
2. The Top 10 groups defects into risks.
3. ASVS states the requirement that prevents it.
4. Testing verifies the requirement (P2).
5. SSDF and SAMM make the practice repeatable.

ASVS 5.0 dropped its direct CWE and NIST mappings, so cross-walks between these layers are approximate.

**Facts and sources.** Facts: F-5 to F-17. Sources: R-2, R-4, R-5, R-10 to R-20, R-28.

**Last reviewed** Oct 12, 2026 · **Watch:** OAuth 2.1 published as an RFC; SSDF v1.2 final; NIST IR 8547 final; next OWASP Top 10, API Security Top 10 or ASVS release; PCI DSS v5.
