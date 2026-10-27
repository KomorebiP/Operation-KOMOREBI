import KomorebiPhysics.RefinementExamples
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : tower 1 (fun _ : ℝ => (1 : ℝ)) 1 1 = 1 := by
  rw [unit_ratio_degenerate]
  norm_num
