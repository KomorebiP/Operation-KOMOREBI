import PaperX.FrobeniusChoiceIndependence
import PaperX.NumberFieldFrobeniusRestriction
import PaperX.UnramifiedFrobeniusUniqueness

/-! Outside the discriminant, absolute Frobenius choices have conjugate
restrictions to any fixed finite normal number field. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.NumberFieldWitnessIndependence
open PaperX.AbsoluteIntegralFrobenius PaperX.AbsoluteFrobeniusWitnesses
open PaperX.NumberFieldPrimeRestriction PaperX.NumberFieldFrobeniusRestriction
open PaperX.UnramifiedFrobeniusUniqueness
open scoped Pointwise

variable (L : Type*) [Field L] [NumberField L] [Normal ℚ L]

/-- The actual absolute inertia at p restricts trivially to a finite normal
number field whenever p is outside its discriminant primes. -/
theorem restriction_inertia_eq_one (p : ℕ) [Fact p.Prime] (v : Witness p)
    (hp : p ∉ discriminantPrimes L) (g : GQ) (hg : g ∈ v.primeIdeal.inertia GQ) :
    AbsoluteGaloisRestriction.restriction L g = 1 := by
  let : v.primeIdeal.IsMaximal := v.isMaximal
  let : v.primeIdeal.LiesOver (Ideal.span {(p : ℤ)}) := v.liesOver
  let : (restrictedPrime L v.primeIdeal).IsMaximal := restrictedPrime_isMaximal L p v.primeIdeal
  let : (restrictedPrime L v.primeIdeal).LiesOver (Ideal.span {(p : ℤ)}) :=
    restrictedPrime_liesOver L p v.primeIdeal
  have h := restriction_mem_inertia L v.primeIdeal g hg
  rw [inertia_eq_bot_of_not_mem L p (restrictedPrime L v.primeIdeal) hp] at h
  exact Subgroup.mem_bot.mp h

/-- All actual choices at p give one finite Frobenius conjugacy class outside
the discriminant. -/
theorem restricted_witnesses_conjugate (p : ℕ) [Fact p.Prime] (u v : Witness p)
    (hp : p ∉ discriminantPrimes L) :
    ∃ a : Gal(L/ℚ),
      a * AbsoluteGaloisRestriction.restriction L u.element * a⁻¹ =
        AbsoluteGaloisRestriction.restriction L v.element := by
  obtain ⟨a, _, ha⟩ := PaperX.FrobeniusChoiceIndependence.witnesses_conjugate_mod_inertia p u v
  let r : GQ →* Gal(L/ℚ) := AbsoluteGaloisRestriction.restriction L
  have h : r (v.element⁻¹ * (a * u.element * a⁻¹)) = 1 :=
    restriction_inertia_eq_one L p v hp _ ha
  rw [map_mul, map_inv] at h
  have hc : r (a * u.element * a⁻¹) = r v.element := (inv_mul_eq_one.mp h).symm
  exact ⟨r a, by simpa only [map_mul, map_inv] using hc⟩


/-- Every representation factoring through the finite number field is actually
trivial on the inertia attached to the chosen absolute prime away from its
discriminant. -/
theorem pullback_inertia_eq_one {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
    (ρ : Representation K Gal(L/ℚ) V) (p : ℕ) [Fact p.Prime] (v : Witness p)
    (hp : p ∉ discriminantPrimes L) (g : GQ) (hg : g ∈ v.primeIdeal.inertia GQ) :
    (ρ.comp (AbsoluteGaloisRestriction.restriction L)) g = 1 := by
  change ρ (AbsoluteGaloisRestriction.restriction L g) = 1
  rw [restriction_inertia_eq_one L p v hp g hg, map_one]

/-- The trace of a finite-field-factor representation is independent of the
actual arithmetic Frobenius choice outside the discriminant. -/
theorem pullback_witness_character_eq {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
    (ρ : Representation K Gal(L/ℚ) V) (p : ℕ) [Fact p.Prime] (u v : Witness p)
    (hp : p ∉ discriminantPrimes L) :
    Representation.character (ρ.comp (AbsoluteGaloisRestriction.restriction L)) u.element =
      Representation.character (ρ.comp (AbsoluteGaloisRestriction.restriction L)) v.element := by
  exact PaperX.FrobeniusChoiceIndependence.witness_character_eq _ p u v
    (pullback_inertia_eq_one L ρ p v hp)

end PaperX.NumberFieldWitnessIndependence
