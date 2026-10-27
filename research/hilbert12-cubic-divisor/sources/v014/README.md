# Cubic Divisor Regularization v0.14.0

Read PROOF.md for the new results and FORMALIZATION_SCOPE.md for the exact
kernel-checked boundary. The original gamma-arithmetic equality remains open.

Reproduce with Python 3 plus SymPy and mpmath, and the user's pinned portable
Lean 4.34.0-rc2 runtime. The runtime is not distributed in this source archive.

```sh
python checks/validate_manifest.py MANIFEST.json --root .
python checks/exact_checks.py
python checks/numerical_checks.py --digits 40
python checks/numerical_checks.py --digits 70
python checks/verify_lean.py --lean /absolute/path/to/toolchain/bin/lean
```

The first command validates shipped output hashes. Subsequent commands
regenerate evidence files and can change runtime fields; rerun hashes describe
a new run, not the shipped manifest. The main mathematical objects are the
explicit divisor product W_D, its cubic exponential correction, and the
branch-free expression for R7(1/3)^3. The infinite product is specified and
proved convergent; no infinite product truncation has been certified numerically.
