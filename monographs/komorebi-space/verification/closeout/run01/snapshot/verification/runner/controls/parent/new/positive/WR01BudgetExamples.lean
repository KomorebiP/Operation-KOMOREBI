import KomorebiSpace.BoundedApproximateRealization

open Filter Topology
open KomorebiSpace.BoundedApproximateRealization

/-- A zero budget is allowed. The zero operator and zero residual admit exactly
the zero correction within that budget. -/
example : ∃ a : ℝ, (0 : ℝ →L[ℝ] ℝ) a = 0 ∧ a = 0 := by
  obtain ⟨a, ha, hb⟩ := exists_solution_of_bounded_approximation
    (0 : ℝ →L[ℝ] ℝ) (fun _ : ℕ => 0) 0 0
    (by intro n; norm_num) (by simp)
  exact ⟨a, ha, norm_eq_zero.mp (le_antisymm hb (norm_nonneg a))⟩

/-- An actual identity operator example saturates the budget instead of losing
it through a strict inequality or an extra scaling factor. -/
example : ∃ a : ℝ, (ContinuousLinearMap.id ℝ ℝ) a = 2 ∧ ‖a‖ ≤ 2 := by
  exact exists_solution_of_bounded_residual_tendsto_zero
    (ContinuousLinearMap.id ℝ ℝ) (fun _ : ℕ => 2) 2 2
    (by intro n; norm_num)
    (by simp)

/-- The full bounded-sequence equivalence recovers a nonzero attained datum. -/
example : ∃ (u : ℕ → ℝ) (M : ℝ), (∀ n, ‖u n‖ ≤ M) ∧
    Tendsto (fun n => ‖(ContinuousLinearMap.id ℝ ℝ) (u n) - 3‖)
      atTop (𝓝 0) := by
  apply (mem_range_iff_bounded_approximation (ContinuousLinearMap.id ℝ ℝ) 3).mp
  exact ⟨3, rfl⟩
