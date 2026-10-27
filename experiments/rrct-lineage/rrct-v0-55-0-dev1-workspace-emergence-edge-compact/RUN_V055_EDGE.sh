#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/src"
python "$ROOT/validation/run_primary.py"
python "$ROOT/validation/run_crossed.py"
python "$ROOT/analysis/analyze_edge.py"
python -m pytest -q -p no:cacheprovider "$ROOT/tests/test_v055_edge.py"
