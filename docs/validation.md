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

GitHub workflow results will provide commit-specific validation after publication.
The manual Kubernetes workflow runs on a hosted runner with a supported Docker
setup; its outcome must be checked before claiming a successful real-cluster retest.
