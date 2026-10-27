import KomorebiLSM.Section88Reference
import KomorebiLSM.RationalLorentzAlgebra
import KomorebiLSM.ComplexCoefficientBox
import KomorebiLSM.UniformAbsoluteMoments

/-! Exact row-sum coefficient bounds and their genuine normalized integrated budget. -/
set_option autoImplicit false
namespace Komorebi.LSM.Section88ComparisonBudget
open scoped BigOperators
open LorentzCylinder RationalBernsteinMargin RationalLorentzMatrix PerturbedOperatorFixture
open MeasureTheory ContinuousInstrument UniformIntervalMoments
noncomputable section

def errorMatrix (a : Bool) (k : Fin 3) : RationalMatrix := rawComparison a k-referenceComparison a k

def coefficientBound (k : Fin 3) : ℝ := ![11/5000,137/30000,37/8000] k

set_option backward.isDefEq.respectTransparency false in
theorem coefficient_error (a : Bool) (k : Fin 3) (v : ℂ) (hv : ‖v‖≤1) :
    probabilityCone.value (matrixOperator (errorMatrix a k) (1,v))≤coefficientBound k := by
  have h := ComplexCoefficientBox.value_bound (fun i j => (errorMatrix a k i j : ℝ)) v hv
  rw [ComplexCoefficientBox.matrixOperator_rat] at h
  apply h.trans
  simp only [errorMatrix,Matrix.sub_apply,Rat.cast_sub]
  have hk : k=0 ∨ k=1 ∨ k=2 := by omega
  rcases hk with hk | hk | hk <;> subst k <;> cases a <;>
    norm_num [coefficientBound,Fin.sum_univ_succ,Matrix.cons_val_two]

def rawOperator (a : Bool) (u : ℝ) : State ℂ →L[ℝ] State ℂ :=
  PolynomialGram.operatorPolynomial (fun k => matrixOperator (rawComparison a k)) u

theorem raw_difference (a : Bool) (u : ℝ) (z : State ℂ) :
    rawOperator a u z-Section88Reference.operator a u z=
      ∑ k : Fin 3,u^(k : ℕ) • matrixOperator (errorMatrix a k) z := by
  simp only [rawOperator,Section88Reference.operator,PolynomialGram.operatorPolynomial,
    errorMatrix,matrixOperator_sub,sub_apply,sum_apply,smul_apply,smul_sub,
    Finset.sum_sub_distrib]

theorem pointwise_raw_error (a : Bool) (u : ℝ) (v : ℂ) (hv : ‖v‖≤1) :
    probabilityCone.value (rawOperator a u (1,v)-Section88Reference.operator a u (1,v))≤
      ∑ k : Fin 3,|u|^(k : ℕ)*coefficientBound k := by
  rw [raw_difference]
  apply (probabilityCone.value_sum_le _ _).trans
  apply Finset.sum_le_sum
  intro k _
  rw [probabilityCone.value_smul,abs_pow]
  exact mul_le_mul_of_nonneg_left (coefficient_error a k v hv) (pow_nonneg (abs_nonneg _) _)

theorem mass_matrix_of_row (M : RationalMatrix) (q : ℚ)
    (h : ∀ j,M 0 j=if j=0 then q else 0) (z : State ℂ) :
    coordinate 0 (matrixOperator M z)=(q : ℝ)*z.1 := by
  rw [coordinate_matrixOperator]
  simp_rw [h]
  norm_num [Fin.sum_univ_succ,coordinate,Matrix.cons_val_two]

theorem moment_mass_of_rows (M : Fin 3 → RationalMatrix) (q0 q2 : ℚ)
    (h0 : ∀ j,M 0 0 j=if j=0 then q0 else 0)
    (h2 : ∀ j,M 2 0 j=if j=0 then q2 else 0) (hq : q0+q2/3=1) (z : State ℂ) :
    probabilityCone.mass ((∑ k : Fin 3,moment k • matrixOperator (M k)) z)=probabilityCone.mass z := by
  have hc0 := mass_matrix_of_row (M 0) q0 h0 z
  have hc2 := mass_matrix_of_row (M 2) q2 h2 z
  change coordinate 0 ((∑ k : Fin 3,moment k • matrixOperator (M k)) z)=z.1
  simp only [sum_apply,smul_apply,map_sum,map_smul]
  simp only [Fin.sum_univ_succ]
  change moment 0*coordinate 0 (matrixOperator (M 0) z)+
    (moment 1*coordinate 0 (matrixOperator (M 1) z)+
      (moment 2*coordinate 0 (matrixOperator (M 2) z)+0))=z.1
  have hms : moment 0=1 ∧ moment 1=0 ∧ moment 2=1/3 := by norm_num [moment_formula]
  rw [hms.1,hms.2.1,hms.2.2,hc0,hc2]
  simp only [one_mul,zero_mul,add_zero,zero_add]
  have hqr : (q0 : ℝ)+(q2 : ℝ)/3=1 := by exact_mod_cast hq
  calc
    _=((q0 : ℝ)+(q2 : ℝ)/3)*z.1 := by ring
    _=z.1 := by rw [hqr]; ring

theorem raw_moment_mass (a : Bool) (z : State ℂ) :
    probabilityCone.mass ((∑ k : Fin 3,moment k • matrixOperator (rawComparison a k)) z)=probabilityCone.mass z := by
  apply moment_mass_of_rows (rawComparison a) (1/4) (9/4) _ _ (by norm_num) z
  · intro j
    cases a <;> fin_cases j <;> norm_num [Matrix.cons_val_two]
  · intro j
    cases a <;> fin_cases j <;> norm_num [Matrix.cons_val_two]

def rawEstimate : InteriorRepair.EstimateFamily (V := ℂ) (A := Bool) :=
  InteriorRepair.EstimateFamily.ofPolynomial (fun a k => matrixOperator (rawComparison a k)) raw_moment_mass

/-- No signed odd-moment cancellation is used for this error integral. -/
theorem integrated_raw_error (a : Bool) (z : State ℂ) (hz : z∈probabilityCone.base) :
    (∫ u,probabilityCone.value (rawEstimate.op a u z-Section88Reference.instrument.op a u z)∂measure)≤241/40000 := by
  have hm : z.1=1 := hz.2
  have hv : ‖z.2‖≤1 := by rw [← hm]; exact hz.1
  have he : z=(1,z.2) := Prod.ext hm rfl
  have hi := probabilityCone.integrable_value
    ((rawEstimate.applied_integrable a z).sub (Section88Reference.instrument.applied_integrable a z))
  have hj : Integrable (fun u => ∑ k : Fin 3,|u|^(k : ℕ)*coefficientBound k) measure := by
    exact integrable_finsetSum _ (fun k _ => (UniformAbsoluteMoments.abs_power_integrable k).mul_const _)
  have hp (u : ℝ) : probabilityCone.value (rawEstimate.op a u z-Section88Reference.instrument.op a u z)≤
      ∑ k : Fin 3,|u|^(k : ℕ)*coefficientBound k := by
    rw [he]
    exact pointwise_raw_error a u z.2 hv
  apply (integral_mono hi hj hp).trans
  rw [integral_finsetSum Finset.univ (fun (k : Fin 3) _ => (UniformAbsoluteMoments.abs_power_integrable k).mul_const _)]
  simp_rw [integral_mul_const,UniformAbsoluteMoments.integral_abs_power]
  norm_num [coefficientBound,Fin.sum_univ_succ,Matrix.cons_val_two]

end
end Komorebi.LSM.Section88ComparisonBudget
