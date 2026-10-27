import PaperX.RepresentationTopology
import PaperX.Compactness
import Mathlib.Data.Fintype.EquivFin

/-! Finite nonempty forests of actual finite-level representations have actual
integral realizations, once the coefficient ring is adically complete. Finite
level occupancy and continuity are hypotheses, not consequences of compactness. -/
set_option autoImplicit false
namespace PaperX.RepresentationForests
open PaperX.RepresentationLimits PaperX.RepresentationTopology
variable {R G ι : Type} [CommRing R] [Group G] [Fintype ι] [DecidableEq ι]
variable (I : Ideal R)

/-- The finite conditions live on actual quotient representations. -/
structure Conditions where
  allowed : (k : ℕ) → MatrixRep (R ⧸ I^k) G ι → Prop
  downward : ∀ {j k} (h : j ≤ k) ρ, allowed k ρ → allowed j (transition I h ρ)

/-- Every chosen finite representation has a total reduction to the previous
allowed level. Surjectivity of these reduction maps is not assumed. -/
def tower (C : Conditions (G := G) (ι := ι) I) : PaperX.Compactness.Tower where
  Level k := {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ}
  parent k ρ := ⟨transition I (Nat.le_succ k) ρ.val, C.downward _ _ ρ.property⟩

theorem all_compatible (C : Conditions (G := G) (ι := ι) I)
    (b : PaperX.Compactness.Branch (tower I C)) {j k : ℕ} (h : j ≤ k) :
    transition I h (b.value k).val = (b.value j).val := by
  ext g a c
  apply (Ideal.Quotient.eq_factor_of_eq_factor_succ
    (fun _ _ h => Ideal.pow_le_pow_right h)
    (fun m => (b.value m).val g a c) ?_ h).symm
  intro m
  exact (congrArg (fun x => x.val g a c) (b.compatible m)).symm

def family (C : Conditions (G := G) (ι := ι) I)
    (b : PaperX.Compactness.Branch (tower I C)) : Family R I G ι where
  maps k := (b.value k).val
  compatible := all_compatible I C b

/-- Compactness is established for the actual subtype, not for the coefficient
ring alone. A finite coefficient ring does not imply finitely many group maps. -/
theorem finite_levels (C : Conditions (G := G) (ι := ι) I)
    (h : ∀ k, Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ}) :
    PaperX.Compactness.FiniteLevels (tower I C) := by
  intro k
  let : Finite ((tower I C).Level k) := h k
  let : Fintype ((tower I C).Level k) := Fintype.ofFinite _
  classical
  exact ⟨Finset.univ.toList, by simp⟩

/-- An actual realization satisfies the allowed constraints at every precision. -/
def Realizes (C : Conditions (G := G) (ι := ι) I) (ρ : MatrixRep R G ι) : Prop :=
  ∀ k, C.allowed k (reduce I ρ k)

theorem exists_realization [IsAdicComplete I R]
    (C : Conditions (G := G) (ι := ι) I)
    (finite : ∀ k, Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ})
    (occupied : ∀ k, ∃ ρ, C.allowed k ρ) :
    ∃ ρ : MatrixRep R G ι, Realizes I C ρ := by
  obtain ⟨b⟩ := PaperX.Compactness.finite_branch_compactness (tower I C)
    (finite_levels I C finite) (fun k => let ⟨ρ,h⟩ := occupied k; ⟨ρ,h⟩)
  refine ⟨reconstruct I (family I C b), ?_⟩
  intro k
  rw [reconstruct_reduces]
  exact (b.value k).property

/-- This converse does not need completeness, finiteness, or surjective reductions. -/
theorem levels_of_realization (C : Conditions (G := G) (ι := ι) I)
    (ρ : MatrixRep R G ι) (h : Realizes I C ρ) :
    ∀ k, ∃ τ, C.allowed k τ := fun k => ⟨reduce I ρ k, h k⟩

/-- The completed congruence problem is nonempty iff all its finite levels are,
under the explicit complete-ring and finite-allowed-level assumptions. -/
theorem realization_iff [IsAdicComplete I R]
    (C : Conditions (G := G) (ι := ι) I)
    (finite : ∀ k, Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ}) :
    (∃ ρ, Realizes I C ρ) ↔ ∀ k, ∃ τ, C.allowed k τ :=
  ⟨fun ⟨ρ,h⟩ => levels_of_realization I C ρ h, exists_realization I C finite⟩

/-- Failure at any precision obstructs a realization. -/
theorem empty_level_obstructs (C : Conditions (G := G) (ι := ι) I)
    (k : ℕ) (h : ¬ ∃ τ, C.allowed k τ) : ¬ ∃ ρ, Realizes I C ρ := by
  rintro ⟨ρ,hρ⟩
  exact h ⟨reduce I ρ k, hρ k⟩

variable [TopologicalSpace G]

/-- Actual continuity is retained; no abstract realization map is assumed. -/
theorem exists_continuous_realization [IsAdicComplete I R]
    (C : Conditions (G := G) (ι := ι) I)
    (finite : ∀ k, Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ})
    (occupied : ∀ k, ∃ ρ, C.allowed k ρ)
    (continuous : ∀ k ρ, C.allowed k ρ → FiniteRepContinuous ρ) :
    ∃ ρ : MatrixRep R G ι, Realizes I C ρ ∧ AdicRepContinuous I ρ := by
  obtain ⟨b⟩ := PaperX.Compactness.finite_branch_compactness (tower I C)
    (finite_levels I C finite) (fun k => let ⟨ρ,h⟩ := occupied k; ⟨ρ,h⟩)
  refine ⟨reconstruct I (family I C b), ?_, ?_⟩
  · intro k
    rw [reconstruct_reduces]
    exact (b.value k).property
  · apply reconstructed_continuous
    intro k
    exact continuous k (b.value k).val (b.value k).property

/-- A separate local-property implication is explicit. This theorem does not
assert closedness or construct a Hodge--Tate/Weil--Deligne local condition. -/
theorem completion_with_local_condition [IsAdicComplete I R]
    (C : Conditions (G := G) (ι := ι) I)
    (finite : ∀ k, Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ})
    (occupied : ∀ k, ∃ ρ, C.allowed k ρ)
    (continuous : ∀ k ρ, C.allowed k ρ → FiniteRepContinuous ρ)
    (Local : MatrixRep R G ι → Prop)
    (stable : ∀ ρ, Realizes I C ρ → Local ρ) :
    ∃ ρ, Realizes I C ρ ∧ AdicRepContinuous I ρ ∧ Local ρ := by
  obtain ⟨ρ,hρ,hc⟩ := exists_continuous_realization I C finite occupied continuous
  exact ⟨ρ,hρ,hc,stable ρ hρ⟩

end PaperX.RepresentationForests
