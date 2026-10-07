/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.CanonicalProductQuotient
import Mathlib.Analysis.Complex.HasPrimitives
import Mathlib.Analysis.Complex.BorelCaratheodory

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Metric
open scoped Topology

/-- A normalized entire function without zeros has an entire logarithm,
constructed by integrating its logarithmic derivative. -/
theorem entire_normalized_exists_log {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hn : ∀ z, f z ≠ 0) (h0 : f 0 = 1) :
    ∃ g : ℂ → ℂ, Differentiable ℂ g ∧ g 0 = 0 ∧ ∀ z, Complex.exp (g z) = f z := by
  have hd : Differentiable ℂ (fun z => deriv f z / f z) := by
    intro z
    exact (hf.analyticAt z).deriv.differentiableAt.div (hf z) (hn z)
  obtain ⟨g, hg0, hg⟩ := hd.isExactOn_univ.with_val_at 0 0
  have hg' : Differentiable ℂ g := fun z => (hg z (mem_univ z)).differentiableAt
  have hH : ∀ z, HasDerivAt (fun w => f w * Complex.exp (-g w)) 0 z := by
    intro z
    convert! ((hf z).hasDerivAt).mul ((hg z (mem_univ z)).neg.cexp) using 1
    field_simp [hn z]
    ring
  have he : ∀ z, f z * Complex.exp (-g z) = 1 := by
    intro z
    have h := is_const_of_deriv_eq_zero (fun w => (hH w).differentiableAt)
      (fun w => (hH w).deriv) z 0
    simpa only [hg0, h0, neg_zero, Complex.exp_zero, one_mul] using h
  refine ⟨g, hg', hg0, fun z => ?_⟩
  have h := he z
  rw [Complex.exp_neg, ← div_eq_mul_inv] at h
  exact ((div_eq_one_iff_eq (Complex.exp_ne_zero _)).mp h).symm

/-- Borel-Carathéodory turns a sublinear bound on real parts into rigidity.
The bound is uniform throughout each disk, not merely along one ray. -/
theorem entire_realPart_sublinear_constant {g : ℂ → ℂ} (hg : Differentiable ℂ g)
    (h0 : g 0 = 0) {M : ℝ → ℝ}
    (hp : ∀ᶠ R in atTop, 0 < M R)
    (hM : Tendsto (fun R => M R / R) atTop (𝓝 0))
    (hb : ∀ᶠ R in atTop, ∀ w : ℂ, ‖w‖ < R → (g w).re ≤ M R) : g = 0 := by
  funext z
  have hb' : ∀ᶠ R in atTop, ‖g z‖ ≤ 2 * (M R / R) * ‖z‖ / (1 - ‖z‖ / R) := by
    filter_upwards [hp, hb, eventually_gt_atTop (‖z‖ + 1)] with R hRp hRb hR
    have hR0 : 0 < R := by linarith [norm_nonneg z]
    have h := Complex.borelCaratheodory_zero hRp hg.differentiableOn
      (fun w hw => hRb w (mem_ball_zero_iff.mp hw)) hR0
      (mem_ball_zero_iff.mpr (by linarith)) h0
    convert h using 1
    field_simp
  have hsmall : Tendsto (fun R : ℝ => ‖z‖ / R) atTop (𝓝 0) := by
    simpa only [div_eq_mul_inv, mul_zero] using (tendsto_inv_atTop_zero.const_mul ‖z‖)
  have ht : Tendsto (fun R => 2 * (M R / R) * ‖z‖ / (1 - ‖z‖ / R)) atTop (𝓝 0) := by
    simpa only [mul_zero, zero_mul, sub_zero, zero_div] using!
      ((hM.const_mul 2).mul_const ‖z‖).div (tendsto_const_nhds.sub hsmall) (by norm_num)
  exact norm_eq_zero.mp (le_antisymm (ge_of_tendsto ht hb') (norm_nonneg _))

/-- The remaining Hadamard reduction can use any proved uniform sublinear
log-norm bound for the normalized zero-free quotient. -/
theorem entire_zeroFree_sublinear_logNorm_eq_one {f : ℂ → ℂ}
    (hf : Differentiable ℂ f) (hn : ∀ z, f z ≠ 0) (h0 : f 0 = 1) {M : ℝ → ℝ}
    (hp : ∀ᶠ R in atTop, 0 < M R)
    (hM : Tendsto (fun R => M R / R) atTop (𝓝 0))
    (hb : ∀ᶠ R in atTop, ∀ w : ℂ, ‖w‖ < R → Real.log ‖f w‖ ≤ M R) :
    f = 1 := by
  obtain ⟨g, hg, hg0, he⟩ := entire_normalized_exists_log hf hn h0
  have hre : ∀ z, (g z).re = Real.log ‖f z‖ := by
    intro z
    rw [← he z, Complex.norm_exp, Real.log_exp]
  have hgzero : g = 0 := entire_realPart_sublinear_constant hg hg0 hp hM (by
    filter_upwards [hb] with R hR w hw
    rw [hre]
    exact hR w hw)
  funext z
  rw [← he z, hgzero]
  exact Complex.exp_zero

theorem entireReducedDenominator_product_quotient_has_log {N : ℕ} (hN : 2 ≤ N) :
    ∃ g : ℂ → ℂ, Differentiable ℂ g ∧ g 0 = 0 ∧
      ∀ z, Complex.exp (g z) * fullCanonicalProduct (entireReducedDenominator N) z = entireReducedDenominator N z := by
  obtain ⟨hd, hn, h0, he⟩ := entireReducedDenominator_product_quotient hN
  obtain ⟨g, hg, hg0, hgexp⟩ := entire_normalized_exists_log hd hn h0
  exact ⟨g, hg, hg0, fun z => by rw [hgexp, mul_comm]; exact he z⟩

end
end Komorebi.PaperIV
