#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$ROOT/experiment"
export PYTHONDONTWRITEBYTECODE=1
python "$ROOT/verify_release.py"
python -m pytest -q -p no:cacheprovider "$ROOT/tests"
