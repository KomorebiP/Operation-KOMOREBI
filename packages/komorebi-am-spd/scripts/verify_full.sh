#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARCHIVE_SOURCE="$ROOT/research/original"
if [[ ! -f "$ARCHIVE_SOURCE/verify_am_spd_final.py" ]]; then
    echo "Historical verification requires the full source bundle containing research/original. Use python -m am_spd verify --full for the installed package." >&2
    exit 1
fi
ARTIFACT="$ROOT/artifacts/verification"
mkdir -p "$ARTIFACT"
RUN_DIRECTORY="$(mktemp -d "$ARTIFACT/run_$(date -u +%Y%m%d_%H%M%S)_XXXXXX")"
WORKING_SOURCE="$RUN_DIRECTORY/research"
mkdir "$WORKING_SOURCE"
cp -a "$ARCHIVE_SOURCE/." "$WORKING_SOURCE/"
LOG="$RUN_DIRECTORY/full_verification.log"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$ROOT"
python -m am_spd verify --full 2>&1 | tee "$LOG"
cd "$WORKING_SOURCE"
python infinite_packet_gibbs_reconstruction.py --tests-only 2>&1 | tee -a "$LOG"
python verify_singular_packet_decomposition.py 2>&1 | tee -a "$LOG"
python verify_am_spd.py 2>&1 | tee -a "$LOG"
python verify_am_spd_final.py 2>&1 | tee -a "$LOG"
echo "$LOG"
