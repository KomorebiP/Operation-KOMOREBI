import CoupledExpressionRefinement
open Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions
example : (interpretedDictionary 0 0 1 1 0 0).length = 6 := by
  norm_num [interpretedDictionary,evalDictionary,Source.dictionary]
