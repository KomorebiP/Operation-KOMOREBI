#!/usr/bin/env bash
set -euo pipefail
package_root="$(cd "$(dirname "$0")/.." && pwd)"
wheelhouse="${1:-$package_root/wheelhouse}"
environment="${2:-$package_root/.venv}"
python3 -m venv "$environment"
"$environment/bin/python" -m pip install --no-index --only-binary=:all: --find-links "$wheelhouse" --constraint "$package_root/requirements-release-lock.txt" 'komorebi-am-spd==1.0.0'
"$environment/bin/python" -m am_spd verify --full
"$environment/bin/python" -m am_spd info
