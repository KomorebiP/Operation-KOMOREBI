#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then
  echo 'Usage: bash Run-Reverified.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2' >&2
  exit 2
fi
ROOT="$(cd -- "$(dirname -- "$0")" && pwd)"
bash "$ROOT/Run-Portable.sh" "$1"
python3 "$ROOT/checks/check_final_claims.py" "$1"
