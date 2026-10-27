#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/src"
"$PYTHON_BIN" -c 'import torch, numpy; print("torch="+torch.__version__); print("numpy="+numpy.__version__)'
"$PYTHON_BIN" validation/verify_v049_results.py
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests/test_v049_instrumented_transformer_dyad.py
printf '%s\n' 'V049_RESULTS_AND_FOCUSED_TESTS_VERIFIED'
