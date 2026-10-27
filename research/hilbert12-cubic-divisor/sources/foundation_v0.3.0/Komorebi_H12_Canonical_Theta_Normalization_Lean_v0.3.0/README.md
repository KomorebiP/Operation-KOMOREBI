# H12 canonical theta normalization — v0.3.0

The main theorem is

    theta0(z;t)^5/theta0(5z;5t)
      = (wp_t(1/5)-wp_t(2/5))^2
        /[(wp_t(z)-wp_t(1/5))(wp_t(z)-wp_t(2/5))].

The separate eta normalizer is now fixed by the fifth-torsion kernel. All first-order signed unit carries retain their exact normalization in rational elliptic coordinates. The arithmetic evaluation of the gamma limit remains open.

Read PROOF.md and FORMALIZATION_SCOPE.md before interpreting the verification counts.

## Reproduce

Check the shipped hashes before running scripts that regenerate evidence:

    python checks/validate_manifest.py MANIFEST.json --root .

Dependencies: Python, SymPy 1.14.0, mpmath 1.3.0. The user's pinned offline Lean runtime is external and is not bundled.

    python checks/exact_checks.py
    python checks/numerical_checks.py --digits 40
    python checks/numerical_checks.py --digits 70
    python checks/run_lean.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --part 1
    python checks/run_lean.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --part 2
    python checks/run_lean.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --part 3

The Lean build is intentionally split into three synchronous stages. Stage 1 starts a clean build; later stages authenticate the previous compiled files and all current source hashes. A partial stage is not a complete verification verdict.

The numerical scripts are regression tests, not interval proofs or algebraicity tests. No U_alg is evaluated. Rerunning scripts changes recorded runtimes and evidence hashes; the shipped manifest authenticates the delivered run.
