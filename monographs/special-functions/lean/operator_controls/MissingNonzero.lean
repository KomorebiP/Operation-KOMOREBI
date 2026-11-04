import CoupledOperator
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive) :
    s.Autonomous 0 → s.q = s.a := by
  intro h
  exact (s.autonomous_ordered_rows hs 0 (by simp) h).1
