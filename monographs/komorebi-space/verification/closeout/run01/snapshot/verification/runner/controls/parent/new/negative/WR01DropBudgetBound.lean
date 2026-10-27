import KomorebiSpace.BoundedApproximateRealization

open Filter Topology
open KomorebiSpace.BoundedApproximateRealization

/-- EXPECTED REJECTION: the constant sequence 2 has zero residual for the
identity at datum 2, but dropping its norm bound cannot produce a solution in
the budget-one ball. Rejection must be the false obligation 2 ≤ 1. This tests
the sharp budget claim, not infinite-dimensional range nonclosedness. -/
example : ∃ a : ℝ, (ContinuousLinearMap.id ℝ ℝ) a = 2 ∧ ‖a‖ ≤ 1 := by
  apply exists_solution_of_bounded_approximation
    (ContinuousLinearMap.id ℝ ℝ) (fun _ : ℕ => 2) 2 1
  · intro n
    norm_num
  · simp
