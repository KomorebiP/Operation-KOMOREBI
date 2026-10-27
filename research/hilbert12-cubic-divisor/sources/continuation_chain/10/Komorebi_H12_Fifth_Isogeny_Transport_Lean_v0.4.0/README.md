# Komorebi H12 fifth-isogeny transport, v0.4.0

Read PROOF.md for the mathematical statements and FORMALIZATION_SCOPE.md for the exact Lean boundary. The new result is an explicit normalized fifth-isogeny map, its moduli transformations, and its differential relation to the gamma transport. The gamma-arithmetic comparison is still open.

## Reproduce

Python requirements are in requirements.txt. From this directory:

```bash
python checks/validate_manifest.py MANIFEST.json --root .
python checks/exact_checks.py
python checks/numerical_checks.py --digits 40
python checks/numerical_checks.py --digits 70
python checks/run_lean.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --part 1
python checks/run_lean.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --part 2
python checks/run_lean.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --part 3
python checks/run_lean.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --part 4
```

The runtime is external and not bundled. The compiler and Mathlib pins are checked by the runner. Run the manifest check before reproduction: tests overwrite result logs and execution times, so a rerun changes evidence hashes.

All 140 theorem constants, including the inherited 109, are rebuilt in an isolated `.lean-check` directory. The final stage audits every theorem's transitive axioms and requires a false statement to be rejected. Stages 1-3 are explicitly not whole-project pass verdicts.

The numerical evaluations are not interval certificates. The independent differentiated gamma series tests the new inhomogeneous equations, not equality with U_alg. No algebraic candidate is fitted or evaluated by the new tests.
