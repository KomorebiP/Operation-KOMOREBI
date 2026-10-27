import KomorebiPhysics.Relativistic3DCubicalRefinement

open KomorebiPhysics
open Relativistic3DCubicalRefinement
open Relativistic3DCubicalRefinement.CubeLinks

/-- Deliberately false: the explicit nonflat cube has distinct corner paths. -/
example : nonflatCube.pathXYZ = nonflatCube.pathYXZ := by
  simp
