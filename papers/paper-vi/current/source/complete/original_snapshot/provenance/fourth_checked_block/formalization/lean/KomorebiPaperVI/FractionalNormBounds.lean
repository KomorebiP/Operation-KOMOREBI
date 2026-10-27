import KomorebiPaperVI.FractionalResolvent
import KomorebiPaperVI.FractionalScalarBounds

/-! Author: Komorebi P. Norm estimates for the actual fractional resolvent defect. -/
namespace KomorebiPaperVI.FractionalNormBounds
open Set MeasureTheory Real
open KomorebiPaperVI.PositiveResolvent KomorebiPaperVI.NormalizedFractional KomorebiPaperVI.FractionalResolvent
open scoped NNReal
attribute [local instance] IsStarNormal.instContinuousFunctionalCalculus
set_option backward.isDefEq.respectTransparency false
variable {R : Type*} [CStarAlgebra R] [PartialOrder R] [StarOrderedRing R]

noncomputable def integrand (p t : ℝ) (A B C : R) : R :=
  t^p • (PositiveResolvent.resolvent B t*(C*A-B*C)*PositiveResolvent.resolvent A t)

theorem integrand_saturation (p t : ℝ) (hp : p∈Ioo 0 1) (ht : 0 < t) (A : R) (hA : 0 ≤ A) :
    cfcₙ (rpowIntegrand₀₁ p t) A=t^(p-1) • (A*PositiveResolvent.resolvent A t) := by
  have hc : ContinuousOn (fun x : ℝ => (t+x)⁻¹) (spectrum ℝ A) := by
    apply ContinuousOn.inv₀ (by fun_prop)
    exact fun x hx => (spectral_positive A hA t ht x hx).ne'
  rw [cfcₙ_eq_cfc (hf := (continuousOn_rpowIntegrand₀₁_Ici hp ht).mono (by grind)) (hf0 := by simp)]
  have he : cfc (rpowIntegrand₀₁ p t) A=cfc (fun x : ℝ => t^(p-1) • (x*(t+x)⁻¹)) A := by
    apply cfc_congr
    intro x hx
    rw [rpowIntegrand₀₁_eq_pow_div hp ht.le (spectrum_nonneg_of_nonneg hA hx)]
    simp only [smul_eq_mul,div_eq_mul_inv,mul_assoc]
  rw [he,cfc_smul (t^(p-1)) (fun x : ℝ => x*(t+x)⁻¹) A ((continuous_id.continuousOn).mul hc),← saturation_cfc A hA t ht]

theorem integrand_low_bound (p t : ℝ) (hp : p∈Ioo 0 1) (ht : 0 < t)
    (A B C : R) (hA : 0 ≤ A) (hB : 0 ≤ B) : ‖integrand p t A B C‖ ≤ 2*‖C‖*t^(p-1) := by
  rw [integrand,← integrand_defect p t hp ht A B C hA hB,
    integrand_saturation p t hp ht A hA,integrand_saturation p t hp ht B hB,
    Algebra.mul_smul_comm,Algebra.smul_mul_assoc,← smul_sub,norm_smul,
    Real.norm_of_nonneg (Real.rpow_nonneg ht.le _)]
  have ha := saturation_norm A hA t ht
  have hb := saturation_norm B hB t ht
  calc
    _ ≤ t^(p-1)*(‖C‖*‖A*PositiveResolvent.resolvent A t‖+‖B*PositiveResolvent.resolvent B t‖*‖C‖) := by
      gcongr
      exact (norm_sub_le _ _).trans (add_le_add (norm_mul_le _ _) (norm_mul_le _ _))
    _ ≤ t^(p-1)*(‖C‖*1+1*‖C‖) := by gcongr
    _ = _ := by ring

theorem integrand_gap_bound (p t m : ℝ) (ht : 0 < t) (hm : 0 ≤ m)
    (A B C : R) (hA : 0 ≤ A) (hB : 0 ≤ B)
    (hgA : algebraMap ℝ R m ≤ A) (hgB : algebraMap ℝ R m ≤ B) :
    ‖integrand p t A B C‖ ≤ ‖C*A-B*C‖*(t^p/(t+m)^2) := by
  rw [integrand,norm_smul,Real.norm_of_nonneg (Real.rpow_nonneg ht.le _)]
  calc
    _ ≤ t^p*(‖PositiveResolvent.resolvent B t‖*‖C*A-B*C‖*‖PositiveResolvent.resolvent A t‖) := by
      gcongr
      exact norm_mul_le_of_le (norm_mul_le _ _) le_rfl
    _ ≤ t^p*((t+m)⁻¹*‖C*A-B*C‖*(t+m)⁻¹) := by
      gcongr
      · exact resolvent_gap_norm B hB t m ht hm hgB
      · exact resolvent_gap_norm A hA t m ht hm hgA
    _ = _ := by
      have htm : t+m ≠ 0 := ne_of_gt (add_pos_of_pos_of_nonneg ht hm)
      field_simp [htm]

theorem integrand_high_bound (p t : ℝ) (ht : 0 < t)
    (A B C : R) (hA : 0 ≤ A) (hB : 0 ≤ B) :
    ‖integrand p t A B C‖ ≤ ‖C*A-B*C‖*t^(p-2) := by
  have h := integrand_gap_bound p t 0 ht le_rfl A B C hA hB (by simpa using hA) (by simpa using hB)
  simpa only [add_zero,Real.rpow_sub ht,Real.rpow_two] using h

theorem common_gap_estimate (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1) (m : ℝ) (hm : 0 < m)
    (A B C : R) (hA : 0 ≤ A) (hB : 0 ≤ B)
    (hgA : algebraMap ℝ R m ≤ A) (hgB : algebraMap ℝ R m ≤ B) :
    ‖C*CFC.nnrpow A p-CFC.nnrpow B p*C‖ ≤ (p:ℝ)*m^((p:ℝ)-1)*‖C*A-B*C‖ := by
  have hd := normalized_defect p hp A B C hA hB
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
    _ ≤ coefficient p*(∫ t in Ioi 0,‖integrand p t A B C‖) := by
      apply mul_le_mul_of_nonneg_left (norm_integral_le_integral_norm _) hk.le
    _ ≤ coefficient p*(∫ t in Ioi 0,‖C*A-B*C‖*(t^(p:ℝ)/(t+m)^2)) := by
      apply mul_le_mul_of_nonneg_left _ hk.le
      apply setIntegral_mono_on hd.1.norm (hg.const_mul _) measurableSet_Ioi
      intro t ht
      exact integrand_gap_bound p t m ht hm.le A B C hA hB hgA hgB
    _ = _ := by
      rw [integral_const_mul,mul_left_comm,coefficient,BetaNormalization.normalized_gap_integral p m hp hm]
      ring

noncomputable def holderConstant (p : ℝ) : ℝ := 2^(1-p)*coefficient p/(p*(1-p))

theorem holder_estimate (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (A B C : R) (hA : 0 ≤ A) (hB : 0 ≤ B) :
    ‖C*CFC.nnrpow A p-CFC.nnrpow B p*C‖ ≤
      holderConstant p*‖C‖^(1-(p:ℝ))*‖C*A-B*C‖^(p:ℝ) := by
  by_cases hc : C=0
  · subst C
    simp [Real.zero_rpow hp.1.ne']
  by_cases hd : C*A-B*C=0
  · have he := exact_fractional_intertwining p hp A B C hA hB (sub_eq_zero.mp hd)
    rw [he,sub_self,norm_zero,hd]
    simp [Real.zero_rpow hp.1.ne']
  have hcn : 0 < ‖C‖ := norm_pos_iff.mpr hc
  have hdn : 0 < ‖C*A-B*C‖ := norm_pos_iff.mpr hd
  have hf := normalized_defect p hp A B C hA hB
  have hk : 0 < coefficient p := BetaNormalization.sine_factor_positive p hp
  have hbound := FractionalScalarBounds.split_norm_bound (integrand p · A B C) p (2*‖C‖) ‖C*A-B*C‖
    (‖C*A-B*C‖/(2*‖C‖)) hp (by positivity) hf.1
    (fun t ht => integrand_low_bound p t hp ht A B C hA hB)
    (fun t ht => integrand_high_bound p t ht A B C hA hB)
  rw [FractionalScalarBounds.optimize_split p (2*‖C‖) ‖C*A-B*C‖ hp (by positivity) hdn] at hbound
  rw [hf.2,norm_smul,Real.norm_of_nonneg hk.le]
  calc
    _ ≤ coefficient p*((2*‖C‖)^(1-(p:ℝ))*‖C*A-B*C‖^(p:ℝ)/((p:ℝ)*(1-(p:ℝ)))) :=
      mul_le_mul_of_nonneg_left hbound hk.le
    _ = _ := by
      rw [Real.mul_rpow (by norm_num : (0:ℝ) ≤ 2) (norm_nonneg C)]
      unfold holderConstant
      ring

end KomorebiPaperVI.FractionalNormBounds
