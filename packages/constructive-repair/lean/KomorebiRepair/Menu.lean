import KomorebiRepair.Basic
import Mathlib.LinearAlgebra.Pi
import Mathlib.Algebra.BigOperators.Fin

/-! # Finite menus with actual correction coefficients -/
namespace KomorebiRepair
open scoped BigOperators

variable {k U V I J : Type*} [CommRing k]
  [AddCommGroup U] [Module k U] [AddCommGroup V] [Module k V]

/-- Only selected directions occur. The coefficient domain is the selected finite set. -/
def menuMap (e : J → V) (S : Finset J) : (S → k) →ₗ[k] V where
  toFun a := ∑ j : S, a j • e j
  map_add' a b := by simp [add_smul, Finset.sum_add_distrib]
  map_smul' c a := by simp [Finset.smul_sum, mul_smul]

@[simp] theorem menuMap_apply (e : J → V) (S : Finset J) (a : S → k) :
    menuMap e S a = ∑ j : S, a j • e j := rfl

def menuObstructionSpan (D : U →ₗ[k] V) (e : J → V) (S : Finset J) :=
  Submodule.span k (Set.range fun j : S => obstructionMap D (e j))

theorem menu_quotient_range (D : U →ₗ[k] V) (e : J → V) (S : Finset J) :
    LinearMap.range ((obstructionMap D).comp (menuMap e S)) =
      menuObstructionSpan D e S := by
  classical
  apply le_antisymm
  · rintro _ ⟨a, rfl⟩
    simp only [LinearMap.comp_apply, menuMap_apply, map_sum, map_smul]
    apply Submodule.sum_mem
    intro j _
    exact Submodule.smul_mem _ _ (Submodule.subset_span ⟨j, rfl⟩)
  · apply Submodule.span_le.mpr
    rintro _ ⟨j, rfl⟩
    refine ⟨Pi.single j 1, ?_⟩
    simp [menuMap, Pi.single_apply]

/-- Exact finite-menu feasibility, including existence of original-space coefficients. -/
theorem finite_menu_repair_iff_span (D : U →ₗ[k] V) (e : J → V)
    (S : Finset J) (r : I → V) :
    (∀ i, ∃ u : U, ∃ a : S → k, D u + ∑ j : S, a j • e j = -r i) ↔
      obstructionSpan D r ≤ menuObstructionSpan D e S := by
  change FamilyRepairable D (menuMap e S) r ↔ _
  rw [family_repairable_iff_span_le, menu_quotient_range]

theorem menu_mono (D : U →ₗ[k] V) (e : J → V) {S T : Finset J} (hST : S ⊆ T) :
    menuObstructionSpan D e S ≤ menuObstructionSpan D e T := by
  apply Submodule.span_le.mpr
  rintro _ ⟨j, rfl⟩
  exact Submodule.subset_span ⟨⟨j, hST j.property⟩, rfl⟩

theorem repairable_menu_mono (D : U →ₗ[k] V) (e : J → V) {S T : Finset J}
    (hST : S ⊆ T) (r : I → V) (h : FamilyRepairable D (menuMap e S) r) :
    FamilyRepairable D (menuMap e T) r := by
  apply (family_repairable_iff_span_le D (menuMap e T) r).mpr
  rw [menu_quotient_range]
  have hs := (family_repairable_iff_span_le D (menuMap e S) r).mp h
  rw [menu_quotient_range] at hs
  exact hs.trans (menu_mono D e hST)

end KomorebiRepair
