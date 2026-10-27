module
import KomorebiPhysics.Relativistic3DEuclideanDyadicProjection
open KomorebiPhysics.Relativistic3DEuclideanDyadicProjection
example (a : ℕ) :
    ‖euclideanProjection (E := ℂ) a (0 : CubeState (E := ℂ))‖ = 1 := by
  simp
