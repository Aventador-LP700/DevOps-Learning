# 18 — Path Traversal

**Difficulty:** Beginner · **CWE:** CWE-22 · **OWASP Top 10:2025:** A01

## Learning objectives

Identify the trust boundary behind path traversal, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

A file reader constrains paths to synthetic lab storage but fails to separate public and private fixture directories.

- Vulnerable implementation: [`vulnerable.py`](../../labs/path_traversal/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/path_traversal/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/path_traversal/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/path_traversal/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario path-traversal --output reports/path-traversal
cat reports/path-traversal/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.path_traversal.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/path-traversal/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario path-traversal --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

The traversal reads the fake private payroll file; resolved-path and symlink tests verify the public-root control.

## Remediation

Reject absolute paths and require the resolved target to remain under the public directory.

## Scope and residual risk

An outer safety envelope prevents real host-file reads. Production designs must consider races and filesystem-level no-follow/openat controls.

## Interview questions and answers

**Why check the resolved path rather than a ../ substring?**  
Encoding and symlinks can escape lexical checks; canonical resolution checks where the file actually points.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/path-traversal/assessment.json reports/path-traversal/assessment.md
rmdir reports/path-traversal
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
