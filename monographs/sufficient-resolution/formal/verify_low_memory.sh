#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if [[ $# -lt 1 ]]; then
  echo 'Usage: bash verify_low_memory.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2 [verifier arguments]' >&2
  echo 'Requires the separately supplied matching runtime and pinned Mathlib cache; neither is included here.' >&2
  exit 2
fi
runtime_root="$1"
shift
if [[ ! -f "$runtime_root/run.sh" ]]; then
  echo "Missing pinned portable runtime: $runtime_root/run.sh" >&2
  exit 2
fi
export LEAN_NUM_THREADS=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
# A per-process address-space cap. Lower it only if the pinned imports still fit.
# It is inherited by Lean commands and is not a total process-tree memory cap.
memory_kib="${KOMOREBI_VERIFY_MEMORY_KIB:-4194304}"
case "$memory_kib" in
  ''|*[!0-9]*) echo 'KOMOREBI_VERIFY_MEMORY_KIB must be a positive integer.' >&2; exit 2 ;;
esac
[[ "$memory_kib" -gt 0 ]] || { echo 'Memory limit must be positive.' >&2; exit 2; }
ulimit -v "$memory_kib"
cd -- "$project_root"
exec "${KOMOREBI_VERIFY_PYTHON:-python3}" scripts/verify.py --runtime "$runtime_root" "$@"
