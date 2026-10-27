#!/usr/bin/env bash
# Run both stages from empty output directories with the pinned offline runtime.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 /absolute/path/to/portable-runtime /absolute/path/to/new-output" >&2
  exit 2
fi
KIT="$(realpath "$1")"
OUT="$(realpath -m "$2")"
if [[ -e "$OUT" ]]; then echo "Refusing existing output: $OUT" >&2; exit 2; fi
mkdir -p "$OUT"
bash "$ROOT/predecessor/scripts/run_block03.sh" "$KIT" "$OUT/baseline"
bash "$KIT/run.sh" lake -d "$KIT/workspace" env python3 \
  "$ROOT/scripts/verify_block04.py" --root "$ROOT" --kit "$KIT" \
  --baseline "$OUT/baseline" --out "$OUT/extension"
