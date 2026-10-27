import Mathlib.Analysis.Calculus.Deriv.Pow
import Mathlib.Analysis.Calculus.Deriv.Add
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

/-! # Proven counterexamples to both naive nonlinear upgrades -/
namespace KomorebiRepair.Nonlinear

/-- A nonzero linearized obstruction need not exclude an exact nonlinear root. -/
theorem nonlinear_root_despite_first_order_obstruction (a : ℝ) (ha : a ≠ 0) :
    HasDerivAt (fun x : ℝ => x ^ 2 - a ^ 2) 0 0 ∧
    (¬ ∃ u : ℝ, (0 : ℝ) * u = -(0 ^ 2 - a ^ 2)) ∧
    a ^ 2 - a ^ 2 = 0 := by
  refine ⟨?_, ?_, sub_self _⟩
  · have h := ((hasDerivAt_id (0 : ℝ)).pow 2).sub_const (a ^ 2)
    norm_num at h
    simpa using h
  · intro ⟨u, hu⟩
    have hn := pow_ne_zero 2 ha
    apply hn
    simpa using hu.symm

/-- A solvable linearization does not imply a global real root. -/
theorem linearized_solution_without_real_root :
    HasDerivAt (fun x : ℝ => x ^ 2 + x + 1) 1 0 ∧
    (∃ u : ℝ, (1 : ℝ) * u = -1) ∧
    (∀ x : ℝ, x ^ 2 + x + 1 ≠ 0) := by
  refine ⟨?_, ⟨-1, by norm_num⟩, ?_⟩
  · have h := (((hasDerivAt_id (0 : ℝ)).pow 2).add (hasDerivAt_id 0)).add_const 1
    norm_num at h
    simpa using h
  · intro x h
    nlinarith [sq_nonneg (x + 1 / 2)]

end KomorebiRepair.Nonlinear
