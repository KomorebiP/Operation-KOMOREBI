import KomorebiPhysics.Relativistic3DHilbertScalarDefect

open KomorebiPhysics
open Relativistic3DCliffordTransportU1
open Relativistic3DCliffordHilbertRefinement
open Relativistic3DEdgeCompatibility
open Relativistic3DHilbertScalarDefect

/-- Deliberately false: the normalized Euclidean realization does not erase
the explicit quarter-turn adjacent-scale defect. -/
example :
    fineEdgeDefectHilbertCLM (quarterPair PUnit) hermitianX.toClifford
      (Equiv.refl PUnit) (fun _ => 1) = 0 := by
  apply ContinuousLinearMap.ext
  intro ψ
  simp [fineEdgeDefectHilbertCLM_apply, halfStateToHilbert,
    FineEdgePair.fineIntertwiningDefect]
