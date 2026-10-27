/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.NormalizedOrder
import Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

theorem log_growth_ratio_of_polynomial_exp_bounds {M : ℝ → ℝ} {p B C : ℝ} (j : ℕ)
    (hp : 0 < p) (hB : 0 < B) (hC : 0 < C)
    (hb : ∀ᶠ R in atTop,
      Real.exp (R ^ p) / (C * (R ^ p) ^ j) ≤ M R ∧ M R ≤ B * Real.exp (R ^ p)) :
    Tendsto (fun R : ℝ => Real.log (M R) / R ^ p) atTop (𝓝 1) := by
  have ht := tendsto_rpow_atTop hp
  have hlog : Tendsto (fun R : ℝ => Real.log (R ^ p) / R ^ p) atTop (𝓝 0) := by
    have h : Tendsto (fun x : ℝ => Real.log x / x) atTop (𝓝 0) := by
      simpa using (isLittleO_log_rpow_atTop (by norm_num : (0 : ℝ) < 1)).tendsto_div_nhds_zero
    exact h.comp ht
  have hl : Tendsto (fun R : ℝ => 1 - Real.log C / R ^ p - (j : ℝ) * (Real.log (R ^ p) / R ^ p))
      atTop (𝓝 1) := by
    simpa using (tendsto_const_nhds.sub (tendsto_const_nhds.div_atTop ht)).sub (hlog.const_mul (j : ℝ))
  have hu : Tendsto (fun R : ℝ => 1 + Real.log B / R ^ p) atTop (𝓝 1) := by
    simpa using tendsto_const_nhds.add (tendsto_const_nhds.div_atTop ht)
  apply tendsto_of_tendsto_of_tendsto_of_le_of_le' hl hu
  · filter_upwards [hb, eventually_gt_atTop (0 : ℝ)] with R hR hpos
    have ht0 : 0 < R ^ p := Real.rpow_pos_of_pos hpos p
    have hden : 0 < C * (R ^ p) ^ j := mul_pos hC (pow_pos ht0 j)
    have h := Real.log_le_log (div_pos (Real.exp_pos _) hden) hR.1
    rw [Real.log_div (Real.exp_ne_zero _) hden.ne', Real.log_exp,
      Real.log_mul hC.ne' (pow_ne_zero j ht0.ne'), Real.log_pow] at h
    have hh := div_le_div_of_nonneg_right h ht0.le
    convert hh using 1
    field_simp
    ring
  · filter_upwards [hb, eventually_gt_atTop (0 : ℝ)] with R hR hpos
    have ht0 : 0 < R ^ p := Real.rpow_pos_of_pos hpos p
    have hm : 0 < M R := (div_pos (Real.exp_pos _) (mul_pos hC (pow_pos ht0 j))).trans_le hR.1
    have h := Real.log_le_log hm hR.2
    rw [Real.log_mul hB.ne' (Real.exp_ne_zero _), Real.log_exp] at h
    have hh := div_le_div_of_nonneg_right h ht0.le
    convert hh using 1
    field_simp
    ring

theorem entireTransfer_positive_ray_lower {N : ℕ} (hN : 0 < N) (j : ℕ)
    {ω : ℂ} (hω : IsPrimitiveRoot ω N) :
    ∀ᶠ r : ℝ in atTop, Real.exp r / (2 * N) ≤ ‖entireTransfer N j ω 1 r‖ := by
  have ht := (entireTransfer_positive_ray hN j hω).norm
  have hh := ht.eventually (eventually_ge_nhds (by norm_num : (1 / 2 : ℝ) < ‖(1 : ℂ)‖))
  filter_upwards [hh] with r hr
  have hn : (0 : ℝ) < N := by exact_mod_cast hN
  simp only [norm_mul, Complex.norm_natCast, Complex.norm_exp, Complex.neg_re, Complex.ofReal_re] at hr
  have he : ‖entireTransfer N j ω 1 r‖ =
      (Real.exp r / N) * ((N : ℝ) * Real.exp (-r) * ‖entireTransfer N j ω 1 r‖) := by
    rw [Real.exp_neg]
    field_simp
  rw [he]
  have hmul := mul_le_mul_of_nonneg_left hr (le_of_lt (div_pos (Real.exp_pos r) hn))
  convert! hmul using 1
  ring

theorem entireNormalizedSection_maximum_bounds {N j : ℕ} (hN : 0 < N) (hj : j < N) :
    ∀ᶠ R : ℝ in atTop,
      Real.exp (R ^ (1 / (N : ℝ))) / (2 * N * (R ^ (1 / (N : ℝ))) ^ j) ≤
        diskMaximumModulus (entireNormalizedSection N j) R ∧
      diskMaximumModulus (entireNormalizedSection N j) R ≤
        (j.factorial : ℝ) * Real.exp (R ^ (1 / (N : ℝ))) := by
  have hp : 0 < 1 / (N : ℝ) := by positivity
  have ht := tendsto_rpow_atTop hp
  have hc : Continuous (entireNormalizedSection N j) :=
    (show Differentiable ℂ (entireNormalizedSection N j) from fun z =>
      (analyticAt_entireNormalizedSection hN j z).differentiableAt).continuous
  filter_upwards [ht.eventually (entireTransfer_positive_ray_lower hN j (canonicalPrimitiveRoot_isPrimitive hN)),
    eventually_gt_atTop (0 : ℝ)] with R hlow hR
  let t : ℝ := R ^ (1 / (N : ℝ))
  have ht0 : 0 < t := Real.rpow_pos_of_pos hR _
  have hpow : t ^ N = R := by simpa only [t, one_div] using Real.rpow_inv_natCast_pow hR.le hN.ne'
  have he := congrArg norm (entireNormalizedSection_transfer hN hj
    (canonicalPrimitiveRoot_isPrimitive hN) (t : ℂ))
  simp only [norm_mul, norm_pow, Complex.norm_real, Real.norm_eq_abs, abs_of_pos ht0,
    Complex.norm_natCast] at he
  have hf : (1 : ℝ) ≤ j.factorial := by exact_mod_cast Nat.one_le_iff_ne_zero.mpr j.factorial_ne_zero
  constructor
  · have hcoeff : Real.exp t / (2 * N) ≤
        ‖entireNormalizedSection N j ((t : ℂ) ^ N)‖ * t ^ j := by
      rw [he]
      exact hlow.trans (le_mul_of_one_le_left (norm_nonneg _) hf)
    have hdiv := (div_le_iff₀ (pow_pos ht0 j)).mpr hcoeff
    have hmax := norm_le_diskMaximumModulus hc (z := (t : ℂ) ^ N) (r := R)
      (by simp [norm_pow, Complex.norm_real, Real.norm_eq_abs, abs_of_pos ht0, hpow])
    have hdiv' : Real.exp t / (2 * N * t ^ j) ≤ ‖entireNormalizedSection N j ((t : ℂ) ^ N)‖ := by
      simpa only [div_div] using hdiv
    exact hdiv'.trans hmax
  · apply diskMaximumModulus_le hR.le
    intro w hw
    exact (entireNormalizedSection_norm_le hN j w).trans
      (mul_le_mul_of_nonneg_left (Real.exp_le_exp.mpr (Real.rpow_le_rpow (norm_nonneg _) hw hp.le)) (by positivity))

theorem entireNormalizedSection_growth_limit {N j : ℕ} (hN : 0 < N) (hj : j < N) :
    Tendsto (fun R : ℝ => Real.log (diskMaximumModulus (entireNormalizedSection N j) R) /
      R ^ (1 / (N : ℝ))) atTop (𝓝 1) :=
  log_growth_ratio_of_polynomial_exp_bounds j (by positivity) (by positivity) (by positivity)
    (entireNormalizedSection_maximum_bounds hN hj)

/-- Exact order, including the N=1 case; no coefficient-order formula is assumed. -/
theorem entireNormalizedSection_order_exact {N j : ℕ} (hN : 0 < N) (hj : j < N) :
    entireGrowthOrder (entireNormalizedSection N j) = 1 / (N : ℝ) :=
  (order_ratio_of_log_growth (entireNormalizedSection_growth_limit hN hj)).limsup_eq

end
end Komorebi.PaperIV
