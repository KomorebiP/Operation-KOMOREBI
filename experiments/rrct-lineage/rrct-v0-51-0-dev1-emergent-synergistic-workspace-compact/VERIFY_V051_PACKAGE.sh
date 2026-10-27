#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/src"
"$PYTHON_BIN" validation/verify_v051_build_manifest.py
"$PYTHON_BIN" validation/verify_v051_wheel.py
"$PYTHON_BIN" validation/verify_v051_results.py
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests/test_v051_emergent_synergistic_workspace.py
printf '%s\n' 'V051_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED'
