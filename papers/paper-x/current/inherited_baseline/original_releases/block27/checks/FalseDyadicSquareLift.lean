import PaperX.PadicQuadraticSplitting
example : ∃ x : ℚ_[2], x ^ 2 = -1 := by
  rw [iff_false_intro PaperX.PadicQuadraticSplitting.no_root_two]
