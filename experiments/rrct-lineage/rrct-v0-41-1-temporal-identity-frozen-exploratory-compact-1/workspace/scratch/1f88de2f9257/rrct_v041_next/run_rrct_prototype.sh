#!/usr/bin/env sh
set -eu
project_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python -m pip install -e "$project_root[figures]"
python -m rrct.cli verify
python -m rrct.cli demo --output "$project_root/results_v0.4" --seed 17 --train-episodes 256 --test-episodes 128
