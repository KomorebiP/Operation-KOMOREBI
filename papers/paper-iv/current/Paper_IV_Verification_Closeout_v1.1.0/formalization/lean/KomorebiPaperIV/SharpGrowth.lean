/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.DominantExponential
import KomorebiPaperIV.CanonicalProductGrowth
import Mathlib.Topology.Order.LiminfLimsup

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Metric
open scoped Topology

/-- Maximum modulus on the closed disk. -/
def diskMaximumModulus (f : ℂ → ℂ) (r : ℝ) : ℝ :=
  sSup ((fun z => ‖f z‖) '' closedBall 0 r)

/-- Growth order in the usual maximum-modulus normalization. -/
def entireGrowthOrder (f : ℂ → ℂ) : ℝ :=
  limsup (fun r : ℝ => Real.log (Real.log (diskMaximumModulus f r)) / Real.log r) atTop

/-- Exponential type for functions of order one. -/
def entireExponentialType (f : ℂ → ℂ) : ℝ :=
  limsup (fun r : ℝ => Real.log (diskMaximumModulus f r) / r) atTop

theorem norm_le_diskMaximumModulus {f : ℂ → ℂ} (hf : Continuous f)
    {z : ℂ} {r : ℝ} (hz : ‖z‖ ≤ r) : ‖f z‖ ≤ diskMaximumModulus f r :=
  le_csSup ((isCompact_closedBall (0 : ℂ) r).bddAbove_image hf.norm.continuousOn)
    (mem_image_of_mem _ (mem_closedBall_zero_iff.mpr hz))

theorem diskMaximumModulus_le {f : ℂ → ℂ} {r B : ℝ} (hr : 0 ≤ r)
    (hf : ∀ z : ℂ, ‖z‖ ≤ r → ‖f z‖ ≤ B) : diskMaximumModulus f r ≤ B := by
  apply csSup_le
  · exact ⟨‖f 0‖, mem_image_of_mem _ (mem_closedBall_self hr)⟩
  · rintro _ ⟨z, hz, rfl⟩
    exact hf z (mem_closedBall_zero_iff.mp hz)

/-- Sharp logarithmic growth follows from matching exponential bounds. -/
theorem log_growth_ratio_of_exp_bounds {M : ℝ → ℝ} {p C : ℝ}
    (hp : 0 < p) (hC : 0 < C)
    (hb : ∀ᶠ r in atTop, Real.exp (r ^ p) / C ≤ M r ∧ M r ≤ Real.exp (r ^ p)) :
    Tendsto (fun r : ℝ => Real.log (M r) / r ^ p) atTop (𝓝 1) := by
  have hl : Tendsto (fun r : ℝ => 1 - Real.log C / r ^ p) atTop (𝓝 1) := by
    simpa using tendsto_const_nhds.sub (tendsto_const_nhds.div_atTop (tendsto_rpow_atTop hp))
  apply tendsto_of_tendsto_of_tendsto_of_le_of_le' hl tendsto_const_nhds
  · filter_upwards [hb, eventually_gt_atTop (0 : ℝ)] with r hr hpos
    have hm : 0 < M r := (div_pos (Real.exp_pos _) hC).trans_le hr.1
    have h := Real.log_le_log (div_pos (Real.exp_pos _) hC) hr.1
    rw [Real.log_div (Real.exp_ne_zero _) hC.ne', Real.log_exp] at h
    apply (le_div_iff₀ (Real.rpow_pos_of_pos hpos _)).mpr
    have hne : r ^ p ≠ 0 := (Real.rpow_pos_of_pos hpos p).ne'
    field_simp
    nlinarith
  · filter_upwards [hb, eventually_gt_atTop (0 : ℝ)] with r hr hpos
    have hm : 0 < M r := (div_pos (Real.exp_pos _) hC).trans_le hr.1
    apply (div_le_one (Real.rpow_pos_of_pos hpos _)).mpr
    exact (Real.log_le_iff_le_exp hm).mpr hr.2

/-- The logarithmic ratio limit also proves the exact growth-order limit. -/
theorem order_ratio_of_log_growth {M : ℝ → ℝ} {p : ℝ}
    (h : Tendsto (fun r : ℝ => Real.log (M r) / r ^ p) atTop (𝓝 1)) :
    Tendsto (fun r : ℝ => Real.log (Real.log (M r)) / Real.log r) atTop (𝓝 p) := by
  have hlog : Tendsto (fun r : ℝ => Real.log (Real.log (M r) / r ^ p)) atTop (𝓝 0) := by
    simpa only [Real.log_one] using! (Real.continuousAt_log (by norm_num : (1 : ℝ) ≠ 0)).tendsto.comp h
  have hlim : Tendsto (fun r : ℝ => p + Real.log (Real.log (M r) / r ^ p) / Real.log r) atTop (𝓝 p) := by
    simpa using tendsto_const_nhds.add (hlog.div_atTop Real.tendsto_log_atTop)
  apply hlim.congr'
  filter_upwards [eventually_gt_atTop (1 : ℝ), h.eventually (eventually_gt_nhds (by norm_num : (0 : ℝ) < 1))] with r hr hratio
  have hr0 : 0 < r := by linarith
  have hpow : 0 < r ^ p := Real.rpow_pos_of_pos hr0 p
  have hm : 0 < Real.log (M r) := (div_pos_iff_of_pos_right hpow).mp hratio
  rw [Real.log_div hm.ne' hpow.ne', Real.log_rpow hr0]
  field_simp [(Real.log_pos hr).ne']
  ring

/-- A concrete lower bound on a vertex-facing ray, derived from the proved limit. -/
theorem canonicalSignedDenominator_ray_lower {N : ℕ} (hN : 0 < N) :
    ∀ᶠ r : ℝ in atTop,
      Real.exp r / (2 * N) ≤
        ‖canonicalSignedDenominator N ((r : ℂ) * star (canonicalSignedVertex N 0))‖ := by
  have ht := (canonicalSignedDenominator_dominant_ray hN hN).norm
  have hh : ∀ᶠ r : ℝ in atTop,
      (1 / 2 : ℝ) ≤ ‖(N : ℂ) * Complex.exp (-(r : ℂ)) *
        canonicalSignedDenominator N ((r : ℂ) * star (canonicalSignedVertex N 0))‖ := by
    exact (ht.eventually (eventually_ge_nhds (by norm_num : (1 / 2 : ℝ) < ‖(1 : ℂ)‖)))
  filter_upwards [hh] with r hr
  have hn : (0 : ℝ) < N := by exact_mod_cast hN
  simp only [norm_mul, Complex.norm_natCast, Complex.norm_exp, Complex.neg_re, Complex.ofReal_re] at hr
  have he : ‖canonicalSignedDenominator N ((r : ℂ) * star (canonicalSignedVertex N 0))‖ =
      (Real.exp r / N) * ((N : ℝ) * Real.exp (-r) *
        ‖canonicalSignedDenominator N ((r : ℂ) * star (canonicalSignedVertex N 0))‖) := by
    rw [Real.exp_neg]
    field_simp
  rw [he]
  have hmul := mul_le_mul_of_nonneg_left hr (le_of_lt (div_pos (Real.exp_pos r) hn))
  convert! hmul using 1
  ring

/-- The actual denominator maximum has matching exponential bounds. -/
theorem canonicalSignedDenominator_maximum_bounds {N : ℕ} (hN : 0 < N) :
    ∀ᶠ r : ℝ in atTop, Real.exp r / (2 * N) ≤ diskMaximumModulus (canonicalSignedDenominator N) r ∧
      diskMaximumModulus (canonicalSignedDenominator N) r ≤ Real.exp r := by
  have hc : Continuous (canonicalSignedDenominator N) :=
    (show Differentiable ℂ (canonicalSignedDenominator N) from fun z =>
      (analyticAt_entireSigned N 0 (canonicalPrimitiveRoot N) (canonicalSignedRoot N) z).differentiableAt).continuous
  filter_upwards [canonicalSignedDenominator_ray_lower hN, eventually_ge_atTop (0 : ℝ)] with r hr hr0
  constructor
  · exact hr.trans (norm_le_diskMaximumModulus hc (by simp [norm_canonicalSignedVertex, abs_of_nonneg hr0]))
  · exact diskMaximumModulus_le hr0 (fun z hz =>
      (norm_entireSigned_zero_le hN (canonicalPrimitiveRoot_isPrimitive hN) (canonicalSignedRoot_pow hN) z).trans
        (Real.exp_le_exp.mpr hz))

theorem canonicalSignedDenominator_type_limit {N : ℕ} (hN : 0 < N) :
    Tendsto (fun r : ℝ => Real.log (diskMaximumModulus (canonicalSignedDenominator N) r) / r) atTop (𝓝 1) := by
  simpa using log_growth_ratio_of_exp_bounds (p := 1) (by norm_num)
    (show (0 : ℝ) < 2 * N by positivity)
    (by simpa using canonicalSignedDenominator_maximum_bounds hN)

theorem canonicalSignedDenominator_order_limit {N : ℕ} (hN : 0 < N) :
    Tendsto (fun r : ℝ => Real.log (Real.log (diskMaximumModulus (canonicalSignedDenominator N) r)) / Real.log r)
      atTop (𝓝 1) :=
  order_ratio_of_log_growth (by simpa using canonicalSignedDenominator_type_limit hN)

theorem canonicalSignedDenominator_order_one {N : ℕ} (hN : 0 < N) :
    entireGrowthOrder (canonicalSignedDenominator N) = 1 :=
  (canonicalSignedDenominator_order_limit hN).limsup_eq

theorem canonicalSignedDenominator_type_one {N : ℕ} (hN : 0 < N) :
    entireExponentialType (canonicalSignedDenominator N) = 1 :=
  (canonicalSignedDenominator_type_limit hN).limsup_eq

/-- Passing to w=z^N transfers the sharp bound to the reduced entire function. -/
theorem entireReducedDenominator_maximum_bounds {N : ℕ} (hN : 0 < N) :
    ∀ᶠ r : ℝ in atTop,
      Real.exp (r ^ (1 / (N : ℝ))) / (2 * N) ≤ diskMaximumModulus (entireReducedDenominator N) r ∧
      diskMaximumModulus (entireReducedDenominator N) r ≤ Real.exp (r ^ (1 / (N : ℝ))) := by
  have hn : (0 : ℝ) < N := by exact_mod_cast hN
  have hp : 0 < 1 / (N : ℝ) := one_div_pos.mpr hn
  have ht := tendsto_rpow_atTop hp
  have hc : Continuous (entireReducedDenominator N) :=
    (show Differentiable ℂ (entireReducedDenominator N) from fun z =>
      (analyticAt_entireReducedDenominator hN z).differentiableAt).continuous
  filter_upwards [ht.eventually (canonicalSignedDenominator_ray_lower hN),
    eventually_ge_atTop (0 : ℝ)] with r hr hr0
  let z : ℂ := (r ^ (1 / (N : ℝ)) : ℝ) * star (canonicalSignedVertex N 0)
  have hz : ‖z‖ = r ^ (1 / (N : ℝ)) := by
    simp [z, norm_canonicalSignedVertex, abs_of_nonneg (Real.rpow_nonneg hr0 _)]
  have hw : ‖z ^ N‖ = r := by
    rw [norm_pow, hz, one_div, Real.rpow_inv_natCast_pow hr0 hN.ne']
  constructor
  · have hlow := norm_le_diskMaximumModulus hc (le_of_eq hw)
    rw [← canonicalSignedDenominator_eq_reduced_power hN] at hlow
    exact hr.trans hlow
  · apply diskMaximumModulus_le hr0
    intro w hw
    exact (entireReducedDenominator_norm_le hN w).trans
      (Real.exp_le_exp.mpr (Real.rpow_le_rpow (norm_nonneg _) hw hp.le))

theorem entireReducedDenominator_growth_limit {N : ℕ} (hN : 0 < N) :
    Tendsto (fun r : ℝ => Real.log (diskMaximumModulus (entireReducedDenominator N) r) / r ^ (1 / (N : ℝ)))
      atTop (𝓝 1) :=
  log_growth_ratio_of_exp_bounds (by positivity) (by positivity) (entireReducedDenominator_maximum_bounds hN)

theorem entireReducedDenominator_order_limit {N : ℕ} (hN : 0 < N) :
    Tendsto (fun r : ℝ => Real.log (Real.log (diskMaximumModulus (entireReducedDenominator N) r)) / Real.log r)
      atTop (𝓝 (1 / (N : ℝ))) :=
  order_ratio_of_log_growth (entireReducedDenominator_growth_limit hN)

/-- The complete order assertion of Proposition 11.2. -/
theorem entireReducedDenominator_order_exact {N : ℕ} (hN : 0 < N) :
    entireGrowthOrder (entireReducedDenominator N) = 1 / (N : ℝ) :=
  (entireReducedDenominator_order_limit hN).limsup_eq

end
end Komorebi.PaperIV
