import CoupledUniqueness
open Komorebi.SpecialFunctions.Coupled.Scales

-- A nonzero origin value is not a normalized solution.
example : workedScales.IsEntireSolution (fun z : ℂ => z + 1) (fun z => z) := by
  norm_num [IsEntireSolution]
