/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.LeadingPoleBounds
import Mathlib.Analysis.Asymptotics.AsymptoticEquivalent

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Asymptotics
open scoped Topology Classical

def cosineNearestZeros : Finset ℂ := {(Real.pi : ℂ)/2, -(Real.pi : ℂ)/2}

theorem canonicalSignedDenominator_two_cos : canonicalSignedDenominator 2 = Complex.cos :=
  funext (entireSigned_two_eq_cos (canonicalPrimitiveRoot_isPrimitive (by norm_num))
    (canonicalSignedRoot_pow (by norm_num)))

theorem cosineNearestZeros_norm {z : ℂ} (hz : z ∈ cosineNearestZeros) : ‖z‖ = Real.pi/2 := by
  simp only [cosineNearestZeros, Finset.mem_insert, Finset.mem_singleton] at hz
  rcases hz with rfl | rfl <;> simp [Complex.norm_real, Real.norm_eq_abs, Real.pi_pos.le]

theorem cosineNearestZeros_root {z : ℂ} (hz : z ∈ cosineNearestZeros) : canonicalSignedDenominator 2 z = 0 := by
  rw [canonicalSignedDenominator_two_cos]
  simp only [cosineNearestZeros, Finset.mem_insert, Finset.mem_singleton] at hz
  rcases hz with rfl | rfl <;> simp [neg_div, Complex.cos_neg, Complex.cos_pi_div_two]

theorem cosineNearestZeros_simple {z : ℂ} (hz : z ∈ cosineNearestZeros) :
    deriv (canonicalSignedDenominator 2) z ≠ 0 :=
  entireSigned_two_zero_derivative_ne_zero (canonicalPrimitiveRoot_isPrimitive (by norm_num))
    (canonicalSignedRoot_pow (by norm_num)) (cosineNearestZeros_root hz)

theorem cosine_nearest_zero_exhaustion {z : ℂ} (hnorm : ‖z‖ < 3*Real.pi/2)
    (hz : canonicalSignedDenominator 2 z = 0) : z ∈ cosineNearestZeros := by
  obtain ⟨m, hm⟩ := (entireSigned_two_zero_iff_nat (canonicalPrimitiveRoot_isPrimitive (by norm_num))
    (canonicalSignedRoot_pow (by norm_num))).mp hz
  have hmod : ‖(((m : ℂ)+1/2)*(Real.pi : ℂ))‖ = ((m : ℝ)+1/2)*Real.pi := by
    have he : (((m : ℂ)+1/2)*(Real.pi : ℂ)) = ((((m : ℝ)+1/2)*Real.pi : ℝ) : ℂ) := by push_cast; rfl
    rw [he, Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg (by positivity)]
  have hle : ((m : ℝ)+1/2)*Real.pi < 3*Real.pi/2 := by
    rcases hm with hm | hm <;> simpa only [hm, norm_neg, hmod] using hnorm
  have hm0 : m = 0 := by
    by_contra h
    have hm1 : (1 : ℝ) ≤ m := by exact_mod_cast Nat.one_le_iff_ne_zero.mpr h
    nlinarith [Real.pi_pos]
  subst m
  rcases hm with rfl | rfl <;> simp [cosineNearestZeros, div_eq_mul_inv, mul_comm]

theorem secant_leading_coefficient (n : ℕ) :
    leadingPoleCoefficient cosineNearestZeros
      (canonicalPoleCoefficient (canonicalSignedDenominator 2) 1) 1 (2*n) =
      2 * (2/(Real.pi : ℂ)) ^ (2*n+1) := by
  have hp : (Real.pi : ℂ) ≠ 0 := by exact_mod_cast Real.pi_ne_zero
  have hne : (Real.pi : ℂ)/2 ≠ -(Real.pi : ℂ)/2 := by
    intro he
    have hh := congrArg Complex.re he
    simp at hh
    linarith [Real.pi_pos]
  simp only [leadingPoleCoefficient, Nat.add_sub_cancel, Nat.sub_self, Nat.choose_zero_right,
    Nat.cast_one, one_mul, cosineNearestZeros, Finset.sum_pair hne,
    canonicalPoleCoefficient_leading, canonicalSignedDenominator_two_cos, Complex.deriv_cos,
    pow_one, Complex.sin_pi_div_two]
  rw [show -(Real.pi : ℂ)/2 = -((Real.pi : ℂ)/2) by ring,
    Complex.sin_neg, Complex.sin_pi_div_two]
  simp only [neg_neg, mul_neg, mul_one, inv_neg, (even_two_mul n).neg_pow]
  rw [pow_succ]
  field_simp
  ring

/-- A quantitative version of the secant asymptotic, with an explicit
exponentially smaller Cauchy remainder. -/
theorem secant_coefficient_error : ∃ C : ℝ, ∀ n : ℕ, 1 ≤ n →
    ‖reciprocalCoeff 2 n (1 : ℂ) - 2 * ((2*n).factorial : ℂ) * (2/(Real.pi : ℂ)) ^ (2*n+1)‖ ≤
      C * ((2*n).factorial : ℝ) * Real.pi⁻¹ ^ (2*n) := by
  obtain ⟨C, hC⟩ := reciprocalCoeff_leading_bound (by norm_num : 0 < 2)
    (show 0 < Real.pi/2 by positivity) (show Real.pi/2 < Real.pi by linarith [Real.pi_pos])
    (show Real.pi < 3*Real.pi/2 by linarith [Real.pi_pos])
    (fun _ hz => cosineNearestZeros_norm hz) (fun _ hz => cosineNearestZeros_root hz)
    (fun _ hz => cosineNearestZeros_simple hz) (fun _ hz => cosine_nearest_zero_exhaustion hz)
    (by norm_num : 0 < 1)
  refine ⟨C, fun n hn => ?_⟩
  have h := hC n hn
  rw [secant_leading_coefficient] at h
  simpa only [lowerPrincipalConstant_one, zero_mul, mul_zero, zero_add, Nat.cast_one,
    mul_assoc, mul_comm, mul_left_comm] using h

def secantMainTerm (n : ℕ) : ℂ :=
  2 * ((2*n).factorial : ℂ) * (2/(Real.pi : ℂ)) ^ (2*n+1)

theorem secantMainTerm_norm (n : ℕ) :
    ‖secantMainTerm n‖ = 2 * ((2*n).factorial : ℝ) * (2/Real.pi) ^ (2*n+1) := by
  simp [secantMainTerm, norm_pow, Complex.norm_real,
    Real.norm_eq_abs, abs_of_pos Real.pi_pos]

theorem secantMainTerm_ne_zero (n : ℕ) : secantMainTerm n ≠ 0 := by
  apply norm_ne_zero_iff.mp
  rw [secantMainTerm_norm]
  positivity

theorem secant_relative_error : ∃ C : ℝ, ∀ n : ℕ, 1 ≤ n →
    ‖reciprocalCoeff 2 n (1 : ℂ) / secantMainTerm n - 1‖ ≤
      (C * Real.pi / 4) * (1/4 : ℝ) ^ n := by
  obtain ⟨C, hC⟩ := secant_coefficient_error
  refine ⟨C, fun n hn => ?_⟩
  rw [div_sub_one (secantMainTerm_ne_zero n), norm_div]
  have hp : (0 : ℝ) < 2 * ((2*n).factorial : ℝ) * (2/Real.pi) ^ (2*n+1) := by positivity
  rw [secantMainTerm_norm]
  have hb := div_le_div_of_nonneg_right (hC n hn) hp.le
  apply hb.trans_eq
  rw [pow_succ, pow_mul, pow_mul, div_pow, inv_pow, div_pow]
  have hfac : ((2*n).factorial : ℝ) ≠ 0 := by positivity
  have hpi : Real.pi ^ (n*2) * Real.pi⁻¹ ^ (n*2) = 1 := by
    rw [← mul_pow, mul_inv_cancel₀ Real.pi_ne_zero, one_pow]
  have hfour : (1/4 : ℝ)^n * 4^n = 1 := by rw [← mul_pow]; norm_num
  field_simp
  ring_nf
  linear_combination 4*C*hpi - 4*C*hfour

/-- Corollary 13.4 as a genuine ratio limit for the named reciprocal coefficients. -/
theorem secant_coefficient_ratio_limit :
    Tendsto (fun n : ℕ => reciprocalCoeff 2 n (1 : ℂ) / secantMainTerm n) atTop (𝓝 1) := by
  obtain ⟨C, hC⟩ := secant_relative_error
  have hg : Tendsto (fun n : ℕ => (C*Real.pi/4) * (1/4 : ℝ)^n) atTop (𝓝 0) := by
    simpa using (tendsto_pow_atTop_nhds_zero_of_lt_one (by norm_num : (0:ℝ) ≤ 1/4)
      (by norm_num : (1/4:ℝ) < 1)).const_mul (C*Real.pi/4)
  have hh : Tendsto (fun n : ℕ => ‖reciprocalCoeff 2 n (1 : ℂ) / secantMainTerm n - 1‖) atTop (𝓝 0) :=
    squeeze_zero' (Eventually.of_forall (fun n => norm_nonneg _))
      ((eventually_ge_atTop (1:ℕ)).mono (fun n hn => hC n hn)) hg
  exact tendsto_iff_norm_sub_tendsto_zero.mpr hh

theorem secant_coefficient_asymptotic :
    (fun n : ℕ => reciprocalCoeff 2 n (1 : ℂ)) ~[atTop] secantMainTerm :=
  (isEquivalent_iff_tendsto_one (Eventually.of_forall secantMainTerm_ne_zero)).mpr secant_coefficient_ratio_limit

end
end Komorebi.PaperIV
