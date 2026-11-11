# Explicit inverse CDF: self-review

**Claim reviewed.** For `0 ≤ ρ < 1` and `0 ≤ u ≤ 1`, the real
piecewise arctangent formula in `SmithExplicitInverse.explicitQuantile` lies
in `[0,2π]` and its integral-defined CDF equals `u`. It equals the unique
noncomputable inverse, with exact values `π/2` and `3π/2` at masses `1/4`
and `3/4`.

**Dependencies.** The principal branch follows from the derivatives of
tangent and arctangent and the integral CDF's derivative, agreeing at zero.
The density has period `π`; normalization and reflection symmetry give the
half-turn shift and quarter-turn CDF values. Shifted principal branches
cover the middle and final intervals; the two branch points are handled
separately. Strict monotonicity identifies the formula with the abstract
inverse. A separate Lean statement checks that at `ρ=0` the formula reduces
to `2πu` throughout `[0,1]`.

**Boundaries.** The theorem includes `ρ=0`, `u=0`, `u=1`, and both branch
points; it excludes `ρ=1` and masses outside `[0,1]`. It proves a real
piecewise arctangent formula. It does not establish equivalence to the
browser's complex Möbius/atan2 lift or prove IEEE-754 behavior, and it does
not establish reconstruction or RF-performance optimality.

**Verdict.** The stated mathematical formula is proved under its displayed
hypotheses when the companion replay succeeds. The source mapping and
edge-case review are self-review, not independent review. The replay records
the axioms used and reuses pinned precompiled Mathlib objects.
