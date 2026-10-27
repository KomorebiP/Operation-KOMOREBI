/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroZetaContinuation
import Mathlib.Analysis.SpecialFunctions.Trigonometric.DerivHyp

namespace Komorebi.PaperIV
noncomputable section
open Complex

theorem quartic_root_square : ((1 + I) / (Real.sqrt 2 : ℂ)) ^ 2 = I := by
  have hq : (Real.sqrt 2 : ℂ) ^ 2 = 2 := by
    norm_cast
    exact Real.sq_sqrt (by norm_num)
  rw [div_pow, hq, add_sq, I_sq]
  ring

theorem canonicalSignedDenominator_four_eq_cos_cosh (z : ℂ) :
    canonicalSignedDenominator 4 z = cos (z / (Real.sqrt 2 : ℂ)) * cosh (z / (Real.sqrt 2 : ℂ)) := by
  have hr : ((1 + I) / (Real.sqrt 2 : ℂ)) ^ 4 = -1 := by
    rw [show 4 = 2 * 2 by rfl, pow_mul, quartic_root_square, I_sq]
  rw [canonicalSignedDenominator, entireSigned_independent_roots (by norm_num) (by norm_num)
    (canonicalPrimitiveRoot_isPrimitive (by norm_num)) isPrimitiveRoot_I
    (canonicalSignedRoot_pow (by norm_num)) hr, entireSigned_zero_eq_average]
  norm_num only [Finset.sum_range_succ, Finset.sum_range_zero, pow_zero, pow_one,
    pow_succ, I_sq, mul_one, zero_add, Nat.cast_ofNat]
  rw [cos, cosh, div_mul_div_comm, add_mul, mul_add, mul_add]
  simp only [mul_add, ← exp_add, one_mul, neg_mul]
  have h1 : (1 + I) / (Real.sqrt 2 : ℂ) * z = z / (Real.sqrt 2 : ℂ) * I + z / (Real.sqrt 2 : ℂ) := by ring
  have h2 : (1 + I) / (Real.sqrt 2 : ℂ) * I * z = z / (Real.sqrt 2 : ℂ) * I + -(z / (Real.sqrt 2 : ℂ)) := by
    linear_combination (z / (Real.sqrt 2 : ℂ)) * I_sq
  have h3 : (1 + I) / (Real.sqrt 2 : ℂ) * (I * I) * z =
      -(z / (Real.sqrt 2 : ℂ) * I) + -(z / (Real.sqrt 2 : ℂ)) := by
    rw [I_mul_I]; ring
  have h4 : (1 + I) / (Real.sqrt 2 : ℂ) * (I * I * I) * z =
      -(z / (Real.sqrt 2 : ℂ) * I) + z / (Real.sqrt 2 : ℂ) := by
    rw [I_mul_I]
    linear_combination -(z / (Real.sqrt 2 : ℂ)) * I_sq
  rw [h1, h2, h3, h4]
  ring

theorem complex_cos_zero_iff_nat {z : ℂ} :
    cos z = 0 ↔ ∃ m : ℕ, z = ((m : ℂ) + 1 / 2) * (Real.pi : ℂ) ∨
      z = -(((m : ℂ) + 1 / 2) * (Real.pi : ℂ)) := by
  rw [← entireSigned_two_eq_cos (IsPrimitiveRoot.neg_one 0 (by decide)) I_sq]
  exact entireSigned_two_zero_iff_nat (IsPrimitiveRoot.neg_one 0 (by decide)) I_sq

def quarticPositiveZero (m : ℕ) : ℝ := Real.sqrt 2 * Real.pi * ((m : ℝ) + 1 / 2)

theorem quarticPositiveZero_pos (m : ℕ) : 0 < quarticPositiveZero m := by
  unfold quarticPositiveZero
  positivity

theorem quarticPositiveZero_div_sqrt (m : ℕ) :
    (quarticPositiveZero m : ℂ) / (Real.sqrt 2 : ℂ) =
      ((m : ℂ) + 1 / 2) * (Real.pi : ℂ) := by
  have hq : (Real.sqrt 2 : ℂ) ≠ 0 := ofReal_ne_zero.mpr (by positivity)
  unfold quarticPositiveZero
  push_cast
  field_simp

theorem canonicalSignedDenominator_four_zero_iff {z : ℂ} :
    canonicalSignedDenominator 4 z = 0 ↔ ∃ m : ℕ,
      z = (quarticPositiveZero m : ℂ) ∨ z = -(quarticPositiveZero m : ℂ) ∨
      z = I * (quarticPositiveZero m : ℂ) ∨ z = -(I * (quarticPositiveZero m : ℂ)) := by
  have hq : (Real.sqrt 2 : ℂ) ≠ 0 := ofReal_ne_zero.mpr (by positivity)
  rw [canonicalSignedDenominator_four_eq_cos_cosh, mul_eq_zero, ← cos_mul_I]
  constructor
  · intro hz
    rcases hz with hc | hc
    · obtain ⟨m, hm | hm⟩ := complex_cos_zero_iff_nat.mp hc
      · refine ⟨m, Or.inl ?_⟩
        apply (div_left_inj' hq).mp
        rw [quarticPositiveZero_div_sqrt, hm]
      · refine ⟨m, Or.inr (Or.inl ?_)⟩
        apply (div_left_inj' hq).mp
        rw [neg_div, quarticPositiveZero_div_sqrt, hm]
    · obtain ⟨m, hm | hm⟩ := complex_cos_zero_iff_nat.mp hc
      · refine ⟨m, Or.inr (Or.inr (Or.inr ?_))⟩
        have h := congrArg (fun w : ℂ => -(w * I)) hm
        rw [mul_assoc, I_mul_I, mul_neg_one, neg_neg] at h
        apply (div_left_inj' hq).mp
        rw [h, neg_div, mul_div_assoc, quarticPositiveZero_div_sqrt]
        ring
      · refine ⟨m, Or.inr (Or.inr (Or.inl ?_))⟩
        have h := congrArg (fun w : ℂ => -(w * I)) hm
        rw [mul_assoc, I_mul_I, mul_neg_one, neg_neg] at h
        apply (div_left_inj' hq).mp
        rw [h, mul_div_assoc, quarticPositiveZero_div_sqrt]
        ring
  · rintro ⟨m, hm | hm | hm | hm⟩
    · left; rw [hm, quarticPositiveZero_div_sqrt]
      exact complex_cos_zero_iff_nat.mpr ⟨m, Or.inl rfl⟩
    · left; rw [hm, neg_div, quarticPositiveZero_div_sqrt, cos_neg]
      exact complex_cos_zero_iff_nat.mpr ⟨m, Or.inl rfl⟩
    · right
      rw [hm, mul_div_assoc, quarticPositiveZero_div_sqrt]
      have he : I * (((m : ℂ) + 1 / 2) * (Real.pi : ℂ)) * I =
          -(((m : ℂ) + 1 / 2) * (Real.pi : ℂ)) := by
        linear_combination (((m : ℂ) + 1 / 2) * (Real.pi : ℂ)) * I_sq
      rw [he, cos_neg]
      exact complex_cos_zero_iff_nat.mpr ⟨m, Or.inl rfl⟩
    · right
      rw [hm, neg_div, mul_div_assoc, quarticPositiveZero_div_sqrt]
      have he : -(I * (((m : ℂ) + 1 / 2) * (Real.pi : ℂ))) * I =
          ((m : ℂ) + 1 / 2) * (Real.pi : ℂ) := by
        linear_combination -(((m : ℂ) + 1 / 2) * (Real.pi : ℂ)) * I_sq
      rw [he]
      exact complex_cos_zero_iff_nat.mpr ⟨m, Or.inl rfl⟩

theorem quarticPositiveZero_simple (m : ℕ) :
    analyticOrderAt (canonicalSignedDenominator 4) (quarticPositiveZero m : ℂ) = 1 := by
  let z : ℂ := quarticPositiveZero m
  let a : ℂ := Real.sqrt 2
  have ha : a ≠ 0 := ofReal_ne_zero.mpr (by positivity)
  have hc : cos (z / a) = 0 := by
    rw [show z / a = ((m : ℂ) + 1 / 2) * (Real.pi : ℂ) from quarticPositiveZero_div_sqrt m]
    exact complex_cos_zero_iff_nat.mpr ⟨m, Or.inl rfl⟩
  have hch : cosh (z / a) ≠ 0 := by
    rw [show z / a = ((m : ℂ) + 1 / 2) * (Real.pi : ℂ) from quarticPositiveZero_div_sqrt m]
    have he : ((m : ℂ) + 1 / 2) * (Real.pi : ℂ) = (((m : ℝ) + 1 / 2) * Real.pi : ℝ) := by push_cast; rfl
    rw [he, ← ofReal_cosh]
    exact ofReal_ne_zero.mpr (Real.cosh_pos _).ne'
  have hs : sin (z / a) ≠ 0 := by
    intro h
    have he := sin_sq_add_cos_sq (z / a)
    simp only [h, hc, zero_pow two_ne_zero, zero_add, zero_ne_one] at he
  have he : canonicalSignedDenominator 4 = fun w => cos (w / a) * cosh (w / a) :=
    funext canonicalSignedDenominator_four_eq_cos_cosh
  have hd := ((hasDerivAt_cos (z / a)).comp z ((hasDerivAt_id z).div_const a)).mul
    ((hasDerivAt_cosh (z / a)).comp z ((hasDerivAt_id z).div_const a))
  apply (analyticAt_entireSigned 4 0 _ _ _).analyticOrderAt_eq_one_of_zero_deriv_ne_zero
  · exact canonicalSignedDenominator_four_zero_iff.mpr ⟨m, Or.inl rfl⟩
  · change deriv (canonicalSignedDenominator 4) z ≠ 0
    rw [he]
    erw [hd.deriv]
    simp only [Function.comp_apply, id_eq, hc, zero_mul, add_zero, one_div]
    exact mul_ne_zero (mul_ne_zero (neg_ne_zero.mpr hs) (inv_ne_zero ha)) hch

theorem canonicalSignedDenominator_four_zero_order_one {z : ℂ}
    (hz : canonicalSignedDenominator 4 z = 0) :
    analyticOrderAt (canonicalSignedDenominator 4) z = 1 := by
  obtain ⟨m, hm | hm | hm | hm⟩ := canonicalSignedDenominator_four_zero_iff.mp hz
  · rw [hm]; exact quarticPositiveZero_simple m
  · rw [hm, show -(quarticPositiveZero m : ℂ) = (-1 : ℂ) * (quarticPositiveZero m : ℂ) by ring,
      ← canonicalSignedDenominator_order_rotation (by norm_num) (show (-1 : ℂ) ^ 4 = 1 by norm_num)]
    exact quarticPositiveZero_simple m
  · rw [hm, ← canonicalSignedDenominator_order_rotation (by norm_num) isPrimitiveRoot_I.pow_eq_one]
    exact quarticPositiveZero_simple m
  · rw [hm, show -(I * (quarticPositiveZero m : ℂ)) = (-I) * (quarticPositiveZero m : ℂ) by ring,
      ← canonicalSignedDenominator_order_rotation (by norm_num) isPrimitiveRoot_neg_I.pow_eq_one]
    exact quarticPositiveZero_simple m

end
end Komorebi.PaperIV
