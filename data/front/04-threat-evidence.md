# Threat evidence


Exploiting known vulnerabilities is now the most common way breaches begin, and remediation is slowing while exploitation speeds up. That shifts priority toward patch latency, supply-chain integrity and authorisation, ahead of injection classes that frameworks largely close by construction.

| Signal | Earlier | Latest | Fact |
| --- | --- | --- | --- |
| Exploitation as initial access vector (Verizon DBIR) | 20%, second to credential abuse (2025) | 31%, top vector (2026) | F-20, F-21 |
| Third-party involvement in breaches | 15% (2024) → 30% (2025) | 48% (2026) | F-22 |
| Ransomware present in breaches; victims not paying | 44%; 64% (2025) | 48%; 69% (2026) | F-23 |
| Median time to full patching | 32 days | 43 days (2026 report) | F-24 |
| Share of KEV-listed vulnerabilities fully patched | 38% | 26% (2026 report) | F-24 |
| Attack techniques assisted by generative AI | — | 15% (2026 report) | F-25 |
| CISA KEV additions per year | 187 (2023), 185 (2024) | 245 (2025); 1,484 total, 24 linked to ransomware | F-26 |

Two further sources show where weaknesses and research effort concentrate:

- **Weakness frequency:** the 2025 CWE Top 25, ranked from CVE data, puts cross-site scripting, SQL injection, CSRF and missing authorisation in its first four places (F-27). The ranking reflects CVE volume and severity across all software, not breach frequency.
- **Offensive research:** PortSwigger’s top ten web hacking techniques of 2025 cluster around template injection, ORM data leaks, blind SSRF, Unicode normalisation, cross-site leaks, framework cache poisoning and parser differentials (F-28). These are the classes most likely to defeat controls designed for older attack forms.

The ranking sources measure different things and should not be expected to agree: the OWASP Top 10 blends incidence data with a practitioner survey, the CWE Top 25 counts CVE records, and the DBIR counts breaches.

**Facts and sources.** Facts: F-20 to F-28. Sources: R-2, R-21 to R-26.

**Last reviewed** Oct 12, 2026 · **Watch:** each annual DBIR (usually May); CWE Top 25 (usually December); PortSwigger top ten (usually February); KEV annual totals.
