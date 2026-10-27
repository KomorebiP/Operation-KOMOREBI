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

open KomorebiSpace
open scoped RealInnerProductSpace

-- The full allowance succeeds on the same sharp operator-error example.
example : |BudgetProfile.beta (0 : ℝ →L[ℝ] ℝ) 1 1 -
    BudgetProfile.beta (ContinuousLinearMap.id ℝ ℝ) 1 1| ≤ 1 := by
  simpa using BudgetRobustness.beta_abs_sub_le (0 : ℝ →L[ℝ] ℝ)
    (ContinuousLinearMap.id ℝ ℝ) 1 1 (M := 1) (η := 1) (δ := 0)
    (by norm_num) (by simp) (by simp)

-- A nominal zero-operator witness with no uncertainty remains a valid lower bound.
example : ⟪(1 : ℝ), (1 : ℝ)⟫ - 0 * ‖(0 : ℝ →L[ℝ] ℝ).adjoint 1‖ - 0 - 0 * 0 ≤
    BudgetProfile.beta (0 : ℝ →L[ℝ] ℝ) 1 0 := by
  exact BudgetRobustness.nominal_dual_lower_certificate (0 : ℝ →L[ℝ] ℝ)
    (0 : ℝ →L[ℝ] ℝ) 1 1 (M := 0) (η := 0) (δ := 0)
    (by norm_num) (by simp) (by simp) (by norm_num)
