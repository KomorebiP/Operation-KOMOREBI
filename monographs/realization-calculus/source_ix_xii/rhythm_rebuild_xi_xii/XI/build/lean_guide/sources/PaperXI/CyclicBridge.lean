import PaperXI.DiscrepancyCharacter
import Mathlib.GroupTheory.SemidirectProduct

/-! A trivial scalar discrepancy on one cyclic generator closes an actual
semidirect-product bridge. Phase means the scalar discrepancy, not trace. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicBridge
variable {H C V W : Type*} [Group H] [Group C]
variable [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

theorem character_trivial (δ : C →* ℂˣ) (c : C)
    (hgen : ∀ g : C, ∃ n : ℤ, g = c ^ n) (hc : δ c = 1) : ∀ g, δ g = 1 := by
  intro g
  obtain ⟨n, rfl⟩ := hgen g
  simp [map_zpow, hc]

theorem semidirect_intertwining (α : C →* MulAut H)
    (π : Representation ℂ (H ⋊[α] C) V) (σ : Representation ℂ (H ⋊[α] C) W)
    (U : V ≃ₗ[ℂ] W)
    (hH : ∀ h x, U (π (SemidirectProduct.inl h) x) = σ (SemidirectProduct.inl h) (U x))
    (hC : ∀ g x, U (π (SemidirectProduct.inr g) x) = σ (SemidirectProduct.inr g) (U x)) :
    ∀ a x, U (π a x) = σ a (U x) := by
  intro a x
  rw [← SemidirectProduct.inl_left_mul_inr_right a]
  simp only [map_mul, Module.End.mul_apply, hH, hC]

theorem stabilizer_covariance (α : C →* MulAut H)
    (π : Representation ℂ (H ⋊[α] C) V) (g : C) (h : H) (x : V) :
    π (SemidirectProduct.inr g) (π (SemidirectProduct.inl h) x) =
      π (SemidirectProduct.inl (α g h)) (π (SemidirectProduct.inr g) x) := by
  have he : (SemidirectProduct.inr g : H ⋊[α] C) * SemidirectProduct.inl h =
      SemidirectProduct.inl (α g h) * SemidirectProduct.inr g := by
    rw [SemidirectProduct.inl_aut]
    simp [mul_assoc]
  have hr := congrArg (fun a => π a x) he
  simpa [map_mul, Module.End.mul_apply] using hr

/-- The character is produced from the actual actions. Its generator value
being one is sufficient to intertwine every semidirect-product element. -/
theorem one_phase_bridge [FiniteDimensional ℂ V] (α : C →* MulAut H)
    (π : Representation ℂ (H ⋊[α] C) V) (σ : Representation ℂ (H ⋊[α] C) W)
    [Representation.IsIrreducible (π.comp SemidirectProduct.inl)]
    (U : V ≃ₗ[ℂ] W)
    (hH : ∀ h x, U (π (SemidirectProduct.inl h) x) = σ (SemidirectProduct.inl h) (U x))
    (c : C) (hgen : ∀ g : C, ∃ n : ℤ, g = c ^ n) :
    ∃ δ : C →* ℂˣ,
      (∀ g x, U (π (SemidirectProduct.inr g) x) =
        (δ g : ℂ) • σ (SemidirectProduct.inr g) (U x)) ∧
      (δ c = 1 → ∀ a x, U (π a x) = σ a (U x)) := by
  obtain ⟨δ, hδ⟩ := PaperXI.DiscrepancyCharacter.exists_character
    (π.comp SemidirectProduct.inl) (σ.comp SemidirectProduct.inl) U hH α
    (π.comp SemidirectProduct.inr) (σ.comp SemidirectProduct.inr)
    (stabilizer_covariance α π) (stabilizer_covariance α σ)
  refine ⟨δ, hδ, ?_⟩
  intro hc
  apply semidirect_intertwining α π σ U hH
  intro g x
  simpa [character_trivial δ c hgen hc g] using hδ g x


/-- Assemble compatible honest actions into the actual semidirect representation. -/
def semidirectRepresentation (α : C →* MulAut H)
    (ρ : Representation ℂ H V) (R : Representation ℂ C V)
    (hR : ∀ g h x, R g (ρ h x) = ρ (α g h) (R g x)) :
    Representation ℂ (H ⋊[α] C) V where
  toFun a := ρ a.left * R a.right
  map_one' := by simp
  map_mul' a b := by
    apply LinearMap.ext
    intro x
    simp [map_mul, Module.End.mul_apply, hR]

@[simp] theorem semidirectRepresentation_inl (α : C →* MulAut H)
    (ρ : Representation ℂ H V) (R : Representation ℂ C V)
    (hR : ∀ g h x, R g (ρ h x) = ρ (α g h) (R g x)) (h : H) :
    semidirectRepresentation α ρ R hR (SemidirectProduct.inl h) = ρ h := by
  simp [semidirectRepresentation]

@[simp] theorem semidirectRepresentation_inr (α : C →* MulAut H)
    (ρ : Representation ℂ H V) (R : Representation ℂ C V)
    (hR : ∀ g h x, R g (ρ h x) = ρ (α g h) (R g x)) (g : C) :
    semidirectRepresentation α ρ R hR (SemidirectProduct.inr g) = R g := by
  simp [semidirectRepresentation]

/-- The manuscript's input form: compatible normal-subgroup and cyclic
stabilizer actions are assembled here rather than assumed preassembled. -/
theorem one_phase_bridge_from_actions [FiniteDimensional ℂ V]
    (ρ : Representation ℂ H V) [Representation.IsIrreducible ρ]
    (σ : Representation ℂ H W) (U : V ≃ₗ[ℂ] W)
    (hU : ∀ h x, U (ρ h x) = σ h (U x))
    (α : C →* MulAut H) (R : Representation ℂ C V) (S : Representation ℂ C W)
    (hR : ∀ g h x, R g (ρ h x) = ρ (α g h) (R g x))
    (hS : ∀ g h x, S g (σ h x) = σ (α g h) (S g x))
    (c : C) (hgen : ∀ g : C, ∃ n : ℤ, g = c ^ n) :
    ∃ δ : C →* ℂˣ,
      (∀ g x, U (R g x) = (δ g : ℂ) • S g (U x)) ∧
      (δ c = 1 → ∀ a x,
        U (semidirectRepresentation α ρ R hR a x) =
          semidirectRepresentation α σ S hS a (U x)) := by
  obtain ⟨δ, hδ⟩ := PaperXI.DiscrepancyCharacter.exists_character ρ σ U hU α R S hR hS
  refine ⟨δ, hδ, ?_⟩
  intro hc
  apply semidirect_intertwining α (semidirectRepresentation α ρ R hR)
    (semidirectRepresentation α σ S hS) U
  · simpa only [semidirectRepresentation_inl] using hU
  · intro g x
    simpa only [semidirectRepresentation_inr, character_trivial δ c hgen hc g,
      Units.val_one, one_smul] using hδ g x

end PaperXI.CyclicBridge
