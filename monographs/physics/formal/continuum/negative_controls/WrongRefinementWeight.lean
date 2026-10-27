import KomorebiPhysics.RefinementExamples
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : (4*(1/2 : ℝ)-1)/(4-1) = 0 := by
  rw [wrong_first_weight]
  norm_num
