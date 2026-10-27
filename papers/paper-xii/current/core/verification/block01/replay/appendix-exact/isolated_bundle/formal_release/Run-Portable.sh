#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then echo 'Usage: bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2' >&2; exit 2; fi
ROOT="$(cd -- "$(dirname -- "$0")" && pwd)"
python3 "$ROOT/checks/verify.py" "$1" --start --batch 4
while python3 - "$ROOT/verification.json" <<'PY'
import json,sys
sys.exit(0 if json.load(open(sys.argv[1]))['status']=='RUNNING' else 1)
PY
do
  python3 "$ROOT/checks/verify.py" "$1" --resume --batch 4
done
python3 - "$ROOT/verification.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]));assert r['status']=='PASS',r
print('Full cumulative Paper XII replay: PASS')
PY
