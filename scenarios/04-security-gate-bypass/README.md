# Security-gate bypass

Reference: CWE-693.

## Threat and preconditions

A release pipeline runs a scan only as an advisory step.

## Reproduce

```bash
make build
docker compose run --rm lab run --scenario security-gate-bypass --output /reports
make report
```

## Vulnerable observation

A critical synthetic Trivy-format finding is logged while the vulnerable step exits zero.

## Detection

Compare process exit status against the enforced policy decision. The finding is a fixture, not a real CVE.

## Remediation

Enforce severity policy and reject missing or malformed reports. Protect the scanner execution and report provenance.

## Retest

The identical report is denied by the hardened release decision.

Positive control: A clean report with Trivy-style null vulnerability results is accepted.

Evidence is under the `security-gate-bypass` result in `reports/assessment.json` and `.md`.
A successful exercise command checks both the vulnerable observation and hardened
retest. Read the evidence, not only the exit status.
