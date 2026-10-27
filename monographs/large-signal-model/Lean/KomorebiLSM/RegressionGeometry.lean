import Mathlib.Analysis.Matrix.PosDef
import Mathlib.Tactic

/-! Deterministic geometry for actual ridge-regression confidence ellipsoids. -/
set_option autoImplicit false
namespace Komorebi.LSM.RegressionConfidence
open Matrix
open scoped BigOperators ComplexOrder

variable {I : Type*} [Fintype I] [DecidableEq I]

/-- The literal quadratic norm used by the ridge confidence ellipsoid. -/
noncomputable def weightedNorm (V : Matrix I I ℝ) (x : I → ℝ) : ℝ :=
  Real.sqrt (x ⬝ᵥ (V *ᵥ x))

omit [DecidableEq I] in
theorem weightedNorm_nonneg (V : Matrix I I ℝ) (x : I → ℝ) :
    0 ≤ weightedNorm V x := Real.sqrt_nonneg _

omit [DecidableEq I] in
theorem induced_norm_eq {V : Matrix I I ℝ} (hV : V.PosDef) (x : I → ℝ) :
    @norm (I → ℝ) (V.toNormedAddCommGroup hV).toNorm x = weightedNorm V x := by
  change Real.sqrt ((V *ᵥ x) ⬝ᵥ x) = _
  rw [dotProduct_comm]
  rfl

omit [DecidableEq I] in
/-- Triangle inequality for the actual positive-definite quadratic norm. -/
theorem weightedNorm_add_le {V : Matrix I I ℝ} (hV : V.PosDef) (x y : I → ℝ) :
    weightedNorm V (x+y) ≤ weightedNorm V x + weightedNorm V y := by
  rw [← induced_norm_eq hV (x+y), ← induced_norm_eq hV x, ← induced_norm_eq hV y]
  exact @norm_add_le _ (V.toSeminormedAddCommGroup hV.posSemidef).toSeminormedAddGroup x y

omit [DecidableEq I] in
theorem weightedNorm_sub_le {V : Matrix I I ℝ} (hV : V.PosDef) (x y : I → ℝ) :
    weightedNorm V (x-y) ≤ weightedNorm V x + weightedNorm V y := by
  rw [← induced_norm_eq hV (x-y), ← induced_norm_eq hV x, ← induced_norm_eq hV y]
  exact @norm_sub_le _ (V.toSeminormedAddCommGroup hV.posSemidef).toSeminormedAddGroup x y

/-- Weighted Cauchy--Schwarz uses the genuine inverse matrix norm. -/
theorem weighted_cauchy_schwarz {V : Matrix I I ℝ} (hV : V.PosDef) (e x : I → ℝ) :
    |e ⬝ᵥ x| ≤ weightedNorm V e * weightedNorm V⁻¹ x := by
  have hinv : V *ᵥ (V⁻¹ *ᵥ x) = x := by
    rw [mulVec_mulVec, Matrix.mul_nonsing_inv V (isUnit_iff_ne_zero.mpr (ne_of_gt hV.det_pos)),
      Matrix.one_mulVec]
  have hquad : weightedNorm V (V⁻¹ *ᵥ x) = weightedNorm V⁻¹ x := by
    unfold weightedNorm
    congr 1
    rw [hinv, dotProduct_comm]
  have h := @abs_real_inner_le_norm _ (V.toSeminormedAddCommGroup hV.posSemidef)
    (V.toInnerProductSpace hV.posSemidef) e (V⁻¹ *ᵥ x)
  change |(V *ᵥ (V⁻¹ *ᵥ x)) ⬝ᵥ e| ≤ _ at h
  rw [hinv, dotProduct_comm] at h
  simpa only [induced_norm_eq hV, hquad] using h

omit [DecidableEq I] in
theorem weightedNorm_sq {V : Matrix I I ℝ} (hV : V.PosSemidef) (x : I → ℝ) :
    (weightedNorm V x)^2 = x ⬝ᵥ (V *ᵥ x) := by
  unfold weightedNorm
  apply Real.sq_sqrt
  simpa only [star_trivial] using hV.dotProduct_mulVec_nonneg x

omit [DecidableEq I] in
/-- Euclidean Cauchy--Schwarz in the literal coordinate convention. -/
theorem dotProduct_sq_le (x y : I → ℝ) :
    (x ⬝ᵥ y)^2 ≤ (x ⬝ᵥ x)*(y ⬝ᵥ y) := by
  simpa [dotProduct,pow_two] using Finset.sum_mul_sq_le_sq_mul_sq Finset.univ x y

/-- A genuine quadratic lower bound reverses to the inverse quadratic bound. -/
theorem inverse_quadratic_le {V : Matrix I I ℝ} (hV : V.PosDef)
    (γ : ℝ) (hγ : 0 < γ)
    (hlower : ∀ y,γ*(y ⬝ᵥ y) ≤ y ⬝ᵥ (V *ᵥ y)) (x : I → ℝ) :
    γ*(x ⬝ᵥ (V⁻¹ *ᵥ x)) ≤ x ⬝ᵥ x := by
  let y := V⁻¹ *ᵥ x
  have hinv : V *ᵥ y = x := by
    dsimp [y]
    rw [mulVec_mulVec,Matrix.mul_nonsing_inv V (isUnit_iff_ne_zero.mpr (ne_of_gt hV.det_pos)),
      Matrix.one_mulVec]
  have hl := hlower y
  rw [hinv,dotProduct_comm y x] at hl
  have hcs := dotProduct_sq_le x y
  have ha : 0 ≤ x ⬝ᵥ x := by
    exact Finset.sum_nonneg (fun i _ => mul_self_nonneg (x i))
  have hr : 0 ≤ x ⬝ᵥ y := by
    simpa only [y,star_trivial] using hV.inv.posSemidef.dotProduct_mulVec_nonneg x
  have h1 := mul_le_mul_of_nonneg_left hcs hγ.le
  have h2 := mul_le_mul_of_nonneg_left hl ha
  change γ*(x ⬝ᵥ y) ≤ x ⬝ᵥ x
  by_cases hz : x ⬝ᵥ y = 0
  · simp [hz,ha]
  · have hp : 0 < x ⬝ᵥ y := lt_of_le_of_ne hr (Ne.symm hz)
    nlinarith

/-- Euclidean length in coordinates, independent of the function-space sup norm. -/
noncomputable def euclideanNorm (x : I → ℝ) : ℝ := weightedNorm (1 : Matrix I I ℝ) x

@[simp] theorem euclideanNorm_eq (x : I → ℝ) :
    euclideanNorm x = Real.sqrt (x ⬝ᵥ x) := by simp [euclideanNorm,weightedNorm]

theorem euclideanNorm_sq (x : I → ℝ) :
    (euclideanNorm x)^2 = x ⬝ᵥ x := by
  rw [euclideanNorm_eq]
  exact Real.sq_sqrt (Finset.sum_nonneg (fun i _ => mul_self_nonneg (x i)))

omit [DecidableEq I] in
theorem weightedNorm_smul (V : Matrix I I ℝ) (c : ℝ) (x : I → ℝ) :
    weightedNorm V (c • x) = |c| * weightedNorm V x := by
  unfold weightedNorm
  have hq : (c • x) ⬝ᵥ (V *ᵥ (c • x)) = c^2*(x ⬝ᵥ (V *ᵥ x)) := by
    simp only [Matrix.mulVec_smul,dotProduct_smul,smul_dotProduct,smul_eq_mul]
    ring
  rw [hq,Real.sqrt_mul (sq_nonneg c),Real.sqrt_sq_eq_abs]

theorem weightedNorm_inverse_mulVec {V : Matrix I I ℝ} (hV : V.PosDef) (x : I → ℝ) :
    weightedNorm V (V⁻¹ *ᵥ x) = weightedNorm V⁻¹ x := by
  unfold weightedNorm
  congr 1
  rw [mulVec_mulVec,Matrix.mul_nonsing_inv V (isUnit_iff_ne_zero.mpr (ne_of_gt hV.det_pos)),
    Matrix.one_mulVec,dotProduct_comm]

/-- The ridge lower bound controls the inverse-matrix norm. -/
theorem inverse_weightedNorm_le {V : Matrix I I ℝ} (hV : V.PosDef)
    (γ : ℝ) (hγ : 0 < γ)
    (hlower : ∀ y,γ*(y ⬝ᵥ y) ≤ y ⬝ᵥ (V *ᵥ y)) (x : I → ℝ) :
    weightedNorm V⁻¹ x ≤ euclideanNorm x / Real.sqrt γ := by
  apply (le_div_iff₀ (Real.sqrt_pos.2 hγ)).2
  have hs : (weightedNorm V⁻¹ x * Real.sqrt γ)^2 ≤ (euclideanNorm x)^2 := by
    rw [mul_pow,Real.sq_sqrt hγ.le,weightedNorm_sq hV.inv.posSemidef,euclideanNorm_sq]
    simpa only [mul_comm] using inverse_quadratic_le hV γ hγ hlower x
  have hn : 0 ≤ euclideanNorm x := weightedNorm_nonneg _ _
  nlinarith [mul_nonneg (weightedNorm_nonneg V⁻¹ x) (Real.sqrt_nonneg γ)]

/-- The exact regularization contribution has the source's sqrt(gamma) factor. -/
theorem ridge_bias_le {V : Matrix I I ℝ} (hV : V.PosDef)
    (γ : ℝ) (hγ : 0 < γ)
    (hlower : ∀ y,γ*(y ⬝ᵥ y) ≤ y ⬝ᵥ (V *ᵥ y)) (x : I → ℝ) :
    weightedNorm V (γ • (V⁻¹ *ᵥ x)) ≤ Real.sqrt γ * euclideanNorm x := by
  rw [weightedNorm_smul,abs_of_pos hγ,weightedNorm_inverse_mulVec hV]
  have hq := inverse_quadratic_le hV γ hγ hlower x
  have hq' := mul_le_mul_of_nonneg_left hq hγ.le
  have hs : (γ * weightedNorm V⁻¹ x)^2 ≤ (Real.sqrt γ * euclideanNorm x)^2 := by
    rw [mul_pow,mul_pow,Real.sq_sqrt hγ.le,weightedNorm_sq hV.inv.posSemidef,
      euclideanNorm_sq]
    nlinarith
  have hn : 0 ≤ euclideanNorm x := weightedNorm_nonneg _ _
  nlinarith [mul_nonneg hγ.le (weightedNorm_nonneg V⁻¹ x),
    mul_nonneg (Real.sqrt_nonneg γ) hn]

/-- The actual accumulated rank-one design matrices. -/
noncomputable def designGram (φ : ℕ → I → ℝ) (n : ℕ) : Matrix I I ℝ :=
  ∑ i∈Finset.range n,Matrix.vecMulVec (φ i) (φ i)

/-- The literal ridge matrix in Proposition81. -/
noncomputable def ridgeMatrix (γ : ℝ) (φ : ℕ → I → ℝ) (n : ℕ) : Matrix I I ℝ :=
  γ • (1 : Matrix I I ℝ) + designGram φ n

omit [DecidableEq I] in
theorem designGram_posSemidef (φ : ℕ → I → ℝ) (n : ℕ) :
    (designGram φ n).PosSemidef := by
  apply Matrix.posSemidef_sum
  intro i _
  simpa only [star_trivial] using Matrix.posSemidef_vecMulVec_self_star (φ i)

theorem ridgeMatrix_posDef (γ : ℝ) (hγ : 0 < γ) (φ : ℕ → I → ℝ) (n : ℕ) :
    (ridgeMatrix γ φ n).PosDef :=
  (Matrix.PosDef.one.smul hγ).add_posSemidef (designGram_posSemidef φ n)

theorem ridgeMatrix_lower (γ : ℝ) (φ : ℕ → I → ℝ) (n : ℕ) (x : I → ℝ) :
    γ*(x ⬝ᵥ x) ≤ x ⬝ᵥ (ridgeMatrix γ φ n *ᵥ x) := by
  have hn : 0 ≤ x ⬝ᵥ (designGram φ n *ᵥ x) := by
    simpa only [star_trivial] using (designGram_posSemidef φ n).dotProduct_mulVec_nonneg x
  simpa [ridgeMatrix,Matrix.add_mulVec,Matrix.smul_mulVec,dotProduct_add,dotProduct_smul] using
    le_add_of_nonneg_right hn (a := γ*(x ⬝ᵥ x))

omit [DecidableEq I] in
/-- The actual Gram quadratic is the sum of squared predictable projections. -/
theorem designGram_quadratic (φ : ℕ → I → ℝ) (n : ℕ) (x : I → ℝ) :
    x ⬝ᵥ (designGram φ n *ᵥ x) = ∑ i∈Finset.range n,(x ⬝ᵥ φ i)^2 := by
  unfold designGram
  rw [Matrix.sum_mulVec,dotProduct_sum]
  apply Finset.sum_congr rfl
  intro i _
  have hout : Matrix.vecMulVec (φ i) (φ i) *ᵥ x = (x ⬝ᵥ φ i) • φ i := by
    ext j
    simp [Matrix.mulVec,dotProduct,Matrix.vecMulVec_apply,Finset.mul_sum,mul_comm,mul_left_comm]
  rw [hout,dotProduct_smul,smul_eq_mul,pow_two]

/-- Literal design-times-response sum; it also defines the accumulated noise vector. -/
noncomputable def responseVector (φ : ℕ → I → ℝ) (y : ℕ → ℝ) (n : ℕ) : I → ℝ :=
  ∑ i∈Finset.range n,y i • φ i

/-- The actual ridge estimator obtained by matrix inversion. -/
noncomputable def ridgeEstimate (γ : ℝ) (φ : ℕ → I → ℝ) (y : ℕ → ℝ) (n : ℕ) : I → ℝ :=
  (ridgeMatrix γ φ n)⁻¹ *ᵥ responseVector φ y n

omit [DecidableEq I] in
theorem responseVector_regression (φ : ℕ → I → ℝ) (y ξ : ℕ → ℝ) (θ : I → ℝ)
    (n : ℕ) (hy : ∀ i<n,y i=θ ⬝ᵥ φ i+ξ i) :
    responseVector φ y n = designGram φ n *ᵥ θ+responseVector φ ξ n := by
  have hout (i : ℕ) : Matrix.vecMulVec (φ i) (φ i) *ᵥ θ = (θ ⬝ᵥ φ i) • φ i := by
    ext j
    simp [Matrix.mulVec,dotProduct,Matrix.vecMulVec_apply,Finset.mul_sum,mul_comm,mul_left_comm]
  unfold responseVector designGram
  rw [Matrix.sum_mulVec,← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i hi
  rw [hy i (Finset.mem_range.mp hi),add_smul,hout]

/-- The regression equation gives the exact ridge error identity before any
probabilistic bound is applied. -/
theorem ridge_error_identity (γ : ℝ) (hγ : 0 < γ) (φ : ℕ → I → ℝ)
    (y ξ : ℕ → ℝ) (θ : I → ℝ) (n : ℕ)
    (hy : ∀ i<n,y i=θ ⬝ᵥ φ i+ξ i) :
    ridgeEstimate γ φ y n-θ =
      (ridgeMatrix γ φ n)⁻¹ *ᵥ (responseVector φ ξ n-γ • θ) := by
  let V := ridgeMatrix γ φ n
  have hV := ridgeMatrix_posDef γ hγ φ n
  have hr : responseVector φ y n = V *ᵥ θ+(responseVector φ ξ n-γ • θ) := by
    rw [responseVector_regression φ y ξ θ n hy]
    simp only [V,ridgeMatrix,Matrix.add_mulVec,Matrix.smul_mulVec,Matrix.one_mulVec]
    abel
  have hinv : V⁻¹ *ᵥ (V *ᵥ θ)=θ := by
    rw [mulVec_mulVec,Matrix.nonsing_inv_mul V (isUnit_iff_ne_zero.mpr (ne_of_gt hV.det_pos)),
      Matrix.one_mulVec]
  change V⁻¹ *ᵥ responseVector φ y n-θ=V⁻¹ *ᵥ (responseVector φ ξ n-γ • θ)
  rw [hr,Matrix.mulVec_add,hinv]
  abel

/-- The deterministic noise/regularization decomposition yields the true
ellipsoid error bound, before the anytime noise event is supplied. -/
theorem ridge_error_le (γ : ℝ) (hγ : 0 < γ) (φ : ℕ → I → ℝ)
    (y ξ : ℕ → ℝ) (θ : I → ℝ) (n : ℕ)
    (hy : ∀ i<n,y i=θ ⬝ᵥ φ i+ξ i) :
    weightedNorm (ridgeMatrix γ φ n) (ridgeEstimate γ φ y n-θ) ≤
      weightedNorm (ridgeMatrix γ φ n)⁻¹ (responseVector φ ξ n)+
        Real.sqrt γ * euclideanNorm θ := by
  have hV := ridgeMatrix_posDef γ hγ φ n
  rw [ridge_error_identity γ hγ φ y ξ θ n hy,Matrix.mulVec_sub,Matrix.mulVec_smul]
  apply (weightedNorm_sub_le hV _ _).trans
  rw [weightedNorm_inverse_mulVec hV]
  exact add_le_add le_rfl (ridge_bias_le hV γ hγ (ridgeMatrix_lower γ φ n) θ)

end Komorebi.LSM.RegressionConfidence
