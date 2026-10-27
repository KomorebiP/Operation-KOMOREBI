import KomorebiLSM.PerturbedOperatorFixture
import KomorebiLSM.InteriorRepair

/-! The actual unmodified fixture is positive on the predecessor comparison cone. -/
set_option autoImplicit false
namespace Komorebi.LSM.Section88Reference
open scoped BigOperators
open LorentzCylinder RationalBernsteinMargin RationalLorentzMatrix PerturbedOperatorFixture
open RobustOrientedMargin ContinuousInstrument MeasureTheory
noncomputable section

def operator (a : Bool) (u : ℝ) : State ℂ →L[ℝ] State ℂ :=
  PolynomialGram.operatorPolynomial (fun k => matrixOperator (referenceComparison a k)) u

theorem coordinate_operator (a : Bool) (u : ℝ) (z : State ℂ) (i : Fin 3) :
    coordinate i (operator a u z)=∑ k : Fin 3,u^(k : ℕ)*
      (∑ j : Fin 3,(referenceComparison a k i j : ℝ)*coordinate j z) := by
  simp only [operator,PolynomialGram.operatorPolynomial,sum_apply,smul_apply,map_sum,map_smul,
    coordinate_matrixOperator,smul_eq_mul]

theorem direct_mass (u : ℝ) (z : State ℂ) :
    (operator false u z).1=(1/4+9/4*u^2)*z.1+u*(6/5*z.2.re+9/10*z.2.im) := by
  change coordinate 0 (operator false u z)=_
  rw [coordinate_operator]
  norm_num [Fin.sum_univ_succ,coordinate,Matrix.cons_val_two]
  ring

theorem direct_real (u : ℝ) (z : State ℂ) :
    (operator false u z).2.re=6/5*u*z.1+(1/4+63/100*u^2)*z.2.re+54/25*u^2*z.2.im := by
  change coordinate 1 (operator false u z)=_
  rw [coordinate_operator]
  norm_num [Fin.sum_univ_succ,coordinate,Matrix.cons_val_two]
  ring

theorem direct_imag (u : ℝ) (z : State ℂ) :
    (operator false u z).2.im=9/10*u*z.1+54/25*u^2*z.2.re+(1/4-63/100*u^2)*z.2.im := by
  change coordinate 2 (operator false u z)=_
  rw [coordinate_operator]
  norm_num [Fin.sum_univ_succ,coordinate,Matrix.cons_val_two]
  ring

/-- Exact conformal quadratic identity for the full observation polynomial. -/
theorem direct_quadratic (u : ℝ) (z : State ℂ) :
    (operator false u z).1^2-(operator false u z).2.re^2-(operator false u z).2.im^2=
      ((1-9*u^2)/4)^2*(z.1^2-z.2.re^2-z.2.im^2) := by
  rw [direct_mass,direct_real,direct_imag]
  ring

theorem direct_normalized_positive (u : ℝ) (v : ℂ) (hv : ‖v‖≤1) : operator false u (1,v)∈cone := by
  have hsq : v.re^2+v.im^2≤1 := by
    have he := Complex.normSq_eq_norm_sq v
    simp only [Complex.normSq_apply,pow_two] at he
    nlinarith [norm_nonneg v]
  let d : ℝ := 4/5*v.re+3/5*v.im
  have hd : |d|≤1 := by
    apply (sq_le_sq₀ (abs_nonneg _) (by norm_num : (0 : ℝ)≤1)).mp
    rw [sq_abs]
    dsimp [d]
    nlinarith [sq_nonneg (3/5*v.re-4/5*v.im)]
  let b : ℝ := 3*u/2
  have hm : (operator false u (1,v)).1=1/4+b^2+b*d := by
    rw [direct_mass]
    dsimp [b,d]
    ring
  have hb : |b*d|≤|b| := by
    rw [abs_mul]
    simpa using mul_le_mul_of_nonneg_left hd (abs_nonneg b)
  have hm0 : 0≤(operator false u (1,v)).1 := by
    rw [hm]
    nlinarith [neg_abs_le (b*d),sq_abs b,sq_nonneg (|b|-1/2)]
  have hquad : 0≤(operator false u (1,v)).1^2-(operator false u (1,v)).2.re^2-
      (operator false u (1,v)).2.im^2 := by
    rw [direct_quadratic]
    exact mul_nonneg (sq_nonneg _) (by norm_num; linarith)
  change ‖(operator false u (1,v)).2‖≤(operator false u (1,v)).1
  apply (sq_le_sq₀ (norm_nonneg _) hm0).mp
  rw [← Complex.normSq_eq_norm_sq,Complex.normSq_apply]
  nlinarith

def rotation : RationalMatrix := ![![1,0,0],![0,3/5,4/5],![0,-4/5,3/5]]

theorem rotation_action (z : State ℂ) :
    matrixOperator rotation z=(z.1,(⟨3/5,-4/5⟩ : ℂ)*z.2) := by
  apply coordinate_ext
  intro i
  simp only [coordinate_matrixOperator]
  fin_cases i <;> norm_num [rotation,coordinate,Fin.sum_univ_succ,Matrix.cons_val_two]
  ring

theorem rotation_positive {z : State ℂ} (hz : z∈cone) : matrixOperator rotation z∈cone := by
  rw [rotation_action]
  change ‖(⟨3/5,-4/5⟩ : ℂ)*z.2‖≤z.1
  rw [norm_mul]
  have hn : ‖(⟨3/5,-4/5⟩ : ℂ)‖=1 := by
    have h := Complex.normSq_eq_norm_sq (⟨3/5,-4/5⟩ : ℂ)
    norm_num [Complex.normSq_apply] at h
    nlinarith [norm_nonneg (⟨3/5,-4/5⟩ : ℂ)]
  simpa [hn] using hz

theorem rotated_action (u : ℝ) (z : State ℂ) :
    operator true u z=operator false u (matrixOperator rotation z) := by
  apply coordinate_ext
  intro i
  simp only [coordinate_operator,coordinate_matrixOperator]
  fin_cases i <;> norm_num [rotation,coordinate,Fin.sum_univ_succ,Matrix.cons_val_two] <;> first | trivial | (ring <;> simp)

theorem positive (a : Bool) (u : ℝ) {z : State ℂ} (hz : z∈cone) : operator a u z∈cone := by
  have hd : ∀ w∈cone,operator false u w∈cone :=
    fun w hw => preserves_of_normalized (operator false u) (direct_normalized_positive u) hw
  cases a
  · exact hd z hz
  · rw [rotated_action]
    exact hd _ (rotation_positive hz)

theorem moment_mass (a : Bool) (z : State ℂ) :
    probabilityCone.mass ((∑ k : Fin 3,UniformIntervalMoments.moment k •
      matrixOperator (referenceComparison a k)) z)=probabilityCone.mass z := by
  change coordinate 0 ((∑ k : Fin 3,UniformIntervalMoments.moment k •
    matrixOperator (referenceComparison a k)) z)=z.1
  simp only [sum_apply,smul_apply,map_sum,map_smul,coordinate_matrixOperator]
  cases a <;> norm_num [Fin.sum_univ_succ,coordinate,UniformIntervalMoments.moment_formula,Matrix.cons_val_two] <;> ring

def instrument : DensityInstrument (A := Bool) (probabilityCone (V := ℂ)) UniformIntervalMoments.measure where
  op := operator
  measurable_op a := (PolynomialGram.operatorPolynomial_continuous _).measurable
  integrable_op a := PolynomialGram.operatorPolynomial_integrable _
  positive a := by
    filter_upwards [] with u
    exact fun z hz => positive a u hz
  mass_preserving a z := by
    change probabilityCone.mass ((∫ u,PolynomialGram.operatorPolynomial
      (fun k => matrixOperator (referenceComparison a k)) u∂UniformIntervalMoments.measure) z)=_
    rw [PolynomialGram.operatorPolynomial_integral]
    exact moment_mass a z

end
end Komorebi.LSM.Section88Reference
