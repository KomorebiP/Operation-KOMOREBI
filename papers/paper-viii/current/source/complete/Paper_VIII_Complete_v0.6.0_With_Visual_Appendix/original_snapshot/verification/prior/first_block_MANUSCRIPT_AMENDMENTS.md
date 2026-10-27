# Paper VIII: Statement Amendments and Boundaries

Author: Komorebi P.

## Required clarification for Theorem 8.4

The strengthened source states positive sensitivities and positive costs, and optimizes over strictly positive tolerances subject to a weighted equality budget. It does not explicitly require a strictly positive total budget.

For a nonempty finite edge set, add **tau > 0**. State nonemptiness explicitly, or treat the empty index set separately. Positive costs then ensure the denominator sum of costs is positive. Without the positive-budget hypothesis, the claimed positive minimizer need not even be feasible.

`positive_allocation_budget` proves that a finite nonempty sum of positive sensitivity-times-tolerance terms is positive. `no_positive_allocation_nonpositive_budget` proves that the feasible set is empty at every nonpositive budget. `one_edge_zero_budget_infeasible` specializes this to one unit-sensitivity edge and budget zero.

These are Lean-checked necessity and infeasibility statements. They do not yet prove the optimality or uniqueness of the corrected allocation formula. Theorem 8.4 remains boundary-audit-only in the coverage ledger.

## Support is an inclusion, not equality

This is already correct in the source. The additional exact rational matrix example A = [[1,1],[-1,-1]] has A^2 = 0 while a length-two active path from packet zero to itself exists. The example is checked in Lean and guards against an invalid strengthening of the graph-support statements.

## Path terminology

`TransferPath` permits repeated vertices. It is a directed walk of the indicated length, the notion required for powers of a matrix. The source uses the word path in this algebraic sense. For acyclic support graphs this distinction disappears.

## Norm and hypothesis conventions

The inverse-norm bound uses the Hilbert-space L2 operator norm, not the entrywise maximum norm. Rectangular factors have their corresponding operator norms. The adjoint identity requires self-adjoint projectors explicitly. Woodbury requires invertibility of both the diagonal matrix and the small correction core. Update invertibility is derived rather than assumed.

The packet perturbation theorem uses continuous linear maps and their operator norm. Only error support is needed for its proof. The formal statement therefore drops the unnecessary exact-block support assumption while retaining the source conclusion. It is not a floating-point rounding theorem or a correctness proof for a particular kernel.

## Preserved edition

The original manuscript PDF, TeX, bibliography, and source package are unchanged. This note and the supplement carry the amendment and formalization status. The source's historical numerical verification and benchmark claims remain identifiable as historical claims. A separate fresh CPU numerical-suite report is supplied. No GPU timing measurements were rerun.
