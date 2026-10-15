# Web Application Security: A Vendor-Neutral Taxonomy of Requirements, Threats and Mitigations (October 2026)

Web application security is best treated as about 25 distinct control areas across design, code, runtime, supply chain and hosting. Authorization failures, misconfiguration and supply-chain compromise now dominate the evidence base. Exploitation of known vulnerabilities has overtaken stolen credentials as the leading breach entry point. This makes patch latency, dependency integrity and object-level access control the highest-leverage investments, ahead of the classic injection defences, which are largely solved structurally.

## TL;DR

- **Where the risk is (2025–26 evidence):** OWASP Top 10:2025 keeps Broken Access Control at #1, now with SSRF folded in. Security Misconfiguration rises to #2 and the new Software Supply Chain Failures category enters at #3. The 2026 Verizon DBIR finds vulnerability exploitation is the top initial access vector (31% of breaches), the first time in the report's 19-year history. Third-party involvement is up 60% to 48% of breaches.
- **What "standard" mitigation looks like:** ASVS 5.0 as the requirements baseline and SSDF/SAMM for process; server-side, deny-by-default, per-object authorization; phishing-resistant authentication (WebAuthn/passkeys, per NIST SP 800-63-4); RFC 9700 OAuth hygiene; parameterised and contextually encoded data handling; strict CSP with Trusted Types; dependency provenance via SBOM, SLSA and signing; KEV-driven patch deadlines; least-privilege cloud IAM with IMDSv2 against SSRF.
- **Where mitigations are only partial:** prompt injection (the UK NCSC says it "may never be totally mitigated"), business-logic abuse and bots, request smuggling over HTTP/1.1 upstreams, XS-Leaks, malicious packages in public registries, and AI-generated code (Veracode's 2025 GenAI Code Security Report, testing over 100 LLMs on 80 coding tasks, found "only 55% of AI-generated code was secure"). For these, design for blast-radius reduction and detection rather than prevention.

---

## 1. How the domain is framed: the reference stack

The authoritative sources have different jobs. Confusing them is a common architectural error.

| Layer | Artefact (current edition) | What it is | What it is not |
|---|---|---|---|
| Weakness taxonomy | MITRE CWE (Top 25 2025) | Root-cause defect classes; Top 25 ranked from 39,080 CVE records (June 2024–June 2025)\[1\]\[2\] | Not a control set |
| Attack taxonomy | MITRE CAPEC, ATT&CK | Attacker techniques (CAPEC app-level; ATT&CK post-compromise) | Not requirements |
| Risk ranking | OWASP Top 10:2025 | 10 categories mapping 248 CWEs, from data on 589 CWEs plus a community survey\[3\]\[4\] | Not a testable standard |
| Verifiable requirements | OWASP ASVS 5.0.0 (May 2025) | 345 requirements (70 at L1), 17 chapters (V1–V17), levels L1–L3 | Not a process model; excludes infra/mobile\[5\] |
| Process maturity | OWASP SAMM; NIST SSDF SP 800-218 v1.1 (v1.2 draft) | Organisational SDLC practices | Not app-level controls |
| Organisational controls | NIST SP 800-53 Rel. 5.2.0; ISO/IEC 27001 | Enterprise control catalogues | Not web-specific |
| Identity assurance | NIST SP 800-63-4 (final, July 2025) | Authenticator/federation assurance levels | Not authorisation |
| Protocol specs | IETF (RFC 9700, HTTP, TLS), W3C/WHATWG (CSP, Fetch, WebAuthn) | Normative behaviour | Not threat models |
| Exploitation evidence | CISA KEV; Verizon DBIR; PortSwigger research | What is exploited / novel | Not exhaustive |
| Specialised lists | OWASP API Top 10 (2023); LLM Top 10 (2025); Agentic Top 10 (2026); Automated Threats (OAT) | Domain risk catalogues | Not substitutes for ASVS |

CWE names the defect; the Top 10 groups CWEs into risks for prioritisation; ASVS states the requirement that prevents the defect, and testing verifies it; SSDF/SAMM ensure the organisation does this repeatedly. ASVS 5.0 deliberately removed its direct CWE and NIST mappings in favour of a planned linkage through OWASP's Common Requirement Enumeration (CRE), so treat cross-walks as approximate.\[6\]\[7\]

**Recent revisions (2025–26):**
- **OWASP Top 10:2025** (release candidate November 2025, since finalised) adds Software Supply Chain Failures (A03) and Mishandling of Exceptional Conditions (A10), and absorbs SSRF (CWE-918) into A01.\[8\]\[9\]
- **ASVS 5.0.0** (30 May 2025) adds standalone chapters for Web Frontend Security (V3), Self-contained Tokens (V9), OAuth and OIDC (V10) and WebRTC (V17); 109 of 286 v4.0.3 requirements (38%) no longer exist separately.\[5\]\[6\]\[10\]
- **NIST SP 800-63-4** (final 31 July 2025): AAL2 verifiers must offer a phishing-resistant option; syncable passkeys are permitted at AAL2 but "SHALL NOT be used at AAL3."\[11\]\[12\]
- **NIST SSDF v1.2** (SP 800-218r1 initial public draft, 17 December 2025; comments closed 30 January 2026) adds PO.6 (Continuous Process Improvement) and PS.4 (Robust and Reliable Software Updates). v1.1 remains normative.\[13\]\[14\]
- **NIST SP 800-53 Release 5.2.0** (27 August 2025) targets software update and patch integrity: adds SA-15(13) (logging syntax), SA-24 (Design for Cyber Resiliency) and SI-02(07) (root cause analysis), and broadens SI-07(12) to all organisation-defined software.\[15\]
- **RFC 9700** (OAuth 2.0 Security BCP, January 2025) deprecates the implicit and password grants; OAuth 2.1 remains an Internet-Draft.\[16\]\[17\]
- **SLSA v1.1** (approved 21 April 2025) was followed by **v1.2** (24 November 2025), adding an approved Source track.\[18\]\[19\]\[20\]
- **CA/Browser Forum Ballot SC-081v3** (11 April 2025) cuts public TLS certificate lifetimes to 200 days from 15 March 2026, 100 days from 15 March 2027 and 47 days from 15 March 2029.\[21\]\[22\]\[23\]
- **OWASP Top 10 for Agentic Applications 2026** (9 December 2025) is new.\[24\]

---

## 2. Cross-cutting principles

1. **Complete mediation / deny by default.** Every request to every object is authorised server-side; absence of a rule means deny.
2. **Least privilege and least agency** for users, services, CI jobs, cloud roles and AI agents ("Least Agency" is the OWASP agentic list's term).\[25\]
3. **Defence in depth** with uncorrelated failure modes; a WAF is not a substitute for parameterisation.
4. **Separation of code and data** is the structural fix for injection; where impossible, as with LLM prompts, the class cannot be fully closed.\[26\]
5. **Secure defaults and fail-closed** (now a Top 10 category, A10:2025).
6. **Zero trust:** authenticate and authorise each hop, including service-to-service.
7. **Minimise attack surface and data.**
8. **Parser consistency.** Many 2025 research highlights (SAML bypass, Unicode normalisation, request smuggling) are *parser differentials*: two components interpret the same bytes differently.\[27\]\[28\] Use one canonical parser, normalise before validating, and reject ambiguity.
9. **Verifiability:** requirements testable (ASVS), artefacts attestable (SLSA), controls observable.

---

## 3. Development and design-time areas

### 3.1 Secure SDLC, threat modelling and security requirements

- **Requirements:** security requirements defined per risk level; documented design decisions; threats enumerated before build and revisited on change; a vulnerability disclosure and response process (SSDF RV group).
- **Threats:** insecure design (A06:2025, "missing or ineffective control design", which implementation cannot fix);\[8\] unmodelled trust boundaries; unconsidered abuse cases.
- **Mitigations:** SSDF practice groups (Prepare the Organisation, Protect the Software, Produce Well-Secured Software, Respond to Vulnerabilities);\[13\] SAMM for maturity; an ASVS level per application (ASVS 5.0 lowered the L1 barrier and *mandates documented security decisions* so implementations can vary while remaining verifiable).\[29\] Threat modelling: **STRIDE** for per-element enumeration on data-flow diagrams; **PASTA** for risk-centric, business-impact analysis; **attack trees** for goal decomposition, the closest analogue to fault trees.
- **Caveat:** no method is demonstrably superior. The defensible position is lightweight threat modelling on every significant change rather than heavyweight modelling once.

### 3.2 Authentication

- **Requirements:** verifier impersonation (phishing) resistance; replay resistance; online-guessing protection; secure enrolment and recovery; assurance proportionate to risk (AAL1–3).
- **Threats:** credential stuffing (OAT-008) and spraying; adversary-in-the-middle phishing relaying OTP and push MFA; MFA fatigue; infostealers harvesting passwords and session cookies; SIM swap; weak account recovery, which becomes the real authentication; federation flaws such as SAML signature-wrapping and parser-differential bypasses (e.g. ruby-saml CVE-2025-25291/25292, in PortSwigger's 2025 top ten),\[27\] and OAuth redirect-URI manipulation, code injection, mix-up and token leakage.
- **Mitigations:**
  - **Phishing-resistant authenticators:** WebAuthn/FIDO2 passkeys bind credentials to the origin. NIST SP 800-63B-4 states "Passwords are not phishing-resistant" and that OTP and out-of-band authenticators "SHALL NOT be considered phishing-resistant."\[11\] Syncable passkeys at AAL2; device-bound, non-exportable keys at AAL3.\[12\]\[30\]
  - **Passwords where retained:** breached-password checks; no composition rules or forced rotation (NIST position); throttling; memory-hard KDF storage (see 3.10).
  - **Recovery** at least as strong as the primary authenticator, with user notification.
  - **OAuth/OIDC per RFC 9700:** PKCE for all clients; exact redirect-URI string matching; no implicit or password grants; sender-constrained tokens (DPoP or mTLS) where feasible; refresh-token rotation or sender-constraint for public clients;\[16\]\[31\] issuer identification against mix-up (RFC 9207).
  - **SAML:** maintained library, strict schema validation, signature verified over exactly the assertion consumed, one XML parser for both.
- **Evidence:** the 2026 DBIR still finds stolen credentials the top action in Basic Web Application Attacks,\[32\] even though exploitation leads initial access overall. These are complementary priorities.

### 3.3 Session management and tokens

- **Requirements:** unpredictable session identifiers bound to the authenticated context, rotated on privilege change, invalidated server-side on logout or timeout; tokens integrity-protected, audience-restricted and short-lived.
- **Threats:** fixation, hijacking and cookie theft (XSS, infostealers); CSRF; JWT pitfalls (`alg: none`, RS256→HS256 algorithm confusion, `kid`/`jku` injection, missing `aud`/`iss`/`exp` checks, non-revocable long-lived tokens, sensitive data in claims).
- **Mitigations:** regenerate session ID at login and elevation; cookies `Secure`, `HttpOnly`, `SameSite=Lax`/`Strict`, `__Host-` prefix; idle and absolute timeouts; pin the JWT algorithm server-side and validate all registered claims (ASVS 5.0 V9 treats self-contained tokens as a distinct mechanism);\[6\] opaque reference tokens or short-lived JWTs plus revocation; DPoP to blunt token theft.
- **Partial:** no web-layer control fully defeats cookie theft by endpoint infostealers; device-bound session credentials are emerging but not universally deployable.

### 3.4 Authorisation and access control

- **Requirements:** every operation on every object and property is authorised server-side, including tenant boundaries, on every channel (UI, API, GraphQL resolver, WebSocket message, background job).
- **Threats:** IDOR/BOLA (CWE-639); function-level bypass (BFLA); property-level exposure and mass assignment (BOPLA); vertical and horizontal escalation; forced browsing; multi-tenant isolation failures; confused-deputy patterns, including SSRF (now under A01:2025) and AI agents acting with delegated user authority.
- **Evidence:** Broken Access Control is #1 in the Top 10:2025, mapping 40 CWEs.\[33\] In the 2025 CWE Top 25, Missing Authorization (CWE-862) rose five places to #4, and CWE-639 and Improper Access Control (CWE-284) newly entered.\[1\]\[2\] The OWASP API Top 10 places three authorisation categories in its top five.\[34\]\[35\]
- **Mitigations:** centralised policy decision points (policy engine or framework middleware, not ad hoc checks); deny by default; **RBAC** for coarse function access, **ABAC** for contextual rules, **ReBAC** (Zanzibar-style graphs) for object sharing; tenant ID derived from the authenticated principal, never request parameters, and enforced at the data layer (e.g. row-level security); response DTO allow-lists and bind allow-lists against BOPLA; unguessable IDs as defence in depth only; automated role × endpoint × owner test matrices.
- **Partial:** scanners largely cannot find BOLA because it needs ownership semantics.\[36\] Verification requires authorisation-aware tests or manual testing; formal policy specification and property-based testing pay off here.

### 3.5 Input handling and injection

- **Requirements:** untrusted data never changes the structure of an interpreter command (SQL, NoSQL, shell, LDAP, XPath, template, expression language, XML entity, deserialiser, filesystem path).
- **Threats:** SQL injection (CWE-89, #2 in the 2025 CWE Top 25)\[37\] and NoSQL operator injection; OS command injection (CWE-78, the most common CWE among 2025 KEV additions);\[38\] code injection (CWE-94); LDAP injection; XXE; server-side template injection (PortSwigger's #1 technique of 2025 introduced error-based exploitation of blind SSTI);\[39\] insecure deserialisation (CWE-502, 11 KEV entries in the Top 25 data);\[40\] path traversal (CWE-22, #6); unrestricted upload (CWE-434, #12);\[37\] ORM leaks (PortSwigger's #2 of 2025, exfiltration through user-controllable filter parameters); Unicode normalisation bypasses (#4),\[39\] where validation precedes normalisation.\[28\]
- **Mitigations:** parameterised queries and safe ORM APIs, with allow-listed filterable fields; argument-vector process APIs instead of shells; DTDs and external entities disabled; logic-less or sandboxed templates, never concatenating input into template source; data-only formats with schema validation instead of native deserialisation; canonicalise-then-check path containment; uploads validated by content, renamed, stored outside the web root, served from a separate origin with `Content-Disposition: attachment`, and scanned; normalise, then validate. Allow-list input validation is defence in depth; ASVS 5.0 V1 frames the primary control as encoding and sanitisation at the point of interpretation.
- **Status:** SQL injection is structurally solved where frameworks are used, which is why Injection fell to #5 in the Top 10:2025,\[3\] but it persists in legacy code and remains #2 in CWE by CVE volume.

### 3.6 Output handling and client-side attacks

- **Requirements:** untrusted data rendered in the browser cannot execute; cross-origin interactions occur only as intended; client-side state holds no secrets.
- **Threats:** XSS, reflected/stored/DOM (CWE-79, #1 in the CWE Top 25 2025); CSRF (CWE-352, #3);\[37\] clickjacking; open redirects chained into OAuth token theft; prototype pollution; CORS misconfiguration (reflected `Origin` with credentials, trusted `null`); unchecked `postMessage` handlers; client-side path traversal in SPA fetch routing;\[41\] DOM clobbering; tokens in `localStorage`; XS-Leaks (twice in PortSwigger's 2025 top ten: connection-pool redirect leak, ETag length leak);\[39\] cross-site WebSocket hijacking.\[41\]
- **Mitigations:** auto-escaping frameworks with context-aware encoding; avoid dangerous sinks (`innerHTML`, `eval`) and sanitise rich HTML; **strict CSP** (nonce/hash with `strict-dynamic`) plus **Trusted Types**; `SameSite` cookies, synchroniser or double-submit tokens and Fetch Metadata (`Sec-Fetch-Site`) filtering against CSRF; `frame-ancestors`; redirect allow-lists; null-prototype objects and validated merge inputs; explicit CORS origin allow-lists; `event.origin` checks; tokens in `HttpOnly` cookies or memory; `Origin` validation on WebSocket upgrade.
- **Partial:** XS-Leaks have no single fix; SameSite, Fetch Metadata isolation policies, COOP and framing restrictions reduce exposure while browsers patch individual oracles.

### 3.7 Browser security model and security headers

- **Requirements:** use the same-origin policy and opt-in hardening to isolate the application from other origins, injected content and cross-origin side channels (Spectre-class reads, opener abuse, SSL stripping, compromised third-party scripts).

| Control | Purpose | Notes |
|---|---|---|
| CSP (strict, nonce/hash) | Restrict script execution | Allow-list CSPs are routinely bypassable |
| Trusted Types | Eliminate DOM-XSS sinks | Strongest DOM-XSS control |
| HSTS (+ preload) | Force HTTPS | Mitigates SSL stripping |
| SRI | Integrity of fetched scripts | Ineffective for legitimately changing third-party tags |
| Cookie attributes (`Secure`, `HttpOnly`, `SameSite`, `__Host-`) | Cookie confidentiality/scope | Default `SameSite=Lax` is not a complete CSRF fix |
| COOP / COEP / CORP | Cross-origin isolation | COEP can break third-party embeds |
| Permissions-Policy | Disable unneeded features | Low cost |
| `nosniff`, `Referrer-Policy` | MIME sniffing, referrer leakage | Baseline hygiene |

ASVS 5.0 groups these under the Web Frontend Security chapter (V3).\[5\]

### 3.8 SSRF, request smuggling, cache attacks, host-header attacks

- **Requirements:** outbound requests only to intended destinations; all HTTP intermediaries agree on message boundaries; caches never serve private or attacker-influenced content to others; routing never trusts the client-supplied `Host`.
- **Threats:** **SSRF** against cloud metadata, internal admin interfaces and localhost services (PortSwigger's #3 of 2025 made blind SSRF observable via redirect loops; HTTP/2 CONNECT offers internal port scanning, #9);\[39\] **request smuggling/desync** (CL.TE, TE.CL, H2 downgrade, malformed chunks; James Kettle's 2025 "HTTP/1.1 Must Die" research argued "the industry has not properly fixed request smuggling");\[42\] **web cache poisoning**, including internal framework caches (Next.js, #7);\[39\] **web cache deception** via path confusion; **host-header injection** (password-reset poisoning, routing SSRF).
- **Mitigations:** SSRF: destination allow-lists; resolve, validate, then connect to the validated IP (anti-rebinding); block link-local, private and loopback ranges at an egress proxy; re-validate each redirect hop; default-deny egress; **IMDSv2 on AWS** (PUT-issued session tokens, refusal of requests with `X-Forwarded-For`, hop limit 1), which AWS describes as protecting against "unpatched SSRF vulnerabilities" and misconfigured-open reverse proxies and WAFs.\[43\]\[44\]\[45\] Smuggling: HTTP/2 or HTTP/3 end-to-end including edge-to-origin; reject ambiguous requests at the edge. Caching: keys include all response-varying inputs; `Cache-Control: private, no-store` on authenticated responses; consistent CDN/origin path normalisation; no extension-based caching heuristics. Host: canonical hostnames, never absolute links from `Host`.
- **Partial:** smuggling remains structurally possible wherever HTTP/1.1 links intermediaries. PortSwigger's position that HTTP/1.1 upstreams should be retired\[42\] is not universally accepted, and many CDNs and load balancers still downgrade toward origins.

### 3.9 API security (REST, GraphQL, gRPC, WebSockets)

- **Requirements:** each endpoint, operation, field and message is authenticated, authorised and resource-bounded; the API inventory is complete; third-party API responses are untrusted input.
- **Threats (OWASP API Security Top 10, 2023, still current):** API1 Broken Object Level Authorization; API2 Broken Authentication; API3 Broken Object Property Level Authorization (merging 2019's Excessive Data Exposure and Mass Assignment); API4 Unrestricted Resource Consumption; API5 Broken Function Level Authorization; API6 Unrestricted Access to Sensitive Business Flows; API7 SSRF; API8 Security Misconfiguration; API9 Improper Inventory Management (shadow and zombie APIs); API10 Unsafe Consumption of APIs.\[36\]\[46\]\[47\] Protocol-specific: GraphQL introspection exposure, depth/complexity DoS, batching brute force and per-resolver authorisation gaps; gRPC reflection exposure and trust in internal transport; WebSocket per-message authorisation gaps and cross-site hijacking.
- **Mitigations:** schema-first contracts (OpenAPI, GraphQL SDL, protobuf) with request and response validation; per-object and per-property authorisation in handlers and resolvers; per-identity quotas, GraphQL cost analysis and depth limits, pagination caps; introspection and reflection disabled in production; an API gateway for authentication, throttling and inventory, but not as the sole authorisation layer; continuous API discovery; timeouts and validation on outbound calls.

### 3.10 Cryptography and data protection

- **Requirements:** confidentiality and integrity in transit and at rest; correct algorithm and mode selection; controlled key lifecycle; irreversible password storage; no secrets in code; crypto-agility for the post-quantum transition.
- **Threats:** legacy TLS and cipher suites; unencrypted internal hops; certificate-expiry outages; mis-issuance; fast or unsalted password hashes; secrets leaked in repositories, images and CI logs; nonce reuse and mode misuse; weak randomness; harvest-now-decrypt-later collection.
- **Mitigations:** TLS 1.3 preferred, 1.2 minimum, with HSTS; AEAD ciphers (AES-GCM, ChaCha20-Poly1305); Argon2id, scrypt, bcrypt or PBKDF2 at current OWASP Cheat Sheet work factors; KMS/HSM with envelope encryption; a secrets manager issuing short-lived dynamic credentials; secret scanning pre-commit and in CI. **Certificate automation (ACME) is now mandatory in practice:** under SC-081v3 the maximum public certificate lifetime is 200 days as of March 2026, falling to 100 days in 2027 and 47 in March 2029, with domain-validation reuse falling to 10 days.\[48\]\[49\] **Post-quantum:** NIST finalised ML-KEM (FIPS 203), ML-DSA (FIPS 204) and SLH-DSA (FIPS 205) in August 2024; NIST IR 8547 (initial public draft, November 2024) proposes deprecating 112-bit RSA and ECC after 2030 and disallowing quantum-vulnerable public-key algorithms after 2035.\[50\]\[51\] Hybrid key exchange (X25519MLKEM768) is already widely deployed in TLS.\[51\]\[52\] Inventory cryptographic usage, enable hybrid key exchange at the edge, and plan PQ signatures as PKI support matures.
- **Disagreement:** NIST and most implementers endorse hybrid key exchange during transition as a hedge against cryptanalytic surprise, and Germany's BSI (TR-02102-1, January 2026) recommends the hybrid form. The NSA takes the opposite view: its CNSA 2.0 FAQ states it "will not require NSS developers to use hybrid certified products for security purposes" and requires ML-KEM-1024 and ML-DSA-87 "for all classification levels." IR 8547 dates are draft.

### 3.11 Business logic, race conditions, abuse, fraud and automated threats

- **Requirements:** workflows enforce invariants (ordering, limits, single-use, monetary conservation) server-side and atomically; automated abuse is economically bounded.
- **Threats:** step-skipping; negative or overflow quantities; coupon and referral abuse; race conditions/TOCTOU (limit overrun via concurrent requests, made practical by single-packet attacks); the OWASP Automated Threats catalogue (credential stuffing OAT-008, carding, scalping, scraping, account-creation abuse, denial of inventory, card and token cracking); API6:2023 is the API framing.
- **Mitigations:** explicit state machines; idempotency keys; database atomicity (transactions, row locks, unique constraints); server-side price and total recomputation; abuse-case modelling; layered bot defence (identity/device/network rate limits, behavioural signals, progressive challenges, business velocity limits).
- **Partial:** bot mitigation is an arms race; CAPTCHAs are increasingly solvable and fingerprinting has privacy costs. No vendor-neutral standard defines adequacy; treat it as fraud-economics risk management.

### 3.12 Software supply chain

- **Requirements:** every component and build step known, trusted and verifiable; artefacts traceable to source and build; upstream maintainer compromise cannot silently reach production; third-party browser scripts inventoried and integrity-controlled.
- **Threats:**
  - known-vulnerable dependencies;
  - malicious packages (typosquatting, dependency confusion, maintainer takeover);
  - **self-propagating registry worms:**
    - CISA's 23 September 2025 alert reported that "Shai-Hulud" had compromised over 500 npm packages by stealing developer and CI tokens and republishing;
    - Shai-Hulud 2.0 followed in November 2025 and, per the Cloud Security Alliance, backdoored 796 unique npm packages with over 20 million combined weekly downloads;
    - 2026 variants followed, such as those in Singapore CSA's 6 August 2026 advisory on `keyv`-family packages;
  - compromised CI/CD;
  - unsigned updates;
  - malicious IDE and AI coding-tool extensions;
  - Magecart-style e-skimming.
- **Evidence:** Software Supply Chain Failures is A03:2025; the 2026 DBIR reports third-party breaches rose 60% to 48% of breaches.\[53\]\[54\]
- **Mitigations:** SCA with reachability; lockfiles with integrity hashes; private registry proxy with scoped namespaces; cool-down policies for new versions; install scripts disabled by default where possible; SBOMs (SPDX/CycloneDX) generated and consumed; **SLSA** Build L1 (provenance exists), L2 (signed provenance from a hosted platform), L3 (hardened, isolated builds), and the v1.2 Source track (L1–L4, L4 requiring two-party review);\[55\]\[56\] artefact signing and verification; OIDC-based trusted publishing without long-lived registry tokens; phishing-resistant MFA for maintainers. For browser scripts: inventory, authorisation, integrity (SRI for static scripts, CSP) and tamper detection, now mandatory on cardholder-data payment pages under PCI DSS v4.0.1 requirements 6.4.3 and 11.6.1 from 31 March 2025.\[57\]\[58\]
- **Partial:** provenance proves *where* an artefact was built, not that its source is benign. The Cloud Security Alliance reports that Mini Shai-Hulud "became the first publicly documented supply chain attack to produce cryptographically valid SLSA Build Level 3 provenance attestations by hijacking a legitimate build pipeline"; it published 84 malicious artefacts across 42 @tanstack packages on 11 May 2026. SBOMs inventory but do not detect malice; malicious-package detection is heuristic.

### 3.13 Security testing and verification

- **Requirements:** controls verified continuously, at depth proportionate to risk, against a stated ASVS level.

| Method | Finds well | Misses |
|---|---|---|
| SAST | Injection sinks, dangerous APIs, secrets, taint flows | Authorisation logic, config; false positives |
| SCA | Known-vulnerable components | Malicious packages without advisories |
| DAST | Runtime misconfig, reflected injection, headers | Deep logic, BOLA, crawl gaps |
| IAST | Confirmed runtime data flows | Unexercised paths |
| Fuzzing | Parser crashes, edge cases, memory safety | Semantic logic errors |
| Manual code review | Design, logic, authz flaws | Scale |
| Penetration testing | Chained, creative exploitation | Point-in-time, scope-limited |
| Bug bounty / VDP | Long-tail real-world findings | Guaranteed coverage |

- **Mitigations:** combine methods across the pipeline; gate releases on policy severities; dedicated authorisation suites; a published vulnerability disclosure policy (CISA Secure by Design pledge; SSDF RV.1). The SSDF v1.2 draft extends RV.1.2 to testing default and common configurations, not just code.\[14\]

### 3.14 Error handling, logging, privacy and sensitive-data exposure

- **Requirements:** errors fail closed and reveal nothing exploitable; security events logged with integrity and context; no secrets or unnecessary personal data in logs; personal data minimised, purpose-bound and time-limited.
- **Threats:** verbose stack traces and debug endpoints; fail-open exception paths (A10:2025, 24 CWEs);\[4\] error-based oracles (cf. the 2025 #1 SSTI technique); log injection (CWE-117); logged tokens and passwords; insufficient logging (A09:2025 Security Logging & Alerting Failures);\[3\] sensitive information exposure (CWE-200, #20).\[40\]
- **Mitigations:** global exception handlers returning generic errors with correlation IDs; explicit fail-closed defaults; structured logging with encoded untrusted fields (SP 800-53 Rel. 5.2.0 adds SA-15(13) on logging syntax);\[15\] redaction filters; centralised tamper-evident storage; data classification; field-level encryption or tokenisation; privacy by design and DPIAs (GDPR Art. 25/35); ASVS 5.0 V14 (Data Protection) and V16 (Security Logging and Error Handling).\[59\]

### 3.15 AI/LLM features in web applications, and AI-generated code

- **Requirements:** model outputs untrusted; model and agent privileges bounded to the invoking user's authority; untrusted content cannot silently redirect agent goals; prompts, retrieval stores and tools integrity-controlled; consumption bounded.
- **Threats (OWASP Top 10 for LLM Applications 2025):** LLM01 Prompt Injection (direct and indirect); LLM02 Sensitive Information Disclosure; LLM03 Supply Chain; LLM04 Data and Model Poisoning; LLM05 Improper Output Handling (model output reaching HTML, SQL or shell sinks); LLM06 Excessive Agency; LLM07 System Prompt Leakage; LLM08 Vector and Embedding Weaknesses (RAG cross-tenant leakage, embedding inversion); LLM09 Misinformation; LLM10 Unbounded Consumption.\[60\]\[61\]
- **Threats (OWASP Top 10 for Agentic Applications 2026):** ASI01 Agent Goal Hijack; ASI02 Tool Misuse and Exploitation; ASI03 Identity and Privilege Abuse; ASI04 Agentic Supply Chain Vulnerabilities (malicious tools, MCP servers, agent cards); ASI05 Unexpected Code Execution; ASI06 Memory and Context Poisoning; ASI07 Insecure Inter-Agent Communication; ASI08 Cascading Failures; ASI09 Human-Agent Trust Exploitation; ASI10 Rogue Agents.\[24\]\[62\]
- **AI-generated code:** Veracode's 2025 GenAI Code Security Report tested more than 100 LLMs on 80 tasks and found security flaws in 45% of cases; samples failed to defend against XSS 86% of the time and log injection 88%, and Java failed over 70%.\[63\]\[64\] Its 2026 follow-up reports security pass rates clustered at 51–53% regardless of model size.\[65\] These are vendor benchmarks on curated tasks; treat absolute figures as indicative. Related risks: hallucinated package names ("slopsquatting") and prompt injection against coding agents.
- **Mitigations:** treat the LLM as an untrusted confused deputy; enforce authorisation outside the model, in tools and APIs, using the end user's identity and scopes; least privilege and least agency; human approval for consequential actions; allow-listed tools; sandboxed code execution; encode and validate model output before any sink; no secrets or authorisation logic in system prompts; tenant-partitioned vector stores with retrieval-time access filtering; provenance for models, datasets and tools; rate and cost limits; input/output classifiers as defence in depth. Gate AI-written code with the same SAST, SCA and review as human code, and verify suggested packages exist and are reputable. NIST SP 800-218A (SSDF Generative AI Community Profile) provides process guidance.\[66\]
- **Expert position:** the UK NCSC (December 2025): "As there is no inherent distinction between 'data' and 'instruction', it's very possible that prompt injection attacks may never be totally mitigated in the way that SQL injection attacks can be."\[67\] It recommends reducing impact rather than expecting prevention.\[68\]\[69\] Assume the model can be instructed by any content it reads, and bound what it can then do.

---

## 4. Hosting, infrastructure and operations areas

### 4.1 Server, OS and runtime hardening; misconfiguration; patch and vulnerability management

- **Requirements:** minimal, hardened, supported platforms; consistent, drift-detected configuration; known-exploited vulnerabilities remediated within defined deadlines.
- **Threats:** default credentials; exposed admin consoles and debug modes; directory listing; outdated runtimes; misconfiguration (A02:2025, the list's largest riser);\[70\] exploitation of edge devices and public-facing applications.
- **Evidence:** DBIR 2026: exploitation is the top initial access vector at 31% of breaches, and median time to patch rose from 32 to 43 days.\[71\] CISA added 245 vulnerabilities to KEV in 2025 (total 1,484), 24 of them marked as ransomware-used.\[72\]
- **Mitigations:** CIS Benchmarks or vendor hardening baselines; immutable infrastructure and golden images; configuration-as-code with drift detection; unused services and debug features disabled; risk-based patching (KEV first, then EPSS, then CVSS); internet-facing asset inventory; WAF virtual patching as a time-bounded stopgap only.
- **Partial:** patch velocity is losing to exploit velocity, and DBIR notes AI is compressing time-to-exploit.\[54\] Architectural exposure reduction (fewer internet-facing management planes) is the durable control.

### 4.2 Cloud security

- **Requirements:** explicit responsibility split per service model; least-privilege IAM without long-lived keys; private-by-default storage and services; protected, logged control plane.
- **Threats:** over-permissioned IAM and escalation paths; leaked access keys; public object storage; metadata credential theft via SSRF; permissive security groups; cross-account trust abuse; unlogged control-plane activity.
- **Evidence:** DBIR 2026 reports that for weak passwords and permission misconfigurations in third-party cloud environments, resolving 50% of findings took nearly eight months.\[32\]
- **Mitigations:** workload identity federation instead of static keys; permission boundaries and organisation policies; block-public-access guardrails; IMDSv2 required, hop limit 1 where containers do not need metadata;\[43\] CSPM/CNAPP; control-plane audit logs to an isolated account; separate accounts per environment and blast radius.
- **Note:** the shared responsibility model is clear for infrastructure but blurs for managed PaaS/SaaS configuration, where most customer-side failures occur.

### 4.3 Containers, orchestration and serverless

- **Requirements:** minimal, scanned, signed images from trusted sources; unprivileged, isolated workloads; authenticated and authorised control plane; no secrets baked into images.
- **Threats:** vulnerable or malicious base images; privileged containers and host mounts enabling escape; exposed Kubernetes API or kubelet; over-broad RBAC and service-account tokens; admission and ingress flaws such as "IngressNightmare" (CVE-2025-1974, unauthenticated configuration injection to RCE in ingress-nginx);\[41\] flat pod networks; serverless event-data injection, over-privileged function roles and denial of wallet.
- **Mitigations:** distroless or minimal images; signing with admission-time verification; **Kubernetes Pod Security Standards** (Privileged / Baseline / Restricted) enforced via Pod Security Admission, GA since v1.25 and replacing the removed PodSecurityPolicy,\[73\]\[74\]\[75\] with Restricted for application workloads; read-only root filesystems, dropped capabilities, seccomp, non-root; default-deny NetworkPolicies; least-privilege RBAC and no automounted tokens; restricted control-plane exposure; runtime detection; sandboxed runtimes (gVisor, Kata, microVMs) for untrusted or multi-tenant code; per-function least-privilege roles, event-source validation and concurrency/budget limits for serverless.

### 4.4 Network and edge security

- **Requirements:** origin reachable only via the intended edge; volumetric and L7 DoS absorbed; malicious traffic filtered; internal segments isolated; DNS integrity and ownership maintained.
- **Threats:** volumetric and L7 DDoS; origin bypass around the CDN or WAF; proxy/origin parsing discrepancies; DNS hijacking; **subdomain takeover** via dangling CNAMEs to deprovisioned cloud resources; exposed internal services.
- **Mitigations:** CDN and DDoS scrubbing; **WAF/WAAP**, which PCI DSS v4.0.1 requirement 6.4.2 mandates from 31 March 2025 as "an automated technical solution … that continually detects and prevents web-based attacks" in front of in-scope public-facing web applications;\[76\]\[77\] origin lockdown by mTLS or edge IP allow-lists; API gateways for authentication, throttling and schema enforcement; segmentation; DNSSEC where supported, registrar lock and CAA records; automated dangling-DNS detection tied to deprovisioning.
- **Disagreement / partial:** WAFs stop commodity attacks and enable virtual patching but are widely documented as bypassable (Unicode normalisation, parser differentials, payload mutation), and attackers modifying exploits to evade WAF rules is a recurring incident pattern.\[54\] A WAF is a compensating control, never a substitute for fixing code.

### 4.5 CI/CD and infrastructure-as-code

- **Requirements:** pipelines protected as production systems; only reviewed code reaches production; short-lived, scoped pipeline credentials; separated environments; IaC scanned and policy-checked.
- **Threats:** poisoned pipeline execution via fork pull requests; compromised third-party actions or plugins; secrets in logs and variables; self-hosted runner persistence (Shai-Hulud 2.0 installed rogue runners and workflow files);\[78\]\[79\] over-privileged deploy credentials; IaC misconfiguration at scale; prompt injection against AI agents in CI.
- **Mitigations:** branch protection with mandatory review (SLSA Source L4 two-party review); actions pinned by commit SHA; OIDC-federated short-lived cloud credentials; ephemeral, isolated runners; separate build and deploy identities; IaC scanning and policy-as-code gates; separate production approval; SSDF PS.4 (draft v1.2) staged rollouts, rollback protection against downgrade to vulnerable versions, and resilient update delivery.\[14\] Incident playbooks must include full credential rotation: removing a malicious package does not revoke what it stole.\[78\]

### 4.6 Databases, data stores, backups, resilience and availability

- **Requirements:** data stores not internet-exposed; least-privilege per-service access; encryption at rest; immutable, isolated, restore-tested backups; availability targets met under attack and failure.
- **Threats:** exposed unauthenticated databases and search clusters; shared superuser application accounts; ransomware encrypting primary and backup copies (DBIR 2026: ransomware in 48% of breaches, 69% of victims did not pay);\[32\]\[80\] resource-exhaustion DoS (CWE-770, new in the 2025 Top 25);\[1\] integrity attacks.
- **Mitigations:** private networking only; per-service credentials with minimal grants; row-level security for multi-tenancy; encryption at rest with customer-managed keys where warranted; immutable or offline backups (3-2-1 with an immutable copy); restore drills against RPO/RTO; application and database resource limits; multi-zone/region designs proportionate to criticality; SP 800-53 Rel. 5.2.0 SA-24 Design for Cyber Resiliency.\[15\]

### 4.7 Logging, monitoring, detection, incident response, RASP, SIEM

- **Requirements:** security events across application, platform and cloud planes collected, correlated and alerted on; incidents detected, contained and recovered to defined objectives; lessons fed into root-cause fixes.
- **Threats:** undetected intrusion and long dwell time; log tampering; alert fatigue; SaaS and third-party blind spots.
- **Mitigations:** application-level security event logging (authentication, authorisation failures, validation failures, admin actions) per the OWASP Logging Cheat Sheet and ASVS V16; SIEM correlation with detections mapped to MITRE ATT&CK; immutable log storage; RASP for sink-level exploit blocking; NIST SP 800-61 incident response plans, regularly exercised; root-cause analysis after remediation (SP 800-53 SI-02(07), new in Rel. 5.2.0).\[15\]\[81\]
- **Partial:** RASP has overhead and language coverage limits and is contested as a primary control; detection effectiveness depends more on tuning than tooling.

### 4.8 Operator, administrator and privileged access

- **Requirements:** administrative access strongly authenticated, just-in-time, recorded and separated from user paths; controlled break-glass.
- **Threats:** phished or infostealer-harvested admin credentials and cookies; standing privileges; shared accounts; exposed management interfaces; helpdesk social engineering for MFA resets; insider misuse.
- **Mitigations:** phishing-resistant MFA for all privileged access, with AAL3-class hardware-bound authenticators for the most sensitive roles per 800-63-4;\[30\] just-in-time elevation (PAM); privileged access workstations; session recording; admin interfaces on private networks or behind identity-aware proxies; strict identity verification for resets; access recertification; separation of duties for production changes.

### 4.9 Compliance and standards landscape (general)

| Regime / standard | Web-relevant thrust | Recent change |
|---|---|---|
| PCI DSS v4.0.1 | Secure development (Req. 6); automated web-attack protection (6.4.2); payment-page script inventory/integrity (6.4.3); header/script tamper detection (11.6.1); MFA | Future-dated requirements mandatory 31 March 2025; SAQ A merchants had 6.4.3/11.6.1 replaced by an eligibility criterion (January 2025)\[58\]\[82\]\[83\] |
| GDPR and similar regimes | Minimisation, privacy by design (Art. 25), security of processing (Art. 32), 72-hour breach notification | Analogous regimes proliferating |
| ISO/IEC 27001:2022 | ISMS with Annex A controls incl. secure coding (A.8.28) | 2013-edition transition completed |
| SOC 2 | Trust Services Criteria attestation, common for SaaS | — |
| NIST SSDF (SP 800-218) | Secure development practices; basis of US federal self-attestation | v1.2 draft (Dec 2025)\[84\] |
| NIST SP 800-53 | Enterprise control catalogue | Rel. 5.2.0 (Aug 2025)\[85\] |
| NIST SP 800-63-4 | Digital identity assurance | Final July 2025\[86\] |
| CISA Secure by Design | MFA by default, eliminating vulnerability classes, transparency | Voluntary pledge |
| EU Cyber Resilience Act | Product security and vulnerability handling | Phased application through 2027; limited scope for pure SaaS |

Compliance is a floor and an evidence obligation, not a threat model. PCI DSS 6.4.3/11.6.1 is the clearest recent case of a standard codifying a client-side control (Magecart defence)\[58\] that applies equally outside payments.

---

## 5. Summary matrix: area → principal threats → primary mitigations

| Area | Principal threats | Primary mitigations | Completeness |
|---|---|---|---|
| SDLC / design | Insecure design, unmodelled trust boundaries | SSDF, SAMM, ASVS levels, threat modelling | Process-dependent |
| Authentication | Stuffing, AitM phishing, recovery abuse, federation parser bugs | Passkeys, breached-password checks, RFC 9700, hardened SAML | Strong if phishing-resistant |
| Sessions/tokens | Fixation, hijack, cookie theft, JWT alg confusion | Rotation, cookie attributes, pinned algorithms, DPoP | Partial vs infostealers |
| Authorisation | BOLA, BFLA, BOPLA, tenant escape | Central policy, deny-by-default, data-layer tenancy, authz tests | Strong design; hard to verify |
| Injection | SQLi, OS cmd, SSTI, XXE, deserialisation, traversal, ORM leaks | Parameterisation, safe APIs, parser hardening, normalise-then-validate | Structurally solvable |
| Client-side | XSS, CSRF, clickjacking, CORS, prototype pollution, XS-Leaks | Auto-escaping, strict CSP + Trusted Types, SameSite + tokens, Fetch Metadata | XS-Leaks partial |
| Browser headers | Downgrade, script injection, cross-origin leaks | HSTS, CSP, SRI, COOP/COEP/CORP, Permissions-Policy | Strong when deployed |
| SSRF / smuggling / cache | Metadata theft, desync, poisoning/deception, host-header | Egress allow-list, IMDSv2, HTTP/2 upstream, correct cache keys | Smuggling partial on HTTP/1.1 |
| APIs | API Top 10, GraphQL DoS, shadow APIs | Schema validation, per-resolver authz, quotas, inventory | Inventory partial |
| Crypto / data | Weak TLS, cert expiry, weak hashing, secret leakage, HNDL | TLS 1.3, ACME, Argon2id, KMS/secrets manager, hybrid PQC | PQ migration in progress |
| Business logic / bots | Workflow abuse, races, OAT catalogue | State machines, atomicity, idempotency, layered bot defence | Partial (arms race) |
| Supply chain | Malicious deps, worms, build compromise, Magecart | SCA, pinning, private registry, SBOM, SLSA, signing, script inventory | Partial vs malicious packages |
| Testing | Undetected defects | SAST+SCA+DAST+manual+bounty, authz suites | Coverage-bounded |
| Errors / logging / privacy | Fail-open, leakage, log injection, missing telemetry | Fail-closed handlers, redacted structured logs, minimisation | Strong if enforced |
| AI/LLM/agents | Prompt injection, excessive agency, RAG leakage, insecure AI code | External authz, least agency, output encoding, sandboxing, human approval | Prompt injection not fully mitigable |
| Hardening / patching | Misconfig, exploited CVEs | Baselines, drift control, KEV-first SLAs | Velocity-limited |
| Cloud | Over-privileged IAM, public storage, key leakage | Workload identity, guardrails, CSPM, IMDSv2 | Strong with guardrails |
| Containers / serverless | Escape, RBAC abuse, ingress flaws | Pod Security Restricted, signing, NetworkPolicy, sandboxed runtimes | Strong for known classes |
| Network / edge | DDoS, origin bypass, subdomain takeover | CDN/DDoS, WAF (compensating), origin lockdown, DNS hygiene | WAF bypassable |
| CI/CD / IaC | Pipeline poisoning, secret theft, runner persistence | SHA-pinned actions, OIDC creds, ephemeral runners, review gates | Improving |
| Data stores / resilience | Exposure, ransomware, resource exhaustion | Private access, least privilege, immutable backups, restore drills | Strong if tested |
| Detection / IR | Dwell time, blind spots | App security logging, SIEM, IR exercises, RCA | Tuning-dependent |
| Privileged access | Admin credential theft, standing privilege | Hardware-bound MFA, JIT/PAM, isolated admin planes | Strong |

---

## 6. Emerging and shifting threat areas (2025–2026)

1. **Exploitation outpacing patching:** KEV additions accelerated to 245 in 2025, against 185 in 2024 and 187 in 2023.\[87\]
2. **Supply-chain worms:** self-replicating registry malware (Shai-Hulud lineage) converts one stolen token into ecosystem-wide compromise. The Cloud Security Alliance (22 May 2026) reports that on 12 May 2026 the threat actor TeamPCP "publicly released the Shai-Hulud worm source code as open-source software."
3. **Agentic AI and MCP-style tool ecosystems:** new confused-deputy and supply-chain risk\[62\] with immature controls.
4. **AI-generated code at volume:** flat per-task pass rates times higher output imply rising absolute vulnerability counts (Veracode's inference).\[65\]
5. **Parser differentials and framework-internal caches** dominate current offensive research.
6. **Certificate lifecycle compression and post-quantum migration:** manual PKI becomes an availability risk; PQ signatures and PKI lag hybrid key exchange.

---

## 7. Where expert sources disagree or mitigations are partial

- **Ranking methodology.** The OWASP Top 10 blends incidence data with a community survey; the CWE Top 25 ranks by CVE frequency × severity, over-weighting widely deployed products (XSS ranks #1 by volume despite few KEV entries);\[37\] DBIR measures breaches. They should not be expected to agree.
- **Prompt injection.** The NCSC holds that it is likely not fully mitigable;\[69\] some vendors market detection classifiers as prevention. Assume bypass.\[26\]\[88\]
- **HTTP/1.1 retirement.** PortSwigger argues for eliminating it between intermediaries;\[42\] infrastructure realities slow adoption.
- **Passkey syncing.** NIST accepts syncable passkeys at AAL2 but not AAL3;\[12\] some practitioners object to cloud-account recovery becoming the effective root of trust.
- **Password policy and SBOMs.** NIST and ASVS dropped composition and rotation rules, which some auditors still require; SBOMs are mandated widely but are inventory, not assurance.
- WAF value, hybrid-vs-pure PQC and provenance limits are discussed in 4.4, 3.10 and 3.12.

---

## 8. Recommendations for an enterprise architecture programme

1. **Adopt ASVS 5.0 as the normative requirements set** with a level per application; SSDF v1.1 (tracking v1.2) and SAMM for process; the Top 10 only for awareness.
2. **Make authorisation an architectural component:** a central policy engine with a formal policy model, data-layer tenant enforcement and generated authorisation test matrices; formal specification yields the highest return here.
3. **Move to phishing-resistant authentication** (passkeys for users, hardware-bound authenticators for administrators) and RFC 9700 conformance.
4. **Set exploitation-driven patch SLAs** (KEV, then EPSS, then CVSS), in days for internet-facing systems.
5. **Treat the supply chain as production:** pinned, hashed dependencies; registry proxy with cool-down; SHA-pinned CI actions; OIDC short-lived credentials; SLSA Build L3; signatures verified at deploy; browser script inventory with tamper detection.
6. **Close injection classes structurally:** auto-escaping, parameterising frameworks; strict CSP with Trusted Types; one parser per format.
7. **Retire HTTP/1.1 on intermediary-to-origin hops**; require IMDSv2 and egress allow-listing.
8. **For AI features, design for prompt-injection compromise:** authorisation outside the model, least agency, sandboxing, human approval, and identical gates for AI-generated code.
9. **Automate certificates (ACME) before the 100-day phase in March 2027**; enable hybrid key exchange at the edge.
10. **Instrument for detection and recovery:** application security events, immutable logs, restore-tested backups, exercised IR with root-cause closure.

---

## Caveats

- Several 2026 datapoints (DBIR, Shai-Hulud 2026 waves) come via secondary analyses; Verizon's release confirms the headline 31% and 48% figures.\[80\]
- PCI DSS requirement wording was confirmed via secondary sources quoting the standard; effective dates are confirmed by PCI SSC.\[83\]
- KEV 2025 totals derive from Cyble's analysis; Veracode's figures are a vendor benchmark.\[38\]
- NIST IR 8547 and SSDF v1.2 are drafts;\[50\] the OWASP API Top 10 dates from 2023 and the Agentic Top 10 is a first edition.

## Sources

1. [MITRE shares 2025's top 25 most dangerous software weaknesses](https://www.bleepingcomputer.com/news/security/mitre-shares-2025s-top-25-most-dangerous-software-weaknesses/)
2. [MITRE Top 25 Most Dangerous Software Weaknesses 2025: Complete Analysis and Protection Guide](https://www.siteguarding.com/security-blog/mitre-top-25-most-dangerous-software-weaknesses-2025-complete-analysis-and-protection-guide/)
3. [Introduction - OWASP Top 10:2025](https://owasp.org/Top10/2025/0x00_2025-Introduction/)
4. [OWASP Top 10:2025 Explained With Code Examples](https://cyberphinix.de/en/blog/owasp-top-10/)
5. [OWASP ASVS: A Comprehensive Overview - Codific](https://codific.com/owasp-asvs-a-comprehensive-overview/)
6. [ASVS/5.0/en/0x05-For-Users-Of-4.0.md at master · OWASP/ASVS](https://github.com/OWASP/ASVS/blob/master/5.0/en/0x05-For-Users-Of-4.0.md)
7. [What’s New in ASVS 5.0](https://softwaremill.com/whats-new-in-asvs-5-0/)
8. [The New 2025 OWASP Top 10 List: What Changed, and What You Need to Know](https://www.fastly.com/blog/new-2025-owasp-top-10-list-what-changed-what-you-need-to-know)
9. [OWASP Top 10 2025: All 10 Vulnerabilities Explained & How to Fix Them](https://www.reflectiz.com/blog/owasp-top-ten-2025/)
10. [ASVS 4.0.3 vs 5.0: Developer Migration Guide (2026)](https://www.securecodinghub.com/blog/owasp-asvs-4-vs-5-changes-developers)
11. [NIST Special Publication NIST SP 800-63B-4 Digital Identity Guidelines](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63B-4.pdf)
12. [NIST's 2025 identity guidance drew a line around syncable passkeys — Patch & Proof](https://patchandproof.com/desk/nist-sp-800-63-4-digital-identity-2025/)
13. [NIST SSDF (SP 800-218): Practices, tasks, and examples](https://edu.chainguard.dev/software-security/secure-software-development/ssdf/)
14. [NIST SSDF 1.2 Changes: Key Updates for Teams](https://cycode.com/blog/nist-ssdf-1-2-changes-compliance-guide/)
15. <https://csrc.nist.gov/csrc/media/Projects/risk-management/800-53%20Comment%20Site/SP800-53-r5.2.0-changes.pdf>
16. [OAuth 2.0 Security Best Current Practice — RFC 9700](https://oauth.net/2/oauth-best-practice/)
17. [OAuth 2.1 and the Security BCP: RFC 9700 and RFC 6819 (Changes from OAuth 2.0)](https://bmf-tech.com/posts/oauth-2-1-security-bcp/)
18. [SLSA • Blog](https://slsa.dev/blog)
19. [SLSA • SLSA v1.1 is now Approved!](https://slsa.dev/blog/2025/04/slsa-v1.1)
20. [SLSA (Supply-chain Levels for Software Artifacts)](https://rywalker.com/research/slsa)
21. [47-Day TLS Certificate Era: How to Prepare Your PKI](https://www.encryptionconsulting.com/47-day-tls-certificate-era/)
22. [Shorter SSL/TLS Certificate Lifetimes 2026](https://www.brandshelter.com/blog/shorter-ssl-certificate-lifetimes-2026/)
23. [The 47-Day Certificate: What Breaks and How to Fix It](https://matrixgard.com/blog/tls-certificate-lifetime-47-days-automation-2026/)
24. [OWASP Top 10 for Agentic Applications 2026](https://cycode.com/blog/owasp-top-10-agentic-applications/)
25. [Lessons from OWASP Top 10 for Agentic Applications](https://auth0.com/blog/owasp-top-10-agentic-applications-lessons/)
26. [Prompt injection is not SQL injection: why there's no patch coming](https://zerberus.ai/blog/prompt-injection-is-not-sql-injection/)
27. [PortSwigger's Top 10 Web Hacking Techniques of 2025 — A Deep Dive - DEV Community](https://dev.to/latentbreach/portswiggers-top-10-web-hacking-techniques-of-2025-a-deep-dive-25k6)
28. [\[HackerNotes Ep. 163\] PortSwigger Top 10 Web Hacking Techniques of 2025](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-163-portswigger-top-10-web-hacking-techniques-of-2025)
29. [OWASP 2025 Global AppSec EU: Introducing the 5.0 release of the ASVS](https://owasp2025globalappseceu.sched.com/event/1whCc/introducing-the-50-release-of-the-asvs)
30. [Phishing-Resistant MFA in 2025: Buyer’s Guide to NIST SP 800-63-4 & OMB M-22-09 — WWPass blog-Insights into Authentication & Security](https://www.wwpass.com/blog/phishing-resistant-mfa-in-2025-buyer-s-guide-to-nist-sp-800-63-4-omb-m-22-09/)
31. [OAuth best practices: We read RFC 9700 so you don’t have to — WorkOS](https://workos.com/blog/oauth-best-practices)
32. [Top Takeaways from the 2026 Verizon Data Breach Investigations Report](https://spycloud.com/blog/top-takeaways-from-the-2026-verizon-data-breach-investigations-report/)
33. [OWASP Top 10 2025 - Revised Version Released With Two New Categories](https://cybersecuritynews.com/owasp-top-10-2025/)
34. [OWASP API Security Top 10: The 2026 Guide With Examples](https://hackerdna.com/blog/owasp-api-security-top-10)
35. [OWASP API Top 10: Testing Authorisation Failures](https://www.adayptus.com/blog/owasp-api-security-top-10-testing-authorisation)
36. [OWASP API Security Top 10 (2023): What Changed and How to Fix it](https://zerothreat.ai/blog/introduction-to-owasp-top-10-api-security-risks)
37. [MITRE Releases Top 25 Most Dangerous Software Weaknesses of 2025](https://cybersecuritynews.com/mitre-releases-top-25-most-dangerous-software/)
38. [CISA Known Exploited Vulnerabilities (KEV) Soared 20% In 2025](https://thecyberexpress.com/cisa-known-exploited-vulnerabilities-kev-2025/)
39. [Top 10 web hacking techniques of 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025)
40. [2025 CWE Top 25 Most Dangerous Software Weaknesses](https://www.hackerstorm.com/articles/our-blog/government-regulatory-alerts/2025-cwe-top-25-most-dangerous-software-weaknesses)
41. [Top 10 web hacking techniques of 2025: call for nominations](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025-nominations-open)
42. [PortSwigger Research Sheds Light on HTTP1.1 Vulnerabilities Urges Industry Shift Toward Safer Protocols](https://www.businesswire.com/news/home/20250806802876/en/PortSwigger-Research-Sheds-Light-on-HTTP1.1-Vulnerabilities-Urges-Industry-Shift-Toward-Safer-Protocols)
43. [Identity and Access Management - Amazon EKS](https://docs.aws.amazon.com/eks/latest/best-practices/identity-and-access-management.html)
44. [Exploiting SNI SSRF to access the AWS IDMSv2 service](https://appcheck-ng.com/exploiting-sni-ssrf-to-access-the-aws-idmsv2-service/)
45. [AWS Security Blog](https://aws.amazon.com/blogs/security/defense-in-depth-open-firewalls-reverse-proxies-ssrf-vulnerabilities-ec2-instance-metadata-service/)
46. [OWASP API Security Top 10 (2023): A Cloud-Native Guide for Security Teams](https://orca.security/resources/blog/owasp-api-security-top-10/)
47. [OWASP API Security Top 10 Explained (2023)](https://cyberfortify.co/blog/owasp-api-security-top-10)
48. [Why Certificate Lifetimes Are Getting Shorter - Blog](https://generatorlabs.com/blog/why-certificate-lifetimes-are-getting-shorter)
49. [The 47-Day Certificate Schedule: SC-081v3, DCV Reuse, and What to Automate](https://tlsradar.com/blog/sc-081-certificate-validity-schedule)
50. [NIST IR 8547 Explained: 2030 and 2035 PQC Deadlines](https://www.encryptionconsulting.com/nist-ir-8547-2030-2035-action-plan/)
51. [The Colossus with Feet of Clay: Debunking Encrypted Traffic Classifiers under PQC Evolution](https://arxiv.org/pdf/2608.22683)
52. [Aquaman: A Transparent Proxy Architecture for Quantum Resilient Key Establishment](https://arxiv.org/pdf/2605.06932)
53. [What Changed in OWASP Top 10 2025? Full Breakdown & Recommendations](https://blog.qualys.com/qualys-insights/2026/06/15/what-changed-in-owasp-top-10-2025-and-recommendations-for-each-category)
54. [FBI breach shows the patching problem is getting harder for CIOs](https://informationweek.com/cybersecurity/fbi-breach-exposes-enterprise-patching-crisis)
55. [SLSA Deep Dive: Securing the Supply Chain Using Verifiable Levels - DEV Community](https://dev.to/kanywst/slsa-deep-dive-securing-the-supply-chain-using-verifiable-levels-klk)
56. [Understanding SLSA: Tracks, Levels, and the Checks at Each Step](https://blog.shivamsaraswat.com/understanding-slsa/)
57. [PCI DSS 6.4.3 & 11.6.1 Compliance Tools: 2026 Comparison](https://cside.com/blog/solution-comparison-pci-dss-6-4-3-and-11-6-1)
58. [PCI DSS 4.0 Requirements: Key Updates and What They Mean](https://www.securetrust.com/blog/pci-4-0-requirements)
59. [OWASP ASVS: Levels 1-3, Controls & Verification Checklist](https://cybersigmacs.com/knowledge-center/owasp-asvs/)
60. [OWASP Top 10 For LLM Applications 2025](https://www.indusface.com/learning/owasp-top-10-llm/)
61. [OWASP Top 10 for LLMs 2025: Key Risks and Mitigation Strategies](https://www.invicti.com/blog/web-security/owasp-top-10-risks-llm-security-2025)
62. [OWASP Top 10 for Agentic Applications 2026](https://www.aigl.blog/owasp-top-10-for-agentic-applications-2026/)
63. [AI can write your code, but nearly half of it may be insecure - Help Net Security](https://www.helpnetsecurity.com/2025/08/07/create-ai-code-security-risks/)
64. [AI-Generated Code Poses Major Security Risks in Nearly Half of All Development Tasks, Veracode Research Reveals](https://www.businesswire.com/news/home/20250730694951/en/AI-Generated-Code-Poses-Major-Security-Risks-in-Nearly-Half-of-All-Development-Tasks-Veracode-Research-Reveals)
65. [2026 GenAI Code Security Report](https://community.veracode.com/s/question/0D5Uf00001PQu6yKAD/2026-genai-code-security-report)
66. [NIST SSDF 1.2 Draft Walkthrough](https://safeguard.sh/resources/blog/nist-ssdf-1-2-draft-public-comment-2026)
67. [NCSC warns of confusion over true nature of AI prompt injection](https://www.computerweekly.com/news/366636155/NCSC-warns-of-confusion-over-true-nature-of-AI-prompt-injection)
68. [NCSC Alert: Why Prompt Injection May Be a Permanent Flaw in the AI Landscape](https://www.indianic.com/blog/ncsc-alert-why-prompt-injection-may-be-a-permanent-flaw-in-the-ai-landscape/)
69. [Mistaking AI vulnerability could lead to large-scale breaches, NCSC warns](https://www.ncsc.gov.uk/news/mistaking-ai-vulnerability-could-lead-to-large-scale-breaches)
70. [OWASP Top 10 2026: All 10 Risks Explained (Complete Guide)](https://www.reflectiz.com/blog/owasp-top-ten-2026/)
71. [Key findings from the Verizon DBIR 2026: Slower vulnerability remediation meets faster exploitation](https://connect.tenable.com/discussions/vulnerability-watch/key-findings-from-the-verizon-dbir-2026-slower-vulnerability-remediation-meets-f/111972)
72. [CISA KEV Catalog Expanded 20% in 2025, Topping 1,480 Entries - SecurityWeek](https://www.securityweek.com/cisa-kev-catalog-expanded-20-in-2025-topping-1480-entries/)
73. [Security Checklist](https://kubernetes.io/docs/concepts/security/security-checklist/?amp=&amp=)
74. [Enforce Pod Security Standards with Namespace Labels](https://www.kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/)
75. [Pod Security Admission](https://www.kubernetes.io/docs/concepts/security/pod-security-admission/)
76. [Achieving PCI DSS 4.0.1 Compliance with API Security](https://www.cequence.ai/blog/api-security/pci-dss-4-compliance-api-security/)
77. [PCI DSS 4.0 Requirement 6: Software Security Guide](https://safeguard.sh/resources/blog/pci-dss-4-requirement-6-guide)
78. [Shai-Hulud npm Supply Chain Attack: What to Know](https://panther.com/blog/shai-hulud-npm-supply-chain-attack)
79. [Shai-Hulud 2.0 Worm Supply-Chain Attack on npm Dependencies](https://www.invicti.com/blog/web-security/shai-hulud-2-worm-supply-chain-attack-on-npm-dependencies)
80. [2026 Data Breach Investigations Report (DBIR)](https://www.verizon.com/business/resources/reports/dbir/)
81. [NIST enhances SP 800-53 controls to improve cybersecurity and software maintenance, reduce cyber risks - Industrial Cyber](https://industrialcyber.co/nist/nist-enhances-sp-800-53-controls-to-improve-cybersecurity-and-software-maintenance-reduce-cyber-risks/)
82. [Coffee with the Council Podcast: Guidance for PCI DSS E-commerce Requirements Effective After 31 March 2025](https://blog.pcisecuritystandards.org/coffee-with-the-council-podcast-guidance-for-pci-dss-e-commerce-requirements-effective-after-31-march-2025)
83. [Important Updates Announced for Merchants Validating to Self-Assessment Questionnaire A](https://blog.pcisecuritystandards.org/important-updates-announced-for-merchants-validating-to-self-assessment-questionnaire-a)
84. [Secure Software Development Framework (SSDF) Version 1.2 is Available for Public Comment](https://www.nist.gov/news-events/news/2025/12/secure-software-development-framework-ssdf-version-12-available-public)
85. [NIST SP 800-53](https://en.wikipedia.org/wiki/NIST_Special_Publication_800-53)
86. [NIST SP 800-63-3 & 63-4: Digital Identity Guidelines](https://www.hypr.com/blog/nist-sp-800-63-3-digital-identity-guidelines-review)
87. [Exploited vulnerabilities accelerated in 2025, CISA KEV catalog shows](https://www.scworld.com/brief/exploited-vulnerabilities-accelerate-in-2025-cisa-kev-catalog-shows)
88. [Prompt Injection Attacks: Examples, Techniques, and Defence](https://blog.cyberdesserts.com/prompt-injection-attacks/)
