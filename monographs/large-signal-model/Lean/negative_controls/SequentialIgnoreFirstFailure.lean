import KomorebiLSM.SequentialConfidence
/- A certain first failure spends a unit budget, even when all later stages cost zero. -/
example : (∑' n : ℕ, if n=0 then (1:NNReal) else 0) ≤ 0 := by
  norm_num
