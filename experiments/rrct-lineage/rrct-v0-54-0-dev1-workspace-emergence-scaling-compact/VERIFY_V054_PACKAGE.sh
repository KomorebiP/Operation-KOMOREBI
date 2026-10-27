#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
"$PYTHON_BIN" "$ROOT/validation/verify_v054_build_manifest.py"
PYTHON="$PYTHON_BIN" "$ROOT/RUN_V054_SCALING.sh"
printf '%s\n' 'V054_PACKAGE_VERIFIED'
