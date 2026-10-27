import KomorebiSpace.BudgetProfileGeometry
import KomorebiSpace.BudgetRobustness

set_option autoImplicit false
noncomputable section
open KomorebiSpace

-- Deliberately invalid WR05 mutation: eta=0, delta=1, M=0, but delta is deleted.
example : |BudgetProfile.beta (0 : ℝ →L[ℝ] ℝ) 1 0 -
    BudgetProfile.beta (0 : ℝ →L[ℝ] ℝ) 0 0| ≤ 0 := by
  rw [BudgetProfileGeometry.beta_zero, BudgetProfileGeometry.beta_zero]
  norm_num
