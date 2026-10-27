import KomorebiLSM.RationalBernsteinTermination
import Mathlib.Topology.Instances.Matrix
import Mathlib.Topology.Instances.Rat

set_option autoImplicit false
namespace Komorebi.LSM.RationalTransform
open scoped BigOperators Matrix
open LorentzCylinder
noncomputable section

abbrev RealMatrix := Matrix (Fin 3) (Fin 3) ℝ
abbrev RationalMatrix := Matrix (Fin 3) (Fin 3) ℚ
abbrev Vector := Fin 3 → ℝ
abbrev Parameters (R : Type*) := Fin 2 → Fin 3 → R

/-- Literal mass, real and imaginary coordinates. -/
def coordinates : State ℂ ≃ₗ[ℝ] Vector where
  toFun z := ![z.1,z.2.re,z.2.im]
  invFun v := (v 0,⟨v 1,v 2⟩)
  left_inv z := by rfl
  right_inv v := by funext i; fin_cases i <;> rfl
  map_add' x y := by funext i; fin_cases i <;> rfl
  map_smul' a x := by funext i; fin_cases i <;> simp [Complex.real_smul]

/-- A matrix acts through the actual fixed coordinate equivalence. -/
def operatorLinear : RealMatrix →ₗ[ℝ] (State ℂ →L[ℝ] State ℂ) where
  toFun M := coordinates.symm.toContinuousLinearEquiv.toContinuousLinearMap.comp
    ((M.mulVecLin.toContinuousLinearMap).comp coordinates.toContinuousLinearEquiv.toContinuousLinearMap)
  map_add' M N := by
    apply ContinuousLinearMap.ext
    intro z
    apply coordinates.injective
    simp
  map_smul' a M := by
    apply ContinuousLinearMap.ext
    intro z
    apply coordinates.injective
    simp

def operator (M : RealMatrix) : State ℂ →L[ℝ] State ℂ := operatorLinear M

@[simp] theorem coordinates_operator (M : RealMatrix) (z : State ℂ) :
    coordinates (operator M z) = M *ᵥ coordinates z := by
  change coordinates (coordinates.symm (M *ᵥ coordinates z)) = _
  exact coordinates.apply_symm_apply _

theorem operator_mul (M N : RealMatrix) : operator (M*N) = (operator M).comp (operator N) := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinates.injective
  simp only [coordinates_operator, ContinuousLinearMap.comp_apply]
  rw [Matrix.mulVec_mulVec]

@[simp] theorem operator_one : operator (1 : RealMatrix) = ContinuousLinearMap.id ℝ (State ℂ) := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinates.injective
  simp

theorem continuous_operator : Continuous (operator : RealMatrix → (State ℂ →L[ℝ] State ℂ)) :=
  operatorLinear.continuous_of_finiteDimensional

/-- The P75 rational operator is exactly the real matrix action. -/
def castMatrix (M : RationalMatrix) : RealMatrix := M.map (algebraMap ℚ ℝ)

theorem operator_castMatrix (M : RationalMatrix) :
    operator (castMatrix M) = RationalBernsteinMargin.matrixOperator M := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinates.injective
  funext i
  change (coordinates (operator (castMatrix M) z)) i = _
  rw [coordinates_operator]
  have h := RationalBernsteinMargin.coordinate_matrixOperator M i z
  convert h using 1 <;> fin_cases i <;> rfl

/-- Invertibility is actual nonsingular matrix invertibility. -/
def atlas (M : RealMatrix) (hM : IsUnit M.det) : State ℂ ≃ₗ[ℝ] State ℂ where
  toFun := operator M
  invFun := operator M⁻¹
  left_inv z := by
    have h := congrArg (fun F : State ℂ →L[ℝ] State ℂ => F z)
      (operator_mul M⁻¹ M)
    rw [Matrix.nonsing_inv_mul _ hM, operator_one] at h
    exact h.symm
  right_inv z := by
    have h := congrArg (fun F : State ℂ →L[ℝ] State ℂ => F z)
      (operator_mul M M⁻¹)
    rw [Matrix.mul_nonsing_inv _ hM, operator_one] at h
    exact h.symm
  map_add' := (operator M).map_add
  map_smul' := (operator M).map_smul

/-- The first row is fixed exactly, with all six remaining entries free. -/
def MassPreserving {R : Type*} [Zero R] [One R] (M : Matrix (Fin 3) (Fin 3) R) : Prop :=
  M 0 = ![1,0,0]

theorem mass_preserving_operator (M : RealMatrix) (hM : MassPreserving M) (z : State ℂ) :
    (operator M z).1 = z.1 := by
  have h := congrArg (fun v : Vector => v 0) (coordinates_operator M z)
  change (operator M z).1 = _ at h
  rw [Matrix.mulVec, dotProduct, hM] at h
  simp [Fin.sum_univ_three] at h
  exact h

/-- Parameterizing the affine mass-row space preserves its constraint exactly. -/
def affineMatrix {R : Type*} [Zero R] [One R] (p : Parameters R) : Matrix (Fin 3) (Fin 3) R :=
  ![![1,0,0],p 0,p 1]

@[simp] theorem affineMatrix_mass {R : Type*} [Zero R] [One R] (p : Parameters R) :
    MassPreserving (affineMatrix p) := rfl

def parametersOf (M : RealMatrix) : Parameters ℝ := ![M 1,M 2]

theorem affineMatrix_parametersOf (M : RealMatrix) (hM : MassPreserving M) :
    affineMatrix (parametersOf M) = M := by
  funext i
  fin_cases i
  · exact hM.symm
  · rfl
  · rfl

def castParameters (p : Parameters ℚ) : Parameters ℝ := fun i j => (p i j : ℝ)

theorem affineMatrix_cast (p : Parameters ℚ) :
    affineMatrix (castParameters p) = castMatrix (affineMatrix p) := by
  ext i j
  change (affineMatrix (castParameters p)) i j = ((affineMatrix p) i j : ℝ)
  fin_cases i <;> fin_cases j <;> simp [affineMatrix,castParameters]

theorem continuous_affineMatrix : Continuous (affineMatrix (R := ℝ)) := by
  apply continuous_pi
  intro i
  fin_cases i
  · exact continuous_const
  · exact continuous_apply 0
  · exact continuous_apply 1

theorem dense_castParameters : DenseRange castParameters := by
  exact DenseRange.piMap (fun _ : Fin 2 => DenseRange.piMap (fun _ : Fin 3 => Rat.denseRange_cast))

@[simp] theorem castMatrix_one : castMatrix (1 : RationalMatrix) = 1 := by
  simp [castMatrix]

@[simp] theorem castMatrix_mul (M N : RationalMatrix) : castMatrix (M*N) = castMatrix M*castMatrix N := by
  simp [castMatrix, Matrix.map_mul]

@[simp] theorem det_castMatrix (M : RationalMatrix) : (castMatrix M).det = (M.det : ℝ) :=
  ((algebraMap ℚ ℝ).map_det M).symm

theorem unit_castMatrix (M : RationalMatrix) (hM : IsUnit M.det) : IsUnit (castMatrix M).det := by
  rw [isUnit_iff_ne_zero,det_castMatrix]
  exact_mod_cast (isUnit_iff_ne_zero.mp hM)

theorem unit_of_castMatrix (M : RationalMatrix) (hM : IsUnit (castMatrix M).det) : IsUnit M.det := by
  rw [isUnit_iff_ne_zero] at hM ⊢
  rw [det_castMatrix] at hM
  exact_mod_cast hM

/-- Rational inversion and real inversion are the same actual inverse. -/
theorem castMatrix_inv (M : RationalMatrix) (hM : IsUnit M.det) :
    castMatrix M⁻¹ = (castMatrix M)⁻¹ := by
  have hr := unit_castMatrix M hM
  have he : castMatrix M * castMatrix M⁻¹ = 1 := by
    rw [← castMatrix_mul, Matrix.mul_nonsing_inv _ hM, castMatrix_one]
  calc
    castMatrix M⁻¹ = (castMatrix M)⁻¹ * (castMatrix M * castMatrix M⁻¹) := by
      rw [← Matrix.mul_assoc,Matrix.nonsing_inv_mul _ hr,Matrix.one_mul]
    _ = (castMatrix M)⁻¹ := by rw [he,Matrix.mul_one]

/-- Forward similarity is the literal submitted coordinate transformation. -/
def conjugate (T : RealMatrix) (F : State ℂ →L[ℝ] State ℂ) : State ℂ →L[ℝ] State ℂ :=
  (operator T).comp (F.comp (operator T⁻¹))

variable {n : ℕ}
def conjugated (T : RealMatrix) (G : Fin n → RationalMatrix) (u : ℝ) : State ℂ →L[ℝ] State ℂ :=
  conjugate T (PolynomialGram.operatorPolynomial (fun k => operator (castMatrix (G k))) u)

def rationalConjugated (T : RationalMatrix) (G : Fin n → RationalMatrix) : Fin n → RationalMatrix :=
  fun k => T*G k*T⁻¹

theorem conjugated_polynomial (T : RealMatrix) (G : Fin n → RationalMatrix) (u : ℝ) :
    conjugated T G u = PolynomialGram.operatorPolynomial
      (fun k => conjugate T (operator (castMatrix (G k)))) u := by
  apply ContinuousLinearMap.ext
  intro z
  simp [conjugated,conjugate,PolynomialGram.operatorPolynomial,sum_apply,smul_apply]

/-- The rational transformed coefficients give exactly the full inverse-conjugated density. -/
theorem rational_conjugated_operator (T : RationalMatrix) (hT : IsUnit T.det)
    (G : Fin n → RationalMatrix) (u : ℝ) :
    PolynomialGram.operatorPolynomial (fun k => RationalBernsteinMargin.matrixOperator (rationalConjugated T G k)) u =
      conjugated (castMatrix T) G u := by
  rw [conjugated_polynomial]
  congr 1
  funext k
  rw [← operator_castMatrix]
  simp only [rationalConjugated,castMatrix_mul,castMatrix_inv T hT,operator_mul]
  rfl

theorem continuousAt_inverse (T : RealMatrix) (hT : IsUnit T.det) :
    ContinuousAt (Inv.inv : RealMatrix → RealMatrix) T := by
  apply continuousAt_matrix_inv T
  rw [Ring.inverse_eq_inv']
  exact continuousAt_inv₀ (isUnit_iff_ne_zero.mp hT)

theorem continuous_slack : Continuous (RobustOrientedMargin.slack : State ℂ → ℝ) :=
  continuous_fst.sub continuous_snd.norm

/-- Continuity is derived under the actual matrix inverse at an invertible transform. -/
theorem continuousAt_conjugated (G : Fin n → RationalMatrix) (T : RealMatrix)
    (hT : IsUnit T.det) (u : ℝ) :
    ContinuousAt (fun Tu : RealMatrix×ℝ => conjugated Tu.1 G Tu.2) (T,u) := by
  have hleft : ContinuousAt (fun Tu : RealMatrix×ℝ => operator Tu.1) (T,u) :=
    continuous_operator.continuousAt.comp continuous_fst.continuousAt
  have hright : ContinuousAt (fun Tu : RealMatrix×ℝ => operator Tu.1⁻¹) (T,u) :=
    continuous_operator.continuousAt.comp ((continuousAt_inverse T hT).comp continuous_fst.continuousAt)
  have hmiddle : ContinuousAt (fun Tu : RealMatrix×ℝ =>
      PolynomialGram.operatorPolynomial (fun k => operator (castMatrix (G k))) Tu.2) (T,u) :=
    (PolynomialGram.operatorPolynomial_continuous _).continuousAt.comp continuous_snd.continuousAt
  exact hleft.clm_comp (hmiddle.clm_comp hright)

/-- Rational initial coordinates have the same literal state interpretation. -/
def rationalState (z : Fin 3 → ℚ) : State ℂ :=
  ((z 0 : ℝ),⟨(z 1 : ℝ),(z 2 : ℝ)⟩)

@[simp] theorem coordinates_rationalState (z : Fin 3 → ℚ) :
    coordinates (rationalState z) = fun i => (z i : ℝ) := by
  funext i
  fin_cases i <;> rfl

theorem operator_rationalState (M : RationalMatrix) (z : Fin 3 → ℚ) :
    operator (castMatrix M) (rationalState z) = rationalState (M *ᵥ z) := by
  apply coordinates.injective
  rw [coordinates_operator]
  simp only [coordinates_rationalState]
  funext i
  exact ((algebraMap ℚ ℝ).map_mulVec M z i).symm

/-- A finite rational strict-cone test has no square root. -/
def StrictVector (z : Fin 3 → ℚ) : Prop :=
  0<z 0 ∧ z 1^2+z 2^2<z 0^2

theorem strictVector_iff_slack (z : Fin 3 → ℚ) :
    StrictVector z ↔ 0<RobustOrientedMargin.slack (rationalState z) := by
  have hs : ‖(rationalState z).2‖^2 = (z 1 : ℝ)^2+(z 2 : ℝ)^2 := by
    rw [← Complex.normSq_eq_norm_sq]
    simp [rationalState,Complex.normSq_apply,pow_two]
  constructor
  · rintro ⟨hm,hq⟩
    have hmR : 0<(z 0 : ℝ) := by exact_mod_cast hm
    have hqR : (z 1 : ℝ)^2+(z 2 : ℝ)^2<(z 0 : ℝ)^2 := by exact_mod_cast hq
    change 0<(z 0 : ℝ)-‖(rationalState z).2‖
    nlinarith [norm_nonneg (rationalState z).2]
  · intro h
    change 0<(z 0 : ℝ)-‖(rationalState z).2‖ at h
    have hmR : 0<(z 0 : ℝ) := by linarith [norm_nonneg (rationalState z).2]
    have hqR : (z 1 : ℝ)^2+(z 2 : ℝ)^2<(z 0 : ℝ)^2 := by
      nlinarith [norm_nonneg (rationalState z).2]
    exact ⟨by exact_mod_cast hmR,by exact_mod_cast hqR⟩

theorem mass_preserving_inverse (M : RealMatrix) (hM : IsUnit M.det)
    (hmass : MassPreserving M) (z : State ℂ) : (operator M⁻¹ z).1=z.1 := by
  have he : operator M (operator M⁻¹ z)=z := (atlas M hM).apply_symm_apply z
  have h := mass_preserving_operator M hmass (operator M⁻¹ z)
  rw [he] at h
  exact h.symm

theorem conjugate_weighted (T : RealMatrix) (F : Fin n → State ℂ →L[ℝ] State ℂ)
    (w : Fin n → ℝ) :
    conjugate T (∑ k,w k • F k) = ∑ k,w k • conjugate T (F k) := by
  apply ContinuousLinearMap.ext
  intro z
  simp [conjugate,sum_apply,smul_apply]

/-- Exact averaged mass transports through the actual inverse, independently of cone positivity. -/
theorem conjugate_mass (T : RealMatrix) (hT : IsUnit T.det) (hmass : MassPreserving T)
    (F : Fin n → State ℂ →L[ℝ] State ℂ) (w : Fin n → ℝ)
    (hF : ∀ z, ((∑ k,w k • F k) z).1=z.1) (z : State ℂ) :
    ((∑ k,w k • conjugate T (F k)) z).1=z.1 := by
  rw [← conjugate_weighted]
  change (operator T ((∑ k,w k • F k) (operator T⁻¹ z))).1=z.1
  rw [mass_preserving_operator T hmass, hF, mass_preserving_inverse T hT hmass]

theorem rational_conjugated_coefficient (T : RationalMatrix) (hT : IsUnit T.det)
    (G : Fin n → RationalMatrix) (k : Fin n) :
    RationalBernsteinMargin.matrixOperator (rationalConjugated T G k) =
      conjugate (castMatrix T) (operator (castMatrix (G k))) := by
  rw [← operator_castMatrix]
  simp only [rationalConjugated,castMatrix_mul,castMatrix_inv T hT,operator_mul]
  rfl

end
end Komorebi.LSM.RationalTransform
