#!/usr/bin/env bash
# Run all current audit stages serially. Linux or WSL; Python 3 and matching kit required.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# -ne 2 ]]; then
  echo "Usage: bash scripts/run_audit.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output" >&2
  exit 2
fi
KIT="$(cd -- "$1" && pwd)"
OUTPUT="$2"
if [[ -e "$OUTPUT" ]]; then echo "Refusing an existing output path: $OUTPUT" >&2; exit 2; fi
mkdir -p -- "$OUTPUT"
OUTPUT="$(cd -- "$OUTPUT" && pwd)"
run_python() {
  bash "$KIT/run.sh" lake -d "$KIT/workspace" env python3 "$@"
}
run_python "$ROOT/scripts/verify_lean_predecessor.py" \
  --project "$ROOT/source/main" --kit "$KIT" --out "$OUTPUT/main" \
  2>&1 | tee "$OUTPUT/main_console.log"
run_python "$ROOT/scripts/verify_additional.py" \
  --root "$ROOT" --main-run "$OUTPUT/main" --out "$OUTPUT/additional" \
  2>&1 | tee "$OUTPUT/additional_console.log"
run_python "$ROOT/scripts/verify_controls.py" \
  --root "$ROOT" --main-run "$OUTPUT/main" --out "$OUTPUT/controls" \
  2>&1 | tee "$OUTPUT/controls_console.log"
echo "All three audit stages completed. Read each JSON receipt for exact scope."
