/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroZetaConvergence
import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics
import Mathlib.Topology.Algebra.InfiniteSum.TsumUniformlyOn

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Metric
open scoped Topology

def positiveZetaTerm (r : ℝ) (s : ℂ) : ℂ := Complex.exp (-s * (Real.log r : ℂ))

def exponentialZetaDifference (x y : ℕ → ℝ) (m : ℕ) (s : ℂ) : ℂ :=
  positiveZetaTerm (x m) s - positiveZetaTerm (y m) s

theorem positiveZetaTerm_entire (r : ℝ) : Differentiable ℂ (positiveZetaTerm r) := by
  unfold positiveZetaTerm
  fun_prop

theorem exponentialZetaDifference_entire (x y : ℕ → ℝ) (m : ℕ) :
    Differentiable ℂ (exponentialZetaDifference x y m) :=
  (positiveZetaTerm_entire _).sub (positiveZetaTerm_entire _)

theorem real_log_lipschitz_one {x y : ℝ} (hx : 1 ≤ x) (hy : 1 ≤ y) :
    |Real.log x - Real.log y| ≤ |x - y| := by
  have h := (convex_Ici (1 : ℝ)).norm_image_sub_le_of_norm_deriv_le
    (f := Real.log) (C := 1)
    (fun u hu => Real.differentiableAt_log (by change 1 ≤ u at hu; linarith))
    (fun u hu => by
      rw [Real.deriv_log, Real.norm_eq_abs, abs_of_pos (inv_pos.mpr (by change 1 ≤ u at hu; linarith))]
      exact inv_le_one_of_one_le₀ hu) hy hx
  simpa only [one_mul, Real.norm_eq_abs] using h

theorem positiveZetaTerm_norm_le_rpow {y K : ℝ} (hy : 1 ≤ y) {s : ℂ} (hs : ‖s‖ ≤ K) :
    ‖positiveZetaTerm y s‖ ≤ y ^ K := by
  rw [positiveZetaTerm, Complex.norm_exp]
  simp only [Complex.mul_re, Complex.neg_re, Complex.neg_im, Complex.ofReal_re,
    Complex.ofReal_im, mul_zero, sub_zero]
  rw [Real.rpow_def_of_pos (by linarith : 0 < y)]
  apply Real.exp_le_exp.mpr
  have hre : -s.re ≤ K := (neg_le_abs _).trans ((Complex.abs_re_le_norm s).trans hs)
  have hl : 0 ≤ Real.log y := Real.log_nonneg hy
  nlinarith

theorem exponentialZetaDifference_factor (x y : ℝ) (s : ℂ) :
    positiveZetaTerm x s - positiveZetaTerm y s = positiveZetaTerm y s *
      (Complex.exp (-s * ((Real.log x - Real.log y : ℝ) : ℂ)) - 1) := by
  unfold positiveZetaTerm
  rw [mul_sub, ← Complex.exp_add, mul_one]
  congr 2
  push_cast
  ring

theorem summable_polynomial_exponential {y : ℕ → ℝ} (hy : ∀ m, 0 < y m)
    (ht : Tendsto y atTop atTop) (hs : Summable (fun m => 1 / y m ^ (2 : ℝ)))
    (K : ℝ) {γ : ℝ} (hγ : 0 < γ) :
    Summable (fun m => y m ^ K * Real.exp (-γ * y m)) := by
  have h := (tendsto_rpow_mul_exp_neg_mul_atTop_nhds_zero (K + 2) γ hγ).comp ht
  have hb := h.eventually (eventually_le_nhds (by norm_num : (0 : ℝ) < 1))
  apply hs.of_norm_bounded_eventually_nat
  filter_upwards [hb] with m hm
  rw [Real.norm_eq_abs, abs_of_nonneg (mul_nonneg (Real.rpow_nonneg (hy m).le _) (Real.exp_pos _).le)]
  apply (le_div_iff₀ (Real.rpow_pos_of_pos (hy m) 2)).mpr
  rw [Function.comp_apply, Real.rpow_add (hy m)] at hm
  nlinarith

/-- A summable majorant uniform on each bounded set of complex parameters.
The finitely many early indices are handled by the cofinite Weierstrass test. -/
theorem exponentialZetaDifference_majorant {x y : ℕ → ℝ}
    (hy : ∀ m, 0 < y m) (hxT : Tendsto x atTop atTop) (hyT : Tendsto y atTop atTop)
    (hs : Summable (fun m => 1 / y m ^ (2 : ℝ)))
    {C γ : ℝ} (_hC : 0 < C) (hγ : 0 < γ)
    (hclose : ∀ᶠ m in atTop, |x m - y m| ≤ C * Real.exp (-γ * y m))
    {K : ℝ} (hK : 0 < K) :
    ∃ u : ℕ → ℝ, Summable u ∧ ∀ᶠ m in atTop, ∀ s : ℂ, ‖s‖ ≤ K →
      ‖exponentialZetaDifference x y m s‖ ≤ u m := by
  let u := fun m => (2 * K * C) * (y m ^ K * Real.exp (-γ * y m))
  have hu : Summable u := (summable_polynomial_exponential hy hyT hs K hγ).mul_left _
  have ht := hyT.const_mul_atTop_of_neg (neg_lt_zero.mpr hγ)
  have he := (Real.tendsto_exp_atBot.comp ht).const_mul (K * C)
  simp only [mul_zero] at he
  have hsmall := he.eventually (eventually_le_nhds (by norm_num : (0 : ℝ) < 1))
  refine ⟨u, hu, ?_⟩
  filter_upwards [hxT.eventually_ge_atTop 1, hyT.eventually_ge_atTop 1, hclose, hsmall]
    with m hxm hym hcm hsm
  intro s hsmK
  have hl : |Real.log (x m) - Real.log (y m)| ≤ C * Real.exp (-γ * y m) :=
    (real_log_lipschitz_one hxm hym).trans hcm
  have hz : ‖-s * ((Real.log (x m) - Real.log (y m) : ℝ) : ℂ)‖ ≤
      K * (C * Real.exp (-γ * y m)) := by
    rw [norm_mul, norm_neg, Complex.norm_real, Real.norm_eq_abs]
    exact mul_le_mul hsmK hl (abs_nonneg _) hK.le
  have hz1 : ‖-s * ((Real.log (x m) - Real.log (y m) : ℝ) : ℂ)‖ ≤ 1 := by
    apply hz.trans
    simpa only [Function.comp_apply, mul_assoc] using hsm
  have hb := (Complex.norm_exp_sub_one_le hz1).trans (mul_le_mul_of_nonneg_left hz (by norm_num))
  rw [exponentialZetaDifference, exponentialZetaDifference_factor, norm_mul]
  calc
    _ ≤ y m ^ K * (2 * (K * (C * Real.exp (-γ * y m)))) :=
      mul_le_mul (positiveZetaTerm_norm_le_rpow hym hsmK) hb (norm_nonneg _)
        (Real.rpow_nonneg (hy m).le _)
    _ = u m := by dsimp [u]; ring

theorem exponentialZetaDifference_locally_uniform {x y : ℕ → ℝ}
    (hy : ∀ m, 0 < y m) (hxT : Tendsto x atTop atTop) (hyT : Tendsto y atTop atTop)
    (hs : Summable (fun m => 1 / y m ^ (2 : ℝ)))
    {C γ : ℝ} (hC : 0 < C) (hγ : 0 < γ)
    (hclose : ∀ᶠ m in atTop, |x m - y m| ≤ C * Real.exp (-γ * y m)) :
    HasSumLocallyUniformlyOn (exponentialZetaDifference x y)
      (fun s => ∑' m, exponentialZetaDifference x y m s) univ := by
  apply hasSumLocallyUniformlyOn_of_of_forall_exists_nhds
  intro s _
  obtain ⟨u, hu, hbound⟩ := exponentialZetaDifference_majorant hy hxT hyT hs hC hγ hclose
    (show 0 < ‖s‖ + 1 by positivity)
  refine ⟨ball 0 (‖s‖ + 1), mem_nhdsWithin_of_mem_nhds
    (isOpen_ball.mem_nhds (by simp only [mem_ball, dist_zero_right]; linarith)), ?_⟩
  apply HasSumUniformlyOn.of_norm_le_summable_eventually hu
  rw [Nat.cofinite_eq_atTop]
  filter_upwards [hbound] with m hm
  intro z hz
  exact hm z (le_of_lt (by simpa only [mem_ball, dist_zero_right] using hz))

theorem exponentialZetaDifference_sum_entire {x y : ℕ → ℝ}
    (hy : ∀ m, 0 < y m) (hxT : Tendsto x atTop atTop) (hyT : Tendsto y atTop atTop)
    (hs : Summable (fun m => 1 / y m ^ (2 : ℝ)))
    {C γ : ℝ} (hC : 0 < C) (hγ : 0 < γ)
    (hclose : ∀ᶠ m in atTop, |x m - y m| ≤ C * Real.exp (-γ * y m)) :
    Differentiable ℂ (fun s => ∑' m, exponentialZetaDifference x y m s) := by
  apply differentiableOn_univ.mp
  exact (exponentialZetaDifference_locally_uniform hy hxT hyT hs hC hγ hclose).summableLocallyUniformlyOn.differentiableOn isOpen_univ
    (fun m s _ => exponentialZetaDifference_entire x y m s)

end
end Komorebi.PaperIV
