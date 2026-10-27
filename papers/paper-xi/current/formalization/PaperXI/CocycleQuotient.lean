import PaperXI.CocycleCommutator

/-! Paper XI, Proposition 8.2: the actual quotient by the commutator radical. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CocycleCommutator

variable {A C : Type*} [CommGroup A] [CommGroup C]

/-- First descent: characters indexed by the actual radical quotient. -/
def quotientCharacter (c : Cocycle A C) : A ⧸ radical c →* (A →* C) :=
  QuotientGroup.kerLift (characterMap c)

@[simp] theorem quotientCharacter_mk (c : Cocycle A C) (a b : A) :
    quotientCharacter c (QuotientGroup.mk a) b = commutator c a b := rfl

theorem radical_le_quotientCharacter_ker (c : Cocycle A C)
    (z : A ⧸ radical c) : radical c ≤ (quotientCharacter c z).ker := by
  induction z using QuotientGroup.induction_on with | H a =>
    intro b hb
    change commutator c a b = 1
    rw [commutator_swap, (mem_radical_iff c b).mp hb a, inv_one]

/-- The commutator descends in both variables to the radical quotient. -/
def quotientPairing (c : Cocycle A C) :
    (A ⧸ radical c) →* ((A ⧸ radical c) →* C) where
  toFun z := QuotientGroup.lift (radical c) (quotientCharacter c z)
    (radical_le_quotientCharacter_ker c z)
  map_one' := by
    apply MonoidHom.ext
    intro z
    induction z using QuotientGroup.induction_on with | H a =>
      change quotientCharacter c 1 a = 1
      simp
  map_mul' x y := by
    apply MonoidHom.ext
    intro z
    induction z using QuotientGroup.induction_on with | H a =>
      change quotientCharacter c (x * y) a = quotientCharacter c x a * quotientCharacter c y a
      rw [map_mul]
      rfl

@[simp] theorem quotientPairing_mk (c : Cocycle A C) (a b : A) :
    quotientPairing c (QuotientGroup.mk a) (QuotientGroup.mk b) = commutator c a b := rfl

/-- Alternation is inherited by the descended pairing. -/
theorem quotientPairing_self (c : Cocycle A C) (z : A ⧸ radical c) :
    quotientPairing c z z = 1 := by
  induction z using QuotientGroup.induction_on with | H a =>
    exact commutator_self c a

theorem quotientPairing_swap (c : Cocycle A C) (x y : A ⧸ radical c) :
    quotientPairing c y x = (quotientPairing c x y)⁻¹ := by
  induction x using QuotientGroup.induction_on with | H a =>
    induction y using QuotientGroup.induction_on with | H b =>
      exact commutator_swap c a b

/-- The quotient pairing has trivial left radical, proved from the quotient
relation and the original cocycle rather than assumed as data. -/
theorem quotientPairing_nondegenerate_left (c : Cocycle A C) (z : A ⧸ radical c) :
    (∀ w, quotientPairing c z w = 1) ↔ z = 1 := by
  induction z using QuotientGroup.induction_on with | H a =>
    constructor
    · intro h
      apply (QuotientGroup.eq_one_iff a).2
      apply (mem_radical_iff c a).2
      intro b
      exact h (QuotientGroup.mk b)
    · intro h w
      rw [h, map_one]
      rfl

/-- The quotient pairing also has trivial right radical. -/
theorem quotientPairing_nondegenerate_right (c : Cocycle A C) (z : A ⧸ radical c) :
    (∀ w, quotientPairing c w z = 1) ↔ z = 1 := by
  rw [← quotientPairing_nondegenerate_left c z]
  constructor <;> intro h w
  · rw [quotientPairing_swap, h, inv_one]
  · rw [quotientPairing_swap, h, inv_one]

/-- Nondegeneracy can equivalently be read as injectivity into the character group. -/
theorem quotientCharacter_injective (c : Cocycle A C) :
    Function.Injective (quotientCharacter c) := QuotientGroup.kerLift_injective _

end PaperXI.CocycleCommutator
