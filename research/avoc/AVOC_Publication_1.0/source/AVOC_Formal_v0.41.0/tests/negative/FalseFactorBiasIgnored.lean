import AVOC.AffineFactorExamples
open Komorebi.AVOC.Affine
open FactorExamples
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
example : Factorization.check rankOne wrongBias = true := by
  rw [wrong_bias_rejected]
  decide
