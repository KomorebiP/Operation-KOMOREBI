import AVOC.AffineReuseExamples
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
open Komorebi.AVOC.Affine
open ReuseExamples FactorExamples
example : Factorization.check shifted rankOneCandidate = true := by decide
