import KomorebiSpace.BudgetDuality

set_option autoImplicit false
noncomputable section
open scoped RealInnerProductSpace
open KomorebiSpace

-- Deliberately invalid: omitting M*norm(T* z) would certify 1 <= 0.
example : ⟪(1 : ℝ), (1 : ℝ)⟫ ≤
    BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 1 1 := by
  have hb : BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 1 1 = 0 := by
    apply le_antisymm _ (BudgetProfile.beta_nonneg _ _ _)
    have h := BudgetProfile.beta_le_residual (ContinuousLinearMap.id ℝ ℝ) 1
      (M := 1) (a := 1) (by norm_num)
    simpa using h
  rw [hb]
  norm_num
