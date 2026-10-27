import PaperXI.HyperbolicSpace
import Mathlib.LinearAlgebra.Determinant

/-! Determinants of the literal inverse-dual and hyperbolic difference maps.
All identities are established for the actual endomorphisms. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HyperbolicDeterminant

variable {k U : Type*} [Field k] [AddCommGroup U] [Module k U]

/-- The inverse difference factors through the original difference. -/
theorem inverse_difference (a : U ≃ₗ[k] U) :
    a.symm.toLinearMap - 1 = (-1 : k) • (a.symm.toLinearMap * (a.toLinearMap - 1)) := by
  apply LinearMap.ext
  intro u
  change a.symm u - u = (-1 : k) • a.symm (a u - u)
  rw [map_sub, a.symm_apply_apply, neg_one_smul, neg_sub]

/-- The inverse-dual difference is exactly the dual of the inverse difference. -/
theorem dual_difference (a : U ≃ₗ[k] U) :
    a.symm.dualMap.toLinearMap - 1 = (a.symm.toLinearMap - 1).dualMap := by
  apply LinearMap.ext
  intro l
  apply LinearMap.ext
  intro u
  change l (a.symm u) - l u = l (a.symm u - u)
  rw [map_sub]

variable [FiniteDimensional k U]

/-- The inverse-dual determinant identity in source 12.8. -/
theorem dual_difference_det (a : U ≃ₗ[k] U) :
    LinearMap.det (a.symm.dualMap.toLinearMap - 1) =
      (-1 : k) ^ Module.finrank k U * (LinearMap.det a.toLinearMap)⁻¹ *
        LinearMap.det (a.toLinearMap - 1) := by
  rw [dual_difference, LinearMap.det_dualMap, inverse_difference, LinearMap.det_smul,
    map_mul, LinearEquiv.det_coe_symm]
  ring

omit [FiniteDimensional k U] in
/-- The actual hyperbolic difference is a block product of the two differences. -/
theorem action_difference (a : U ≃ₗ[k] U) :
    (HyperbolicSpace.action a).toLinearMap - 1 =
      (a.toLinearMap - 1).prodMap (a.symm.dualMap.toLinearMap - 1) := by
  apply LinearMap.ext
  intro x
  apply Prod.ext <;> rfl

/-- The full determinant is the stated sign times determinant inverse times a square. -/
theorem total_difference_det (a : U ≃ₗ[k] U) :
    LinearMap.det ((HyperbolicSpace.action a).toLinearMap - 1) =
      (-1 : k) ^ Module.finrank k U * (LinearMap.det a.toLinearMap)⁻¹ *
        LinearMap.det (a.toLinearMap - 1) ^ 2 := by
  rw [action_difference, LinearMap.det_prodMap, dual_difference_det]
  ring

/-- The hyperbolic action itself has determinant one. -/
theorem action_det (a : U ≃ₗ[k] U) : LinearMap.det (HyperbolicSpace.action a).toLinearMap = 1 := by
  change LinearMap.det (a.toLinearMap.prodMap a.symm.dualMap.toLinearMap) = 1
  rw [LinearMap.det_prodMap]
  change LinearMap.det a.toLinearMap * LinearMap.det a.symm.toLinearMap.dualMap = 1
  rw [LinearMap.det_dualMap]
  exact a.det_mul_det_symm

end PaperXI.HyperbolicDeterminant
