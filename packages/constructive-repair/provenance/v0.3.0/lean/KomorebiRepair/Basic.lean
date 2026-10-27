import Mathlib.LinearAlgebra.Quotient.Basic
import Mathlib.Tactic.Abel

/-!
# Linear repair and the actual quotient obstruction
The equation is always `D u + E w = -r` in the original target module.
Nothing in the problem data assumes a repair exists.
-/
namespace KomorebiRepair

variable {k U V W I : Type*} [CommRing k]
  [AddCommGroup U] [Module k U] [AddCommGroup V] [Module k V]
  [AddCommGroup W] [Module k W]

abbrev ObstructionSpace (D : U →ₗ[k] V) := V ⧸ LinearMap.range D

def obstructionMap (D : U →ₗ[k] V) : V →ₗ[k] ObstructionSpace D :=
  (LinearMap.range D).mkQ

def Correctable (D : U →ₗ[k] V) (r : V) : Prop := ∃ u, D u = -r

def Repairable (D : U →ₗ[k] V) (E : W →ₗ[k] V) (r : V) : Prop :=
  ∃ u w, D u + E w = -r

def FamilyRepairable (D : U →ₗ[k] V) (E : W →ₗ[k] V) (r : I → V) : Prop :=
  ∀ i, Repairable D E (r i)

def obstructionSpan (D : U →ₗ[k] V) (r : I → V) : Submodule k (ObstructionSpace D) :=
  Submodule.span k (Set.range fun i => obstructionMap D (r i))

@[simp] theorem obstructionMap_correction (D : U →ₗ[k] V) (u : U) :
    obstructionMap D (D u) = 0 := by
  exact (Submodule.Quotient.mk_eq_zero _).mpr ⟨u, rfl⟩

theorem correctable_iff_obstruction_zero (D : U →ₗ[k] V) (r : V) :
    Correctable D r ↔ obstructionMap D r = 0 := by
  constructor
  · rintro ⟨u, hu⟩
    have h := congrArg (obstructionMap D) hu
    simpa only [obstructionMap_correction, map_neg, zero_eq_neg] using h
  · intro h
    obtain ⟨u, hu⟩ := (Submodule.Quotient.mk_eq_zero _).mp h
    refine ⟨-u, ?_⟩
    simp [hu]

theorem repairable_iff_obstruction_mem_range (D : U →ₗ[k] V) (E : W →ₗ[k] V) (r : V) :
    Repairable D E r ↔
      obstructionMap D r ∈ LinearMap.range ((obstructionMap D).comp E) := by
  constructor
  · rintro ⟨u, w, hw⟩
    have h : obstructionMap D (E w) = -obstructionMap D r := by
      simpa only [map_add, map_neg, obstructionMap_correction, zero_add] using
        congrArg (obstructionMap D) hw
    refine ⟨-w, ?_⟩
    simp only [LinearMap.comp_apply, map_neg, h, neg_neg]
  · rintro ⟨w, hw⟩
    have hzero : obstructionMap D (r - E w) = 0 := by
      simp only [map_sub, LinearMap.comp_apply] at hw ⊢
      rw [hw, sub_self]
    obtain ⟨u, hu⟩ := (Submodule.Quotient.mk_eq_zero _).mp hzero
    refine ⟨-u, -w, ?_⟩
    simp only [map_neg, hu]
    abel

theorem obstruction_mem_span (D : U →ₗ[k] V) (r : I → V) (i : I) :
    obstructionMap D (r i) ∈ obstructionSpan D r :=
  Submodule.subset_span ⟨i, rfl⟩

theorem family_repairable_iff_span_le (D : U →ₗ[k] V) (E : W →ₗ[k] V) (r : I → V) :
    FamilyRepairable D E r ↔
      obstructionSpan D r ≤ LinearMap.range ((obstructionMap D).comp E) := by
  constructor
  · intro h
    apply Submodule.span_le.mpr
    rintro _ ⟨i, rfl⟩
    exact (repairable_iff_obstruction_mem_range D E (r i)).mp (h i)
  · intro h i
    exact (repairable_iff_obstruction_mem_range D E (r i)).mpr
      (h (obstruction_mem_span D r i))

/-- A positive quotient witness gives a genuine cancellation in the original module. -/
theorem reconstruct_cancellation (D : U →ₗ[k] V) (E : W →ₗ[k] V)
    (r : V) (w : W) (hw : obstructionMap D (E w) = obstructionMap D r) :
    ∃ u w', D u + E w' + r = 0 := by
  obtain ⟨u, w', h⟩ := (repairable_iff_obstruction_mem_range D E r).mpr ⟨w, hw⟩
  exact ⟨u, w', by rw [h]; simp⟩

end KomorebiRepair
