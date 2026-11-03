# SF-LEAN-B04: analytic uniqueness and the reverse series bridge

Base: `b479654cc33423e56e3dd81cd1f63f9e19efcf84`, checkpoint SF-LEAN-B03.
Keep Lean 4.34.0-rc2 and Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

Target: prove uniqueness of normalized analytic solution germs of the two
coupled equations, then uniqueness among normalized entire pairs. Identify
any such analytic germ with the already constructed coefficient sums, yielding
their canonical convergent odd-series representation without assuming parity.
For positive real scales strictly below one, combine this with Block03's
existence and Block01's positive coefficient recurrence to cover Appendix F.1.

The canonical coefficient `u_n` multiplies `z^(2*n+1)`; it is not an EGF
coefficient. Entire solutions must satisfy actual `HasDerivAt` equations,
not just equalities involving the totalized `deriv` operator. A germ result
requires analyticity at zero and equations in a neighborhood of zero; it
does not assert equality away from that neighborhood without global analyticity.

Three routes:

1. Extract dense Taylor coefficients using derivative, product and linear
   composition APIs. This directly exposes a recurrence but requires
   sparse/dense bookkeeping and coefficient normalizations.
2. Compare orders of vanishing of differences. If both differences vanish to
   order at least `n`, their derivative equations imply order at least `n`
   for their derivatives, hence order at least `n+1` for the differences.
   Induction gives infinite order and equality of germs. The analytic identity
   theorem gives entire uniqueness. This identifies arbitrary solution germs
   with the known coefficient sums and provides a reverse series bridge.
3. Use local uniform norm bounds and a small-disk contraction argument for
   differences. This needs compact maxima and a quantitative mean-value bound.

Route 2 is selected first. Its decisive checks are preservation of vanishing
order by scaling, including a zero scale, and the derivative-order increment
at a zero. Germ uniqueness should work conditionally for arbitrary real
scales; strict positive contraction is needed for the canonical entire
existence theorem being compared to.

A canonical `HasSum` representation is part of the target. An API identifying
every coefficient of an arbitrary supplied Mathlib multilinear Taylor series
is separate packaging unless explicitly proved; do not label that transport
complete merely from the function-identification theorem.

Keep all earlier blocks and their guides unchanged. Admit results only after
warning-as-error compilation, exact theorem/axiom audit, kernel replay and
positive/negative controls. Record the remaining inverse/growth obligations
separately from Appendix F.1.
