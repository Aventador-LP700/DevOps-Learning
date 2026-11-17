# Artifact tampering

Reference: CWE-353.

## Threat and preconditions

An attacker can modify artifact bytes after a trusted build but cannot change the trusted expected digest.

## Reproduce

```bash
make build
docker compose run --rm lab run --scenario artifact-tampering --output /reports
make report
```

## Vulnerable observation

A modified JSON release is accepted by the unchecked teaching deployment.

## Detection

Record the trusted and received SHA256 digests and verification error.

## Remediation

Verify bytes against an expected digest obtained from trusted build state. Use protected signing and provenance for stronger trust chains.

## Retest

The modified bytes raise an integrity verification error.

Positive control: The unmodified artifact is verified before the attack.

Evidence is under the `artifact-tampering` result in `reports/assessment.json` and `.md`.
A successful exercise command checks both the vulnerable observation and hardened
retest. Read the evidence, not only the exit status.
