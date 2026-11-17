# 17 — OS Command Injection

**Difficulty:** Intermediate · **CWE:** CWE-78 · **OWASP Top 10:2025:** A05

## Learning objectives

Identify the trust boundary behind os command injection, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

An application diagnostic label becomes shell source rather than an argument.

- Vulnerable implementation: [`vulnerable.py`](../../labs/os_command_injection_rce/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/os_command_injection_rce/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/os_command_injection_rce/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/os_command_injection_rce/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario os-command-injection-rce --output reports/os-command-injection-rce
cat reports/os-command-injection-rce/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.os_command_injection_rce.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/os-command-injection-rce/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario os-command-injection-rce --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

The harmless command writes a temporary rce-proof marker; the fixed implementation rejects the same input.

## Remediation

Avoid the shell, pass argument arrays and validate the allowed diagnostic-label grammar.

## Scope and residual risk

This is application command execution, while scenario 01 targets a CI metadata boundary. No network, reverse shell or persistence is used.

## Knowledge checks

**Does shell escaping solve every command-injection problem?**  
No. Prefer avoiding the shell; argument injection and option handling still need validation even with argument arrays.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/os-command-injection-rce/assessment.json reports/os-command-injection-rce/assessment.md
rmdir reports/os-command-injection-rce
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
