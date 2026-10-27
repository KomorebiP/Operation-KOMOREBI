import PaperXI.CocycleQuotient

/-! Exact universal properties of the quotient detected by the scalar
commutator. A pairing descends through A/L precisely when L lies in its
radical; that descended pairing is nondegenerate precisely at the radical. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CommutatorEnvelope
open CocycleCommutator

variable {A C : Type*} [CommGroup A] [CommGroup C]

/-- The character map descends through any subgroup of the radical. -/
def descendedCharacter (c : Cocycle A C) (L : Subgroup A) (hL : L ≤ radical c) :
    (A ⧸ L) →* (A →* C) := QuotientGroup.lift L (characterMap c) hL

@[simp] theorem descendedCharacter_mk (c : Cocycle A C) (L : Subgroup A)
    (hL : L ≤ radical c) (a b : A) :
    descendedCharacter c L hL (QuotientGroup.mk a) b = commutator c a b := rfl

theorem le_descendedCharacter_ker (c : Cocycle A C) (L : Subgroup A)
    (hL : L ≤ radical c) (z : A ⧸ L) : L ≤ (descendedCharacter c L hL z).ker := by
  induction z using QuotientGroup.induction_on with | H a =>
    intro b hb
    change commutator c a b = 1
    rw [commutator_swap, (mem_radical_iff c b).1 (hL hb) a, inv_one]

/-- The literal commutator pairing on an arbitrary admissible quotient. -/
def descendedPairing (c : Cocycle A C) (L : Subgroup A) (hL : L ≤ radical c) :
    (A ⧸ L) →* ((A ⧸ L) →* C) where
  toFun z := QuotientGroup.lift L (descendedCharacter c L hL z)
    (le_descendedCharacter_ker c L hL z)
  map_one' := by
    apply MonoidHom.ext
    intro z
    induction z using QuotientGroup.induction_on with | H a =>
      change descendedCharacter c L hL 1 a = 1
      simp
  map_mul' x y := by
    apply MonoidHom.ext
    intro z
    induction z using QuotientGroup.induction_on with | H a =>
      change descendedCharacter c L hL (x * y) a =
        descendedCharacter c L hL x a * descendedCharacter c L hL y a
      rw [map_mul]
      rfl

@[simp] theorem descendedPairing_mk (c : Cocycle A C) (L : Subgroup A)
    (hL : L ≤ radical c) (a b : A) :
    descendedPairing c L hL (QuotientGroup.mk a) (QuotientGroup.mk b) =
      commutator c a b := rfl

/-- The exact condition for the pairing to descend through both quotient variables. -/
theorem descends_iff (c : Cocycle A C) (L : Subgroup A) :
    (∃ B : (A ⧸ L) →* ((A ⧸ L) →* C),
      ∀ a b, B (QuotientGroup.mk a) (QuotientGroup.mk b) = commutator c a b) ↔
      L ≤ radical c := by
  constructor
  · rintro ⟨B, hB⟩ a ha
    apply (mem_radical_iff c a).2
    intro b
    rw [← hB, (QuotientGroup.eq_one_iff a).2 ha, map_one]
    rfl
  · intro hL
    exact ⟨descendedPairing c L hL, descendedPairing_mk c L hL⟩

/-- The pairing on a specified quotient is uniquely determined on representatives. -/
theorem descendedPairing_unique (c : Cocycle A C) (L : Subgroup A)
    (hL : L ≤ radical c) (B : (A ⧸ L) →* ((A ⧸ L) →* C))
    (hB : ∀ a b, B (QuotientGroup.mk a) (QuotientGroup.mk b) = commutator c a b) :
    B = descendedPairing c L hL := by
  apply MonoidHom.ext
  intro x
  apply MonoidHom.ext
  intro y
  induction x using QuotientGroup.induction_on with | H a =>
    induction y using QuotientGroup.induction_on with | H b =>
      exact hB a b

/-- The complete unique-descent statement. -/
theorem existsUnique_descendedPairing (c : Cocycle A C) (L : Subgroup A)
    (hL : L ≤ radical c) :
    ∃! B : (A ⧸ L) →* ((A ⧸ L) →* C),
      ∀ a b, B (QuotientGroup.mk a) (QuotientGroup.mk b) = commutator c a b :=
  ⟨descendedPairing c L hL, descendedPairing_mk c L hL,
    fun B hB => descendedPairing_unique c L hL B hB⟩

/-- The descended pairing is alternating on its actual quotient. -/
theorem descendedPairing_self (c : Cocycle A C) (L : Subgroup A)
    (hL : L ≤ radical c) (z : A ⧸ L) : descendedPairing c L hL z z = 1 := by
  induction z using QuotientGroup.induction_on with | H a =>
    exact commutator_self c a

/-- Nondegeneracy of the descended pairing is equivalent to quotienting by the full radical. -/
theorem nondegenerate_iff (c : Cocycle A C) (L : Subgroup A) (hL : L ≤ radical c) :
    (∀ x : A ⧸ L, (∀ y, descendedPairing c L hL x y = 1) → x = 1) ↔
      L = radical c := by
  constructor
  · intro h
    apply le_antisymm hL
    intro a ha
    apply (QuotientGroup.eq_one_iff a).1
    apply h
    intro y
    induction y using QuotientGroup.induction_on with | H b =>
      exact (mem_radical_iff c a).1 ha b
  · intro h x hx
    induction x using QuotientGroup.induction_on with | H a =>
      apply (QuotientGroup.eq_one_iff a).2
      rw [h]
      apply (mem_radical_iff c a).2
      intro b
      exact hx (QuotientGroup.mk b)

/-- Every admissible quotient maps canonically onto the radical quotient. -/
def quotientFactor (c : Cocycle A C) (L : Subgroup A) (hL : L ≤ radical c) :
    (A ⧸ L) →* (A ⧸ radical c) :=
  QuotientGroup.map L (radical c) (MonoidHom.id A) (by simpa using hL)

@[simp] theorem quotientFactor_mk (c : Cocycle A C) (L : Subgroup A)
    (hL : L ≤ radical c) (a : A) :
    quotientFactor c L hL (QuotientGroup.mk a) = QuotientGroup.mk a := rfl

/-- The canonical comparison is surjective. -/
theorem quotientFactor_surjective (c : Cocycle A C) (L : Subgroup A)
    (hL : L ≤ radical c) : Function.Surjective (quotientFactor c L hL) := by
  intro y
  induction y using QuotientGroup.induction_on with | H a =>
    exact ⟨QuotientGroup.mk a, rfl⟩

/-- The comparison preserves the literal descended pairings. -/
theorem quotientFactor_pairing (c : Cocycle A C) (L : Subgroup A)
    (hL : L ≤ radical c) (x y : A ⧸ L) :
    quotientPairing c (quotientFactor c L hL x) (quotientFactor c L hL y) =
      descendedPairing c L hL x y := by
  induction x using QuotientGroup.induction_on with | H a =>
    induction y using QuotientGroup.induction_on with | H b => rfl

/-- The map to the radical quotient is the unique factorization of its quotient map. -/
theorem existsUnique_quotientFactor (c : Cocycle A C) (L : Subgroup A)
    (hL : L ≤ radical c) :
    ∃! q : (A ⧸ L) →* (A ⧸ radical c),
      ∀ a, q (QuotientGroup.mk a) = QuotientGroup.mk a := by
  refine ⟨quotientFactor c L hL, quotientFactor_mk c L hL, ?_⟩
  intro q hq
  apply MonoidHom.ext
  intro x
  induction x using QuotientGroup.induction_on with | H a => exact hq a

/-- The character map factors uniquely and injectively through the radical quotient. -/
theorem existsUnique_injective_characterFactor (c : Cocycle A C) :
    ∃! f : (A ⧸ radical c) →* (A →* C),
      Function.Injective f ∧ ∀ a, f (QuotientGroup.mk a) = characterMap c a := by
  refine ⟨quotientCharacter c, ⟨quotientCharacter_injective c, fun _ => rfl⟩, ?_⟩
  intro f hf
  apply MonoidHom.ext
  intro x
  induction x using QuotientGroup.induction_on with | H a => exact hf.2 a

end PaperXI.CommutatorEnvelope
