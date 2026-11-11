# Sampling integral and partition: self-review

**Claim reviewed.** For every real `0 ≤ ρ < 1`, the chart density

```
pρ(θ) = (1 - ρ⁴) / (2π (1 - 2ρ² cos(2θ) + ρ⁴))
```

is positive and continuous, integrates to one on `[0,2π]`, and defines a
continuous, strictly increasing integral CDF. Every mass in `[0,1]` has a
unique preimage, and a noncomputable inverse is strictly increasing and
inverts the CDF in both directions on the stated intervals. For every natural
`N > 0`, there are `N+1` strictly ordered endpoints from zero to `2π` whose consecutive
intervals each have density integral `1/N`.

**Dependencies.** `SmithSamplingIntegral.lean` applies Mathlib's Poisson
integral formula to the constant complex function on the unit disk, translates
the kernel to the real trigonometric expression, and uses periodicity and a
change of variables for the doubled angle. The fundamental theorem of
calculus gives the CDF derivative; positivity gives strict monotonicity. The
intermediate value theorem and classical choice construct the endpoints and
the abstract inverse; interval-integral additivity gives their masses. The Mathlib revision and
compiler are pinned in the companion replay.

**Checks and boundaries.** The theorem includes `ρ=0` and `N=1`; separate
Lean statements identify the zero-radius uniform density and CDF. `N=0` and
the unit boundary `ρ=1` are excluded. The formal inverse is noncomputable;
the browser's branch-aware formula is not proved equal to it. The
previous minimax statement bounds integrated coordinate-speed masses; it does
not establish optimal reconstruction or measured RF performance.

**Verdict.** The stated result is proved under its displayed hypotheses when
the companion replay succeeds. This mapping and edge-case audit are
self-review, not independent review. The replay records theorem axioms and
uses precompiled Mathlib objects rather than rebuilding every dependency.
