#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
"${PYTHON:-python}" -m rrct_lab verify
"${PYTHON:-python}" -m pytest -q -p no:cacheprovider
"${PYTHON:-python}" -m rrct_lab smoke --config configs/00_smoke.toml
printf '%s\n' "V060_LOCAL_CHECKS_PASSED"
