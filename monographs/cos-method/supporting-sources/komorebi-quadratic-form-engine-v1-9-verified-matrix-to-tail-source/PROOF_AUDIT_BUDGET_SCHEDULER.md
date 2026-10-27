# Proof audit: budget-optimal phase scheduler

Date: 2026-09-23

## Claim 1: edge-additive leakage majorant

**Statement.** For a nonnegative transfer matrix `B`, nonnegative start profile
`rho0`, and a retained matrix `B_O <= B` obtained by zeroing symmetric phase
pairs,

`(B^k - B_O^k) rho0 <= sum_{e in O} q_e^(k)` componentwise,

where

`q_e^(k) = sum_{j=0}^{k-1} B^(k-1-j) Delta_e B^j rho0`.

**Audit.** Passed.

- The exact noncommutative identity
  `B^k-C^k = sum B^(k-1-j)(B-C)C^j` is used with `C=B_O`.
- Since `0 <= B_O <= B` entrywise and all matrices are nonnegative,
  `B_O^j rho0 <= B^j rho0` follows by monotonicity.
- `B-B_O` is exactly the sum of disjoint pair matrices `Delta_e`.
- No commutativity assumption is used.
- The final scalar certificate uses only the Euclidean triangle inequality.

## Claim 2: cardinality-optimal equal-cost pruning

**Statement.** Under the scalar additive constraint
`sum_{e in O} beta_e <= tau`, omitting the smallest risks until the next risk
would exceed the budget maximizes the number of omitted pairs.

**Audit.** Passed.

For any fixed cardinality `r`, the minimum possible sum of `r` nonnegative
risks is the sum of the `r` smallest risks. Therefore if the prefix of length
`r+1` exceeds the budget, every subset of cardinality `r+1` is infeasible.

The theorem is explicitly limited to the scalar additive surrogate. It does
not assert optimality under the tighter nonlinear transfer envelope.

## Claim 3: exact-envelope refinement

**Statement.** Additional pairs may be omitted while the exact transfer
envelope remains at most `tau`.

**Audit.** Passed as a certificate-preservation statement.

No global optimality is claimed for the greedy refinement order.

## Claim 4: unequal-cost problem is 0-1 knapsack

**Statement.** Maximizing saved communication cost subject to the scalar
additive risk budget is a 0-1 knapsack problem.

**Audit.** Passed by direct identification of binary item variables, item value
`c_e`, item weight `beta_e`, and capacity `tau`.

The supplied ratio-greedy algorithm is a certified heuristic, not an exact
integer-knapsack solver. The fractional relaxation is used only as an upper
bound on saveable cost.

## Claim 5: ideal double-buffer time formula

**Statement.** Under perfect overlap of transfer `b+1` with compute `b`,

`T = t_1 + sum_{b=1}^{B-1} max(c_b,t_{b+1}) + c_B`.

**Audit.** Passed under the explicitly stated ideal pipeline model.

This is not a GPU benchmark and does not include contention, synchronization,
allocator, launch, or library-workspace effects.

## Primary verdict

**Proved as written under the stated nonnegativity and ideal-pipeline
hypotheses.**

The finite computations audit implementations and comparative behavior; they
are not used as proof of the universal theorems.
