import CoupledCharacteristic
open Komorebi.SpecialFunctions.Coupled
open Scales
noncomputable section
def halfScales : Scales := ⟨1 / 2, 1 / 2, 1 / 2, 1 / 2⟩
example : halfScales.normalizedCharacteristicVector 1 0 +
    halfScales.normalizedCharacteristicVector 1 1 = 1 := by
  norm_num [normalizedCharacteristicVector, characteristicNormalizer,
    characteristicVector, halfScales]
