import CoupledGermInverse
open Komorebi.SpecialFunctions.Coupled
open Scales Filter
open scoped Topology
example {s t : Scales} (hs : s.positive) (ht : t.positive)
    (hss : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (hst : t.q < 1 ∧ t.r < 1 ∧ t.a < 1 ∧ t.b < 1)
    (hu : s.U =ᶠ[𝓝 0] t.U) (hv : s.V =ᶠ[𝓝 0] t.V) : s = t := by
  exact parameters_of_analytic_germs hs ht hss hst hu hv
