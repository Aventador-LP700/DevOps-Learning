# Synthetic secret exposure

Reference: CWE-532.

## Threat and preconditions

A log reader can view a build step that has access to a CI credential.

## Reproduce

```bash
make build
docker compose run --rm lab run --scenario secret-exposure --output /reports
make report
```

## Vulnerable observation

A clearly synthetic credential appears in captured stdout.

## Detection

Exact matching of the synthetic token in output proves exposure. This is not a claim of a live Gitleaks run.

## Remediation

Log operation results without credential values. Avoid environment dumps and tracing.

## Retest

The same supplied synthetic token is absent from both output streams.

Positive control: The hardened step accepts the supplied token and exits successfully.

Evidence is under the `secret-exposure` result in `reports/assessment.json` and `.md`.
A successful exercise command checks both the vulnerable observation and hardened
retest. Read the evidence, not only the exit status.
