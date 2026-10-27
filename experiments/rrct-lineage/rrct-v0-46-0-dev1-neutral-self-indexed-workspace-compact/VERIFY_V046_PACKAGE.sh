#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON:-python}"
export PYTHONPATH="$ROOT/src"
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON_BIN" validation/verify_v046_build_manifest.py
PYTHON="$PYTHON_BIN" "$ROOT/RUN_V046_NEUTRAL_WORKSPACE.sh"
"$PYTHON_BIN" validation/audit_v046_postoutcome.py
"$PYTHON_BIN" validation/verify_v046_wheel.py
"$PYTHON_BIN" validation/verify_v046_build_manifest.py
printf '%s\n' 'V046_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED'
