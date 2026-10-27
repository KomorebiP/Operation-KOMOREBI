import KomorebiPaperVI.Semigroups

/-! Author: Komorebi P. General growth and finite-horizon contraction bounds. -/
namespace KomorebiPaperVI.OperatorBounds
open KomorebiPaperVI.Semigroups
open scoped BigOperators
variable {E F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
    [NormedAddCommGroup F] [NormedSpace ℝ F] [CompleteSpace F]

theorem growth_duhamel_bound (A : E →L[ℝ] E) (B : F →L[ℝ] F) (C : E →L[ℝ] F)
    (Mf Mc wf wc t : ℝ) (ht : 0 ≤ t)
    (hA : ∀ u, 0 ≤ u → ‖transfer A u‖ ≤ Mf*Real.exp (wf*u))
    (hB : ∀ u, 0 ≤ u → ‖transfer B u‖ ≤ Mc*Real.exp (wc*u)) :
    ‖C.comp (transfer A t)-(transfer B t).comp C‖ ≤
      Mf*Mc*‖C.comp A-B.comp C‖ * ∫ r in 0..t, Real.exp (wc*(t-r))*Real.exp (wf*r) := by
  let D := C.comp A-B.comp C
  let f := fun r => (transfer B (t-r)).comp (D.comp (transfer A r))
  let g := fun r => Mf*Mc*‖D‖*(Real.exp (wc*(t-r))*Real.exp (wf*r))
  have hf : Continuous f := by dsimp [f]; fun_prop
  have hg : Continuous g := by dsimp [g]; fun_prop
  rw [duhamel_rectangular]
  change ‖∫ r in 0..t, f r‖ ≤ _
  calc
    _ ≤ ∫ r in 0..t, ‖f r‖ := intervalIntegral.norm_integral_le_integral_norm ht
    _ ≤ ∫ r in 0..t, g r := by
      apply intervalIntegral.integral_mono_on ht (hf.norm.intervalIntegrable 0 t) (hg.intervalIntegrable 0 t)
      intro r hr
      have ha := hA r hr.1
      have hb := hB (t-r) (sub_nonneg.mpr hr.2)
      calc
        _ ≤ ‖transfer B (t-r)‖*‖D.comp (transfer A r)‖ := ContinuousLinearMap.opNorm_comp_le _ _
        _ ≤ (Mc*Real.exp (wc*(t-r)))*(‖D‖*(Mf*Real.exp (wf*r))) :=
          mul_le_mul hb ((ContinuousLinearMap.opNorm_comp_le _ _).trans
            (mul_le_mul_of_nonneg_left ha (norm_nonneg _)))
            (norm_nonneg _) ((norm_nonneg _).trans hb)
        _ = g r := by dsimp [g]; ring
    _ = _ := by dsimp [g,D]; rw [intervalIntegral.integral_const_mul]

omit [CompleteSpace E] in
theorem contraction_powers (A : E →L[ℝ] E) (hA : ‖A‖ ≤ 1) (n : ℕ) : ‖A^n‖ ≤ 1 := by
  induction n with
  | zero =>
    simp only [pow_zero]
    exact ContinuousLinearMap.norm_id_le
  | succ n ih =>
    rw [pow_succ]
    exact (norm_mul_le _ _).trans (by nlinarith [norm_nonneg (A^n),norm_nonneg A])

omit [CompleteSpace E] [CompleteSpace F] in
theorem finite_horizon_contraction (A : E →L[ℝ] E) (B : F →L[ℝ] F) (C : E →L[ℝ] F)
    (hA : ‖A‖ ≤ 1) (hB : ‖B‖ ≤ 1) (n : ℕ) :
    ‖C.comp (A^n)-(B^n).comp C‖ ≤ (n:ℝ)*‖C.comp A-B.comp C‖ := by
  induction n with
  | zero => simp [ContinuousLinearMap.one_def]
  | succ n ih =>
    have he : C.comp (A^(n+1))-(B^(n+1)).comp C =
        B.comp (C.comp (A^n)-(B^n).comp C)+(C.comp A-B.comp C).comp (A^n) := by
      ext x
      simp [pow_succ', mul_apply_eq_comp, ContinuousLinearMap.comp_apply]
    rw [he]
    calc
      _ ≤ ‖B.comp (C.comp (A^n)-(B^n).comp C)‖+
          ‖(C.comp A-B.comp C).comp (A^n)‖ := norm_add_le _ _
      _ ≤ 1*((n:ℝ)*‖C.comp A-B.comp C‖)+‖C.comp A-B.comp C‖*1 := by
        apply add_le_add
        · exact (ContinuousLinearMap.opNorm_comp_le _ _).trans
            (mul_le_mul hB ih (norm_nonneg _) (by norm_num))
        · exact (ContinuousLinearMap.opNorm_comp_le _ _).trans
            (mul_le_mul_of_nonneg_left (contraction_powers A hA n) (norm_nonneg _))
      _ = _ := by push_cast; ring

end KomorebiPaperVI.OperatorBounds
