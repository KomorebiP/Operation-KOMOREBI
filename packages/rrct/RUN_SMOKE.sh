#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
"${PYTHON:-python}" -m rrct_lab smoke --config "$ROOT/configs/00_smoke.toml"
