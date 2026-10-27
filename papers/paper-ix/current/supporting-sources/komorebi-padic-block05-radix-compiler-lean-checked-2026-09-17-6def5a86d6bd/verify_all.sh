#!/usr/bin/env bash
set -euo pipefail

lake build -KwarningAsError=true
lake env lean -DwarningAsError=true lean/KomorebiPadic.lean
lake env lean -DwarningAsError=true verification/LeanCompilerVector.lean
lake env lean -DwarningAsError=true verification/AxiomAudit.lean
python verification/verify_radix_compiler.py

if lake env lean -DwarningAsError=true verification/RejectFalse.lean \
    > logs/reject_false.reproduced.log 2>&1; then
  echo 'ERROR: false-theorem negative control unexpectedly succeeded' >&2
  exit 1
fi
if lake env lean -DwarningAsError=true verification/RejectSorry.lean \
    > logs/reject_sorry.reproduced.log 2>&1; then
  echo 'ERROR: sorry negative control unexpectedly succeeded' >&2
  exit 1
fi

echo 'Block 05 verification passed.'
