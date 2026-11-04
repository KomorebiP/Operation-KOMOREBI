import KCosCertification

set_option autoImplicit false
open KCosCertification KomorebiQCOS

-- Expected type error: a lower bound for the error cannot be used as its
-- directed upper bound in the acceptance implication.
example {p estimate lower upper ratioUpper toleranceLower tolerance : ℝ}
    (hp : 0 < p) (he : Enclosed (decimalLog p) lower upper)
    (hx : Enclosed estimate (decimalExp lower) (decimalExp upper))
    (hr : ratioUpper ≤ logWidthRatio lower upper)
    (ht : toleranceLower ≤ tolerance) (ha : ratioUpper ≤ toleranceLower) :
    |estimate - p| / p ≤ tolerance := by
  exact directed_log_acceptance hp he hx hr ht ha
