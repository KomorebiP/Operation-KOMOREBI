#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${KOMOREBI_LEAN_RUNTIME:?Set to the exact recovered portable RC2 runtime directory}"
export PATH="$KOMOREBI_LEAN_RUNTIME/toolchain/bin:$PATH"
export PYTHONDONTWRITEBYTECODE=1
python verification/prepare_offline.py "$KOMOREBI_LEAN_RUNTIME"
python verification/run_final.py
python verify_release.py --unsealed
# A rerun replaces receipts and compiled artifacts. Regenerate a new release's
# hashes before using sealed integrity replay; never silently reuse old hashes.
