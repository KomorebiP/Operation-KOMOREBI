import Mathlib.FieldTheory.LinearDisjoint
import Mathlib.FieldTheory.PrimitiveElement
import Mathlib.NumberTheory.NumberField.Cyclotomic.Galois
import Mathlib.NumberTheory.LSeries.PrimesInAP
import Mathlib.RingTheory.RootsOfUnity.AlgebraicallyClosed

/-! Auxiliary cyclotomic fields can be chosen disjoint from a supplied number field.
The proof uses finite intermediate fields and pairwise disjoint prime conductors,
without invoking ramification or prime distribution over number fields. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.AuxiliaryCyclotomicDisjoint
open IntermediateField

section FiniteExceptions
variable {k M I : Type*} [Field k] [Field M] [Algebra k M]
  (L : IntermediateField k M) [Finite (IntermediateField k L)]
  (C : I → IntermediateField k M)

/-- Pairwise disjoint extensions have nontrivial intersection with a fixed
extension at only finitely many indices, if that extension has finitely many
intermediate fields. -/
theorem finite_nontrivial_intersections
    (hC : ∀ i j, i ≠ j → C i ⊓ C j = ⊥) :
    Set.Finite {i | L ⊓ C i ≠ ⊥} := by
  let f : {i // L ⊓ C i ≠ ⊥} → IntermediateField k L :=
    fun i => (L ⊓ C i.val).restrict inf_le_left
  have hf : Function.Injective f := by
    intro i j hij
    apply Subtype.ext
    by_contra hne
    have heq : L ⊓ C i.val = L ⊓ C j.val := by
      have hh := congrArg IntermediateField.lift hij
      simpa only [f, lift_restrict] using hh
    apply i.property
    apply le_antisymm _ bot_le
    calc
      L ⊓ C i.val ≤ C i.val ⊓ C j.val :=
        le_inf inf_le_right (heq ▸ inf_le_right)
      _ = ⊥ := hC i.val j.val hne
  exact Set.finite_coe_iff.mp (Finite.of_injective f hf)
end FiniteExceptions

section CyclotomicFields
variable (M : Type*) [Field M] [CharZero M] [IsAlgClosed M] [Algebra.IsAlgebraic ℚ M]

/-- The actual cyclotomic subfield in the fixed ambient algebraically closed field. -/
def cyclotomicPart (n : ℕ) [NeZero n] : IntermediateField ℚ M :=
  IntermediateField.adjoin ℚ {Classical.choose (HasEnoughRootsOfUnity.exists_primitiveRoot M n)}

instance cyclotomicPart_isCyclotomic (n : ℕ) [NeZero n] :
    IsCyclotomicExtension {n} ℚ (cyclotomicPart M n) :=
  IsPrimitiveRoot.intermediateField_adjoin_isCyclotomicExtension ℚ
    (Classical.choose_spec (HasEnoughRootsOfUnity.exists_primitiveRoot M n))

instance cyclotomicPart_finite (n : ℕ) [NeZero n] :
    FiniteDimensional ℚ (cyclotomicPart M n) :=
  IsCyclotomicExtension.finite_of_singleton n ℚ _

instance cyclotomicPart_numberField (n : ℕ) [NeZero n] :
    NumberField (cyclotomicPart M n) := {}

/-- Coprime conductors give linearly disjoint actual cyclotomic subfields. -/
theorem cyclotomicPart_linearDisjoint (m n : ℕ) [NeZero m] [NeZero n]
    (h : m.Coprime n) : (cyclotomicPart M m).LinearDisjoint (cyclotomicPart M n) := by
  have : NeZero (m.lcm n) := ⟨Nat.lcm_ne_zero (NeZero.ne _) (NeZero.ne _)⟩
  have : IsCyclotomicExtension {m.lcm n} ℚ
      (cyclotomicPart M m ⊔ cyclotomicPart M n : IntermediateField ℚ M) :=
    IntermediateField.isCyclotomicExtension_lcm_sup ℚ M m n _ _
  have : NumberField (cyclotomicPart M m ⊔ cyclotomicPart M n : IntermediateField ℚ M) :=
    {}
  apply IntermediateField.LinearDisjoint.of_finrank_sup
  rw [IsCyclotomicExtension.Rat.finrank (m.lcm n),
    IsCyclotomicExtension.Rat.finrank m, IsCyclotomicExtension.Rat.finrank n,
    h.lcm_eq_mul, Nat.totient_mul h]

/-- The cyclotomic field of prime conductor. -/
def primeCyclotomicPart (p : Nat.Primes) : IntermediateField ℚ M :=
  let : NeZero (p : ℕ) := ⟨p.property.ne_zero⟩
  cyclotomicPart M (p : ℕ)

instance primeCyclotomicPart_isCyclotomic (p : Nat.Primes) :
    IsCyclotomicExtension {(p : ℕ)} ℚ (primeCyclotomicPart M p) := by
  let : NeZero (p : ℕ) := ⟨p.property.ne_zero⟩
  exact cyclotomicPart_isCyclotomic M p

instance primeCyclotomicPart_finite (p : Nat.Primes) :
    FiniteDimensional ℚ (primeCyclotomicPart M p) := by
  let : NeZero (p : ℕ) := ⟨p.property.ne_zero⟩
  exact cyclotomicPart_finite M p

instance primeCyclotomicPart_numberField (p : Nat.Primes) :
    NumberField (primeCyclotomicPart M p) := {}

/-- Distinct prime conductors give trivial intersection. -/
theorem primeCyclotomicPart_inf (p q : Nat.Primes) (hpq : p ≠ q) :
    primeCyclotomicPart M p ⊓ primeCyclotomicPart M q = ⊥ := by
  let : NeZero (p : ℕ) := ⟨p.property.ne_zero⟩
  let : NeZero (q : ℕ) := ⟨q.property.ne_zero⟩
  apply (cyclotomicPart_linearDisjoint M (p : ℕ) (q : ℕ) _).inf_eq_bot
  exact (Nat.coprime_primes p.property q.property).mpr (fun h => hpq (Subtype.ext h))

/-- Only finitely many prime cyclotomic fields intersect a fixed number field
nontrivially. The finite exceptional set is derived, not supplied. -/
theorem finite_bad_prime_conductors (L : IntermediateField ℚ M) [NumberField L] :
    Set.Finite {p : Nat.Primes | L ⊓ primeCyclotomicPart M p ≠ ⊥} := by
  have : Finite (IntermediateField ℚ L) :=
    Field.finite_intermediateField_of_exists_primitive_element ℚ L
      (Field.exists_primitive_element ℚ L)
  exact finite_nontrivial_intersections L (primeCyclotomicPart M)
    (primeCyclotomicPart_inf M)

/-- A prime conductor congruent to one modulo any positive integer can be
chosen outside every finite exclusion, with cyclotomic field disjoint from L. -/
theorem exists_prime_conductor (L : IntermediateField ℚ M) [NumberField L]
    (n : ℕ) [NeZero n] (forbidden : Finset ℕ) (B : ℕ) :
    ∃ p : Nat.Primes, B < (p : ℕ) ∧ (p : ℕ) ∉ forbidden ∧
      ((p : ℕ) : ZMod n) = 1 ∧
      (primeCyclotomicPart M p).LinearDisjoint L := by
  classical
  let bad := (finite_bad_prime_conductors M L).toFinset.image (fun p : Nat.Primes => (p : ℕ))
  let exc := forbidden ∪ bad
  obtain ⟨p, hpB, hp, hres⟩ := Nat.forall_exists_prime_gt_and_eq_mod
    (show IsUnit (1 : ZMod n) from isUnit_one) (max B (exc.sup id))
  have hpnot : p ∉ exc := by
    intro hm
    exact (not_lt_of_ge ((Finset.le_sup (f := id) hm).trans (le_max_right _ _))) hpB
  let p' : Nat.Primes := ⟨p, hp⟩
  have hbad : L ⊓ primeCyclotomicPart M p' = ⊥ := by
    by_contra h
    apply hpnot
    apply Finset.mem_union_right
    apply Finset.mem_image.mpr
    exact ⟨p', (Set.Finite.mem_toFinset _).mpr h, rfl⟩
  refine ⟨p', (le_max_left _ _).trans_lt hpB, ?_, hres, ?_⟩
  · intro hm
    exact hpnot (Finset.mem_union_left _ hm)
  · have : IsCyclotomicExtension {(p' : ℕ)} ℚ (primeCyclotomicPart M p') :=
      primeCyclotomicPart_isCyclotomic M p'
    have : IsGalois ℚ (primeCyclotomicPart M p') :=
      IsCyclotomicExtension.isGalois {(p' : ℕ)} ℚ _
    apply IntermediateField.LinearDisjoint.of_inf_eq_bot
    simpa only [inf_comm] using hbad

end CyclotomicFields
end PaperX.AuxiliaryCyclotomicDisjoint
