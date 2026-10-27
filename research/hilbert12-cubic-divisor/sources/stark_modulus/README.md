# Hilbert 12: Stark/logarithmic gap closed for the pure cubic test case

Start with **PROOF.md**, then **CONTINUE_HERE.md**.

For the fixed field beta^3=7, the new ordinary proof identifies all six ray partial-zeta derivatives with the logarithms of sigma(W). It proves the exact equality

    |U_gamma| = |U_alg|.

The complex equality U_gamma = U_alg is still unproved. The proof closes a previously missing logarithmic comparison, not the phase problem.

## Files

- `PROOF.md`: full derivation, assumptions, external theorems, corrections, and remaining gap.
- `CONTINUE_HERE.md`: current status and the next phase-sensitive target.
- `checks/exact_checks.py`: standalone rational quotient algebra plus independent SymPy verification. 140 checks.
- `checks/numerical_checks.py`: independent CM/Siegel, Gauss-sum, and gamma evaluations. 27 comparisons at each of 70 and 110 digits, plus negative controls.
- `checks/verify_manifest.py`: validates the shipped evidence records and file hashes. This is a provenance checker, not a mathematical proof checker.
- `evidence/`: actual results, logs, per-run manifests, and the failed exploratory draft.
- `SOURCE_LEDGER.md`: external theorem locators and which implications they supply.
- `predecessors/`: the nine retained earlier Markdown files, unchanged. They are historical snapshots; their statements that the Stark logarithmic comparison is open are superseded by this checkpoint. Their gamma phase gap is not superseded. These are predecessor proof notes, not a claim that every historical code bundle has been included.

## Verify and rerun

Tested on Python 3.13.5, SymPy 1.14.0, mpmath 1.3.0.

```text
python -m pip install sympy==1.14.0 mpmath==1.3.0
python checks/verify_manifest.py
python checks/exact_checks.py
python checks/numerical_checks.py
```

Run the manifest checker before recomputation to authenticate the shipped output files. Re-running a calculation changes the recorded runtime and therefore the output hash. No Lean certificate or interval-rounding certificate is included.

Ordinary proof dependencies: classical Artin induction, cubic reciprocity, the class number formula, Kronecker's limit formula with the normalization derived here, classical elliptic addition, BCG Theorem 3.2, and the explicit field/CM branch constructions in the predecessor notes. None requires assuming the desired gamma algebraicity.
