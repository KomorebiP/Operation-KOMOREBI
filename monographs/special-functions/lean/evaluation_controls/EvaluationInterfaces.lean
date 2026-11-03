import CoupledEvaluation
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 0 ≤ R) :
    ∃ fuel : ℕ, s.maxScale^fuel * R < 1 ∧ ∀ i : Fin 2, ∀ z : ℂ, ‖z‖ ≤ R →
      ‖s.complexComponent i z‖ ≤ diskMajorant s.maxScale fuel R :=
  s.disk_majorant_exists hs hc hR

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (i : Fin 2) (z : ℂ) :
    s.oddPolynomial i 0 z = z := by
  fin_cases i <;> simp [oddPolynomial, componentCoefficient, coefficients_zero]

example (Q : ℚ) (fuel : ℕ) : rationalDiskMajorant Q fuel 0 = 0 := by
  cases fuel <;> simp [rationalDiskMajorant]

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    ‖s.complexComponent i 0‖ ≤ diskMajorant s.maxScale 0 0 :=
  s.component_disk_majorant hs hc i (by norm_num) 0 (by norm_num) (by simp)

example (i : Fin 2) (z : ℂ) (hz : ‖z‖ ≤ 1) :
    ‖unequalScales.complexComponent i z - unequalScales.oddPolynomial i 30 z‖ <
      (16/100000000000000 : ℝ) := unequal_last_thirty_error i z hz

example (p : RationalScales) (n : ℕ) :
    (((p.coefficients n).1 : ℝ), ((p.coefficients n).2 : ℝ)) = p.toReal.coefficients n :=
  rational_coefficients_cast p n

example (i : Fin 2) :
    let p : RationalScales := ⟨1/5,2/5,3/5,7/10⟩
    (p.polynomial i 30 1 : ℝ) ≤ p.toReal.realComponent i 1 ∧
      p.toReal.realComponent i 1 ≤
        ((p.polynomial i 30 1 + rationalDiskMajorant p.maxScale 2 2 * (1/2 : ℚ)^63 : ℚ) : ℝ) := by
  dsimp only
  convert rational_endpoint_enclosure (⟨1/5,2/5,3/5,7/10⟩ : RationalScales)
    (by norm_num [RationalScales.toReal, positive]) (by norm_num [RationalScales.toReal])
    1 2 (by norm_num) (by norm_num) 2 (by norm_num [RationalScales.maxScale]) 30 i using 1
  all_goals norm_num

example (p : RationalScales) (hs : p.toReal.positive)
    (hc : p.toReal.q < 1 ∧ p.toReal.r < 1 ∧ p.toReal.a < 1 ∧ p.toReal.b < 1) :
    ∃ fuel : ℕ, p.maxScale^fuel * 2 < 1 := rational_fuel_exists p hs hc 2
