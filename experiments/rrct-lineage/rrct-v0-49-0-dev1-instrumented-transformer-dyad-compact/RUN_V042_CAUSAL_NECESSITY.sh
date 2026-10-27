#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
"$PYTHON" -c 'import numpy, pytest; print("numpy=" + numpy.__version__); print("pytest=" + pytest.__version__)'
"$PYTHON" -m pip install --disable-pip-version-check --no-deps --no-build-isolation -e "$ROOT"
"$PYTHON" "$ROOT/validation/run_v042_causal_necessity_analysis.py"
"$PYTHON" -m pytest -q "$ROOT/tests/test_v042_causal_self_model_necessity.py"
