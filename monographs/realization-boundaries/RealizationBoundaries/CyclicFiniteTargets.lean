import RealizationBoundaries.CyclicQuotients
import RealizationBoundaries.FiniteTargets
import Mathlib.GroupTheory.SpecificGroups.Cyclic
import Mathlib.Data.Nat.Squarefree

/-! # Exact classification of finite quotient targets

Every finite quotient, not only the displayed canonical quotients, is cyclic of
squarefree order. Conversely every finite cyclic squarefree target occurs. A
surjective map's kernel is the actual multiple subgroup indexed by target order.
-/
set_option autoImplicit false
noncomputable section
open scoped BigOperators
namespace RealizationBoundaries

theorem primeRadical_squarefree (m : ℕ) : Squarefree (primeRadical m) := by
  apply Finset.squarefree_prod_of_pairwise_isCoprime
  · intro p hp q hq hpq
    exact Nat.coprime_iff_isRelPrime.mp
      ((Nat.coprime_primes (Nat.prime_of_mem_primeFactors hp)
        (Nat.prime_of_mem_primeFactors hq)).mpr hpq)
  · intro p hp
    exact (Nat.prime_of_mem_primeFactors hp).prime.squarefree

theorem primeRadical_eq_of_squarefree {m : ℕ} (hm : Squarefree m) : primeRadical m = m :=
  Nat.prod_primeFactors_of_squarefree hm

variable (W : Submodule ℚ TailSpace) (F : Type*) [AddGroup F] [Finite F]

/-- A factor through the actual cyclic radical quotient for every finite-target map. -/
def finiteTargetCyclicFactor (f : preimage W →+ F) : ZMod (primeRadical (Nat.card F)) →+ F :=
  (finiteTargetFactor W F f).comp (divisorCrtEquiv Nat.card_pos).toAddMonoidHom

@[simp] theorem finiteTargetCyclicFactor_quotient (f : preimage W →+ F) (x : preimage W) :
    finiteTargetCyclicFactor W F f
      (cyclicIntegerQuotientEquiv W Nat.card_pos (QuotientAddGroup.mk x)) = f x := by
  change finiteTargetFactor W F f
    (divisorCrtEquiv Nat.card_pos
      (cyclicIntegerQuotientEquiv W Nat.card_pos (QuotientAddGroup.mk x))) = _
  rw [cyclicIntegerQuotientEquiv_mk, finiteTargetFactor_coordinate]

theorem finiteTargetCyclicFactor_surjective (f : preimage W →+ F)
    (hf : Function.Surjective f) : Function.Surjective (finiteTargetCyclicFactor W F f) := by
  intro z
  obtain ⟨x, rfl⟩ := hf z
  exact ⟨cyclicIntegerQuotientEquiv W Nat.card_pos (QuotientAddGroup.mk x),
    finiteTargetCyclicFactor_quotient W F f x⟩

/-- A finite quotient has no repeated prime in its order. -/
theorem finite_quotient_radical_card (f : preimage W →+ F) (hf : Function.Surjective f) :
    primeRadical (Nat.card F) = Nat.card F := by
  have hpos := primeRadical_pos (Nat.card F)
  let : NeZero (primeRadical (Nat.card F)) := ⟨Nat.ne_of_gt hpos⟩
  apply Nat.le_antisymm (Nat.le_of_dvd Nat.card_pos (primeRadical_dvd _))
  have h := Nat.card_le_card_of_surjective (finiteTargetCyclicFactor W F f)
    (finiteTargetCyclicFactor_surjective W F f hf)
  simpa only [Nat.card_eq_fintype_card, ZMod.card] using h

theorem finite_quotient_squarefree (f : preimage W →+ F) (hf : Function.Surjective f) :
    Squarefree (Nat.card F) := by
  rw [← finite_quotient_radical_card W F f hf]
  exact primeRadical_squarefree _

/-- Cyclicity is derived for the target, even if it was supplied as an arbitrary finite group. -/
theorem finite_quotient_cyclic (f : preimage W →+ F) (hf : Function.Surjective f) :
    IsAddCyclic F :=
  isAddCyclic_of_surjective (finiteTargetCyclicFactor W F f)
    (finiteTargetCyclicFactor_surjective W F f hf)

/-- With a surjective original map, the full divisor-coordinate factor is bijective. -/
theorem finiteTargetFactor_bijective (f : preimage W →+ F) (hf : Function.Surjective f) :
    Function.Bijective (finiteTargetFactor W F f) := by
  let : Finite (DivisorCoordinates (Nat.card F)) := divisorCoordinates_finite Nat.card_pos
  apply (Nat.bijective_iff_surjective_and_card _).mpr
  constructor
  · intro z
    obtain ⟨x, rfl⟩ := hf z
    exact ⟨coordinateMap W (Nat.card F) x, finiteTargetFactor_coordinate W F f x⟩
  · rw [divisorCoordinates_card Nat.card_pos, finite_quotient_radical_card W F f hf]

/-- Target order determines the literal kernel of a finite surjection. -/
theorem finite_surjection_ker (f : preimage W →+ F) (hf : Function.Surjective f) :
    f.ker = multiples W (Nat.card F) := by
  rw [← coordinateMap_ker W Nat.card_pos]
  ext x
  change f x = 0 ↔ coordinateMap W (Nat.card F) x = 0
  rw [← finiteTargetFactor_coordinate W F f x, ← (finiteTargetFactor W F f).map_zero]
  exact (finiteTargetFactor_bijective W F f hf).injective.eq_iff

/-- Construct a surjection onto any finite cyclic squarefree group. -/
def squarefreeCyclicQuotient (hc : IsAddCyclic F) (hs : Squarefree (Nat.card F)) :
    preimage W →+ F :=
  ((cyclicIntegerQuotientEquiv W Nat.card_pos).trans
    ((ZMod.ringEquivCongr (primeRadical_eq_of_squarefree hs)).toAddEquiv.trans
      (zmodAddCyclicAddEquiv hc))).toAddMonoidHom.comp
    (QuotientAddGroup.mk' (multiples W (Nat.card F)))

theorem squarefreeCyclicQuotient_surjective (hc : IsAddCyclic F)
    (hs : Squarefree (Nat.card F)) : Function.Surjective (squarefreeCyclicQuotient W F hc hs) := by
  exact (((cyclicIntegerQuotientEquiv W Nat.card_pos).trans
    ((ZMod.ringEquivCongr (primeRadical_eq_of_squarefree hs)).toAddEquiv.trans
      (zmodAddCyclicAddEquiv hc))).surjective).comp (QuotientAddGroup.mk'_surjective _)

/-- The full finite-target classification, with an actual surjection in the converse. -/
theorem finite_quotient_exists_iff :
    (∃ f : preimage W →+ F, Function.Surjective f) ↔
      IsAddCyclic F ∧ Squarefree (Nat.card F) := by
  constructor
  · rintro ⟨f, hf⟩
    exact ⟨finite_quotient_cyclic W F f hf, finite_quotient_squarefree W F f hf⟩
  · rintro ⟨hc, hs⟩
    exact ⟨squarefreeCyclicQuotient W F hc hs, squarefreeCyclicQuotient_surjective W F hc hs⟩

end RealizationBoundaries
