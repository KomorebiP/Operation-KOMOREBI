import KomorebiPhysics.Relativistic3DCubicalRefinement

open KomorebiPhysics
open Relativistic3DGeometricEdgeRefinement
open Relativistic3DCliffordTransportU1
open Relativistic3DCubicalRefinement
open Relativistic3DCubicalRefinement.CubeLinks

/-- Deliberately false: the lower-face holonomy `-1` has nonzero corner defect. -/
example :
    pathDefect nonflatCube.pathXYZ nonflatCube.pathYXZ basisSpinor0 = 0 := by
  simp [pathDefect, phaseMul, basisSpinor0]
