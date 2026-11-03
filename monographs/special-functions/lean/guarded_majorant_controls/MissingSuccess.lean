import CoupledGuardedMajorant
noncomputable section
open Komorebi.SpecialFunctions.Coupled.Scales

example (p : RationalScales) (hs : p.toReal.positive)
    (hc : p.toReal.q < 1 ∧ p.toReal.r < 1 ∧ p.toReal.a < 1 ∧ p.toReal.b < 1)
    (R B : ℚ) (hR : 0 ≤ R) (budget : ℕ) (fits : ℚ → Bool) (i : Fin 2)
    (z : ℂ) (hz : ‖z‖ ≤ (R : ℝ)) : ‖p.toReal.complexComponent i z‖ ≤ (B : ℝ) := by
  exact guarded_majorant_disk_bound p hs hc R B hR budget fits i z hz
