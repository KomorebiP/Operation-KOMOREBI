import AVOC.AffineReuseExamples
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
open Komorebi.AVOC.Affine
open ReuseExamples
example : ∃ c, Reuse.importFor changedLinear saved = some c := by
  rw [wrong_linear_cannot_reuse]
  simp
