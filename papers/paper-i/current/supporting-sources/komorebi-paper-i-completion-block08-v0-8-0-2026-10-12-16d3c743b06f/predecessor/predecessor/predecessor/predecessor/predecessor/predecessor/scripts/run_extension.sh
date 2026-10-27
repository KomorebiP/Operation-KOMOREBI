#!/usr/bin/env bash
# Linux / WSL. All arguments are directories; OUT must not already exist.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# -ne 3 ]]; then
  echo "Usage: bash scripts/run_extension.sh /path/to/pinned-kit /path/to/successful-baseline-run /path/to/new-output" >&2
  exit 2
fi
KIT="$(cd -- "$1" && pwd)"
BASE_RUN="$(cd -- "$2" && pwd)"
OUT="$3"
bash "$KIT/run.sh" lake -d "$KIT/workspace" env python3 "$ROOT/scripts/verify_extension.py" \
  --source "$ROOT/source/extension" --tests "$ROOT/tests" \
  --baseline-root "$ROOT/baseline" --baseline-run "$BASE_RUN" \
  --coverage "$ROOT/coverage/COVERAGE_108.json" --out "$OUT"
