# Optional live security tools

Install tools from their official release instructions and record their versions
in your assessment. These extensions require network/download access and are
separate from the deterministic, network-disabled core exercises.

## Pinned Linux amd64 helper

```bash
bash scripts/install_tools.sh trivy syft cosign gitleaks
export PATH="$PWD/.work/bin:$PATH"
```

The helper checks hard-coded SHA256 values for the downloaded release artifacts.
Review and update versions/checksums together. For other platforms, use official
installation instructions. The manual **Live security tools** GitHub workflow runs
image gating, signed SBOM retests and source/secret scans as separate jobs. A blocked
image release intentionally fails that job; it does not get converted to a pass.

## Real image vulnerabilities — Trivy

Install [Trivy](https://trivy.dev/latest/getting-started/installation/), then:

```bash
make scan
```

The script exports this lab's image, scans it into `reports/trivy.json`, and invokes
the same hardened release gate used by the fixture exercise. Findings at HIGH or
CRITICAL severity produce a nonzero exit. Missing/malformed output fails closed.
Database availability and findings change over time. A passing teaching exercise
is not a promise that the current base image has no CVEs.

## Source and secrets

Install [Semgrep](https://semgrep.dev/docs/getting-started/) and
[Gitleaks](https://github.com/gitleaks/gitleaks#installing), then:

```bash
semgrep scan --config policies/semgrep.yml app lab pipelines/hardened --error
# Intentional vulnerable teaching material is excluded from this production-path scan.
gitleaks git . --redact --report-format json --report-path reports/gitleaks.json
```

Gitleaks tests for real accidental secrets; the lab's exact synthetic-token check
is a separate exercise and is not claimed to be a Gitleaks finding.

## SBOM integrity — Syft and Cosign

Install [Syft](https://github.com/anchore/syft#installation) and
[Cosign](https://docs.sigstore.dev/cosign/system_config/installation/), then:

```bash
make build
bash scripts/supply_chain.sh
```

This creates an SPDX SBOM, generates a passwordless disposable lab key, signs the
SBOM, verifies its original bytes, then proves the signature rejects modified bytes.
Keys live only in ignored `.work/signing/`; never treat them as a production identity.
The script explicitly disables transparency-log use for an offline key-based lab.
Production signing should use a protected identity and an appropriate verification policy.
The extension signs the SBOM blob, not the deployed container image.

## Local HTTP checks — ZAP

After `make up`, a Linux Docker host can run the baseline against localhost:

```bash
docker run --rm --network host ghcr.io/zaproxy/zaproxy:stable   zap-baseline.py -t http://127.0.0.1:8080
```

This uses a mutable tool tag and should be pinned to a reviewed digest for controlled
assessments. Docker Desktop host networking needs explicit support/configuration.
A three-route JSON API provides limited DAST coverage; do not infer pipeline security
from a clean web scan. Never point this exercise at an unauthorized external service.
