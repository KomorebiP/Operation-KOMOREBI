import KomorebiSpace.CoordinateBasisChange
import KomorebiSpace.ProtectedRegularizedRepair
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.LinearAlgebra.Matrix.ToLin

set_option autoImplicit false

/-!
# Coordinate covectors in an arbitrary full Hilbert basis

The basis is a basis of the entire correction space.  Coefficients and
covectors are finite real coordinate functions; every norm in the certificate
is the original Hilbert norm.  No nonemptiness assumption is made on the basis
index, so the zero-dimensional correction space is included.
-/

noncomputable section
universe u v w
namespace KomorebiSpace.CoordinateCovector
open Module
open scoped RealInnerProductSpace Matrix

variable {ι : Type u} [Fintype ι]
variable {H : Type v} [NormedAddCommGroup H] [InnerProductSpace ℝ H]

/-- Synthesis in a full, possibly nonorthonormal basis. -/
def synthesis (B : Basis ι ℝ H) (c : ι → ℝ) : H := B.equivFun.symm c

/-- The coordinate covector of a vector consists of its pairings with the basis. -/
def pairings (B : Basis ι ℝ H) (x : H) : ι → ℝ := fun i => ⟪B i, x⟫

/-- The Gram matrix uses the actual Hilbert inner product. -/
def gram (B : Basis ι ℝ H) : Matrix ι ι ℝ := fun i j => ⟪B i, B j⟫

theorem synthesis_eq_sum (B : Basis ι ℝ H) (c : ι → ℝ) :
    synthesis B c = ∑ i, c i • B i := by
  exact B.equivFun_symm_apply c

theorem synthesis_injective (B : Basis ι ℝ H) : Function.Injective (synthesis B) :=
  B.equivFun.symm.injective

theorem pairings_synthesis (B : Basis ι ℝ H) (c : ι → ℝ) :
    pairings B (synthesis B c) = (gram B) *ᵥ c := by
  ext i
  simp [pairings, synthesis_eq_sum, gram, Matrix.mulVec, dotProduct, inner_sum,
    real_inner_smul_right, mul_comm]

theorem inner_synthesis (B : Basis ι ℝ H) (c : ι → ℝ) (x : H) :
    ⟪synthesis B c, x⟫ = dotProduct c (pairings B x) := by
  simp [synthesis_eq_sum, pairings, dotProduct, sum_inner, real_inner_smul_left]

theorem gram_posDef (B : Basis ι ℝ H) : (gram B).PosDef := by
  classical
  refine Matrix.PosDef.of_dotProduct_mulVec_pos ?_ ?_
  · ext i j
    simp [Matrix.conjTranspose_apply, gram, real_inner_comm]
  · intro c hc
    have hz : synthesis B c ≠ 0 := by
      intro h
      apply hc
      exact B.equivFun.symm.injective (h.trans (map_zero B.equivFun.symm).symm)
    have hp := real_inner_self_pos.mpr hz
    rw [inner_synthesis, pairings_synthesis] at hp
    simpa using hp

variable [DecidableEq ι]

theorem gram_isUnit (B : Basis ι ℝ H) : IsUnit (gram B) := (gram_posDef B).isUnit

theorem inverse_gram_pairings (B : Basis ι ℝ H) (x : H) :
    (gram B)⁻¹ *ᵥ pairings B x = B.equivFun x := by
  have h : pairings B x = gram B *ᵥ B.equivFun x := by
    rw [← pairings_synthesis]
    simp [synthesis]
  rw [h, Matrix.mulVec_mulVec,
    Matrix.nonsing_inv_mul _ ((gram B).isUnit_iff_isUnit_det.mp (gram_isUnit B)),
    Matrix.one_mulVec]

theorem reconstruct (B : Basis ι ℝ H) (x : H) :
    x = synthesis B ((gram B)⁻¹ *ᵥ pairings B x) := by
  rw [inverse_gram_pairings]
  simp [synthesis]

theorem norm_sq_pairings (B : Basis ι ℝ H) (x : H) :
    ‖x‖ ^ 2 = dotProduct (pairings B x) ((gram B)⁻¹ *ᵥ pairings B x) := by
  rw [← real_inner_self_eq_norm_sq]
  conv_lhs => lhs; rw [reconstruct B x]
  rw [inner_synthesis, dotProduct_comm]

section OrthonormalCoordinates
variable {κ : Type w} [Fintype κ]

/-- Coordinates in an orthonormal basis, used only for the residual space. -/
def orthonormalCoordinates {Y : Type*} [NormedAddCommGroup Y]
    [InnerProductSpace ℝ Y] (e : OrthonormalBasis κ ℝ Y) (y : Y) : κ → ℝ :=
  fun j => ⟪e j, y⟫

/-- Columns of an arbitrary basis in orthonormal Hilbert coordinates. -/
def basisMatrix (e : OrthonormalBasis κ ℝ H) (B : Basis ι ℝ H) : Matrix κ ι ℝ :=
  fun j i => ⟪e j, B i⟫

omit [DecidableEq ι] in
theorem gram_eq_transpose_mul (e : OrthonormalBasis κ ℝ H) (B : Basis ι ℝ H) :
    gram B = (basisMatrix e B)ᵀ * basisMatrix e B := by
  ext i j
  change ⟪B i, B j⟫ = ∑ k, ⟪e k, B i⟫ * ⟪e k, B j⟫
  rw [← e.sum_inner_mul_inner (B i) (B j)]
  apply Finset.sum_congr rfl
  intro k _
  rw [real_inner_comm (B i) (e k)]

variable {Y : Type*} [NormedAddCommGroup Y] [InnerProductSpace ℝ Y]

/-- The literal observation matrix has columns equal to the observed basis vectors. -/
def operatorMatrix (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) : Matrix κ ι ℝ := fun j i => ⟪e j, T (B i)⟫

omit [DecidableEq ι] in
theorem operatorMatrix_synthesis (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) (c : ι → ℝ) :
    orthonormalCoordinates e (T (synthesis B c)) = operatorMatrix B e T *ᵥ c := by
  ext j
  simp [orthonormalCoordinates, synthesis_eq_sum, operatorMatrix, map_sum,
    Matrix.mulVec, dotProduct, inner_sum, real_inner_smul_right, mul_comm]

variable [CompleteSpace H] [CompleteSpace Y]

omit [DecidableEq ι] in
theorem pairings_adjoint (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) (y : Y) :
    pairings B (T.adjoint y) = (operatorMatrix B e T)ᵀ *ᵥ orthonormalCoordinates e y := by
  ext i
  change ⟪B i, T.adjoint y⟫ = ∑ j, ⟪e j, T (B i)⟫ * ⟪e j, y⟫
  rw [ContinuousLinearMap.adjoint_inner_right, ← e.sum_inner_mul_inner (T (B i)) y]
  apply Finset.sum_congr rfl
  intro j _
  rw [real_inner_comm (T (B i)) (e j)]

/-- The displayed normal-equation residual is derived to be the covector of the
accepted Hilbert normal residual; this is not an additional assumption. -/
theorem normalResidual_eq_pairings (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) (α : ℝ) (c : ι → ℝ) (r : Y) :
    normalResidual (operatorMatrix B e T) (gram B) α c (orthonormalCoordinates e r) =
      pairings B (RegularizedHilbertRepair.gradient T α r (synthesis B c)) := by
  have hT := pairings_adjoint B e T (T (synthesis B c))
  rw [operatorMatrix_synthesis] at hT
  have hr := pairings_adjoint B e T r
  have hG := pairings_synthesis B c
  ext i
  simp only [normalResidual, Matrix.add_mulVec, Matrix.smul_mulVec,
    Matrix.mul_smul, ← Matrix.mulVec_mulVec, Pi.sub_apply, Pi.add_apply,
    Pi.smul_apply, smul_eq_mul]
  change _ = ⟪B i, T.adjoint (T (synthesis B c)) + α • synthesis B c - T.adjoint r⟫
  rw [inner_sub_right, inner_add_right, real_inner_smul_right]
  rw [← congrFun hT i, ← congrFun hr i, ← congrFun hG i]
  rfl

/-- WR15: the actual normal residual is obtained by the inverse Gram metric. -/
theorem gradient_eq_synthesis_inverse_normalResidual
    (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) (α : ℝ) (c : ι → ℝ) (r : Y) :
    RegularizedHilbertRepair.gradient T α r (synthesis B c) =
      synthesis B ((gram B)⁻¹ *ᵥ
        normalResidual (operatorMatrix B e T) (gram B) α c (orthonormalCoordinates e r)) := by
  rw [normalResidual_eq_pairings]
  exact reconstruct B _

/-- WR15: the Gram-corrected scalar is the squared original Hilbert norm. -/
theorem gradient_norm_sq_eq_normalResidual
    (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) (α : ℝ) (c : ι → ℝ) (r : Y) :
    ‖RegularizedHilbertRepair.gradient T α r (synthesis B c)‖ ^ 2 =
      dotProduct
        (normalResidual (operatorMatrix B e T) (gram B) α c (orthonormalCoordinates e r))
        ((gram B)⁻¹ *ᵥ
          normalResidual (operatorMatrix B e T) (gram B) α c (orthonormalCoordinates e r)) := by
  rw [normalResidual_eq_pairings]
  exact norm_sq_pairings B _

end OrthonormalCoordinates

end KomorebiSpace.CoordinateCovector
