#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
"$PYTHON_BIN" "$ROOT/analysis/uncertainty_analysis.py"
"$PYTHON_BIN" "$ROOT/analysis/validate_scaling_law.py"
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider "$ROOT/tests/test_v054_scaling.py"
"$PYTHON_BIN" "$ROOT/validation/verify_v054_release.py"
