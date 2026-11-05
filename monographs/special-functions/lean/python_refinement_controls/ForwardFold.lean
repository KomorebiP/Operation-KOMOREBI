import CoupledPythonRefinement
open Komorebi.SpecialFunctions.Coupled.Scales
example : majorantStep 1 (majorantStep 2 (2/3)) = (500/81 : ℚ) := by
  norm_num [majorantStep]
