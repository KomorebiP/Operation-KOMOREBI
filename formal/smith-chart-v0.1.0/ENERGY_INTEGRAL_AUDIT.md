# Finite-radius angular energy: self-review

**Claim reviewed.** For `0 ≤ ρ < 1` and `N > 0`, the angular mean-square
of the actual impedance packet at `t = ρ exp(iθ)` equals its proved sum of
squared coefficients. The zero lane has value
`1 + 4ρ^(2N)/(1-ρ^(2N))`; each nonzero lane `j` has value
`4ρ^(2j)/(1-ρ^(2N))`.

**Dependencies.** `SmithEnergyIntegral.lean` applies the normalized Poisson
kernel over an arbitrary positive integer number of periods. It proves the
pointwise squared norms of the rational zero and nonzero packet formulas,
integrates them, then invokes `SmithChart.packet_zero` and `packet_nonzero`
to identify the rational formulas with the convergent series. Finally it
compares the results to `SmithEnergy`'s independently proved coefficient sums.
The Mathlib and compiler identities are pinned by the companion replay.

**Checks and boundaries.** The statements include `ρ=0` and `N=1`. The
nonzero theorem requires `j ≠ 0`; canonical lanes also satisfy `j < N`. The
unit boundary is excluded, and no finite boundary H² norm or Lean proof of
divergence at the boundary is claimed. The uniform-convergence derivation in
`ENERGY_DERIVATION.md` is an alternative self-reviewed argument, not the
formal proof route.

**Verdict.** The displayed finite-radius identities are proved when the
companion replay succeeds. This mapping and edge-case audit are self-review,
not independent review. The replay records theorem axioms and uses cached
Mathlib objects rather than rebuilding every transitive dependency.
