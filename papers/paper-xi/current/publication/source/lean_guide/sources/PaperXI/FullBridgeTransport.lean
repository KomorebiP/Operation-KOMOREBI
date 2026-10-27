import PaperXI.CyclicBridge

/-! Actual semidirect and carrier transport of a finite bridge. These endpoints
connect the tensor model's normal and stabilizer equations to full operators. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FullBridgeTransport

variable {H H' C V W : Type*} [Group H] [Group H'] [Group C]
variable [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

/-- Matching actual group lifts and both generator actions give a bridge for
all elements of the two isomorphic semidirect products. -/
theorem semidirect_along (e : H ≃* H')
    (α : C →* MulAut H) (β : C →* MulAut H')
    (he : ∀ g, (α g).trans e = e.trans (β g))
    (ρ : Representation ℂ H V) (σ : Representation ℂ H' W)
    (R : Representation ℂ C V) (T : Representation ℂ C W)
    (hR : ∀ g h x, R g (ρ h x) = ρ (α g h) (R g x))
    (hT : ∀ g h x, T g (σ h x) = σ (β g h) (T g x))
    (U : V ≃ₗ[ℂ] W)
    (hU : ∀ h x, U (ρ h x) = σ (e h) (U x))
    (hC : ∀ g x, U (R g x) = T g (U x)) :
    ∀ a x, U (CyclicBridge.semidirectRepresentation α ρ R hR a x) =
      CyclicBridge.semidirectRepresentation β σ T hT
        (SemidirectProduct.congr e (MulEquiv.refl C) he a) (U x) := by
  intro a x
  change U (ρ a.left (R a.right x)) = σ (e a.left) (T a.right (U x))
  rw [hU, hC]

variable {V₀ W₀ : Type*} [AddCommGroup V₀] [Module ℂ V₀]
variable [AddCommGroup W₀] [Module ℂ W₀]

/-- Conjugating a model bridge by actual intertwining factorizations produces
a bridge of the declared representations on their original carrier spaces. -/
theorem through_factorizations (e : H →* H')
    (ρ₀ : Representation ℂ H V₀) (σ₀ : Representation ℂ H' W₀)
    (ρ : Representation ℂ H V) (σ : Representation ℂ H' W)
    (F : V₀ ≃ₗ[ℂ] V) (G : W₀ ≃ₗ[ℂ] W)
    (hF : ∀ h x, F (ρ₀ h x) = ρ h (F x))
    (hG : ∀ h x, G (σ₀ h x) = σ h (G x))
    (U : V₀ ≃ₗ[ℂ] W₀) (hU : ∀ h x, U (ρ₀ h x) = σ₀ (e h) (U x)) :
    ∀ h x, (F.symm.trans (U.trans G)) (ρ h x) =
      σ (e h) ((F.symm.trans (U.trans G)) x) := by
  intro h x
  obtain ⟨y, rfl⟩ := F.surjective x
  rw [← hF]
  simp only [LinearEquiv.trans_apply, LinearEquiv.symm_apply_apply, hU, hG]

end PaperXI.FullBridgeTransport
