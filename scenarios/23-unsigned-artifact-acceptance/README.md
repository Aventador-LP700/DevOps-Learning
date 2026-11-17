# 23 — Unauthenticated Artifact Acceptance

**Difficulty:** Intermediate · **CWE:** CWE-345 · **OWASP Top 10:2025:** A08

## Learning objectives

Identify the trust boundary behind unauthenticated artifact acceptance, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

The sender supplies both artifact and matching checksum, so checksum verification does not establish trusted producer origin.

- Vulnerable implementation: [`vulnerable.py`](../../labs/unsigned_artifact_acceptance/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/unsigned_artifact_acceptance/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/unsigned_artifact_acceptance/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/unsigned_artifact_acceptance/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario unsigned-artifact-acceptance --output reports/unsigned-artifact-acceptance
cat reports/unsigned-artifact-acceptance/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.unsigned_artifact_acceptance.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/unsigned-artifact-acceptance/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario unsigned-artifact-acceptance --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

An attacker-selected artifact with a valid self-supplied digest is accepted, while an authenticated envelope is required by the fixed path.

## Remediation

Verify an HMAC-SHA256 authenticator using a randomly generated protected key before consuming the payload.

## Scope and residual risk

This uses a shared-key MAC, not a public-key digital signature. Scenario 03 protects a trusted digest; this lab demonstrates missing producer authentication.

## Interview questions and answers

**How does authenticity differ from a plain checksum?**  
An attacker can recompute an unkeyed checksum. A protected-key authenticator requires access to the trusted producer key.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/unsigned-artifact-acceptance/assessment.json reports/unsigned-artifact-acceptance/assessment.md
rmdir reports/unsigned-artifact-acceptance
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
