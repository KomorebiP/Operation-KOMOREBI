import KomorebiPhysics.Relativistic3DHilbertFullWalkDefect

open KomorebiPhysics
open Relativistic3DEdgeCompatibility
open Relativistic3DHilbertScalarDefect
open Relativistic3DHilbertFullWalkDefect
open Relativistic3DCombinedDefect

example :
    hilbertEdgeBudget
      (quarterPair PUnit).productLink (fun _ => 1) (fun _ => 1)
      (fun _ => 1) (fun _ => 1) (fun _ => 1) ≤
      curvatureBudget flatQuarterCube := by
  norm_num
