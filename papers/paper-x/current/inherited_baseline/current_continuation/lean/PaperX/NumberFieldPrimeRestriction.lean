import PaperX.AbsoluteIntegralFrobenius

/-! Restriction of actual primes of the algebraic integers in Qbar to the ring
of integers of an arbitrary normal number field. All maps use the same chosen
field embedding as absolute Galois restriction. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.NumberFieldPrimeRestriction
open scoped Pointwise
open AbsoluteIntegralFrobenius
open NumberField

variable (L : Type*) [Field L] [NumberField L] [Normal ℚ L]

/-- The chosen field embedding restricted to the actual rings of integers. -/
def integralEmbedding : 𝓞 L →+* IntegralClosure :=
  RingOfIntegers.mapRingHom (AbsoluteGaloisRestriction.embedding L).toRingHom

theorem integralEmbedding_apply (x : 𝓞 L) :
    (integralEmbedding L x : Qbar) = AbsoluteGaloisRestriction.embedding L (x : L) := rfl

theorem integralEmbedding_injective : Function.Injective (integralEmbedding L) := by
  intro x y h
  apply Subtype.ext
  apply (AbsoluteGaloisRestriction.embedding L).injective
  exact congrArg (fun z : IntegralClosure => (z : Qbar)) h

/-- The integral embedding intertwines the actual absolute and restricted actions. -/
theorem integralEmbedding_smul (σ : GQ) (x : 𝓞 L) :
    integralEmbedding L (AbsoluteGaloisRestriction.restriction L σ • x) =
      σ • integralEmbedding L x := by
  apply Subtype.ext
  exact AbsoluteGaloisRestriction.restriction_commutes L σ (x : L)

/-- Contraction of an actual algebraic-integer prime to the chosen number field. -/
def restrictedPrime (Q : Ideal IntegralClosure) : Ideal (𝓞 L) :=
  Q.comap (integralEmbedding L)

theorem mem_restrictedPrime (Q : Ideal IntegralClosure) (x : 𝓞 L) :
    x ∈ restrictedPrime L Q ↔ integralEmbedding L x ∈ Q := Iff.rfl

theorem restrictedPrime_isPrime (Q : Ideal IntegralClosure) [Q.IsPrime] :
    (restrictedPrime L Q).IsPrime := Q.comap_isPrime (integralEmbedding L)

/-- The actual residue map induced by the integral embedding. -/
def quotientEmbedding (Q : Ideal IntegralClosure) :
    (𝓞 L ⧸ restrictedPrime L Q) →+* (IntegralClosure ⧸ Q) :=
  Ideal.quotientMap Q (integralEmbedding L) le_rfl

theorem quotientEmbedding_mk (Q : Ideal IntegralClosure) (x : 𝓞 L) :
    quotientEmbedding L Q (Ideal.Quotient.mk (restrictedPrime L Q) x) =
      Ideal.Quotient.mk Q (integralEmbedding L x) := rfl

theorem quotientEmbedding_injective (Q : Ideal IntegralClosure) :
    Function.Injective (quotientEmbedding L Q) := Ideal.quotientMap_injective

variable (p : ℕ) [hp : Fact p.Prime]
  (Q : Ideal IntegralClosure) [hQover : Q.LiesOver (Ideal.span {(p : ℤ)})]

omit hp in
/-- Contraction preserves the specified rational prime below the ideal. -/
theorem restrictedPrime_liesOver :
    (restrictedPrime L Q).LiesOver (Ideal.span {(p : ℤ)}) := by
  constructor
  rw [Ideal.over_def Q (Ideal.span {(p : ℤ)})]
  ext z
  change algebraMap ℤ IntegralClosure z ∈ Q ↔
    integralEmbedding L (algebraMap ℤ (𝓞 L) z) ∈ Q
  simp only [map_intCast, eq_intCast]

omit hp in
theorem prime_mem_restrictedPrime : (p : 𝓞 L) ∈ restrictedPrime L Q := by
  let : (restrictedPrime L Q).LiesOver (Ideal.span {(p : ℤ)}) :=
    restrictedPrime_liesOver L p Q
  simpa only [map_natCast] using
    (Ideal.mem_of_liesOver (restrictedPrime L Q) (Ideal.span {(p : ℤ)}) (p : ℤ)).mp
    (Ideal.subset_span (Set.mem_singleton _))

include hp hQover in
/-- A contracted prime above p is nonzero. -/
theorem restrictedPrime_ne_bot : restrictedPrime L Q ≠ ⊥ := by
  intro h
  have hz : (p : 𝓞 L) = 0 := by
    simpa only [h, Ideal.mem_bot] using prime_mem_restrictedPrime L p Q
  exact hp.out.ne_zero ((Nat.cast_eq_zero.mp hz))

include hp hQover in
/-- Nonzero prime ideals of a number-field ring of integers are maximal. -/
theorem restrictedPrime_isMaximal [Q.IsPrime] : (restrictedPrime L Q).IsMaximal :=
  (restrictedPrime_isPrime L Q).isMaximal (restrictedPrime_ne_bot L p Q)

end PaperX.NumberFieldPrimeRestriction
