# Inclusion review: single-source items

## Verdicts at a glance

Of the 45 single-source items, 27 can go into the merged report as written, 15 need a correction first, 2 should be dropped, and 1 should be rebuilt after the merge. The Claude report's items mostly hold up; the Gemini report's items are mostly legitimate topics carried by an overstated or mischaracterised claim.

| Verdict | Claude-only (of 26) | Gemini-only (of 19) | Meaning |
| --- | --- | --- | --- |
| Include | 22 | 5 | Accurate, in scope; may want a primary citation swapped in |
| Include with correction | 3 | 12 | Topic belongs; a specific claim is wrong, overstated or misattributed |
| Exclude | 0 | 2 | Mischaracterised source or out of scope |
| Rebuild after merge | 1 | 0 | Author synthesis that must be re-derived from the merged content |

Each item was judged on three tests:

- **Legitimate:** the claim matches the best available source, checked by opening it for every 2026 figure, CVE, research paper and standards status.
- **In scope:** it bears on securing web applications, not adjacent fields.
- **Sourced:** primary source (standard, regulator, vendor advisory, peer-reviewed paper) preferred; vendor blogs and Medium posts acceptable only for uncontroversial claims.

The two reports fail in different ways. The Claude report leans on vendor blogs for OWASP lists and leaves several 2026 supply-chain claims uncited in the text; its three errors are figures or labels. The Gemini report cites primary items for its research claims but misreads several of them (WAFBooster, strict-dynamic, Kyverno), and its foundational sections rest on Medium and vendor blogs.

## Claude-only items

Included: 22; with correction: 3 (CL13, CL15, CL18); rebuilt: 1 (CL26). The corrections are one false “first” claim, one misread benchmark figure and one unconfirmed date.

| # | Area | Verdict | Sourcing | Correction or note |
| --- | --- | --- | --- | --- |
| CL1 | Reference stack | Include | Mixed; ASVS counts via Codific and SoftwareMill blogs | Cite the OWASP ASVS repository for 345 / 70 / 17 |
| CL2 | 2025–26 revision log | Include | Mostly primary (NIST, SLSA blog, PCI SSC); SC-081v3 via vendor blogs | Cite the CA/Browser Forum ballot for the certificate schedule |
| CL3 | Cross-cutting principles | Include | Synthesis; “least agency” sourced | None |
| CL4 | Secure SDLC, threat modelling | Include | SSDF primary; method comparison uncited | Label “no method demonstrably superior” as judgement |
| CL5 | Authentication | Include | Strong: NIST SP 800-63B-4 quoted from the PDF; RFC 9700 via oauth.net; PortSwigger for ruby-saml | None |
| CL6 | Session management | Include | Largely uncited, standard practice | Add OWASP Session Management and JWT cheat sheets |
| CL7 | Authorisation detail | Include | CWE movements via BleepingComputer and SiteGuarding; confirmed against SecurityWeek | Cite cwe.mitre.org for Top 25 ranks |
| CL8 | Injection family | Include | PortSwigger top-ten page (primary); CWE ranks confirmed | None |
| CL9 | Client-side attacks | Include | PortSwigger primary; CWE ranks confirmed | None |
| CL10 | Security headers | Include | Uncited table | Add MDN or OWASP Secure Headers Project |
| CL11 | SSRF, cache, host header | Include | AWS Security Blog and EKS docs (primary); PortSwigger | None |
| CL12 | API detail | Include | Vendor blogs for the API Top 10 | Cite owasp.org API Security project |
| CL13 | Cryptography | Include with correction | FIPS, IR 8547 via vendor blog; hybrid deployment cited to two unrelated arXiv papers | Since confirmed: BSI TR-02102-1 version 2026-01 recommends hybrid, so the date stands; the NSA quote matches its April 2024 CNSA 2.0 update; replace the arXiv citations for X25519MLKEM768 deployment |
| CL14 | Business logic and bots | Include | Uncited | Cite Kettle’s single-packet attack research and the OWASP Automated Threats project |
| CL15 | Supply-chain detail | Include with correction | 2026 items uncited in text; all three confirmed (SLSA blog, SecurityWeek, Singapore CSA AD-2026-009) | Mini Shai-Hulud did not produce valid Build L3 provenance. SLSA’s own analysis: attestations were cryptographically valid, but npm provenance is Build L2 and the platform did not meet L3 isolation, which would have blocked the cache-poisoning vector. Drop “first … Build Level 3” |
| CL16 | Security testing | Include | Uncited table, uncontroversial | None |
| CL17 | Errors, logging, privacy | Include | OWASP and NIST primary | None |
| CL18 | AI/LLM and agents | Include with correction | NCSC primary; LLM Top 10 via vendor blogs; Veracode 2025 via press release | Veracode 2026 headline is a 56% average pass rate; 51–53% are model-size averages (large 53%, medium and small 51%), with the top model at 68%. Cite genai.owasp.org for both OWASP lists |
| CL19 | Hardening and patching | Include | KEV counts via SecurityWeek and Cyble | Prefer CISA KEV catalogue data |
| CL20 | Cloud security | Include | DBIR eight-month figure confirmed (SpyCloud summary of DBIR 2026) | Scope it as third-party cloud findings, as the source does |
| CL21 | Containers | Include | kubernetes.io (primary) | None |
| CL22 | Network and edge | Include | PCI 6.4.2 wording via vendor blogs | Cite the PCI DSS v4.0.1 standard |
| CL23 | CI/CD and IaC | Include | Panther, Invicti on Shai-Hulud | None |
| CL24 | Data stores, resilience | Include | Ransomware 48% / 69% confirmed for DBIR 2026 | None |
| CL25 | Detection, IR, privileged access | Include | NIST primary | Label RASP as “contested” judgement |
| CL26 | Compliance and synthesis | Rebuild after merge | Compliance table sourced; matrix, emerging threats and recommendations are author synthesis | Keep the compliance table; re-derive the matrix, emerging-threats list and recommendations from the merged content |

## Gemini-only items

Included: 5; with correction: 12; excluded: 2 (GE12, GE19). Every corrected item names a real mechanism; the fixes are to overstated reach, wrong attribution or outdated premises.

| # | Topic | Verdict | Sourcing | Correction or note |
| --- | --- | --- | --- | --- |
| GE1 | DBIR human element | Include with correction | Keepnet blog; figures confirmed against Verizon’s 2025 executive summary | Label as DBIR 2025 (\~60%); “82%” is DBIR 2022. Drop “behavioral floor” as interpretation |
| GE2 | Edge and VPN exploitation | Include with correction | Confirmed: 22% of exploitation targets, up from 3% (DBIR 2025) | Label edition. “Exposure-centric” prioritisation is Tenable’s framing; attribute it |
| GE3 | Remaining Top 10:2025 categories | Include | Confirmed against top10.owasp.org | None |
| GE4 | NIST SP 800-207 model | Include | NIST SP 800-207A (primary) plus Tetrate and Palo Alto | None |
| GE5 | Sessions vs stateless tokens | Include | Medium and vendor blogs; OWASP JWT cheat sheet | Re-source to OWASP cheat sheets and RFC 9700; drop “industry consensus” |
| GE6 | OAuth Rich Authorization Requests | Include with correction | SecureAuth docs, Medium, Raidiam | RAR is standalone RFC 9396 (May 2023), not part of OAuth 2.1; cite the RFC |
| GE7 | FedCM | Include with correction | Chrome, MDN, W3C (primary) | Chrome did not deprecate third-party cookies; Google’s 17 October 2025 update keeps user choice and continues FedCM. Restate the motive as browser privacy restrictions (Safari, Firefox block by default) |
| GE8 | PQC for passkeys | Include with correction | Single ResearchGate paper | Harvest-now-decrypt-later targets encrypted data, not signatures. The passkey risk is a future quantum computer deriving private keys from stored public keys and forging assertions. One line under cryptography |
| GE9 | TE.TE smuggling | Include | PortSwigger Web Security Academy (primary) | None |
| GE10 | WebSocket hijacking detail | Include with correction | MeshCentral GitHub advisory and PortSwigger (primary) | CVE-2024-26135 confirmed, but the SameSite=Lax bypass needs a same-site attacker (sibling subdomain via takeover or XSS). Query-string tokens leak into logs; prefer a first-message token |
| GE11 | WAFFLED and HTTP-Normalizer | Include | arXiv; peer-reviewed at ACSAC 2025; 1,207 bypasses across AWS, Azure, Cloud Armor, Cloudflare, ModSecurity confirmed | None |
| GE12 | WAFBooster | Exclude | arXiv preprint, not peer-reviewed | Report presents it as an attacker tool; it is a defensive framework that found bypasses and generated rules, raising rejection of mutated payloads from 21% to 96%. Scoring-function detail is too granular for the merged report |
| GE13 | “Ghost Bits” | Include with correction | NSFOCUS vendor blog (30 April 2026) | Disclosed at Black Hat Asia 2026 and tied to Java narrowing conversions; “Node.js” is unsupported. Cite the conference talk (“Cast Attack: A New Threat Posed by Ghost Bits in Java”) |
| GE14 | CSP script gadgets | Include with correction | Google “CSP Is Dead” paper (primary) plus blogs | `strict-dynamic` defeats allow-list and JSONP bypasses but not gadgets; gadgets that create scripts inherit trust under it. Cite Lekies et al., CCS 2017, and point to Trusted Types |
| GE15 | Private State Tokens | Include with correction | MDN only | Formerly “Trust Tokens” (built on the Privacy Pass protocol). Google kept it in the October 2025 retirement; Chromium-only. One line under bot defence |
| GE16 | Serverless warm containers | Include with correction | AWS Lambda best practices (primary) plus vendor blogs | Reuse is within one function’s execution environment: the risk is leakage between requests from different users of the same function, not cross-tenant |
| GE17 | Kubernetes SSRF chain | Include with correction | SANS plus Medium and vendor blogs; Orca for the CVE | Default service accounts are not “highly privileged”; risk comes from added RBAC bindings. Reading the token needs file read (LFI or `file://` SSRF), not plain HTTP SSRF. CVE-2026-4789 needs permission to create namespaced policies and is a different pattern (the Kyverno pod makes the request) |
| GE18 | Client-side field-level encryption | Include with correction | MongoDB community forum thread | Deterministic encryption leaks equality and frequency; state the trade-off. Cite MongoDB documentation |
| GE19 | Zero-knowledge proofs | Exclude | General ZKP surveys and an IoT blockchain paper | No evidence of web-application practice; “trustless, decentralized” framing is off scope. Keep only the PQC handshake-overhead point, sourced to NIST’s presentation, under cryptography |

## Sources opened in this review

- [SLSA blog: Mini Shai-Hulud — what SLSA can and cannot do](https://slsa.dev/blog/2026/05/mini-shai-hulud-what-slsa-can-and-cannot-do) (CL15)
- [SecurityWeek: TeamPCP releases Shai-Hulud worm’s source code](https://securityweek.com/teampcp-ups-the-game-releases-shai-hulud-worms-source-code) (CL15)
- [Singapore CSA advisory AD-2026-009: Keyv and related packages](https://csa.gov.sg/alerts-and-advisories/advisories/ad-2026-009) (CL15)
- [SpyCloud: Top takeaways from the 2026 Verizon DBIR](https://spycloud.com/blog/top-takeaways-from-the-2026-verizon-data-breach-investigations-report/) (CL20, CL24)
- [Veracode: 2026 GenAI Code Security Report finds security stalled at 56% pass rate](https://www.veracode.com/news/llms-are-getting-smarter-but-not-safer-veracode-2026-genai-code-security-report-finds-ai-generated-code-security-has-stalled-at-56%25-pass-rate/) (CL18)
- [PostQuantum.com: Global PQC requirements](https://postquantum.com/cnsa-2-0/global-pqc-requirements/) (CL13)
- [SecurityWeek: MITRE releases 2025 CWE Top 25](https://www.securityweek.com/mitre-releases-2025-list-of-top-25-most-dangerous-software-vulnerabilities/) (CL7, CL8)
- [Verizon 2025 DBIR executive summary](https://www.verizongov.com/resources/reports/2025-dbir-executive-summary.pdf) (GE1, GE2)
- [OWASP Top 10:2025 introduction](https://top10.owasp.org/2025/0x00_2025-Introduction/) (GE3)
- [Google Privacy Sandbox: Update on plans for Privacy Sandbox technologies](https://privacysandbox.google.com/blog/update-on-plans-for-privacy-sandbox-technologies) (GE7, GE15)
- [MeshCentral advisory GHSA-cp68-qrhr-g9h8 (CVE-2024-26135)](https://github.com/Ylianst/MeshCentral/security/advisories/GHSA-cp68-qrhr-g9h8) (GE10)
- [WAFFLED: Exploiting Parsing Discrepancies to Bypass Web Application Firewalls](https://arxiv.org/abs/2503.10846) (GE11)
- [WAFBooster: Automatic Boosting of WAF Security Against Mutated Malicious Payloads](https://arxiv.org/abs/2501.14008) (GE12)
- [NSFOCUS: Ghost Bits attacks](https://nsfocusglobal.com/waf-defense-in-crisis-nsfocus-locks-down-ghost-bits-attacks-in-advance/) (GE13)
- [Truesec: Bypassing modern XSS mitigations with code-reuse attacks](https://www.truesec.com/hub/blog/bypassing-modern-xss-mitigations-with-code-reuse-attacks) (GE14)
- [Orca Security: Kyverno SSRF vulnerability CVE-2026-4789](https://orca.security/resources/blog/kyverno-ssrf-vulnerability-cve-2026-4789/) (GE17)
