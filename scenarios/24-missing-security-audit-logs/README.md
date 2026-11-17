# 24 — Missing Security Audit Logs

**Difficulty:** Beginner · **CWE:** CWE-778 · **OWASP Top 10:2025:** A09

## Learning objectives

Identify the trust boundary behind missing security audit logs, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

An administrative role change mutates state without recording a security event.

- Vulnerable implementation: [`vulnerable.py`](../../labs/missing_security_audit_logs/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/missing_security_audit_logs/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/missing_security_audit_logs/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/missing_security_audit_logs/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario missing-security-audit-logs --output reports/missing-security-audit-logs
cat reports/missing-security-audit-logs/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.missing_security_audit_logs.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/missing-security-audit-logs/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario missing-security-audit-logs --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

Inspect missing vulnerable log output versus structured allowed/denied events in the fixed JSONL log.

## Remediation

Record action, actor, target, outcome, timestamp and correlation ID; fail the critical action if its audit write fails.

## Scope and residual risk

Local JSONL is not a tamper-resistant audit store or a SIEM. Production collection, access control and alerting remain separate.

## Knowledge checks

**Should audit logs record only successful actions?**  
No. Denied privileged actions are useful attack signals; avoid logging credentials or unnecessary personal data.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/missing-security-audit-logs/assessment.json reports/missing-security-audit-logs/assessment.md
rmdir reports/missing-security-audit-logs
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
