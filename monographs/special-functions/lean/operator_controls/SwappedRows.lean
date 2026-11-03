import CoupledOperator
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example : let s : Komorebi.SpecialFunctions.Coupled.Scales := ⟨1/2,1/4,1/4,1/2⟩
    s.Autonomous ![1,-1] := by
  dsimp only
  apply ordered_rows_autonomous
  all_goals norm_num
