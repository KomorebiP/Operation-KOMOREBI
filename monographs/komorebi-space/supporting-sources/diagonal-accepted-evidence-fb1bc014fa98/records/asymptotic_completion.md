# Sharp diagonal budget asymptotic: formal completion

Theorem 30.2 is fully proved in `lean/KomorebiSpace/DiagonalAsymptotic.lean` under the pinned Lean 4.34.0-rc2 and mathlib revision. The bundled declaration `KomorebiSpace.DiagonalRegularization.sharp_diagonal_budget_asymptotic` states all four printed conclusions, including the limit over **all real correction budgets**, and the genuine Hilbert-space hard-prefix norm product.

## Exact checked conclusions

- `tendsto_A_div`: A_m/m tends to pi/4.
- `tendsto_mul_B`: m B_m tends to pi/4.
- `tendsto_actual_budget_product`: M beta(T,w,M) tends to pi/4 as real M tends to infinity.
- `tendsto_sqrt_mul_hardPrefix_residual`: sqrt(N) times the actual residual norm tends to one.

The mesh sqrt(A(n+1)) is an internal proof device. The final budget theorem has no subsequence restriction or unproved analytic assumption. The zero parameter is excluded in intermediate algebra by m>=1; all final natural-index limits are ordinary atTop limits. Natural coordinate j denotes positive printed coordinate j+1 throughout.

## Proof route

The formal proof replaces the printed Riemann-sum argument by a shorter exact integral comparison. Both h(x)=1/(1+x^2) and f(x)=h(x)^2 are nonnegative and decreasing on the positive half-line. Their integrals are pi/2 and pi/4. For any such integrable kernel, the infinite right-sample sum divided by m lies between its integral minus k(0)/m and its integral. Exact termwise identities then give the two energy limits.

The actual norm mesh is positive, monotone, divergent, and has consecutive ratio tending to one. `budget_at_sqrt_A` identifies its exact residual value. The independently developed `tendsto_budget_product_of_mesh` transfers the product limit to every real budget. For hard-prefix repair, the actual Hilbert residual square equals the omitted reciprocal-square tail; its lower and upper bounds squeeze the squared product to one.

## Verification and scope

Run 14 compiled with `-DwarningAsError=true` and emitted an olean. It exited 0 with an empty compiler log. All 47 explicit declarations were separately checked with `#print axioms`; every dependency list contains only `propext`, `Classical.choice`, and `Quot.sound`. No sorry, admit, new axiom, or unsafe declaration appears. Exact source, olean, and dependency hashes are in `asymptotic_status.json`; command, exit code, timings, and source-before/source-after hashes are in `asymptotic_runs.json`.

The source is frozen at SHA-256 `6d1cb7c7e068b9e007c0304359db172ee3ecd66bd90fae6a72d23076de0a0c47`. Independent review and release replay are coordinated by the lead agent. The finished parent publication is unchanged.

## Failed attempts and repairs

Initial probes encountered a missing local compiled definition and incomplete local dependency setup. Root completed the pinned environment; the first analytic probes ran from the established mathlib workspace. Subsequent compiler errors were API names, function coercion and composition normalization, and redundant tactics. The first all-budget compile found a missing existing BudgetProfileGeometry olean, fixed by a narrow build without source edits. Final hard-prefix errors were the algebraic normalization of inverse squares and an unexpanded definition; both are now checked. A successful penultimate compile still emitted two informational ring suggestions; replacing those normalizations with ring_nf produced the clean final log.

No mathematical counterexample was found. Raw diagnostic logs and available failed-source snapshots are retained. Attempts 1–8 did not separately capture compiler exit status because their initial wrapper printed the log afterward; no successful status is inferred for those attempts. Structured run evidence starts at run9.
