# Komorebi H12: polarized CM comparison, v0.6.0

Read PROOF.md and FORMALIZATION_SCOPE.md first. The new exact result is an arithmetic cube factorization and positive-real polarization. The gamma equality remains open.

## Reproduce the accepted block

```
python checks/validate_manifest.py MANIFEST.json --root .
python checks/exact_checks.py
python checks/interval_checks.py --digits 90
python checks/interval_checks.py --digits 120
python checks/verify_new_lean.py --runtime PATH_TO_PINNED_LEAN_KIT
```

Python dependencies: SymPy and mpmath. Runtime: the user's portable Lean 4.34.0-rc2, Mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The multi-gigabyte runtime is not included.

Reruns overwrite result files and change timings/hashes; validate the shipped manifest first. The accepted verifier compiles 18 new theorems and their inherited cubic-branch dependency in a fresh directory. It does not claim a full replay of the 154 inherited theorem constants.

The other Lean replay scripts are retained for provenance and full-project continuation, not as evidence that the full inherited replay succeeded. See evidence/FAILURES.md.

The deliverable preserves the complete predecessor source-and-evidence ZIP and unchanged inherited theorem sources. There is no Library mutation or upload-back in this run.
