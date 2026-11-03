import CoupledGuardedMajorant
noncomputable section
open Komorebi.SpecialFunctions.Coupled.Scales

example : checkedMajorant (⟨1/2,1/2,1/2,1/2⟩ : RationalScales)
    (3/4) (some 0) (some 1) = .error (.resource .bits) := by
  norm_num [checkedMajorant,RationalScales.strictRational,guardedMajorant,buildLadder,guardedFold]
