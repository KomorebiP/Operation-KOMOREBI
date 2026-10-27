import Mathlib.Topology.Algebra.Group.Quotient
import Mathlib.Topology.Instances.Int
import Mathlib.Tactic

/-! Compact fundamental domains from a finite period modulo a compact subgroup. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CompactQuotientPeriod69
open scoped Pointwise
variable {G : Type*} [Group G] [TopologicalSpace G] [IsTopologicalGroup G]
variable (J Z : Subgroup G) [Z.Normal] (t : G)

/-- An explicit finite union of translates of a compact subgroup covers the quotient.
No compactness of the ambient group is assumed. -/
theorem compact_quotient_of_period
    (hJ : IsCompact (J : Set G))
    (hcover : ∀ g : G, ∃ r : ℤ, ∃ j : J, g = t ^ r * (j : G))
    (m : ℕ) (hm : 0 < m)
    (hperiod : (QuotientGroup.mk' Z t) ^ m ∈ J.map (QuotientGroup.mk' Z)) :
    CompactSpace (G ⧸ Z) := by
  let q := QuotientGroup.mk' Z
  let U := J.map q
  let : CompactSpace J := isCompact_iff_compactSpace.mp hJ
  let F : Fin m × J → G ⧸ Z := fun p => q (t ^ (p.1 : ℕ) * (p.2 : G))
  have hF : Continuous F := by
    have hc : Continuous (fun i : Fin m => t ^ (i : ℕ)) := continuous_of_discreteTopology
    exact QuotientGroup.continuous_mk.comp
      ((hc.comp continuous_fst).mul (continuous_subtype_val.comp continuous_snd))
  have hsurj : Function.Surjective F := by
    intro x
    obtain ⟨g, rfl⟩ := QuotientGroup.mk'_surjective Z x
    obtain ⟨r, j, rfl⟩ := hcover g
    have hmz : (0 : ℤ) < m := Int.natCast_pos.mpr hm
    have hrem0 : 0 ≤ r % (m : ℤ) := Int.emod_nonneg r (ne_of_gt hmz)
    have hremm : r % (m : ℤ) < m := Int.emod_lt_of_pos r hmz
    let i : Fin m := ⟨(r % (m : ℤ)).toNat, by omega⟩
    have hi : (i : ℕ) = (r % (m : ℤ)).toNat := rfl
    have hice : ((i : ℕ) : ℤ) = r % (m : ℤ) := Int.toNat_of_nonneg hrem0
    have hp : q t ^ ((m : ℤ) * (r / (m : ℤ))) ∈ U := by
      have h := U.zpow_mem hperiod (r / (m : ℤ))
      simpa only [zpow_mul, zpow_natCast] using h
    have hprod : q t ^ ((m : ℤ) * (r / (m : ℤ))) * q (j : G) ∈ U :=
      U.mul_mem hp (Subgroup.mem_map.mpr ⟨j, j.property, rfl⟩)
    obtain ⟨j', hj', hj'e⟩ := Subgroup.mem_map.mp hprod
    refine ⟨(i, ⟨j', hj'⟩), ?_⟩
    change q (t ^ (i : ℕ) * j') = q (t ^ r * (j : G))
    rw [map_mul, map_pow, hj'e, map_mul, map_zpow]
    rw [← mul_assoc, ← zpow_natCast (q t) (i : ℕ), ← zpow_add]
    rw [hice, Int.emod_add_mul_ediv]
  exact hsurj.compactSpace hF

end PaperXI.CompactQuotientPeriod69
