import CoupledPythonRefinement
open Komorebi.SpecialFunctions.Coupled.Scales.Python
example : (resultDictionary 0 0 1 1 0 0).length = 6 := by
  simp [resultDictionary]
