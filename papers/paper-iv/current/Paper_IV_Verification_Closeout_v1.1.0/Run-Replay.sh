#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ "$#" -ne 2 ]; then
  printf 'Usage: bash Run-Replay.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2 /new/output/directory\n' >&2
  exit 2
fi
exec python3 -B scripts/run_checks.py --mode full --runtime "$1" --work "$2"
