import AVOC.AffineProbeExamples
open Komorebi.AVOC.Affine.ProbeExamples Komorebi.AVOC.Affine.RankProbe
example : probeFee * (scan rankOne.linear 1 8 [corner]).tested = 0 := by
  rw [rank_one_inconclusive_paid.2.1]
  decide
