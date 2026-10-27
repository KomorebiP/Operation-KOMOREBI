# Paper VIII statement amendments and model clarifications

**Author: Komorebi P.**

## Current amendment: item 8.4 is now proved under a positive budget

For a finite nonempty edge set, assume every sensitivity s_e and cost c_e is strictly positive and explicitly assume budget > 0. The formula budget*c_e/(s_e*sum c) is then feasible and is the unique global minimizer of sum c_e log(1/eps_e) over positive eps with sum s_e eps_e = budget. ContinuousPrecision.lean proves the complete amended statement, not only stationarity.

The first block's proof that nonpositive budget is infeasible remains unchanged in BoundaryChecks.lean. The original PDF and TeX are not silently edited. The amendment is stated in this ledger and the second supplement.

## Explicit model hypotheses

Roofline time divisions use positive operation and bandwidth capacities. The rate form also uses positive elapsed time and positive byte traffic. The square-root memory threshold uses nonnegative n and available capacity, with strictly positive scalar size. Reduction factors use nonzero denominators. Theorems remain available for zero-size storage and operation counts without forming undefined physical ratios.

Counts charge two scalar operations per coefficient per right-hand side. The final thin BDLR product is interpreted as accumulating into the diagonal result. Index metadata, temporary workspace, launch overhead, discovery, transfer, and materialization remain distinct modeled costs. Explicit materialization has a concrete 2*n^2*r+n^2 event count for the declared implementation, with quadratic remainder bounded by n^2.

The compiler stability hypothesis constrains changes in solved keep/split scores. Changes in raw local costs alone need not satisfy it. At an exact tie, the strict half-gap condition is impossible, so no tie robustness is claimed.

The cached update uses correct old sibling caches. It does not assume the desired new root optimum. Replacement of one subtree encodes changes to local data confined to that subtree, while ancestors and siblings retain their declared local models.
