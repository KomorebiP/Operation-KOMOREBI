/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.LargeZeroCompletion
import KomorebiPaperIV.AnalyticCycles

namespace Komorebi.PaperIV
noncomputable section

/-- All canonical signed sections commute with complex conjugation. -/
theorem entireSigned_canonical_conj {N j : ℕ} (hN : 0 < N) (hj : j < N) (z : ℂ) :
    entireSigned N j (canonicalPrimitiveRoot N) (canonicalSignedRoot N) (star z) =
      star (entireSigned N j (canonicalPrimitiveRoot N) (canonicalSignedRoot N) z) := by
  have hs := (hasSum_entireSigned hN hj (canonicalPrimitiveRoot_isPrimitive hN)
    (canonicalSignedRoot_pow hN) z).star
  have ht := hasSum_entireSigned hN hj (canonicalPrimitiveRoot_isPrimitive hN)
    (canonicalSignedRoot_pow hN) (star z)
  apply ht.unique
  convert hs using 1
  funext n
  by_cases h : n % N = j <;> simp [coeff_signedSection, signedSectionCoeff, h]

theorem entireSigned_canonical_real {N j : ℕ} (hN : 0 < N) (hj : j < N) (x : ℝ) :
    (entireSigned N j (canonicalPrimitiveRoot N) (canonicalSignedRoot N) (x : ℂ)).im = 0 := by
  have h := congrArg Complex.im (entireSigned_canonical_conj hN hj (x : ℂ))
  simp only [Complex.star_def, Complex.conj_ofReal, Complex.conj_im] at h
  linarith

theorem canonicalSignedDenominator_derivative_real {N : ℕ} (hN : 0 < N) (x : ℝ) :
    (deriv (canonicalSignedDenominator N) (x : ℂ)).im = 0 := by
  change (deriv (entireSigned N 0 (canonicalPrimitiveRoot N) (canonicalSignedRoot N)) (x : ℂ)).im = 0
  rw [entireSigned_derivative_zero hN (canonicalPrimitiveRoot_isPrimitive hN) (canonicalSignedRoot_pow hN)]
  simp only [Complex.neg_im, entireSigned_canonical_real hN (by omega : N - 1 < N), neg_zero]

theorem signed_sine_mul_center {N : ℕ} (hN : 2 ≤ N) (m : ℕ) :
    Real.sin (Real.pi / N) * signedZeroCenter N m = Real.pi * ((m : ℝ) + 1 / 2) := by
  unfold signedZeroCenter
  field_simp [(signed_sine_pos hN).ne']

theorem signedZeroCenter_positive_phase {N : ℕ} (hN : 2 ≤ N) (m : ℕ) :
    Complex.exp ((Real.sin (Real.pi / N) * signedZeroCenter N m : ℝ) * Complex.I) =
      (-1 : ℂ) ^ m * Complex.I := by
  rw [signed_sine_mul_center hN]
  have he : ((Real.pi * ((m : ℝ) + 1 / 2) : ℝ) : ℂ) * Complex.I =
      (m : ℂ) * ((Real.pi : ℂ) * Complex.I) + (Real.pi : ℂ) / 2 * Complex.I := by
    push_cast
    ring
  rw [he, Complex.exp_add, Complex.exp_nat_mul, Complex.exp_pi_mul_I,
    Complex.exp_pi_div_two_mul_I]

theorem signedZeroCenter_negative_phase {N : ℕ} (hN : 2 ≤ N) (m : ℕ) :
    Complex.exp ((-(Real.sin (Real.pi / N) * signedZeroCenter N m) : ℝ) * Complex.I) =
      (-1 : ℂ) ^ m * (-Complex.I) := by
  have h := congrArg star (signedZeroCenter_positive_phase hN m)
  simpa only [map_mul, map_pow, map_neg, map_one, Complex.star_def, ← Complex.exp_conj,
    Complex.conj_ofReal, Complex.conj_I, Complex.ofReal_neg,
    neg_mul, mul_neg] using h

def signedDerivativeScale (N : ℕ) (x : ℝ) : ℝ :=
  (2 * Real.sin (Real.pi / N) / N) * Real.exp (Real.cos (Real.pi / N) * x)

def signedDerivativeMainTerm (N m : ℕ) (x : ℝ) : ℝ :=
  (-1 : ℝ) ^ (m + 1) * signedDerivativeScale N x

theorem signedDerivativeScale_pos {N : ℕ} (hN : 2 ≤ N) (x : ℝ) :
    0 < signedDerivativeScale N x :=
  mul_pos (div_pos (mul_pos (by norm_num) (signed_sine_pos hN)) (by exact_mod_cast (show 0 < N by omega))) (Real.exp_pos _)

theorem signedDerivativeMainTerm_ne_zero {N : ℕ} (hN : 2 ≤ N) (m : ℕ) (x : ℝ) :
    signedDerivativeMainTerm N m x ≠ 0 :=
  mul_ne_zero (pow_ne_zero _ (by norm_num)) (signedDerivativeScale_pos hN x).ne'

/-- Exact phase decomposition of the leading derivative at every real point. -/
theorem signed_derivative_leading_phase {N : ℕ} (hN : 2 ≤ N) (m : ℕ) (x : ℝ) :
    -signedZeroFrequency N / signedNormalizationFactor N (x : ℂ) =
      (signedDerivativeMainTerm N m x : ℂ) *
        Complex.exp ((-(Real.sin (Real.pi / N) * (x - signedZeroCenter N m)) : ℝ) * Complex.I) := by
  have hn : (N : ℂ) ≠ 0 := by exact_mod_cast (show N ≠ 0 by omega)
  have hv : canonicalSignedVertex N (N - 1) =
      (Real.cos (Real.pi / N) : ℂ) - (Real.sin (Real.pi / N) : ℂ) * Complex.I := by
    apply Complex.ext
    · simp only [canonicalSignedVertex_last_re (show 0 < N by omega), Complex.sub_re,
        Complex.ofReal_re, Complex.mul_re, Complex.I_re, Complex.ofReal_im, Complex.I_im,
        mul_zero, zero_mul, sub_zero]
    · simp only [canonicalSignedVertex_last_im (show 0 < N by omega), Complex.sub_im,
        Complex.ofReal_im, Complex.mul_im, Complex.I_im, Complex.I_re, Complex.ofReal_re,
        mul_one, zero_mul, add_zero, zero_sub]
  have he : canonicalSignedVertex N (N - 1) * (x : ℂ) =
      ((Real.cos (Real.pi / N) * x : ℝ) : ℂ) +
      ((-(Real.sin (Real.pi / N) * signedZeroCenter N m) : ℝ) : ℂ) * Complex.I +
      ((-(Real.sin (Real.pi / N) * (x - signedZeroCenter N m)) : ℝ) : ℂ) * Complex.I := by
    rw [hv]; push_cast; ring
  rw [signedNormalizationFactor, Complex.exp_neg, div_mul_eq_div_div, div_inv_eq_mul,
    he, Complex.exp_add, Complex.exp_add, signedZeroCenter_negative_phase hN,
    ← Complex.ofReal_exp, signedZeroFrequency, canonicalSignedVertex_adjacent_difference (by omega),
    signedDerivativeMainTerm, signedDerivativeScale]
  push_cast
  rw [pow_succ]
  field_simp
  ring_nf
  simp [Complex.I_sq]

end
end Komorebi.PaperIV
