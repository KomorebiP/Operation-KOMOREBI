import KomorebiPhysics.UnboundedExamples
open Filter
open scoped Topology
open KomorebiPhysics.UnboundedExamples
-- The input sequence really tends to zero, but its generator images do not.
example : Tendsto (fun n => harmonic (shrinking n)) atTop (𝓝 0) := by
  simp only [shrinking_action_not_zero]
