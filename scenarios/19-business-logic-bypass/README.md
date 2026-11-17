# 19 — Coupon Reuse / Business Logic Bypass

**Difficulty:** Intermediate · **CWE:** CWE-841 · **OWASP Top 10:2025:** A06

## Learning objectives

Identify the trust boundary behind coupon reuse / business logic bypass, reproduce its failure,
apply the separate fixed implementation and verify that legitimate behavior survives.
Explain the detection evidence and the residual limitation below.

## Root cause and implementation

The checkout applies a one-use coupon without recording prior redemption.

- Vulnerable implementation: [`vulnerable.py`](../../labs/business_logic_bypass/vulnerable.py)
- Fixed implementation: [`secure.py`](../../labs/business_logic_bypass/secure.py)
- Harmless attack and observed evidence: [`attack.py`](../../labs/business_logic_bypass/attack.py)
- Automated vulnerable, fixed and positive tests: [`test_lab.py`](../../labs/business_logic_bypass/test_lab.py)

These are runnable Python module exercises using real state, queries, parsers or
local services; they are not empty HTTP endpoints. The optional HTTP adapter exposes
only the routes listed in [the operating guide](../../docs/OPERATING_LABS.md).

## Start and reproduce without Docker

From the repository root with Bash and Python 3.10+:

```bash
python3 -m lab.cli run --native --scenario business-logic-bypass --output reports/business-logic-bypass
cat reports/business-logic-bypass/assessment.md
```

Native mode is explicit and has no OS sandbox. Only the fixed shipped proof is
intended for this mode. Use a disposable VM when modifying attack code. All data is
synthetic; temporary services bind to loopback and shut down automatically.

## Test and verify

```bash
python3 -m unittest labs.business_logic_bypass.test_lab -v
```

Three checks assert that the vulnerable behavior occurs, the same attack is blocked
by the fixed path, and a legitimate operation remains allowed. The shared runner
fails if either the exploit observation or the hardened/positive retest is wrong.
Read actual evidence under `reports/business-logic-bypass/assessment.json`; no result is fabricated.
For browser execution/CORS tests use the commands in the operating guide.

## Docker alternative

```bash
make build
docker compose run --rm lab run --scenario business-logic-bypass --output /reports
make report
```

The container has no external network and can use only loopback for internal mocks.
Its JSON/Markdown report is exported into `reports/` by the final command.

## Detection

Compare repeated discounted purchases and the fixed database redemption ledger.

## Remediation

Enforce the workflow invariant atomically with a UNIQUE(user,coupon) constraint and a transaction.

## Scope and residual risk

The subtotal is a trusted integer fixture, not a client-controlled production price. Real checkout also needs inventory, payment and idempotency controls.

## Interview questions and answers

**Why is a check-then-insert pattern risky?**  
Concurrent requests can both observe no redemption. A database uniqueness constraint makes the invariant atomic.

**How do you know the fix did not simply break the feature?**  
The positive regression test checks the intended successful behavior independently
of the rejected attack. Compare all three assertions and the recorded evidence.

## Cleanup

The runner automatically closes mock servers/databases and deletes temporary attack
files. Remove only this run's exported files when finished:

```bash
rm -f reports/business-logic-bypass/assessment.json reports/business-logic-bypass/assessment.md
rmdir reports/business-logic-bypass
```

For the Docker alternative, `make clean` stops the lab project and deletes its
Docker evidence volume. The optional persistent HTTP lab stops with Ctrl+C.
