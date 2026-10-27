#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then echo "Usage: bash Run-Portable.sh /path/to/extracted/kit" >&2; exit 2; fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$(cd "$1" && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-python3}"
"$PYTHON" -m unittest discover -s tests -v
"$PYTHON" scripts/regressions.py
"$PYTHON" scripts/second_regressions.py
"$PYTHON" scripts/third_regressions.py
"$PYTHON" scripts/verify.py --kit "$KIT"
