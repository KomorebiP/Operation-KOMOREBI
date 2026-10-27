# H12 CM-threefold bridge v0.7.0

Start with PROOF.md and FORMALIZATION_SCOPE.md. The main result is an explicit
split fixed-point sequence for the original cubic-unit matrix, with oriented
seven-torsion kernel E[J], plus the joined-order conductor calculation.
The original gamma-arithmetic equality is not proved.

## Reproduce

Python 3 with SymPy is required for exact checks. The new Lean modules use only
bundled Std and the same pinned Lean 4.34.0-rc2 used by the predecessor.

```sh
python checks/validate_manifest.py MANIFEST.json --root .
python checks/exact_checks.py
python checks/verify_lean.py --lean /path/to/toolchain/bin/lean
```

The checks overwrite their own evidence with current runtimes; validate the
shipped manifest BEFORE rerunning. No runtime binaries are distributed here.
No broad Mathlib import or network fetch is needed for the new formal files.

The prior v0.6.0 ZIP is preserved with its historical evidence. This package's
fresh verification applies to its own 44 theorems, not all cumulative sources.
