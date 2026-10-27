import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.LinearAlgebra.Matrix.ToLinearEquiv
import Mathlib.Tactic

/-!
# Coordinate changes for a normal-equation covector

These finite matrix identities are the basis-change part of WR15. The index
types may be empty. No orthonormality assumption is made on the change matrix.
The Hilbert-space interpretation and invertibility of a basis Gram matrix are
established in `CoordinateCovector`.
-/

set_option autoImplicit false

open Matrix

namespace KomorebiSpace.CoordinateCovector

variable {m n k : Type*} [Fintype m] [Fintype n]

/-- The residual of the coordinate normal equation, regarded as a covector. -/
def normalResidual (S : Matrix m n ℝ) (G : Matrix n n ℝ)
    (α : ℝ) (c : n → ℝ) (r : m → ℝ) : n → ℝ :=
  (Sᵀ * S + α • G) *ᵥ c - Sᵀ *ᵥ r

/-- The Gram matrix transforms by congruence, for every finite change matrix. -/
theorem gram_matrix_basis_change (B : Matrix m n ℝ) (C : Matrix n n ℝ) :
    (B * C)ᵀ * (B * C) = Cᵀ * (Bᵀ * B) * C := by
  simp only [Matrix.transpose_mul, Matrix.mul_assoc]

/-- The matrix of the observed correction transforms with the same change matrix. -/
theorem observation_matrix_basis_change
    (d : Matrix k m ℝ) (B : Matrix m n ℝ) (C : Matrix n n ℝ) :
    d * (B * C) = (d * B) * C := by
  rw [Matrix.mul_assoc]

/-- A transpose moves between the two factors of the real dot product. -/
theorem transpose_mulVec_dotProduct (C : Matrix m n ℝ)
    (q : m → ℝ) (v : n → ℝ) :
    dotProduct (Cᵀ *ᵥ q) v = dotProduct q (C *ᵥ v) := by
  classical
  simp only [Matrix.mulVec, dotProduct, Matrix.transpose_apply]
  simp_rw [Finset.sum_mul, Finset.mul_sum]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i hi
  apply Finset.sum_congr rfl
  intro j hj
  ring

variable [DecidableEq n]

/-- Applying an invertible change and its inverse preserves a coefficient vector. -/
theorem change_mul_inverse_mulVec (C : Matrix n n ℝ) (hC : IsUnit C)
    (c : n → ℝ) : C *ᵥ (C⁻¹ *ᵥ c) = c := by
  rw [Matrix.mulVec_mulVec, Matrix.mul_nonsing_inv C
    (C.isUnit_iff_isUnit_det.mp hC), Matrix.one_mulVec]

omit [Fintype m] in
/-- The changed coordinates represent exactly the same ambient correction. -/
theorem correction_basis_change (B : Matrix m n ℝ) (C : Matrix n n ℝ)
    (hC : IsUnit C) (c : n → ℝ) :
    (B * C) *ᵥ (C⁻¹ *ᵥ c) = B *ᵥ c := by
  rw [← Matrix.mulVec_mulVec, change_mul_inverse_mulVec C hC]

omit [Fintype m] in
/-- For independent columns, preservation of the correction forces the inverse
coordinate transformation. -/
theorem coordinates_basis_change (B : Matrix m n ℝ)
    (hB : Function.Injective B.mulVec) (C : Matrix n n ℝ)
    (hC : IsUnit C) (c c' : n → ℝ) :
    (B * C) *ᵥ c' = B *ᵥ c ↔ c' = C⁻¹ *ᵥ c := by
  constructor
  · intro h
    have hc : C *ᵥ c' = c := hB (by simpa only [Matrix.mulVec_mulVec] using h)
    have hi := congrArg (fun v => C⁻¹ *ᵥ v) hc
    simpa only [Matrix.mulVec_mulVec, Matrix.nonsing_inv_mul C
      (C.isUnit_iff_isUnit_det.mp hC), Matrix.one_mulVec] using hi
  · intro h
    rw [h, correction_basis_change B C hC]

/-- Covariance is derived from the changed coordinate normal equation. -/
theorem normalResidual_basis_change (S : Matrix m n ℝ) (G : Matrix n n ℝ)
    (C : Matrix n n ℝ) (hC : IsUnit C) (α : ℝ)
    (c : n → ℝ) (r : m → ℝ) :
    normalResidual (S * C) (Cᵀ * G * C) α (C⁻¹ *ᵥ c) r =
      Cᵀ *ᵥ normalResidual S G α c r := by
  simp only [normalResidual, Matrix.transpose_mul, Matrix.add_mulVec,
    Matrix.smul_mulVec, ← Matrix.mulVec_mulVec, Matrix.mulVec_sub,
    Matrix.mulVec_add, Matrix.mulVec_smul, change_mul_inverse_mulVec C hC]

/-- The inverse metric transforms in the reverse order. This identity even
holds for the total matrix inverse when the metric is singular. -/
theorem inverse_gram_basis_change (G C : Matrix n n ℝ) :
    (Cᵀ * G * C)⁻¹ = C⁻¹ * G⁻¹ * (C⁻¹)ᵀ := by
  simp only [Matrix.mul_inv_rev, ← Matrix.transpose_nonsing_inv, Matrix.mul_assoc]

/-- The inverse-Gram quadratic form is unchanged by any invertible coordinate
change; the covector transforms by the transpose. -/
theorem inverse_gram_quadratic_basis_change (G C : Matrix n n ℝ)
    (hC : IsUnit C) (q : n → ℝ) :
    dotProduct (Cᵀ *ᵥ q) ((Cᵀ * G * C)⁻¹ *ᵥ (Cᵀ *ᵥ q)) =
      dotProduct q (G⁻¹ *ᵥ q) := by
  have hCC : C * C⁻¹ = 1 :=
    Matrix.mul_nonsing_inv C (C.isUnit_iff_isUnit_det.mp hC)
  have hCT : (C⁻¹)ᵀ * Cᵀ = 1 := by
    rw [← Matrix.transpose_mul, hCC, Matrix.transpose_one]
  rw [inverse_gram_basis_change, transpose_mulVec_dotProduct]
  simp only [← Matrix.mulVec_mulVec]
  rw [Matrix.mulVec_mulVec q (C⁻¹)ᵀ Cᵀ, hCT, Matrix.one_mulVec,
    change_mul_inverse_mulVec C hC]

/-- The certificate computed from the changed equation has the same value. -/
theorem normalResidual_certificate_basis_change
    (S : Matrix m n ℝ) (G C : Matrix n n ℝ) (hC : IsUnit C)
    (α : ℝ) (c : n → ℝ) (r : m → ℝ) :
    let q' := normalResidual (S * C) (Cᵀ * G * C) α (C⁻¹ *ᵥ c) r
    dotProduct q' ((Cᵀ * G * C)⁻¹ *ᵥ q') =
      dotProduct (normalResidual S G α c r) (G⁻¹ *ᵥ normalResidual S G α c r) := by
  dsimp only
  rw [normalResidual_basis_change S G C hC]
  exact inverse_gram_quadratic_basis_change G C hC _

/-- Empty coefficient spaces produce the zero scalar certificate. -/
theorem zero_dimensional_certificate (G : Matrix (Fin 0) (Fin 0) ℝ)
    (q : Fin 0 → ℝ) : dotProduct q (G⁻¹ *ᵥ q) = 0 := by
  simp [dotProduct]

section FullBasis

open Module

variable {H : Type*} [AddCommGroup H] [Module ℝ H]

/-- Every invertible coordinate matrix determines a basis of the same entire
space, with its columns transformed by that matrix. -/
noncomputable def changedBasis (B : Basis n ℝ H) (C : Matrix n n ℝ)
    (hC : IsUnit C) : Basis n ℝ H :=
  B.map (Matrix.toLinearEquiv B C (C.isUnit_iff_isUnit_det.mp hC))

/-- The changed basis columns are exactly `B C`. -/
theorem changedBasis_apply (B : Basis n ℝ H) (C : Matrix n n ℝ)
    (hC : IsUnit C) (j : n) :
    changedBasis B C hC j = B.equivFun.symm (fun i => C i j) := by
  simp only [changedBasis, Basis.map_apply, Matrix.toLinearEquiv_apply,
    Matrix.toLin_self, Basis.equivFun_symm_apply]

/-- Synthesis in the changed full basis is synthesis after matrix transport. -/
theorem changedBasis_synthesis (B : Basis n ℝ H) (C : Matrix n n ℝ)
    (hC : IsUnit C) (c : n → ℝ) :
    (changedBasis B C hC).equivFun.symm c = B.equivFun.symm (C *ᵥ c) := by
  rw [changedBasis, Basis.map_equivFun]
  change Matrix.toLin B B C (B.equivFun.symm c) = B.equivFun.symm (C *ᵥ c)
  rw [Matrix.toLin_apply, ← B.equivFun_apply,
    LinearEquiv.apply_symm_apply, Basis.equivFun_symm_apply]

/-- The inverse coordinates synthesize the same vector in the changed basis. -/
theorem changedBasis_same_vector (B : Basis n ℝ H) (C : Matrix n n ℝ)
    (hC : IsUnit C) (c : n → ℝ) :
    (changedBasis B C hC).equivFun.symm (C⁻¹ *ᵥ c) = B.equivFun.symm c := by
  rw [changedBasis_synthesis, change_mul_inverse_mulVec C hC]

/-- Coordinates of a fixed vector transform by the inverse matrix. -/
theorem changedBasis_coordinates (B : Basis n ℝ H) (C : Matrix n n ℝ)
    (hC : IsUnit C) (x : H) :
    (changedBasis B C hC).equivFun x = C⁻¹ *ᵥ B.equivFun x := by
  apply (changedBasis B C hC).equivFun.symm.injective
  rw [LinearEquiv.symm_apply_apply, changedBasis_same_vector,
    LinearEquiv.symm_apply_apply]

end FullBasis

end KomorebiSpace.CoordinateCovector
