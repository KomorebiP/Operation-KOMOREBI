#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
KIT="${KOMOREBI_LEAN_KIT:?Set KOMOREBI_LEAN_KIT to your portable Lean kit, or use tools/verify.py --kit PATH}"
BUILD="$ROOT/lean/.lake/build/lib/lean"
mkdir -p "$BUILD/KomorebiInformation"
cd "$KIT/workspace"
bash "$KIT/run.sh" lake env bash -c 'export LEAN_PATH="$1:$LEAN_PATH"; shift; exec lean "$@"' \
  komorebi-information "$BUILD" -j1 -DwarningAsError=true -R "$ROOT/lean" "$@"
