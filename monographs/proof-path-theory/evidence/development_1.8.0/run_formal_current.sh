#!/bin/bash
cd /mnt/data/pp18/Proof_Path_Theory_Monograph_v1.8.0
python -u scripts/verify_lean.py --runtime /mnt/data/tooling/Komorebi_Portable_Lean_4.34.0-rc2 --timeout 240
result=$?
echo "$result" > evidence/development_1.8.0/integrated_formal_run02.exit
exit "$result"
