import CoupledEvaluationResult
open Komorebi.SpecialFunctions.Coupled.Scales
example (p : RationalScales) :
    (makeEvaluationResult p 1 2 1 0).tail_bound = (1/2 : ℚ)^5 := by
  norm_num [makeEvaluationResult]
