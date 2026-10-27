import KomorebiPhysics.Relativistic3DEdgeCompatibility

open KomorebiPhysics
open Relativistic3DCliffordTransportU1
open Relativistic3DEdgeCompatibility

/-- Deliberately false: two quarter-turn half links reconstruct `-1`, not the
trivial coarse link. -/
example : (quarterPair PUnit).productLink = (fun _ => 1) := by
  funext x
  simp
