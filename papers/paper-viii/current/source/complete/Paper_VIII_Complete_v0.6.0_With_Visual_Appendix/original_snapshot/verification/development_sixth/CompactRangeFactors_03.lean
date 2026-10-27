module
public import SmallCoreNorms
public import Mathlib.Analysis.InnerProductSpace.PiL2
public import Mathlib.Analysis.InnerProductSpace.Subspace
public import Mathlib.Analysis.InnerProductSpace.Adjoint
public import Mathlib.Tactic

/-! Author: Komorebi P. Actual compact orthonormal column-space factorization.
This is exact mathematics, not a floating-point QR implementation. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII.SmallCore
open scoped BigOperators Matrix Classical
variable {m n : Type*} [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n]

noncomputable def columnSpace (A : Matrix m n ℂ) : Submodule ℂ (EuclideanSpace ℂ m) :=
  LinearMap.range (Matrix.toEuclideanLin A)
noncomputable def compactDim (A : Matrix m n ℂ) : ℕ := Module.finrank ℂ (columnSpace A)
noncomputable def columnBasis (A : Matrix m n ℂ) :
    OrthonormalBasis (Fin (compactDim A)) ℂ (columnSpace A) :=
  stdOrthonormalBasis ℂ (columnSpace A)
noncomputable def compactQ (A : Matrix m n ℂ) : Matrix m (Fin (compactDim A)) ℂ :=
  LinearMap.toMatrix (columnBasis A).toBasis (EuclideanSpace.basisFun m ℂ).toBasis
    (columnSpace A).subtype
noncomputable def compactR (A : Matrix m n ℂ) : Matrix (Fin (compactDim A)) n ℂ :=
  LinearMap.toMatrix (EuclideanSpace.basisFun n ℂ).toBasis (columnBasis A).toBasis
    (Matrix.toEuclideanLin A).rangeRestrict

omit [DecidableEq m] in
theorem compactDim_eq_rank (A : Matrix m n ℂ) : compactDim A = A.rank := by
  unfold compactDim columnSpace
  rw [Matrix.toEuclideanLin_eq_toLin_orthonormal]
  exact (Matrix.rank_eq_finrank_range_toLin A
    (EuclideanSpace.basisFun m ℂ).toBasis (EuclideanSpace.basisFun n ℂ).toBasis).symm

omit [DecidableEq m] in
theorem compactQ_apply (A : Matrix m n ℂ) (i : m) (j : Fin (compactDim A)) :
    compactQ A i j = (columnBasis A j : EuclideanSpace ℂ m) i := by
  simp [compactQ,LinearMap.toMatrix_apply]

omit [DecidableEq m] in
theorem compactQ_isometry (A : Matrix m n ℂ) : (compactQ A)ᴴ*compactQ A = 1 := by
  ext i j
  have h := orthonormal_iff_ite.mp (columnBasis A).orthonormal i j
  simpa only [Submodule.coe_inner,PiLp.inner_apply,RCLike.inner_apply,
    Matrix.mul_apply,Matrix.conjTranspose_apply,compactQ_apply,Matrix.one_apply,
    Complex.star_def,mul_comm] using h

omit [DecidableEq m] in
set_option backward.isDefEq.respectTransparency false in
theorem compact_factorization (A : Matrix m n ℂ) : compactQ A * compactR A = A := by
  unfold compactQ compactR
  rw [←LinearMap.toMatrix_comp]
  have he : (columnSpace A).subtype ∘ₗ (Matrix.toEuclideanLin A).rangeRestrict =
      Matrix.toEuclideanLin A := by ext x i; rfl
  rw [he,Matrix.toEuclideanLin_eq_toLin_orthonormal]
  exact LinearMap.toMatrix_toLin _ _ _

theorem compactR_is_compression (A : Matrix m n ℂ) : compactR A = (compactQ A)ᴴ*A := by
  calc
    compactR A = (compactQ A)ᴴ*(compactQ A*compactR A) := by
      rw [←Matrix.mul_assoc,compactQ_isometry,Matrix.one_mul]
    _ = (compactQ A)ᴴ*A := congrArg (fun B => (compactQ A)ᴴ*B) (compact_factorization A)

theorem compactR_full_row_rank (A : Matrix m n ℂ) :
    (compactR A).rank = compactDim A := by
  apply le_antisymm
  · simpa only [Fintype.card_fin] using Matrix.rank_le_card_height (compactR A)
  · calc
      compactDim A = A.rank := compactDim_eq_rank A
      _ = (compactQ A * compactR A).rank := congrArg Matrix.rank (compact_factorization A).symm
      _ ≤ (compactR A).rank := Matrix.rank_mul_le_right _ _

theorem compact_rank_zero (A : Matrix m n ℂ) : compactDim A = 0 ↔ A = 0 := by
  constructor
  · intro h
    let : IsEmpty (Fin (compactDim A)) := ⟨fun i => by have := i.isLt; omega⟩
    calc
      A = compactQ A * compactR A := (compact_factorization A).symm
      _ = 0 := by ext i j; simp [Matrix.mul_apply]
  · intro h
    simp [compactDim_eq_rank,h]

end KomorebiPaperVIII.SmallCore
