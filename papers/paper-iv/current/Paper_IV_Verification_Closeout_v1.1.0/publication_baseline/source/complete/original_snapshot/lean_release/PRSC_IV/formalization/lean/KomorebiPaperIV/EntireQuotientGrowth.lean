/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SublinearExponentialRigidity
import Mathlib.Analysis.Complex.ValueDistribution.FirstMainTheorem
import Mathlib.Analysis.Complex.Harmonic.Poisson

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Metric Real ValueDistribution
open scoped Topology

theorem entire_logCounting_poles_zero {f : ℂ → ℂ} (hf : Differentiable ℂ f) :
    logCounting f ⊤ = 0 := by
  have ha : AnalyticOnNhd ℂ f univ := fun z _ => hf.analyticAt z
  rw [logCounting_top, negPart_eq_zero.mpr (MeromorphicOn.AnalyticOnNhd.divisor_nonneg ha)]
  simp

theorem entire_normalized_proximity_inv_le {f : ℂ → ℂ}
    (hf : Differentiable ℂ f) (h0 : f 0 = 1) {R : ℝ} (hR : 1 ≤ R) :
    proximity f⁻¹ ⊤ R ≤ proximity f ⊤ R := by
  have hm : Meromorphic f := fun z => (hf.analyticAt z).meromorphicAt
  have ht := (hf.analyticAt 0).meromorphicTrailingCoeffAt_of_ne_zero (by rw [h0]; exact one_ne_zero)
  have he := characteristic_sub_characteristic_inv_le (R := R) hm
  rw [ht, h0, norm_one, log_one, abs_zero, max_self] at he
  have heq := abs_nonpos_iff.mp he
  simp only [characteristic, Pi.add_apply, entire_logCounting_poles_zero hf, Pi.zero_apply, add_zero] at heq
  have hn := logCounting_nonneg (f := f⁻¹) (e := ⊤) hR
  linarith

theorem entire_eventually_codiscrete_ne_zero {f : ℂ → ℂ}
    (hf : Differentiable ℂ f) (h0 : f 0 ≠ 0) :
    ∀ᶠ z in codiscrete ℂ, f z ≠ 0 := by
  have hm : MeromorphicOn f univ := fun z _ => (hf.analyticAt z).meromorphicAt
  have hh := hm.eventually_codiscreteWithin_apply_ne_zero (fun z _ => ?_)
  · simpa only [Filter.codiscrete] using hh
  · rw [(hf.analyticAt z).meromorphicOrderAt_eq,
      ← Nat.cast_analyticOrderNatAt (entire_analyticOrderAt_ne_top (fun w => hf.analyticAt w) h0 z),
      ENat.map_natCast]
    exact WithTop.coe_ne_top

/-- Jensen's formula controls a normalized entire quotient using only upper
growth of numerator and denominator, including circles through their zeros. -/
theorem entire_quotient_proximity_le {f P Q : ℂ → ℂ}
    (hf : Differentiable ℂ f) (hP : Differentiable ℂ P)
    (hP0 : P 0 = 1) (he : ∀ z, P z * Q z = f z)
    {R : ℝ} (hR : 1 ≤ R) :
    proximity Q ⊤ R ≤ proximity f ⊤ R + proximity P ⊤ R := by
  have hm : Meromorphic f := fun z => (hf.analyticAt z).meromorphicAt
  have hp : Meromorphic P := fun z => (hP.analyticAt z).meromorphicAt
  have heq : Q =ᶠ[codiscrete ℂ] f * P⁻¹ := by
    filter_upwards [entire_eventually_codiscrete_ne_zero hP (by rw [hP0]; exact one_ne_zero)] with z hz
    change Q z = f z * (P z)⁻¹
    rw [← he z]
    field_simp
  rw [proximity_congr_codiscrete heq (by linarith)]
  exact (proximity_mul_top_le hm hp.inv R).trans
    (add_le_add_right (entire_normalized_proximity_inv_le hP hP0 hR) _)

/-- A Poisson-kernel estimate on the half-radius disk. -/
theorem entire_re_le_three_proximity_exp {g : ℂ → ℂ} (hg : Differentiable ℂ g)
    {R : ℝ} (hR : 0 < R) {z : ℂ} (hz : ‖z‖ < R / 2) :
    (g z).re ≤ 3 * proximity (fun w => Complex.exp (g w)) ⊤ R := by
  let K : ℂ → ℝ := fun w => (herglotzRieszKernel 0 z w).re
  have hzR : z ∈ ball (0 : ℂ) R := by
    rw [mem_ball_zero_iff]; linarith
  have hK : ContinuousOn K (sphere 0 |R|) :=
    Complex.continuous_re.comp_continuousOn
      (continuousOn_herglotzRieszKernel_sphere (by
        rw [abs_of_pos hR, mem_sphere_zero_iff_norm]; intro heq; linarith))
  have hh : InnerProductSpace.HarmonicOnNhd (fun w => (g w).re) (closedBall 0 R) :=
    fun w _ => (hg.analyticAt w).harmonicAt_re
  have he := hh.circleAverage_re_herglotzRieszKernel_smul hzR
  change circleAverage (fun w => K w * (g w).re) 0 R = (g z).re at he
  have hi : CircleIntegrable (fun w => K w * (g w).re) 0 R :=
    (hK.mul (Complex.continuous_re.comp hg.continuous).continuousOn).circleIntegrable'
  have hj : CircleIntegrable (fun w => 3 * max 0 (g w).re) 0 R := by
    exact (continuous_const.mul (continuous_const.max (Complex.continuous_re.comp hg.continuous))).continuousOn.circleIntegrable'
  have hm := circleAverage_mono hi hj (fun w hw => ?_)
  · rw [he] at hm
    simpa only [proximity_top, Complex.norm_exp, posLog, log_exp,
      ← smul_eq_mul, circleAverage_fun_smul] using hm
  · have hw' : w ∈ sphere (0 : ℂ) R := by rwa [abs_of_pos hR] at hw
    have hu := re_herglotzRieszKernel_le hw' hzR
    have hl := le_re_herglotzRieszKernel hw' hzR
    simp only [sub_zero] at hu hl
    have hd : 0 < R - ‖z‖ := by linarith
    have hk3 : K w ≤ 3 := by
      simpa only [K, herglotzRieszKernel, sub_zero] using
        hu.trans ((div_le_iff₀ hd).mpr (show R + ‖z‖ ≤ 3 * (R - ‖z‖) by linarith))
    have hk0 : 0 ≤ K w := by
      have hd2 : 0 ≤ R + ‖z‖ := by positivity
      simpa only [K, herglotzRieszKernel, sub_zero] using (div_nonneg hd.le hd2).trans hl
    exact (mul_le_mul_of_nonneg_left (le_max_right 0 _) hk0).trans
      (mul_le_mul_of_nonneg_right hk3 (le_max_left 0 _))

theorem entire_proximity_le_of_growth {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    {R B : ℝ} (hB : 0 ≤ B) (hb : ∀ z ∈ sphere (0 : ℂ) |R|, ‖f z‖ ≤ exp B) :
    proximity f ⊤ R ≤ B := by
  rw [proximity_top]
  apply circleAverage_mono_on_of_le_circle
    ((show MeromorphicOn f (sphere 0 |R|) from fun z _ => (hf.analyticAt z).meromorphicAt).circleIntegrable_posLog_norm)
  intro z hz
  rw [posLog, max_le_iff]
  refine ⟨hB, ?_⟩
  by_cases h : f z = 0
  · simpa [h] using hB
  · exact (log_le_iff_le_exp (norm_pos_iff.mpr h)).mpr (hb z hz)

/-- Sublinear growth of two entire factors eliminates a normalized exponential
factor. All estimates are derived from circle means, even when a circle meets zeros. -/
theorem entire_sublinear_factor_rigidity {f P g : ℂ → ℂ}
    (hf : Differentiable ℂ f) (hP : Differentiable ℂ P) (hg : Differentiable ℂ g)
    (hP0 : P 0 = 1) (hg0 : g 0 = 0)
    (he : ∀ z, P z * Complex.exp (g z) = f z)
    {C s : ℝ} (hC : 0 ≤ C) (hs : s < 1)
    (hbound : ∀ R : ℝ, 1 ≤ R → ∀ z : ℂ, ‖z‖ ≤ R →
      ‖f z‖ ≤ exp (C * R ^ s) ∧ ‖P z‖ ≤ exp (C * R ^ s)) : g = 0 := by
  let M : ℝ → ℝ := fun R => 1 + 6 * C * (2 * R) ^ s
  apply entire_realPart_sublinear_constant hg hg0 (M := M)
  · filter_upwards [eventually_ge_atTop (1 : ℝ)] with R hR
    dsimp [M]
    positivity
  · have ht : Tendsto (fun R : ℝ => R ^ (s - 1)) atTop (𝓝 0) := by
      simpa only [neg_sub] using tendsto_rpow_neg_atTop (show 0 < 1 - s by linarith)
    have heq : (fun R => M R / R) =ᶠ[atTop]
        (fun R => R⁻¹ + (6 * C * (2 : ℝ) ^ s) * R ^ (s - 1)) := by
      filter_upwards [eventually_gt_atTop (0 : ℝ)] with R hR
      dsimp [M]
      rw [Real.mul_rpow (by norm_num) hR.le, Real.rpow_sub hR, Real.rpow_one]
      ring
    have hlim : Tendsto (fun R : ℝ => R⁻¹ + (6 * C * (2 : ℝ) ^ s) * R ^ (s - 1)) atTop (𝓝 0) := by
      simpa only [mul_zero, add_zero] using tendsto_inv_atTop_zero.add (ht.const_mul (6 * C * (2 : ℝ) ^ s))
    exact hlim.congr' heq.symm
  · filter_upwards [eventually_ge_atTop (1 : ℝ)] with R hR z hz
    have hR0 : 0 < R := by linarith
    have h2R : 1 ≤ 2 * R := by linarith
    have hzb : ‖z‖ < (2 * R) / 2 := by linarith
    have hgrowth := entire_re_le_three_proximity_exp hg (by linarith : 0 < 2 * R) hzb
    have hp := entire_quotient_proximity_le hf hP hP0 he h2R
    have hb : 0 ≤ C * (2 * R) ^ s := mul_nonneg hC (Real.rpow_nonneg (by linarith) _)
    have hbF := entire_proximity_le_of_growth hf (R := 2 * R) hb (fun w hw => ?_)
    have hbP := entire_proximity_le_of_growth hP (R := 2 * R) hb (fun w hw => ?_)
    · dsimp [M]
      linarith
    all_goals
      rw [abs_of_pos (by linarith : 0 < 2 * R), mem_sphere_zero_iff_norm] at hw
      first | exact (hbound (2 * R) h2R w hw.le).1 | exact (hbound (2 * R) h2R w hw.le).2

end
end Komorebi.PaperIV
