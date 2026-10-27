/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedZeroLocalization

/-! # Quantified leading correction for the actual signed zero strings -/

namespace Komorebi.PaperIV
noncomputable section
open Metric

/-- The explicit coefficient in the exponential remainder envelope. -/
def signedRemainderScale (N : ℕ) : ℝ :=
  ((N - 2 : ℕ) : ℝ) * Real.exp (signedPolygonGap N * (1 / ‖signedZeroFrequency N‖) +
    2 * (1 / ‖signedZeroFrequency N‖))

def signedRemainderEnvelope (N : ℕ) (t : ℝ) : ℝ :=
  signedRemainderScale N * Real.exp (-signedPolygonGap N * t)

theorem signedRemainderEnvelope_pos {N : ℕ} (hN : 3 ≤ N) (t : ℝ) :
    0 < signedRemainderEnvelope N t := by
  unfold signedRemainderEnvelope signedRemainderScale
  have hn : 0 < N - 2 := by omega
  positivity

theorem signedRemainderEnvelope_bounds {N : ℕ} (hN : 3 ≤ N) {t : ℝ}
    (ht : 1 / ‖signedZeroFrequency N‖ ≤ t) {z : ℂ}
    (hz : z ∈ closedBall (t : ℂ) (1 / ‖signedZeroFrequency N‖)) (q : ℕ) :
    ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) q z‖ ≤
      2 ^ q * signedRemainderEnvelope N t := by
  have h := canonicalSignedRemainder_disk_bound hN ht hz q
  unfold signedRemainderEnvelope signedRemainderScale
  convert h using 1
  ring

/-- The error after subtracting the actual leading correction is quadratic
in the exponentially decaying remainder envelope. -/
theorem canonicalSignedDenominator_first_correction {N : ℕ} (hN : 3 ≤ N)
    {t : ℝ} (ht : 1 / ‖signedZeroFrequency N‖ ≤ t)
    (hc : Complex.exp (signedZeroFrequency N * (t : ℂ)) = -1)
    (hsmall : signedRemainderEnvelope N t ≤ 1 / 2)
    {z : ℂ} (hz : z ∈ closedBall (t : ℂ) (1 / ‖signedZeroFrequency N‖))
    (hz0 : canonicalSignedDenominator N z = 0) :
    ‖z - (t : ℂ) -
      signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0 (t : ℂ) /
        signedZeroFrequency N‖ ≤
      ((1 + 3 / ‖signedZeroFrequency N‖) / ‖signedZeroFrequency N‖) *
        signedRemainderEnvelope N t ^ 2 := by
  have ha := signedZeroFrequency_ne_zero (show 2 ≤ N by omega)
  have h := perturbed_exponential_first_correction
    (R := signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0)
    (R' := signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 1) ha hc hsmall
    (fun w hw => by simpa using signedRemainderEnvelope_bounds hN ht hw 0)
    (fun w _ => hasDerivAt_finiteExponentialRemainder _ _ _ 0 w)
    (fun w hw => by simpa using signedRemainderEnvelope_bounds hN ht hw 1)
    hz ((signed_two_term_zero_iff (by omega) _ _ z).mp hz0)
  convert h using 1
  ring

/-- The quadratic envelope is exactly a constant times exp(-2 gamma t). -/
theorem signedRemainderEnvelope_sq (N : ℕ) (t : ℝ) :
    signedRemainderEnvelope N t ^ 2 =
      signedRemainderScale N ^ 2 * Real.exp (-(2 * signedPolygonGap N) * t) := by
  unfold signedRemainderEnvelope
  rw [mul_pow, pow_two (Real.exp _), ← Real.exp_add]
  congr 2
  ring

/-- The actual normalized derivative has a quantified exponentially small error. -/
theorem canonicalSignedDenominator_normalized_derivative_error {N : ℕ} (hN : 3 ≤ N)
    {t : ℝ} (ht : 1 / ‖signedZeroFrequency N‖ ≤ t) {z : ℂ}
    (hz : z ∈ closedBall (t : ℂ) (1 / ‖signedZeroFrequency N‖))
    (hz0 : canonicalSignedDenominator N z = 0) :
    ‖(signedZeroFrequency N * Complex.exp (signedZeroFrequency N * z) +
      signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 1 z) +
        signedZeroFrequency N‖ ≤
      (‖signedZeroFrequency N‖ + 2) * signedRemainderEnvelope N t := by
  have h := perturbed_exponential_derivative_error
    (a := signedZeroFrequency N)
    (R := signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0)
    ((signed_two_term_zero_iff (by omega) _ _ z).mp hz0)
    (Rz' := signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 1 z)
  have h0 := signedRemainderEnvelope_bounds hN ht hz 0
  have h1 := signedRemainderEnvelope_bounds hN ht hz 1
  simp only [pow_zero, one_mul, pow_one] at h0 h1
  exact h.trans (by nlinarith [mul_le_mul_of_nonneg_left h0 (norm_nonneg (signedZeroFrequency N))])

end
end Komorebi.PaperIV
