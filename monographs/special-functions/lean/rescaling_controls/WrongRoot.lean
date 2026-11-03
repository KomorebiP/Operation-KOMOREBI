import CoupledRescaling
open Komorebi.SpecialFunctions.Coupled
open Scales
example : (⟨1 / 2, 1 / 8, 1 / 2, 1 / 2⟩ : Scales).reductionScale = 4 := by
  norm_num [reductionScale, k, p]
