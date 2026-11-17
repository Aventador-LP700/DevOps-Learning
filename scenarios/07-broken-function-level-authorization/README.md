# 07 — Broken Function Level Authorization

**Difficulty:** Beginner · **CWE:** CWE-862 · **OWASP Top 10:2025:** A01

## Learning objectives

Identify the trust boundary behind broken function level authorization, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

An authenticated user can invoke an administrative deactivate operation because the function lacks a role check.

- Vulnerable implementation: [`vulnerable.py`](../../labs/broken_function_level_authorization/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/broken_function_level_authorization/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/broken_function_level_authorization/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/broken_function_level_authorization/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario broken-function-level-authorization --output reports/broken-function-level-authorization
cat reports/broken-function-level-authorization/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.broken_function_level_authorization.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/broken-function-level-authorization/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario broken-function-level-authorization --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

Record attempted administrative action, authenticated role, target and allow/deny decision.

## Remediation

Authorize the administrative capability server-side before any state mutation.

## Scope and residual risk

A hidden UI button is not a control. Roles must come from trusted server-side identity, not request fields.

## Knowledge checks

**How does BFLA differ from BOLA?**  
BOLA checks access to a particular object; BFLA checks permission to invoke a privileged operation.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/broken-function-level-authorization/assessment.json reports/broken-function-level-authorization/assessment.md
rmdir reports/broken-function-level-authorization
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
