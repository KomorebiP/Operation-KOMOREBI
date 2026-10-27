import AVOC.AffineProbeExamples
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
open Komorebi.AVOC.Affine.ProbeExamples Komorebi.AVOC.Affine.RankProbe
example : (scan diagonal.linear 1 7 [corner]).tested = 1 := by
  rw [insufficient_probe_credit_keeps_floor]
  decide
