#!/usr/bin/env bash
# Native entry point: standard-library Python only; no Docker, pip, sudo or downloads.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
usage() {
  cat <<'HELP'
Usage: bash ./setup.sh [--lab-only | --serve-only] [--port PORT] [--output DIRECTORY]

Default: run the four native exercises, save reports, then serve the API on localhost.
  --lab-only       Run exercises and exit (suitable for CI).
  --serve-only     Serve the demo API without running exercises.
  --port PORT      Local API port (default: 8080).
  --output DIR     Report directory relative to this repo or absolute (default: reports).
  --help           Show this help.

Requirements: Bash, Python 3.10+, /bin/sh and printf on Linux/macOS/WSL2.
Native practice runs fixed harmless proofs as your user, without container isolation.
Use a disposable VM for modified attack payloads. Kubernetes/image tooling is separate.
HELP
}
mode=all
port=8080
output=reports
while (($#)); do
  case "$1" in
    --lab-only|--serve-only)
      [[ "$mode" == all ]] || { echo 'Choose only one execution mode.' >&2; exit 2; }
      mode="${1#--}"; shift ;;
    --port|--output)
      (($# >= 2)) || { echo "Missing value for $1" >&2; exit 2; }
      if [[ "$1" == --port ]]; then port="$2"; else output="$2"; fi
      shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done
command -v python3 >/dev/null || { echo 'Install Python 3.10+ from python.org or your OS package manager, then rerun.' >&2; exit 2; }
command -v printf >/dev/null && [[ -x /bin/sh ]] || { echo 'POSIX sh and printf are required; use Linux, macOS or WSL2.' >&2; exit 2; }
python3 - "$port" <<'CHECK'
import os, sys
if sys.version_info < (3, 10) or os.name != "posix":
    raise SystemExit("Python 3.10+ on Linux, macOS or WSL2 is required.")
port = sys.argv[1]
if not port.isascii() or not port.isdecimal() or not 1 <= int(port) <= 65535:
    raise SystemExit("Port must be a number between 1 and 65535.")
CHECK
export PYTHONDONTWRITEBYTECODE=1
if [[ "$mode" != serve-only ]]; then
  python3 -m lab.cli run --native --output "$output"
fi
if [[ "$mode" != lab-only ]]; then
  exec python3 -m app.server --host 127.0.0.1 --port "$port"
fi
