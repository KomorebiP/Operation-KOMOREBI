# Mathematical scope review — publication 1.4.0

This is an editorial examination of statements, proofs, examples and their actual source declarations. It is not a new compiler run or a machine-certified prose translation.

## Principal declarations newly developed

- **KS71–KS72:** `Exactification.lean` uses a complete pseudometric candidate space, a real nonnegative lower-semicontinuous residual, vanishing residuals, and a summable movement budget. The manuscript specializes to a metric space. Variable factors are nonnegative, not necessarily below one. Their prefix product tends to zero, and the weighted movement series is summable. The restarted geometric estimate uses the residual at the actual restart index.
- **KS73:** `LinearExactification.lean` requires a complete normed linear candidate space and continuous linear residual and preservation maps. A convergent controlled path supplies an actual allowed correction. The claim is algebraic obstruction zero, not merely zero numerical floor. Completeness of the residual target is not added unnecessarily.
- **KS74:** Path comparison is a metric-space statement about two already convergent paths and a vanishing pairwise distance budget. Residual zero and a shared observable alone do not assert uniqueness. The same-input parametric path family is separately worked out, not claimed to be a new Lean instance.
- **KS75:** `Profiles.lean` requires a nonnegative decreasing scalar profile and a monotone unbounded sampling schedule. Its conclusion is equivalence of vanishing, not equality of rates. The alternating counterexample is retained.
- **KS76–KS77:** `ObstructionFloor.lean` uses a normed additive commutative group and an additive subgroup. Zero distance means closure membership. Closedness is required to replace closure by exact membership. The persistent-floor theorem quantifies over every admissible correction sequence under an eventually uniform positive lower bound. The quotient-seminorm explanation is an additional printed elementary derivation.
- **KS78–KS79:** `WeightedGeometry.lean` starts with an independently specified extended nonnegative arrow cost, zero on identities and subadditive under composition. It proves directed-distance and symmetric-zero-setoid laws. It does not identify zero distance with isomorphism. The free-path example deliberately retains path length as different from cost.
- **KS80:** `ProjectiveExample.lean` proves the additive two-bit phase identities and failure of scalar flattening. Its coefficient group is F2. The real matrix lifts, nonzero-complex-scalar observation, and eight-element group are printed algebraic consequences and finite calculations, not newly compiled declarations. This pair-phase model is not the earlier arrow-cocycle stack.

## Infinite Hilbert example

The state space is ell2 on positive integers plus R with the Hilbert direct-sum norm. The defect d(u,t)_n=(u_n+t)/n and observable p(u,t)=t are bounded linear maps between complete spaces. The raw state is (0,1). Exactness under t=1 requires the nonsquare-summable constant sequence -1. The permitted correction image is the dense proper range of diag(1/n), so the algebraic obstruction is nonzero and its numerical floor is zero.

Finite repairs have correction norm squared N and residual norm squared between 1/(N+1) and 1/N. The latter is an infinite-tail inequality proved by telescoping, not a finite summation extrapolation. The bound ||u|| >= sqrt(N)-N*epsilon proves that every protected sequence with residual tending to zero has correction norm tending to infinity, not merely the displayed iteration. The finite solution sets are singletons and have a coherent ordinary inverse-limit point. That point lies outside the semantic comparison image of the declared Hilbert space. This does not contradict finite-fiber existence.

The whole model is supplied as a complete written derivation. No new Lean instance or proof of historical novelty is claimed. The finite checker verifies prefixes, inequalities on stated rational inputs, and diagonal inverses, not the infinite existence question.

## Figure and computation scope

All plotted quantities are explicit formulas or certified bounds. The escape band is not an evaluated infinite tail. Path limits at omitted infinite time are open endpoint markers justified by the printed formula. The directed graph's labels are associated to oriented generators in the source; the distance table is independently checked by two finite algorithms. Exhaustive finite group checks apply only to the stated eight-element model. Infinite theorems remain supported by proofs.
