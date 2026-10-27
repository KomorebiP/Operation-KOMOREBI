import KomorebiPhysics.Relativistic3DCombinedDefect

open KomorebiPhysics
open Relativistic3DCubicalRefinement
open Relativistic3DCubicalRefinement.CubeLinks
open Relativistic3DCombinedDefect

/-- Deliberately false: the explicit lower `xy` plaquette has holonomy `-1`. -/
example : curvatureBudget nonflatCube = 0 := by
  simp [curvatureBudget]
