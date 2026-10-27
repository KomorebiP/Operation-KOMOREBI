#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
export PYTHONDONTWRITEBYTECODE=1
cd "$ROOT"
"$PYTHON_BIN" validation/verify_build_manifest.py
"$PYTHON_BIN" validation/verify_freeze.py
"$PYTHON_BIN" validation/verify_results.py
"$PYTHON_BIN" validation/verify_syntax.py
PYTHONPATH="$ROOT/src" "$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests/test_v056.py
printf '%s\n' 'V056_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED'
