import KomorebiPaperVI.NormalizedFractional
import KomorebiPaperVI.PositiveResolvent

/-! Author: Komorebi P. The actual normalized fractional resolvent-defect integral. -/
namespace KomorebiPaperVI.FractionalResolvent
open Set MeasureTheory Real
open KomorebiPaperVI.PositiveResolvent KomorebiPaperVI.NormalizedFractional
open scoped NNReal
attribute [local instance] IsStarNormal.instContinuousFunctionalCalculus
set_option backward.isDefEq.respectTransparency false
variable {R : Type*} [CStarAlgebra R] [PartialOrder R] [StarOrderedRing R]

theorem cfc_integrand (p t : ℝ) (hp : p∈Ioo 0 1) (ht : 0 < t) (A : R) (hA : 0 ≤ A) :
    cfcₙ (rpowIntegrand₀₁ p t) A=t^p • (algebraMap ℝ R t⁻¹-PositiveResolvent.resolvent A t) := by
  have hc : ContinuousOn (fun x : ℝ => (t+x)⁻¹) (spectrum ℝ A) := by
    apply ContinuousOn.inv₀ (by fun_prop)
    exact fun x hx => (spectral_positive A hA t ht x hx).ne'
  rw [cfcₙ_eq_cfc (hf := (continuousOn_rpowIntegrand₀₁_Ici hp ht).mono (by grind)) (hf0 := by simp)]
  unfold rpowIntegrand₀₁
  change cfc (fun x : ℝ => t^p • (t⁻¹-(t+x)⁻¹)) A= _
  rw [cfc_smul (t^p) (fun x : ℝ => t⁻¹-(t+x)⁻¹) A ((continuous_const.continuousOn).sub hc),
    cfc_sub (fun _ : ℝ => t⁻¹) (fun x : ℝ => (t+x)⁻¹) A (by fun_prop) hc,
    cfc_const t⁻¹ A hA.isSelfAdjoint]
  rfl

theorem integrand_defect (p t : ℝ) (hp : p∈Ioo 0 1) (ht : 0 < t)
    (A B C : R) (hA : 0 ≤ A) (hB : 0 ≤ B) :
    C*cfcₙ (rpowIntegrand₀₁ p t) A-cfcₙ (rpowIntegrand₀₁ p t) B*C=
      t^p • (PositiveResolvent.resolvent B t*(C*A-B*C)*PositiveResolvent.resolvent A t) := by
  rw [cfc_integrand p t hp ht A hA,cfc_integrand p t hp ht B hB]
  rw [Algebra.mul_smul_comm,Algebra.smul_mul_assoc,← smul_sub]
  congr 1
  rw [← resolvent_defect A B C hA hB t ht]
  have hc := Algebra.commutes (R := ℝ) (A := R) t⁻¹ C
  simp only [mul_sub,sub_mul,hc]
  abel

theorem normalized_defect (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (A B C : R) (hA : 0 ≤ A) (hB : 0 ≤ B) :
    IntegrableOn (fun t => t^(p:ℝ) • (PositiveResolvent.resolvent B t*(C*A-B*C)*PositiveResolvent.resolvent A t)) (Ioi 0) ∧
      C*CFC.nnrpow A p-CFC.nnrpow B p*C=coefficient p •
        ∫ t in Ioi 0,t^(p:ℝ) • (PositiveResolvent.resolvent B t*(C*A-B*C)*PositiveResolvent.resolvent A t) := by
  have hiA := cfc_lebesgue_integral p hp A hA
  have hiB := cfc_lebesgue_integral p hp B hB
  have hl : IntegrableOn (fun t => C*cfcₙ (rpowIntegrand₀₁ p t) A) (Ioi 0) :=
    (ContinuousLinearMap.mul ℝ R C).integrable_comp hiA.1
  have hr : IntegrableOn (fun t => cfcₙ (rpowIntegrand₀₁ p t) B*C) (Ioi 0) :=
    (ContinuousLinearMap.mul ℝ R).flip C |>.integrable_comp hiB.1
  have hd := hl.sub hr
  have he : EqOn (fun t => C*cfcₙ (rpowIntegrand₀₁ p t) A-cfcₙ (rpowIntegrand₀₁ p t) B*C)
      (fun t => t^(p:ℝ) • (PositiveResolvent.resolvent B t*(C*A-B*C)*PositiveResolvent.resolvent A t)) (Ioi 0) :=
    fun t ht => integrand_defect p t hp ht A B C hA hB
  constructor
  · exact (integrableOn_congr_fun he measurableSet_Ioi).mp hd
  · rw [← setIntegral_congr_fun measurableSet_Ioi he,integral_sub hl hr,
      integral_const_mul_of_integrable hiA.1,integral_mul_const_of_integrable hiB.1,
      hiA.2,hiB.2,Algebra.mul_smul_comm,Algebra.smul_mul_assoc,smul_sub]

theorem exact_fractional_intertwining (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (A B C : R) (hA : 0 ≤ A) (hB : 0 ≤ B) (h : C*A=B*C) :
    C*CFC.nnrpow A p=CFC.nnrpow B p*C := by
  have he := (normalized_defect p hp A B C hA hB).2
  simp only [h,sub_self,mul_zero,zero_mul,smul_zero,integral_zero] at he
  exact sub_eq_zero.mp he

end KomorebiPaperVI.FractionalResolvent
