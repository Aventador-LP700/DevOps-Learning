# 11 — Debug Information Disclosure

**Difficulty:** Beginner · **CWE:** CWE-209 · **OWASP Top 10:2025:** A10/A02

The first category is the official OWASP 2025 mapping for the selected CWE;
subsequent categories describe related application or supply-chain context.

## Learning objectives

Identify the trust boundary behind debug information disclosure, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

An exception handler serializes stack traces and synthetic configuration into the client response.

- Vulnerable implementation: [`vulnerable.py`](../../labs/debug_information_disclosure/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/debug_information_disclosure/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/debug_information_disclosure/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/debug_information_disclosure/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario debug-information-disclosure --output reports/debug-information-disclosure
cat reports/debug-information-disclosure/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.debug_information_disclosure.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/debug-information-disclosure/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario debug-information-disclosure --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

Trigger the synthetic failure and inspect response content, status code and request correlation identifier.

## Remediation

Return a generic error with a correlation ID; restrict detailed diagnostics to protected operational channels.

## Scope and residual risk

The lab does not ship a production log collector. The dummy configuration is intentionally synthetic.

## Knowledge checks

**Should an error return HTTP 200 to hide the failure?**  
No. Keep accurate failure status while removing sensitive detail from the public body.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/debug-information-disclosure/assessment.json reports/debug-information-disclosure/assessment.md
rmdir reports/debug-information-disclosure
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
