#!/usr/bin/env bash
# Detached signatures for exported artifacts; use only throwaway lab keys here.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v cosign >/dev/null || { echo 'Install Cosign; see docs/tooling.md' >&2; exit 2; }
command -v syft >/dev/null || { echo 'Install Syft; see docs/tooling.md' >&2; exit 2; }
mkdir -p .work/signing reports
if [[ -e .work/signing/cosign.key || -e .work/signing/cosign.pub ]]; then
  echo 'Signing keys already exist. Reuse manually or remove .work/signing first.' >&2
  exit 2
fi
syft pipelineproof:local -o spdx-json=reports/sbom.spdx.json
# Intentionally passwordless ephemeral LAB key, never a production signing identity.
export COSIGN_PASSWORD=''
cosign generate-key-pair --output-key-prefix .work/signing/cosign
cosign sign-blob --yes --tlog-upload=false --key .work/signing/cosign.key --output-signature reports/sbom.sig reports/sbom.spdx.json
cosign verify-blob --key .work/signing/cosign.pub --signature reports/sbom.sig --insecure-ignore-tlog reports/sbom.spdx.json
python3 -c 'from pathlib import Path; p=Path("reports/sbom.spdx.json"); Path("reports/tampered.spdx.json").write_bytes(p.read_bytes()+b"tampered")'
if cosign verify-blob --key .work/signing/cosign.pub --signature reports/sbom.sig --insecure-ignore-tlog reports/tampered.spdx.json; then
  echo 'FAIL: tampered SBOM accepted' >&2; exit 1
fi
echo 'PASS: original signature verified; tampered SBOM rejected'
