import KomorebiPhysics.RefinementExamples
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : ‖tower 2 sampleNoise 1 1‖ ≤ 1 := by
  rw [sampleNoise_amplified]
  norm_num
