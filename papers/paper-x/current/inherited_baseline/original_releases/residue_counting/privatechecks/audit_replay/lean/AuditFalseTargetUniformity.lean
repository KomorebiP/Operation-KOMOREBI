import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
example : (Finset.univ.filter (fun x : ZMod 4 => 2 * x = 1)).card = 1 := by
  have hn : (Finset.univ.filter (fun x : ZMod 4 => 2 * x = 1)).card = 0 := by decide
  rw [hn]
  norm_num
