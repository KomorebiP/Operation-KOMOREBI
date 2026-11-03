import CoupledGuardedMajorant
noncomputable section
open Komorebi.SpecialFunctions.Coupled.Scales

example : guardedFold (fun _ => true) (2/3) [2,1] = .ok (757/81) := by
  norm_num [guardedFold,majorantStep]
