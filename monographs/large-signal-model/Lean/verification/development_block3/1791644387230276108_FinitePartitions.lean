import KomorebiLSM.FiniteBayes
import Mathlib.Data.Setoid.Partition
import Mathlib.Data.Fintype.Card

/-! Finite partitions with block aggregation and strict-refinement cardinality. -/
set_option autoImplicit false
namespace Komorebi.LSM.FinitePartitions
open scoped BigOperators
open FiniteBayes
universe u
variable {I : Type u} [Fintype I]

noncomputable instance quotientEnumeration (r : Setoid I) : Fintype (Quotient r) :=
  Fintype.ofFinite _

noncomputable def blockCount (r : Setoid I) : ℕ := Fintype.card (Quotient r)

def coarsenMap {r s : Setoid I} (h : r ≤ s) : Quotient r → Quotient s :=
  Quotient.map' id (fun _ _ hxy => h hxy)

@[simp] theorem coarsenMap_mk {r s : Setoid I} (h : r ≤ s) (i : I) :
    coarsenMap h (Quotient.mk r i) = Quotient.mk s i := rfl

theorem coarsenMap_surjective {r s : Setoid I} (h : r ≤ s) :
    Function.Surjective (coarsenMap h) := by
  intro q
  induction q using Quotient.inductionOn with
  | h i => exact ⟨Quotient.mk r i, rfl⟩

theorem blockCount_le (r : Setoid I) : blockCount r ≤ Fintype.card I :=
  Fintype.card_le_of_surjective (Quotient.mk r) Quotient.mk_surjective

theorem blockCount_refines {r s : Setoid I} (h : r ≤ s) : blockCount s ≤ blockCount r :=
  Fintype.card_le_of_surjective (coarsenMap h) (coarsenMap_surjective h)

theorem equal_of_refines_card {r s : Setoid I} (h : r ≤ s)
    (hc : blockCount r = blockCount s) : r = s := by
  have hinj : Function.Injective (coarsenMap h) :=
    ((Fintype.bijective_iff_surjective_and_card (coarsenMap h)).mpr
      ⟨coarsenMap_surjective h, hc⟩).1
  apply le_antisymm h
  intro i j hij
  exact Quotient.exact (hinj (show coarsenMap h (Quotient.mk r i) =
    coarsenMap h (Quotient.mk r j) from Quotient.sound hij))

theorem strict_refinement_count {r s : Setoid I} (h : r ≤ s) (hne : r ≠ s) :
    blockCount s < blockCount r := by
  have hle := blockCount_refines h
  have hneq : blockCount r ≠ blockCount s := fun hc => hne (equal_of_refines_card h hc)
  omega

noncomputable def blockAggregate (r : Setoid I) (p : I → ℝ) : Quotient r → ℝ := by
  classical
  exact aggregate (Quotient.mk r) p

@[simp] theorem blockAggregate_mk (r : Setoid I) (p : I → ℝ) (j : I) :
    blockAggregate r p (Quotient.mk r j) = ∑ i, if r i j then p i else 0 := by
  classical
  simp only [blockAggregate, aggregate, Quotient.eq_iff_equiv]

theorem blockAggregate_comp {r s : Setoid I} (h : r ≤ s) (p : I → ℝ) :
    blockAggregate s p = by classical exact aggregate (coarsenMap h) (blockAggregate r p) := by
  classical
  simp only [blockAggregate, aggregate_comp]
  rfl

theorem same_fine_implies_same_coarse {r s : Setoid I} (h : r ≤ s) (p q : I → ℝ)
    (he : blockAggregate r p = blockAggregate r q) :
    blockAggregate s p = blockAggregate s q := by
  classical
  rw [blockAggregate_comp h p, blockAggregate_comp h q, he]

end Komorebi.LSM.FinitePartitions
