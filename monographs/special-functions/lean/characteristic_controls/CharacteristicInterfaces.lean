import CoupledCharacteristic
open Komorebi.SpecialFunctions.Coupled
open Scales
open scoped Matrix
noncomputable section
def halfScales : Scales := ⟨1 / 2, 1 / 2, 1 / 2, 1 / 2⟩

example : workedScales.characteristicExponent workedScales_positive
    (by norm_num [workedScales]) = 1 := by
  exact (workedScales.characteristic_exponent_exists_unique workedScales_positive
    (by norm_num [workedScales])).unique
      (workedScales.characteristicExponent_spec workedScales_positive (by norm_num [workedScales]))
      (by norm_num [workedScales])

example : workedScales.normalizedCharacteristicVector 1 = ![1 / 2, 1] := by
  funext i
  fin_cases i <;> norm_num [normalizedCharacteristicVector, characteristicNormalizer,
    characteristicVector, workedScales]

example : (workedScales.characteristicMatrix 1)ᵀ *ᵥ
    workedScales.characteristicLeftVector 1 = workedScales.characteristicLeftVector 1 :=
  workedScales.characteristic_left_eigenvector workedScales_positive (by norm_num [workedScales])

example : spectralRadius ℂ (workedScales.characteristicMatrixC 1) = 1 :=
  workedScales.characteristic_spectralRadius workedScales_positive
    (by norm_num [workedScales]) (by norm_num) (by norm_num [workedScales])

example : workedScales.q ^ (1 : ℝ) + workedScales.b ^ (1 : ℝ) - 1 = -(1 / 10 : ℝ) := by
  norm_num [workedScales]

example : halfScales.normalizedCharacteristicVector 1 = ![1, 1] ∧
    spectralRadius ℂ (halfScales.characteristicMatrixC 1) = 1 := by
  constructor
  · funext i
    fin_cases i <;> norm_num [normalizedCharacteristicVector, characteristicNormalizer,
      characteristicVector, halfScales]
  · apply halfScales.characteristic_spectralRadius
      (by norm_num [positive, halfScales]) (by norm_num [halfScales])
      (by norm_num) (by norm_num [halfScales])

-- Strict contraction is essential: all-one scales have no characteristic root.
example : ¬ ∃ t : ℝ, 0 < t ∧
    (1 - (1 : ℝ) ^ t) * (1 - (1 : ℝ) ^ t) = ((1 : ℝ) * 1) ^ t := by
  simp
