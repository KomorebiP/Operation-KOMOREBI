import CoupledEvaluationResult
open Komorebi.SpecialFunctions.Coupled.Scales
example : evaluationOuter 0 none = 0 := by
  norm_num [evaluationOuter]
