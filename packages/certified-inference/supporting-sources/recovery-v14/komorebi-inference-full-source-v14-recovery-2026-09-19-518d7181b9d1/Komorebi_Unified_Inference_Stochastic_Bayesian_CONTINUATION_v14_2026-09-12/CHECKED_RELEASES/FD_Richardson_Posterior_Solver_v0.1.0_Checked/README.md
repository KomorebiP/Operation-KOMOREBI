# Exact Richardson posterior solver — v0.1.0

**Status: CLOSED / LEAN CHECKED for the stated exact-rational contract.**

The executable gain solver now has a proved successful finite-termination theorem
for every valid factor-coded model, fixed complete self-adjoint rational packet
geometry, arbitrary rational starting gain and positive rational tolerance.
Its return has an actual Bayesian-posterior Wasserstein-2 guarantee.

Read `PROOF_NOTE.md` for the mathematical statement, hypotheses and boundaries.
The main proof is `Komorebi/RationalSolverPosterior.lean`:

```
Komorebi.ExactPosterior.solver_reaches_posterior_tolerance
```

## Run an exact example

From this directory, using Python 3.11 or newer:

```bash
python checks/solve_richardson.py examples/solver_scalar.json --output results/my_scalar.json --emit-lean Komorebi/MyScalar.lean --namespace MyScalar
```

The producer uses Python standard-library exact `Fraction` arithmetic. Inputs use
integers and exact fraction/decimal strings. JSON floats are rejected. Read
`examples/solver_scalar.json` or `examples/solver_rotated.json` for the full schema.
The root object contains exactly `model`, `initial_gain` and `epsilon`.

`PASS_EXACT_DIAGNOSTIC` is provisional until the exported Lean module is checked.
The explicit data in that Lean file is the mathematical input being certified.
Parsing, serialization and export fidelity are not universally formalized.

The Python utility imposes a step cap (default 10000) and a bit-size check on each
proposed gain entry (default 32768 bits). These are not OS memory/CPU limits and
do not bound every intermediate arithmetic object. On a resource cap the tool
returns `RESOURCE_LIMIT`, exits with status 2, and does not export a success
proof. Invalid inputs fail explicitly. The ideal Lean solver uses proved finite
fuel and has no externally imposed resource cap.

## Reproduce the proof checks in bounded blocks

Required pinned environment:

- Lean `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- The portable runtime's `run.sh` and `workspace` layout.

Set `RUNTIME` to the unpacked portable runtime directory. Clear only this active
project's compiled outputs once, then follow `MODULE_ORDER.json` sequentially.
Do not run competing Lean builds in parallel.

```bash
python verify_blocks.py --runtime "$RUNTIME" --clean --modules
python verify_blocks.py --runtime "$RUNTIME" --modules FDKalmanDefs FDInnovationIdentities --timeout 40
# Continue in MODULE_ORDER.json order in bounded calls.
python verify_blocks.py --runtime "$RUNTIME" --modules RichardsonSolverAxiomAudit --timeout 40
python checks/test_richardson.py
python checks/negative_controls.py --runtime "$RUNTIME"
python audit_integrity.py --runtime "$RUNTIME" --seal
```

The independent diagnostics require the version recorded in
`requirements-checks.txt`; the exact solver itself does not require SymPy.
After dependencies are built, check a newly exported example with:

```bash
python verify_blocks.py --runtime "$RUNTIME" --modules MyScalar --timeout 40
```

This does not automatically add that example to the sealed active declaration
inventory. A new release must regenerate and audit its changed inventory.

## Evidence

- `FINAL_VERIFICATION_RECEIPT.json`: successful final-source compile receipts,
  direct-dependency hashes, failed attempts, diagnostics and audit summary.
- `DECLARATIONS.json`, `AXIOM_AUDIT.json`: all 294 active declarations, 62 new.
- `results/FORMAL_INSTANCES.json`: actual solver returns checked in Lean.
- `results/exact_tests.json`: 12-case exact independent diagnostics.
- `FAILURE_LOG.md`: corrected failures and resource boundaries.
- `MANIFEST_SHA256.txt`: file integrity, not a substitute for compilation.

The focused release includes all 50 inherited active source modules unchanged.
The full v8 continuation additionally preserves the entire v7 archive contents
and prior checked releases, with the old root instructions archived as history.

## Next mathematical boundary

The exact-rational solver-specific convergence gap is closed. The next practical
extension is certified finite-precision or interval-input residual/energy/floor
enclosures, kept distinct from exact rational values. Sequential Gaussian
filtering recursion remains a separate probabilistic extension. Neither is
claimed by this release.
