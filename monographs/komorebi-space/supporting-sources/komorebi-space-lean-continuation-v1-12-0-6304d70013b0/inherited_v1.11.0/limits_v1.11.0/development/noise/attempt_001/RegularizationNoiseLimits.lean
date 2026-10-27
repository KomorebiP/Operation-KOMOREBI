import KomorebiSpace.RegularizedHilbertRepair
import Mathlib.Analysis.Normed.Group.Continuity

set_option autoImplicit false

/-!
# Noisy data and inexact stopping limits

The data and solver errors are measured for one fixed bounded linear operator
between the declared real Hilbert spaces. Parameter choices are limits along
arbitrary filters; in particular, they include a full positive real family.
-/

noncomputable section
universe u v w
namespace KomorebiSpace.RegularizationNoiseLimits
open Filter
open scoped Topology RealInnerProductSpace
open RegularizedHilbertRepair

/-- The one-dimensional operator attaining the universal correction-noise gain. -/
def scalarSharpOperator (α : ℝ) : ℝ →L[ℝ] ℝ :=
  Real.sqrt α • ContinuousLinearMap.id ℝ ℝ

theorem scalarSharpOperator_adjoint (α : ℝ) :
    (scalarSharpOperator α).adjoint = scalarSharpOperator α := by
  apply (ContinuousLinearMap.eq_adjoint_iff _ _).2 |>.symm
  intro x y
  simp [scalarSharpOperator, real_inner_comm, mul_comm, mul_left_comm]

/-- Sharpness holds at every positive parameter and for every scalar datum. -/
theorem scalar_correction_formula (α : ℝ) (hα : 0 < α) (r : ℝ) :
    correction (scalarSharpOperator α) α hα r = r / (2 * Real.sqrt α) := by
  symm
  apply normal_unique
  rw [normal_apply, scalarSharpOperator_adjoint]
  simp only [scalarSharpOperator, ContinuousLinearMap.smul_apply,
    ContinuousLinearMap.id_apply, smul_eq_mul]
  have hs : Real.sqrt α ≠ 0 := ne_of_gt (Real.sqrt_pos.mpr hα)
  have hsq := Real.sq_sqrt hα.le
  field_simp
  nlinarith

theorem data_noise_coefficient_attained (α : ℝ) (hα : 0 < α) (r s : ℝ) :
    ‖correction (scalarSharpOperator α) α hα r -
      correction (scalarSharpOperator α) α hα s‖ = ‖r-s‖ / (2 * Real.sqrt α) := by
  rw [scalar_correction_formula, scalar_correction_formula, ← sub_div, norm_div]
  rw [Real.norm_of_nonneg (by positivity : 0 ≤ 2 * Real.sqrt α)]

end KomorebiSpace.RegularizationNoiseLimits
