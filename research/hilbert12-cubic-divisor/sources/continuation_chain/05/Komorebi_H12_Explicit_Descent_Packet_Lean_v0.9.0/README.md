# Komorebi H12: explicit descent packet v0.9.0

Start with PROOF.md and FORMALIZATION_SCOPE.md. The main gamma-arithmetic
comparison remains unproved. New: an explicit compact seven-dimensional
projective model, mixed-period cochain, twisted-unit lift, simultaneous-
invariance obstruction, and coherent three-class replacement.

Reproduce from this directory:

```sh
python checks/validate_manifest.py MANIFEST.json --root .
python checks/exact_checks.py
python checks/verify_lean.py --lean /absolute/path/to/pinned/toolchain/bin/lean
```

The first command validates the shipped hashes. The other commands overwrite
their own result files and timings, so check the shipped manifest before reruns.
The Lean toolchain is not included. Use the pinned Lean 4.34.0-rc2 compiler;
bundled Std suffices. Exact checks require SymPy (executed version is in evidence).
No network, floating-point gamma evaluation, or Mathlib import is used by the
checkers. The exact and Lean checkers have fixed finite input families; Lean
uses a 90-second per-module cap and one worker.

The previous v0.8 source/evidence is preserved in prior/, not presented as
freshly replayed. Refer to evidence/FAILURES.md for all corrected failures in
this block. REVIEW.md records the mathematical trust boundary.
