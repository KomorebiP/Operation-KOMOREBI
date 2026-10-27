import AVOC.QuoteAuthority
open Komorebi.AVOC.Affine.QuoteAuthority

def candidateA : RatBand := ⟨5,12,by norm_num⟩
def candidateB : RatBand := ⟨8,10,by norm_num⟩

/-- MUST fail: overlapping intervals do not certify A's lower bound above B's upper bound. -/
example : candidateB.upper ≤ candidateA.lower := by
  norm_num [candidateA,candidateB]
