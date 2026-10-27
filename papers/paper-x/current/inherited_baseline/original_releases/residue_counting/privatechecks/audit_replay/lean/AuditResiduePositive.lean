import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
example : ((-1 : ℤ) : ZMod 3) ≠ ((-1 : ℤ).natAbs : ZMod 3) := by decide
example : ∀ a b : ZMod 4, (a ^ 2 + b ^ 2).val % 2 = 1 → a ^ 2 + b ^ 2 = 1 := by
  decide
example : (Finset.univ.filter (fun x : ZMod 4 => 2 * x = 0)).card = 2 := by decide
example : (Finset.univ.filter (fun x : ZMod 4 => 2 * x = 1)).card = 0 := by decide
example : (Finset.univ.filter (fun x : ZMod 4 => 2 * x = 2)).card = 2 := by decide
