import AVOC.AffineFactorExamples
open Komorebi.AVOC.Affine
open FactorExamples
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
example : Factorization.campaignCost rankOneProgram rankOneChecked 0 0 ≤ 0 := by
  have h := (rankOne_amortization 0 0).2 (by decide)
  exact h
