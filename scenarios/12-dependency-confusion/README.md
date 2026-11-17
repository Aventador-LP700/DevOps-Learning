# 12 — Local Dependency Confusion

**Difficulty:** Intermediate · **CWE:** CWE-427 · **OWASP Top 10:2025:** A08/A03

The first category is the official OWASP 2025 mapping for the selected CWE;
subsequent categories describe related application or supply-chain context.

## Learning objectives

Identify the trust boundary behind local dependency confusion, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

A resolver chooses the highest version across private and public namespaces, preferring a planted public package.

- Vulnerable implementation: [`vulnerable.py`](../../labs/dependency_confusion/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/dependency_confusion/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/dependency_confusion/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/dependency_confusion/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario dependency-confusion --output reports/dependency-confusion
cat reports/dependency-confusion/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.dependency_confusion.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/dependency-confusion/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario dependency-confusion --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

The loopback registry logs both namespace queries and the selected package identity and version.

## Remediation

Resolve exclusively from the approved private namespace and pin version and trusted content digest.

## Scope and residual risk

This is a real local JSON index simulation, not a PyPI-compatible registry or internet package takeover. No package is installed.

## Knowledge checks

**Why does a version lock alone not establish publisher trust?**  
A lock needs an authenticated source and trusted content identity; an attacker may control a competing source or mutable metadata.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/dependency-confusion/assessment.json reports/dependency-confusion/assessment.md
rmdir reports/dependency-confusion
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
