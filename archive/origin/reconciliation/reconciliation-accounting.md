# Web Application Security: Cross-Report Reconciliation

Oct 12, 2026 · @John Siegrist

## Scope and method

This is an accounting of where two research reports agree, conflict, or cover different ground. No discrepancy is adjudicated here; correctness is the next step.

| Label used here | Title | Shape | Citations |
| --- | --- | --- | --- |
| Claude report | Web Application Security: A Vendor-Neutral Taxonomy of Requirements, Threats and Mitigations (October 2026) | \~25 control areas, each as requirements · threats · mitigations; summary matrix; expert-disagreement section; recommendations; caveats | 88 |
| Gemini report | The Architecture of Web Application Security: A Comprehensive Analysis of Threats, Vulnerabilities, and Mitigations | 10 narrative sections with selected deep dives; no recommendations, matrix or caveats | 110 |

Claims were compared at the level of a single assertion. Each falls into one of four buckets:

- **Consensus:** both reports state compatible positions, even if at different depth.
- **Disagreement:** the reports give conflicting figures, conflicting descriptions of the same standard, or materially different strength of claim about the same control.
- **Claude-only / Gemini-only:** one report covers a topic the other omits or mentions only in passing.

## At a glance

The reports agree on 25 points and conflict on 11. The Claude report covers 26 areas the Gemini report omits; the Gemini report covers 19 topics the Claude report omits.

| Bucket | Count | Headline items |
| --- | --- | --- |
| Consensus | 25 | Exploitation now leads initial access; OWASP Top 10:2025 structure; authorisation failures dominate; request smuggling, CSP and WAF-bypass mechanics; passkeys; IMDSv2; SLSA; PQC hybrid key exchange |
| Disagreement | 11 | 3 conflicting figures (DBIR shares); 4 conflicting descriptions of a standard (ASVS chapters, SLSA levels, PCI DSS SRI, OAuth 2.1); 4 differences in strength of claim (IMDSv2, passkeys, object references, hybrid PQC) |
| Claude-only | 26 areas | Entire AI/LLM/agent area; authentication protocol detail (RFC 9700, NIST 800-63-4, SAML); injection family; browser headers; business logic and bots; testing; cloud, CI/CD, edge, data, detection, privileged access; compliance; recommendations |
| Gemini-only | 19 topics | NIST SP 800-207 component model; FedCM; OAuth RAR; WAF-evasion research (WAFFLED, WAFBooster, Ghost Bits); CSP script gadgets; Private State Tokens; serverless warm-container leakage; Kubernetes SSRF-to-API chain; zero-knowledge proofs |

The structural difference drives most of the coverage gaps. The Claude report is a breadth-first taxonomy; the Gemini report goes deep on about eight mechanisms and leaves whole areas untouched, including AI/LLM security, despite opening with AI-accelerated exploitation. The Claude report records expert dissent explicitly; the Gemini report mostly presents single positions, several framed as “industry consensus”, which is where the strength-of-claim disagreements come from.

## Consensus

Both reports hold these 25 positions. The third column records non-conflicting differences in depth or detail; where the shared position carries a conflicting figure or qualifier, the disagreement number points to it.

| # | Topic | Shared position | Depth / detail difference |
| --- | --- | --- | --- |
| C1 | Breach trends (DBIR) | Vulnerability exploitation has overtaken stolen credentials as the leading initial access vector | Shares and scope differ: see D1 |
| C2 | Patch latency | Median time to patch rose from 32 to 43 days | Gemini qualifies it as “critical vulnerabilities”; Claude does not |
| C3 | AI and exploitation | AI is compressing time from disclosure to exploit | Gemini says “within hours”; Claude cites DBIR without a figure |
| C4 | OWASP Top 10:2025 | A01 Broken Access Control (SSRF folded in), A02 Security Misconfiguration, A03 Software Supply Chain Failures, A05 Injection, A06 Insecure Design, A09 Logging & Alerting Failures, A10 Mishandling of Exceptional Conditions | Gemini also names A04, A07, A08 and maps 2021→2025; Claude gives CWE counts per category |
| C5 | Access control | Deny by default, enforced server-side; automated tools largely cannot detect broken object-level access | Remedies differ in emphasis: see D9 |
| C6 | Fine-grained authorisation | Relationship-based access control (Zanzibar-style graphs) for per-object sharing | Gemini goes deep (OpenFGA, tuple model); Claude lists it beside RBAC and ABAC |
| C7 | ASVS 5.0.0 | 17 chapters, levels L1–L3, V10 OAuth and OIDC, V17 WebRTC | Other chapter numbers conflict: see D4 |
| C8 | OWASP API Top 10 (2023) | Still current; BOLA, BFLA, BOPLA (merging mass assignment and excessive data exposure), API10 Unsafe Consumption | Claude lists all ten plus gRPC; Gemini details four with attack examples |
| C9 | GraphQL | Depth limits plus query cost analysis against resource-exhaustion DoS | Gemini explains AST cost scoring; Claude adds introspection and batching |
| C10 | JWTs | Algorithm confusion and `alg: none` are core pitfalls; short-lived tokens need a revocation path | Gemini frames 15-minute access tokens plus rotating refresh tokens as “industry consensus”; Claude lists that among options, with DPoP |
| C11 | Passkeys | WebAuthn/FIDO2 passkeys are phishing-resistant; syncing moves the trust boundary to the cloud account | Strength of claim differs: see D8 |
| C12 | Request smuggling | CL.TE, TE.CL and HTTP/2 downgrade variants; mitigate with end-to-end HTTP/2 and rejection of ambiguous requests | Gemini adds TE.TE; Claude adds the contested call to retire HTTP/1.1 upstreams |
| C13 | Cross-site WebSocket hijacking | Validate `Origin` on the upgrade handshake | Gemini goes deep (CVE, SameSite bypass, token-based handshake); Claude is one line |
| C14 | WAF bypass | Parser differentials and Unicode normalisation defeat WAFs; normalise at ingress and keep parameterisation behind the WAF | Gemini details named research; Claude frames the WAF as a compensating control |
| C15 | Content Security Policy | Allow-list CSPs are bypassable; use nonce/hash with `strict-dynamic` | Gemini adds script gadgets and JSONP; Claude adds Trusted Types |
| C16 | PCI DSS 6.4.3 / 11.6.1 | Payment-page scripts in scope: inventory, authorisation, integrity, tamper detection | SRI scope and version differ: see D6 |
| C17 | Cloud metadata SSRF | IMDSv2’s PUT-issued session token defends against SSRF credential theft | Strength of claim differs: see D7 |
| C18 | Kubernetes | Automounted service-account tokens plus over-broad RBAC form an escalation path | Gemini walks the full SSRF-to-API chain; Claude lists “no automounted tokens” as a control |
| C19 | Serverless | Event-data injection and over-privileged function roles | Gemini adds warm-container leakage; Claude adds denial of wallet and budget limits |
| C20 | Supply-chain threats | Dependency confusion, typosquatting, CI/CD compromise; Shai-Hulud npm worm as reference case | Claude gives wave-by-wave figures; Gemini names it once |
| C21 | SLSA | Build levels as the provenance framework | Level definitions conflict: see D5 |
| C22 | Software composition analysis | Reachability analysis cuts false positives from unused vulnerable code | Gemini explains call-graph method; Claude names it |
| C23 | Post-quantum cryptography | NIST standards finalised; harvest-now-decrypt-later is the driver; hybrid key exchange in TLS | Whether hybrid is required differs: see D10 |
| C24 | Field-level encryption | Encrypt sensitive fields beyond storage-level encryption | Gemini goes deep (client-side, deterministic, queryable); Claude names it |
| C25 | Zero trust | Authenticate and authorise every hop, including service-to-service | Gemini details NIST SP 800-207 components; Claude states it as a principle |

## Disagreements

The reports conflict on 11 points: three figures, four descriptions of a standard, and four differences in how strongly a control is claimed to work. Each row states both positions as written; none is resolved here.

| # | Topic | Type | Claude report | Gemini report |
| --- | --- | --- | --- | --- |
| D1 | Exploitation as initial access vector | Figure and scope | 31% of breaches (2026 DBIR); top vector overall, first time in the report’s 19-year history | 20% in 2025, up 34% year on year; overtaking stolen credentials “in specific sectors” (table) yet “the premier initial access vector” (text) |
| D2 | Third-party share of breaches | Figure | 48%, up 60% (2026 DBIR) | 30% in 2025, doubled from 15% in 2024 |
| D3 | Ransomware (DBIR) | Figure | Present in 48% of breaches; 69% of victims did not pay | Present in 44% of breaches; 64% refused to pay |
| D4 | ASVS 5.0.0 chapter numbering | Standard description | V1 frames encoding and sanitisation; V3 Web Frontend Security; V9 Self-contained Tokens; V14 Data Protection; V16 Security Logging and Error Handling | V1 Architecture, Design and Threat Modeling; V2 Authentication; V3 Session Management; V5 File Handling |
| D5 | SLSA build levels | Standard description | L1 provenance exists; L2 signed provenance from a hosted platform; L3 hardened, isolated builds. SBOMs are separate from provenance. Provenance does not prove benign source (Mini Shai-Hulud produced valid L3 attestations) | L1 “unverified provenance data (such as a Software Bill of Materials)”; L2 “prevents insider tampering and rogue uploads”; L3 adds “fully reproducible” builds and “guarantees” tamper resistance. No version cited; adds L0 |
| D6 | PCI DSS script integrity | Standard description | v4.0.1, mandatory from 31 March 2025; SRI for static scripts, noted as ineffective for legitimately changing third-party tags; SAQ A eligibility change (January 2025) | v4.0; “every script must be pinned to a known-good cryptographic hash using SRI” under 6.4.3 |
| D7 | IMDSv2 effectiveness | Strength of claim | One layer alongside destination allow-lists, egress proxies, redirect re-validation and hop limit 1; quotes AWS on protecting against unpatched SSRF | “Effectively neutralizes standard SSRF attacks” because SSRF payloads cannot issue PUT requests or custom headers |
| D8 | Passkey protection | Strength of claim | Phishing-resistant per NIST; no web-layer control fully defeats session-cookie theft by infostealers; recovery can become the real authentication | “Immune to traditional credential harvesting, adversary-in-the-middle (AitM) attacks, and phishing” |
| D9 | Broken access control remedy | Strength of claim | RBAC for coarse function access only, ABAC/ReBAC for object rules; unguessable IDs are defence in depth only | Broken access control “necessitat\[es\] strict RBAC and indirect object references” |
| D10 | Hybrid post-quantum key exchange | Strength of claim | NIST and Germany’s BSI endorse hybrid; the NSA (CNSA 2.0) does not require it and mandates pure ML-KEM-1024 / ML-DSA-87; NIST IR 8547 dates are draft | Web architecture “must transition” TLS 1.3 to hybrid models; no dissent noted |
| D11 | OAuth 2.1 status | Standard description | OAuth 2.1 “remains an Internet-Draft”; RFC 9700 is the operative security guidance | “OAuth 2.1 introduces Rich Authorization Requests (RAR) via RFC 9396” |

The three figure conflicts may partly reflect different DBIR editions. The Gemini report labels its table “2025 / 2026” and cites a mix of 2025 and 2026 secondary summaries; the Claude report attributes its figures to the 2026 edition. For D2, the two numbers are arithmetically consistent with successive editions (30% × 1.6 = 48%), but neither report states the other’s figure.

## Covered only in the Claude report

The Claude report covers 26 areas or sub-topics the Gemini report omits. The largest gap is AI/LLM security, which the Gemini report does not address at all.

| # | Area | Topics absent from the Gemini report |
| --- | --- | --- |
| CL1 | Reference stack | Roles of CWE, CAPEC, ATT&CK, SAMM, NIST SSDF, SP 800-53, ISO/IEC 27001, SP 800-63, IETF/W3C specs, CISA KEV; ASVS 5.0 counts (345 requirements, 70 at L1) and its move to CRE linkage |
| CL2 | 2025–26 revision log | NIST SP 800-63-4 final; SSDF v1.2 draft; SP 800-53 Rel. 5.2.0; RFC 9700; SLSA v1.1 and v1.2 Source track; CA/Browser Forum SC-081v3; OWASP Agentic Top 10 |
| CL3 | Cross-cutting principles | Complete mediation, least agency, defence in depth, code/data separation, fail-closed, parser consistency, verifiability |
| CL4 | Secure SDLC and threat modelling | SSDF practice groups, SAMM, STRIDE, PASTA, attack trees; “no method demonstrably superior” |
| CL5 | Authentication | NIST 800-63B-4 positions (OTP and push not phishing-resistant; no composition or rotation rules); AAL1–3; account recovery; RFC 9700 controls (PKCE, exact redirect match, DPoP/mTLS, RFC 9207); SAML signature wrapping and ruby-saml CVEs; infostealers; MFA fatigue; SIM swap |
| CL6 | Session management | Cookie attributes and `__Host-` prefix; `kid`/`jku` injection; device-bound session credentials; CSRF defences |
| CL7 | Authorisation detail | ABAC; tenant ID from principal enforced at data layer (row-level security); DTO allow-lists; CWE Top 25 2025 authorisation movements; role × endpoint test matrices; formal policy specification |
| CL8 | Injection family | SSTI, ORM leaks, XXE, insecure deserialisation, path traversal, file upload, NoSQL, LDAP; CWE Top 25 ranks; PortSwigger 2025 top ten techniques |
| CL9 | Client-side attacks | XSS and CSRF rankings; clickjacking; open redirects into OAuth; prototype pollution; CORS misconfiguration; `postMessage`; DOM clobbering; XS-Leaks; Trusted Types; Fetch Metadata |
| CL10 | Security headers | HSTS, SRI limits, COOP/COEP/CORP, Permissions-Policy, `nosniff`, Referrer-Policy |
| CL11 | SSRF, cache and host header | SSRF egress controls and anti-rebinding; web cache poisoning and deception as distinct topics; host-header attacks; contested HTTP/1.1 retirement |
| CL12 | API detail | API2, API4, API6–API9; gRPC reflection; gateways not as sole authorisation; API inventory |
| CL13 | Cryptography | TLS versions; AEAD ciphers; password KDFs; KMS and secrets managers; certificate lifetime cuts to 47 days by 2029; FIPS 203–205; NIST IR 8547 deprecation dates; NSA vs BSI hybrid dispute |
| CL14 | Business logic and bots | State machines, race conditions, single-packet attacks, idempotency; OWASP Automated Threats catalogue; bot defence as an arms race |
| CL15 | Supply-chain detail | Shai-Hulud wave figures; Mini Shai-Hulud forging valid SLSA L3 provenance; public release of worm source; cool-down policies; trusted publishing; malicious IDE and AI extensions |
| CL16 | Security testing | SAST, SCA, DAST, IAST, fuzzing, manual review, pen testing, bug bounty: what each finds and misses |
| CL17 | Errors, logging, privacy | Fail-closed handlers; log injection; redaction; GDPR Art. 25/35; ASVS V14 and V16 |
| CL18 | AI/LLM and agents | OWASP LLM Top 10 (2025); OWASP Agentic Top 10 (2026); UK NCSC on prompt injection never fully mitigable; Veracode AI-code figures; slopsquatting; SP 800-218A |
| CL19 | Hardening and patching | KEV 2025 counts; KEV → EPSS → CVSS prioritisation; WAF virtual patching as stopgap |
| CL20 | Cloud security | Workload identity federation; guardrails; CSPM/CNAPP; DBIR eight-month remediation figure; shared-responsibility blur in PaaS/SaaS |
| CL21 | Containers | Pod Security Standards; IngressNightmare (CVE-2025-1974); sandboxed runtimes; NetworkPolicies |
| CL22 | Network and edge | DDoS; origin bypass; subdomain takeover; DNSSEC and CAA; PCI DSS 6.4.2 WAF requirement |
| CL23 | CI/CD and IaC | Poisoned pipeline execution; SHA-pinned actions; OIDC short-lived credentials; ephemeral runners; credential rotation after compromise |
| CL24 | Data stores and resilience | Exposed databases; immutable backups and restore drills; resource-exhaustion limits; SA-24 cyber resiliency |
| CL25 | Detection, IR, privileged access | SIEM and ATT&CK mapping; RASP; SP 800-61; root-cause analysis; PAM, just-in-time elevation, privileged access workstations |
| CL26 | Compliance and synthesis | Compliance landscape (GDPR, ISO 27001, SOC 2, CISA Secure by Design, EU CRA); summary matrix with completeness ratings; emerging threats; expert-disagreement section; ten recommendations; caveats |

## Covered only in the Gemini report

The Gemini report covers 19 topics the Claude report omits or names only in passing. Most are deeper treatments of mechanisms, plus a few technologies the Claude report does not mention at all (FedCM, OAuth RAR, Private State Tokens, zero-knowledge proofs).

| # | Topic | What the Gemini report says |
| --- | --- | --- |
| GE1 | DBIR human element | Human factor in 60% of breaches in 2025 (82% historically); phishing susceptibility at a “behavioral floor” |
| GE2 | Edge and VPN exploitation | Eightfold increase in exploitation; argues for exposure-centric prioritisation by asset exposure and attack path |
| GE3 | OWASP Top 10 remaining categories | A04 Cryptographic Failures, A07 Authentication Failures, A08 Software or Data Integrity Failures; 2021→2025 mapping; A05 includes XSS; A10 covers CWE-209 and CWE-636 |
| GE4 | NIST SP 800-207 zero-trust model | Policy Engine, Policy Administrator, Policy Enforcement Point; control/data plane split; OAuth tokens exchanged at the edge for internal JWTs |
| GE5 | Sessions vs stateless tokens | Trade-off analysis: instant revocation vs latency; JWT blocklists reintroduce the state JWTs avoid |
| GE6 | OAuth Rich Authorization Requests | RFC 9396 `authorization_details` for transaction-specific consent (e.g. a single payment) instead of broad scopes |
| GE7 | FedCM | Third-party cookie deprecation breaks iframe-based SSO; W3C FedCM moves the federation trust decision into the browser |
| GE8 | PQC for passkeys | Long-lived FIDO2 key material exposed to harvest-now-decrypt-later; FIDO2 ecosystem must transition to PQC |
| GE9 | TE.TE smuggling | Obfuscated Transfer-Encoding variant; smuggling consequences (cookie capture, cache poisoning, open redirects) |
| GE10 | WebSocket hijacking detail | Browsers apply no same-origin policy to WebSockets; CVE-2024-26135 (MeshCentral) bypassed SameSite=Lax; pass a token in the handshake or first message |
| GE11 | WAFFLED and HTTP-Normalizer | Academic WAF fuzzing found 1,200+ bypasses via multipart, XML and JSON parsing; ingress RFC-compliance normalisation as mitigation |
| GE12 | WAFBooster | ML shadow models and delete/replace/head-tail scoring to mutate payloads past WAF semantics |
| GE13 | “Ghost Bits” | Narrowing conversions in Java/Node.js truncate high-order bytes, turning WAF-benign Unicode into ASCII payloads |
| GE14 | CSP script gadgets | Legitimate library code (AngularJS, jQuery) executes injected markup under a nonced CSP; JSONP bypasses allow-lists |
| GE15 | Private State Tokens | Blind-signature tokens (formerly Privacy Pass) for anti-bot trust across origins without tracking |
| GE16 | Serverless warm containers | Reused execution environments leak state in globals or `/tmp` across invocations; four-vector attack surface |
| GE17 | Kubernetes SSRF chain | SSRF reads the mounted service-account token and calls the in-cluster API server; CVE-2026-4789 (Kyverno) |
| GE18 | Client-side field-level encryption | Encrypt on the client before transmission; deterministic encryption allows exact-match queries |
| GE19 | Zero-knowledge proofs | zk-SNARKs, zk-STARKs, MPC-in-the-Head compared by trusted setup, PQ security and proof size; PQC adds bandwidth and latency overhead |
