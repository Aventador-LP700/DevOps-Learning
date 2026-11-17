# 13 — Untrusted Build Dependency

**Difficulty:** Intermediate · **CWE:** CWE-829 · **OWASP Top 10:2025:** A08/A03

The first category is the official OWASP 2025 mapping for the selected CWE;
subsequent categories describe related application or supply-chain context.

## Learning objectives

Identify the trust boundary behind untrusted build dependency, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

Building a dependency executes its Python hook with the build process privileges.

- Vulnerable implementation: [`vulnerable.py`](../../labs/untrusted_build_dependency/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/untrusted_build_dependency/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/untrusted_build_dependency/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/untrusted_build_dependency/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario untrusted-build-dependency --output reports/untrusted-build-dependency
cat reports/untrusted-build-dependency/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.untrusted_build_dependency.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/untrusted-build-dependency/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario untrusted-build-dependency --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

A temporary marker proves the local dependency hook actually executed; compare it after the fixed path.

## Remediation

Do not execute untrusted source hooks in the protected build. This lab consumes pinned prebuilt metadata as data.

The fixed builder validates nonempty string name/version fields and bounds the JSON metadata size; a trusted digest alone does not establish a valid schema.

## Scope and residual risk

The fixed alternative models a prebuilt dependency workflow, not a complete wheel installer. Production builders still need isolation and provenance.

## Knowledge checks

**Why can installing a development dependency compromise a pipeline?**  
Package build/install hooks can execute before the application runs and may inherit the runner’s privileges and secrets.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/untrusted-build-dependency/assessment.json reports/untrusted-build-dependency/assessment.md
rmdir reports/untrusted-build-dependency
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
