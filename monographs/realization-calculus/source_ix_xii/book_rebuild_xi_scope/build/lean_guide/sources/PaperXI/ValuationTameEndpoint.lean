import PaperXI.ValuationConductor
import Mathlib.FieldTheory.Finite.Basic
import Mathlib.RingTheory.DiscreteValuationRing.Basic

/-! Actual valuation-ring specialization with a constructed geometric residue
Frobenius. The finite residue-base embedding remains declared. There is no
claimed identification with an absolute Weil group or extension-independent
arithmetic conductor. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ValuationTameEndpoint
open PaperXI.ResidueWeil PaperXI.ValuationConductor PaperXI.ValuationRamification

variable (k : Type*) [Field k] [Fintype k]
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L) [Algebra k (IsLocalRing.ResidueField A)]
  [Algebra.IsAlgebraic k (IsLocalRing.ResidueField A)]

/-- Inverse of the actual q-power residue automorphism, q = card k. -/
def geometricFrobenius : RingAut (IsLocalRing.ResidueField A) :=
  (FiniteField.frobeniusAlgEquivOfAlgebraic k (IsLocalRing.ResidueField A)).symm.toRingEquiv

/-- The convention is fixed by its q-power identity, not an arbitrary scalar label. -/
theorem geometric_power (x : IsLocalRing.ResidueField A) :
    (geometricFrobenius k A x) ^ Fintype.card k = x :=
  (FiniteField.frobeniusAlgEquivOfAlgebraic k (IsLocalRing.ResidueField A)).apply_symm_apply x

abbrev WeilPullback := valuationGroup K A (geometricFrobenius k A)

def inertiaIdentification :
    (degree (residueAction K A) (geometricFrobenius k A)).ker ≃* A.inertiaSubgroup K :=
  valuationInertiaEquiv K A (geometricFrobenius k A)

variable {V : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]

/-- Source-facing arithmetic-ring endpoint. All groups and weights come from A;
the hypothesis is trivial action of the first actual congruence subgroup. -/
theorem conductor [IsDiscreteValuationRing A] [Finite (A.decompositionSubgroup K)]
    (ρ : Representation ℂ (WeilPullback k K A) V) [Representation.IsIrreducible ρ]
    (ht : ∀ g : lower A (A.decompositionSubgroup K) 1,
      ρ (lift A (A.decompositionSubgroup K) (geometricFrobenius k A) 1 g) = 1)
    (hdim : 1 < Module.finrank ℂ V) :
    fixed A (A.decompositionSubgroup K) (geometricFrobenius k A) ρ 0 = ⊥ ∧
    swan A (A.decompositionSubgroup K) (geometricFrobenius k A) ρ = 0 ∧
    artin A (A.decompositionSubgroup K) (geometricFrobenius k A) ρ =
      (Module.finrank ℂ V : ℝ) ∧
    Summable (summand A (A.decompositionSubgroup K) (geometricFrobenius k A) ρ) := by
  obtain ⟨hf, hs, ha⟩ := tame_irreducible_dimension A (A.decompositionSubgroup K)
    (geometricFrobenius k A) ρ ht hdim
  exact ⟨hf, hs, ha, summable_summands A (A.decompositionSubgroup K) (geometricFrobenius k A) ρ⟩

end PaperXI.ValuationTameEndpoint
