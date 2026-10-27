import KomorebiPaperVI.ComplexSemigroups

/-! Author: Komorebi P. Fractional semigroup refinement between distinct Hilbert spaces. -/
namespace KomorebiPaperVI.RectangularSemigroup
open Set MeasureTheory
open scoped NNReal
open KomorebiPaperVI.RectangularFractional KomorebiPaperVI.Semigroups
set_option backward.isDefEq.respectTransparency false
attribute [local instance] IsStarNormal.instContinuousFunctionalCalculus
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E] [CompleteSpace E]
    [NormedAddCommGroup F] [InnerProductSpace ℂ F] [CompleteSpace F]

noncomputable def evolution (A : E →L[ℂ] E) (p : ℝ≥0) (t : ℝ) : E →L[ℂ] E :=
  transfer (-power A p) t

noncomputable def timeDefect (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F)
    (p : ℝ≥0) (t : ℝ) : E →L[ℂ] F := C.comp (evolution A p t)-(evolution B p t).comp C

theorem evolution_exponential (A : E →L[ℂ] E) (p : ℝ≥0) (t : ℝ) :
    evolution A p t=NormedSpace.exp ((-t) • power A p) := by
  simp [evolution,transfer,smul_neg,neg_smul]

theorem evolution_cfc (A : E →L[ℂ] E) (p : ℝ≥0) (hp : 0 < p) (t : ℝ) :
    evolution A p t=FractionalSemigroup.evolution A p t := by
  rw [evolution_exponential]
  unfold power FractionalSemigroup.evolution FractionalSemigroup.power
  congr 2
  exact CFC.nnrpow_eq_rpow hp

theorem contraction (A : E →L[ℂ] E) (hA : 0 ≤ A) (p : ℝ≥0) (hp : 0 < p)
    (t : ℝ) (ht : 0 ≤ t) : ‖evolution A p t‖ ≤ 1 := by
  rw [evolution_cfc A p hp t]
  exact FractionalSemigroup.exponential_contraction A hA p t hp ht

theorem gap_decay (A : E →L[ℂ] E) (hA : 0 ≤ A) (p : ℝ≥0) (hp : 0 < p)
    (t m : ℝ) (ht : 0 ≤ t) (hm : 0 ≤ m) (hgA : algebraMap ℝ (E →L[ℂ] E) m ≤ A) :
    ‖evolution A p t‖ ≤ Real.exp (-t*m^(p:ℝ)) := by
  rw [evolution_cfc A p hp t]
  exact FractionalSemigroup.exponential_gap A hA p t m hp ht hm hgA

theorem fractional_duhamel (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F)
    (p : ℝ≥0) (t : ℝ) :
    timeDefect A B C p t= -(∫ r in 0..t,(evolution B p (t-r)).comp
      ((fractionalDefect A B C p).comp (evolution A p r))) := by
  unfold timeDefect evolution
  rw [ComplexSemigroups.duhamel_rectangular]
  have he : C.comp (-power A p)-(-power B p).comp C= -fractionalDefect A B C p := by
    simp only [fractionalDefect,ContinuousLinearMap.comp_neg,ContinuousLinearMap.neg_comp]
    abel
  rw [he]
  simp only [ContinuousLinearMap.neg_comp,ContinuousLinearMap.comp_neg,intervalIntegral.integral_neg]

theorem fractional_contraction_bound (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F)
    (hA : 0 ≤ A) (hB : 0 ≤ B) (p : ℝ≥0) (hp : 0 < p) (t : ℝ) (ht : 0 ≤ t) :
    ‖timeDefect A B C p t‖ ≤ t*‖fractionalDefect A B C p‖ := by
  have h := ComplexSemigroups.contraction_duhamel_bound (-power A p) (-power B p) C t ht
    (fun r hr => contraction A hA p hp r hr) (fun r hr => contraction B hB p hp r hr)
  have he : C.comp (-power A p)-(-power B p).comp C= -fractionalDefect A B C p := by
    simp only [fractionalDefect,ContinuousLinearMap.comp_neg,ContinuousLinearMap.neg_comp]
    abel
  simpa only [timeDefect,evolution,he,norm_neg] using h

theorem fractional_gap_bound (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F)
    (hA : 0 ≤ A) (hB : 0 ≤ B) (p : ℝ≥0) (hp : 0 < p) (t m : ℝ) (ht : 0 ≤ t) (hm : 0 ≤ m)
    (hgA : algebraMap ℝ (E →L[ℂ] E) m ≤ A) (hgB : algebraMap ℝ (F →L[ℂ] F) m ≤ B) :
    ‖timeDefect A B C p t‖ ≤ t*Real.exp (-t*m^(p:ℝ))*‖fractionalDefect A B C p‖ := by
  rw [fractional_duhamel,norm_neg]
  have hc : Continuous (fun r => (evolution B p (t-r)).comp
      ((fractionalDefect A B C p).comp (evolution A p r))) := by
    unfold evolution
    fun_prop
  calc
    _ ≤ ∫ r in 0..t,‖(evolution B p (t-r)).comp ((fractionalDefect A B C p).comp (evolution A p r))‖ :=
      intervalIntegral.norm_integral_le_integral_norm ht
    _ ≤ ∫ _ in 0..t,Real.exp (-t*m^(p:ℝ))*‖fractionalDefect A B C p‖ := by
      apply intervalIntegral.integral_mono_on ht (hc.norm.intervalIntegrable 0 t) intervalIntegrable_const
      intro r hr
      calc
        _ ≤ ‖evolution B p (t-r)‖*(‖fractionalDefect A B C p‖*‖evolution A p r‖) :=
          (ContinuousLinearMap.opNorm_comp_le _ _).trans
            (mul_le_mul_of_nonneg_left (ContinuousLinearMap.opNorm_comp_le _ _) (norm_nonneg _))
        _ ≤ Real.exp (-(t-r)*m^(p:ℝ))*(‖fractionalDefect A B C p‖*Real.exp (-r*m^(p:ℝ))) := by
          gcongr
          · exact gap_decay B hB p hp (t-r) m (by linarith [hr.2]) hm hgB
          · exact gap_decay A hA p hp r m hr.1 hm hgA
        _ = _ := by
          rw [← mul_assoc,mul_right_comm,← Real.exp_add]
          congr 2
          ring
    _ = _ := by
      simp only [intervalIntegral.integral_const,sub_zero,smul_eq_mul]
      ring

theorem generator_gap_bound (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F)
    (hA : 0 ≤ A) (hB : 0 ≤ B) (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1) (t m : ℝ) (ht : 0 ≤ t) (hm : 0 < m)
    (hgA : algebraMap ℝ (E →L[ℂ] E) m ≤ A) (hgB : algebraMap ℝ (F →L[ℂ] F) m ≤ B) :
    ‖timeDefect A B C p t‖ ≤ t*Real.exp (-t*m^(p:ℝ))*(p:ℝ)*m^((p:ℝ)-1)*‖defect A B C‖ := by
  calc
    _ ≤ t*Real.exp (-t*m^(p:ℝ))*‖fractionalDefect A B C p‖ :=
      fractional_gap_bound A B C hA hB p hp.1 t m ht hm.le hgA hgB
    _ ≤ t*Real.exp (-t*m^(p:ℝ))*((p:ℝ)*m^((p:ℝ)-1)*‖defect A B C‖) :=
      mul_le_mul_of_nonneg_left (common_gap_estimate p hp m hm A B C hA hB hgA hgB) (by positivity)
    _ = _ := by ring

end KomorebiPaperVI.RectangularSemigroup
