#!/usr/bin/env bash
set -euo pipefail
PHASE="${1:-all}"
ROOT="${KOMOREBI_LEAN_ROOT:-/mnt/data/lean_compact_runtime/extracted/Komorebi_Portable_Lean_4.34.0-rc2}"
[[ -x "$ROOT/run.sh" ]] || { echo "Set KOMOREBI_LEAN_ROOT to the extracted portable runtime." >&2; exit 2; }
export PATH="$ROOT/toolchain/bin:$PATH" TERM=dumb
prepare(){ bash "$ROOT/run.sh" attach "$PWD"; lean --version; lake --version; }
build(){ prepare; lake build -KwarningAsError=true; }
kernel(){ build; python3 verification/audit_source_block12.py; python3 verification/generate_axiom_audit_block12.py; lake env lean -DwarningAsError=true verification/AxiomAuditBlock12.lean > logs/axiom_audit_block12.log 2>&1; python3 verification/parse_axiom_audit_block12.py; }
vectors(){ prepare; for f in verification/LeanParameter*Vector_[0-9][0-9].lean; do lake env lean -DwarningAsError=true "$f"; done; }
finite(){ python3 verification/verify_parameter_envelope.py; }
controls(){ prepare; python3 verification/verify_negative_controls_block12.py; }
release(){ python3 verification/verify_release.py --root .; }
case "$PHASE" in
 prepare) prepare;; build) build;; kernel) kernel;; vectors) vectors;; finite) finite;; controls) controls;; release) release;; all) kernel; vectors; finite; controls; release;; *) echo "Usage: bash verify_all.sh {prepare|build|kernel|vectors|finite|controls|release|all}" >&2; exit 2;; esac
