import CoupledEvaluationResult
open Komorebi.SpecialFunctions.Coupled.Scales
example (p : RationalScales) (x : ℚ) (last : Option ℕ) (outer : Option ℚ)
    (v : EvaluationResult) :
    (v.U.1 : ℝ) ≤ p.toReal.realComponent 0 (x : ℝ) := by
  exact (evaluation_success_encloses p x last outer v).1.1
