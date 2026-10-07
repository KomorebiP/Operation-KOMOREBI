/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedCorrectionCompletion
import KomorebiPaperIV.ZeroZetaConvergence
import Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

/-- A global exponential lower bound at every sufficiently large zero,
including every root-of-unity ray. -/
theorem canonicalSignedDenominator_derivative_lower_bound {N : ℕ} (hN : 3 ≤ N) :
    ∃ A : ℝ, 0 < A ∧ ∃ R : ℝ, 0 < R ∧ ∀ z : ℂ,
      R ≤ ‖z‖ → canonicalSignedDenominator N z = 0 →
      A * Real.exp (Real.cos (Real.pi / N) * ‖z‖) ≤ ‖deriv (canonicalSignedDenominator N) z‖ := by
  obtain ⟨B, _, M0, hM0⟩ := signedPositiveZero_derivative_asymptotic hN
  have ht := (signedPositiveZero_tendsto_atTop (show 3 ≤ N from hN)).const_mul_atTop_of_neg
    (neg_lt_zero.mpr (signedPolygonGap_pos hN))
  have he := (Real.tendsto_exp_atBot.comp ht).const_mul B
  simp only [mul_zero] at he
  have hs := he.eventually (eventually_le_nhds (by norm_num : (0 : ℝ) < 1 / 2))
  simp only [Function.comp_apply] at hs
  obtain ⟨M1, hM1⟩ := eventually_atTop.mp hs
  obtain ⟨M, hM, R, hR, hex⟩ := signedPositiveZero_unique_global_strings hN (max M0 M1)
  let a := 2 * Real.sin (Real.pi / N) / N
  have ha : 0 < a := div_pos (mul_pos (by norm_num) (signed_sine_pos (by omega))) (by exact_mod_cast (show 0 < N by omega))
  refine ⟨a / 2, by positivity, R, hR, ?_⟩
  intro z hz hz0
  obtain ⟨p, hp, _⟩ := hex z hz hz0
  have hm0 := le_trans (le_max_left M0 M1) (le_trans hM p.property)
  have hm1 := le_trans (le_max_right M0 M1) (le_trans hM p.property)
  have hb := (hM0 p.val.2 hm0).trans (hM1 p.val.2 hm1)
  have hd : a / 2 * Real.exp (Real.cos (Real.pi / N) * signedPositiveZero N p.val.2) ≤
      ‖deriv (canonicalSignedDenominator N) (signedPositiveZero N p.val.2 : ℂ)‖ := by
    have hlow := (abs_le.mp hb).1
    have hpos : 0 < a * Real.exp (Real.cos (Real.pi / N) * signedPositiveZero N p.val.2) := by positivity
    have hq : (1 / 2 : ℝ) ≤ ‖deriv (canonicalSignedDenominator N) (signedPositiveZero N p.val.2 : ℂ)‖ /
        (a * Real.exp (Real.cos (Real.pi / N) * signedPositiveZero N p.val.2)) := by dsimp [a]; linarith
    have h := (le_div_iff₀ hpos).mp hq
    nlinarith
  rw [hp, signedPositiveZero_derivative_rotation (by omega)]
  have hw := (canonicalPrimitiveRoot_isPrimitive (show 0 < N by omega)).norm'_eq_one (by omega)
  simpa only [norm_mul, norm_inv, norm_pow, hw, one_pow, inv_one, one_mul,
    Complex.norm_real, Real.norm_eq_abs, abs_of_pos (signedPositiveZero_pos (show 2 ≤ N by omega) _)] using hd

/-- Exponential growth dominates any real power. The threshold is derived
from the actual denominator, not supplied as an analytic certificate. -/
theorem canonicalSignedDenominator_derivative_power_bound {N : ℕ} (hN : 3 ≤ N)
    {q : ℕ} (hq : 0 < q) (t : ℝ) :
    ∃ R : ℝ, 0 < R ∧ ∀ z : ℂ, R ≤ ‖z‖ → canonicalSignedDenominator N z = 0 →
      1 / ‖deriv (canonicalSignedDenominator N) z‖ ^ q / ‖z‖ ^ t ≤ 1 / ‖z‖ ^ (2 : ℝ) := by
  obtain ⟨A, hA, R0, hR0, hR0b⟩ := canonicalSignedDenominator_derivative_lower_bound hN
  have hc : 0 < (q : ℝ) * Real.cos (Real.pi / N) := mul_pos (by exact_mod_cast hq) (signed_cosine_pos hN)
  have he := (tendsto_rpow_mul_exp_neg_mul_atTop_nhds_zero (2 - t)
    ((q : ℝ) * Real.cos (Real.pi / N)) hc).const_mul (1 / A ^ q)
  simp only [mul_zero] at he
  have hb := he.eventually (eventually_le_nhds (by norm_num : (0 : ℝ) < 1))
  obtain ⟨R1, hR1⟩ := eventually_atTop.mp hb
  refine ⟨max R0 R1, lt_of_lt_of_le hR0 (le_max_left _ _), ?_⟩
  intro z hz hz0
  have hzpos : 0 < ‖z‖ := lt_of_lt_of_le hR0 (le_trans (le_max_left _ _) hz)
  have hd := hR0b z (le_trans (le_max_left _ _) hz) hz0
  have hdpos : 0 < ‖deriv (canonicalSignedDenominator N) z‖ := lt_of_lt_of_le (by positivity) hd
  have hdp := pow_le_pow_left₀ (by positivity : 0 ≤ A * Real.exp (Real.cos (Real.pi / N) * ‖z‖)) hd q
  have hratio := hR1 ‖z‖ (le_trans (le_max_right _ _) hz)
  have heq : (A * Real.exp (Real.cos (Real.pi / N) * ‖z‖)) ^ q =
      A ^ q * Real.exp (((q : ℝ) * Real.cos (Real.pi / N)) * ‖z‖) := by
    rw [mul_pow, ← Real.exp_nat_mul]
    congr 2
    ring
  rw [heq] at hdp
  have hinv := one_div_le_one_div_of_le (by positivity : 0 < A ^ q * Real.exp (((q : ℝ) * Real.cos (Real.pi / N)) * ‖z‖)) hdp
  apply (div_le_div_of_nonneg_right hinv (Real.rpow_pos_of_pos hzpos t).le).trans
  have hs : ‖z‖ ^ (2 - t) = ‖z‖ ^ (2 : ℝ) / ‖z‖ ^ t := Real.rpow_sub hzpos _ _
  rw [hs] at hratio
  rw [neg_mul, Real.exp_neg] at hratio
  apply (le_div_iff₀ (Real.rpow_pos_of_pos hzpos 2)).mpr
  convert hratio using 1
  ring

end
end Komorebi.PaperIV
