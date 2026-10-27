# Certified posterior parameter output

This release adds dyadic interval arrays to the v11 rounded posterior solver.
For positive distribution tolerance epsilon and output radius delta, valid exact
factor-coded data, and fixed complete self-adjoint packet families, the Lean
program returns a gain certificate and mean/covariance intervals whose radii are
at most delta. The enclosed parameters belong to exactly the Joseph Gaussian
covered by the posterior Wasserstein guarantee.

The interval centers do not define a separately certified Gaussian. A checked
singular-covariance counterexample shows why that distinction is necessary.
Read PROOF_NOTE.md for the exact contract and SELF_REVIEW.md for the audit scope.
FINAL_VERIFICATION_RECEIPT.json records the completed checks.

## Run

Python 3.10+; standard library only for both the producer and its exact diagnostics.
From this directory:

```bash
python3 checks/posterior_output.py examples/solver_scalar.json --output results/my_output.json --output-radius 1/1000 --try-precisions 4 12 --emit-lean Komorebi/MyOutput.lean --namespace MyOutput
```

`PASS_OUTPUT_PROVISIONAL` means a Python execution succeeded. Compile its exported
Lean instance before calling that execution formally certified. The exporter emits
explicit model/gain data, checks exact reported centers and radii, and proves the
actual combined program return. Parsing and exporter fidelity are not universal
formal guarantees. Exact fractions or decimal strings are accepted; raw JSON
floating-point numbers are rejected by the retained input parser.

The producer retains dimension cap 8, fractional precision cap 512, and solver
resource limits. `RESOURCE_LIMIT` is a failure to produce the requested complete
output; it cannot export a success proof. Model preprocessing, budgets and final
comparisons remain exact rational arithmetic. There is no IEEE-754, overflow,
BLAS, machine-word, sampling or hardware-runtime theorem.

## Rebuild

Use the preserved portable runtime: Lean 4.34.0-rc2, commit
6a10ac8c22beadecabdbb0919c2b50214762f91d; mathlib
aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Runtime metadata is supplied, but the large
runtime binaries are separate from this source release. The continuation retains
its restoration metadata and the original runtime parts remain separately saved.

```bash
python3 verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --timeout 90 --clean
python3 checks/negative_controls.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 checks/seal.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Every module uses one Lean thread and warnings as errors. `--modules` can select
bounded groups in MODULE_ORDER.json dependency order. If adding exported examples,
regenerate the inventory with `python3 checks/build_inventory.py`, compile new
modules and OutputAxiomAudit, then rerun the seal. The seal compares successful
source, attempted-source, log, compiled output and direct-dependency hashes; it is
not itself a Lean invocation. Pinned mathlib caches are reused.

`computations/output-003` is the final bounded diagnostic run. Its manifest records
source hashes, actual execution and six exact test cases. The earlier run is
preserved as history. `checks/test_posterior_output.py results/local_diagnostics.json`
reruns the deterministic numerical checks without external packages.

## Main declarations

- PosteriorOutput.evaluate_encloses and evaluate_grid
- PosteriorOutput.evaluate_radii_le and represent_spec
- PosteriorOutput.approximation_eq_output_gaussian
- PosteriorOutput.outputCovariance_posSemidef and represented_real_errors
- PosteriorOutput.run_terminates and run_sound
- PosteriorOutput.Boundary.centers_not_posSemidef

All names have the prefix Komorebi. Counts include support lemmas and concrete
regressions and are not counts of independent discoveries.

Larger remaining goals: a separately certified point-valued output or executable
sampler, actual packet-selective adaptation, sequential filtering, uncertain
inputs, parser refinement, and credible performance/literature comparison.
