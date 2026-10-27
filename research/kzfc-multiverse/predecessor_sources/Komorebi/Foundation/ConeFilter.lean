import Komorebi.Foundation.FilterExtension

/-!
# The fine cone filter and the compactness equivalences

Regularity enters exactly when fewer than kappa small supports are united. The
filter is explicitly built on P_kappa(I) and proved proper and kappa-complete.
-/

universe u

namespace Komorebi.CompactnessClassification

open Set Filter
open FineUltrafilterCompactness

/-- The upper cone of one genuinely small subset of the index set. -/
def cone {κ : Cardinal.{u}} {I : Type u} (s : SmallPieces κ I) :
    Set (SmallPieces κ I) := {J | s.val ⊆ J.val}

/-- A set is cone-large precisely when it contains the upper cone of some small set. -/
def coneFilter (κ : Cardinal.{u}) (hκ : Cardinal.aleph0 ≤ κ) (I : Type u) :
    Filter (SmallPieces κ I) where
  sets := {D | ∃ s : SmallPieces κ I, cone s ⊆ D}
  univ_sets := ⟨⟨∅, by simpa using Cardinal.aleph0_pos.trans_le hκ⟩,
    Set.subset_univ _⟩
  sets_of_superset := by
    rintro D E ⟨s, hs⟩ hDE
    exact ⟨s, hs.trans hDE⟩
  inter_sets := by
    rintro D E ⟨s, hs⟩ ⟨t, ht⟩
    have hst : Cardinal.mk (s.val ∪ t.val : Set I) < κ :=
      (Cardinal.mk_union_le _ _).trans_lt
        (Cardinal.add_lt_of_lt hκ s.property t.property)
    refine ⟨⟨s.val ∪ t.val, hst⟩, ?_⟩
    intro J hJ
    exact ⟨hs (fun i hi => hJ (Or.inl hi)), ht (fun i hi => hJ (Or.inr hi))⟩

/-- Every generating cone contains its own generating support. -/
theorem coneFilter_neBot (κ : Cardinal.{u}) (hκ : Cardinal.aleph0 ≤ κ) (I : Type u) :
    (coneFilter κ hκ I).NeBot := by
  refine ⟨?_⟩
  intro heq
  have hm : (∅ : Set (SmallPieces κ I)) ∈ coneFilter κ hκ I := by
    rw [heq]
    exact Filter.mem_bot
  obtain ⟨s, hs⟩ := hm
  exact hs (show s ∈ cone s from Set.Subset.refl _)

/-- Regularity gives closure of the cone filter under fewer than kappa intersections. -/
theorem coneFilter_complete (κ : Cardinal.{u}) (hκ : κ.IsRegular) (I : Type u) :
    CardinalInterFilter (coneFilter κ hκ.aleph0_le I) κ := by
  classical
  refine ⟨?_⟩
  intro D hD hmem
  have hw : ∀ d : D, ∃ s : SmallPieces κ I, cone s ⊆ d.val :=
    fun d => hmem d.val d.property
  choose s hs using hw
  have hsmall : Cardinal.mk (⋃ d : D, (s d).val) < κ :=
    (Cardinal.card_iUnion_lt_iff_forall_of_isRegular hκ hD).mpr
      (fun d => (s d).property)
  refine ⟨⟨⋃ d : D, (s d).val, hsmall⟩, ?_⟩
  intro J hJ
  apply Set.mem_sInter.mpr
  intro d hd
  apply hs ⟨d, hd⟩
  intro i hi
  exact hJ (Set.mem_iUnion.mpr ⟨⟨d, hd⟩, hi⟩)

/-- Every coordinate belongs to a cone-large collection of small supports. -/
theorem singleton_mem_coneFilter (κ : Cardinal.{u}) (hκ : Cardinal.aleph0 ≤ κ)
    (I : Type u) (i : I) :
    {J : SmallPieces κ I | i ∈ J.val} ∈ coneFilter κ hκ I := by
  refine ⟨⟨{i}, (Set.finite_singleton i).lt_aleph0.trans_le hκ⟩, ?_⟩
  intro J hJ
  exact hJ (by simp)

/-- Complete filter extension constructs the exact fine ultrafilter needed by the
forward compactness theorem. -/
theorem fine_of_extension (κ : Cardinal.{u}) (hκ : κ.IsRegular)
    (hext : CompleteFilterExtension κ) : FineUltrafilterPrinciple κ := by
  intro I
  obtain ⟨U, hUF, hcomplete⟩ := hext (SmallPieces κ I)
    (coneFilter κ hκ.aleph0_le I) (coneFilter_neBot κ hκ.aleph0_le I)
    (coneFilter_complete κ hκ I)
  refine ⟨U, hcomplete, ?_⟩
  intro i
  exact hUF (singleton_mem_coneFilter κ hκ.aleph0_le I i)

/-- Classification of fixed-domain constraint compactness by an independently
stated complete-filter extension property, for every regular infinite cardinal. -/
theorem fixedDomain_iff_extension (κ : Cardinal.{u}) (hκ : κ.IsRegular) :
    FixedDomainCompactness κ ↔ CompleteFilterExtension κ := by
  constructor
  · intro h
    exact extension_of_boolean κ hκ.aleph0_le (boolean_of_fixedDomain κ hκ.aleph0_le h)
  · intro h
    exact fixedDomain_of_fine κ (fine_of_extension κ hκ h)

theorem boolean_iff_extension (κ : Cardinal.{u}) (hκ : κ.IsRegular) :
    BooleanCompactness κ ↔ CompleteFilterExtension κ := by
  constructor
  · exact extension_of_boolean κ hκ.aleph0_le
  · intro h
    exact boolean_of_fixedDomain κ hκ.aleph0_le
      (fixedDomain_of_fine κ (fine_of_extension κ hκ h))

theorem fixedDomain_iff_fine (κ : Cardinal.{u}) (hκ : κ.IsRegular) :
    FixedDomainCompactness κ ↔ FineUltrafilterPrinciple κ := by
  constructor
  · intro h
    exact fine_of_extension κ hκ ((fixedDomain_iff_extension κ hκ).mp h)
  · exact fixedDomain_of_fine κ

theorem boolean_iff_fixedDomain (κ : Cardinal.{u}) (hκ : κ.IsRegular) :
    BooleanCompactness κ ↔ FixedDomainCompactness κ :=
  (boolean_iff_extension κ hκ).trans (fixedDomain_iff_extension κ hκ).symm

/-- The ordinary infinite-cardinal baseline requires no extra existence principle. -/
theorem extension_aleph0 : CompleteFilterExtension Cardinal.aleph0.{u} := by
  intro X F hF _
  let : F.NeBot := hF
  obtain ⟨U, hUF⟩ := Ultrafilter.exists_le F
  exact ⟨U, hUF, Filter.cardinalInterFilter_aleph0 (U : Filter X)⟩

theorem fixedDomain_aleph0 : FixedDomainCompactness Cardinal.aleph0.{u} :=
  (fixedDomain_iff_extension _ Cardinal.isRegular_aleph0).mpr extension_aleph0

theorem boolean_aleph0 : BooleanCompactness Cardinal.aleph0.{u} :=
  (boolean_iff_extension _ Cardinal.isRegular_aleph0).mpr extension_aleph0

end Komorebi.CompactnessClassification
