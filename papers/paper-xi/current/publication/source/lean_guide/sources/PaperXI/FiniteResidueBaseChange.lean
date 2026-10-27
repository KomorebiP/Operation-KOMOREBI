import PaperXI.ResidueDegreeBaseChange
import Mathlib.FieldTheory.Finite.Basic

/-! Genuine finite-residue Frobenius, base-field change, and period detection.
The chosen embeddings are inputs, not a constructed unramified extension of a
local field. Residue Frobenius is never replaced by an abstract cyclic label. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteResidueBaseChange
open PaperXI.ResidueWeil PaperXI.ResidueDegreeBaseChange

variable (k L : Type*) [Field k] [Fintype k] [Field L] [Algebra k L]
  [Algebra.IsAlgebraic k L]

/-- The literal q-power automorphism, q = |k|. -/
def arithmetic : RingAut L :=
  (FiniteField.frobeniusAlgEquivOfAlgebraic k L).toRingEquiv

/-- The inverse q-power automorphism fixes the geometric convention. -/
def geometric : RingAut L := (arithmetic k L)⁻¹

@[simp] theorem arithmetic_apply (x : L) : arithmetic k L x = x ^ Fintype.card k := rfl

theorem arithmetic_pow_apply (n : ℕ) (x : L) :
    (arithmetic k L ^ n) x = x ^ (Fintype.card k ^ n) := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [pow_succ']
    change arithmetic k L ((arithmetic k L ^ n) x) = _
    rw [arithmetic_apply, ih, ← pow_mul, pow_succ]

@[simp] theorem geometric_inverse_power (x : L) :
    (geometric k L x) ^ Fintype.card k = x :=
  (arithmetic k L).apply_symm_apply x

section Tower
variable (k' : Type*) [Field k'] [Fintype k'] [Algebra k k']
  [Algebra k' L] [Algebra.IsAlgebraic k' L]

/-- Finite-field cardinality supplies the exponent. No degree/Frobenius equality is assumed. -/
theorem arithmetic_tower :
    arithmetic k L ^ Module.finrank k k' = arithmetic k' L := by
  apply RingEquiv.ext
  intro x
  rw [arithmetic_pow_apply, arithmetic_apply]
  rw [← Module.card_eq_pow_finrank (K := k) (V := k')]

/-- Geometric Frobenius of the enlarged residue base is the f-th power. -/
theorem geometric_tower :
    geometric k L ^ Module.finrank k k' = geometric k' L := by
  unfold geometric
  rw [inv_pow, arithmetic_tower k L k']

/-- Base change in the residue Frobenius produces an actual degree-divisible group. -/
def pullbackEquiv {D : Type*} [Group D] (r : D →* RingAut L) :
    Pullback r (geometric k' L) ≃*
      periodSubgroup r (geometric k L) (Module.finrank k k') := by
  rw [← geometric_tower k L k']
  exact periodEquiv r (geometric k L) (Module.finrank_pos.ne')
end Tower

section Order
variable [Finite L]

/-- Forgetting scalar-fixing data is an injective automorphism-group homomorphism. -/
def forget : (L ≃ₐ[k] L) →* RingAut L where
  toFun e := e.toRingEquiv
  map_one' := rfl
  map_mul' _ _ := rfl

omit [Fintype k] [Algebra.IsAlgebraic k L] [Finite L] in
theorem forget_injective : Function.Injective (forget k L) := by
  intro a b h
  apply AlgEquiv.ext
  intro x
  exact RingEquiv.congr_fun h x

/-- Exact field degree, rather than an assumed period certificate. -/
theorem geometric_order : orderOf (geometric k L) = Module.finrank k L := by
  rw [geometric, orderOf_inv]
  exact (orderOf_injective (forget k L) (forget_injective k L) _).trans
    (FiniteField.orderOf_frobeniusAlgEquivOfAlgebraic k L)

/-- Includes zero and negative exponents. -/
theorem geometric_zpow_eq_one (m : ℤ) :
    geometric k L ^ m = 1 ↔ (Module.finrank k L : ℤ) ∣ m := by
  rw [← orderOf_dvd_iff_zpow_eq_one, geometric_order]
end Order

end PaperXI.FiniteResidueBaseChange
