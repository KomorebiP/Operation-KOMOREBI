import CoupledEvaluationResult
open Komorebi.SpecialFunctions.Coupled.Scales
example (p : RationalScales) : (p.ordinaryArray 0 0).length = 0 := by
  rw [ordinary_array_length]
