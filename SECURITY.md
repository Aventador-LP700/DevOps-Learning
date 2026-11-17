# Security policy

This repository intentionally includes vulnerable CI teaching steps under
`pipelines/vulnerable/` and excessive namespace RBAC in
`infra/kubernetes/vulnerable-rbac.yaml`. They are lab material, not production templates.

Use disposable local infrastructure and synthetic data only. Never register the
lab runner with an organization, expose it publicly, or provide cloud credentials.
The container boundary reduces risk; it is not protection against container-runtime vulnerabilities.

For unexpected vulnerabilities outside the exercises, use GitHub private vulnerability
reporting if enabled. Otherwise open an issue with a minimal description and ask for
a private reporting channel; do not post credentials or a working exploit against live systems.

Supported version: current main branch. Exercise findings are expected behavior.
