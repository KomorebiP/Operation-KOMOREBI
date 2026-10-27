module
import KomorebiPhysics.Relativistic3DEuclideanDyadicProjection
open scoped Topology
open Filter
open KomorebiPhysics.Relativistic3DEuclideanDyadicProjection
example (f : CubeState (E := ℂ)) :
    Tendsto (fun a : ℕ => euclideanProjection (E := ℂ) a f) atTop (𝓝 0) := by
  simpa using euclideanProjection_tendsto (E := ℂ) f
