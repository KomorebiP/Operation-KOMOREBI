import CoupledTypeProportions
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    s.lowerTypeScalar hs hstrict = s.upperTypeScalar hs hstrict := by
  exact (s.canonical_type_proportions hs hstrict).2.1
