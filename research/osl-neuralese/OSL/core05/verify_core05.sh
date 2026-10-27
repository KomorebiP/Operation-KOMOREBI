#!/usr/bin/env sh
set -eu

release_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$release_root"

python_command=${PYTHON:-python}
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$release_root/reference${PYTHONPATH:+:$PYTHONPATH}"

"$python_command" reference/verify_core05_package.py
"$python_command" reference/generate_core05_evidence.py >/dev/null
"$python_command" reference/generate_core05_bridge_report.py >/dev/null
"$python_command" reference/generate_core05_focused_report.py >/dev/null
"$python_command" reference/generate_test_report.py >/dev/null
"$python_command" reference/verify_core05_package.py >/dev/null

printf '%s\n' "OSL-Core 0.5 offline verification passed."
