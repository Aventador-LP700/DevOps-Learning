# Validation record

Date: 17 November 2026. Environment: managed Linux amd64 workspace with Docker
29.9.2, Compose 2.40.3 and host Python 3.12.14. Container Python: 3.12.16.

| Check | Actual result |
|---|---|
| Unit/control and HTTP tests | 9 passed |
| Python compile and Compose configuration | Passed |
| Four core attack + hardened retests | All passed in restricted container |
| JSON/Markdown report export | Passed |
| Local demo deployment and health request | Passed |
| Semgrep 1.185.0, one local shell-execution rule on hardened paths | 0 findings; narrow rule coverage only |
| Gitleaks 8.30.1 repository history | No secrets found |
| Syft 1.57.2 + Cosign 2.5.3 | SBOM generated; original signature verified; modified SBOM rejected |
| Trivy 0.76.2 real image scan | Scan completed; release gate correctly blocked HIGH/CRITICAL findings |
| Local kind 0.30.0 startup | Blocked: rootless Docker lacks systemd Delegate=yes |

The pinned Debian bookworm image had 99 HIGH and 2 CRITICAL package findings at
scan time, plus other severities. These are scanner observations, not individually
exploit-validated findings. They are recorded in
[the scan summary](evidence/trivy-summary.json). No severity exception or
`continue-on-error` was used to turn the release decision green. This image is a
learning environment and is not approved for a production release.

The signed-SBOM extension uses disposable keys and deliberately skips transparency
log verification. It demonstrates blob integrity, not a production signing policy.

[Core assessment JSON](evidence/assessment.json) and
[Markdown](evidence/assessment.md) contain the actual recorded exercise evidence.
Their synthetic token is intentionally public and is not a genuine credential.
The image identifier and base digest are recorded in the live scan summary.
Generated timestamps use UTC. This is an implementation snapshot, not a claim that
all platforms, every scanner rule or optional integration has passed.

## GitHub-hosted verification

The following runs tested implementation commit
`c15ac61742b38736b7b5cc92573d6e5c7c1d3fd7`:

- [Core CI: passed](https://github.com/Aventador-LP700/DevOps-Learning/actions/runs/44097426375).
  Unit checks, four attack/defense retests, report export, deployment smoke test and
  evidence upload succeeded.
- [Kubernetes integration: passed](https://github.com/Aventador-LP700/DevOps-Learning/actions/runs/44097428862).
  A real kind cluster deployed successfully. The excessive Role permitted the
  synthetic Secret read; scoped RBAC denied that read and allowed the intended
  Deployment patch. Cleanup succeeded. This resolves the local workspace limitation
  for the hosted test, without claiming the workspace itself supports kind.
- [Live tools](https://github.com/Aventador-LP700/DevOps-Learning/actions/runs/44097439806):
  source/secret checks and signed-SBOM retests passed. The image-release-gate job
  failed because actual HIGH/CRITICAL findings were blocked, as designed. The
  Trivy report was uploaded; the workflow is intentionally not reported as green.

These links identify the tested commit. Subsequent documentation-only changes do
not alter the implementation. Workflow artifacts are retained for a limited time;
the committed local assessment provides a durable core example.

## Native setup addition

`bash ./setup.sh` adds an explicit Docker-free mode for the four fixed exercises
and localhost API. Reports identify the execution mode. Native setup performs no
package installation and requires only Bash, Python 3.10+, sh and printf.

The expanded 12-test suite passed locally, and all four Docker exercise/retest
pairs passed after the native changes. End-to-end tests check the default exercise-to-server flow, report generation,
invocation from outside the checkout through a path containing spaces, and invalid
options. Docker, Make, pip and sudo are replaced with failing test wrappers during
these checks, proving that native setup does not invoke them. The Docker workflow
continues to run separately for regression coverage.

For the subsequent 20-lab expansion, see [the expansion validation record](EXPANSION_VALIDATION.md).
