import CoupledCharacteristic
open Komorebi.SpecialFunctions.Coupled
open Scales
open scoped Matrix
example : workedScales.characteristicMatrix 1 *ᵥ workedScales.characteristicLeftVector 1 =
    workedScales.characteristicLeftVector 1 := by
  norm_num [characteristicMatrix, characteristicLeftVector, workedScales,
    Matrix.mulVec, dotProduct, Fin.sum_univ_two, funext_iff]
