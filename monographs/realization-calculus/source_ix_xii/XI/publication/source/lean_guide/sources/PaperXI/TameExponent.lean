import PaperXI.TameNorm
import PaperXI.ElementaryEnvelope
import Mathlib.GroupTheory.SpecificGroups.Cyclic

/-! Faithful exponent coordinates for genuine finite-field unit characters. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameExponent

/-- The standard injective character of the finite cyclic exponent group. -/
def rootEmbedding (N : ℕ) [NeZero N] : Multiplicative (ZMod N) →* ℂˣ where
  toFun x := ((ElementaryEnvelope.rootEquiv N x.toAdd).toMul : ℂˣ)
  map_one' := by
    change ((ElementaryEnvelope.rootEquiv N 0).toMul : ℂˣ) = 1
    rw [map_zero]
    rfl
  map_mul' x y := by
    change ((ElementaryEnvelope.rootEquiv N (x.toAdd + y.toAdd)).toMul : ℂˣ) = _
    rw [map_add]
    rfl

theorem rootEmbedding_injective (N : ℕ) [NeZero N] :
    Function.Injective (rootEmbedding N) := by
  intro x y h
  apply Multiplicative.toAdd.injective
  apply (ElementaryEnvelope.rootEquiv N).injective
  exact Subtype.ext h

variable (F : Type*) [Field F] [Finite F]

/-- A faithful complex character exists on every finite-field multiplicative group. -/
def faithfulCharacter : Fˣ →* ℂˣ :=
  letI : NeZero (Nat.card Fˣ) := ⟨Nat.card_pos.ne'⟩
  (rootEmbedding (Nat.card Fˣ)).comp (zmodCyclicMulEquiv (G := Fˣ) inferInstance).symm.toMonoidHom

theorem faithfulCharacter_injective : Function.Injective (faithfulCharacter F) := by
  let : NeZero (Nat.card Fˣ) := ⟨Nat.card_pos.ne'⟩
  exact (rootEmbedding_injective (Nat.card Fˣ)).comp
    (zmodCyclicMulEquiv (G := Fˣ) inferInstance).symm.injective

variable {F}

/-- A faithful character power is trivial precisely at a zero residue exponent. -/
theorem pow_eq_one_iff (χ : Fˣ →* ℂˣ) (hχ : Function.Injective χ) (a : ℕ) :
    χ ^ a = 1 ↔ (a : ZMod (Nat.card F - 1)) = 0 := by
  rw [ZMod.natCast_eq_zero_iff]
  rw [← Nat.card_units]
  constructor
  · intro h
    obtain ⟨g, hg⟩ := IsCyclic.exists_generator (α := Fˣ)
    rw [← orderOf_eq_card_of_forall_mem_zpowers hg, orderOf_dvd_iff_pow_eq_one]
    apply hχ
    rw [map_pow, map_one]
    exact congrArg (fun f : Fˣ →* ℂˣ => f g) h
  · rintro ⟨k, rfl⟩
    apply MonoidHom.ext
    intro x
    change χ x ^ (Nat.card Fˣ * k) = 1
    rw [pow_mul, ← map_pow, pow_card_eq_one', map_one, one_pow]

omit [Finite F] in
/-- Exponent coordinates are periodic by the actual unit-group cardinality. -/
theorem pow_add_card (χ : Fˣ →* ℂˣ) (a : ℕ) :
    χ ^ (a + (Nat.card F - 1)) = χ ^ a := by
  apply MonoidHom.ext
  intro x
  change χ x ^ (a + (Nat.card F - 1)) = χ x ^ a
  rw [pow_add, ← Nat.card_units, ← map_pow χ x (Nat.card Fˣ),
    pow_card_eq_one', map_one, mul_one]

omit [Finite F] in
/-- Products of actual characters add exponent coordinates. -/
theorem product (χ : Fˣ →* ℂˣ) (a b : ℕ) : χ ^ a * χ ^ b = χ ^ (a + b) :=
  (pow_add χ a b).symm

/-- Every complex unit character has an exponent in any faithful coordinate system. -/
theorem exists_exponent (χ : Fˣ →* ℂˣ) (hχ : Function.Injective χ)
    (η : Fˣ →* ℂˣ) : ∃ a < Nat.card F - 1, η = χ ^ a := by
  let : NeZero (Nat.card Fˣ) := ⟨Nat.card_pos.ne'⟩
  obtain ⟨g, hg⟩ := IsCyclic.exists_generator (α := Fˣ)
  have hp : IsPrimitiveRoot (χ g) (Nat.card Fˣ) := by
    rw [IsPrimitiveRoot.iff_orderOf, orderOf_injective χ hχ,
      orderOf_eq_card_of_forall_mem_zpowers hg]
  have hη : η g ∈ rootsOfUnity (Nat.card Fˣ) ℂ := by
    rw [mem_rootsOfUnity, ← map_pow, pow_card_eq_one', map_one]
  obtain ⟨a, ha, heq⟩ := hp.eq_pow_of_mem_rootsOfUnity hη
  refine ⟨a, by simpa only [Nat.card_units] using ha, ?_⟩
  apply (MonoidHom.eq_iff_eq_on_generator hg η (χ ^ a)).mpr
  exact heq.symm

/-- Equality of actual characters is exactly equality of residue exponents. -/
theorem pow_eq_pow_iff (χ : Fˣ →* ℂˣ) (hχ : Function.Injective χ) (a b : ℕ) :
    χ ^ a = χ ^ b ↔ (a : ZMod (Nat.card F - 1)) = b := by
  obtain ⟨g, hg⟩ := IsCyclic.exists_generator (α := Fˣ)
  rw [MonoidHom.eq_iff_eq_on_generator hg]
  change χ g ^ a = χ g ^ b ↔ _
  rw [pow_eq_pow_iff_modEq, orderOf_injective χ hχ,
    orderOf_eq_card_of_forall_mem_zpowers hg, Nat.card_units,
    ZMod.natCast_eq_natCast_iff]

/-- Residue exponents parameterize actual characters, using their natural representatives. -/
def coordinate (χ : Fˣ →* ℂˣ) (a : ZMod (Nat.card F - 1)) : Fˣ →* ℂˣ := χ ^ a.val

/-- The parameterization is a bijection, not just a collection of selected powers. -/
theorem coordinate_bijective (χ : Fˣ →* ℂˣ) (hχ : Function.Injective χ) :
    Function.Bijective (coordinate χ) := by
  let : NeZero (Nat.card F - 1) := ⟨by rw [← Nat.card_units]; exact Nat.card_pos.ne'⟩
  constructor
  · intro a b h
    have h' := (pow_eq_pow_iff χ hχ a.val b.val).mp h
    simpa only [ZMod.natCast_zmod_val] using h'
  · intro η
    obtain ⟨a, ha, hη⟩ := exists_exponent χ hχ η
    refine ⟨a, ?_⟩
    simpa only [coordinate, ZMod.val_cast_of_lt ha] using hη.symm

end PaperXI.TameExponent
