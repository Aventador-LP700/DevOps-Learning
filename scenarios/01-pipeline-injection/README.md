# Pipeline command injection

Reference: CWE-78.

## Threat and preconditions

An untrusted contributor controls a change title used in a build shell command.

## Reproduce

```bash
make build
docker compose run --rm lab run --scenario pipeline-injection --output /reports
make report
```

## Vulnerable observation

The payload creates `injected.txt` in disposable scenario storage.

## Detection

Compare the unexpected marker and the captured stdout. A real pipeline would also need process/build telemetry.

## Remediation

Pass metadata as a process argument, never concatenate it into shell source.

## Retest

The same title prints literally and no marker is created.

Positive control: The safe step completes successfully with the attack title as ordinary text.

Evidence is under the `pipeline-injection` result in `reports/assessment.json` and `.md`.
A successful exercise command checks both the vulnerable observation and hardened
retest. Read the evidence, not only the exit status.
