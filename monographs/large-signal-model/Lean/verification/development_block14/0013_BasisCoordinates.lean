import KomorebiLSM.NoisySpectralSubspace
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

set_option autoImplicit false
namespace Komorebi.LSM.BasisCoordinates
open Komorebi.LSM.SubspaceCoordinates
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup F] [InnerProductSpace ℝ F]
variable [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]
variable {r : ℕ}

theorem matrix_action (U : OrthonormalBasis (Fin r) ℝ E)
    (V : OrthonormalBasis (Fin r) ℝ F) (T : E →ₗ[ℝ] F)
    (y : EuclideanSpace ℝ (Fin r)) :
    (LinearMap.toMatrix U.toBasis V.toBasis T).toEuclideanLin y =
      V.repr (T (U.repr.symm y)) := by
  have h := T.toMatrix_mulVec_repr U.toBasis V.toBasis (U.repr.symm y)
  ext i
  have he : (fun j => U.toBasis.repr (U.repr.symm y) j) = WithLp.ofLp y := by
    funext j
    simp
  rw [he] at h
  exact congrFun h i

variable {P Q : Submodule ℝ E}

/-- The matrix whose entries are the inner products of estimated and true basis
vectors: in ambient Euclidean coordinates this is `Uhatᵀ U`. -/
noncomputable def cross (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) : Matrix (Fin r) (Fin r) ℝ :=
  LinearMap.toMatrix U.toBasis V.toBasis (project P Q).toLinearMap

/-- Estimated orthonormal coordinates of an ambient vector. -/
noncomputable def coordinates (V : OrthonormalBasis (Fin r) ℝ Q) :
    E →L[ℝ] EuclideanSpace ℝ (Fin r) :=
  V.repr.toContinuousLinearEquiv.toContinuousLinearMap.comp Q.orthogonalProjectionOnto

/-- The column map of the true orthonormal basis. -/
noncomputable def synthesis (U : OrthonormalBasis (Fin r) ℝ P) :
    EuclideanSpace ℝ (Fin r) →L[ℝ] E :=
  P.subtypeL.comp U.repr.symm.toContinuousLinearEquiv.toContinuousLinearMap

theorem coordinates_entry (V : OrthonormalBasis (Fin r) ℝ Q) (x : E) (i : Fin r) :
    coordinates V x i = inner ℝ (V i:E) x := by
  change V.repr (Q.orthogonalProjectionOnto x) i = _
  rw [V.repr_apply_apply]
  change inner ℝ (V i:E) (Q.starProjection x) = _
  rw [← Q.inner_starProjection_left_eq_right,
    Q.starProjection_eq_self_iff.mpr (V i).property]

theorem cross_entry (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) (i j : Fin r) :
    cross U V i j = inner ℝ (V i:E) (U j:E) := by
  simp only [cross, LinearMap.toMatrix_apply, OrthonormalBasis.coe_toBasis,
    OrthonormalBasis.coe_toBasis_repr_apply]
  exact coordinates_entry V (U j:E) i

theorem cross_action (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) (y : EuclideanSpace ℝ (Fin r)) :
    (cross U V).toEuclideanLin y = V.repr (project P Q (U.repr.symm y)) :=
  matrix_action U V (project P Q).toLinearMap y

theorem cross_lower (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ‖P.starProjection-Q.starProjection‖ ≤ δ)
    (y : EuclideanSpace ℝ (Fin r)) :
    Real.sqrt (1-δ^2)*‖y‖ ≤ ‖(cross U V).toEuclideanLin y‖ := by
  rw [cross_action, V.repr.norm_map]
  have h := coordinate_lower P Q δ hδ hsmall hgap (U.repr.symm y)
  rwa [U.repr.symm.norm_map] at h

/-- Actual smallest singular value of the square cross-basis matrix. -/
theorem cross_min_singular (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) (hr : 0 < r) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ‖P.starProjection-Q.starProjection‖ ≤ δ) :
    Real.sqrt (1-δ^2) ≤ (cross U V).toEuclideanLin.singularValues (r-1) := by
  have hd : Module.finrank ℝ (EuclideanSpace ℝ (Fin r)) = r := by simp
  let i : Fin (Module.finrank ℝ (EuclideanSpace ℝ (Fin r))) := ⟨r-1, by omega⟩
  have h := cross_lower U V δ hδ hsmall hgap (Spectral.rightBasis (cross U V).toEuclideanLin i)
  rw [(Spectral.rightBasis (cross U V).toEuclideanLin).norm_eq_one, mul_one,
    Spectral.image_basis_norm] at h
  exact h

theorem basis_dimensions (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) : Module.finrank ℝ P = Module.finrank ℝ Q :=
  U.toBasis.finrank_eq_card.trans V.toBasis.finrank_eq_card.symm

theorem coordinates_injective (U : OrthonormalBasis (Fin r) ℝ P)
    (V : OrthonormalBasis (Fin r) ℝ Q) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ‖P.starProjection-Q.starProjection‖ ≤ δ) :
    Function.Injective ((coordinates V).comp P.subtypeL) := by
  intro x y h
  apply coordinate_injective P Q δ hδ hsmall hgap
  exact V.repr.injective h

end Komorebi.LSM.BasisCoordinates
