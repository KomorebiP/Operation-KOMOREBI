import Mathlib.NumberTheory.NumberField.Discriminant.Different
import Mathlib.NumberTheory.RamificationInertia.Galois
import Mathlib.NumberTheory.NumberField.Basic
import Mathlib.RingTheory.Ideal.Int
import Mathlib.FieldTheory.Galois.IsGaloisGroup

/-! Genuine unramifiedness in a finite normal number field implies trivial
inertia and uniqueness of the arithmetic Frobenius action at a chosen prime.
The arithmetic hypothesis is ramification index one, not a renamed assertion
that inertia acts trivially. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.UnramifiedFrobeniusUniqueness
open NumberField
open scoped Pointwise

variable (L : Type*) [Field L] [NumberField L] [Normal ℚ L]
  (p : ℕ) [hp : Fact p.Prime]
  (P : Ideal (𝓞 L)) [P.IsMaximal] [P.LiesOver (Ideal.span {(p : ℤ)})]

include p hp in
/-- The cardinality of the actual inertia subgroup is the actual ramification
index over the integers. -/
theorem inertia_card_eq_ramificationIdx :
    Nat.card (P.inertia Gal(L/ℚ)) = Ideal.ramificationIdx P ℤ := by
  let : (Ideal.span {(p : ℤ)}).IsMaximal := Int.ideal_span_isMaximal_of_prime p
  let : IsGalois ℚ L := { }
  let : IsGaloisGroup Gal(L/ℚ) ℤ (𝓞 L) :=
    IsGaloisGroup.of_isFractionRing Gal(L/ℚ) ℤ (𝓞 L) ℚ L
  rw [Ideal.card_inertia_eq_ramificationIdxIn (Ideal.span {(p : ℤ)}) P,
    Ideal.ramificationIdxIn_eq_ramificationIdx (Ideal.span {(p : ℤ)}) P Gal(L/ℚ)]

include p hp in
/-- An unramified prime has trivial actual inertia. -/
theorem inertia_eq_bot (he : Ideal.ramificationIdx P ℤ = 1) :
    P.inertia Gal(L/ℚ) = ⊥ := by
  have hc : Nat.card (P.inertia Gal(L/ℚ)) = 1 :=
    (inertia_card_eq_ramificationIdx L p P).trans he
  exact (Subgroup.eq_bot_iff_card _).mpr hc

include p hp in
/-- The commutative-algebra notion of unramifiedness gives the same conclusion. -/
theorem inertia_eq_bot_of_isUnramifiedAt [Algebra.IsUnramifiedAt ℤ P] :
    P.inertia Gal(L/ℚ) = ⊥ := by
  exact inertia_eq_bot L p P (Ideal.ramificationIdx_eq_one P ℤ)

include hp in
/-- Unramifiedness makes the action of the decomposition group on the actual
residue extension faithful. -/
theorem stabilizerHom_injective (he : Ideal.ramificationIdx P ℤ = 1) :
    Function.Injective (Ideal.Quotient.stabilizerHom P (Ideal.span {(p : ℤ)}) Gal(L/ℚ)) := by
  apply (MonoidHom.ker_eq_bot_iff _).mp
  rw [Ideal.Quotient.ker_stabilizerHom]
  apply le_antisymm ?_ bot_le
  intro σ hσ
  apply Subgroup.mem_bot.mpr
  apply Subtype.ext
  apply Subgroup.mem_bot.mp
  rw [← inertia_eq_bot L p P he]
  exact Ideal.coe_mem_inertia.mpr hσ

include p hp in
/-- Two stabilizing automorphisms with the same actual residue action coincide
at an unramified prime. -/
theorem eq_of_residue_eq (he : Ideal.ramificationIdx P ℤ = 1)
    (σ τ : Gal(L/ℚ))
    (hσ : σ ∈ MulAction.stabilizer Gal(L/ℚ) P)
    (hτ : τ ∈ MulAction.stabilizer Gal(L/ℚ) P)
    (hres : ∀ x : 𝓞 L, Ideal.Quotient.mk P (σ • x) = Ideal.Quotient.mk P (τ • x)) :
    σ = τ := by
  apply congrArg Subtype.val
    (stabilizerHom_injective L p P he (a₁ := ⟨σ, hσ⟩) (a₂ := ⟨τ, hτ⟩) ?_)
  apply AlgEquiv.ext
  intro z
  obtain ⟨x, rfl⟩ := Ideal.Quotient.mk_surjective z
  exact hres x

/-- Arithmetic Frobenius at a fixed unramified prime is unique as an actual
field automorphism, with the p-power residue convention. -/
theorem arithmeticFrobenius_unique (he : Ideal.ramificationIdx P ℤ = 1)
    (σ τ : Gal(L/ℚ))
    (hσ : σ ∈ MulAction.stabilizer Gal(L/ℚ) P)
    (hτ : τ ∈ MulAction.stabilizer Gal(L/ℚ) P)
    (hσp : ∀ x : 𝓞 L, Ideal.Quotient.mk P (σ • x) = (Ideal.Quotient.mk P x) ^ p)
    (hτp : ∀ x : 𝓞 L, Ideal.Quotient.mk P (τ • x) = (Ideal.Quotient.mk P x) ^ p) :
    σ = τ := by
  exact eq_of_residue_eq L p P he σ τ hσ hτ (fun x => (hσp x).trans (hτp x).symm)

/-- A fixed finite set of rational primes, computed from the nonzero field
discriminant, contains every prime that ramifies in this number field. -/
def discriminantPrimes : Finset ℕ := (NumberField.discr L).natAbs.primeFactors

omit [Normal ℚ L] in
/-- Outside the discriminant primes, the rational prime does not divide the
integer discriminant. -/
theorem not_dvd_discr_of_not_mem (h : p ∉ discriminantPrimes L) :
    ¬ (p : ℤ) ∣ NumberField.discr L := by
  intro hd
  exact h (Nat.mem_primeFactors.mpr ⟨hp.out, Int.natCast_dvd.mp hd,
    Int.natAbs_ne_zero.mpr (NumberField.discr_ne_zero L)⟩)

omit [Normal ℚ L] in
/-- Discriminant nondivisibility supplies actual local unramifiedness. -/
theorem isUnramifiedAt_of_not_dvd_discr (hd : ¬ (p : ℤ) ∣ NumberField.discr L) :
    Algebra.IsUnramifiedAt ℤ P := by
  exact (NumberField.not_dvd_discr_iff_forall_liesOver L (𝓞 L)
    (Int.prime_iff_natAbs_prime.mpr (by simpa using hp.out))).mp hd P inferInstance inferInstance

omit [Normal ℚ L] in
/-- Every prime above a rational prime outside this fixed finite set is
unramified in the commutative-algebra sense. -/
theorem isUnramifiedAt_of_not_mem (h : p ∉ discriminantPrimes L) :
    Algebra.IsUnramifiedAt ℤ P :=
  isUnramifiedAt_of_not_dvd_discr L p P (not_dvd_discr_of_not_mem L p h)

/-- The same explicit finite set controls the actual inertia subgroups. -/
theorem inertia_eq_bot_of_not_mem (h : p ∉ discriminantPrimes L) :
    P.inertia Gal(L/ℚ) = ⊥ := by
  let : Algebra.IsUnramifiedAt ℤ P := isUnramifiedAt_of_not_mem L p P h
  exact inertia_eq_bot_of_isUnramifiedAt L p P

/-- Outside the explicit discriminant set, arithmetic Frobenius at any chosen
prime above p is unique among actual stabilizing field automorphisms. -/
theorem arithmeticFrobenius_unique_of_not_mem (h : p ∉ discriminantPrimes L)
    (σ τ : Gal(L/ℚ))
    (hσ : σ ∈ MulAction.stabilizer Gal(L/ℚ) P)
    (hτ : τ ∈ MulAction.stabilizer Gal(L/ℚ) P)
    (hσp : ∀ x : 𝓞 L, Ideal.Quotient.mk P (σ • x) = (Ideal.Quotient.mk P x) ^ p)
    (hτp : ∀ x : 𝓞 L, Ideal.Quotient.mk P (τ • x) = (Ideal.Quotient.mk P x) ^ p) :
    σ = τ := by
  let : Algebra.IsUnramifiedAt ℤ P := isUnramifiedAt_of_not_mem L p P h
  exact arithmeticFrobenius_unique L p P (Ideal.ramificationIdx_eq_one P ℤ)
    σ τ hσ hτ hσp hτp

omit [Normal ℚ L] in
/-- Only finitely many rational primes admit a ramified prime above them. -/
theorem finite_ramified_primes :
    Set.Finite {q : ℕ | q.Prime ∧ ∃ Q : Ideal (𝓞 L), Q.IsMaximal ∧
      Q.LiesOver (Ideal.span {(q : ℤ)}) ∧ Ideal.ramificationIdx Q ℤ ≠ 1} := by
  apply (discriminantPrimes L).finite_toSet.subset
  intro q hq
  rcases hq with ⟨hq, Q, hQ, hQP, hram⟩
  let : Fact q.Prime := ⟨hq⟩
  let : Q.IsMaximal := hQ
  let : Q.LiesOver (Ideal.span {(q : ℤ)}) := hQP
  by_contra h
  let : Algebra.IsUnramifiedAt ℤ Q := isUnramifiedAt_of_not_mem L q Q h
  exact hram (Ideal.ramificationIdx_eq_one Q ℤ)

end PaperX.UnramifiedFrobeniusUniqueness
