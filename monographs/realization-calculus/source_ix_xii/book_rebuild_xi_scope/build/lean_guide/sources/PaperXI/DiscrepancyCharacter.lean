import PaperXI.SchurScalar

/-! Discrepancy of honest stabilizer actions is a character, derived from Schur. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DiscrepancyCharacter
open PaperXI.GeneratedIrreducibility
variable {H C V W : Type*} [Group H] [Group C]
variable [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
variable [AddCommGroup W] [Module ℂ W]

/-- No cyclicity is needed until the later generator test. -/
theorem exists_character (ρ : Representation ℂ H V) [Representation.IsIrreducible ρ]
    (σ : Representation ℂ H W) (U : V ≃ₗ[ℂ] W)
    (hU : ∀ h x, U (ρ h x) = σ h (U x))
    (α : C →* MulAut H) (R : Representation ℂ C V) (S : Representation ℂ C W)
    (hR : ∀ g h x, R g (ρ h x) = ρ (α g h) (R g x))
    (hS : ∀ g h x, S g (σ h x) = σ (α g h) (S g x)) :
    ∃ δ : C →* ℂˣ, ∀ g x, U (R g x) = (δ g : ℂ) • S g (U x) := by
  have hs (g : C) : ∃! c : ℂˣ, ∀ x, U (R g x) = (c : ℂ) • S g (U x) := by
    let σg : Representation ℂ H W := σ.comp (α g).toMonoidHom
    have hB (h : H) (x : V) : (U.trans (actionEquiv S g)) (ρ h x) =
        σg h ((U.trans (actionEquiv S g)) x) := by
      change S g (U (ρ h x)) = σ (α g h) (S g (U x))
      rw [hU, hS]
    have hA (h : H) (x : V) : ((actionEquiv R g).trans U) (ρ h x) =
        σg h (((actionEquiv R g).trans U) x) := by
      change U (R g (ρ h x)) = σ (α g h) (U (R g x))
      rw [hR, hU]
    exact PaperXI.SchurScalar.bridge_unique ρ σg (U.trans (actionEquiv S g))
      ((actionEquiv R g).trans U) hB hA
  choose d hd hu using hs
  have hone : d 1 = 1 := by
    symm
    apply hu 1 1
    intro x
    simp
  have hmul (g h : C) : d (g * h) = d g * d h := by
    symm
    apply hu (g * h) (d g * d h)
    intro x
    calc
      U (R (g * h) x) = U (R g (R h x)) := by rw [map_mul]; rfl
      _ = (d g : ℂ) • S g (U (R h x)) := hd g (R h x)
      _ = (d g : ℂ) • S g ((d h : ℂ) • S h (U x)) := by rw [hd h]
      _ = ((d g * d h : ℂˣ) : ℂ) • S (g * h) (U x) := by
        simp [map_mul, Module.End.mul_apply, smul_smul]
  exact ⟨{ toFun := d, map_one' := hone, map_mul' := hmul }, hd⟩

end PaperXI.DiscrepancyCharacter
