#!/usr/bin/env sh
set -eu
release_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$release_root"
export PYTHONPATH="$release_root/reference${PYTHONPATH:+:$PYTHONPATH}"
python reference/verify_core04_package.py
python reference/generate_core04_evidence.py >/dev/null
python reference/generate_core04_bridge_report.py >/dev/null
python reference/generate_core04_adversarial_report.py >/dev/null
python reference/generate_test_report.py >/dev/null
python reference/verify_core04_package.py >/dev/null
printf '%s\n' "OSL-Core 0.4 offline verification passed."
