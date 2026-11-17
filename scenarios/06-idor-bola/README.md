# 06 — Broken Object Level Authorization

**Difficulty:** Beginner · **CWE:** CWE-639 · **OWASP Top 10:2025:** A01

## Learning objectives

Identify the trust boundary behind broken object level authorization, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

Object IDs are looked up without comparing the authenticated actor to the object owner.

- Vulnerable implementation: [`vulnerable.py`](../../labs/idor_bola/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/idor_bola/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/idor_bola/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/idor_bola/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario idor-bola --output reports/idor-bola
cat reports/idor-bola/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.idor_bola.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/idor-bola/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario idor-bola --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

Observe Alice receiving Bob’s synthetic order 200; correlate authenticated subject, object ID and authorization decision.

## Remediation

Check object ownership at the data access boundary and return the same denial for unknown and unauthorized objects.

## Scope and residual risk

IDs are references, not authorization. Production systems also need tenant constraints, listing filters and consistent error responses.

## Interview questions and answers

**Would UUIDs fix IDOR?**  
No. Hard-to-guess identifiers reduce enumeration but do not enforce ownership.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/idor-bola/assessment.json reports/idor-bola/assessment.md
rmdir reports/idor-bola
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
