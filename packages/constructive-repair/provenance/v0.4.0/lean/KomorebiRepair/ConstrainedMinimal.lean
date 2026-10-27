import KomorebiRepair.Minimal

/-! # Minimum dimension inside a declared linear subspace of legal directions
This is not the same cost model as counting entries of a prescribed finite menu.
-/
namespace KomorebiRepair
variable {k U V I : Type*} [Field k]
  [AddCommGroup U] [Module k U] [AddCommGroup V] [Module k V]

/-- Feasibility inside a subspace produces an optimal-dimensional legal linear lift. -/
theorem admissible_subspace_attainment (D : U →ₗ[k] V) (r : I → V)
    (A : Submodule k V)
    (h : obstructionSpan D r ≤ LinearMap.range ((obstructionMap D).comp A.subtype)) :
    ∃ E : obstructionSpan D r →ₗ[k] V,
      (∀ w, E w ∈ A) ∧
      (obstructionMap D).comp E = (obstructionSpan D r).subtype ∧
      FamilyRepairable D E r := by
  let f := (obstructionMap D).comp A.subtype
  obtain ⟨s, hs⟩ := f.rangeRestrict.exists_rightInverse_of_surjective f.range_rangeRestrict
  let E := A.subtype.comp (s.comp (Submodule.inclusion h))
  have hE : (obstructionMap D).comp E = (obstructionSpan D r).subtype := by
    ext w
    exact congrArg Subtype.val (LinearMap.congr_fun hs (Submodule.inclusion h w))
  refine ⟨E, fun w => (s (Submodule.inclusion h w)).property, hE, ?_⟩
  apply (family_repairable_iff_span_le D E r).mpr
  intro z hz
  exact ⟨⟨z, hz⟩, LinearMap.congr_fun hE ⟨z, hz⟩⟩

/-- A legal added map cannot repair a residual family excluded by the whole legal subspace. -/
theorem admissible_subspace_no_go {W : Type*} [AddCommGroup W] [Module k W]
    (D : U →ₗ[k] V) (r : I → V) (A : Submodule k V) (E : W →ₗ[k] V)
    (hE : ∀ w, E w ∈ A)
    (h : ¬ obstructionSpan D r ≤ LinearMap.range ((obstructionMap D).comp A.subtype)) :
    ¬ FamilyRepairable D E r := by
  intro hr
  apply h
  intro z hz
  obtain ⟨w, hw⟩ := (family_repairable_iff_span_le D E r).mp hr hz
  exact ⟨⟨E w, hE w⟩, hw⟩

end KomorebiRepair
