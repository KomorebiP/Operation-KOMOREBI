import CoupledEntire

-- Without Q<1, the contraction ladder does not reach a radius-two point.
example : ∃ n : ℕ, (2 : ℝ) * 1 ^ n ≤ 1 := by
  norm_num
