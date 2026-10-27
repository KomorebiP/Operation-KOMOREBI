# Komorebi Model-Theory Normalization v0.9

The new costed evaluator computes the same observation-discovery result as v0.8,
with a verified exact high-level arithmetic counter and an explicit polynomial
upper bound. It is not a compiled-runtime or bit-complexity theorem.

Start with NORMALIZED_CORE.md, COST_MODEL.md, FORMALIZATION_COVERAGE.md and RESULTS.md.
Run distribution integrity BEFORE rerunning audits, since audits rewrite results:

    python checks/verify_integrity.py
    python checks/audit_python.py

For a new local cold Lean audit, supply the exact pinned portable runtime. Preserve
old audit evidence before resetting evidence/cold/STATE.json. The driver refuses
to overwrite an existing state:

    python checks/audit_lean.py --runtime /path/to/pinned/runtime --init
    python checks/audit_lean.py --run

The runtime must have toolchain/bin/lean and the pinned workspace/.lake/packages
cache layout. No runtime or upstream cache is shipped here. lean-toolchain and
evidence/ENVIRONMENT.json pin Lean 4.34.0-rc2 and Mathlib revision.

history/ contains the immutable full v0.8 ZIP. This tree retains every inherited
Lean library source under formalization/, but rebuilds only the dependency closure for the new targets. These
are independent ZIPs, not multipart segments. The new Python port is tested, not
verified code extraction. All claims have scope boundaries recorded explicitly.
