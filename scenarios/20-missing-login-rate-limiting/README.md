# 20 — Missing Login Rate Limiting

**Difficulty:** Intermediate · **CWE:** CWE-307 · **OWASP Top 10:2025:** A07

## Learning objectives

Identify the trust boundary behind missing login rate limiting, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

Repeated failed authentications are processed without a bounded attempt policy.

- Vulnerable implementation: [`vulnerable.py`](../../labs/missing_login_rate_limiting/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/missing_login_rate_limiting/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/missing_login_rate_limiting/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/missing_login_rate_limiting/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario missing-login-rate-limiting --output reports/missing-login-rate-limiting
cat reports/missing-login-rate-limiting/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.missing_login_rate_limiting.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/missing-login-rate-limiting/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario missing-login-rate-limiting --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

Six dummy attempts show 401 indefinitely in the vulnerable path and 429 after three failures in the fixed path.

## Remediation

Use an account-scoped limiter with normalized identifiers, expiry and bounded retained state.

## Scope and residual risk

The implementation is in-process. Production services need shared state, distributed abuse detection and lockout/availability tradeoffs.

## Interview questions and answers

**Is per-IP throttling sufficient?**  
No. Distributed clients can rotate addresses, so combine account, network and risk-based signals.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/missing-login-rate-limiting/assessment.json reports/missing-login-rate-limiting/assessment.md
rmdir reports/missing-login-rate-limiting
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
