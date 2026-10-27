import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
example : ∃ a b : ZMod 4, a ^ 2 + b ^ 2 = 3 := by
  have hn : ¬ ∃ a b : ZMod 4, a ^ 2 + b ^ 2 = 3 := by decide
  simp only [hn]
