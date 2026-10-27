# Route index for Euler-Bernoulli-structure-20261005

The live entry point is [README.md](README.md); the mathematical synthesis
is [SYNTHESIS.md](SYNTHESIS.md). The parent radix program remains intact in
the included parent archive. No older proof or failed attempt is overwritten.

| Route | New result and exact limit | Evidence |
|---|---|---|
| Prescribed Bernoulli determinants | Proved all dyadic steps for depleted D; proved actual unit-step transfer in its stated range. No implication from determinant nonzero to Euler simplicity. | [Unit-step and actual transfer](nonintersection/BERNOULLI_HANKEL_SEPARATION.md), [all-step proof](hankel_bridge/ALL_STEP_HANKEL_AND_RESIDUAL_BRIDGE.md), [independent audit](review/HANKEL_REVIEW.md) |
| Contact-to-norm bridge | Exact linear pairing derived. Literal scalar-square kernel identity ruled out on the actual chart. Alternate weights or determinant identities remain unconstructed. | [Bridge and obstruction](hankel_bridge/ALL_STEP_HANKEL_AND_RESIDUAL_BRIDGE.md) |
| Low-degree norm argument | Proved anisotropy through degree three and isotropy in degree four, including scoped actual-moment versions. No low-degree representation of the stationary scalar supplied. | [Proof](root/BERNOULLI_QUADRATIC_FORM.md), [audit](review/QUADRATIC_FORM_REVIEW.md) |
| Recurrence and neighboring cutoff | Proved constrained scaling jets and exact contiguous identity. Neighbor contact measures the same critical scalar; it does not independently bound it. | [Proof](recurrence/CONSTRAINED_TANGENT_AND_CONTIGUOUS_CONTACT.md), [audit](recurrence/INDEPENDENT_REVIEW.md) |
| Structured Padé and carry reset | Global naive height comparison fails; unadapted rank one fails convergence and rank two misses the cancellation. Carry-adapted models repair convergence, prove all-rank denominator control in the carry range, and give exact finite-rank stationary errors. | [Initial attempts](separation/STRUCTURED_BERNOULLI_PADE.md), [carry continuation](separation/carry_adapted/CARRY_ADAPTED_SEPARATION.md), [audit](review/PADE_REVIEW.md) |
| Shifted finite Jacobi model | Proved stable model moments, all-index error and stationary transfer when L>=9. The strict arithmetic separation remains open. | [Proof](nonintersection/jacobi_height/SAFE_JACOBI_AND_HEIGHT_BOUNDARY.md), [audit](review/JACOBI_HEIGHT_REVIEW.md) |
| Conditioning versus height | U-basis conditioning does not remove the Z-degree term in the existing height estimate. Actual dyadic unit moments can already have height beyond the undepletion scale. | [Height analysis](nonintersection/jacobi_height/SAFE_JACOBI_AND_HEIGHT_BOUNDARY.md) |

## Precisely closed constructions

- The literal scalar-square identity for this actual residual kernel is
  false; it cannot be reopened by changing only the proof wording.
- Nonsingular moment matrices do not imply anisotropy in arbitrary degree;
  the actual degree-four construction disproves that shortcut.
- The unadapted first shifted Padé source series is not convergent on the
  whole chart. The second converges but has a large exact model error.
  The carry reset is a materially different construction and has been executed.
- Tangent nonzero and adjacent contact nonzero cannot be inferred from
  the displayed identities alone. A new actual arithmetic input is needed.
- Reexpressing the old rational approximation in an orthogonal moment basis
  does not lower its reduced height or its degree in the critical variable.

## Open continuations and resumption conditions

The parent Euler goal is open. These are deferred mathematical obligations,
not claims that every possible proof method has been exhausted.

1. **Carry-model arithmetic separation.** Establish a prescribed-coefficient
   expression forcing a model critical valuation away from its exact error
   valuation. The cheapest meaningful new test is a symbolic identity or
   valuation inequality; more T digits merely repeat the known cancellation.
2. **Safe Jacobi critical scalar.** Find a reduced-height or valuation bound
   for its analytic stationary value. Matrix entries being rational is not
   evidence that this value is rational. Resume with an actual scalar formula
   or a new approximation whose reduced height can be bounded below precision.
3. **Different contact identity.** An alternate weighted determinant or
   degree-at-most-three norm could use the new nondegeneracy theorem, but
   requires an exact map from both G and its ordinary derivative, retaining
   the finite cutoff and every normalization. No candidate identity has been
   left partly proved in this checkpoint.
4. **Other Bernoulli-specific exclusion.** A genuinely new arithmetic
   invariant could bypass these sufficient routes. Existing recurrence,
   tangent, and radix identities are archived with their precise limits.

The already fixed indices with critical valuations 0, 30, and 91 remain
nonzero. They are finite evidence and controls, not coverage of all ordinary
indices. Higher-address obligations remain in the parent target.
