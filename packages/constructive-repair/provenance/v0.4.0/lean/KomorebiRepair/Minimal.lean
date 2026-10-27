import KomorebiRepair.Basic
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-! # Free linear repair: a proved lower bound and an attained minimum
Existence of the repair is proved from vector-space splitting, not stored as an input.
The splitting uses classical choice and is not claimed to be an executable solver.
-/
namespace KomorebiRepair

variable {k U V I : Type*} [Field k]
  [AddCommGroup U] [Module k U] [AddCommGroup V] [Module k V]

theorem repair_dimension_lower_bound {W : Type*} [AddCommGroup W] [Module k W]
    [FiniteDimensional k W] (D : U →ₗ[k] V) (E : W →ₗ[k] V) (r : I → V)
    (h : FamilyRepairable D E r) :
    Module.finrank k (obstructionSpan D r) ≤ Module.finrank k W := by
  exact (Submodule.finrank_mono ((family_repairable_iff_span_le D E r).mp h)).trans
    (LinearMap.finrank_range_le ((obstructionMap D).comp E))

/-- A lift of the entire obstruction space exists over a field. -/
theorem exists_obstruction_section (D : U →ₗ[k] V) :
    ∃ s : ObstructionSpace D →ₗ[k] V,
      (obstructionMap D).comp s = LinearMap.id := by
  apply LinearMap.exists_rightInverse_of_surjective
  apply LinearMap.range_eq_top.mpr
  exact (LinearMap.range D).mkQ_surjective

/-- Restrict a quotient section to the required obstruction span. -/
theorem exists_attaining_repair (D : U →ₗ[k] V) (r : I → V) :
    ∃ E : obstructionSpan D r →ₗ[k] V,
      (obstructionMap D).comp E = (obstructionSpan D r).subtype ∧
      FamilyRepairable D E r := by
  obtain ⟨s, hs⟩ := exists_obstruction_section D
  let E := s.comp (obstructionSpan D r).subtype
  have hE : (obstructionMap D).comp E = (obstructionSpan D r).subtype := by
    ext x
    exact LinearMap.congr_fun hs (x : ObstructionSpace D)
  refine ⟨E, hE, ?_⟩
  apply (family_repairable_iff_span_le D E r).mpr
  intro x hx
  refine ⟨⟨x, hx⟩, ?_⟩
  exact LinearMap.congr_fun hE ⟨x, hx⟩

/-- The least attainable added dimension is the dimension of the required obstruction span. -/
theorem free_minimal_repair_rank [FiniteDimensional k V]
    (D : U →ₗ[k] V) (r : I → V) :
    (∃ E : obstructionSpan D r →ₗ[k] V, FamilyRepairable D E r) ∧
    ∀ (W : Type*) [AddCommGroup W] [Module k W] [FiniteDimensional k W]
      (E : W →ₗ[k] V), FamilyRepairable D E r →
      Module.finrank k (obstructionSpan D r) ≤ Module.finrank k W := by
  constructor
  · obtain ⟨E, _, hE⟩ := exists_attaining_repair D r
    exact ⟨E, hE⟩
  · intro W _ _ _ E hE
    exact repair_dimension_lower_bound D E r hE

end KomorebiRepair
