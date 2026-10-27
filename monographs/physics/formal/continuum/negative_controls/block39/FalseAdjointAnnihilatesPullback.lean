module
import KomorebiPhysics.Relativistic3DEuclideanDyadicProjection
open KomorebiPhysics.Relativistic3DEuclideanDyadicProjection
example (f : CubeState (E := ℂ)) :
    cubeAdjoint (E := ℂ) (cubePullback (E := ℂ) f) = 0 := by
  rw [cubeAdjoint_pullback]
