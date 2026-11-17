# Scenario audit

Audit baseline: `d08044f`. Date: 17 November 2026.

**No README-only scenarios were found.** Every entry has executable code or real
Kubernetes manifests, a fixed counterpart and an automated proof. This does not
mean 25 separate web servers: most are Python module exercises; scenario 03's
unchecked JSON consumption is in `lab/scenarios.py`, and scenario 05 is a real
Kubernetes Role/API exercise. The registry/index and high-risk execution proofs
use the constrained simulations described in their walkthroughs.

## Findings and fixes

1. **Scenario 19: null-principal coupon reuse.** `checkout(db, None, 'ONCE10')`
   succeeded repeatedly because a nullable SQLite UNIQUE key permits multiple NULL
   values. The fixed function now requires a nonempty principal before touching the
   ledger; the example ledger also has NOT NULL columns. A regression deliberately
   uses the older nullable schema, so the function cannot pass merely by relying on
   a changed fixture. A concurrent-redemption test verifies the atomic invariant.
2. **Scenario 13: incomplete metadata validation.** A matching digest with
   `name: null` and `version: {}` was accepted. The fixed builder now checks the JSON
   object schema, nonempty string fields, bounded field sizes and metadata size,
   returning a controlled rejection for malformed JSON. It never executes hooks.
3. **Classification ambiguity.** The official 2025 CWE lists place CWE-915,
   CWE-427 and CWE-829 under A08, despite the related access-control/supply-chain
   themes. Scenarios 08, 12 and 13 now show A08 first, with A01/A03 as related
   context. CWE-209's primary group is A10 (scenario 11); A02 remains related debug
   configuration context. The original four local mappings are clarified centrally
   without editing their implementations. Scenario 05's CWE-250/A01 mapping is
   explicitly contextual least privilege, not a claim that CWE-250 is in OWASP's
   enumerated A01 list.
4. **Proof coverage.** Added independent checks that execute the actual hardened
   gate CLI, replay metadata/log attacks, check protected-field atomicity, dependency
   identity/digest validation, the real scrypt record and artifact authentication.
   The complete inventory fails for missing implementations. The all-scenario audit
   rejects stale/failed Kubernetes evidence rather than synthesizing scenario 05.
5. **Documentation cleanup.** Removed unrelated promotional guides and retained
   technical Q&A as [knowledge checks](KNOWLEDGE_CHECKS.md). The remaining
   [demonstration guide](DEMO_GUIDE.md) contains only technical operating steps.

No executable code, proof script, pipeline, manifest or walkthrough for the
original five scenarios was changed. [Recorded file hashes](evidence/audit-preserved-files.json)
verify 17 original implementation/proof/documentation files against the baseline.
The Kubernetes workflow only gained an audit step and report upload after its
existing real API test.

## Exact locally executed results

| Run | Tests | Passed | Failed | Errors | Skipped |
|---|---:|---:|---:|---:|---:|
| Baseline unit/integration | 89 | 89 | 0 | 0 | 0 |
| Baseline browser | 2 | 2 | 0 | 0 | 0 |
| Added regressions, before fixes | 11 | 9 | 2 | 0 | 0 |
| Added regressions, after fixes | 11 | 11 | 0 | 0 | 0 |
| Final unit/integration | 106 | 106 | 0 | 0 | 0 |
| Final browser | 2 | 2 | 0 | 0 | 0 |

The pre-fix failures are retained rather than replaced by the passing results.
[Before-fix log](evidence/audit-before-fix.txt),
[final unit log](evidence/audit-unit-tests.txt),
[final browser log](evidence/audit-browser-tests.txt) and
[machine-readable counts](evidence/audit-test-summary.json) record actual executions.

Local scenario audit: **24 PASS, 0 FAIL, 1 NOT_RUN**. Its exit code is 2 because a
complete audit still needs real Kubernetes evidence. This is intentional: a source
inspection or an old hosted run is not a freshly executed scenario 05.

## All 25 implementations and classifications

Primary category is shown first. Related themes do not assert official CWE-list
membership. Full source/proof/test paths and SHA256s appear in the
[local audit JSON](evidence/audit-local-scenarios.json).

| ID | Scenario | Executable pair | OWASP 2025 / CWE | Local proof result |
|---|---|---|---|---|
| 01 | [pipeline-injection](../scenarios/01-pipeline-injection/README.md) | [vulnerable](../pipelines/vulnerable/metadata.py) / [fixed](../pipelines/hardened/metadata.py) | A05 / CWE-78 | PASS locally |
| 02 | [secret-exposure](../scenarios/02-secret-exposure/README.md) | [vulnerable](../pipelines/vulnerable/secrets.py) / [fixed](../pipelines/hardened/secrets.py) | A09; related A02 / CWE-532 | PASS locally |
| 03 | [artifact-tampering](../scenarios/03-artifact-tampering/README.md) | [vulnerable](../lab/scenarios.py) / [fixed](../lab/controls.py) | A08 / CWE-353 | PASS locally |
| 04 | [security-gate-bypass](../scenarios/04-security-gate-bypass/README.md) | [vulnerable](../pipelines/vulnerable/gate.py) / [fixed](../pipelines/hardened/gate.py) | A06; related A02 / CWE-693 | PASS locally |
| 05 | [excessive-permissions](../scenarios/05-excessive-permissions/README.md) | [vulnerable](../infra/kubernetes/vulnerable-rbac.yaml) / [fixed](../infra/kubernetes/hardened-rbac.yaml) | A01 / CWE-250 | NOT RUN locally; real API required |
| 06 | [idor-bola](../scenarios/06-idor-bola/README.md) | [vulnerable](../labs/idor_bola/vulnerable.py) / [fixed](../labs/idor_bola/secure.py) | A01 / CWE-639 | PASS locally |
| 07 | [broken-function-level-authorization](../scenarios/07-broken-function-level-authorization/README.md) | [vulnerable](../labs/broken_function_level_authorization/vulnerable.py) / [fixed](../labs/broken_function_level_authorization/secure.py) | A01 / CWE-862 | PASS locally |
| 08 | [mass-assignment](../scenarios/08-mass-assignment/README.md) | [vulnerable](../labs/mass_assignment/vulnerable.py) / [fixed](../labs/mass_assignment/secure.py) | A08; related A01 / CWE-915 | PASS locally |
| 09 | [ssrf](../scenarios/09-ssrf/README.md) | [vulnerable](../labs/ssrf/vulnerable.py) / [fixed](../labs/ssrf/secure.py) | A01 / CWE-918 | PASS locally |
| 10 | [cors-misconfiguration](../scenarios/10-cors-misconfiguration/README.md) | [vulnerable](../labs/cors_misconfiguration/vulnerable.py) / [fixed](../labs/cors_misconfiguration/secure.py) | A02 / CWE-942 | PASS locally |
| 11 | [debug-information-disclosure](../scenarios/11-debug-information-disclosure/README.md) | [vulnerable](../labs/debug_information_disclosure/vulnerable.py) / [fixed](../labs/debug_information_disclosure/secure.py) | A10; related A02 / CWE-209 | PASS locally |
| 12 | [dependency-confusion](../scenarios/12-dependency-confusion/README.md) | [vulnerable](../labs/dependency_confusion/vulnerable.py) / [fixed](../labs/dependency_confusion/secure.py) | A08; related A03 / CWE-427 | PASS locally |
| 13 | [untrusted-build-dependency](../scenarios/13-untrusted-build-dependency/README.md) | [vulnerable](../labs/untrusted_build_dependency/vulnerable.py) / [fixed](../labs/untrusted_build_dependency/secure.py) | A08; related A03 / CWE-829 | PASS locally |
| 14 | [weak-password-storage](../scenarios/14-weak-password-storage/README.md) | [vulnerable](../labs/weak_password_storage/vulnerable.py) / [fixed](../labs/weak_password_storage/secure.py) | A04 / CWE-916 | PASS locally |
| 15 | [sql-injection](../scenarios/15-sql-injection/README.md) | [vulnerable](../labs/sql_injection/vulnerable.py) / [fixed](../labs/sql_injection/secure.py) | A05 / CWE-89 | PASS locally |
| 16 | [stored-xss](../scenarios/16-stored-xss/README.md) | [vulnerable](../labs/stored_xss/vulnerable.py) / [fixed](../labs/stored_xss/secure.py) | A05 / CWE-79 | PASS locally |
| 17 | [os-command-injection-rce](../scenarios/17-os-command-injection-rce/README.md) | [vulnerable](../labs/os_command_injection_rce/vulnerable.py) / [fixed](../labs/os_command_injection_rce/secure.py) | A05 / CWE-78 | PASS locally |
| 18 | [path-traversal](../scenarios/18-path-traversal/README.md) | [vulnerable](../labs/path_traversal/vulnerable.py) / [fixed](../labs/path_traversal/secure.py) | A01 / CWE-22 | PASS locally |
| 19 | [business-logic-bypass](../scenarios/19-business-logic-bypass/README.md) | [vulnerable](../labs/business_logic_bypass/vulnerable.py) / [fixed](../labs/business_logic_bypass/secure.py) | A06 / CWE-841 | PASS locally |
| 20 | [missing-login-rate-limiting](../scenarios/20-missing-login-rate-limiting/README.md) | [vulnerable](../labs/missing_login_rate_limiting/vulnerable.py) / [fixed](../labs/missing_login_rate_limiting/secure.py) | A07 / CWE-307 | PASS locally |
| 21 | [session-fixation](../scenarios/21-session-fixation/README.md) | [vulnerable](../labs/session_fixation/vulnerable.py) / [fixed](../labs/session_fixation/secure.py) | A07 / CWE-384 | PASS locally |
| 22 | [unsafe-deserialization](../scenarios/22-unsafe-deserialization/README.md) | [vulnerable](../labs/unsafe_deserialization/vulnerable.py) / [fixed](../labs/unsafe_deserialization/secure.py) | A08 / CWE-502 | PASS locally |
| 23 | [unsigned-artifact-acceptance](../scenarios/23-unsigned-artifact-acceptance/README.md) | [vulnerable](../labs/unsigned_artifact_acceptance/vulnerable.py) / [fixed](../labs/unsigned_artifact_acceptance/secure.py) | A08 / CWE-345 | PASS locally |
| 24 | [missing-security-audit-logs](../scenarios/24-missing-security-audit-logs/README.md) | [vulnerable](../labs/missing_security_audit_logs/vulnerable.py) / [fixed](../labs/missing_security_audit_logs/secure.py) | A09 / CWE-778 | PASS locally |
| 25 | [fail-open-error-handling](../scenarios/25-fail-open-error-handling/README.md) | [vulnerable](../labs/fail_open_error_handling/vulnerable.py) / [fixed](../labs/fail_open_error_handling/secure.py) | A10 / CWE-636 | PASS locally |

## Mapping sources

The [source snapshot](evidence/audit-mapping-sources.json) records official
[OWASP/Top10 2025 category documents](https://github.com/OWASP/Top10/tree/master/2025/docs/en),
upstream blob IDs and mapped CWE identifiers. Definitions are referenced through
the [MITRE CWE catalog](https://cwe.mitre.org/). The distinction between official
CWE assignment and contextual classification is covered by automated inventory tests.
For example, CORS (CWE-942) remains A02 in the official 2025 list even though the
A01 narrative also discusses untrusted-origin access.

## Reproduce

```bash
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s tests -p browser_labs.py -v
python3 -m scripts.audit_scenarios --native --output reports/scenario-audit
```

The last command requires only the normal native prerequisites and reports 05 as
NOT_RUN unless supplied with fresh real API evidence. Exit codes: 0 complete pass,
1 an assertion/implementation failed, 2 at least one scenario was not run.

For a complete 25-scenario audit:

```bash
make k8s-up k8s-test
python3 -m scripts.audit_scenarios --native --kubernetes-report reports/rbac.json --output reports/scenario-audit
make k8s-down
```

The report must contain all successful API assertions and be at most 15 minutes
old. The manual Kubernetes workflow performs this sequence and uploads the result.
Fresh hosted outcomes will be appended after publication; no unrun result is marked
PASS here.

## Limits

Passing proofs establish the documented synthetic behaviors and regressions, not
complete security of arbitrary inputs or production readiness. Native execution is
not a sandbox. HMAC authenticity in 23 is not public-key signing. Baseline DAST is
not full authenticated penetration testing. The known HIGH/CRITICAL image dependency
gate remains a separate release limitation; no risk policy was relaxed in this audit.
