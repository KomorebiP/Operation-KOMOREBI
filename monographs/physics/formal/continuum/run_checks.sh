#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo "Usage: bash run_checks.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2 [verifier options]" >&2
  exit 2
fi
KIT="$1"
shift
cd "$(dirname "${BASH_SOURCE[0]}")"
exec python3 scripts/verify_block30.py --kit "$KIT" "$@"
