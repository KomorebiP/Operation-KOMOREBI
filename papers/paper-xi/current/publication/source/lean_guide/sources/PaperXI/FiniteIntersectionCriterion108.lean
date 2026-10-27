import PaperXI.CompactIntersection108

/-! An exact criterion on a literal finite model. The scalar character profile,
compatibility and index identity must still be proved for the arithmetic data. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteIntersectionCriterion108
open Representation IntersectionModel108
variable {K G Q W : Type*} [Group K] [Group G] [Group Q] [Fintype Q]
  [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]

/-- Dimension one of the original operator space is equivalent to the finite
index identity, once the two actual character profiles are established. -/
theorem dimension_one_iff (ι : K →* G) (ρ : Representation ℂ K W) (g : G)
    (q : pairs ι g →* Q) (hq : Function.Surjective q)
    (ρ₁ ρ₂ : Representation ℂ Q W)
    (he₁ : ρ₁.comp q = ρ.comp (left ι g)) (he₂ : ρ₂.comp q = ρ.comp (right ι g))
    (H₁ H₂ : Subgroup Q) (θ₁ : H₁ →* ℂˣ) (θ₂ : H₂ →* ℂˣ)
    (h₁ : ∀ h : H₁, ρ₁ h = (θ₁ h : ℂ) • LinearMap.id)
    (h₂ : ∀ h : H₂, ρ₂ h = (θ₂ h : ℂ) • LinearMap.id)
    (hz₁ : ∀ x : Q, x ∉ H₁ → ρ₁.character x = 0)
    (hz₂ : ∀ x : Q, x ∉ H₂ → ρ₂.character x = 0)
    (hc : ∀ x : Q, ∀ h₁ : x ∈ H₁, ∀ h₂ : x ∈ H₂, θ₁ ⟨x, h₁⟩ = θ₂ ⟨x, h₂⟩) :
    Module.finrank ℂ (IntertwiningSpace107.space ι ρ g) = 1 ↔
      Module.finrank ℂ W * Module.finrank ℂ W * Nat.card (H₁ ⊓ H₂ : Subgroup Q) =
        Nat.card Q := by
  rw [finrank_model ι ρ g q hq ρ₁ ρ₂ he₁ he₂]
  exact CharacterPairing108.dimension_one_iff ρ₁ ρ₂ H₁ H₂ θ₁ θ₂ h₁ h₂ hz₁ hz₂ hc

end PaperXI.FiniteIntersectionCriterion108
