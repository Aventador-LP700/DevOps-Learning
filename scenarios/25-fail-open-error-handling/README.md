# 25 — Fail-Open Error Handling

**Difficulty:** Intermediate · **CWE:** CWE-636 · **OWASP Top 10:2025:** A10

## Learning objectives

Identify the trust boundary behind fail-open error handling, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

An authorization exception returns allow, converting policy-service failure into access.

- Vulnerable implementation: [`vulnerable.py`](../../labs/fail_open_error_handling/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/fail_open_error_handling/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/fail_open_error_handling/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/fail_open_error_handling/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario fail-open-error-handling --output reports/fail-open-error-handling
cat reports/fail-open-error-handling/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.fail_open_error_handling.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/fail-open-error-handling/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario fail-open-error-handling --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

Inject a real TimeoutError and compare authorization decisions; test healthy allow/deny and malformed backend responses.

## Remediation

Deny on exceptions and require an explicit boolean True before granting access.

## Scope and residual risk

Failing closed can affect availability. Design explicit degradation rules without silently granting protected access.

## Knowledge checks

**Why is retrying an authorization error not enough?**  
Retries can fail too. The terminal decision must still deny when policy cannot be established.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/fail-open-error-handling/assessment.json reports/fail-open-error-handling/assessment.md
rmdir reports/fail-open-error-handling
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
