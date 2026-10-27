/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedCorrectionCompletion

namespace Komorebi.PaperIV
noncomputable section

theorem signedPolygonGap_three : signedPolygonGap 3 = 3 / 2 := by
  unfold signedPolygonGap
  norm_num only [Nat.cast_ofNat, Real.cos_pi_div_three,
    show 3 * (Real.pi / 3) = Real.pi by ring, Real.cos_pi]

theorem signedZeroCenter_three (m : ℕ) :
    signedZeroCenter 3 m = (2 * Real.pi / Real.sqrt 3) * (m + 1 / 2) := by
  unfold signedZeroCenter
  norm_num only [Nat.cast_ofNat, Real.sin_pi_div_three]
  ring

theorem canonicalSignedVertex_three_one : canonicalSignedVertex 3 1 = -1 := by
  rw [canonicalSignedVertex_exp]
  norm_num only [Nat.cast_one, Nat.cast_ofNat]
  convert Complex.exp_pi_mul_I using 1
  congr 1
  push_cast
  ring

theorem canonicalSignedVertex_three_two :
    canonicalSignedVertex 3 2 = 1 / 2 - (Real.sqrt 3 : ℂ) / 2 * Complex.I := by
  apply Complex.ext
  · have h := canonicalSignedVertex_last_re (by norm_num : 0 < 3)
    norm_num only [Nat.reduceSub, Nat.cast_ofNat, Real.cos_pi_div_three] at h
    convert h using 1
    norm_num
  · have h := canonicalSignedVertex_last_im (by norm_num : 0 < 3)
    norm_num only [Nat.reduceSub, Nat.cast_ofNat, Real.sin_pi_div_three] at h
    convert h using 1
    norm_num

theorem signedExponentialRemainder_three (z : ℂ) :
    signedExponentialRemainder 3 (canonicalPrimitiveRoot 3) (canonicalSignedRoot 3) 0 z =
      Complex.exp ((-3 / 2 + (Real.sqrt 3 : ℂ) / 2 * Complex.I) * z) := by
  unfold signedExponentialRemainder finiteExponentialRemainder
  have hs : (((Finset.range 3).erase 0).erase (3 - 1)) = {1} := by decide
  rw [hs, Finset.sum_singleton, pow_zero, one_mul]
  change Complex.exp ((canonicalSignedVertex 3 1 - canonicalSignedVertex 3 2) * z) = _
  rw [canonicalSignedVertex_three_one, canonicalSignedVertex_three_two]
  congr 2
  ring

theorem signedLeadingCorrection_three (m : ℕ) :
    signedLeadingCorrection 3 m =
      (((-1 : ℝ) ^ m / Real.sqrt 3 * Real.exp (-3 * signedZeroCenter 3 m / 2) : ℝ) : ℂ) := by
  have hr : (Real.sqrt 3 : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr (Real.sqrt_ne_zero'.mpr (by norm_num))
  rw [signedLeadingCorrection, signedExponentialRemainder_three]
  have he : (-3 / 2 + (Real.sqrt 3 : ℂ) / 2 * Complex.I) * (signedZeroCenter 3 m : ℂ) =
      ((-3 * signedZeroCenter 3 m / 2 : ℝ) : ℂ) +
      ((Real.sin (Real.pi / 3) * signedZeroCenter 3 m : ℝ) : ℂ) * Complex.I := by
    rw [Real.sin_pi_div_three]
    push_cast
    ring
  rw [he, Complex.exp_add]
  have hp := signedZeroCenter_positive_phase (by norm_num : 2 ≤ 3) m
  norm_num only [Nat.cast_ofNat] at hp
  rw [hp, signedZeroFrequency, canonicalSignedVertex_adjacent_difference (by norm_num : 0 < 3)]
  norm_num only [Nat.cast_ofNat, Real.sin_pi_div_three]
  rw [← Complex.ofReal_exp]
  push_cast
  field_simp

/-- The exact cubic correction and the O(exp(-3t)) remainder, at the actual
zeros rather than at a hypothetical approximate root. -/
theorem signedPositiveZero_three_correction :
    ∃ C : ℝ, 0 < C ∧ ∃ M : ℕ, ∀ m ≥ M,
      |signedPositiveZero 3 m - signedZeroCenter 3 m -
        (-1 : ℝ) ^ m / Real.sqrt 3 * Real.exp (-3 * signedZeroCenter 3 m / 2)| ≤
          C * Real.exp (-3 * signedZeroCenter 3 m) := by
  obtain ⟨_, C, hC, M, hM⟩ := signedPositiveZero_first_correction (by norm_num : 3 ≤ 3)
  refine ⟨C, hC, M, ?_⟩
  intro m hm
  have h := hM m hm
  rw [signedLeadingCorrection_three, signedPolygonGap_three] at h
  norm_num only [show -(2 * (3 / 2 : ℝ)) = -3 by norm_num] at h
  simpa only [← Complex.ofReal_sub, Complex.norm_real, Real.norm_eq_abs] using h

end
end Komorebi.PaperIV
