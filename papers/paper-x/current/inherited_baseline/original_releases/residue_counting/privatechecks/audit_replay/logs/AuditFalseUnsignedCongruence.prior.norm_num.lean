import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
example : ((-1 : ℤ) : ZMod 3) = ((-1 : ℤ).natAbs : ZMod 3) := by
  norm_num
