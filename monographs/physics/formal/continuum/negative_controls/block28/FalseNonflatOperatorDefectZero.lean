import KomorebiPhysics.Relativistic3DFullWalkRefinement

open KomorebiPhysics
open Relativistic3DCubicalRefinement
open Relativistic3DCubicalRefinement.CubeLinks
open Relativistic3DFullWalkRefinement

/-- Deliberately false: the explicit lower-`xy` holonomy `-1` produces an
operator defect of norm two. -/
example :
    ‖phaseDefectOp nonflatCube.pathXYZ nonflatCube.pathYXZ‖ = 0 := by
  simp
