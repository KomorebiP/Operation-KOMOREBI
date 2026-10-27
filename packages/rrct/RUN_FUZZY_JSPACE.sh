#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
CONFIG="${1:-configs/14_persistent_fuzzy_j_workspace.toml}"
shift || true
"${PYTHON:-python}" -m rrct_lab run "$CONFIG" "$@"
