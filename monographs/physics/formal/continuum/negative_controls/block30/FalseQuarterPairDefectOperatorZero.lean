import KomorebiPhysics.Relativistic3DCombinedDefect

open KomorebiPhysics
open Relativistic3DCliffordTransportU1
open Relativistic3DEdgeCompatibility
open Relativistic3DCombinedDefect

/-- Deliberately false: the two quarter-turn half-links reconstruct `-1`,
so the adjacent-scale operator is not zero against the trivial coarse link. -/
example :
    fineEdgeDefectCLM (quarterPair PUnit) cliffordX (Equiv.refl PUnit)
      (fun _ => 1) = 0 := by
  ext ψ x j
  simp [fineEdgeDefectCLM_apply, FineEdgePair.fineIntertwiningDefect]
