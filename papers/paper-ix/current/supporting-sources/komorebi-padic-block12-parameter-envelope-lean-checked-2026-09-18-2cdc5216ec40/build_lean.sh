#!/usr/bin/env bash
set -euo pipefail
ROOT="${KOMOREBI_LEAN_ROOT:-/mnt/data/lean_compact_runtime/extracted/Komorebi_Portable_Lean_4.34.0-rc2}"
[[ -x "$ROOT/run.sh" ]] || { echo "Set KOMOREBI_LEAN_ROOT to the extracted portable runtime." >&2; exit 2; }
bash "$ROOT/run.sh" attach "$PWD"
export PATH="$ROOT/toolchain/bin:$PATH"
lake build -KwarningAsError=true
