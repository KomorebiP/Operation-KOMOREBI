import KomorebiSpace.BudgetRobustness

set_option autoImplicit false
noncomputable section
namespace KomorebiSpace.BudgetRobustness.BoundaryExamples

open BudgetProfile

variable {H Y : Type*}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

/-- At zero budget, arbitrary operator mismatch contributes zero to the allowance. -/
theorem zero_budget (T S : H →L[ℝ] Y) (r s : Y) :
    |beta T r 0 - beta S s 0| ≤ ‖r - s‖ := by
  simpa using beta_abs_sub_le T S r s (M := 0) (by norm_num)
    (le_refl ‖T - S‖) (le_refl ‖r - s‖)

/-- With identical datum and operator, the uncertainty allowance vanishes. -/
theorem zero_uncertainty (T : H →L[ℝ] Y) (r : Y) {M : ℝ} (hM : 0 ≤ M) :
    |beta T r M - beta T r M| ≤ 0 := by
  simpa using beta_abs_sub_le T T r r (η := 0) (δ := 0) hM
    (by simp) (by simp)

private theorem real_zero_map_profile (r M : ℝ) (hM : 0 ≤ M) :
    beta (0 : ℝ →L[ℝ] ℝ) r M = |r| := by
  obtain ⟨a, _, h⟩ := exists_budget_minimizer (0 : ℝ →L[ℝ] ℝ) r hM
  simpa using h.symm

private theorem real_identity_feasible (r M : ℝ) (hr : |r| ≤ M) :
    beta (ContinuousLinearMap.id ℝ ℝ) r M = 0 := by
  apply le_antisymm _ (beta_nonneg _ _ _)
  have h := beta_le_residual (ContinuousLinearMap.id ℝ ℝ) r (a := r)
    (show ‖r‖ ≤ M by simpa using hr)
  simpa using h

/-- Deleting the operator-error term is false, even in dimension one. -/
theorem operator_term_necessary :
    ¬ |beta (0 : ℝ →L[ℝ] ℝ) 1 1 -
      beta (ContinuousLinearMap.id ℝ ℝ) 1 1| ≤ 0 := by
  rw [real_zero_map_profile 1 1 (by norm_num),
    real_identity_feasible 1 1 (by norm_num)]
  norm_num

/-- Deleting the datum-error term is false, even with the zero operator. -/
theorem data_term_necessary :
    ¬ |beta (0 : ℝ →L[ℝ] ℝ) 1 1 - beta (0 : ℝ →L[ℝ] ℝ) 0 1| ≤ 0 := by
  rw [real_zero_map_profile 1 1 (by norm_num), real_zero_map_profile 0 1 (by norm_num)]
  norm_num

/-- Replacing the model allowance η*M by η is false for budgets above one. -/
theorem budget_factor_necessary :
    ¬ |beta (0 : ℝ →L[ℝ] ℝ) 2 2 -
      beta (ContinuousLinearMap.id ℝ ℝ) 2 2| ≤ 1 := by
  rw [real_zero_map_profile 2 2 (by norm_num),
    real_identity_feasible 2 2 (by norm_num)]
  norm_num

end KomorebiSpace.BudgetRobustness.BoundaryExamples
