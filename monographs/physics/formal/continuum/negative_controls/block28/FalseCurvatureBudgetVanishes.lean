import KomorebiPhysics.Relativistic3DFullWalkRefinement

open KomorebiPhysics
open Relativistic3DCubicalRefinement
open Relativistic3DCubicalRefinement.CubeLinks
open Relativistic3DFullWalkRefinement

/-- Deliberately false: a nontrivial plaquette cannot have zero curvature
amplitude. -/
example : ‖((nonflatCube.plaquetteXY false : Circle) : ℂ) - 1‖ ≤ 0 := by
  simp
