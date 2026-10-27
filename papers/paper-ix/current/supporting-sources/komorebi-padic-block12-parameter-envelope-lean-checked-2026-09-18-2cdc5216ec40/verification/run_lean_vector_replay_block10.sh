#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

run_one() {
  local source="$1"
  local stem log timefile ec
  stem="$(basename "$source" .lean)"
  log="logs/${stem}_block10_replay.log"
  timefile="logs/${stem}_block10_replay.time"
  set +e
  /usr/bin/time -f 'elapsed_seconds=%e\nmax_rss_kb=%M' -o "$timefile" \
    timeout --signal=TERM --kill-after=10s 240s \
      lake env lean -DwarningAsError=true "$source" > "$log" 2>&1
  ec=$?
  set -e
  printf 'exit_code=%s\n' "$ec" >> "$timefile"
  printf '%s exit=%s\n' "$source" "$ec"
  [[ "$ec" -eq 0 ]]
}

run_batch() {
  local source
  for source in "$@"; do run_one "$source"; done
}

# Small batches make outer execution-window failures easy to resume and audit.
run_batch \
  verification/LeanCompilerVector.lean \
  verification/LeanSuffixWindowVector.lean \
  verification/LeanBoundaryVector.lean \
  verification/LeanComplexityVector_01.lean \
  verification/LeanComplexityVector_02.lean \
  verification/LeanComplexityVector_03.lean \
  verification/LeanComplexityVector_04.lean
run_batch verification/LeanComplexityVector_{05..11}.lean
run_batch verification/LeanComplexityVector_{12..18}.lean
run_batch verification/LeanComplexityVector_{19..25}.lean
run_batch verification/LeanClosedFormVector_{01..07}.lean
run_batch verification/LeanClosedFormVector_{08..14}.lean
run_batch verification/LeanClosedFormVector_{15..17}.lean
python3 verification/collect_lean_vector_replay_block10.py
