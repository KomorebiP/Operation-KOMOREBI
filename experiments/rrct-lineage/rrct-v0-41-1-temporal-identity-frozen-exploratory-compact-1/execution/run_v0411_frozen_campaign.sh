#!/usr/bin/env bash
set -uo pipefail

project_root=/workspace/scratch/1f88de2f9257/rrct_v041_next
log_root=/tmp/rrct-v0411-frozen-pilot-logs
mkdir -p "$log_root"

seeds=(280842095 305790955 582368056 887738207)
conditions=(K_RPLUS N_RPLUS G_RPLUS K_RMINUS N_RMINUS G_RMINUS)
aggregate_rc=0
launched=0

for seed in "${seeds[@]}"; do
  pids=()
  for condition in "${conditions[@]}"; do
    attempt="PILOT_${seed}_${condition}"
    (
      cd "$project_root" || exit 125
      exec env \
        UV_CACHE_DIR=/tmp/rrct_uv_cache \
        PYTHONHASHSEED=0 \
        OPENBLAS_NUM_THREADS=1 \
        OMP_NUM_THREADS=1 \
        MKL_NUM_THREADS=1 \
        uv run python -s -P -B validation/run_v041_frozen_seed.py \
          --project-root "$project_root" \
          --seed "$seed" \
          --condition-id "$condition" \
          --attempt-id "$attempt"
    ) >"$log_root/$attempt.log" 2>&1 &
    pids+=("$!")
    launched=$((launched + 1))
  done

  for pid in "${pids[@]}"; do
    if ! wait "$pid"; then
      aggregate_rc=1
    fi
  done
done

printf 'launched=%d aggregate_rc=%d log_root=%s\n' "$launched" "$aggregate_rc" "$log_root"
exit "$aggregate_rc"
