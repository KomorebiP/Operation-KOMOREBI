import PaperXI.FourierCovariance
import Mathlib.RepresentationTheory.Basic
import Mathlib.NumberTheory.LegendreSymbol.AddCharacter

/-! Actual representations of the additive finite cyclic group. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicAction
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable {M : ℕ}

abbrev Action := Representation K (Multiplicative (ZMod M)) V

def operator (ρ : Action (K := K) (V := V) (M := M)) (a : ZMod M) : Module.End K V :=
  ρ (Multiplicative.ofAdd a)

@[simp] theorem operator_zero (ρ : Action (K := K) (V := V) (M := M)) :
    operator ρ 0 = 1 := map_one ρ

theorem operator_add (ρ : Action (K := K) (V := V) (M := M)) (a b : ZMod M) :
    operator ρ (a + b) = operator ρ a * operator ρ b := map_mul ρ _ _

theorem operator_nsmul (ρ : Action (K := K) (V := V) (M := M)) (a : ZMod M) (n : ℕ) :
    operator ρ (n • a) = operator ρ a ^ n := by
  induction n with
  | zero => simp
  | succ n ih => rw [succ_nsmul, operator_add, ih, pow_succ]

variable [NeZero M]

theorem operator_mul (ρ : Action (K := K) (V := V) (M := M)) (a b : ZMod M) :
    operator ρ (a * b) = operator ρ a ^ b.val := by
  have h : a * b = b.val • a := by simp [nsmul_eq_mul, mul_comm]
  rw [h, operator_nsmul]

theorem operator_eq_generator_pow (ρ : Action (K := K) (V := V) (M := M)) (a : ZMod M) :
    operator ρ a = operator ρ 1 ^ a.val := by simpa using operator_mul ρ 1 a

omit [NeZero M] in
theorem generator_period (ρ : Action (K := K) (V := V) (M := M)) :
    operator ρ 1 ^ M = 1 := by
  rw [← operator_nsmul]
  simp [nsmul_eq_mul]

/-- The generator conjugation relation implies every cyclic action relation. -/
theorem conjugation_from_generator (ρ : Action (K := K) (V := V) (M := M))
    (F : V ≃ₗ[K] V) (q : ZMod M)
    (h : F.conj (operator ρ 1) = operator ρ q) (a : ZMod M) :
    F.conj (operator ρ a) = operator ρ (q * a) := by
  rw [operator_eq_generator_pow ρ a, operator_mul]
  have hp : F.conj (operator ρ 1 ^ a.val) = F.conj (operator ρ 1) ^ a.val :=
    map_pow F.conjRingEquiv _ _
  rw [hp, h]

end PaperXI.CyclicAction
