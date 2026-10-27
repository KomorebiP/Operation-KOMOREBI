#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 build_guide_data.py "$@"
python3 build.py
