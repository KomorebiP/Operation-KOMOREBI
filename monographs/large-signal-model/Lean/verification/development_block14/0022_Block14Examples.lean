import KomorebiLSM.FiniteTableP32
import KomorebiLSM.Block13Examples

set_option autoImplicit false
namespace Komorebi.LSM.Block14Examples
open Komorebi.LSM.Spectral Komorebi.LSM.BasisCoordinates

/-- The sole singular value of scalar multiplication by two is at index zero. -/
theorem double_first_singular :
    ((2:ℝ) • (LinearMap.id : ℝ →ₗ[ℝ] ℝ)).singularValues 0 = 2 := by
  have hr : Module.finrank ℝ (((2:ℝ) • (LinearMap.id : ℝ →ₗ[ℝ] ℝ)).range) = 1 := by
    have hsur : Function.Surjective ((2:ℝ) • (LinearMap.id : ℝ →ₗ[ℝ] ℝ)) := by
      intro y
      refine ⟨y/2, ?_⟩
      change (2:ℝ)*(y/2) = y
      ring
    rw [LinearMap.range_eq_top.mpr hsur]
    simp
  have h := Block13Examples.double_leastPositive
  simpa [leastPositive, hr] using h

theorem discard_all_scalar_modes :
    ‖(leadingLeft (((2:ℝ) • ContinuousLinearMap.id ℝ ℝ).toLinearMap) 0 (by simp))ᗮ.starProjection.comp
      ((2:ℝ) • ContinuousLinearMap.id ℝ ℝ)‖ = 2 := by
  rw [leadingLeft_tail_norm]
  exact double_first_singular

theorem retain_all_scalar_modes :
    ‖(leadingLeft (((2:ℝ) • ContinuousLinearMap.id ℝ ℝ).toLinearMap) 1 (by simp))ᗮ.starProjection.comp
      ((2:ℝ) • ContinuousLinearMap.id ℝ ℝ)‖ = 0 := by
  rw [leadingLeft_tail_norm]
  exact singularValue_zero_at_max_rank _ 1 (by simp)

/-- A wide rank-one table has a zero second singular value. -/
theorem rectangular_maximum_rank_tail_zero : Block13Examples.firstCoordinate.singularValues 1 = 0 :=
  singularValue_zero_at_max_rank _ 1 (by simp)

/-- The universal perturbation constant one is attained by scalar two versus zero. -/
theorem scalar_perturbation_sharp :
    |((2:ℝ) • (LinearMap.id : ℝ →ₗ[ℝ] ℝ)).singularValues 0 -
      (0 : ℝ →ₗ[ℝ] ℝ).singularValues 0| =
      ‖((2:ℝ) • ContinuousLinearMap.id ℝ ℝ) - 0‖ := by
  rw [double_first_singular]
  simp [norm_smul, ContinuousLinearMap.norm_id]

theorem same_basis_cross_identity {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    [FiniteDimensional ℝ E] (P : Submodule ℝ E) (r : ℕ)
    (U : OrthonormalBasis (Fin r) ℝ P) : cross U U = 1 := by
  ext i j
  rw [cross_entry, Matrix.one_apply]
  exact U.inner_eq_ite i j

theorem zero_rank_tail_is_zero :
    ‖(leadingLeft (0 : ℝ →ₗ[ℝ] ℝ) 0 (by simp))ᗮ.starProjection.comp
      (0 : ℝ →L[ℝ] ℝ)‖ = 0 := by simp

end Komorebi.LSM.Block14Examples
