import Mathlib.NumberTheory.Padics.RingHoms
import Mathlib.Algebra.Ring.Commute
import Mathlib.Tactic

/-! Exact arithmetic boundaries for the dyadic quadratic packet equation.
The finite roots are computed in the actual quotient rings.  In particular,
an occupied node at precision three need not have a child at precision four.
-/
set_option autoImplicit false
namespace PaperX.QuadraticPacketBoundary

/-- There are exactly two integral dyadic roots, since the integers are a domain. -/
theorem dyadic_roots (x : ℤ_[2]) : x ^ 2 = 1 ↔ x = 1 ∨ x = -1 :=
  sq_eq_one_iff

theorem dyadic_signs_distinct : (1 : ℤ_[2]) ≠ -1 := by norm_num

/-- The two integral packets have the same residual value. -/
theorem signs_same_mod_two :
    (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) 1 =
      (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) (-1) := by
  simp

/-- The actual reduction modulo four separates them. -/
theorem signs_distinct_mod_four :
    (PadicInt.toZModPow 2 : ℤ_[2] →+* ZMod 4) 1 ≠
      (PadicInt.toZModPow 2 : ℤ_[2] →+* ZMod 4) (-1) := by
  simpa only [map_one, map_neg] using (by decide : (1 : ZMod 4) ≠ -1)

def reduceSixteen : ZMod 16 →+* ZMod 8 := ZMod.castHom (by decide) (ZMod 8)

theorem three_root_mod_eight : (3 : ZMod 8) ^ 2 = 1 := by decide +kernel

theorem three_not_sign_mod_eight : (3 : ZMod 8) ≠ 1 ∧ (3 : ZMod 8) ≠ -1 := by
  decide +kernel

/-- The quotient ring has four roots, although the integral ring has only two. -/
theorem roots_mod_eight (x : ZMod 8) :
    x ^ 2 = 1 ↔ x = 1 ∨ x = 3 ∨ x = 5 ∨ x = 7 := by
  revert x
  decide +kernel

theorem roots_mod_sixteen (x : ZMod 16) :
    x ^ 2 = 1 ↔ x = 1 ∨ x = 7 ∨ x = 9 ∨ x = 15 := by
  revert x
  decide +kernel

/-- Only the reductions of the two integral signs have children at this step. -/
theorem has_root_lift_mod_sixteen (x : ZMod 8) :
    (∃ y : ZMod 16, y ^ 2 = 1 ∧ reduceSixteen y = x) ↔ x = 1 ∨ x = -1 := by
  revert x
  decide +kernel

theorem three_no_root_lift_mod_sixteen :
    ¬ ∃ y : ZMod 16, y ^ 2 = 1 ∧ reduceSixteen y = 3 := by
  rw [has_root_lift_mod_sixteen]
  exact not_or_intro three_not_sign_mod_eight.1 three_not_sign_mod_eight.2

/-- A finite admissible scalar can therefore fail to lift to any integral packet. -/
theorem three_no_integral_root_lift :
    ¬ ∃ x : ℤ_[2], x ^ 2 = 1 ∧ PadicInt.toZModPow 3 x = 3 := by
  rintro ⟨x, hx, hr⟩
  rcases (dyadic_roots x).mp hx with rfl | rfl
  · exact three_not_sign_mod_eight.1 (by simpa only [map_one] using hr.symm)
  · exact three_not_sign_mod_eight.2 (by simpa only [map_neg, map_one] using hr.symm)

end PaperX.QuadraticPacketBoundary
