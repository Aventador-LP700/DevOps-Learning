# 14 — Weak Password Storage

**Difficulty:** Intermediate · **CWE:** CWE-916 · **OWASP Top 10:2025:** A04

## Learning objectives

Identify the trust boundary behind weak password storage, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

Unsalted MD5 yields identical fast hashes and permits cheap recovery of the dummy password from a tiny dictionary.

- Vulnerable implementation: [`vulnerable.py`](../../labs/weak_password_storage/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/weak_password_storage/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/weak_password_storage/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/weak_password_storage/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario weak-password-storage --output reports/weak-password-storage
cat reports/weak-password-storage/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.weak_password_storage.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/weak-password-storage/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario weak-password-storage --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

Compare equal weak hashes, salted record differences, wrong-password rejection and KDF record validation.

## Remediation

Use scrypt with per-record random salt, constant-time verification and bounded work factors.
The fixed profile is N=16384, r=8, p=5 (a 16 MiB memory / higher-work configuration);
production values should be benchmarked against current password-storage guidance.

## Scope and residual risk

Salting and adaptive cost do not make weak passwords unguessable. Production parameters must be benchmarked and authentication needs abuse controls.

## Interview questions and answers

**What does a salt protect against?**  
It prevents identical-password hash equality and cross-account precomputation reuse; it does not add entropy to the password.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/weak-password-storage/assessment.json reports/weak-password-storage/assessment.md
rmdir reports/weak-password-storage
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
