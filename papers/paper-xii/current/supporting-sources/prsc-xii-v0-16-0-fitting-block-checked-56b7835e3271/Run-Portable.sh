#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then echo "Usage: $0 /path/to/Komorebi_Portable_Lean_4.34.0-rc2" >&2; exit 2; fi
ROOT="$(cd -- "$(dirname -- "$0")" && pwd)"
exec python3 "$ROOT/checks/verify.py" "$1"
