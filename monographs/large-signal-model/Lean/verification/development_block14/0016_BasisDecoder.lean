import KomorebiLSM.BasisCoordinates

set_option autoImplicit false
namespace Komorebi.LSM.BasisCoordinates
open Komorebi.LSM.SubspaceCoordinates
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [FiniteDimensional ℝ E] {r : ℕ} {P Q : Submodule ℝ E}

/-- The explicit formula `U (Uhatᵀ U)⁻¹`, as an operator on Euclidean coordinates. -/
noncomputable def decoder (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) : EuclideanSpace ℝ (Fin r) →L[ℝ] E :=
  (synthesis U).comp ((cross U V)⁻¹.toEuclideanLin.toContinuousLinearMap)

theorem cross_inverse_matrix (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ‖P.starProjection-Q.starProjection‖ ≤ δ) :
    (cross U V)⁻¹ = LinearMap.toMatrix V.toBasis U.toBasis
      (coordinateEquiv P Q δ hδ hsmall hgap (basis_dimensions U V)).symm.toLinearMap := by
  apply Matrix.inv_eq_left_inv
  let e := coordinateEquiv P Q δ hδ hsmall hgap (basis_dimensions U V)
  change LinearMap.toMatrix V.toBasis U.toBasis e.symm.toLinearMap *
    LinearMap.toMatrix U.toBasis V.toBasis e.toLinearMap = 1
  rw [← LinearMap.toMatrix_comp U.toBasis V.toBasis U.toBasis]
  have he : e.symm.toLinearMap.comp e.toLinearMap = LinearMap.id := by
    ext x
    exact e.symm_apply_apply x
  rw [he, LinearMap.toMatrix_id]

theorem decoder_apply (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ‖P.starProjection-Q.starProjection‖ ≤ δ)
    (y : EuclideanSpace ℝ (Fin r)) :
    decoder U V y =
      ((coordinateEquiv P Q δ hδ hsmall hgap (basis_dimensions U V)).symm
        (V.repr.symm y) : E) := by
  change (U.repr.symm ((cross U V)⁻¹.toEuclideanLin y) : E) = _
  rw [cross_inverse_matrix U V δ hδ hsmall hgap, matrix_action,
    U.repr.symm_apply_apply]

theorem decoder_coordinates (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ‖P.starProjection-Q.starProjection‖ ≤ δ) (x : P) :
    decoder U V (coordinates V (x:E)) = (x:E) := by
  rw [decoder_apply U V δ hδ hsmall hgap]
  change ((coordinateEquiv P Q δ hδ hsmall hgap (basis_dimensions U V)).symm
    (V.repr.symm (V.repr (project P Q x))) : E) = _
  rw [V.repr.symm_apply_apply]
  exact congrArg Subtype.val
    ((coordinateEquiv P Q δ hδ hsmall hgap (basis_dimensions U V)).symm_apply_apply x)

theorem coordinates_decoder (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ‖P.starProjection-Q.starProjection‖ ≤ δ)
    (y : EuclideanSpace ℝ (Fin r)) : coordinates V (decoder U V y) = y := by
  rw [decoder_apply U V δ hδ hsmall hgap]
  change V.repr (project P Q
    ((coordinateEquiv P Q δ hδ hsmall hgap (basis_dimensions U V)).symm
      (V.repr.symm y))) = y
  have he := (coordinateEquiv P Q δ hδ hsmall hgap (basis_dimensions U V)).apply_symm_apply
    (V.repr.symm y)
  change project P Q _ = _ at he
  rw [he, V.repr.apply_symm_apply]

theorem decoder_mem_true (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) (y : EuclideanSpace ℝ (Fin r)) :
    decoder U V y ∈ P := (U.repr.symm ((cross U V)⁻¹.toEuclideanLin y)).property

theorem decoder_norm_bound (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ‖P.starProjection-Q.starProjection‖ ≤ δ) :
    ‖decoder U V‖ ≤ (Real.sqrt (1-δ^2))⁻¹ := by
  apply ContinuousLinearMap.opNorm_le_bound _ (inv_nonneg.mpr (Real.sqrt_nonneg _))
  intro y
  rw [decoder_apply U V δ hδ hsmall hgap]
  have h := (coordinateEquiv P Q δ hδ hsmall hgap (basis_dimensions U V)).symm.toContinuousLinearMap.le_opNorm
    (V.repr.symm y)
  exact h.trans (by
    rw [V.repr.symm.norm_map]
    exact mul_le_mul_of_nonneg_right
      (coordinate_inverse_bound P Q δ hδ hsmall hgap (basis_dimensions U V)) (norm_nonneg y))

end Komorebi.LSM.BasisCoordinates
