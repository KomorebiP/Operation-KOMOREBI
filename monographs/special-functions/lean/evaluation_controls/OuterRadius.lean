import CoupledEvaluation
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example (z : ℂ) (hz : ‖z‖ ≤ 1) :
    ‖halfScales.complexComponent 0 z - halfScales.oddPolynomial 0 0 z‖ ≤
      halfScales.realComponent 0 1 * (1/1 : ℝ)^3 := by
  exact halfScales.canonical_outer_remainder halfScales_positive halfScales_strict 0
    (by norm_num) (by norm_num : (1 : ℝ) < 1) le_rfl 0 hz
