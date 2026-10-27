import KomorebiLSM.DataSpan
import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.Analysis.InnerProductSpace.Projection.FiniteDimensional

/-! Canonical finite-dimensional orthogonal generalized inverse. -/
set_option autoImplicit false
namespace Komorebi.LSM.Identification
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup F] [InnerProductSpace ℝ F]
variable [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]

noncomputable def retained (A : E →ₗ[ℝ] F) : E →ₗ[ℝ] E :=
  A.kerᗮ.starProjection.toLinearMap

omit [FiniteDimensional ℝ F] in
theorem retained_apply (A : E →ₗ[ℝ] F) (x : E) :
    retained A x = x - A.ker.starProjection x := by
  exact Submodule.starProjection_orthogonal_val _

omit [FiniteDimensional ℝ F] in
theorem retained_kernel (A : E →ₗ[ℝ] F) : A.ker ≤ (retained A).ker := by
  intro x hx
  change retained A x = 0
  rw [retained_apply, A.ker.starProjection_eq_self_iff.mpr hx, sub_self]

noncomputable def pinv (A : E →ₗ[ℝ] F) : F →ₗ[ℝ] E :=
  (onRange A (retained A) (retained_kernel A)).comp A.range.orthogonalProjectionOnto.toLinearMap

@[simp] theorem pinv_apply_image (A : E →ₗ[ℝ] F) (x : E) :
    pinv A (A x) = retained A x := by
  change onRange A (retained A) (retained_kernel A) (A.range.orthogonalProjectionOnto (A x)) = _
  have he : A.range.orthogonalProjectionOnto (A x) = A.rangeRestrict x :=
    A.range.orthogonalProjectionOnto_mem_subspace_eq_self (A.rangeRestrict x)
  rw [he, onRange_apply]

omit [FiniteDimensional ℝ F] in
theorem apply_retained (A : E →ₗ[ℝ] F) (x : E) : A (retained A x) = A x := by
  rw [retained_apply, map_sub]
  have hz : A (A.ker.starProjection x) = 0 := A.ker.starProjection_apply_mem x
  rw [hz, sub_zero]

theorem pinv_apply_mem (A : E →ₗ[ℝ] F) (y : F) : pinv A y ∈ A.kerᗮ := by
  obtain ⟨x,hx⟩ := (A.range.orthogonalProjectionOnto y).property
  have he : A.range.orthogonalProjectionOnto y = A.rangeRestrict x := Subtype.ext hx.symm
  change onRange A (retained A) (retained_kernel A) (A.range.orthogonalProjectionOnto y) ∈ _
  rw [he, onRange_apply]
  exact A.kerᗮ.starProjection_apply_mem x

theorem apply_pinv (A : E →ₗ[ℝ] F) (y : F) : A (pinv A y) = A.range.starProjection y := by
  obtain ⟨x,hx⟩ := (A.range.orthogonalProjectionOnto y).property
  have he : A.range.orthogonalProjectionOnto y = A.rangeRestrict x := Subtype.ext hx.symm
  change A (onRange A (retained A) (retained_kernel A) (A.range.orthogonalProjectionOnto y)) = _
  rw [he, onRange_apply, apply_retained]
  exact hx

theorem penrose_one (A : E →ₗ[ℝ] F) : A.comp ((pinv A).comp A) = A := by
  apply LinearMap.ext
  intro x
  exact (congrArg A (pinv_apply_image A x)).trans (apply_retained A x)

theorem penrose_two (A : E →ₗ[ℝ] F) : (pinv A).comp (A.comp (pinv A)) = pinv A := by
  apply LinearMap.ext
  intro y
  change pinv A (A (pinv A y)) = _
  rw [pinv_apply_image]
  exact A.kerᗮ.starProjection_eq_self_iff.mpr (pinv_apply_mem A y)

theorem penrose_range_projection (A : E →ₗ[ℝ] F) :
    A.comp (pinv A) = A.range.starProjection.toLinearMap := by
  apply LinearMap.ext
  exact apply_pinv A

theorem penrose_source_projection (A : E →ₗ[ℝ] F) :
    (pinv A).comp A = A.kerᗮ.starProjection.toLinearMap := by
  apply LinearMap.ext
  exact pinv_apply_image A

theorem moore_penrose_fit (A : E →ₗ[ℝ] F) (B : E →ₗ[ℝ] F)
    (h : A.ker ≤ B.ker) : (B.comp (pinv A)).comp A = B :=
  generalized_inverse_fit A B (pinv A) h (penrose_one A)
end Komorebi.LSM.Identification
