import KomorebiSpace.BudgetDuality

set_option autoImplicit false
noncomputable section
open scoped RealInnerProductSpace
open KomorebiSpace

-- Deliberately invalid: z=2 is outside the unit ball, even at zero budget.
-- Rejection must occur at the unit-norm obligation, not at an import or symbol.
example : ⟪(1 : ℝ), (2 : ℝ)⟫ - 0 * ‖(0 : ℝ →L[ℝ] ℝ).adjoint 2‖ ≤
    BudgetProfile.beta (0 : ℝ →L[ℝ] ℝ) 1 0 := by
  apply BudgetDuality.dualValue_le_beta (0 : ℝ →L[ℝ] ℝ) 1 (by norm_num)
  norm_num
