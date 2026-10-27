import KomorebiPaperVI.Semigroups
import KomorebiPaperVI.FractionalSemigroup
import KomorebiPaperVI.RectangularFractional

/-! Author: Komorebi P. Real-time Duhamel for bounded complex linear maps. -/
set_option backward.isDefEq.respectTransparency false
namespace KomorebiPaperVI.ComplexSemigroups
open KomorebiPaperVI.Semigroups

variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E] [CompleteSpace E]
    [NormedAddCommGroup F] [InnerProductSpace ℂ F] [CompleteSpace F]

theorem duhamel_integrand_derivative (A : E →L[ℂ] E) (B : F →L[ℂ] F)
    (C : E →L[ℂ] F) (t r : ℝ) :
    HasDerivAt (fun u => (transfer B (t-u)).comp (C.comp (transfer A u)))
      ((transfer B (t-r)).comp ((C.comp A-B.comp C).comp (transfer A r))) r := by
  have hb : HasDerivAt (fun u => transfer B (t-u)) (-(transfer B (t-r)*B)) r := by
    simpa [Function.comp_def] using (transfer_derivative_right B (t-r)).scomp r
      ((hasDerivAt_const r t).sub (hasDerivAt_id r))
  have hc := ((ContinuousLinearMap.compL ℂ E E F).bilinearRestrictScalars ℝ).hasDerivAt_of_bilinear
    (fun _ => hasDerivAt_const r C) (fun _ => transfer_derivative_left A r)
  have hh := ((ContinuousLinearMap.compL ℂ E F F).bilinearRestrictScalars ℝ).hasDerivAt_of_bilinear
    (fun _ => hb) (fun _ => hc)
  convert! hh using 1
  ext x
  simp [mul_apply_eq_comp, ContinuousLinearMap.comp_apply]
  abel

theorem duhamel_rectangular (A : E →L[ℂ] E) (B : F →L[ℂ] F)
    (C : E →L[ℂ] F) (t : ℝ) :
    C.comp (transfer A t)-(transfer B t).comp C =
      ∫ r in 0..t, (transfer B (t-r)).comp ((C.comp A-B.comp C).comp (transfer A r)) := by
  have hc : Continuous (fun r => (transfer B (t-r)).comp
      ((C.comp A-B.comp C).comp (transfer A r))) := by
    fun_prop
  have h := intervalIntegral.integral_eq_sub_of_hasDerivAt
    (fun r _ => duhamel_integrand_derivative A B C t r) (hc.intervalIntegrable 0 t)
  simpa [transfer_zero, ContinuousLinearMap.one_def] using h.symm

theorem exact_rectangular_intertwining (A : E →L[ℂ] E) (B : F →L[ℂ] F)
    (C : E →L[ℂ] F) (h : C.comp A=B.comp C) (t : ℝ) :
    C.comp (transfer A t)=(transfer B t).comp C := by
  have hd := duhamel_rectangular A B C t
  simp only [h, sub_self, ContinuousLinearMap.zero_comp, ContinuousLinearMap.comp_zero,
    intervalIntegral.integral_zero] at hd
  exact sub_eq_zero.mp hd

theorem contraction_duhamel_bound (A : E →L[ℂ] E) (B : F →L[ℂ] F)
    (C : E →L[ℂ] F) (t : ℝ) (ht : 0 ≤ t)
    (hA : ∀ u, 0 ≤ u → ‖transfer A u‖ ≤ 1)
    (hB : ∀ u, 0 ≤ u → ‖transfer B u‖ ≤ 1) :
    ‖C.comp (transfer A t)-(transfer B t).comp C‖ ≤ t*‖C.comp A-B.comp C‖ := by
  rw [duhamel_rectangular]
  have h := intervalIntegral.norm_integral_le_of_norm_le_const (a := 0) (b := t)
    (C := ‖C.comp A-B.comp C‖)
    (f := fun r => (transfer B (t-r)).comp ((C.comp A-B.comp C).comp (transfer A r)))
    (fun r hr => ?_)
  · simpa [abs_of_nonneg ht, mul_comm] using h
  · have hr' : r ∈ Set.Ioc 0 t := by simpa [Set.uIoc_of_le ht] using hr
    calc
      _ ≤ ‖transfer B (t-r)‖ * ‖(C.comp A-B.comp C).comp (transfer A r)‖ :=
        ContinuousLinearMap.opNorm_comp_le _ _
      _ ≤ 1*(‖C.comp A-B.comp C‖*1) :=
        mul_le_mul (hB _ (sub_nonneg.mpr hr'.2))
          ((ContinuousLinearMap.opNorm_comp_le _ _).trans
            (mul_le_mul_of_nonneg_left (hA _ hr'.1.le) (norm_nonneg _)))
          (norm_nonneg _) (by norm_num)
      _ = _ := by ring

end KomorebiPaperVI.ComplexSemigroups
