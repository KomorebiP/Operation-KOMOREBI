import KomorebiLSM.RobustOrientedMargin

/-! P76's literal three-coordinate polynomial coefficient box. The spatial
norm is Euclidean, and integrated mass remains a separate affine constraint. -/
set_option autoImplicit false
namespace Komorebi.LSM.CoefficientBox3
open scoped BigOperators Matrix
open LorentzCylinder RobustOrientedMargin

abbrev Spatial := EuclideanSpace ℝ (Fin 2)
abbrev State := LorentzCylinder.State Spatial
abbrev Index := Unit ⊕ Fin 2
abbrev Coefficient := Matrix Index Index ℝ

/-- Mass first, followed by the two actual Euclidean spatial coordinates. -/
def coordinates : State ≃ₗ[ℝ] (Index → ℝ) where
  toFun z := Sum.elim (fun _ => z.1) (fun i => z.2 i)
  invFun x := (x (.inl ()), WithLp.toLp 2 (fun i => x (.inr i)))
  left_inv z := by apply Prod.ext <;> rfl
  right_inv x := by funext i; cases i <;> rfl
  map_add' x y := by funext i; cases i <;> rfl
  map_smul' a x := by funext i; cases i <;> rfl

/-- Literal matrix multiplication expressed in the Lorentz state space. -/
noncomputable def operator (E : Coefficient) : State →L[ℝ] State :=
  ((coordinates.symm.toLinearMap.comp E.toLin').comp coordinates.toLinearMap).toContinuousLinearMap

@[simp] theorem operator_one_apply (z : State) : operator (1 : Coefficient) z=z := by
  change coordinates.symm ((1 : Coefficient) *ᵥ coordinates z)=z
  rw [Matrix.one_mulVec,LinearEquiv.symm_apply_apply]

@[simp] theorem coordinates_operator (E : Coefficient) (z : State) (i : Index) :
    coordinates (operator E z) i=∑ j : Index,E i j*coordinates z j := by
  change coordinates (coordinates.symm (E *ᵥ coordinates z)) i= _
  rw [LinearEquiv.apply_symm_apply]
  rfl

theorem normalized_coordinate_bound (v : Spatial) (hv : ‖v‖≤1) (j : Index) :
    |coordinates (1,v) j|≤1 := by
  cases j with
  | inl j => simp [coordinates]
  | inr j =>
    change |v j|≤1
    have hcoord : |v j|≤‖v‖ := by simpa only [Real.norm_eq_abs] using PiLp.norm_apply_le v j
    exact hcoord.trans hv

theorem scalar_coefficient_bound (E : Coefficient) (r : ℝ)
    (hE : ∀ i j,|E i j|≤r) (v : Spatial) (hv : ‖v‖≤1) (i : Index) :
    |coordinates (operator E (1,v)) i|≤3*r := by
  have hr : 0≤r := (abs_nonneg (E (.inl ()) (.inl ()))).trans (hE _ _)
  rw [coordinates_operator]
  calc
    _ ≤ ∑ j : Index,|E i j*coordinates (1,v) j| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ _j : Index,r := by
      apply Finset.sum_le_sum
      intro j _
      rw [abs_mul]
      exact (mul_le_mul (hE i j) (normalized_coordinate_bound v hv j) (abs_nonneg _) hr).trans_eq (mul_one _)
    _ = 3*r := by simp [Index]

/-- The actual two-dimensional Euclidean norm is bounded by the L1 sum. -/
theorem spatial_norm_le_sum (v : Spatial) : ‖v‖≤|v 0|+|v 1| := by
  have hs := EuclideanSpace.real_norm_sq_eq v
  simp only [Fin.sum_univ_two] at hs
  nlinarith [sq_abs (v 0),sq_abs (v 1),mul_nonneg (abs_nonneg (v 0)) (abs_nonneg (v 1)),
    norm_nonneg v,abs_nonneg (v 0),abs_nonneg (v 1)]

theorem coefficient_output_bounds (E : Coefficient) (r : ℝ)
    (hE : ∀ i j,|E i j|≤r) (v : Spatial) (hv : ‖v‖≤1) :
    |(operator E (1,v)).1|≤3*r ∧ ‖(operator E (1,v)).2‖≤6*r := by
  have hm := scalar_coefficient_bound E r hE v hv (.inl ())
  have h0 := scalar_coefficient_bound E r hE v hv (.inr 0)
  have h1 := scalar_coefficient_bound E r hE v hv (.inr 1)
  refine ⟨hm,?_⟩
  have hb := spatial_norm_le_sum (operator E (1,v)).2
  change |(operator E (1,v)).2 0|≤3*r at h0
  change |(operator E (1,v)).2 1|≤3*r at h1
  linarith

theorem polynomial_mass {n : ℕ} (E : Fin n → Coefficient) (u : ℝ) (z : State) :
    (PolynomialGram.operatorPolynomial (fun k => operator (E k)) u z).1=
      ∑ k : Fin n,u^(k : ℕ)*(operator (E k) z).1 := by
  change (LinearMap.fst ℝ ℝ Spatial) ((∑ k : Fin n,u^(k : ℕ) • operator (E k)) z)= _
  simp only [sum_apply,smul_apply,map_sum,map_smul]
  rfl

theorem polynomial_spatial {n : ℕ} (E : Fin n → Coefficient) (u : ℝ) (z : State) :
    (PolynomialGram.operatorPolynomial (fun k => operator (E k)) u z).2=
      ∑ k : Fin n,u^(k : ℕ) • (operator (E k) z).2 := by
  change (LinearMap.snd ℝ ℝ Spatial) ((∑ k : Fin n,u^(k : ℕ) • operator (E k)) z)= _
  simp only [sum_apply,smul_apply,map_sum,map_smul]
  rfl

/-- Every entry budget controls the entire observation interval, not a grid. -/
theorem polynomial_output_bounds {n : ℕ} (E : Fin n → Coefficient) (r : Fin n → ℝ)
    (hE : ∀ k i j,|E k i j|≤r k) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1)
    (v : Spatial) (hv : ‖v‖≤1) :
    |(PolynomialGram.operatorPolynomial (fun k => operator (E k)) u (1,v)).1|≤3*∑ k,r k ∧
    ‖(PolynomialGram.operatorPolynomial (fun k => operator (E k)) u (1,v)).2‖≤6*∑ k,r k := by
  have hr (k : Fin n) : 0≤r k := (abs_nonneg (E k (.inl ()) (.inl ()))).trans (hE k _ _)
  have hp (k : Fin n) : |u^(k : ℕ)|≤1 := by
    rw [abs_pow]
    exact pow_le_one₀ (abs_nonneg _) (abs_le.mpr hu)
  constructor
  · rw [polynomial_mass]
    calc
      _ ≤ ∑ k : Fin n,|u^(k : ℕ)*(operator (E k) (1,v)).1| := Finset.abs_sum_le_sum_abs _ _
      _ ≤ ∑ k : Fin n,3*r k := by
        apply Finset.sum_le_sum
        intro k _
        rw [abs_mul]
        exact (mul_le_mul (hp k) (coefficient_output_bounds (E k) (r k) (hE k) v hv).1
          (abs_nonneg _) (by norm_num)).trans_eq (one_mul _)
      _ = _ := (Finset.mul_sum _ _ _).symm
  · rw [polynomial_spatial]
    calc
      _ ≤ ∑ k : Fin n,‖u^(k : ℕ) • (operator (E k) (1,v)).2‖ := norm_sum_le _ _
      _ ≤ ∑ k : Fin n,6*r k := by
        apply Finset.sum_le_sum
        intro k _
        rw [norm_smul,Real.norm_eq_abs]
        exact (mul_le_mul (hp k) (coefficient_output_bounds (E k) (r k) (hE k) v hv).2
          (norm_nonneg _) (by norm_num)).trans_eq (one_mul _)
      _ = _ := (Finset.mul_sum _ _ _).symm

/-- The submitted margin is consumed by the real P71 robustness theorem. -/
theorem coefficient_box_preserves {n : ℕ} (F : State →L[ℝ] State)
    (E : Fin n → Coefficient) (r : Fin n → ℝ)
    (hE : ∀ k i j,|E k i j|≤r k) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1)
    (kappa : ℝ) (hmargin : kappa≤sigma F) (hcover : 9*(∑ k,r k)≤kappa)
    {z : State} (hz : z∈cone) :
    (F+PolynomialGram.operatorPolynomial (fun k => operator (E k)) u) z∈cone := by
  apply robust_preserves F _ kappa (3*∑ k,r k) (6*∑ k,r k) hmargin
    (fun v hv => (polynomial_output_bounds E r hE u hu v hv).1)
    (fun v hv => (polynomial_output_bounds E r hE u hu v hv).2) _ hz
  linarith

/-- All coefficient entries, actions and interval values are covered by the
same submitted radii; the P71 certificate is constructed from those bounds. -/
theorem boxCertificate {A : Type*} {n : ℕ}
    (F : A → Fin n → State →L[ℝ] State) (E : A → Fin n → Coefficient)
    (r : Fin n → ℝ) (kappa : A → ℝ → ℝ)
    (hE : ∀ a k i j,|E a k i j|≤r k)
    (hmargin : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → kappa a u≤sigma (PolynomialGram.operatorPolynomial (F a) u))
    (hcover : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → 9*(∑ k,r k)≤kappa a u) :
    MarginCertificate F (fun a k => operator (E a k)) kappa
      (fun _ _ => 3*∑ k,r k) (fun _ _ => 6*∑ k,r k) where
  margin := hmargin
  mass_error a u hu v hv := (polynomial_output_bounds (E a) r (hE a) u hu v hv).1
  spatial_error a u hu v hv := (polynomial_output_bounds (E a) r (hE a) u hu v hv).2
  cover a u hu := by linarith [hcover a u hu]

/-- Exact mass is retained only for errors satisfying the literal integrated
mass-row-zero condition; it is not inferred from entry radii. -/
theorem exact_mass_with_error {A : Type*} {n : ℕ}
    (F : A → Fin n → State →L[ℝ] State) (E : A → Fin n → Coefficient)
    (hF : ∀ a z,probabilityCone.mass ((∫ u,PolynomialGram.operatorPolynomial (F a) u
      ∂UniformIntervalMoments.measure) z)=probabilityCone.mass z)
    (hE : ∀ a z,probabilityCone.mass ((∫ u,PolynomialGram.operatorPolynomial (fun k => operator (E a k)) u
      ∂UniformIntervalMoments.measure) z)=0) (a : A) (z : State) :
    probabilityCone.mass ((∑ k : Fin n,UniformIntervalMoments.moment k • (F a k+operator (E a k))) z)=
      probabilityCone.mass z := by
  simp only [PolynomialGram.operatorPolynomial_integral] at hF hE
  rw [show (∑ k : Fin n,UniformIntervalMoments.moment k • (F a k+operator (E a k)))=
      (∑ k : Fin n,UniformIntervalMoments.moment k • F a k)+
        ∑ k : Fin n,UniformIntervalMoments.moment k • operator (E a k) by
          simp only [smul_add,Finset.sum_add_distrib],add_apply,map_add,hF a z,hE a z,add_zero]

open MeasureTheory in
/-- A complete box-certified polynomial family is an actual probability
instrument once its separate exact mass constraints hold. -/
noncomputable def boxInstrument {A : Type*} {n : ℕ}
    (F : A → Fin n → State →L[ℝ] State) (E : A → Fin n → Coefficient)
    (r : Fin n → ℝ) (kappa : A → ℝ → ℝ)
    (hE : ∀ a k i j,|E a k i j|≤r k)
    (hmargin : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → kappa a u≤sigma (PolynomialGram.operatorPolynomial (F a) u))
    (hcover : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → 9*(∑ k,r k)≤kappa a u)
    (hF : ∀ a z,probabilityCone.mass ((∫ u,PolynomialGram.operatorPolynomial (F a) u
      ∂UniformIntervalMoments.measure) z)=probabilityCone.mass z)
    (hzero : ∀ a z,probabilityCone.mass ((∫ u,PolynomialGram.operatorPolynomial (fun k => operator (E a k)) u
      ∂UniformIntervalMoments.measure) z)=0) :
    ContinuousInstrument.DensityInstrument (A := A) (probabilityCone (V := Spatial)) UniformIntervalMoments.measure :=
  uncertainInstrument F (fun a k => operator (E a k)) kappa
    (fun _ _ => 3*∑ k,r k) (fun _ _ => 6*∑ k,r k)
    (boxCertificate F E r kappa hE hmargin hcover) (exact_mass_with_error F E hF hzero)

open MeasureTheory in
theorem box_record_probability {A : Type*} [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]
    {n : ℕ} (F : A → Fin n → State →L[ℝ] State) (E : A → Fin n → Coefficient)
    (r : Fin n → ℝ) (kappa : A → ℝ → ℝ)
    (hE : ∀ a k i j,|E a k i j|≤r k)
    (hmargin : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → kappa a u≤sigma (PolynomialGram.operatorPolynomial (F a) u))
    (hcover : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 → 9*(∑ k,r k)≤kappa a u)
    (hF : ∀ a z,probabilityCone.mass ((∫ u,PolynomialGram.operatorPolynomial (F a) u
      ∂UniformIntervalMoments.measure) z)=probabilityCone.mass z)
    (hzero : ∀ a z,probabilityCone.mass ((∫ u,PolynomialGram.operatorPolynomial (fun k => operator (E a k)) u
      ∂UniformIntervalMoments.measure) z)=0)
    (π : ContinuousRecords.Policy (A := A) (Y := ℝ))
    (z : ContinuousInstrument.DensityInstrument.State (probabilityCone (V := Spatial))) (N : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw (boxInstrument F E r kappa hE hmargin hcover hF hzero) π z.1 N) :=
  ContinuousRecords.recordLaw_probability _ π z N

end Komorebi.LSM.CoefficientBox3
