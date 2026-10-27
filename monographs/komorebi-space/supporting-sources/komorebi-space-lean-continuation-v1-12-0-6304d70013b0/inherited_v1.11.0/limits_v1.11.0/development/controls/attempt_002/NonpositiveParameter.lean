import KomorebiSpace.RegularizationLimits

set_option autoImplicit false
noncomputable section
open KomorebiSpace

-- Deliberately invalid use of the positive-parameter comparison with only
-- nonnegativity. The missing strict positivity is the intended obligation.
example (α : ℝ) (hα : 0 ≤ α) :
    ‖BudgetProfile.projectedDatum (0 : ℝ →L[ℝ] ℝ) 3 -
      (0 : ℝ →L[ℝ] ℝ) (RegularizationLimits.path (0 : ℝ →L[ℝ] ℝ) 3 α)‖ ^ 2 +
      α * ‖RegularizationLimits.path (0 : ℝ →L[ℝ] ℝ) 3 α‖ ^ 2 ≤
    ‖BudgetProfile.projectedDatum (0 : ℝ →L[ℝ] ℝ) 3 - (0 : ℝ →L[ℝ] ℝ) 0‖ ^ 2 +
      α * ‖(0 : ℝ)‖ ^ 2 := by
  exact RegularizationLimits.objective_comparison (0 : ℝ →L[ℝ] ℝ) 3 hα 0
