# Deployment and reset

## Prerequisites

- Linux or WSL2 with Docker Engine; Docker Desktop is suitable for local practice.
- Docker Compose v2 (`docker compose version`), Git, Make, Python 3.10+.
- Suggested starting allocation: 2 CPU / 2 GB RAM for the core lab, 4 CPU / 6 GB
  for kind. These are planning recommendations, not measured minimums.
- Internet access for initial image pulls and optional vulnerability databases.
  Core attacks run with networking disabled after the image is built.

Native Windows PowerShell cannot run the Make/bash examples directly: use WSL2.
macOS Docker Desktop should be compatible, but must be independently tested before
claiming platform support. Optional binary download examples assume Linux amd64.

## Core lab

`make lab` builds the image and runs four isolated exercises. Results persist in a
Docker named volume. `make report` copies only the two known report files into
`reports/` without mounting the host into the attack container. It replaces previous
exports. An export before a successful run fails rather than inventing results.

Run one exercise:

```bash
docker compose run --rm lab run --scenario pipeline-injection --output /reports
make report
```

This replaces the assessment with a single-scenario run. Run `make lab` again to
regenerate the full assessment. List exercises with:

```bash
docker compose run --rm lab list
```

`make up` starts the API on localhost. No credentials are required. Endpoints:
`/`, `/health`, `/version`; unknown paths return JSON with HTTP 404.

Without Make, the core commands are:

```bash
docker compose build lab
docker compose run --rm lab
python3 scripts/export_reports.py
docker compose up -d --wait app
```

## Kubernetes

Install [kind](https://kind.sigs.k8s.io/docs/user/quick-start/) and
[kubectl](https://kubernetes.io/docs/tasks/tools/). `make k8s-up` creates the named
cluster if absent, loads the local image, deploys the app and applies hardened RBAC.
The namespace enforces Kubernetes restricted pod security.

`make k8s-test` temporarily replaces the Role, reads a fake Secret as the CI identity,
restores the Role, checks an actual Forbidden response for the same read, and verifies
that the intended deployment patch still succeeds. Administrator impersonation is a
test method; the lab service account is not granted impersonation permission.

Access the cluster app explicitly:

```bash
kubectl --context kind-pipelineproof -n pipelineproof port-forward service/demo 8081:8080
# In another terminal:
curl http://127.0.0.1:8081/health
```

## Reset

```bash
make down           # stop Compose containers; retain evidence
make clean          # stop Compose containers and delete its evidence volume
make k8s-down       # delete only the named kind cluster
```

Exported files under `reports/` and optional `.work/signing/` keys remain on your
host. Delete those directories manually when no longer needed. Do not delete
unrelated Docker images, volumes, or clusters.

## Troubleshooting

- Docker unavailable: start the daemon and check `docker info`.
- Port 8080 in use: stop the other local service or edit the localhost host port.
- No report found: run `make lab` before `make report`.
- Old evidence: exports overwrite old files, but a failed build cannot generate a
  new assessment. Check the report timestamp and command exit code.
- kind startup fails in a nested/managed container: use a local VM with a supported
  Docker daemon; inspect `kind export logs --name pipelineproof`.
- Scan gate fails: inspect actual findings and update/rebuild the base image. Do not
  silently ignore scan failures to obtain a green badge.
