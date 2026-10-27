import KomorebiSpace.BudgetProfile

set_option autoImplicit false
noncomputable section
open KomorebiSpace

-- Deliberately invalid: a negative radius cannot admit an attaining correction.
example : ∃ a : ℝ, ‖a‖ ≤ -1 ∧
    ‖(1 : ℝ) - (ContinuousLinearMap.id ℝ ℝ) a‖ =
      BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 1 (-1) := by
  apply BudgetProfile.exists_budget_minimizer
  norm_num
