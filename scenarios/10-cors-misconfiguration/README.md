# 10 — CORS Misconfiguration

**Difficulty:** Intermediate · **CWE:** CWE-942 · **OWASP Top 10:2025:** A02

## Learning objectives

Identify the trust boundary behind cors misconfiguration, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

The vulnerable response reflects an arbitrary Origin and permits credentialed cross-origin reads.

- Vulnerable implementation: [`vulnerable.py`](../../labs/cors_misconfiguration/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/cors_misconfiguration/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/cors_misconfiguration/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/cors_misconfiguration/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario cors-misconfiguration --output reports/cors-misconfiguration
cat reports/cors-misconfiguration/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.cors_misconfiguration.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/cors-misconfiguration/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario cors-misconfiguration --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

Inspect response ACAO/ACAC headers and confirm read access from a second origin in a real browser.

## Remediation

Return credentialed CORS headers only for exact trusted origins; otherwise omit ACAO and vary responses on Origin.

## Scope and residual risk

CORS governs browser reads, not authentication or server-to-server access. The trusted UI origin in this lab is the explicit localhost:8082 example.

## Interview questions and answers

**Can wildcard origins be used with credentials?**  
Browsers reject that combination. Reflecting arbitrary origins with credentials is the dangerous working pattern shown here.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/cors-misconfiguration/assessment.json reports/cors-misconfiguration/assessment.md
rmdir reports/cors-misconfiguration
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
