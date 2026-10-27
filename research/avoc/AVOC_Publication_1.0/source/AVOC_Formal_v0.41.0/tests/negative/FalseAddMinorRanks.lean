import AVOC.AffineProbeExamples
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
open Komorebi.AVOC.Affine.ProbeExamples Komorebi.AVOC.Affine.RankProbe
example : (scan hiddenTwo.linear 1 16 [⟨1,2,1,2⟩,⟨2,1,1,2⟩]).lower = 4 := by
  rw [witnesses_combine_by_max_not_sum.1]
  decide
