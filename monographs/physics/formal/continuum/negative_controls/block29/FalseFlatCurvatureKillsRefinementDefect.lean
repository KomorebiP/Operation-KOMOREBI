import KomorebiPhysics.Relativistic3DEdgeCompatibility

open KomorebiPhysics
open Relativistic3DCliffordTransportU1
open Relativistic3DEdgeCompatibility

/-- Deliberately false: vanishing face plaquettes do not repair a wrong
straight two-half-edge product. -/
example :
    (quarterPair PUnit).fineIntertwiningDefect cliffordX (Equiv.refl PUnit)
      (fun _ => 1) (fun _ => basisSpinor0) = 0 := by
  rw [FineEdgePair.fineIntertwiningDefect_eq_zero_iff]
