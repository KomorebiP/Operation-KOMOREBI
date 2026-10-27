import KomorebiSpace.BudgetRobustness

set_option autoImplicit false
noncomputable section
open KomorebiSpace

-- Deliberately invalid WR05 mutation: delta=0, eta=1, M=1, but eta*M is deleted.
example : |BudgetProfile.beta (0 : ℝ →L[ℝ] ℝ) 1 1 -
    BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 1 1| ≤ 0 := by
  have hzero : BudgetProfile.beta (0 : ℝ →L[ℝ] ℝ) 1 1 = 1 := by
    obtain ⟨a, _, h⟩ := BudgetProfile.exists_budget_minimizer (0 : ℝ →L[ℝ] ℝ) 1
      (M := 1) (by norm_num)
    simpa using h.symm
  have hid : BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 1 1 = 0 := by
    apply le_antisymm _ (BudgetProfile.beta_nonneg _ _ _)
    have h := BudgetProfile.beta_le_residual (ContinuousLinearMap.id ℝ ℝ) 1
      (M := 1) (a := 1) (by norm_num)
    simpa using h
  rw [hzero, hid]
  norm_num
