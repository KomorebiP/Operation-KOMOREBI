import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.Analysis.InnerProductSpace.ProdL2

set_option autoImplicit false

namespace Komorebi.LSM.EuclideanMatrixNorms
open scoped Matrix

variable {D : Type*}

/-- Entry flattening into an actual Euclidean space; no matrix norm instance is used. -/
noncomputable def flatten : Matrix D D ℝ ≃ₗ[ℝ] EuclideanSpace ℝ (D × D) where
  toFun A := WithLp.toLp 2 (fun p => A p.1 p.2)
  invFun x i j := x (i,j)
  left_inv A := rfl
  right_inv x := by ext p; rfl
  map_add' A B := by ext p; rfl
  map_smul' a A := by ext p; rfl

@[simp] theorem flatten_apply (A : Matrix D D ℝ) (i j : D) :
    flatten A (i,j) = A i j := rfl

@[simp] theorem flatten_symm_apply (x : EuclideanSpace ℝ (D × D)) (i j : D) :
    flatten.symm x i j = x (i,j) := rfl

variable [Fintype D] [DecidableEq D]

/-- The actual Frobenius norm, through Euclidean entry flattening. -/
noncomputable def frobenius (A : Matrix D D ℝ) : ℝ := ‖flatten A‖

/-- The operator norm on Euclidean vectors (the real spectral norm). -/
noncomputable def spectralNorm (A : Matrix D D ℝ) : ℝ :=
  ‖Matrix.toEuclideanCLM (𝕜 := ℝ) A‖

omit [DecidableEq D] in
theorem frobenius_nonneg (A : Matrix D D ℝ) : 0 ≤ frobenius A := norm_nonneg _

theorem spectralNorm_nonneg (A : Matrix D D ℝ) : 0 ≤ spectralNorm A := norm_nonneg _

omit [DecidableEq D] in
theorem frobenius_sq (A : Matrix D D ℝ) :
    frobenius A ^ 2 = ∑ i, ∑ j, A i j ^ 2 := by
  rw [frobenius, EuclideanSpace.real_norm_sq_eq]
  simp [Fintype.sum_prod_type]

omit [DecidableEq D] in
theorem frobenius_transpose (A : Matrix D D ℝ) : frobenius Aᵀ = frobenius A := by
  have hs : frobenius Aᵀ ^ 2 = frobenius A ^ 2 := by
    simp only [frobenius_sq, Matrix.transpose_apply]
    exact Finset.sum_comm
  nlinarith [frobenius_nonneg Aᵀ, frobenius_nonneg A]

omit [DecidableEq D] in
theorem frobenius_add_le (A B : Matrix D D ℝ) :
    frobenius (A+B) ≤ frobenius A + frobenius B := by
  exact (by simpa only [frobenius, map_add] using norm_add_le (flatten A) (flatten B))

omit [DecidableEq D] in
@[simp] theorem frobenius_zero : frobenius (0 : Matrix D D ℝ) = 0 := by
  simp [frobenius]

omit [DecidableEq D] in
@[simp] theorem frobenius_neg (A : Matrix D D ℝ) : frobenius (-A) = frobenius A := by
  simp [frobenius]

omit [DecidableEq D] in
theorem frobenius_sub_le (A B : Matrix D D ℝ) :
    frobenius (A-B) ≤ frobenius A + frobenius B := by
  simpa only [frobenius, map_sub] using norm_sub_le (flatten A) (flatten B)

omit [DecidableEq D] in
theorem frobenius_sub_rev (A B : Matrix D D ℝ) : frobenius (A-B) = frobenius (B-A) := by
  simpa only [frobenius, map_sub] using norm_sub_rev (flatten A) (flatten B)

omit [DecidableEq D] in
theorem frobenius_smul (c : ℝ) (A : Matrix D D ℝ) :
    frobenius (c • A) = |c| * frobenius A := by
  simp [frobenius, norm_smul, Real.norm_eq_abs]

omit [DecidableEq D] in
@[simp] theorem frobenius_eq_zero (A : Matrix D D ℝ) : frobenius A = 0 ↔ A = 0 := by
  rw [frobenius, norm_eq_zero]
  constructor
  · intro h
    exact flatten.injective (by simpa using h)
  · rintro rfl
    simp

theorem spectralNorm_transpose (A : Matrix D D ℝ) : spectralNorm Aᵀ = spectralNorm A := by
  simpa only [spectralNorm, Matrix.l2_opNorm_toEuclideanCLM,
    Matrix.conjTranspose_eq_transpose_of_trivial] using (Matrix.l2_opNorm_conjTranspose A)

/-- Left multiplication is bounded by the spectral norm on the left and Frobenius on the right. -/
theorem frobenius_mul_left (A H : Matrix D D ℝ) :
    frobenius (A*H) ≤ spectralNorm A * frobenius H := by
  have hcol (j : D) :
      (∑ i, (A*H) i j ^ 2) ≤ spectralNorm A ^ 2 * (∑ i, H i j ^ 2) := by
    let x : EuclideanSpace ℝ D := WithLp.toLp 2 (fun i => H i j)
    have h := (Matrix.toEuclideanCLM (𝕜 := ℝ) A).le_opNorm x
    have he : Matrix.toEuclideanCLM (𝕜 := ℝ) A x =
        WithLp.toLp 2 (fun i => (A*H) i j) := by
      ext i
      simp [Matrix.mul_apply, Matrix.mulVec, dotProduct, x]
    rw [he] at h
    have hs : ‖WithLp.toLp 2 (fun i => (A*H) i j)‖ ^ 2 ≤
        spectralNorm A ^ 2 * ‖x‖ ^ 2 := by
      change ‖WithLp.toLp 2 (fun i => (A*H) i j)‖ ≤ spectralNorm A * ‖x‖ at h
      nlinarith [norm_nonneg (WithLp.toLp 2 (fun i => (A*H) i j)),
        norm_nonneg x, spectralNorm_nonneg A]
    simpa only [EuclideanSpace.real_norm_sq_eq, x] using hs
  have hs : frobenius (A*H) ^ 2 ≤ (spectralNorm A * frobenius H) ^ 2 := by
    rw [frobenius_sq, mul_pow, frobenius_sq]
    calc
      (∑ i, ∑ j, (A*H) i j ^ 2) = ∑ j, ∑ i, (A*H) i j ^ 2 := Finset.sum_comm
      _ ≤ ∑ j, spectralNorm A ^ 2 * (∑ i, H i j ^ 2) := Finset.sum_le_sum (fun j _ => hcol j)
      _ = spectralNorm A ^ 2 * (∑ i, ∑ j, H i j ^ 2) := by
        rw [← Finset.mul_sum, Finset.sum_comm]
  nlinarith [frobenius_nonneg (A*H), frobenius_nonneg H, spectralNorm_nonneg A,
    mul_nonneg (spectralNorm_nonneg A) (frobenius_nonneg H)]

/-- The corresponding right multiplication bound follows by transposition. -/
theorem frobenius_mul_right (H A : Matrix D D ℝ) :
    frobenius (H*A) ≤ frobenius H * spectralNorm A := by
  have h := frobenius_mul_left Aᵀ Hᵀ
  simpa only [← Matrix.transpose_mul, frobenius_transpose, spectralNorm_transpose,
    mul_comm (spectralNorm A)] using h

/-- The sharp mixed-norm perturbation bound for the literal quadratic congruence. -/
theorem frobenius_congruence_sub_le (A B H : Matrix D D ℝ) :
    frobenius (Aᵀ*H*A - Bᵀ*H*B) ≤
      (spectralNorm A + spectralNorm B) * spectralNorm (A-B) * frobenius H := by
  have he : Aᵀ*H*A - Bᵀ*H*B = (A-B)ᵀ*H*A + Bᵀ*H*(A-B) := by
    rw [Matrix.transpose_sub]
    noncomm_ring
  have h₁ := (frobenius_mul_right ((A-B)ᵀ*H) A).trans
    (mul_le_mul_of_nonneg_right (frobenius_mul_left (A-B)ᵀ H)
      (spectralNorm_nonneg A))
  have h₂ := (frobenius_mul_right (Bᵀ*H) (A-B)).trans
    (mul_le_mul_of_nonneg_right (frobenius_mul_left Bᵀ H)
      (spectralNorm_nonneg (A-B)))
  rw [spectralNorm_transpose] at h₁ h₂
  rw [he]
  exact (frobenius_add_le _ _).trans (by nlinarith)

end Komorebi.LSM.EuclideanMatrixNorms
