import CoupledUpperGrowth
open Komorebi.SpecialFunctions.Coupled
open Scales
open scoped Matrix
noncomputable section

example : workedScales.UReal 0 ≤ 0 ∧ workedScales.VReal 0 ≤ 0 := by
  simpa only [mul_zero, zero_mul] using
    workedScales.real_axis_full_upper workedScales_positive (by norm_num [workedScales]) (R := 0) le_rfl

example : workedScales.UReal 1 ≤ 2 ∧ workedScales.VReal 1 ≤ 2 :=
  workedScales.real_axis_at_one_le_two workedScales_positive (by norm_num [workedScales])

example : 3 / workedScales.minScale ≤ workedScales.upperRadius 8 := by
  norm_num [minScale, upperRadius, maxScale, workedScales]

example (R : ℝ) (hR : Real.exp 1 ≤ R) :
    Real.log (workedScales.UReal R) ≤
      workedScales.upperPowerConstant 8
        (workedScales.characteristicExponent workedScales_positive (by norm_num [workedScales]))
        (workedScales.normalizedCharacteristicVector
          (workedScales.characteristicExponent workedScales_positive (by norm_num [workedScales]))) *
      workedScales.normalizedCharacteristicVector
        (workedScales.characteristicExponent workedScales_positive (by norm_num [workedScales])) 0 *
      R ^ (workedScales.characteristicExponent workedScales_positive (by norm_num [workedScales])) -
      Real.log R - workedScales.upperCorrection := by
  exact (workedScales.canonical_upper_log_power workedScales_positive
    (by norm_num [workedScales]) (n := 8)
    (by norm_num [minScale, upperRadius, maxScale, workedScales]) hR).1

def quarterScales : Scales := ⟨1 / 4, 1 / 4, 1 / 4, 1 / 4⟩

example : quarterScales.upperSeed 1 = 20 ∧ quarterScales.upperSeed 2 = 6416 := by
  norm_num [upperSeed, upperRadius, maxScale, quarterScales]

example (t : ℝ) (ht : 1 ≤ t) : quarterScales.UpperPowerAt 2 (1 / 2) ![1, 1] t := by
  have hp : (1 / 4 : ℝ) ^ (1 / 2 : ℝ) = 1 / 2 := by
    rw [← Real.sqrt_eq_rpow]
    apply (Real.sqrt_eq_iff_eq_sq (by norm_num) (by norm_num)).mpr
    norm_num
  have he : quarterScales.characteristicMatrix (1 / 2) *ᵥ ![1, 1] = ![1, 1] := by
    funext i
    fin_cases i <;> norm_num [characteristicMatrix, quarterScales, Matrix.mulVec,
      dotProduct, Fin.sum_univ_two, hp]
  exact quarterScales.coupled_upper_log_power (by norm_num [positive, quarterScales])
    (by norm_num [quarterScales])
    (by norm_num [minScale, upperRadius, maxScale, quarterScales])
    (by norm_num) (by intro i; fin_cases i <;> norm_num) he t ht

example (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : Real.exp 1 ≤ R) :
    0 < s.canonicalUpperCoefficient hs hstrict 0 ∧
    (s.canonicalLowerCoefficient hs hstrict 0 ≤
      Real.log (s.UReal R) / R ^ (s.characteristicExponent hs hstrict) ∧
      Real.log (s.UReal R) / R ^ (s.characteristicExponent hs hstrict) ≤
        s.canonicalUpperCoefficient hs hstrict 0) :=
  ⟨s.canonicalUpperCoefficient_positive hs hstrict 0,
    (s.canonical_two_sided_growth_ratio hs hstrict hR).1⟩
