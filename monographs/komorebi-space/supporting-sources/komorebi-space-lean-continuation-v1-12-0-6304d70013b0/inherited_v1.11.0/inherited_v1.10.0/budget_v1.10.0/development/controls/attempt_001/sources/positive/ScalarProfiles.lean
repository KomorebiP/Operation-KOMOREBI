import KomorebiSpace.BudgetProfileGeometry
import KomorebiSpace.BudgetDuality

set_option autoImplicit false
noncomputable section
open scoped RealInnerProductSpace
open KomorebiSpace

example : BudgetProfile.beta (0 : ℝ →L[ℝ] ℝ) 3 5 = 3 := by
  obtain ⟨a, _, h⟩ := BudgetProfile.exists_budget_minimizer (0 : ℝ →L[ℝ] ℝ) 3
    (M := 5) (by norm_num)
  simpa using h.symm

example : BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 1 1 = 0 := by
  apply le_antisymm _ (BudgetProfile.beta_nonneg _ _ _)
  have h := BudgetProfile.beta_le_residual (ContinuousLinearMap.id ℝ ℝ) 1
    (M := 1) (a := 1) (by norm_num)
  simpa using h

example : BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 2 1 = 1 := by
  apply le_antisymm
  · have h := BudgetProfile.beta_le_residual (ContinuousLinearMap.id ℝ ℝ) 2
      (M := 1) (a := 1) (by norm_num)
    simpa using h
  · have h := BudgetDuality.dualValue_le_beta (ContinuousLinearMap.id ℝ ℝ) 2
      (M := 1) (by norm_num) (z := 1) (by norm_num)
    simpa using h

example : BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 2 (1 / 2) ≤
    (1 / 2) * BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 2 0 +
      (1 - 1 / 2) * BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 2 1 := by
  convert BudgetProfileGeometry.beta_convex_combination (ContinuousLinearMap.id ℝ ℝ)
    2 (M₁ := 0) (M₂ := 1) (t := 1 / 2) (by norm_num) (by norm_num)
    (by norm_num) (by norm_num) using 1 <;> norm_num
