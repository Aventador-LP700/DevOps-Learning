# PipelineProof — CI/CD Security Attack & Defense Lab

[![Lab validation](https://github.com/Aventador-LP700/DevOps-Learning/actions/workflows/ci.yml/badge.svg)](https://github.com/Aventador-LP700/DevOps-Learning/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Attack a pipeline. Collect evidence. Apply a control. Prove the same attack fails.**

PipelineProof is an open-source, local-first CI/CD penetration-testing lab. Four
containerized exercises demonstrate pipeline command injection, secret disclosure,
artifact tampering, and security-gate bypass. A fifth exercise uses a real local
Kubernetes API to demonstrate excessive CI deployment permissions and scoped RBAC.

Built for learners and reviewers who want reproducible evidence of CI/CD VAPT,
not just screenshots of installed security tools.

![PipelineProof architecture](docs/architecture.svg)

## Five-minute start

Requirements: Docker Engine or Docker Desktop with Compose v2, Git, Python 3.10+,
and Make. Start Docker before running these commands. Linux and WSL2 are the
primary targets; see [platform notes](docs/deployment.md).

```bash
git clone https://github.com/Aventador-LP700/DevOps-Learning.git
cd DevOps-Learning
make lab
make report
make up
curl http://127.0.0.1:8080/health
```

Open `reports/assessment.md` to review attack evidence and hardened retests.
The demo API binds to `127.0.0.1:8080`. `make down` stops it. `make clean`
also deletes the lab evidence volume; exported host reports remain.

Expected exercise output:

```text
PASS pipeline-injection
PASS secret-exposure
PASS artifact-tampering
PASS security-gate-bypass
```

A PASS means the exploit succeeded against the vulnerable step **and** the
hardened control blocked the same attack. Unexpected outcomes fail the command.
See [recorded validation](docs/validation.md) for what has actually been tested.

## Exercises

| Exercise | Attack evidence | Hardened retest | Walkthrough |
|---|---|---|---|
| Pipeline injection | Change-title payload creates a temporary marker | Metadata passed as an argument; no marker created | [01](scenarios/01-pipeline-injection/README.md) |
| Secret exposure | Synthetic credential appears in captured build logs | Same credential is absent from logs | [02](scenarios/02-secret-exposure/README.md) |
| Artifact tampering | Modified JSON is consumed without verification | Trusted SHA256 digest rejects modified bytes | [03](scenarios/03-artifact-tampering/README.md) |
| Gate bypass | Advisory step exits successfully despite a critical finding | Enforced severity policy rejects the report | [04](scenarios/04-security-gate-bypass/README.md) |
| Excessive deployment permissions | Lab CI identity reads a synthetic Kubernetes Secret | Read is forbidden; intended deployment patch still works | [05](scenarios/05-excessive-permissions/README.md) |

The core gate exercise uses an explicitly labeled **synthetic Trivy-format
fixture**. `make scan` runs a real installed Trivy scanner against the lab image.
The manual **Live security tools** workflow runs real image scanning, source/secret
checks and signed SBOM retests. A scanner finding can legitimately block its release job.
The artifact exercise verifies a trusted digest; it does not claim to demonstrate
signatures. [Supply-chain extensions](docs/tooling.md) include Syft and Cosign.

## Kubernetes exercise

Install kind and kubectl, then:

```bash
make k8s-up
make k8s-test
cat reports/rbac.json
make k8s-down
```

All script requests explicitly target `kind-pipelineproof`. The test temporarily
applies excessive permissions **only within the lab namespace**, makes a real
API request using service-account impersonation, and restores scoped RBAC on exit.
Use a disposable local machine or VM. See [deployment instructions](docs/deployment.md).

## Repository map

```text
app/                    Small deployment target and health endpoint
lab/                    Exercise runner, controls, JSON/Markdown reports
pipelines/vulnerable/   Deliberately insecure teaching steps
pipelines/hardened/     Corrected steps and enforced release policy
infra/                  kind cluster, app deployment, vulnerable/hardened RBAC
scenarios/              Threats, reproduction, detection, remediation, retest
fixtures/               Synthetic scanner report; no real credential or CVE
policies/               Release policy
scripts/                Report export, real image scan, signing, Kubernetes tests
tests/                  Control edge cases and HTTP tests
.github/workflows/      Read-only validation CI and manual Kubernetes integration
```

## Engineering decisions

- The attack container runs as a non-root user with no network, dropped
  capabilities, a read-only root filesystem, and bounded resources.
- No Docker socket, host checkout, or cloud credentials enter the attack container.
- Attacks write temporary files; only generated assessment evidence persists.
- Repository CI uses read-only GitHub permissions, immutable action references,
  and no persisted checkout credentials. It never evaluates PR metadata as shell code.
- The initial version uses local Python pipeline steps and GitHub validation CI.
  It does not deploy a Gitea server/runner or claim to emulate GitHub's token model.
  This keeps the exercises runnable without privileged runner infrastructure.
- Evidence distinguishes reproducible teaching fixtures from real infrastructure tests.

Read the [threat model](docs/threat-model.md), [architecture](docs/architecture.md),
[assessment template](docs/assessment-template.md), and [portfolio demo guide](docs/portfolio.md).

## Safety and scope

Intentionally vulnerable steps are teaching material. Run them through `make lab`,
not directly on a workstation. Use synthetic data and your own disposable lab.
The project is not a production deployment template or a certification of security.
See [SECURITY.md](SECURITY.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

This repository also preserves the original DevOps study file. MIT license applies
to the PipelineProof implementation added here.
