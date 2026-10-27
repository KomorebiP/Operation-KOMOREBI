#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
CONFIG="${1:-configs/12_continuous_open_set_runtime.toml}"
shift || true
"${PYTHON:-python}" -m rrct_lab run "$CONFIG" "$@"
