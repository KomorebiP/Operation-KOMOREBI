import CoupledEvaluation
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {R S B : ℝ} (hR : 0 ≤ R) (hRS : R < S) (hB : s.realComponent i S ≤ B)
    (N : ℕ) (z : ℂ) (hz : ‖z‖ ≤ R) :
    ‖s.complexComponent i z - s.oddPolynomial i N z‖ ≤ B*(R/S)^(2*N+5) := by
  exact s.canonical_outer_remainder hs hc i hR hRS hB N hz
