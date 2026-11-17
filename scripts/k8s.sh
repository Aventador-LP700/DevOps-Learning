#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for tool in kind kubectl docker; do
  command -v "$tool" >/dev/null || { echo "Missing tool: $tool" >&2; exit 2; }
done
context=kind-pipelineproof
k() { kubectl --context="$context" "$@"; }
case "${1:-}" in
  up)
    if ! kind get clusters | grep -qx pipelineproof; then
      kind create cluster --config infra/kind.yaml --wait 120s
    fi
    docker compose build
    kind load docker-image pipelineproof:local --name pipelineproof
    k apply -f infra/kubernetes/base.yaml
    k apply -f infra/kubernetes/hardened-rbac.yaml
    k -n pipelineproof rollout status deployment/demo --timeout=120s
    ;;
  test)
    k get namespace pipelineproof >/dev/null
    mkdir -p reports
    # Always restore least privilege, including after a failed attack assertion.
    trap 'k apply -f infra/kubernetes/hardened-rbac.yaml >/dev/null' EXIT
    k apply -f infra/kubernetes/vulnerable-rbac.yaml >/dev/null
    k -n pipelineproof create secret generic synthetic-ci-secret --from-literal=token=PP_SYNTHETIC_ONLY --dry-run=client -o yaml | k apply -f - >/dev/null
    identity=system:serviceaccount:pipelineproof:ci-deployer
    vulnerable=$(k -n pipelineproof get secret synthetic-ci-secret --as="$identity" -o jsonpath='{.data.token}')
    [[ "$vulnerable" == UFBfU1lOVEhFVElDX09OTFk= ]] || { echo 'FAIL: expected synthetic secret read' >&2; exit 1; }
    k apply -f infra/kubernetes/hardened-rbac.yaml >/dev/null
    if k -n pipelineproof get secret synthetic-ci-secret --as="$identity" >reports/rbac-secret.stdout 2>reports/rbac-secret.stderr; then
      echo 'FAIL: hardened identity can read secret' >&2; exit 1
    fi
    # Verify denial is authorization-related, not a lost API connection.
    grep -q Forbidden reports/rbac-secret.stderr
    k -n pipelineproof patch deployment demo --as="$identity" --type=merge -p '{"spec":{"replicas":1}}' >/dev/null
    python3 - <<'REPORT'
import json
from datetime import datetime, timezone
from pathlib import Path
report = {"scenario": "excessive-deployment-permissions", "generated_at": datetime.now(timezone.utc).isoformat(), "vulnerable_secret_read": True, "hardened_secret_read_forbidden": True, "hardened_deployment_patch_allowed": True, "passed": True, "method": "Real Kubernetes API requests using administrator impersonation of lab CI service account"}
Path("reports/rbac.json").write_text(json.dumps(report, indent=2)+"\n")
REPORT
    echo 'PASS: secret stolen under vulnerable Role; forbidden after hardening; deployment patch allowed'
    ;;
  down) kind delete cluster --name pipelineproof ;;
  *) echo 'Usage: bash scripts/k8s.sh {up|test|down}' >&2; exit 2 ;;
esac
