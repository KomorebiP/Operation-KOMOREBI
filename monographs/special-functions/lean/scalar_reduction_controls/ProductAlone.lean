import CoupledScalarReduction
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (hp : s.p = s.k) : s.U = s.V := by
  exact (s.components_equal_iff_unordered_rows hs hc).mpr hp
