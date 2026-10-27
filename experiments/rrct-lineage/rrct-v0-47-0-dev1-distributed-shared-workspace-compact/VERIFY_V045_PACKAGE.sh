#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON:-python}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/src"
"$PYTHON_BIN" validation/verify_v045_build_manifest.py
"$PYTHON_BIN" validation/verify_v045_built_wheel.py
PYTHON="$PYTHON_BIN" bash "$ROOT/RUN_V045_KOMOREBI_OPERATOR.sh"
printf '%s\n' 'V045_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED'
