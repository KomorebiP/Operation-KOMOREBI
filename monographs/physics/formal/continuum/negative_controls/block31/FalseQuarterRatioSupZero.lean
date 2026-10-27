import KomorebiPhysics.Relativistic3DHilbertScalarDefect

open KomorebiPhysics
open Relativistic3DCliffordTransportU1
open Relativistic3DEdgeCompatibility
open Relativistic3DHilbertScalarDefect

/-- Deliberately false: the two quarter-turn half-links reconstruct `-1`,
so their ratio error against the trivial coarse link has magnitude two. -/
example : edgeRatioSup (quarterPair PUnit).productLink (fun _ => 1) = 0 := by
  simp [edgeRatioSup, edgeRatio]
  norm_num [Complex.norm_def]
