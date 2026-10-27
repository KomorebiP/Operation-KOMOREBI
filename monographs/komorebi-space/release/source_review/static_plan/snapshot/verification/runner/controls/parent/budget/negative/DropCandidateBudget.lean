import KomorebiSpace.BudgetProfile

set_option autoImplicit false
noncomputable section
open KomorebiSpace

-- Deliberately invalid: a=1 exactly realizes r=1 but is infeasible at M=0.
example : BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 1 0 ≤
    ‖(1 : ℝ) - (ContinuousLinearMap.id ℝ ℝ) 1‖ := by
  apply BudgetProfile.beta_le_residual
  norm_num
