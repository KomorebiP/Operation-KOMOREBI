#!/usr/bin/env bash
set +e
bash "/mnt/data/lean_offline_parts/Komorebi_Portable_Lean_4.34.0-rc2/run.sh" lake -d "/mnt/data/kp39_work/Komorebi_Physics_Lean_v0.38.0_Checked_Block_38" env lean -DwarningAsError=true "/mnt/data/kp39_work/Komorebi_Physics_Lean_v0.38.0_Checked_Block_38/KomorebiPhysics/Relativistic3DEuclideanDyadicProjection.lean" > "/mnt/data/kp39_work/Komorebi_Physics_Lean_v0.38.0_Checked_Block_38/Block39.compile.log" 2>&1
rc=$?
echo $rc > "/mnt/data/kp39_work/Komorebi_Physics_Lean_v0.38.0_Checked_Block_38/Block39.compile.rc"
exit $rc
