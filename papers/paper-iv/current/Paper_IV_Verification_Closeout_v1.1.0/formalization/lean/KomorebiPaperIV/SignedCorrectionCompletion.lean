/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedRealPhase

namespace Komorebi.PaperIV
noncomputable section
open Metric Filter
open scoped Topology

def signedLeadingCorrection (N m : ℕ) : ℂ :=
  signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0
    (signedZeroCenter N m : ℂ) / signedZeroFrequency N

theorem signedLeadingCorrection_eq_real_quotient {N : ℕ} (hN : 2 ≤ N) (m : ℕ) :
    signedLeadingCorrection N m = -canonicalSignedDenominator N (signedZeroCenter N m : ℂ) /
      (signedDerivativeMainTerm N m (signedZeroCenter N m) : ℂ) := by
  have ha := signedZeroFrequency_ne_zero hN
  have hP := signedNormalizationFactor_ne_zero (show 0 < N by omega) (signedZeroCenter N m : ℂ)
  have hl := signed_derivative_leading_phase hN m (signedZeroCenter N m)
  simp only [sub_self, mul_zero, neg_zero, Complex.ofReal_zero, zero_mul, Complex.exp_zero, mul_one] at hl
  have hn := signed_two_term_normalization hN
    (canonicalPrimitiveRoot N) (canonicalSignedRoot N) (signedZeroCenter N m : ℂ)
  change signedNormalizationFactor N (signedZeroCenter N m : ℂ) *
    canonicalSignedDenominator N (signedZeroCenter N m : ℂ) =
      1 + Complex.exp (signedZeroFrequency N * (signedZeroCenter N m : ℂ)) + _ at hn
  rw [signedZeroCenter_cancellation hN, add_neg_cancel, zero_add] at hn
  rw [signedLeadingCorrection, ← hn, ← hl]
  field_simp

theorem signedLeadingCorrection_real {N : ℕ} (hN : 2 ≤ N) (m : ℕ) :
    (signedLeadingCorrection N m).im = 0 := by
  rw [signedLeadingCorrection_eq_real_quotient hN]
  simp [Complex.div_im, entireSigned_canonical_real (show 0 < N by omega)
    (show 0 < N by omega), canonicalSignedDenominator]

theorem signedRemainderEnvelope_center_tendsto_zero {N : ℕ} (hN : 3 ≤ N) :
    Tendsto (fun m => signedRemainderEnvelope N (signedZeroCenter N m)) atTop (𝓝 0) := by
  have ht := (signedZeroCenter_tendsto_atTop (show 2 ≤ N by omega)).const_mul_atTop_of_neg
    (neg_lt_zero.mpr (signedPolygonGap_pos hN))
  have he := (Real.tendsto_exp_atBot.comp ht).const_mul (signedRemainderScale N)
  simpa only [mul_zero, signedRemainderEnvelope, Function.comp_apply] using he

/-- The leading displacement, now specialized to the actual named zeros, with
its real correction and the full quadratic exponential error. -/
theorem signedPositiveZero_first_correction {N : ℕ} (hN : 3 ≤ N) :
    (∀ m, (signedLeadingCorrection N m).im = 0) ∧
    ∃ C : ℝ, 0 < C ∧ ∃ M : ℕ, ∀ m ≥ M,
      ‖(signedPositiveZero N m : ℂ) - (signedZeroCenter N m : ℂ) - signedLeadingCorrection N m‖ ≤
        C * Real.exp (-(2 * signedPolygonGap N) * signedZeroCenter N m) := by
  refine ⟨signedLeadingCorrection_real (by omega), ?_⟩
  obtain ⟨_, _, M0, hM0⟩ := signedPositiveZero_local_strings hN
  have hs := (signedRemainderEnvelope_center_tendsto_zero hN).eventually
    (eventually_le_nhds (by norm_num : (0 : ℝ) < 1 / 2))
  obtain ⟨M1, hM1⟩ := eventually_atTop.mp hs
  let C := ((1 + 3 / ‖signedZeroFrequency N‖) / ‖signedZeroFrequency N‖) * signedRemainderScale N ^ 2
  have hS : 0 < signedRemainderScale N := by
    simpa only [signedRemainderEnvelope, mul_zero, Real.exp_zero, mul_one] using signedRemainderEnvelope_pos hN 0
  have ha : 0 < ‖signedZeroFrequency N‖ := norm_pos_iff.mpr (signedZeroFrequency_ne_zero (by omega))
  refine ⟨C, by dsimp [C]; positivity, max M0 M1, ?_⟩
  intro m hm
  have hx := (hM0 m (le_trans (le_max_left M0 M1) hm)).1
  have hb := canonicalSignedDenominator_first_correction hN (signedZeroCenter_ge_radius (by omega) m)
    (signedZeroCenter_cancellation (by omega) m) (hM1 m (le_trans (le_max_right M0 M1) hm)) hx.2.2 hx.2.1
  rw [signedRemainderEnvelope_sq] at hb
  simpa only [signedLeadingCorrection, C, mul_assoc] using hb

/-- A phase perturbation estimate with no small-angle side condition. -/
theorem norm_real_phase_sub_one_le (x : ℝ) :
    ‖Complex.exp ((x : ℂ) * Complex.I) - 1‖ ≤ |x| := by
  rw [mul_comm (x : ℂ), Complex.norm_exp_I_mul_ofReal_sub_one, Real.norm_eq_abs, abs_mul]
  have h := (Real.abs_sin_le_abs (x := x / 2))
  rw [abs_div, abs_of_pos (by norm_num : (0 : ℝ) < 2)] at h
  norm_num only [abs_of_pos (by norm_num : (0 : ℝ) < 2)]
  linarith

theorem relative_error_through_unit_phase {d b p : ℂ} (hb : b ≠ 0) (hp : ‖p‖ = 1) :
    ‖d / b - 1‖ ≤ ‖d / (b * p) - 1‖ + ‖p - 1‖ := by
  have hp0 : p ≠ 0 := by intro h; simp [h] at hp
  have he : d / b - 1 = (d / (b * p) - 1) * p + (p - 1) := by field_simp; ring
  rw [he]
  exact (norm_add_le _ _).trans_eq (by rw [norm_mul, hp, mul_one])

/-- Exact alternating-sign derivative asymptotics, in the original denominator
and at its actual real zeros. -/
theorem signedPositiveZero_signed_derivative_asymptotic {N : ℕ} (hN : 3 ≤ N) :
    ∃ C : ℝ, 0 < C ∧ ∃ M : ℕ, ∀ m ≥ M,
      ‖deriv (canonicalSignedDenominator N) (signedPositiveZero N m : ℂ) /
        (signedDerivativeMainTerm N m (signedPositiveZero N m) : ℂ) - 1‖ ≤
        C * Real.exp (-signedPolygonGap N * signedPositiveZero N m) := by
  obtain ⟨C0, hC0, M, hM⟩ := signedPositiveZero_local_strings hN
  let B := (‖signedZeroFrequency N‖ + 2) / ‖signedZeroFrequency N‖
  let S := signedRemainderScale N
  let r := 1 / ‖signedZeroFrequency N‖
  let T := B * S + Real.sin (Real.pi / N) * C0
  have hB : 0 < B := div_pos (by positivity) (norm_pos_iff.mpr (signedZeroFrequency_ne_zero (by omega)))
  have hS : 0 < S := by
    simpa only [signedRemainderEnvelope, mul_zero, Real.exp_zero, mul_one] using signedRemainderEnvelope_pos hN 0
  have hT : 0 < T := add_pos (mul_pos hB hS) (mul_pos (signed_sine_pos (by omega)) hC0)
  refine ⟨T * Real.exp (signedPolygonGap N * r), by positivity, M, ?_⟩
  intro m hm
  let x := signedPositiveZero N m
  let t := signedZeroCenter N m
  let p := Complex.exp ((-(Real.sin (Real.pi / N) * (x - t)) : ℝ) * Complex.I)
  have hp : ‖p‖ = 1 := Complex.norm_exp_ofReal_mul_I _
  have hx := (hM m hm).1
  have hdelta : |x - t| ≤ r := by
    simpa only [mem_closedBall, dist_eq_norm, ← Complex.ofReal_sub, Complex.norm_real, Real.norm_eq_abs] using hx.2.2
  have hphase : ‖p - 1‖ ≤ Real.sin (Real.pi / N) * |x - t| := by
    have h := norm_real_phase_sub_one_le (-(Real.sin (Real.pi / N) * (x - t)))
    simpa only [abs_neg, abs_mul, abs_of_pos (signed_sine_pos (show 2 ≤ N by omega))] using h
  have hrelative := canonicalSignedDenominator_relative_derivative_error hN
    (signedZeroCenter_ge_radius (by omega) m) hx.2.2 hx.2.1
  have hcombine := relative_error_through_unit_phase (d := deriv (canonicalSignedDenominator N) (x : ℂ))
    (Complex.ofReal_ne_zero.mpr (signedDerivativeMainTerm_ne_zero (show 2 ≤ N by omega) m x)) hp
  rw [← signed_derivative_leading_phase (by omega) m x] at hcombine
  have hsmall : ‖deriv (canonicalSignedDenominator N) (x : ℂ) /
      (signedDerivativeMainTerm N m x : ℂ) - 1‖ ≤ T * Real.exp (-signedPolygonGap N * t) := by
    apply hcombine.trans
    have hc := (hM m hm).2.2.1
    dsimp [T, B, S, signedRemainderEnvelope, x, t] at *
    nlinarith [mul_le_mul_of_nonneg_left hc (signed_sine_pos (by omega : 2 ≤ N)).le]
  have he : Real.exp (-signedPolygonGap N * t) ≤
      Real.exp (signedPolygonGap N * r) * Real.exp (-signedPolygonGap N * x) := by
    rw [← Real.exp_add]
    apply Real.exp_le_exp.mpr
    have hd := (le_abs_self (x - t)).trans hdelta
    nlinarith [signedPolygonGap_pos hN]
  exact hsmall.trans (by simpa only [mul_assoc] using mul_le_mul_of_nonneg_left he hT.le)

/-- The asymptotic sign is an actual eventual sign, not only a modulus claim. -/
theorem signedPositiveZero_eventual_derivative_sign {N : ℕ} (hN : 3 ≤ N) :
    ∃ M : ℕ, ∀ m ≥ M,
      0 < (-1 : ℝ) ^ (m + 1) *
        (deriv (canonicalSignedDenominator N) (signedPositiveZero N m : ℂ)).re := by
  obtain ⟨C, _, M0, hM0⟩ := signedPositiveZero_signed_derivative_asymptotic hN
  have ht := (signedPositiveZero_tendsto_atTop hN).const_mul_atTop_of_neg
    (neg_lt_zero.mpr (signedPolygonGap_pos hN))
  have he := (Real.tendsto_exp_atBot.comp ht).const_mul C
  simp only [mul_zero] at he
  have hs := he.eventually (eventually_le_nhds (by norm_num : (0 : ℝ) < 1 / 2))
  obtain ⟨M1, hM1⟩ := eventually_atTop.mp hs
  refine ⟨max M0 M1, ?_⟩
  intro m hm
  let x := signedPositiveZero N m
  let d := deriv (canonicalSignedDenominator N) (x : ℂ)
  let b := signedDerivativeMainTerm N m x
  have hb0 : b ≠ 0 := signedDerivativeMainTerm_ne_zero (by omega) m x
  have hb := (hM0 m (le_trans (le_max_left _ _) hm)).trans
    (hM1 m (le_trans (le_max_right _ _) hm))
  have hdreal : d = (d.re : ℂ) := by
    apply Complex.ext
    · rfl
    · exact canonicalSignedDenominator_derivative_real (by omega) x
  change ‖d / (b : ℂ) - 1‖ ≤ (1 / 2 : ℝ) at hb
  rw [hdreal, ← Complex.ofReal_div, ← Complex.ofReal_one, ← Complex.ofReal_sub,
    Complex.norm_real, Real.norm_eq_abs] at hb
  have hq : 0 < d.re / b := by have h := (abs_le.mp hb).1; linarith
  have hmul : 0 < d.re * b := by
    have heq : d.re * b = (d.re / b) * b ^ 2 := by field_simp
    rw [heq]
    exact mul_pos hq (sq_pos_of_ne_zero hb0)
  have hspos := signedDerivativeScale_pos (show 2 ≤ N by omega) x
  have h : 0 < ((-1 : ℝ) ^ (m + 1) * d.re) * signedDerivativeScale N x := by
    dsimp [b, signedDerivativeMainTerm] at hmul
    nlinarith
  exact (mul_pos_iff_of_pos_right hspos).mp h

end
end Komorebi.PaperIV
