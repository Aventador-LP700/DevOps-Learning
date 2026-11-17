#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v trivy >/dev/null || { echo 'Install Trivy first; see docs/tooling.md' >&2; exit 2; }
mkdir -p reports .work/cache/trivy
export TRIVY_CACHE_DIR="${TRIVY_CACHE_DIR:-$PWD/.work/cache/trivy}"
rm -f reports/trivy.json
# Export only this lab image; no Docker socket is passed to scanner containers.
docker save pipelineproof:local -o reports/image.tar
trap 'rm -f reports/image.tar' EXIT
trivy image --scanners vuln --format json --output reports/trivy.json --input reports/image.tar
python3 -m pipelines.hardened.gate reports/trivy.json
