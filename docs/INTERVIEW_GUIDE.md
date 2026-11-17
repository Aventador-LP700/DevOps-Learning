# Interview guide

Use observations and residual risk, not a claim that installing a tool proves security.

## 06 — Broken Object Level Authorization

**Would UUIDs fix IDOR?**
No. Hard-to-guess identifiers reduce enumeration but do not enforce ownership.

**How would you verify the remediation?**
Observe Alice receiving Bob’s synthetic order 200; correlate authenticated subject, object ID and authorization decision. Then replay the attack against the separate fixed module and check its positive regression.

## 07 — Broken Function Level Authorization

**How does BFLA differ from BOLA?**
BOLA checks access to a particular object; BFLA checks permission to invoke a privileged operation.

**How would you verify the remediation?**
Record attempted administrative action, authenticated role, target and allow/deny decision. Then replay the attack against the separate fixed module and check its positive regression.

## 08 — Mass Assignment

**Why is binding a request directly to a model dangerous?**
The model often contains internal fields, such as roles, that should never be client-writable.

**How would you verify the remediation?**
Watch for protected fields in profile-update requests and audit rejected privilege changes. Then replay the attack against the separate fixed module and check its positive regression.

## 09 — Server-Side Request Forgery

**Why is URL string filtering insufficient in production?**
Parsing ambiguities, redirects and DNS changes can make a permitted-looking URL reach a different destination.

**How would you verify the remediation?**
The internal mock request log shows an unauthorized metadata read; the hardened retest adds no internal request. Then replay the attack against the separate fixed module and check its positive regression.

## 10 — CORS Misconfiguration

**Can wildcard origins be used with credentials?**
Browsers reject that combination. Reflecting arbitrary origins with credentials is the dangerous working pattern shown here.

**How would you verify the remediation?**
Inspect response ACAO/ACAC headers and confirm read access from a second origin in a real browser. Then replay the attack against the separate fixed module and check its positive regression.

## 11 — Debug Information Disclosure

**Should an error return HTTP 200 to hide the failure?**
No. Keep accurate failure status while removing sensitive detail from the public body.

**How would you verify the remediation?**
Trigger the synthetic failure and inspect response content, status code and request correlation identifier. Then replay the attack against the separate fixed module and check its positive regression.

## 12 — Local Dependency Confusion

**Why does a version lock alone not establish publisher trust?**
A lock needs an authenticated source and trusted content identity; an attacker may control a competing source or mutable metadata.

**How would you verify the remediation?**
The loopback registry logs both namespace queries and the selected package identity and version. Then replay the attack against the separate fixed module and check its positive regression.

## 13 — Untrusted Build Dependency

**Why can installing a development dependency compromise a pipeline?**
Package build/install hooks can execute before the application runs and may inherit the runner’s privileges and secrets.

**How would you verify the remediation?**
A temporary marker proves the local dependency hook actually executed; compare it after the fixed path. Then replay the attack against the separate fixed module and check its positive regression.

## 14 — Weak Password Storage

**What does a salt protect against?**
It prevents identical-password hash equality and cross-account precomputation reuse; it does not add entropy to the password.

**How would you verify the remediation?**
Compare equal weak hashes, salted record differences, wrong-password rejection and KDF record validation. Then replay the attack against the separate fixed module and check its positive regression.

## 15 — SQL Injection

**Can placeholders bind a table name?**
Usually not. Bind data values; map dynamic identifiers to an explicit allowlist instead of interpolating user input.

**How would you verify the remediation?**
The injected owner returns both rows from the actual SQLite database; bound parameters return no rows for the same input. Then replay the attack against the separate fixed module and check its positive regression.

## 16 — Stored Cross-Site Scripting

**Why is CSP not a substitute for output encoding?**
CSP is defense in depth and can be weakened or bypassed by application changes; correct data-to-DOM handling removes the injection primitive.

**How would you verify the remediation?**
Inspect parsed script elements and run the browser regression proving execution in the vulnerable page only. Then replay the attack against the separate fixed module and check its positive regression.

## 17 — OS Command Injection

**Does shell escaping solve every command-injection problem?**
No. Prefer avoiding the shell; argument injection and option handling still need validation even with argument arrays.

**How would you verify the remediation?**
The harmless command writes a temporary rce-proof marker; the fixed implementation rejects the same input. Then replay the attack against the separate fixed module and check its positive regression.

## 18 — Path Traversal

**Why check the resolved path rather than a ../ substring?**
Encoding and symlinks can escape lexical checks; canonical resolution checks where the file actually points.

**How would you verify the remediation?**
The traversal reads the fake private payroll file; resolved-path and symlink tests verify the public-root control. Then replay the attack against the separate fixed module and check its positive regression.

## 19 — Coupon Reuse / Business Logic Bypass

**Why is a check-then-insert pattern risky?**
Concurrent requests can both observe no redemption. A database uniqueness constraint makes the invariant atomic.

**How would you verify the remediation?**
Compare repeated discounted purchases and the fixed database redemption ledger. Then replay the attack against the separate fixed module and check its positive regression.

## 20 — Missing Login Rate Limiting

**Is per-IP throttling sufficient?**
No. Distributed clients can rotate addresses, so combine account, network and risk-based signals.

**How would you verify the remediation?**
Six dummy attempts show 401 indefinitely in the vulnerable path and 429 after three failures in the fixed path. Then replay the attack against the separate fixed module and check its positive regression.

## 21 — Session Fixation

**When should session identifiers rotate?**
At authentication and privilege changes, with the prior identifier invalidated and appropriate cookie protections.

**How would you verify the remediation?**
Observe the old identifier resolving to an authenticated user, then test its invalidation after secure rotation. Then replay the attack against the separate fixed module and check its positive regression.

## 22 — Unsafe Deserialization

**Can a pickle be made safe simply by hiding its class names?**
No. Pickle is a Python object execution format; do not accept it from untrusted producers.

**How would you verify the remediation?**
A temporary marker proves callable execution during unpickling; the JSON-only path creates no marker. Then replay the attack against the separate fixed module and check its positive regression.

## 23 — Unauthenticated Artifact Acceptance

**How does authenticity differ from a plain checksum?**
An attacker can recompute an unkeyed checksum. A protected-key authenticator requires access to the trusted producer key.

**How would you verify the remediation?**
An attacker-selected artifact with a valid self-supplied digest is accepted, while an authenticated envelope is required by the fixed path. Then replay the attack against the separate fixed module and check its positive regression.

## 24 — Missing Security Audit Logs

**Should audit logs record only successful actions?**
No. Denied privileged actions are useful attack signals; avoid logging credentials or unnecessary personal data.

**How would you verify the remediation?**
Inspect missing vulnerable log output versus structured allowed/denied events in the fixed JSONL log. Then replay the attack against the separate fixed module and check its positive regression.

## 25 — Fail-Open Error Handling

**Why is retrying an authorization error not enough?**
Retries can fail too. The terminal decision must still deny when policy cannot be established.

**How would you verify the remediation?**
Inject a real TimeoutError and compare authorization decisions; test healthy allow/deny and malformed backend responses. Then replay the attack against the separate fixed module and check its positive regression.

## CI/CD fundamentals

**Why do the lab report and release gate have different outcomes?**
The lab succeeds when the insecure behavior is reproduced and its fix is verified. A release gate evaluates actual artifact risk and must still block unacceptable findings.

**Which claims are simulations?**
The registry is a local JSON index, the build-hook fixture is not a package installer, HMAC is not public-key signing, and JSONL is not a SIEM. Kubernetes API requests and the browser CORS/XSS tests are real integrations.
