import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

set_option autoImplicit false
namespace KomorebiAddMul.Block03

/-- Exact Teichmueller representatives modulo 9 of F_3. -/
def teichThree (x : ZMod 3) : ZMod 9 :=
  if x = 0 then 0 else if x = 1 then 1 else 8

/-- The representatives preserve multiplication but not addition. -/
theorem teichThree_mul (x y : ZMod 3) :
    teichThree (x*y) = teichThree x * teichThree y := by
  fin_cases x <;> fin_cases y <;> decide

/-- The exact first Witt carry in the nontrivial layer p=3, N=2. -/
def carryThree (x y : ZMod 3) : ZMod 3 :=
  (((teichThree x + teichThree y - teichThree (x+y)).val / 3 : ℕ) : ZMod 3)

/-- Three-point nonzero cycle is the obstruction to a split additive section. -/
theorem nonzero_teich_carry_cycle :
    carryThree 1 0 + carryThree 1 1 + carryThree 1 2 = (1 : ZMod 3) := by
  decide

/-- The first nonzero carry in W_2(F_3). -/
theorem teich_carry_one_one : carryThree 1 1 = 1 := by decide

/-- Associativity forces the additive carry to satisfy a cocycle identity. -/
theorem teich_carry_cocycle (x y z : ZMod 3) :
    carryThree x y + carryThree (x+y) z =
      carryThree y z + carryThree x (y+z) := by
  fin_cases x <;> fin_cases y <;> fin_cases z <;> decide

/-- A lift of the additive generator of F_3 to Z/9 cannot have
additive order three. This rules out any additive section of reduction. -/
private theorem generator_obstruction :
    ∀ x : ZMod 9, (3 : ℕ) • x = 0 → x.val % 3 ≠ 1 := by decide

theorem no_additive_section_mod9 (s : ZMod 3 →+ ZMod 9)
    (hs : (s 1).val % 3 = 1) : False := by
  have hthree : (3 : ℕ) • (1 : ZMod 3) = 0 := by decide
  have himage : (3 : ℕ) • s 1 = 0 := by
    rw [← s.map_nsmul, hthree, s.map_zero]
  exact (generator_obstruction (s 1) himage) hs

end KomorebiAddMul.Block03

-- Verification/Axiom audit (part of reproducible source).
#print axioms KomorebiAddMul.Block03.teichThree_mul
#print axioms KomorebiAddMul.Block03.nonzero_teich_carry_cycle
#print axioms KomorebiAddMul.Block03.teich_carry_one_one
#print axioms KomorebiAddMul.Block03.teich_carry_cocycle
#print axioms KomorebiAddMul.Block03.no_additive_section_mod9
