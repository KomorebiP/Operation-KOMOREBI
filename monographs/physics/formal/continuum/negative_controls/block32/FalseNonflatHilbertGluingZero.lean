import KomorebiPhysics.Relativistic3DHilbertFullWalkDefect

open KomorebiPhysics
open Relativistic3DCubicalRefinement
open Relativistic3DHilbertFullWalkDefect

example :
    ‖hilbertPhaseDefectOp (Site := PUnit)
      nonflatCube.pathXYZ nonflatCube.pathYXZ‖ = 0 := by
  norm_num
