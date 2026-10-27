# Focused regularized protected repair

This extension is deliberately separate from the unchanged canonical `formal/` tree. It adds three production modules and an entrypoint. Its complete local import closure has three inherited modules and the root, for seven source compilation targets. The accepted replay is identified by `../audit/extension/release.json`; inspect that receipt before treating a build as verified.

## Mathematical content

`RegularizedHilbertRepair.lean` constructs the optimizer for a positive quadratic regularization parameter in real Hilbert spaces. Coercivity supplies an actual continuous inverse, not a hypothesis asserting invertibility. The source proves the energy identity, unique global minimality, parameter comparisons, budget optimality, normal-residual bounds, and fixed-parameter data bounds.

`RegularizationCertificates.lean` proves the exact two-square primal/dual gap, attained duality, global error certificates, and the normalized support witness at the optimizer's own budget.

`ProtectedRegularizedRepair.lean` uses the existing `ProtectedHilbertRepair.restricted` operator on the actual protected kernel. It retains the projected adjoint, exact protection, and the distinction between measured fit and the model residual of the repaired candidate.

## Reproduction

From the package root, with the supplied pinned portable runtime available separately:

```sh
python3 extension/scripts/verify.py --runtime /path/to/portable-runtime --label independent-focused1
```

The verifier refuses to overwrite a run. It checks Lean and nine dependency revisions, recompiles the seven targets into an empty local build, exports the actual imported declarations and axiom dependencies, and runs positive, compiler-negative, and policy-negative controls. The runtime's imported mathlib caches are reused, not rebuilt. No runtime or disposable `.work` output is distributed.

The source-copy workspace is `extension/.work/<label>`. The immutable execution evidence goes to `audit/extension/<label>`. A failed or interrupted attempt must not be bound as accepted evidence. `checks/verify_focused_evidence.py` verifies the current accepted source/log/receipt hashes but does not run Lean.

## Scope

The focused replay is not a fresh cumulative build of all 138 canonical production modules. The earlier cumulative evidence remains historical and source-bound. The attempted `baseline16` cumulative run was explicitly stopped and remains INTERRUPTED.

Full focused WR counterparts: WR06, WR07, WR13, WR14. Partial focused coverage: WR09 and WR16 pointwise inequalities only. WR01–WR05, WR08, WR10–WR12, and WR15 remain written-only. In particular, the general weak compactness, budget-attainment, regularization-limit, diagonal-asymptotic, and coordinate-basis results are not newly formalized.

Source correspondence is an editorial relation, not an automatic translation of prose. Exact Python tests are not a universal refinement proof. The official kernel/compiler, standard axioms, and pinned imported dependencies remain trusted.
