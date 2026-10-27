import KomorebiLSM.RationalSemicircle
import KomorebiLSM.TensorBernsteinCertificate

/-! The submitted rational tensor polynomials are the literal operator chart tests. -/
set_option autoImplicit false
namespace Komorebi.LSM.RationalBernsteinMargin
open scoped BigOperators
open LorentzCylinder RobustOrientedMargin RationalSemicircle TensorBernsteinCertificate
noncomputable section

abbrev RationalMatrix := Matrix (Fin 3) (Fin 3) ℚ

def coordinate : Fin 3 → State ℂ →L[ℝ] ℝ :=
  ![ContinuousLinearMap.fst ℝ ℝ ℂ,
    Complex.reCLM.comp (ContinuousLinearMap.snd ℝ ℝ ℂ),
    Complex.imCLM.comp (ContinuousLinearMap.snd ℝ ℝ ℂ)]

def row (M : RationalMatrix) (i : Fin 3) : State ℂ →L[ℝ] ℝ :=
  ∑ j,(M i j : ℝ) • coordinate j

/-- A rational three-coordinate matrix acting on the actual mass/spatial state space. -/
def matrixOperator (M : RationalMatrix) : State ℂ →L[ℝ] State ℂ :=
  (row M 0).prod (Complex.equivRealProdCLM.symm.toContinuousLinearMap.comp
    ((row M 1).prod (row M 2)))

@[simp] theorem coordinate_matrixOperator (M : RationalMatrix) (i : Fin 3) (z : State ℂ) :
    coordinate i (matrixOperator M z)=∑ j,(M i j : ℝ)*coordinate j z := by
  fin_cases i <;> simp [coordinate,matrixOperator,row]

def denominatorPolynomial : Polynomial₂ := 1+MvPolynomial.X 1^2

def liftPolynomial (left : Bool) : Fin 3 → Polynomial₂ :=
  ![denominatorPolynomial,
    (if left then -1 else 1)*(1-MvPolynomial.X 1^2),
    (if left then -1 else 1)*(2*MvPolynomial.X 1)]

theorem value_liftPolynomial (left : Bool) (i : Fin 3) (u t : ℝ) :
    value (liftPolynomial left i) ![u,t]=coordinate i (lift left t) := by
  fin_cases i <;> cases left <;>
    simp [liftPolynomial,denominatorPolynomial,value,coordinate,lift,numerator,denominator]

variable {n : ℕ}

def outputPolynomial (G : Fin n → RationalMatrix) (left : Bool) (i : Fin 3) : Polynomial₂ :=
  ∑ k,∑ j,MvPolynomial.C (G k i j)*MvPolynomial.X 0^(k : ℕ)*liftPolynomial left j

/-- Polynomial equality is connected to the complete operator family, not interpolation samples. -/
theorem value_outputPolynomial (G : Fin n → RationalMatrix) (left : Bool) (i : Fin 3) (u t : ℝ) :
    value (outputPolynomial G left i) ![u,t]=
      coordinate i (PolynomialGram.operatorPolynomial (fun k => matrixOperator (G k)) u (lift left t)) := by
  simp only [outputPolynomial,value,MvPolynomial.eval₂_sum,map_sum,map_smul,
    sum_apply,smul_apply,
    PolynomialGram.operatorPolynomial,coordinate_matrixOperator]
  simp only [MvPolynomial.eval₂_mul,MvPolynomial.eval₂_C,MvPolynomial.eval₂_pow,
    MvPolynomial.eval₂_X,Matrix.cons_val_zero]
  change (∑ k : Fin n,∑ j : Fin 3,((G k i j : ℝ)*u^(k : ℕ))*value (liftPolynomial left j) ![u,t])=
    ∑ k : Fin n,u^(k : ℕ)*(∑ j : Fin 3,(G k i j : ℝ)*coordinate j (lift left t))
  simp only [value_liftPolynomial,Finset.mul_sum]
  congr 1
  funext k
  apply Finset.sum_congr rfl
  intro j _
  ring

def orientationPolynomial (G : Fin n → RationalMatrix) (kappa : ℚ) (left : Bool) : Polynomial₂ :=
  outputPolynomial G left 0-MvPolynomial.C kappa*denominatorPolynomial

def squareGapPolynomial (G : Fin n → RationalMatrix) (kappa : ℚ) (left : Bool) : Polynomial₂ :=
  orientationPolynomial G kappa left^2-outputPolynomial G left 1^2-outputPolynomial G left 2^2

theorem value_orientationPolynomial (G : Fin n → RationalMatrix) (kappa : ℚ) (left : Bool) (u t : ℝ) :
    value (orientationPolynomial G kappa left) ![u,t]=
      orientation (PolynomialGram.operatorPolynomial (fun k => matrixOperator (G k)) u) kappa left t := by
  rw [orientationPolynomial,value,MvPolynomial.eval₂_sub,MvPolynomial.eval₂_mul,
    MvPolynomial.eval₂_C]
  change value (outputPolynomial G left 0) ![u,t]-(kappa : ℝ)*value denominatorPolynomial ![u,t]=_
  rw [value_outputPolynomial]
  simp [coordinate,value,denominatorPolynomial,orientation,denominator]

theorem value_squareGapPolynomial (G : Fin n → RationalMatrix) (kappa : ℚ) (left : Bool) (u t : ℝ) :
    value (squareGapPolynomial G kappa left) ![u,t]=
      squareGap (PolynomialGram.operatorPolynomial (fun k => matrixOperator (G k)) u) kappa left t := by
  simp only [squareGapPolynomial,value,MvPolynomial.eval₂_sub,MvPolynomial.eval₂_pow]
  change value (orientationPolynomial G kappa left) ![u,t]^2-
    value (outputPolynomial G left 1) ![u,t]^2-value (outputPolynomial G left 2) ![u,t]^2=_
  rw [value_orientationPolynomial,value_outputPolynomial,value_outputPolynomial]
  simp [coordinate,squareGap]

/-- Both finite subdivision trees are required for every chart. -/
structure Certificate (G : Fin n → RationalMatrix) (kappa : ℚ) where
  orientationWitness : ∀ left,SubdivisionWitness (orientationPolynomial G kappa left) square
  squareGapWitness : ∀ left,SubdivisionWitness (squareGapPolynomial G kappa left) square

/-- Literal finite rational witnesses certify the actual minimum over every disk input. -/
theorem Certificate.margin {G : Fin n → RationalMatrix} {kappa : ℚ} (cert : Certificate G kappa)
    (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1) :
    (kappa : ℝ)≤sigma (PolynomialGram.operatorPolynomial (fun k => matrixOperator (G k)) u) := by
  apply margin_of_charts
  · intro left t ht
    rw [← value_orientationPolynomial]
    apply (cert.orientationWitness left).sound
    rw [square_domain]
    intro i
    fin_cases i
    · exact hu
    · exact ht
  · intro left t ht
    rw [← value_squareGapPolynomial]
    apply (cert.squareGapWitness left).sound
    rw [square_domain]
    intro i
    fin_cases i
    · exact hu
    · exact ht

/-- Strict actual margin makes both literal chart tests strictly positive. -/
theorem strict_chart_tests (F : State ℂ →L[ℝ] State ℂ) (kappa : ℝ)
    (hmargin : kappa<sigma F) (left : Bool) (t : ℝ) :
    0<orientation F kappa left t ∧ 0<squareGap F kappa left t := by
  have hm : kappa<slack (F (1,chart left t)) :=
    hmargin.trans_le (sigma_le F _ (chart_norm left t).le)
  have hd := denominator_pos t
  have he : (F (lift left t)).2=denominator t • (F (1,chart left t)).2 := by
    rw [lift_eq,map_smul]
    rfl
  have hf : orientation F kappa left t=
      denominator t*((F (1,chart left t)).1-kappa) := by
    unfold orientation
    rw [lift_eq,map_smul]
    change denominator t*(F (1,chart left t)).1-kappa*denominator t=_
    ring
  have hn : ‖(F (lift left t)).2‖<orientation F kappa left t := by
    rw [he,norm_smul,Real.norm_eq_abs,abs_of_pos hd,hf]
    apply mul_lt_mul_of_pos_left _ hd
    dsimp [slack] at hm
    linarith
  have hf0 : 0<orientation F kappa left t := (norm_nonneg _).trans_lt hn
  refine ⟨hf0,?_⟩
  have hs : ‖(F (lift left t)).2‖^2<(orientation F kappa left t)^2 :=
    (sq_lt_sq₀ (norm_nonneg _) hf0.le).mpr hn
  rw [← Complex.normSq_eq_norm_sq,Complex.normSq_apply] at hs
  unfold squareGap
  nlinarith

/-- The checked margin supplies actual pointwise cone preservation at every interval value. -/
theorem Certificate.preserves {G : Fin n → RationalMatrix} {kappa : ℚ} (cert : Certificate G kappa)
    (hkappa : 0≤kappa) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1)
    {z : State ℂ} (hz : z∈cone) :
    PolynomialGram.operatorPolynomial (fun k => matrixOperator (G k)) u z∈cone := by
  apply preserves_of_normalized _ _ hz
  intro v hv
  have hm := ((le_sigma_iff _ _).mp (cert.margin u hu)) v hv
  have hk : (0 : ℝ)≤kappa := by exact_mod_cast hkappa
  change ‖(PolynomialGram.operatorPolynomial (fun k => matrixOperator (G k)) u (1,v)).2‖≤_
  dsimp [slack] at hm
  linarith

/-- Exact averaged mass remains a separate algebraic check on the submitted complete family. -/
def certifiedInstrument {A : Type*} (G : A → Fin n → RationalMatrix) (kappa : ℚ)
    (cert : ∀ a,Certificate (G a) kappa) (hkappa : 0≤kappa)
    (hm : ∀ a z,probabilityCone.mass
      ((∑ k : Fin n,UniformIntervalMoments.moment k • matrixOperator (G a k)) z)=probabilityCone.mass z) :
    ContinuousInstrument.DensityInstrument (A := A) (probabilityCone (V := ℂ)) UniformIntervalMoments.measure where
  op a := PolynomialGram.operatorPolynomial (fun k => matrixOperator (G a k))
  measurable_op a := (PolynomialGram.operatorPolynomial_continuous _).measurable
  integrable_op a := PolynomialGram.operatorPolynomial_integrable _
  positive a := by
    filter_upwards [PolynomialGram.uniform_ae_interval] with u hu
    exact fun z hz => (cert a).preserves hkappa u hu hz
  mass_preserving a z := by
    rw [PolynomialGram.operatorPolynomial_integral]
    exact hm a z

theorem certified_record_probability {A : Type*} [Fintype A] [MeasurableSpace A]
    [MeasurableSingletonClass A] (G : A → Fin n → RationalMatrix) (kappa : ℚ)
    (cert : ∀ a,Certificate (G a) kappa) (hkappa : 0≤kappa)
    (hm : ∀ a z,probabilityCone.mass
      ((∑ k : Fin n,UniformIntervalMoments.moment k • matrixOperator (G a k)) z)=probabilityCone.mass z)
    (policy : ContinuousRecords.Policy (A := A) (Y := ℝ)) (z : State ℂ)
    (hz : z∈probabilityCone.base) (horizon : ℕ) :
    MeasureTheory.IsProbabilityMeasure (ContinuousRecords.recordLaw
      (certifiedInstrument G kappa cert hkappa hm) policy z horizon) :=
  ContinuousRecords.recordLaw_probability (certifiedInstrument G kappa cert hkappa hm)
    policy ⟨z,hz⟩ horizon

end
end Komorebi.LSM.RationalBernsteinMargin
