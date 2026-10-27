import AVOC.AffineFactorExamples
open Komorebi.AVOC.Affine
open FactorExamples
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
example : Factorization.check rankOne redundantCandidate = true := by
  rw [redundant_lower_rejected]
  decide
