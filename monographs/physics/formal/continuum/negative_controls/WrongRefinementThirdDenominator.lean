import KomorebiPhysics.RefinementExamples
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : tower 2 (fun _ : ℝ => (1 : ℝ)) 3 1 = (64-56+14-1)/7 := by
  norm_num [tower]
