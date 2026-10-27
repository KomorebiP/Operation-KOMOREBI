# Roundoff-aware posterior solver

**Checked release v0.1.0**

The gain updates themselves now use the specified outward-rounded dyadic
arithmetic graph. A computed state-dependent precision bounds each update's
roundoff. A uniform tracking theorem, a computed local-accuracy policy, and a
finite iteration horizon force successful rounded posterior certification for
every positive rational tolerance under the stated fixed-model assumptions.

## Main formal results

Namespace `Komorebi.RoundoffSolver`:

- `rounded_step_entry_error`: all local arithmetic roundoff is at most 2^(-t)
  per gain entry, using the precision chosen by the executed update.
- `roundedGain_tracking`: uniform squared-Frobenius tracking tube around the
  ideal trajectory, with explicit dependence on the contraction factor.
- `rounded_score_geometric`: ideal geometric progress plus a quantified floor.
- `rounded_iterate_posterior_bound`: the same bound for actual posterior laws.
- `rounded_solver_reaches_posterior_tolerance`: the actual executable solver
  returns and certifies the requested posterior tolerance.
- `rounded_solver_gain_origin`: the returned gain is an actual rounded iterate
  within the computed fuel, not an independently substituted candidate.

The main probability statement is in `Komorebi/RoundedSolverPosterior.lean`.
See `PROOF_NOTE.md` for equations, assumptions, and remaining proof boundaries.

## Run and export a concrete proof

Python 3.10 or newer is required. The producer itself uses only the standard
library; the independent diagnostic suite additionally uses SymPy.

```bash
python checks/rounded_gain_solver.py examples/solver_scalar.json --output results/my_scalar.json --try-precisions 4 12 --emit-lean Komorebi/MyRoundedSolver.lean --namespace MyRoundedSolver
```

A `PASS_ROUNDED_SOLVER_PROVISIONAL` result is not a formal instance proof until
the exported explicit Lean source compiles. Resource-limited runs cannot export
success proofs. JSON integers and exact fraction/decimal strings are accepted;
raw JSON floating-point numbers are rejected.

The input is H,L,N,sigma,m,y and complete rational projector families, representing
P=L L^T and R=N N^T+sigma I, sigma>0. Priors may be singular. Both example models
and their actual program returns have been kernel-checked.

## Reproduce the checks

Required environment:

- Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
- Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
- One Lean thread, warnings as errors, the preserved portable Mathlib cache.

```bash
python verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --timeout 120 --clean
python checks/negative_controls.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
python checks/test_roundoff_solver.py
python checks/seal.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The verifier runs every module in a separate process and records its exact source,
log, compiled output and direct dependencies. `MODULE_ORDER.json` provides the
active dependency order. In a tool environment with short outer time limits,
run bounded groups with `--modules`; an interrupted run is not a pass.

After the dependencies are present, an exported instance can be checked with
`--modules MyRoundedSolver`. Adding it to the all-source audit additionally
requires rerunning `checks/build_inventory.py` and compiling the regenerated
`RoundoffSolverAxiomAudit` module. `seal.py` audits receipts and hashes; it does not
itself execute Lean. No official Mathbox manifest-validator run is claimed.

## Deliberate limits

Gain update execution is rounded, but model/step preprocessing, precision budgets,
fuel calculation and terminal comparisons use exact rational arithmetic. Dyadic
fractional precision has unbounded integer parts. The finite-sum node follows the
explicit retained ball semantics, not unspecified hardware reduction order.

There is no IEEE-754/BLAS/overflow guarantee, uncertain-measurement theorem,
verified external parser/exporter, certified rounded posterior-output arrays or
sampling implementation, model-changing adaptation, sequential filtering,
performance superiority, or literature-priority claim.

The exact ideal trajectory appears in the proof but is not executed to obtain
the solver's gains. For the scalar test the returned rounded gain differs from
the corresponding exact Richardson gain; this is itself kernel-checked.

## Evidence

`FINAL_VERIFICATION_RECEIPT.json` records actual fresh checks, failed attempts and
scope. `AXIOM_AUDIT.json` covers all active theorem/lemma declarations.
`results/ROUNDOFF_DIAGNOSTICS.json` records twelve constructed exact matrix tests;
these bounded tests are not a universal theorem or a performance benchmark.
`FAILURE_LOG.md` distinguishes corrected proof drafts from execution interruptions.
