# Contributing

Add scenarios with a threat model, a harmless proof, an observable detection,
a remediation, and a negative retest. All attack effects must stay inside temporary
lab storage or the dedicated kind namespace. Never use real credentials or public targets.

For native changes, run `python3 -m unittest discover -s tests -v` and
`bash ./setup.sh --lab-only`. Native payloads must stay fixed and harmless.

Run `make check`, `make lab`, `make report`, and the app smoke test before submitting.
For Kubernetes changes, run `make k8s-up k8s-test k8s-down` as well.
Document actual results and tool versions; do not imply a fixture is a live scan.
Use one focused pull request and describe the behavior and verification performed.
