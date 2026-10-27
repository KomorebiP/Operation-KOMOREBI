import KomorebiPhysics.Relativistic3DAffineConnection

open KomorebiPhysics
open Relativistic3DAffineConnection

/-- Deliberately false: a unit square carrying flux angle `π` has plaquette `-1`,
not the trivial phase. -/
example (p : Point3) :
    plaquetteXY (uniformBzConnection Real.pi) 1 p = 1 := by
  rw [uniformBz_plaquetteXY]
  norm_num
