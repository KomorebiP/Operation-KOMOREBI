import KomorebiSpace.RegularizationLimits

set_option autoImplicit false
noncomputable section
open KomorebiSpace

-- Deliberately invalid use of the positive-parameter comparison with only
-- nonnegativity. At α=0 the total path is zero, so comparison with a=1
-- would incorrectly assert the fitting error 1 is at most 0.
example (α : ℝ) (hα : 0 ≤ α) :
    ‖BudgetProfile.projectedDatum (ContinuousLinearMap.id ℝ ℝ) 1 -
      (ContinuousLinearMap.id ℝ ℝ) (RegularizationLimits.path (ContinuousLinearMap.id ℝ ℝ) 1 α)‖ ^ 2 +
      α * ‖RegularizationLimits.path (ContinuousLinearMap.id ℝ ℝ) 1 α‖ ^ 2 ≤
    ‖BudgetProfile.projectedDatum (ContinuousLinearMap.id ℝ ℝ) 1 - (ContinuousLinearMap.id ℝ ℝ) 1‖ ^ 2 +
      α * ‖(1 : ℝ)‖ ^ 2 := by
  exact RegularizationLimits.objective_comparison (ContinuousLinearMap.id ℝ ℝ) 1 hα 1
