#!/usr/bin/env bash
# Fresh new sources and complete serial replay against the authenticated predecessor.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 /absolute/path/to/pinned-runtime /absolute/path/to/new-output" >&2
  exit 2
fi
KIT="$(realpath "$1")"
OUT="$(realpath -m "$2")"
if [[ -e "$OUT" ]]; then echo "Refusing existing output: $OUT" >&2; exit 2; fi
bash "$KIT/run.sh" lake -d "$KIT/workspace" env python3 \
  "$ROOT/scripts/verify_block06.py" --root "$ROOT" --kit "$KIT" --out "$OUT"
