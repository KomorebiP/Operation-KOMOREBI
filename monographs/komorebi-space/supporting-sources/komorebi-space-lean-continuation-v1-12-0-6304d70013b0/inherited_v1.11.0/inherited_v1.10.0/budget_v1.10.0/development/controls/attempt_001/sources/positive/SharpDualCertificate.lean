import KomorebiSpace.BudgetDuality

set_option autoImplicit false
noncomputable section
open scoped RealInnerProductSpace
open KomorebiSpace

example : IsGreatest ((fun z : ℝ => ⟪(2 : ℝ), z⟫ -
    1 * ‖(ContinuousLinearMap.id ℝ ℝ).adjoint z‖) '' Metric.closedBall (0 : ℝ) 1)
      (BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 2 1) :=
  BudgetDuality.sharp_budget_duality _ _ (by norm_num)

example : ¬ ∃ a : ℝ, ‖a‖ ≤ 1 ∧ ‖(2 : ℝ) - (ContinuousLinearMap.id ℝ ℝ) a‖ ≤ 1 / 2 := by
  apply BudgetDuality.strict_exclusion_certificate (ContinuousLinearMap.id ℝ ℝ) 2
    (M := 1) (ε := 1 / 2) (z := 1) (by norm_num)
  norm_num

example : ∃ z : ℝ, ‖z‖ ≤ 1 ∧ ⟪(0 : ℝ), z⟫ -
    1 * ‖(ContinuousLinearMap.id ℝ ℝ).adjoint z‖ = 0 := by
  exact ⟨0, by norm_num, by simp⟩
