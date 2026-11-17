# 22 — Unsafe Deserialization

**Difficulty:** Advanced · **CWE:** CWE-502 · **OWASP Top 10:2025:** A08

## Learning objectives

Identify the trust boundary behind unsafe deserialization, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

Loading an untrusted pickle invokes a callable supplied by the serialized object graph.

- Vulnerable implementation: [`vulnerable.py`](../../labs/unsafe_deserialization/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/unsafe_deserialization/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/unsafe_deserialization/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/unsafe_deserialization/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario unsafe-deserialization --output reports/unsafe-deserialization
cat reports/unsafe-deserialization/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.unsafe_deserialization.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/unsafe-deserialization/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario unsafe-deserialization --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

A temporary marker proves callable execution during unpickling; the JSON-only path creates no marker.

## Remediation

Use a non-executable format such as JSON with size limits and explicit schema validation.

## Scope and residual risk

Only the shipped marker-writing proof is run. The vulnerable restore function is never exposed as an HTTP endpoint.

## Interview questions and answers

**Can a pickle be made safe simply by hiding its class names?**  
No. Pickle is a Python object execution format; do not accept it from untrusted producers.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/unsafe-deserialization/assessment.json reports/unsafe-deserialization/assessment.md
rmdir reports/unsafe-deserialization
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
