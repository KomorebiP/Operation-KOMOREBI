import PaperX.CofiniteConjugacyCoverage
import PaperX.AbsoluteFrobeniusWitnesses
import PaperX.UnramifiedFrobeniusUniqueness
import PaperX.NumberFieldWitnessIndependence
import PaperX.RestrictionEmbeddingConjugacy
import Mathlib.FieldTheory.Galois.Infinite

/-! The quotient interface for the remaining arithmetic prime-coverage input.
Every open normal subgroup of the actual absolute Galois group is realized by
its fixed finite Galois number field. Coverage of samples in all those fields is
therefore enough for the existing separation machinery. The arithmetic coverage
itself is an explicit premise, not an axiom or a theorem of this module. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.GeneralArithmeticCoverage
open PaperX.AbsoluteIntegralFrobenius PaperX.CofiniteConjugacyCoverage

/-- The closed subgroup underlying an actual open normal subgroup of G_Q. -/
def closedSubgroup (H : OpenNormalSubgroup GQ) : ClosedSubgroup GQ :=
  ⟨H.toSubgroup, H.toOpenSubgroup.isClosed⟩

/-- An open normal subgroup has the same fixing subgroup as its fixed field. -/
theorem fixingSubgroup_fixedField (H : OpenNormalSubgroup GQ) :
    (IntermediateField.fixedField H.toSubgroup).fixingSubgroup = H.toSubgroup :=
  InfiniteGalois.fixingSubgroup_fixedField (closedSubgroup H)

/-- Openness proves that the actual fixed field is finite over Q. -/
theorem fixedField_finite (H : OpenNormalSubgroup GQ) :
    FiniteDimensional ℚ (IntermediateField.fixedField H.toSubgroup) := by
  apply (InfiniteGalois.isOpen_iff_finite _).mp
  rw [fixingSubgroup_fixedField H]
  exact H.toOpenSubgroup.isOpen

/-- Normality proves that the actual fixed field is Galois over Q. -/
theorem fixedField_isGalois (H : OpenNormalSubgroup GQ) :
    IsGalois ℚ (IntermediateField.fixedField H.toSubgroup) := by
  apply (InfiniteGalois.normal_iff_isGalois _).mp
  rw [fixingSubgroup_fixedField H]
  infer_instance

/-- The fixed field packaged as a finite Galois subfield of the chosen Qbar. -/
def fixedFiniteField (H : OpenNormalSubgroup GQ) :
    FiniteGaloisIntermediateField ℚ Qbar where
  __ := IntermediateField.fixedField H.toSubgroup
  finiteDimensional := fixedField_finite H
  isGalois := fixedField_isGalois H

/-- The fixed finite extension is an actual number field. -/
theorem fixedFiniteField_numberField (H : OpenNormalSubgroup GQ) :
    NumberField (fixedFiniteField H) := ⟨⟩

/-- The kernel of restriction to the actual fixed field is exactly the starting
open normal subgroup. No abstract finite quotient is substituted for the field. -/
theorem restriction_fixedFiniteField_ker (H : OpenNormalSubgroup GQ) :
    (AlgEquiv.restrictNormalHom (fixedFiniteField H)).ker = H.toSubgroup := by
  rw [IntermediateField.restrictNormalHom_ker]
  exact fixingSubgroup_fixedField H

/-- A purely algebraic coverage condition on the restrictions of a sample family.
When applied to Frobenius, the sample must carry its arithmetic witness separately. -/
def FiniteFieldCoverage {X : Type*} (s : X → GQ) : Prop :=
  ∀ (L : FiniteGaloisIntermediateField ℚ Qbar) (bad : Finset X) (σ : Gal(L/ℚ)),
    ∃ p : X, p ∉ bad ∧ IsConj (AlgEquiv.restrictNormalHom L (s p)) σ

/-- Coverage in every finite Galois subfield supplies conjugacy coverage in
every open normal quotient, with arbitrary finite exclusions preserved. -/
theorem cofiniteQuotientCoverage_of_finiteFieldCoverage
    {X : Type*} (s : X → GQ) (h : FiniteFieldCoverage s) :
    CofiniteQuotientCoverage s := by
  intro bad H g
  let L := fixedFiniteField H
  let r : GQ →* Gal(L/ℚ) := AlgEquiv.restrictNormalHom L
  obtain ⟨p, hp, hc⟩ := h L bad (r g)
  obtain ⟨c, hc⟩ := isConj_iff.mp hc
  obtain ⟨k, hk⟩ := AlgEquiv.restrictNormalHom_surjective Qbar c
  refine ⟨⟨p, hp⟩, k, ?_⟩
  change g⁻¹ * (k * s p * k⁻¹) ∈ H.toSubgroup
  rw [← restriction_fixedFiniteField_ker H]
  change r (g⁻¹ * (k * s p * k⁻¹)) = 1
  change r k = c at hk
  change c * r (s p) * c⁻¹ = r g at hc
  simp only [map_mul, map_inv, hk, hc, inv_mul_cancel]

/-- Conversely, open-normal quotient coverage gives conjugacy coverage in every
actual finite Galois subfield. Thus the field interface adds no stronger algebraic
or representation-theoretic premise. -/
theorem finiteFieldCoverage_of_cofiniteQuotientCoverage
    {X : Type*} (s : X → GQ) (h : CofiniteQuotientCoverage s) :
    FiniteFieldCoverage s := by
  intro L bad σ
  let r : GQ →* Gal(L/ℚ) := AlgEquiv.restrictNormalHom L
  have hr : IsOpen (r.ker : Set GQ) :=
    (isOpen_discrete ({1} : Set Gal(L/ℚ))).preimage
      (InfiniteGalois.restrictNormalHom_continuous L.toIntermediateField)
  let H : OpenNormalSubgroup GQ := ⟨⟨r.ker, hr⟩, inferInstance⟩
  obtain ⟨g, hg⟩ := AlgEquiv.restrictNormalHom_surjective Qbar σ
  obtain ⟨p, k, hk⟩ := h bad H g
  refine ⟨p.val, p.property, isConj_iff.mpr ⟨r k, ?_⟩⟩
  change r (g⁻¹ * (k * s p.val * k⁻¹)) = 1 at hk
  change r g = σ at hg
  simp only [map_mul, map_inv, hg] at hk
  exact (inv_mul_eq_one.mp hk).symm

/-- The exact algebraic equivalence between the finite-field arithmetic input
and the quotient interface used by the separator. -/
theorem finiteFieldCoverage_iff_cofiniteQuotientCoverage
    {X : Type*} (s : X → GQ) :
    FiniteFieldCoverage s ↔ CofiniteQuotientCoverage s :=
  ⟨cofiniteQuotientCoverage_of_finiteFieldCoverage s,
    finiteFieldCoverage_of_cofiniteQuotientCoverage s⟩

section ArithmeticWitnesses
open PaperX.AbsoluteFrobeniusWitnesses PaperX.UnramifiedFrobeniusUniqueness

local instance (L : FiniteGaloisIntermediateField ℚ Qbar) : NumberField L := ⟨⟩

/-- Finite-field coverage with the actual discriminant primes excluded. The
exclusion depends on the finite extension, as arithmetic unramifiedness does. -/
def UnramifiedFiniteFieldCoverage (s : RationalPrime → GQ) : Prop :=
  ∀ (L : FiniteGaloisIntermediateField ℚ Qbar) (bad : Finset RationalPrime)
    (σ : Gal(L/ℚ)), ∃ p : RationalPrime, p ∉ bad ∧
      p.val ∉ discriminantPrimes L ∧ IsConj (AlgEquiv.restrictNormalHom L (s p)) σ

/-- Arbitrary finite avoidance allows the actual discriminant primes to be
excluded separately for each finite extension. -/
theorem unramifiedFiniteFieldCoverage_of_finiteFieldCoverage
    (s : RationalPrime → GQ) (h : FiniteFieldCoverage s) :
    UnramifiedFiniteFieldCoverage s := by
  classical
  intro L bad σ
  obtain ⟨p, hp, hc⟩ := h L (bad ∪ (discriminantPrimes L).subtype Nat.Prime) σ
  refine ⟨p, (Finset.notMem_union.mp hp).1, ?_, hc⟩
  exact fun hmem => (Finset.notMem_union.mp hp).2 (Finset.mem_subtype.mpr hmem)

/-- The discriminant-avoiding arithmetic formulation is exactly equivalent to
the quotient-coverage condition already required by the separator. -/
theorem unramifiedFiniteFieldCoverage_iff_cofiniteQuotientCoverage
    (s : RationalPrime → GQ) :
    UnramifiedFiniteFieldCoverage s ↔ CofiniteQuotientCoverage s := by
  constructor
  · intro h
    apply cofiniteQuotientCoverage_of_finiteFieldCoverage s
    intro L bad σ
    obtain ⟨p, hp, _, hc⟩ := h L bad σ
    exact ⟨p, hp, hc⟩
  · intro h
    exact unramifiedFiniteFieldCoverage_of_finiteFieldCoverage s
      (finiteFieldCoverage_of_cofiniteQuotientCoverage s h)

/-- The remaining arithmetic input, expressed using actual absolute Frobenius
witnesses at rational primes and actual finite normal number fields. This is a
proposition to be proved, not an existence or coverage axiom. -/
def ArithmeticCoverage (w : (p : RationalPrime) → Witness p.val) : Prop :=
  UnramifiedFiniteFieldCoverage (fun p => (w p).element)

/-- Canonical restriction to a finite normal subfield gives the same Frobenius
conjugacy class for every actual absolute witness outside its discriminant. -/
theorem canonicalRestriction_witnesses_isConj
    (L : FiniteGaloisIntermediateField ℚ Qbar) (p : RationalPrime)
    (u v : Witness p.val) (hp : p.val ∉ discriminantPrimes L) :
    IsConj (AlgEquiv.restrictNormalHom L u.element)
      (AlgEquiv.restrictNormalHom L v.element) := by
  let : Fact p.val.Prime := ⟨p.property⟩
  have h : IsConj (AbsoluteGaloisRestriction.restriction L u.element)
      (AbsoluteGaloisRestriction.restriction L v.element) :=
    isConj_iff.mpr
      (NumberFieldWitnessIndependence.restricted_witnesses_conjugate L p.val u v hp)
  exact (RestrictionEmbeddingConjugacy.restriction_isConj L.toIntermediateField u.element).symm.trans
    (h.trans (RestrictionEmbeddingConjugacy.restriction_isConj L.toIntermediateField v.element))

/-- The arithmetic prime-coverage obligation without a preselected global
Frobenius family: each occurrence may supply its own actual absolute witness.
The prime must avoid both the given finite set and this field's discriminant. -/
def ExistentialArithmeticCoverage : Prop :=
  ∀ (L : FiniteGaloisIntermediateField ℚ Qbar) (bad : Finset RationalPrime)
    (σ : Gal(L/ℚ)), ∃ p : RationalPrime, p ∉ bad ∧
      p.val ∉ discriminantPrimes L ∧ ∃ u : Witness p.val,
        IsConj (AlgEquiv.restrictNormalHom L u.element) σ

/-- Actual prime coverage is independent of every global witness choice.
This uses derived unramifiedness and conjugacy, rather than assuming that the
chosen primes or Frobenius lifts agree. -/
theorem existentialArithmeticCoverage_iff_arithmeticCoverage
    (w : (p : RationalPrime) → Witness p.val) :
    ExistentialArithmeticCoverage ↔ ArithmeticCoverage w := by
  constructor
  · intro h L bad σ
    obtain ⟨p, hp, hdisc, u, hu⟩ := h L bad σ
    exact ⟨p, hp, hdisc,
      (canonicalRestriction_witnesses_isConj L p (w p) u hdisc).trans hu⟩
  · intro h L bad σ
    obtain ⟨p, hp, hdisc, hc⟩ := h L bad σ
    exact ⟨p, hp, hdisc, w p, hc⟩

/-- Once actual arithmetic coverage is supplied, the chosen witness family
satisfies precisely the general separator's quotient hypothesis. -/
theorem cofiniteQuotientCoverage_of_arithmeticCoverage
    (w : (p : RationalPrime) → Witness p.val) (h : ArithmeticCoverage w) :
    CofiniteQuotientCoverage (fun p => (w p).element) :=
  (unramifiedFiniteFieldCoverage_iff_cofiniteQuotientCoverage _).mp h

/-- The same conditional conclusion applies to the witness family whose
existence was derived from integral closure and residue Frobenius. -/
theorem chosenWitness_coverage (h : ArithmeticCoverage chosenWitness) :
    CofiniteQuotientCoverage (fun p => (chosenWitness p).element) :=
  cofiniteQuotientCoverage_of_arithmeticCoverage chosenWitness h

/-- The choice-free arithmetic obligation supplies cofinite quotient coverage
for every actual global Frobenius witness family. -/
theorem cofiniteQuotientCoverage_of_existentialArithmeticCoverage
    (h : ExistentialArithmeticCoverage) (w : (p : RationalPrime) → Witness p.val) :
    CofiniteQuotientCoverage (fun p => (w p).element) :=
  cofiniteQuotientCoverage_of_arithmeticCoverage w
    ((existentialArithmeticCoverage_iff_arithmeticCoverage w).mp h)

/-- Actual Frobenius samples with the arithmetic coverage input give the
conjugacy density needed on each pair of coefficient-prime good sets. -/
theorem arithmetic_dense_good_overlap
    (w : (p : RationalPrime) → Witness p.val) (h : ArithmeticCoverage w)
    (good₁ good₂ : RationalPrime → Prop)
    (h₁ : Set.Finite {p | ¬ good₁ p}) (h₂ : Set.Finite {p | ¬ good₂ p})
    (bad : Finset RationalPrime) :
    DenseRange (fun z : {p : RationalPrime // good₁ p ∧ good₂ p ∧ p ∉ bad} × GQ =>
      z.2 * (w z.1).element * z.2⁻¹) :=
  dense_good_overlap _ (cofiniteQuotientCoverage_of_arithmeticCoverage w h)
    good₁ good₂ h₁ h₂ bad

end ArithmeticWitnesses
end PaperX.GeneralArithmeticCoverage
