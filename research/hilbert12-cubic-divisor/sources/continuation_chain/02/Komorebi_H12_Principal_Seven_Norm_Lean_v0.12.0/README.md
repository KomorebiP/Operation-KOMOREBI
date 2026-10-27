# Komorebi H12 principal-seven norm — v0.12.0

Start with PROOF.md. The actual gamma norm identity is in section 2. The
principal-transfer rigidity theorem and explicit gauge are in section 4.
The nontrivial gamma correction and the still-missing comparison are not omitted.

## Reproduce

Use Python 3 with SymPy and mpmath (executed versions in MANIFEST.json), and the
user's pinned Lean 4.34.0-rc2 compiler. The multi-gigabyte runtime is not included.

```
python checks/validate_manifest.py MANIFEST.json --root .
python checks/exact_checks.py
python checks/numerical_checks.py --digits 40
python checks/numerical_checks.py --digits 70
python checks/verify_lean.py --lean /absolute/path/to/toolchain/bin/lean
```

Check the shipped manifest BEFORE rerunning. Runs overwrite their evidence with
new timings and runtime paths, so hashes then change as expected. Regenerate an
updated local manifest with `python checks/make_manifest.py`.

The numerical tests have explicit series tails but are not directed interval
certificates. They do not compare to U_alg. See FORMALIZATION_SCOPE.md for the
precise proof-assistant boundary and evidence/FAILURES.md for development errors.
