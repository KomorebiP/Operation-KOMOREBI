import PaperX.AbsoluteGaloisRestriction
import PaperX.CyclotomicFrobeniusPrimes
import Mathlib.RepresentationTheory.Character

/-! Global lifts of the finite cyclotomic arithmetic samples. The lifts are
actual absolute-Galois elements, but no membership in an absolute decomposition
group is asserted. Representations factoring through the finite field take
the same value on every lift. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CyclotomicAbsoluteSamples
open PaperX.AbsoluteGaloisRestriction PaperX.CyclotomicPrimeCoverage
open NumberField
open scoped Pointwise

variable (n : ℕ) [NeZero n] (L : Type*) [Field L] [NumberField L]
  [IsCyclotomicExtension {n} ℚ L]

/-- The restriction map with normality derived from the cyclotomic hypothesis. -/
def restrictionMap : Field.absoluteGaloisGroup ℚ →* Gal(L/ℚ) := by
  let : IsGalois ℚ L := IsCyclotomicExtension.isGalois {n} ℚ L
  exact restriction L

/-- The chosen field embedding used by the actual restriction. -/
def fieldEmbedding : L →ₐ[ℚ] AlgebraicClosure ℚ := by
  let : IsGalois ℚ L := IsCyclotomicExtension.isGalois {n} ℚ L
  exact embedding L

omit [NeZero n] in
theorem restrictionMap_surjective : Function.Surjective (restrictionMap n L) := by
  let : IsGalois ℚ L := IsCyclotomicExtension.isGalois {n} ℚ L
  exact restriction_surjective L

omit [NeZero n] in
theorem restrictionMap_continuous : Continuous (restrictionMap n L) := by
  let : IsGalois ℚ L := IsCyclotomicExtension.isGalois {n} ℚ L
  exact restriction_continuous L

omit [NeZero n] in
theorem restrictionMap_commutes (γ : Field.absoluteGaloisGroup ℚ) (x : L) :
    fieldEmbedding n L (restrictionMap n L γ x) =
      (show Gal(AlgebraicClosure ℚ/ℚ) from γ) (fieldEmbedding n L x) := by
  let : IsGalois ℚ L := IsCyclotomicExtension.isGalois {n} ℚ L
  exact restriction_commutes L γ x

/-- A chosen global lift, with no assertion that this choice belongs to a
specified absolute decomposition subgroup. -/
def liftSample (p : PermittedPrime n ∅) : Field.absoluteGaloisGroup ℚ :=
  (restrictionMap_surjective n L (primeSample n L ∅ p)).choose

@[simp] theorem restriction_liftSample (p : PermittedPrime n ∅) :
    restrictionMap n L (liftSample n L p) = primeSample n L ∅ p :=
  (restrictionMap_surjective n L (primeSample n L ∅ p)).choose_spec

/-- The chosen global element acts by the arithmetic power on every embedded
n-th root of unity in the finite field. -/
theorem liftSample_apply_root (p : PermittedPrime n ∅) (x : L) (hx : x ^ n = 1) :
    (show Gal(AlgebraicClosure ℚ/ℚ) from liftSample n L p) (fieldEmbedding n L x) = (fieldEmbedding n L x) ^ p.val := by
  rw [← restrictionMap_commutes n L, restriction_liftSample,
    primeSample, primePowerAutomorphism_apply n L p.val p.property.2.1 hx, map_pow]

/-- Every lift restricts to the proved arithmetic Frobenius at an actual
unramified prime ideal of the finite cyclotomic field. This conclusion is about
that finite field, and does not assert absolute decomposition membership. -/
theorem lift_restriction_has_prime_witness (p : PermittedPrime n ∅)
    (γ : Field.absoluteGaloisGroup ℚ) (hγ : restrictionMap n L γ = primeSample n L ∅ p) :
    ∃ P : Ideal (𝓞 L), P.IsMaximal ∧ P.LiesOver (Ideal.span {(p.val : ℤ)}) ∧
      Ideal.ramificationIdx P ℤ = 1 ∧
      restrictionMap n L γ ∈ MulAction.stabilizer Gal(L/ℚ) P ∧
      ∀ x : 𝓞 L, Ideal.Quotient.mk P (restrictionMap n L γ • x) =
        (Ideal.Quotient.mk P x) ^ p.val := by
  rw [hγ]
  exact PaperX.CyclotomicFrobeniusPrimes.permitted_prime_has_frobenius_witness n L ∅ p

section Representations
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable (ρ : Representation K Gal(L/ℚ) V)

/-- The entire linear action, rather than only its trace, is independent of
the chosen global lift once the representation factors through the field. -/
theorem pullback_on_lift (p : PermittedPrime n ∅) (γ : Field.absoluteGaloisGroup ℚ)
    (hγ : restrictionMap n L γ = primeSample n L ∅ p) :
    (ρ.comp (restrictionMap n L)) γ = ρ (primeSample n L ∅ p) := by
  change ρ (restrictionMap n L γ) = _
  rw [hγ]

theorem pullback_character_on_lift (p : PermittedPrime n ∅)
    (γ : Field.absoluteGaloisGroup ℚ) (hγ : restrictionMap n L γ = primeSample n L ∅ p) :
    Representation.character (ρ.comp (restrictionMap n L)) γ = ρ.character (primeSample n L ∅ p) := by
  change LinearMap.trace K V ((ρ.comp (restrictionMap n L)) γ) = _
  rw [pullback_on_lift n L ρ p γ hγ]
  rfl

end Representations
end PaperX.CyclotomicAbsoluteSamples
