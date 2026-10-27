import PaperXI.CentralExtensionInducing
import Mathlib.Topology.Instances.Int
import Mathlib.GroupTheory.OrderOfElement

/-!
# Compact subgroups have zero integer degree

A continuous integer degree has finite image on a compact subgroup, because
the target has its usual discrete topology.  The image is a finite subgroup of
the torsion-free group `Multiplicative ℤ`, so it is trivial.  This supplies the
separation hypothesis for adjoining any element of nonzero degree.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CompactDegreeSeparation

variable {G : Type*} [Group G] [TopologicalSpace G]

/-- Compactness and continuity force a compact subgroup into the integer-degree kernel. -/
theorem compact_le_degree_ker (J : Subgroup G) (δ : G →* Multiplicative ℤ)
    (hδ : Continuous δ) (hJ : IsCompact (J : Set G)) : J ≤ δ.ker := by
  have hfinite : (J.map δ : Set (Multiplicative ℤ)).Finite := by
    rw [Subgroup.coe_map]
    exact (hJ.image hδ).finite_of_discrete
  let : Finite (J.map δ) := hfinite.to_subtype
  intro j hj
  let x : J.map δ := ⟨δ j, ⟨j, hj, rfl⟩⟩
  have hx : x = 1 := (isOfFinOrder_of_finite x).eq_one'
  exact congrArg Subtype.val hx

/-- A nonzero integer degree prevents a nonzero power from meeting a compact subgroup. -/
theorem hfree_from_compact_degree (J : Subgroup G) (δ : G →* Multiplicative ℤ)
    (hδ : Continuous δ) (hJ : IsCompact (J : Set G))
    (z : G) (hz : δ z ≠ 1) : ∀ n : ℤ, z ^ n ∈ J → n = 0 :=
  CentralExtensionInducing.hfree_from_degree J δ (compact_le_degree_ker J δ hδ hJ) z hz

end PaperXI.CompactDegreeSeparation
