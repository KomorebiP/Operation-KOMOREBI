import KomorebiPhysics.Relativistic3DCubicalRefinement

open KomorebiPhysics
open Relativistic3DGeometricEdgeRefinement
open Relativistic3DCubicalRefinement
open Relativistic3DCubicalRefinement.CubeLinks

/-- Deliberately false: omitting the one-eighth cell measure multiplies the
embedded Hilbert weight by eight. -/
example :
    (8 : ℂ) * cubeIP (nonflatCube.embed basisSpinor0)
      (nonflatCube.embed basisSpinor0) =
    cubeIP (nonflatCube.embed basisSpinor0)
      (nonflatCube.embed basisSpinor0) := by
  simp
