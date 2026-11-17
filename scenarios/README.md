# Scenario catalog

The original scenarios 01–05 are preserved. New scenarios 06–25 add application,
supply-chain, authentication, logging and error-handling practice using the same
runner/report conventions.

```bash
bash ./setup.sh --lab-only             # 24 local exercises; report records actual outcomes
python3 -m lab.cli list                # runnable local IDs
make k8s-up k8s-test                   # separate real Kubernetes exercise 05
```

| ID | Walkthrough | Runtime |
|---|---|---|
| 01 | [CI metadata command injection](01-pipeline-injection/README.md) | Python / Docker |
| 02 | [Synthetic build-log secret exposure](02-secret-exposure/README.md) | Python / Docker |
| 03 | [Mutable artifact tampering](03-artifact-tampering/README.md) | Python / Docker |
| 04 | [Advisory release-gate bypass](04-security-gate-bypass/README.md) | Python / Docker |
| 05 | [Excessive Kubernetes deployment permissions](05-excessive-permissions/README.md) | kind + kubectl |
| 06 | [Broken Object Level Authorization](06-idor-bola/README.md) | Python / Docker |
| 07 | [Broken Function Level Authorization](07-broken-function-level-authorization/README.md) | Python / Docker |
| 08 | [Mass Assignment](08-mass-assignment/README.md) | Python / Docker |
| 09 | [Server-Side Request Forgery](09-ssrf/README.md) | Python / Docker |
| 10 | [CORS Misconfiguration](10-cors-misconfiguration/README.md) | Python / Docker |
| 11 | [Debug Information Disclosure](11-debug-information-disclosure/README.md) | Python / Docker |
| 12 | [Local Dependency Confusion](12-dependency-confusion/README.md) | Python / Docker |
| 13 | [Untrusted Build Dependency](13-untrusted-build-dependency/README.md) | Python / Docker |
| 14 | [Weak Password Storage](14-weak-password-storage/README.md) | Python / Docker |
| 15 | [SQL Injection](15-sql-injection/README.md) | Python / Docker |
| 16 | [Stored Cross-Site Scripting](16-stored-xss/README.md) | Python / Docker |
| 17 | [OS Command Injection](17-os-command-injection-rce/README.md) | Python / Docker |
| 18 | [Path Traversal](18-path-traversal/README.md) | Python / Docker |
| 19 | [Coupon Reuse / Business Logic Bypass](19-business-logic-bypass/README.md) | Python / Docker |
| 20 | [Missing Login Rate Limiting](20-missing-login-rate-limiting/README.md) | Python / Docker |
| 21 | [Session Fixation](21-session-fixation/README.md) | Python / Docker |
| 22 | [Unsafe Deserialization](22-unsafe-deserialization/README.md) | Python / Docker |
| 23 | [Unauthenticated Artifact Acceptance](23-unsigned-artifact-acceptance/README.md) | Python / Docker |
| 24 | [Missing Security Audit Logs](24-missing-security-audit-logs/README.md) | Python / Docker |
| 25 | [Fail-Open Error Handling](25-fail-open-error-handling/README.md) | Python / Docker |

Start with the [operating guide](../docs/OPERATING_LABS.md), then compare the
[vulnerability matrix](../docs/VULNERABILITY_MATRIX.md) and
[actual validation](../docs/EXPANSION_VALIDATION.md). Every new lab supplies a
vulnerable implementation, fixed implementation, proof, tests and knowledge checks.
