# 16 — Stored Cross-Site Scripting

**Difficulty:** Intermediate · **CWE:** CWE-79 · **OWASP Top 10:2025:** A05

## Learning objectives

Identify the trust boundary behind stored cross-site scripting, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

Stored comments are inserted into HTML without context-appropriate encoding.

- Vulnerable implementation: [`vulnerable.py`](../../labs/stored_xss/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/stored_xss/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/stored_xss/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/stored_xss/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario stored-xss --output reports/stored-xss
cat reports/stored-xss/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.stored_xss.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/stored-xss/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario stored-xss --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

Inspect parsed script elements and run the browser regression proving execution in the vulnerable page only.

## Remediation

HTML-escape comment text and add a restrictive CSP in the fixed HTTP application.

## Scope and residual risk

This covers HTML text context. Attribute, URL and JavaScript contexts require their own encoding or safe DOM APIs.

## Interview questions and answers

**Why is CSP not a substitute for output encoding?**  
CSP is defense in depth and can be weakened or bypassed by application changes; correct data-to-DOM handling removes the injection primitive.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/stored-xss/assessment.json reports/stored-xss/assessment.md
rmdir reports/stored-xss
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
