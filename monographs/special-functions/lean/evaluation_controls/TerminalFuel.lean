import CoupledEvaluation
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example : halfScales.realPairMax 2 ≤ diskMajorant halfScales.maxScale 0 2 := by
  exact halfScales.pair_le_diskMajorant halfScales_positive halfScales_strict 0
    (by norm_num) (by norm_num)
