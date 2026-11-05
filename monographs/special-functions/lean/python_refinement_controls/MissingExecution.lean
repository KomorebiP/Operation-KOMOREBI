import CoupledPythonRefinement
open Komorebi.SpecialFunctions.Coupled.Scales
open Komorebi.SpecialFunctions.Coupled.Scales.Python
example (p : RationalScales) (x : ℚ) (last : Option ℕ) (outer : Option ℚ) (d : Dictionary) :
    ∃ v, certifiedEvaluationSpec p x last outer = .ok v ∧ d = encode v := by
  exact source_return_refines p x last outer d
