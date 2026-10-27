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

## Fourth-block formal conventions

Items 4.3 and 4.4 use positive transform/order size. Item 4.3 uses the negative-exponential unitary Fourier convention and derives both unitarity identities. Item 4.5 uses column-major vectorization and an ordinary transpose, not a conjugate transpose. Items 4.6 and 4.7 separate exact mathematical action from declared scalar-operation models. The tensor count assumes reuse of intermediate slices; no claim is made that an arbitrary evaluator of the functional action has this cost.

Item 8.5 uses positive sensitivities, costs, and caps and a nonempty finite edge set, with 0 < budget <= sum(s_e*m_e). The clipped vector is globally uniquely optimal. Existence of a positive multiplier is proved rather than assumed. Its uniqueness is proved for strictly submaximal budget. At maximal budget the vector is still unique although the multiplier need not be. This preserves the manuscript's endpoint distinction rather than reporting a new contradiction.

These conventions are recorded in the fourth supplement and the coverage ledger. The original manuscript remains unchanged.

## Fifth-block conventions and checked scope

Item 4.1 uses `w < p`. For the original `p = n/b` notation, use positive block width and `n = p*b`; the address-cardinality theorem does not justify division by zero. Arithmetic counts are finite multiply/accumulate event models, not observed hardware instructions.

Items 6.6 and 10.3 use nonempty task graphs for the phrase “one plus longest edge-path length.” The empty graph has zero tasks and depth zero. Scheduling assumes unit task costs, positive integer stages and unlimited concurrency. Levels and the staged triangular solve in item 6.5 are constructed rather than supplied as correctness hypotheses.

Items 6.7 and 6.8 use reflexive reachability, including a zero-length path within the same packet. This is already implicit in the manuscript's reachable set including its source. Support inclusion does not imply that every permitted block is nonzero.

Item 9.2 uses actual arbitrary orthogonal projector families. The squared Frobenius identity and operator-norm inequality use their corresponding distinct norm instances. It is a certificate for a supplied decomposition, not a theorem of autonomous projector discovery.

Items 7.4 and 7.6 use a nonempty finite coordinate space, positive definite D and D+K, and the actual inverse square root. The bound on the normalized perturbation has eta < 1; eta >= 0 is derived from the norm bound. Item 7.6 is the checked factor comparison and substitution into the explicitly assumed classical convergence estimate. Classical input 7.5 itself remains external and unformalized here.

These conventions and proof scopes are in the fifth supplement. The original manuscript is preserved rather than silently rewritten.
