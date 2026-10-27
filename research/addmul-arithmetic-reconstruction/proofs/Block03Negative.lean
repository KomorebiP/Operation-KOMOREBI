import Mathlib.Tactic.NormNum
/-! Intentionally false negative control: compilation must FAIL. -/
example : (36 : ℕ) = 35 := by norm_num
