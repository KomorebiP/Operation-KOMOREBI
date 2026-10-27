#!/usr/bin/env bash
# Linux or WSL, Python 3. KIT is the pinned portable runtime; OUT must not exist.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# -ne 2 ]]; then
  echo "Usage: bash scripts/run_block03.sh /absolute/path/to/pinned-kit /absolute/path/to/new-output" >&2
  exit 2
fi
KIT="$(cd -- "$1" && pwd)"
OUT="$2"
if [[ "$OUT" != /* ]]; then echo 'OUT must be an absolute path' >&2; exit 2; fi
bash "$KIT/run.sh" lake -d "$KIT/workspace" env python3 "$ROOT/scripts/verify_block03.py" \
  --root "$ROOT" --kit "$KIT" --out "$OUT"
