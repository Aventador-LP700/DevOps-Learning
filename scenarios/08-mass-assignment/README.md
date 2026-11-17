# 08 — Mass Assignment

**Difficulty:** Beginner · **CWE:** CWE-915 · **OWASP Top 10:2025:** A08/A01

The first category is the official OWASP 2025 mapping for the selected CWE;
subsequent categories describe related application or supply-chain context.

## Learning objectives

Identify the trust boundary behind mass assignment, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

A client dictionary is merged into a server profile, allowing the protected role field to change.

- Vulnerable implementation: [`vulnerable.py`](../../labs/mass_assignment/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/mass_assignment/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/mass_assignment/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/mass_assignment/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario mass-assignment --output reports/mass-assignment
cat reports/mass-assignment/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.mass_assignment.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/mass-assignment/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario mass-assignment --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

Watch for protected fields in profile-update requests and audit rejected privilege changes.

## Remediation

Accept an explicit schema of editable fields and validate their types and lengths.

## Scope and residual risk

A denylist can miss newly added privileged fields; explicit writable-field schemas are easier to review.

## Knowledge checks

**Why is binding a request directly to a model dangerous?**  
The model often contains internal fields, such as roles, that should never be client-writable.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/mass-assignment/assessment.json reports/mass-assignment/assessment.md
rmdir reports/mass-assignment
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
