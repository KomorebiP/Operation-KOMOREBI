import AVOC.AffineFactorExamples
open Komorebi.AVOC.Affine.FactorExamples
example : rankOne.linear.rank = 0 := by
  rw [rankOne_rank]
  decide
