import CoupledAnalytic
open Komorebi.SpecialFunctions.Coupled.Scales

-- The norm-one guard on the scaling lemma cannot be omitted.
example : (2 : ℂ) * 1 ∈ localDisk := by
  norm_num [localDisk]
