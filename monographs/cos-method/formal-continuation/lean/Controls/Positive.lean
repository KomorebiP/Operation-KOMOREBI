import KomorebiQCOS

open KomorebiQCOS MeasureTheory

namespace KCOSControls

theorem acceptance_at_boundary : acceptsRational 100 101 (1/100) = true := by norm_num [acceptsRational]

theorem reject_wide : acceptsRational 100 102 (1/100) = false := by norm_num [acceptsRational]

theorem reject_zero_lower : acceptsRational 0 0 (1/100) = false := by norm_num [acceptsRational]

theorem reject_negative_lower : acceptsRational (-1) 0 (1/100) = false := by norm_num [acceptsRational]

theorem reject_swapped_endpoints : acceptsRational 101 100 (1/100) = false := by norm_num [acceptsRational]

theorem reject_negative_tolerance : acceptsRational 100 101 (-1/100) = false := by norm_num [acceptsRational]

theorem exact_interval_accepted : acceptsRational 100 100 0 = true := by norm_num [acceptsRational]

theorem midpoint_budget_is_not_interval_budget :
    (10 : ℝ) / (100 - 10) ≤ 1/9 ∧
      ¬ MultiplicativeBudget (100 - 10) (100 + 10) (1/9) := by
  norm_num [MultiplicativeBudget]

theorem rational_narrowing : acceptsRational (1001/10) (1009/10) (1/100) = true := by
  apply acceptsRational_narrow acceptance_at_boundary <;> norm_num

theorem true_positive_relative_guarantee {p : ℝ} (hp : Enclosed p 100 101) :
    |(201/2 : ℝ) - p| / p ≤ 1/100 := by
  have h := acceptsRational_relative_error (lower := 100) (upper := 101)
    (tolerance := 1/100) hp (show Enclosed (201/2 : ℝ) 100 101 by norm_num [Enclosed])
    acceptance_at_boundary
  simpa using h

-- The closed tail includes the atom at zero, even for a rank-zero spectrum.
theorem zero_spectrum_atom : gaussianWeightedTail (fun _ : Fin 2 => 0) 0 = 1 := by
  norm_num [gaussianWeightedTail, tailProbability, tailEvent, weightedSquares]

theorem zero_spectrum_above_support : gaussianWeightedTail (fun _ : Fin 2 => 0) 1 = 0 := by
  norm_num [gaussianWeightedTail, tailProbability, tailEvent, weightedSquares]

theorem signed_coefficient_bracket (q : ℝ) :
    Enclosed (gaussianWeightedTail (fun _ : Fin 1 => (0 : ℝ)) q)
      (gaussianWeightedTail (fun _ : Fin 1 => (-2 : ℝ)) q)
      (gaussianWeightedTail (fun _ : Fin 1 => (1 : ℝ)) q) := by
  apply gaussianWeightedTail_enclosed <;> intro i <;> norm_num

-- Counterexample: containment without an accuracy budget is not enough.
theorem missing_budget_counterexample :
    Enclosed (1 : ℝ) 1 2 ∧ Enclosed (2 : ℝ) 1 2 ∧
      ¬ (|(2 : ℝ) - 1| / 1 ≤ 1/100) := by
  norm_num [Enclosed]

theorem reversed_probability_counterexample :
    tailProbability (Measure.dirac ()) (fun _ => (1 : ℝ)) 1 = 1 ∧
      tailProbability (Measure.dirac ()) (fun _ => (0 : ℝ)) 1 = 0 := by
  simp [tailProbability, tailEvent]

end KCOSControls
