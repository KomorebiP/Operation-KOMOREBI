import AVOC.AffineReuseExamples
open Komorebi.AVOC.Affine
open ReuseExamples
example : ∃ c, Reuse.importFor changedLinear saved = some c := by
  rw [wrong_linear_cannot_reuse]
  simp
