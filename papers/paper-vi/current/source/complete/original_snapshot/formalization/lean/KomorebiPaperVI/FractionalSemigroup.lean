import KomorebiPaperVI.Semigroups
import KomorebiPaperVI.BanachDefects
import Mathlib.Analysis.SpecialFunctions.ContinuousFunctionalCalculus.Rpow.IntegralRepresentation
import Mathlib.Analysis.CStarAlgebra.ContinuousFunctionalCalculus.Basic
import Mathlib.Analysis.CStarAlgebra.ContinuousFunctionalCalculus.Instances
import Mathlib.Analysis.SpecialFunctions.ContinuousFunctionalCalculus.Rpow.Basic
import Mathlib.Analysis.SpecialFunctions.ContinuousFunctionalCalculus.ExpLog.Basic
import Mathlib.Analysis.CStarAlgebra.ContinuousFunctionalCalculus.Isometric

/-! Author: Komorebi P. Actual positive CFC powers and their exponential contraction. -/
set_option backward.isDefEq.respectTransparency false
namespace KomorebiPaperVI.FractionalSemigroup
open KomorebiPaperVI.Semigroups
attribute [local instance] IsStarNormal.instContinuousFunctionalCalculus
variable {R : Type*} [CStarAlgebra R] [PartialOrder R] [StarOrderedRing R]

noncomputable def power (A : R) (a : ℝ) : R := CFC.rpow A a

theorem power_nonnegative (A : R) (a : ℝ) : 0 ≤ power A a := CFC.rpow_nonneg

theorem exponential_cfc (A : R) (hA : 0 ≤ A) (a t : ℝ) (ha : 0 < a) :
    NormedSpace.exp ((-t) • power A a)=
      cfc (fun x : ℝ => Real.exp (-t*x^a)) A := by
  have hp : IsSelfAdjoint (power A a) := (power_nonnegative A a).isSelfAdjoint
  rw [← CFC.real_exp_eq_normedSpace_exp (by cfc_tac : IsSelfAdjoint ((-t) • power A a))]
  rw [← cfc_comp_smul (-t) Real.exp (power A a)]
  unfold power
  have he : CFC.rpow A a=cfc (fun x : ℝ => x^a) A := CFC.rpow_eq_cfc_real hA
  simp only [smul_eq_mul]
  rw [he,← cfc_comp (fun x : ℝ => Real.exp (-t*x)) (fun x : ℝ => x^a) A hA.isSelfAdjoint (by fun_prop) (Real.continuous_rpow_const ha.le).continuousOn]
  rfl

theorem exponential_contraction (A : R) (hA : 0 ≤ A) (a t : ℝ) (ha : 0 < a) (ht : 0 ≤ t) :
    ‖NormedSpace.exp ((-t) • power A a)‖ ≤ 1 := by
  rw [exponential_cfc A hA a t ha]
  apply norm_cfc_le (by norm_num)
  intro x hx
  have hx0 : 0 ≤ x := by grind
  rw [Real.norm_of_nonneg (Real.exp_pos _).le,Real.exp_le_one_iff]
  exact mul_nonpos_of_nonpos_of_nonneg (neg_nonpos.mpr ht) (Real.rpow_nonneg hx0 _)

theorem exponential_gap (A : R) (hA : 0 ≤ A) (a t m : ℝ) (ha : 0 < a)
    (ht : 0 ≤ t) (hm : 0 ≤ m) (hgap : algebraMap ℝ R m ≤ A) :
    ‖NormedSpace.exp ((-t) • power A a)‖ ≤ Real.exp (-t*m^a) := by
  rw [exponential_cfc A hA a t ha]
  apply norm_cfc_le (Real.exp_pos _).le
  intro x hx
  have hx : m ≤ x := (algebraMap_le_iff_le_spectrum hA.isSelfAdjoint).mp hgap x hx
  rw [Real.norm_of_nonneg (Real.exp_pos _).le,Real.exp_le_exp]
  exact mul_le_mul_of_nonpos_left (Real.rpow_le_rpow hm hx ha.le) (neg_nonpos.mpr ht)

noncomputable def defect (A B C : R) (a : ℝ) : R := C*power A a-power B a*C
noncomputable def evolution (A : R) (a t : ℝ) : R := NormedSpace.exp ((-t) • power A a)

theorem evolution_transfer (A : R) (a t : ℝ) : evolution A a t=transfer (-power A a) t := by
  simp [evolution,transfer,smul_neg,neg_smul]

theorem fractional_duhamel (A B C : R) (a t : ℝ) :
    C*evolution A a t-evolution B a t*C=
      -(∫ r in 0..t,evolution B a (t-r)*defect A B C a*evolution A a r) := by
  simp only [evolution_transfer]
  rw [BanachDefects.duhamel]
  have he : C*(-power A a)-(-power B a)*C= -defect A B C a := by
    simp only [defect,mul_neg,neg_mul]
    abel
  rw [he]
  simp only [mul_neg,neg_mul,intervalIntegral.integral_neg]

theorem fractional_contraction_bound (A B C : R) (hA : 0 ≤ A) (hB : 0 ≤ B)
    (a t : ℝ) (ha : 0 < a) (ht : 0 ≤ t) :
    ‖C*evolution A a t-evolution B a t*C‖ ≤ t*‖defect A B C a‖ := by
  simp only [evolution_transfer]
  have h := BanachDefects.contraction_bound (-power A a) (-power B a) C t ht
    (fun r hr => by rw [← evolution_transfer]; exact exponential_contraction A hA a r ha hr)
    (fun r hr => by rw [← evolution_transfer]; exact exponential_contraction B hB a r ha hr)
  have he : C*(-power A a)-(-power B a)*C= -defect A B C a := by
    simp only [defect,mul_neg,neg_mul]
    abel
  simpa only [he,norm_neg] using h

theorem fractional_gap_bound (A B C : R) (hA : 0 ≤ A) (hB : 0 ≤ B)
    (a t m : ℝ) (ha : 0 < a) (ht : 0 ≤ t) (hm : 0 ≤ m)
    (hgA : algebraMap ℝ R m ≤ A) (hgB : algebraMap ℝ R m ≤ B) :
    ‖C*evolution A a t-evolution B a t*C‖ ≤ t*Real.exp (-t*m^a)*‖defect A B C a‖ := by
  rw [fractional_duhamel,norm_neg]
  have hc : Continuous (fun r => evolution B a (t-r)*defect A B C a*evolution A a r) := by
    simp only [evolution_transfer]
    fun_prop
  calc
    _ ≤ ∫ r in 0..t,‖evolution B a (t-r)*defect A B C a*evolution A a r‖ :=
      intervalIntegral.norm_integral_le_integral_norm ht
    _ ≤ ∫ _ in 0..t,Real.exp (-t*m^a)*‖defect A B C a‖ := by
      apply intervalIntegral.integral_mono_on ht (hc.norm.intervalIntegrable 0 t) intervalIntegrable_const
      intro r hr
      calc
        _ ≤ ‖evolution B a (t-r)‖*‖defect A B C a‖*‖evolution A a r‖ :=
          norm_mul_le_of_le (norm_mul_le _ _) le_rfl
        _ ≤ Real.exp (-(t-r)*m^a)*‖defect A B C a‖*Real.exp (-r*m^a) := by
          gcongr
          · exact exponential_gap B hB a (t-r) m ha (by linarith [hr.2]) hm hgB
          · exact exponential_gap A hA a r m ha hr.1 hm hgA
        _ = _ := by
          rw [mul_right_comm,← Real.exp_add]
          congr 2
          ring
    _ = _ := by
      simp only [intervalIntegral.integral_const,sub_zero,smul_eq_mul]
      ring

end KomorebiPaperVI.FractionalSemigroup
