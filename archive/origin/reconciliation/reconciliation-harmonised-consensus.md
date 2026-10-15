# Harmonised consensus

Each of the 25 agreed points below is a single merged statement, ready to drop into the final report. Six rules governed the merge:

1. The shared position leads; detail from either report follows where it adds substance.
2. Corrections from the Inclusion review apply to any detail carried in.
3. Where a point touches an open disagreement, only the agreed part is stated and the D-number marks the rest.
4. Absolute words from either report (“immune”, “neutralizes”, “industry consensus”) are dropped unless a source supports them.
5. Figures carry their edition or date.
6. A “Sourcing” note flags points where both reports rest on thin or secondary evidence.

## Threat evidence

**C1 · Breach trends.** Exploitation of vulnerabilities has overtaken stolen credentials as the leading way attackers first get into breached organisations, per Verizon’s DBIR. The shift was under way in the 2025 edition and complete in 2026, when exploitation became the top vector overall for the first time in the report’s history. Stolen credentials remain the top action within Basic Web Application Attacks, so both credential and patching controls stay priorities. *Resolved (D1): exploitation rose from 20% (DBIR 2025, second to credential abuse) to 31% (DBIR 2026, top vector).*

**C2 · Patch latency.** DBIR 2026 reports median time to patch rising from 32 to 43 days, while KEV-listed “must-patch” vulnerabilities increased. Remediation is falling behind exploitation. *Sourcing (checked): SecurityWeek’s DBIR 2026 coverage describes it as median time to full patching, scope unstated; organisations fully patched 26% of KEV vulnerabilities, down from 38%. The Gemini report’s “critical vulnerabilities” qualifier is unsupported and dropped.*

**C3 · AI and exploitation.** AI is shortening the interval between vulnerability disclosure and working exploit, which compounds the patch-latency gap in C2. *Sourcing (checked): DBIR 2026 says threat actors use AI to speed exploitation and that the defensive window has shrunk “from months to hours”, which supports the Gemini report’s “within hours”. The median actor used AI across 15 documented techniques. No time-to-exploit statistic is given.*

## Standards and risk lists

**C4 · OWASP Top 10:2025.** The 2025 list is: A01 Broken Access Control, A02 Security Misconfiguration, A03 Software Supply Chain Failures, A04 Cryptographic Failures, A05 Injection, A06 Insecure Design, A07 Authentication Failures, A08 Software or Data Integrity Failures, A09 Security Logging & Alerting Failures, A10 Mishandling of Exceptional Conditions. Against 2021:

- SSRF is folded into A01 as an access-control failure.
- Misconfiguration rises to second.
- Software Supply Chain Failures widens the old Vulnerable and Outdated Components to cover build pipelines and distribution.
- Injection, which includes XSS, drops to fifth as frameworks close SQL injection structurally.
- A10 is new and covers fail-open and error-leakage paths.

The list ranks risks for awareness and is not a testable standard. *Sourcing: confirmed against top10.owasp.org. The Gemini report’s table names “Sensitive Data Exposure” as the 2021 predecessor of A04, but that name was already retired in 2021, so the row is dropped.*

**C7 · ASVS 5.0.0.** OWASP ASVS 5.0.0 (May 2025) is the verifiable requirements standard for application security: 17 chapters, three levels that scale verification rigour to an application’s risk, and new standalone chapters including V10 OAuth and OIDC and V17 WebRTC. Organisations assign a level per application, with L2 the usual target for applications handling sensitive data. *Resolved (D4): use the published 5.0 chapter list — V1 Encoding and Sanitization through V17 WebRTC, with V6 Authentication, V7 Session Management and V15 Secure Coding and Architecture.*

**C8 · OWASP API Security Top 10 (2023).** The 2023 list remains current. Three of its top five risks are authorisation failures, attacked by changing identifiers, methods or JSON properties in otherwise valid requests:

- API1 Broken Object Level Authorization
- API3 Broken Object Property Level Authorization, which merges mass assignment and excessive data exposure
- API5 Broken Function Level Authorization

The rest of the list: API2 Broken Authentication, API4 Unrestricted Resource Consumption, API6 Unrestricted Access to Sensitive Business Flows, API7 SSRF, API8 Security Misconfiguration, API9 Improper Inventory Management, API10 Unsafe Consumption of APIs. API10 treats third-party API responses as untrusted input. *Sourcing: both reports use vendor summaries; cite the OWASP API Security project.*

## Identity and access

**C5 · Access control.** Every request to every object is authorised on the server, and the absence of a rule means deny. Broken access control tops the OWASP list because the flaw lives in application logic: a request with a changed object ID or manipulated client state looks legitimate to a scanner. Detection therefore needs authorisation-aware tests built on ownership semantics, not generic scanning. *Resolved (D9): the fix is a per-object authorisation check tied to the principal; RBAC covers function access, and random identifiers are defence in depth only.*

**C6 · Fine-grained authorisation.** Role-based access control alone does not express per-object sharing in multi-tenant or collaborative systems. Relationship-based access control on the Zanzibar model, as implemented in OpenFGA, stores permissions as relation tuples and answers checks by graph reachability through a central policy service. It sits alongside RBAC for coarse function access and ABAC for contextual rules, not in place of them.

**C10 · JSON Web Tokens.** JWT validation must pin the algorithm server-side, because `alg: none` and asymmetric-to-symmetric algorithm confusion let attackers forge tokens. Self-contained tokens cannot be withdrawn before expiry without reintroducing a server-side lookup, so short lifetimes need a revocation path. The common pattern pairs short-lived access tokens with rotating refresh tokens held in `HttpOnly` cookies; opaque reference tokens and sender-constrained tokens (DPoP) are alternatives. *Sourcing: re-source to the OWASP JWT Cheat Sheet and RFC 9700.*

**C11 · Passkeys.** WebAuthn/FIDO2 passkeys are phishing-resistant because each credential is bound to the origin that registered it, and the private key never leaves the authenticator or its sync fabric. Cloud synchronisation solves device loss by moving the trust boundary to the user’s platform account (Apple, Google), so that account’s security and recovery become part of the authentication assurance. *Dual position (D8): the credential cannot be phished, but accounts with phishable fallbacks or stolen post-login sessions stay exposed.*

**C25 · Zero trust.** No request is trusted for its network location. Each hop, including service-to-service calls, is authenticated and authorised against policy. NIST SP 800-207 models this as a Policy Engine and Policy Administrator (the decision point) programming a Policy Enforcement Point in the data path. SP 800-207A applies the model to cloud-native services, where tokens issued at the edge are validated at each internal hop.

## Protocol, browser and API mechanics

**C9 · GraphQL resource exhaustion.** Client-shaped queries shift cost control to the server, so deeply nested or wide queries can exhaust backend resources. Depth limits stop recursive nesting. Query cost analysis catches shallow but expensive queries by weighting each field, computing the total from the parsed query before execution, and rejecting anything over budget. Production APIs also disable introspection and cap batched operations.

**C12 · HTTP request smuggling.** Smuggling arises when a front-end and back-end disagree on where an HTTP/1.1 request ends:

- **CL.TE / TE.CL:** conflicting Content-Length and Transfer-Encoding headers.
- **TE.TE:** an obfuscated Transfer-Encoding header that one hop honours and the other ignores.
- **HTTP/2 downgrade:** front-ends that pass forbidden headers into HTTP/1.1 translation.

The leftover bytes prefix the next user’s request on a reused connection, enabling session capture, cache poisoning and filter bypass. Mitigation is HTTP/2 end-to-end, including edge-to-origin, plus rejection of ambiguous requests at the edge. *Open on retiring HTTP/1.1 upstreams: carried in the Claude report as a contested position.*

**C13 · Cross-site WebSocket hijacking.** Browsers attach ambient cookies to a cross-site WebSocket handshake and apply no same-origin check to the connection. An attacker page can therefore open an authenticated, two-way channel as the victim and both act and read. Unlike blind CSRF, the attacker sees responses. The server must validate `Origin` on the upgrade request and should not rely on cookies alone; a token sent in the first message avoids query-string leakage into logs. SameSite=Lax blocks cross-site attempts but not same-site ones, such as a compromised sibling subdomain, as CVE-2024-26135 (MeshCentral) showed.

**C14 · WAF bypass.** WAFs fail when they parse a request differently from the application behind them. Malformed multipart, XML or JSON structure can hide a payload the WAF cannot parse, and Unicode a backend narrows or normalises differently can carry an attack in. Peer-reviewed fuzzing (WAFFLED, ACSAC 2025) found 1,207 such bypasses across five major WAFs. Strict RFC normalisation at ingress narrows the gap. Parameterisation and output encoding behind the WAF remain the real fix, so a WAF is a compensating control.

**C15 · Content Security Policy.** Allow-list CSPs are routinely bypassed through JSONP endpoints and other script on trusted domains. A strict CSP uses per-response nonces or hashes with `strict-dynamic`, which defeats those bypasses. Script gadgets in trusted libraries can still turn injected markup into execution under a strict CSP, so Trusted Types and avoiding gadget-prone libraries complete the defence.

## Cloud-native

**C17 · Cloud metadata SSRF.** IMDSv1 handed instance IAM credentials to any GET to 169.254.169.254, which made SSRF a direct route to cloud credentials. IMDSv2 requires a session token obtained by a PUT with a TTL header, refuses token requests carrying `X-Forwarded-For`, and with hop limit 1 keeps tokens from leaving the instance. AWS positions this as defence against unpatched SSRF and open reverse proxies. *Dual position (D7): effective against URL-only SSRF; full-request SSRF can still obtain a token, so egress controls remain.*

**C18 · Kubernetes service-account tokens.** Kubernetes mounts a service-account token into pods by default. An attacker who can read files in the pod, via local file read or an SSRF that supports `file://`, can use it against the in-cluster API server. Impact depends on the RBAC bindings granted to that account: default accounts hold little, and over-broad bindings (listing secrets, creating workloads) turn a foothold into cluster or cloud compromise. Disable automounting where pods do not call the API, and bind least-privilege roles. Separately, CVE-2026-4789 shows an admission controller (Kyverno) making SSRF requests from its own privileged pod; exploiting it requires permission to create namespaced policies.

**C19 · Serverless.** A function’s attack surface is its code, its event sources, its execution role and its dependencies:

- **Events:** queue messages, storage notifications and stream records are untrusted input and need the same validation as HTTP requests (event-data injection).
- **Roles:** an over-privileged execution role turns any code flaw into broad cloud access, so roles are scoped per function.
- **Warm reuse:** platforms reuse a function’s execution environment across invocations, so secrets or user data left in globals or `/tmp` can leak between requests from different users of the same function.

## Supply chain, payments and cryptography

**C16 · PCI DSS client-side requirements.** Magecart-style skimmers run in the shopper’s browser, out of sight of server-side controls, so PCI DSS v4 brings payment-page scripts into scope. Both requirements became mandatory on 31 March 2025:

- **Requirement 6.4.3:** an inventory of every script on the page, a written business justification for each, and a method to authorise scripts and assure their integrity.
- **Requirement 11.6.1:** detection of unauthorised changes to the page’s security-relevant headers and content as the browser receives them.

CSP is the usual authorisation mechanism. *Resolved (D6): v4.0.1 requires “a method” to assure integrity; SRI is one option, suited to static scripts.*

**C20 · Supply-chain threats.** Attackers reach applications through what they import and how it is built: typosquatted and dependency-confusion packages, hijacked maintainer accounts, and compromised CI/CD pipelines. The Shai-Hulud npm worm (from September 2025, with later waves through 2026) is the reference case. It steals developer and CI tokens, then republishes poisoned versions of every package those tokens can reach, so one theft spreads across the registry.

**C21 · SLSA.** SLSA’s build track sets levels of build integrity for software artefacts:

- **L1:** provenance exists.
- **L2:** provenance is signed and generated by a hosted build platform rather than a developer machine.
- **L3:** builds are isolated so one run cannot tamper with another or reach signing secrets.

Provenance records where and how an artefact was built, not whether its source is benign. Mini Shai-Hulud (May 2026) shipped cryptographically valid provenance from a hijacked workflow; SLSA’s own analysis says L3 isolation would have blocked its cache-poisoning vector. *Resolved (D5): SBOMs are separate from provenance, and L3 does not require reproducible builds.*

**C22 · Reachability in software composition analysis.** Manifest-only SCA flags every dependency with a known CVE, burying teams in findings for code that is never called. Reachability analysis traces call graphs from application entry points into transitive dependencies and deprioritises vulnerabilities in unreachable functions. It lowers priority without removing the dependency, so it complements patching rather than replacing it.

**C23 · Post-quantum cryptography.** Adversaries can record encrypted traffic now and decrypt it once a cryptographically relevant quantum computer exists (harvest now, decrypt later). This makes key exchange the first migration priority. NIST finalised ML-KEM (FIPS 203), ML-DSA (FIPS 204) and SLH-DSA (FIPS 205) in August 2024. Hybrid TLS 1.3 key exchange, which combines a classical curve with ML-KEM (X25519MLKEM768), is already widely deployed, at the cost of larger handshakes. *Dual position (D10): NIST and BSI favour hybrid (BSI requires it); NSA CNSA 2.0 targets pure ML-KEM-1024 for national security systems.*

**C24 · Field-level encryption.** Storage- or disk-level encryption does not protect data from database administrators, compromised application credentials or the hosting provider. Encrypting sensitive fields individually, ideally in the client or application before data reaches the store, keeps plaintext out of the database. Deterministic encryption allows exact-match queries on encrypted fields but reveals which records share a value. Randomised encryption or tokenisation suits fields that are never queried.
