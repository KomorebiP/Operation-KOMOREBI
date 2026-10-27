import PaperXI.CyclicBridge
import Mathlib.Algebra.Group.Subgroup.Basic

/-! Triviality of the actual stabilizer discrepancy on a generating set. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CharacterGenerators

variable {C D : Type*} [Group C] [Group D]

/-- Kernel membership propagates from generators through the subgroup closure. -/
theorem eq_one_on_closure (δ : C →* D) (S : Set C)
    (hS : ∀ g ∈ S, δ g = 1) : ∀ g ∈ Subgroup.closure S, δ g = 1 := by
  have hle : Subgroup.closure S ≤ δ.ker := (Subgroup.closure_le δ.ker).mpr hS
  exact fun g hg => hle hg

/-- The arbitrary generating-set test, including noncyclic stabilizers. -/
theorem trivial (δ : C →* D) (S : Set C) (hgen : Subgroup.closure S = ⊤)
    (hS : ∀ g ∈ S, δ g = 1) : ∀ g, δ g = 1 := by
  intro g
  apply eq_one_on_closure δ S hS
  rw [hgen]
  trivial

theorem trivial_iff (δ : C →* D) (S : Set C) (hgen : Subgroup.closure S = ⊤) :
    (∀ g, δ g = 1) ↔ ∀ g ∈ S, δ g = 1 :=
  ⟨fun h g _ => h g, trivial δ S hgen⟩

variable {H V W : Type*} [Group H]
variable [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
variable [AddCommGroup W] [Module ℂ W]

/-- Actual honest stabilizer actions produce the character. Generator values
of this character close the whole semidirect-product bridge. -/
theorem bridge_from_actions
    (ρ : Representation ℂ H V) [Representation.IsIrreducible ρ]
    (σ : Representation ℂ H W) (U : V ≃ₗ[ℂ] W)
    (hU : ∀ h x, U (ρ h x) = σ h (U x))
    (α : C →* MulAut H) (R : Representation ℂ C V) (T : Representation ℂ C W)
    (hR : ∀ g h x, R g (ρ h x) = ρ (α g h) (R g x))
    (hT : ∀ g h x, T g (σ h x) = σ (α g h) (T g x))
    (S : Set C) (hgen : Subgroup.closure S = ⊤) :
    ∃ δ : C →* ℂˣ,
      (∀ g x, U (R g x) = (δ g : ℂ) • T g (U x)) ∧
      ((∀ g ∈ S, δ g = 1) → ∀ a x,
        U (CyclicBridge.semidirectRepresentation α ρ R hR a x) =
          CyclicBridge.semidirectRepresentation α σ T hT a (U x)) := by
  obtain ⟨δ, hδ⟩ := DiscrepancyCharacter.exists_character ρ σ U hU α R T hR hT
  refine ⟨δ, hδ, ?_⟩
  intro hs
  apply CyclicBridge.semidirect_intertwining α
    (CyclicBridge.semidirectRepresentation α ρ R hR)
    (CyclicBridge.semidirectRepresentation α σ T hT) U
  · simpa only [CyclicBridge.semidirectRepresentation_inl] using hU
  · intro g x
    simpa only [CyclicBridge.semidirectRepresentation_inr, trivial δ S hgen hs g,
      Units.val_one, one_smul] using hδ g x

end PaperXI.CharacterGenerators
