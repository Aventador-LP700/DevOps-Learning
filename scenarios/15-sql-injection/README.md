# 15 — SQL Injection

**Difficulty:** Beginner · **CWE:** CWE-89 · **OWASP Top 10:2025:** A05

## Learning objectives

Identify the trust boundary behind sql injection, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

An owner value is concatenated into SQL source, changing the query predicate.

- Vulnerable implementation: [`vulnerable.py`](../../labs/sql_injection/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/sql_injection/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/sql_injection/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/sql_injection/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario sql-injection --output reports/sql-injection
cat reports/sql-injection/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.sql_injection.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/sql-injection/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario sql-injection --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

The injected owner returns both rows from the actual SQLite database; bound parameters return no rows for the same input.

## Remediation

Use parameterized queries for values, and separate allowlists for dynamic identifiers if needed.

## Scope and residual risk

Parameterization does not implement object authorization. The query operates only on a synthetic in-memory database.

## Interview questions and answers

**Can placeholders bind a table name?**  
Usually not. Bind data values; map dynamic identifiers to an explicit allowlist instead of interpolating user input.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/sql-injection/assessment.json reports/sql-injection/assessment.md
rmdir reports/sql-injection
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
