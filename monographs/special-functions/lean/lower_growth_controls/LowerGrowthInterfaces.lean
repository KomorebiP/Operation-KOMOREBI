import CoupledLowerGrowth
open Komorebi.SpecialFunctions.Coupled
open Scales
open scoped Matrix
noncomputable section

example : workedScales.lowerShift = 7 / 3 ∧ workedScales.lowerDescent = 4 := by
  norm_num [lowerShift, lowerDescent, lowerThreshold, minScale, maxScale, workedScales]

example : workedScales.maxScale * (11 + workedScales.lowerShift) =
    workedScales.maxScale * (11 - 1) + workedScales.lowerShift := by
  norm_num [lowerShift, maxScale, workedScales]

example : workedScales.LowerPowerAt 1 ![1, 1] 2 :=
  workedScales.lower_power_seed workedScales_positive (by norm_num [workedScales])
    (by norm_num) (by intro i; fin_cases i <;> norm_num)
    (by norm_num) (by norm_num [lowerThreshold, minScale, workedScales])

example (R : ℝ) (hR : 2 ≤ R) :
    workedScales.LowerPowerAt
      (workedScales.characteristicExponent workedScales_positive (by norm_num [workedScales]))
      (workedScales.normalizedCharacteristicVector
        (workedScales.characteristicExponent workedScales_positive (by norm_num [workedScales]))) R :=
  workedScales.canonical_lower_log_power workedScales_positive (by norm_num [workedScales]) hR

def quarterScales : Scales := ⟨1 / 4, 1 / 4, 1 / 4, 1 / 4⟩

-- This exercises the full lower bound with a genuinely sublinear exponent.
example (R : ℝ) (hR : 2 ≤ R) : quarterScales.LowerPowerAt (1 / 2) ![1, 1] R := by
  have hp : (1 / 4 : ℝ) ^ (1 / 2 : ℝ) = 1 / 2 := by
    rw [← Real.sqrt_eq_rpow]
    apply (Real.sqrt_eq_iff_eq_sq (by norm_num) (by norm_num)).mpr
    norm_num
  have he : quarterScales.characteristicMatrix (1 / 2) *ᵥ ![1, 1] = ![1, 1] := by
    funext i
    fin_cases i <;> norm_num [characteristicMatrix, quarterScales, Matrix.mulVec,
      dotProduct, Fin.sum_univ_two, hp]
  exact quarterScales.coupled_lower_log_power (by norm_num [positive, quarterScales])
    (by norm_num [quarterScales]) (by norm_num)
    (by intro i; fin_cases i <;> norm_num) (by intro i; fin_cases i <;> norm_num) he R hR

example (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 2 ≤ R) :
    0 < s.canonicalLowerCoefficient hs hstrict 0 ∧
    s.canonicalLowerCoefficient hs hstrict 0 ≤
      Real.log (s.UReal R) / R ^ (s.characteristicExponent hs hstrict) :=
  ⟨s.canonicalLowerCoefficient_positive hs hstrict 0,
    (s.canonical_lower_growth_ratio hs hstrict hR).1⟩
