import AVOC.QuoteAuthority
open Komorebi.AVOC.Affine.QuoteAuthority

def wideProbability : ProbabilityBand :=
  ⟨⟨0,1,by norm_num⟩,by norm_num,by norm_num⟩

/-- MUST fail: membership in an interval does not identify its lower endpoint. -/
example : (1 : ℚ) = wideProbability.lower := by
  norm_num [wideProbability]
