import PaperX.RepresentationForests
import PaperX.JointOccupancy

/-! Conditional system realization. This constructs actual coefficient-indexed
matrix representations; it does not assume an unspecified realization map.
Every arithmetic admissibility condition beyond the finite congruence conditions
is an explicit separate implication. No universal companion or occupancy axiom. -/
set_option autoImplicit false
namespace PaperX.SystemCompletion
open PaperX.RepresentationLimits PaperX.RepresentationTopology PaperX.RepresentationForests
variable {Λ G ι : Type} [Group G] [Fintype ι] [DecidableEq ι]
variable (O : Λ → Type) [∀ l, CommRing (O l)] (I : (l : Λ) → Ideal (O l))
variable (C : (l : Λ) → Conditions (G := G) (ι := ι) (I l))

/-- A completed family of actual representations satisfies every selected finite
condition, rather than merely supplying a branch in an unrelated set tower. -/
def SystemRealizes (ρ : (l : Λ) → MatrixRep (O l) G ι) : Prop :=
  ∀ l, Realizes (I l) (C l) (ρ l)

theorem exists_system [∀ l, IsAdicComplete (I l) (O l)]
    (finite : ∀ l k, Finite {ρ : MatrixRep (O l ⧸ (I l)^k) G ι // (C l).allowed k ρ})
    (occupied : ∀ l k, ∃ ρ, (C l).allowed k ρ) :
    ∃ ρ : (l : Λ) → MatrixRep (O l) G ι, SystemRealizes O I C ρ := by
  classical
  have H := fun l => exists_realization (I l) (C l) (finite l) (occupied l)
  exact ⟨fun l => Classical.choose (H l), fun l => Classical.choose_spec (H l)⟩

/-- Exact two-sided finite-level criterion for the congruence-defined system. -/
theorem system_realization_iff [∀ l, IsAdicComplete (I l) (O l)]
    (finite : ∀ l k, Finite {ρ : MatrixRep (O l ⧸ (I l)^k) G ι // (C l).allowed k ρ}) :
    (∃ ρ, SystemRealizes O I C ρ) ↔ ∀ l k, ∃ τ, (C l).allowed k τ := by
  constructor
  · rintro ⟨ρ,hρ⟩ l k
    exact ⟨reduce (I l) (ρ l) k, hρ l k⟩
  · exact exists_system O I C finite

theorem system_empty_level_obstruction (l : Λ) (k : ℕ)
    (h : ¬ ∃ τ, (C l).allowed k τ) : ¬ ∃ ρ, SystemRealizes O I C ρ := by
  rintro ⟨ρ,hρ⟩
  exact h ⟨reduce (I l) (ρ l) k, hρ l k⟩

/-- Conditional completion together with a separately supplied fixed finite
carrier. Nonempty forests and positive carrier occupancy remain independent. -/
theorem completion_and_occupancy_iff [∀ l, IsAdicComplete (I l) (O l)]
    (finite : ∀ l k, Finite {ρ : MatrixRep (O l ⧸ (I l)^k) G ι // (C l).allowed k ρ})
    {K V J : Type*} [Field K] [CharZero K] [AddCommGroup V] [Module K V]
    [FiniteDimensional K V]
    (T : J → Module.End K V) (a : J → K) (indices : List J)
    (hs : ∀ j, PaperX.SpectralProjectors.Split (T j))
    (hc : ∀ i j, Commute (T i) (T j)) :
    (∃ ρ, SystemRealizes O I C ρ ∧ PaperX.JointOccupancy.Occupied T a indices) ↔
      (∀ l k, ∃ τ, (C l).allowed k τ) ∧
        LinearMap.trace K V (PaperX.JointOccupancy.joint T a indices) ≠ 0 := by
  rw [show (∃ ρ, SystemRealizes O I C ρ ∧ PaperX.JointOccupancy.Occupied T a indices) ↔
      (∃ ρ, SystemRealizes O I C ρ) ∧ PaperX.JointOccupancy.Occupied T a indices from
    ⟨fun ⟨ρ,hρ,ho⟩ => ⟨⟨ρ,hρ⟩,ho⟩, fun ⟨⟨ρ,hρ⟩,ho⟩ => ⟨ρ,hρ,ho⟩⟩]
  rw [system_realization_iff O I C finite,
    PaperX.JointOccupancy.occupied_iff_trace_ne_zero T a hs hc indices]

variable [TopologicalSpace G]

/-- Every local-property assertion below is an explicit hypothesis on the
realized congruence conditions. In particular, this does not prove p-adic Hodge
conditions are closed, or supply a compatible-system carrier. -/
theorem continuous_system_completion [∀ l, IsAdicComplete (I l) (O l)]
    (finite : ∀ l k, Finite {ρ : MatrixRep (O l ⧸ (I l)^k) G ι // (C l).allowed k ρ})
    (occupied : ∀ l k, ∃ ρ, (C l).allowed k ρ)
    (continuous : ∀ l k ρ, (C l).allowed k ρ → FiniteRepContinuous ρ)
    (Local : (l : Λ) → MatrixRep (O l) G ι → Prop)
    (stable : ∀ l ρ, Realizes (I l) (C l) ρ → Local l ρ) :
    ∃ ρ : (l : Λ) → MatrixRep (O l) G ι,
      SystemRealizes O I C ρ ∧ ∀ l, AdicRepContinuous (I l) (ρ l) ∧ Local l (ρ l) := by
  classical
  have H := fun l => completion_with_local_condition (I l) (C l)
    (finite l) (occupied l) (continuous l) (Local l) (stable l)
  refine ⟨fun l => Classical.choose (H l), ?_, ?_⟩
  · intro l
    exact (Classical.choose_spec (H l)).1
  · intro l
    exact (Classical.choose_spec (H l)).2

end PaperX.SystemCompletion
