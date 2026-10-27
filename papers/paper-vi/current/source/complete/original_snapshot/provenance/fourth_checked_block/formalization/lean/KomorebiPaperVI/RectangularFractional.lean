import KomorebiPaperVI.FractionalNormBounds
import Mathlib.Analysis.CStarAlgebra.ContinuousLinearMap
import Mathlib.Analysis.InnerProductSpace.StarOrder

/-! Author: Komorebi P. Fractional defects between distinct complex Hilbert spaces. -/
namespace KomorebiPaperVI.RectangularFractional
open Set MeasureTheory Real
open scoped NNReal
open KomorebiPaperVI.NormalizedFractional
attribute [local instance] IsStarNormal.instContinuousFunctionalCalculus
set_option backward.isDefEq.respectTransparency false
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E] [CompleteSpace E]
    [NormedAddCommGroup F] [InnerProductSpace ℂ F] [CompleteSpace F]

noncomputable def defect (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) : E →L[ℂ] F :=
  C.comp A-B.comp C
noncomputable def power (A : E →L[ℂ] E) (p : ℝ≥0) : E →L[ℂ] E := CFC.nnrpow A p
noncomputable def fractionalDefect (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) (p : ℝ≥0) : E →L[ℂ] F :=
  C.comp (power A p)-(power B p).comp C
noncomputable def integrand (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) (p t : ℝ) : E →L[ℂ] F :=
  C.comp (cfcₙ (rpowIntegrand₀₁ p t) A)-(cfcₙ (rpowIntegrand₀₁ p t) B).comp C

theorem normalized_integral (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) (hA : 0 ≤ A) (hB : 0 ≤ B) :
    IntegrableOn (integrand A B C p) (Ioi 0) ∧
      fractionalDefect A B C p=coefficient p • ∫ t in Ioi 0,integrand A B C p t := by
  have ha := cfc_lebesgue_integral p hp A hA
  have hb := cfc_lebesgue_integral p hp B hB
  let L := ContinuousLinearMap.compL ℂ E E F C
  let M := (ContinuousLinearMap.compL ℂ E F F).flip C
  have hl : IntegrableOn (fun t => C.comp (cfcₙ (rpowIntegrand₀₁ p t) A)) (Ioi 0) := L.integrable_comp ha.1
  have hr : IntegrableOn (fun t => (cfcₙ (rpowIntegrand₀₁ p t) B).comp C) (Ioi 0) := M.integrable_comp hb.1
  refine ⟨hl.sub hr,?_⟩
  unfold fractionalDefect power integrand
  rw [ha.2,hb.2,integral_sub hl hr]
  have hL := L.integral_comp_comm ha.1
  have hM := M.integral_comp_comm hb.1
  change (∫ t in Ioi 0,C.comp (cfcₙ (rpowIntegrand₀₁ p t) A))=C.comp (∫ t in Ioi 0,cfcₙ (rpowIntegrand₀₁ p t) A) at hL
  change (∫ t in Ioi 0,(cfcₙ (rpowIntegrand₀₁ p t) B).comp C)=(∫ t in Ioi 0,cfcₙ (rpowIntegrand₀₁ p t) B).comp C at hM
  rw [hL,hM,ContinuousLinearMap.comp_smul,ContinuousLinearMap.smul_comp,smul_sub]

theorem low_bound (p t : ℝ) (hp : p∈Ioo 0 1) (ht : 0 < t)
    (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) (hA : 0 ≤ A) (hB : 0 ≤ B) :
    ‖integrand A B C p t‖ ≤ 2*‖C‖*t^(p-1) := by
  unfold integrand
  rw [FractionalNormBounds.integrand_saturation p t hp ht A hA,
    FractionalNormBounds.integrand_saturation p t hp ht B hB,
    ContinuousLinearMap.comp_smul,ContinuousLinearMap.smul_comp,← smul_sub,norm_smul,
    Real.norm_of_nonneg (Real.rpow_nonneg ht.le _)]
  have ha := PositiveResolvent.saturation_norm A hA t ht
  have hb := PositiveResolvent.saturation_norm B hB t ht
  calc
    _ ≤ t^(p-1)*(‖C‖*‖A*PositiveResolvent.resolvent A t‖+‖B*PositiveResolvent.resolvent B t‖*‖C‖) := by
      gcongr
      exact (norm_sub_le _ _).trans (add_le_add (ContinuousLinearMap.opNorm_comp_le _ _) (ContinuousLinearMap.opNorm_comp_le _ _))
    _ ≤ t^(p-1)*(‖C‖*1+1*‖C‖) := by gcongr
    _ = _ := by ring

theorem resolvent_defect (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F)
    (hA : 0 ≤ A) (hB : 0 ≤ B) (t : ℝ) (ht : 0 < t) :
    (PositiveResolvent.resolvent B t).comp C-C.comp (PositiveResolvent.resolvent A t)=
      (PositiveResolvent.resolvent B t).comp ((defect A B C).comp (PositiveResolvent.resolvent A t)) := by
  let RA := PositiveResolvent.resolvent A t
  let RB := PositiveResolvent.resolvent B t
  have ha := PositiveResolvent.resolvent_left_inverse A hA t ht
  have hb := PositiveResolvent.resolvent_right_inverse B hB t ht
  ext x
  have hax := congrArg (fun T : E →L[ℂ] E => RB (C (T x))) ha
  have hbx := congrArg (fun T : F →L[ℂ] F => T (C (RA x))) hb
  simp only [Algebra.algebraMap_eq_smul_one,mul_apply_eq_comp,add_apply,
    smul_apply,one_apply_eq_self,map_add,ContinuousLinearMap.map_smul_of_tower] at hax hbx
  change RB (C x)-C (RA x)=RB (C (A (RA x))-B (C (RA x)))
  rw [map_sub]
  calc
    _ = (t • RB (C (RA x))+RB (C (A (RA x))))-
        (t • RB (C (RA x))+RB (B (C (RA x)))) := congrArg₂ (·-·) hax.symm hbx.symm
    _ = _ := by abel


theorem literal_integrand (p t : ℝ) (hp : p∈Ioo 0 1) (ht : 0 < t)
    (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) (hA : 0 ≤ A) (hB : 0 ≤ B) :
    integrand A B C p t=t^p • (PositiveResolvent.resolvent B t).comp
      ((defect A B C).comp (PositiveResolvent.resolvent A t)) := by
  rw [integrand,FractionalResolvent.cfc_integrand p t hp ht A hA,
    FractionalResolvent.cfc_integrand p t hp ht B hB,
    ContinuousLinearMap.comp_smul,ContinuousLinearMap.smul_comp,← smul_sub,
    ← resolvent_defect A B C hA hB t ht]
  congr 1
  ext x
  simp only [ContinuousLinearMap.comp_apply,sub_apply,map_sub,
    Algebra.algebraMap_eq_smul_one,smul_apply,one_apply_eq_self,
    ContinuousLinearMap.map_smul_of_tower]
  abel

theorem literal_resolvent_integral (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) (hA : 0 ≤ A) (hB : 0 ≤ B) :
    let f := fun t : ℝ => t^(p:ℝ) • (Ring.inverse (algebraMap ℝ (F →L[ℂ] F) t+B)).comp
      ((defect A B C).comp (Ring.inverse (algebraMap ℝ (E →L[ℂ] E) t+A)))
    IntegrableOn f (Ioi 0) ∧ fractionalDefect A B C p=coefficient p • ∫ t in Ioi 0,f t := by
  dsimp only
  have he : (fun t : ℝ => t^(p:ℝ) • (Ring.inverse (algebraMap ℝ (F →L[ℂ] F) t+B)).comp
      ((defect A B C).comp (Ring.inverse (algebraMap ℝ (E →L[ℂ] E) t+A))))
      =ᵐ[volume.restrict (Ioi 0)] integrand A B C p := by
    filter_upwards [ae_restrict_mem measurableSet_Ioi] with t ht
    rw [literal_integrand p t hp ht A B C hA hB,
      PositiveResolvent.resolvent_inverse A hA t ht,PositiveResolvent.resolvent_inverse B hB t ht]
  have h := normalized_integral p hp A B C hA hB
  exact ⟨h.1.congr he.symm,h.2.trans (congrArg (coefficient p • ·) (integral_congr_ae he.symm))⟩

theorem exact_fractional_intertwining (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) (hA : 0 ≤ A) (hB : 0 ≤ B)
    (hD : defect A B C=0) : fractionalDefect A B C p=0 := by
  rw [(normalized_integral p hp A B C hA hB).2]
  have he : integrand A B C p=ᵐ[volume.restrict (Ioi 0)] 0 := by
    filter_upwards [ae_restrict_mem measurableSet_Ioi] with t ht
    rw [literal_integrand p t hp ht A B C hA hB,hD]
    simp
  rw [integral_congr_ae he]
  simp

theorem gap_bound (p t m : ℝ) (ht : 0 < t) (hm : 0 ≤ m) (hp : p∈Ioo 0 1)
    (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) (hA : 0 ≤ A) (hB : 0 ≤ B)
    (hgA : algebraMap ℝ (E →L[ℂ] E) m ≤ A) (hgB : algebraMap ℝ (F →L[ℂ] F) m ≤ B) :
    ‖integrand A B C p t‖ ≤ ‖defect A B C‖*(t^p/(t+m)^2) := by
  rw [literal_integrand p t hp ht A B C hA hB,norm_smul,Real.norm_of_nonneg (Real.rpow_nonneg ht.le _)]
  calc
    _ ≤ t^p*(‖PositiveResolvent.resolvent B t‖*(‖defect A B C‖*‖PositiveResolvent.resolvent A t‖)) := by
      gcongr
      exact (ContinuousLinearMap.opNorm_comp_le _ _).trans
        (mul_le_mul_of_nonneg_left (ContinuousLinearMap.opNorm_comp_le _ _) (norm_nonneg _))
    _ ≤ t^p*((t+m)⁻¹*(‖defect A B C‖*(t+m)⁻¹)) := by
      gcongr
      · exact PositiveResolvent.resolvent_gap_norm B hB t m ht hm hgB
      · exact PositiveResolvent.resolvent_gap_norm A hA t m ht hm hgA
    _ = _ := by
      have htm : t+m ≠ 0 := ne_of_gt (add_pos_of_pos_of_nonneg ht hm)
      field_simp [htm]

theorem high_bound (p t : ℝ) (ht : 0 < t) (hp : p∈Ioo 0 1)
    (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) (hA : 0 ≤ A) (hB : 0 ≤ B) :
    ‖integrand A B C p t‖ ≤ ‖defect A B C‖*t^(p-2) := by
  have h := gap_bound p t 0 ht le_rfl hp A B C hA hB (by simpa using hA) (by simpa using hB)
  simpa only [add_zero,Real.rpow_sub ht,Real.rpow_two] using h

theorem common_gap_estimate (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1) (m : ℝ) (hm : 0 < m)
    (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) (hA : 0 ≤ A) (hB : 0 ≤ B)
    (hgA : algebraMap ℝ (E →L[ℂ] E) m ≤ A) (hgB : algebraMap ℝ (F →L[ℂ] F) m ≤ B) :
    ‖fractionalDefect A B C p‖ ≤ (p:ℝ)*m^((p:ℝ)-1)*‖defect A B C‖ := by
  have hd := normalized_integral p hp A B C hA hB
  have hk : 0 < coefficient p := BetaNormalization.sine_factor_positive p hp
  have hs : 0 < Real.sin (Real.pi*(p:ℝ)) := by
    apply Real.sin_pos_of_pos_of_lt_pi
    · exact mul_pos Real.pi_pos hp.1
    · nlinarith [Real.pi_pos,hp.2]
  have hg : IntegrableOn (fun t : ℝ => t^(p:ℝ)/(t+m)^2) (Ioi 0) := by
    by_contra hn
    have hz := integral_undef hn
    rw [BetaNormalization.gap_integral p m hp hm] at hz
    exact (mul_pos (Real.rpow_pos_of_pos hm _) (div_pos (mul_pos hp.1 Real.pi_pos) hs)).ne' hz
  rw [hd.2,norm_smul,Real.norm_of_nonneg hk.le]
  calc
    _ ≤ coefficient p*(∫ t in Ioi 0,‖integrand A B C p t‖) := by
      apply mul_le_mul_of_nonneg_left (norm_integral_le_integral_norm _) hk.le
    _ ≤ coefficient p*(∫ t in Ioi 0,‖defect A B C‖*(t^(p:ℝ)/(t+m)^2)) := by
      apply mul_le_mul_of_nonneg_left _ hk.le
      apply setIntegral_mono_on hd.1.norm (hg.const_mul _) measurableSet_Ioi
      intro t ht
      exact gap_bound p t m ht hm.le hp A B C hA hB hgA hgB
    _ = _ := by
      rw [integral_const_mul,mul_left_comm,coefficient,BetaNormalization.normalized_gap_integral p m hp hm]
      ring

theorem holder_estimate (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (A : E →L[ℂ] E) (B : F →L[ℂ] F) (C : E →L[ℂ] F) (hA : 0 ≤ A) (hB : 0 ≤ B) :
    ‖fractionalDefect A B C p‖ ≤
      FractionalNormBounds.holderConstant p*‖C‖^(1-(p:ℝ))*‖defect A B C‖^(p:ℝ) := by
  by_cases hc : C=0
  · subst C
    simp [fractionalDefect,defect,Real.zero_rpow hp.1.ne']
  by_cases hd : defect A B C=0
  · have he := exact_fractional_intertwining p hp A B C hA hB hd
    rw [he,norm_zero,hd]
    simp [Real.zero_rpow hp.1.ne']
  have hcn : 0 < ‖C‖ := norm_pos_iff.mpr hc
  have hdn : 0 < ‖defect A B C‖ := norm_pos_iff.mpr hd
  have hf := normalized_integral p hp A B C hA hB
  have hk : 0 < coefficient p := BetaNormalization.sine_factor_positive p hp
  have hbound := FractionalScalarBounds.split_norm_bound (integrand A B C p) p (2*‖C‖) ‖defect A B C‖
    (‖defect A B C‖/(2*‖C‖)) hp (by positivity) hf.1
    (fun t ht => low_bound p t hp ht A B C hA hB)
    (fun t ht => high_bound p t ht hp A B C hA hB)
  rw [FractionalScalarBounds.optimize_split p (2*‖C‖) ‖defect A B C‖ hp (by positivity) hdn] at hbound
  rw [hf.2,norm_smul,Real.norm_of_nonneg hk.le]
  calc
    _ ≤ coefficient p*((2*‖C‖)^(1-(p:ℝ))*‖defect A B C‖^(p:ℝ)/((p:ℝ)*(1-(p:ℝ)))) :=
      mul_le_mul_of_nonneg_left hbound hk.le
    _ = _ := by
      rw [Real.mul_rpow (by norm_num : (0:ℝ) ≤ 2) (norm_nonneg C)]
      unfold FractionalNormBounds.holderConstant
      ring

end KomorebiPaperVI.RectangularFractional
