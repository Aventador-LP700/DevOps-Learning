#!/usr/bin/env bash
# Pinned Linux amd64 release artifacts, verified against recorded SHA256 values.
set -euo pipefail
cd "$(dirname "$0")/.."
[[ "$(uname -s)-$(uname -m)" == Linux-x86_64 ]] || { echo 'This helper supports Linux amd64 only. See official installation docs.' >&2; exit 2; }
mkdir -p .work/bin
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
fetch() {
  curl --fail --silent --show-error --location --retry 3 "$1" -o "$scratch/$2"
  echo "$3  $scratch/$2" | sha256sum --check
}
for tool in "$@"; do
  case "$tool" in
    trivy)
      fetch https://github.com/aquasecurity/trivy/releases/download/v0.76.2/trivy_0.76.2_Linux-64bit.tar.gz trivy.tar.gz bc0fc726e017b8927a62b2d3531d7a84ee01769daf5c99ed866dced54089fdbf
      tar -xzf "$scratch/trivy.tar.gz" -C "$scratch" trivy
      install -m 755 "$scratch/trivy" .work/bin/trivy ;;
    syft)
      fetch https://github.com/anchore/syft/releases/download/v1.57.2/syft_1.57.2_linux_amd64.tar.gz syft.tar.gz ad92bd3ec1b94a3df01d4d0aec199afa9c42b72e86da436ff5f837914d32706b
      tar -xzf "$scratch/syft.tar.gz" -C "$scratch" syft
      install -m 755 "$scratch/syft" .work/bin/syft ;;
    cosign)
      fetch https://github.com/sigstore/cosign/releases/download/v2.5.3/cosign-linux-amd64 cosign 783b5d6c74105401c63946c68d9b2a4e1aab3c8abce043e06b8510b02b623ec9
      install -m 755 "$scratch/cosign" .work/bin/cosign ;;
    gitleaks)
      fetch https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz gitleaks.tar.gz 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb
      tar -xzf "$scratch/gitleaks.tar.gz" -C "$scratch" gitleaks
      install -m 755 "$scratch/gitleaks" .work/bin/gitleaks ;;
    *) echo "Unknown tool: $tool" >&2; exit 2 ;;
  esac
done
echo 'Installed requested tools. Add this repository .work/bin directory to PATH.'
