import CoupledOperator
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example : halfScales.Autonomous ![1,0] := by
  apply ordered_rows_autonomous
  all_goals norm_num [halfScales]
