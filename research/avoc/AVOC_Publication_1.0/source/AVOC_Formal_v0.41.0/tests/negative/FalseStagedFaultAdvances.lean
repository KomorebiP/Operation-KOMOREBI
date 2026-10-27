import AVOC.StagedAffineExamples
open Komorebi.AVOC.Affine.Staged
open Komorebi.AVOC.Affine.StagedExamples
example : acknowledge certainModel startCertain .inspectWarm .fault =
    some (step certainModel startCertain .inspectWarm true) := by
  rw [fault_rejected]
