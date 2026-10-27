#!/usr/bin/env bash
set -euo pipefail
python3 "$(dirname "$0")/repo.py" "${1:-verify}" "${@:2}"
