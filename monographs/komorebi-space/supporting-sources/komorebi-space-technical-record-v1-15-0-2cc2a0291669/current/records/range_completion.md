# Concrete diagonal range completion

The actual infinite diagonal operator now has a compiled nonclosed-range theorem. The same source also covers the printed closure-without-attainability example.

## Accepted result

`KomorebiSpace/DiagonalRangeObstruction.lean` adds one definition and 12 theorems. The main endpoints are `T_not_closed_range` and `w_mem_closure_not_range` in `KomorebiSpace.DiagonalRegularization`.

The proof uses actual unit coordinate vectors in the existing real `lp` exponent-two space. Their norms are one and their image norms are exactly `1/(j+1)`. Injectivity supplies the orthogonality condition for the previously compiled general obstruction theorem. Separately, actual finite-prefix images converge to `w`, while every putative exact preimage would be the constant-one sequence and would fail square summability.

All 12 theorems passed Lean with one thread, automatic implicit variables disabled, and warnings treated as errors. All 13 new declarations have exactly the standard dependencies `propext`, `Classical.choice`, and `Quot.sound`. There are no new axioms or admitted proofs.

## Failures retained

The initial shell invocation used paths relative to the wrong working directory and created no source. The first source compile exposed a dependent `lp.single` inference issue and a wrong orthogonal-complement API name. The next compile rejected an unused simp argument under warnings-as-errors. Those were corrected, and the required result passed. An optional API exploration queried one nonexistent identifier. The first optional closure proof needed an explicit unfolding of function composition before square-root simplification. The complete source then passed. The first axiom audit was invoked outside the Lean project and could not resolve imports; the identical audit source passed when run from the correct directory. Snapshots and original logs are retained and hashed in `range_completion.json`.

## Scope boundary and restart

This completes the concrete infinite diagonal paragraph, including hard-prefix convergence and nonattainability. It does not claim that the separate protected product-space construction is now formalized. Root integration, independent statement review, global replay, and publication changes remain the parent task's responsibility. No inherited source or import root was modified by this task.
