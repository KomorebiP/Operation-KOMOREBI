import KomorebiSpace.BoundedApproximateRealization

open Filter Topology
open KomorebiSpace.BoundedApproximateRealization

/-- EXPECTED REJECTION: a valid norm-two realization certificate cannot be
silently strengthened to norm one. The actual identity solution is 2. -/
example : ∃ a : ℝ, (ContinuousLinearMap.id ℝ ℝ) a = 2 ∧ ‖a‖ ≤ 1 := by
  obtain ⟨a, ha, hb⟩ := exists_solution_of_bounded_approximation
    (ContinuousLinearMap.id ℝ ℝ) (fun _ : ℕ => 2) 2 2
    (by intro n; norm_num) (by simp)
  refine ⟨a, ha, ?_⟩
  change a = 2 at ha
  subst a
  norm_num
