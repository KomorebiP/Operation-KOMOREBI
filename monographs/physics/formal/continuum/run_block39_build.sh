#!/usr/bin/env bash
set -o pipefail
R=/mnt/data/lean_offline_parts/Komorebi_Portable_Lean_4.34.0-rc2
P=/mnt/data/kp39_work/Komorebi_Physics_Lean_v0.38.0_Checked_Block_38
cd "$P"
start=$(date +%s)
bash "$R/run.sh" lake -d "$P" build KomorebiPhysics.Relativistic3DEuclideanDyadicProjection > "$P/Block39.module_build.log" 2>&1
rc=$?
end=$(date +%s)
printf '%s\n' "$rc" > "$P/Block39.module_build.rc"
printf '%s\n' "$((end-start))" > "$P/Block39.module_build.elapsed"
exit "$rc"
