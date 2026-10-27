#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then echo "Usage: bash Run-Portable.sh /path/to/extracted/kit" >&2; exit 2; fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$(cd "$1" && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/check_manifest.py
"$PYTHON" -m unittest discover -s extension_tests -v
"$PYTHON" scripts/eleventh_regressions.py
"$PYTHON" scripts/verify.py --kit "$KIT"
"$PYTHON" scripts/check_manifest.py
