import KomorebiPadic.ResidualMinimalityExamples
example : Nat.card (ZMod 5) ≤ 1 := by
  have h : Nat.card (ZMod 5) = 5 := by simp
  rw [h]
  decide
