/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedZeroOrbits
import KomorebiPaperIV.SignedZeroCorrection

namespace Komorebi.PaperIV
noncomputable section
open Metric

/-- The exact nonvanishing factor used in the two-term normalization. -/
def signedNormalizationFactor (N : ℕ) (z : ℂ) : ℂ :=
  (N : ℂ) * Complex.exp (-(canonicalSignedVertex N (N - 1) * z))

theorem signedNormalizationFactor_ne_zero {N : ℕ} (hN : 0 < N) (z : ℂ) :
    signedNormalizationFactor N z ≠ 0 :=
  mul_ne_zero (by exact_mod_cast hN.ne') (Complex.exp_ne_zero _)

/-- At a denominator zero, the product-rule term containing the denominator
vanishes, leaving the actual derivative of the original entire function. -/
theorem canonicalSignedDenominator_derivative_normalization {N : ℕ} (hN : 3 ≤ N)
    {z : ℂ} (hz : canonicalSignedDenominator N z = 0) :
    signedNormalizationFactor N z * deriv (canonicalSignedDenominator N) z =
      signedZeroFrequency N * Complex.exp (signedZeroFrequency N * z) +
        signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 1 z := by
  let R := signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0
  let G := fun w : ℂ => 1 + Complex.exp (signedZeroFrequency N * w) + R w
  have hP : AnalyticAt ℂ (signedNormalizationFactor N) z := by
    unfold signedNormalizationFactor; fun_prop
  have hD : AnalyticAt ℂ (canonicalSignedDenominator N) z := analyticAt_entireSigned _ _ _ _ _
  have hp := hP.differentiableAt.hasDerivAt.mul hD.differentiableAt.hasDerivAt
  have hR : HasDerivAt R
      (signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 1 z) z :=
    hasDerivAt_finiteExponentialRemainder _ _ _ 0 z
  have hg := hasDerivAt_perturbed_exponential (signedZeroFrequency N) hR
  have he : (fun w => signedNormalizationFactor N w * canonicalSignedDenominator N w) = G := by
    funext w
    exact signed_two_term_normalization (by omega) _ _ w
  change HasDerivAt (fun w => signedNormalizationFactor N w * canonicalSignedDenominator N w) _ z at hp
  rw [he, hz, mul_zero, zero_add] at hp
  have hh := hp.unique hg
  simpa only [mul_comm] using hh

/-- A relative derivative estimate for the original denominator. Its leading
term is `-a/P(z)`, where `a=2 i sin(pi/N)` and `P` is the exact prefactor. -/
theorem canonicalSignedDenominator_relative_derivative_error {N : ℕ} (hN : 3 ≤ N)
    {t : ℝ} (ht : 1 / ‖signedZeroFrequency N‖ ≤ t) {z : ℂ}
    (hz : z ∈ closedBall (t : ℂ) (1 / ‖signedZeroFrequency N‖))
    (hz0 : canonicalSignedDenominator N z = 0) :
    ‖deriv (canonicalSignedDenominator N) z /
      (-signedZeroFrequency N / signedNormalizationFactor N z) - 1‖ ≤
      ((‖signedZeroFrequency N‖ + 2) / ‖signedZeroFrequency N‖) * signedRemainderEnvelope N t := by
  have ha := signedZeroFrequency_ne_zero (show 2 ≤ N by omega)
  have hP := signedNormalizationFactor_ne_zero (show 0 < N by omega) z
  have hnorm := canonicalSignedDenominator_derivative_normalization hN hz0
  have hb := canonicalSignedDenominator_normalized_derivative_error hN ht hz hz0
  have he : deriv (canonicalSignedDenominator N) z /
      (-signedZeroFrequency N / signedNormalizationFactor N z) - 1 =
      -((signedZeroFrequency N * Complex.exp (signedZeroFrequency N * z) +
        signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 1 z) +
          signedZeroFrequency N) / signedZeroFrequency N := by
    rw [← hnorm]
    field_simp
    ring
  rw [he, norm_div, norm_neg]
  calc
    _ ≤ ((‖signedZeroFrequency N‖ + 2) * signedRemainderEnvelope N t) /
        ‖signedZeroFrequency N‖ := div_le_div_of_nonneg_right hb (norm_nonneg _)
    _ = _ := by ring

/-- At a real point the leading derivative modulus is exactly the manuscript's
`(2 sin(pi/N)/N) exp(cos(pi/N) t)` scale. -/
theorem signed_derivative_leading_norm {N : ℕ} (hN : 3 ≤ N) (t : ℝ) :
    ‖-signedZeroFrequency N / signedNormalizationFactor N (t : ℂ)‖ =
      (2 * Real.sin (Real.pi / N) / N) * Real.exp (Real.cos (Real.pi / N) * t) := by
  have hn : (N : ℝ) ≠ 0 := by exact_mod_cast (show N ≠ 0 by omega)
  rw [norm_div, norm_neg, signedZeroFrequency_norm (by omega)]
  unfold signedNormalizationFactor
  rw [norm_mul, Complex.norm_natCast, Complex.norm_exp, Complex.neg_re, Complex.mul_re,
    Complex.ofReal_re, Complex.ofReal_im, mul_zero, sub_zero,
    canonicalSignedVertex_last_re (by omega), Real.exp_neg]
  field_simp

/-- The relative estimate also controls the modulus of the actual derivative. -/
theorem canonicalSignedDenominator_derivative_modulus_error {N : ℕ} (hN : 3 ≤ N)
    {t x : ℝ} (ht : 1 / ‖signedZeroFrequency N‖ ≤ t)
    (hx : (x : ℂ) ∈ closedBall (t : ℂ) (1 / ‖signedZeroFrequency N‖))
    (hx0 : canonicalSignedDenominator N (x : ℂ) = 0) :
    |‖deriv (canonicalSignedDenominator N) (x : ℂ)‖ /
        ((2 * Real.sin (Real.pi / N) / N) * Real.exp (Real.cos (Real.pi / N) * x)) - 1| ≤
      ((‖signedZeroFrequency N‖ + 2) / ‖signedZeroFrequency N‖) * signedRemainderEnvelope N t := by
  have hb := canonicalSignedDenominator_relative_derivative_error hN ht hx hx0
  have hh := abs_norm_sub_norm_le
    (deriv (canonicalSignedDenominator N) (x : ℂ) /
      (-signedZeroFrequency N / signedNormalizationFactor N (x : ℂ))) (1 : ℂ)
  rw [norm_div, norm_one, signed_derivative_leading_norm hN] at hh
  exact hh.trans hb

end
end Komorebi.PaperIV
