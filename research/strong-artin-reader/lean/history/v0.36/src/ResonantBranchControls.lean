import SimultaneousGaugeBranch
import Mathlib.Tactic.NormNum

/-! Resonance permits both multiple infinite branches and finite dead ends.
Finite calculations use kernel reduction, not native_decide. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower.BranchControls

/-- The same residue fibre contains two distinct genuine roots in the resonant case. -/
theorem two_distinct_two_adic_square_roots :
    ∃ x y : ℤ_[2], x ≠ y ∧ x^2 = 1 ∧ y^2 = 1 ∧
      x.toZModPow 1 = 1 ∧ y.toZModPow 1 = 1 := by
  refine ⟨1, -1, ?_, by simp, by simp, by simp, ?_⟩
  · intro h
    have h' := congrArg (PadicInt.toZModPow 2) h
    have h'' : (1 : ZMod 4) = -1 := by simpa only [map_one, map_neg] using h'
    exact (by decide : (1 : ZMod 4) ≠ -1) h''
  · change PadicInt.toZModPow 1 (-1 : ℤ_[2]) = (1 : ZMod 2)
    rw [map_neg, map_one]
    decide

def red32to16 : ZMod 32 →+* ZMod 16 := ZMod.castHom (by decide) _

/-- 9 is a successful square-root prefix modulo 16. -/
theorem square_root_prefix_mod16 : (9 : ZMod 16)^2 = 1 := by decide

/-- The same prefix has no successor modulo 32. -/
theorem square_root_prefix_dies_mod32 :
    ¬ ∃ x : ZMod 32, red32to16 x = 9 ∧ x^2 = 1 := by decide

/-- Its finite certificate excludes a genuine 2-adic continuation. -/
theorem no_two_adic_root_above_nine :
    ¬ ∃ x : ℤ_[2], x.toZModPow 4 = 9 ∧ x^2 = 1 := by
  rintro ⟨x, hx, hs⟩
  apply square_root_prefix_dies_mod32
  refine ⟨x.toZModPow 5, ?_, ?_⟩
  · exact (PadicInt.cast_toZModPow 4 5 (by decide) x).trans hx
  · change (PadicInt.toZModPow 5 x)^2 = (1 : ZMod (2^5))
    rw [← map_pow, hs, map_one]

/-- All four finite roots occur modulo 16, but only two survive the next reduction. -/
theorem roots_mod16_and_extendable_prefixes :
    (∀ x : ZMod 16, x^2 = 1 ↔ x = 1 ∨ x = 7 ∨ x = 9 ∨ x = 15) ∧
    (∀ x : ZMod 16, (∃ y : ZMod 32, y^2 = 1 ∧ red32to16 y = x) ↔
      x = 1 ∨ x = 15) := by decide

end Komorebi.StrongArtin.FrobeniusTower.BranchControls
