import PaperX.FrobeniusChoiceIndependence
import PaperX.NumberFieldFrobeniusRestriction
import PaperX.UnramifiedFrobeniusUniqueness

/-! Compiler controls connecting actual prime witnesses to unramified finite
restrictions and representation traces. No arithmetic coverage is assumed. -/
set_option autoImplicit false
noncomputable section
open NumberField
open PaperX.AbsoluteIntegralFrobenius PaperX.AbsoluteFrobeniusWitnesses
open PaperX.NumberFieldPrimeRestriction PaperX.NumberFieldFrobeniusRestriction
open PaperX.UnramifiedFrobeniusUniqueness PaperX.FrobeniusChoiceIndependence
open scoped Pointwise

example : Nonempty (Witness 2) := by
  let : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩
  exact witness_nonempty 2

example (L : Type*) [Field L] [NumberField L] [Normal ℚ L]
    (p : ℕ) [Fact p.Prime] (P : Ideal (𝓞 L))
    [P.IsMaximal] [P.LiesOver (Ideal.span {(p : ℤ)})]
    (hp : p ∉ discriminantPrimes L) (σ τ : Gal(L/ℚ))
    (hσ : σ ∈ MulAction.stabilizer Gal(L/ℚ) P)
    (hτ : τ ∈ MulAction.stabilizer Gal(L/ℚ) P)
    (hσp : ∀ x : 𝓞 L, Ideal.Quotient.mk P (σ • x) = (Ideal.Quotient.mk P x) ^ p)
    (hτp : ∀ x : 𝓞 L, Ideal.Quotient.mk P (τ • x) = (Ideal.Quotient.mk P x) ^ p) :
    σ = τ :=
  arithmeticFrobenius_unique_of_not_mem L p P hp σ τ hσ hτ hσp hτp

example (L : Type*) [Field L] [NumberField L] [Normal ℚ L]
    {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
    (ρ : Representation K Gal(L/ℚ) V)
    (p : ℕ) [Fact p.Prime] (u v : Witness p)
    (hp : p ∉ discriminantPrimes L) :
    Representation.character (ρ.comp (PaperX.AbsoluteGaloisRestriction.restriction L))
      u.element =
    Representation.character (ρ.comp (PaperX.AbsoluteGaloisRestriction.restriction L))
      v.element := by
  let : v.primeIdeal.IsMaximal := v.isMaximal
  let : v.primeIdeal.LiesOver (Ideal.span {(p : ℤ)}) := v.liesOver
  let : (restrictedPrime L v.primeIdeal).IsMaximal :=
    restrictedPrime_isMaximal L p v.primeIdeal
  let : (restrictedPrime L v.primeIdeal).LiesOver (Ideal.span {(p : ℤ)}) :=
    restrictedPrime_liesOver L p v.primeIdeal
  apply witness_character_eq _ p u v
  intro g hg
  have hmem := restriction_mem_inertia L v.primeIdeal g hg
  rw [inertia_eq_bot_of_not_mem L p (restrictedPrime L v.primeIdeal) hp] at hmem
  have heq := Subgroup.mem_bot.mp hmem
  change ρ (PaperX.AbsoluteGaloisRestriction.restriction L g) = 1
  rw [heq, map_one]
