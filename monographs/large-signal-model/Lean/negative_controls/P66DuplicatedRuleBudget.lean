import KomorebiLSM.CountableConfidence

open scoped BigOperators NNReal
private noncomputable def budget (_ : Unit) : NNReal := 1/4
private def duplicate (_ : Fin 2) : Unit := ()
/- A noninjective relabeling duplicates a registered rule and its cost.
It cannot be used as the exact budget-preserving equivalence transport. -/
example : (∑' k : Fin 2,budget (duplicate k))≤∑' j : Unit,budget j := by
  norm_num [tsum_fintype,Fin.sum_univ_succ,budget,duplicate]
  change ((1/2 : NNReal) : ℝ)≤((1/4 : NNReal) : ℝ)
  norm_num
