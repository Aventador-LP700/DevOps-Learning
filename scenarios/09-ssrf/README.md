# 09 — Server-Side Request Forgery

**Difficulty:** Intermediate · **CWE:** CWE-918 · **OWASP Top 10:2025:** A01

## Learning objectives

Identify the trust boundary behind server-side request forgery, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

The preview function permits both the public and internal mock origins instead of restricting the application’s outbound capability.

- Vulnerable implementation: [`vulnerable.py`](../../labs/ssrf/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/ssrf/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/ssrf/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/ssrf/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario ssrf --output reports/ssrf
cat reports/ssrf/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.ssrf.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/ssrf/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario ssrf --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

The internal mock request log shows an unauthorized metadata read; the hardened retest adds no internal request.

## Remediation

Allow only the configured public endpoint, validate canonical destinations and disallow redirects in this constrained lab.

## Scope and residual risk

Both versions have a separate safety envelope allowing only allocated loopback mocks. Production controls must address DNS rebinding, redirects, IPv6 and network egress.

## Interview questions and answers

**Why is URL string filtering insufficient in production?**  
Parsing ambiguities, redirects and DNS changes can make a permitted-looking URL reach a different destination.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/ssrf/assessment.json reports/ssrf/assessment.md
rmdir reports/ssrf
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
