import PaperXI.HeisenbergTrace108

/-! Exact character pairing on a finite intersection. The index equality used
for dimension one is an explicit, separate arithmetic obligation. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CharacterPairing108
open Representation
variable {L W U : Type*} [Group L] [Fintype L]
  [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]
  [AddCommGroup U] [Module ℂ U] [FiniteDimensional ℂ U]
  (ρ : Representation ℂ L W) (σ : Representation ℂ L U)
  (H₁ H₂ : Subgroup L) (θ₁ : H₁ →* ℂˣ) (θ₂ : H₂ →* ℂˣ)
  (h₁ : ∀ h : H₁, ρ h = (θ₁ h : ℂ) • LinearMap.id)
  (h₂ : ∀ h : H₂, σ h = (θ₂ h : ℂ) • LinearMap.id)
  (hz₁ : ∀ x : L, x ∉ H₁ → ρ.character x = 0)
  (hz₂ : ∀ x : L, x ∉ H₂ → σ.character x = 0)
  (hc : ∀ x : L, ∀ h₁ : x ∈ H₁, ∀ h₂ : x ∈ H₂, θ₁ ⟨x, h₁⟩ = θ₂ ⟨x, h₂⟩)

include h₁ h₂ hz₁ hz₂ hc in
/-- The formula computes the dimension of the actual Hom space. -/
theorem dimension_formula :
    Nat.card L * Module.finrank ℂ (IntertwiningMap ρ σ) =
      Module.finrank ℂ W * Module.finrank ℂ U * Nat.card (H₁ ⊓ H₂ : Subgroup L) := by
  classical
  have hcard : (Nat.card L : ℂ) ≠ 0 := by exact_mod_cast (Nat.card_pos (α := L)).ne'
  let : Invertible (Nat.card L : ℂ) := invertibleOfNonzero hcard
  have hp (x : L) (hx : x ∈ (H₁ ⊓ H₂ : Subgroup L)) :
      σ.character x * ρ.character x⁻¹ =
        (Module.finrank ℂ W : ℂ) * (Module.finrank ℂ U : ℂ) := by
    have hxi : x⁻¹ ∈ H₁ := H₁.inv_mem hx.1
    rw [HeisenbergTrace108.character_on_subgroup H₂ θ₂ σ h₂ ⟨x, hx.2⟩,
      HeisenbergTrace108.character_on_subgroup H₁ θ₁ ρ h₁ ⟨x⁻¹, hxi⟩]
    have hi : θ₁ ⟨x⁻¹, hxi⟩ = (θ₁ ⟨x, hx.1⟩)⁻¹ := map_inv θ₁ ⟨x, hx.1⟩
    rw [hi, hc x hx.1 hx.2]
    have hu : (θ₂ ⟨x, hx.2⟩ : ℂ) ≠ 0 := Units.ne_zero _
    simp only [Units.val_inv_eq_inv_val]
    field_simp
  have hz (x : L) (hx : x ∉ (H₁ ⊓ H₂ : Subgroup L)) :
      σ.character x * ρ.character x⁻¹ = 0 := by
    by_cases ha : x ∈ H₁
    · have hb : x ∉ H₂ := fun hb => hx ⟨ha, hb⟩
      rw [hz₂ x hb, zero_mul]
    · have hb : x⁻¹ ∉ H₁ := fun hb => ha (by simpa using H₁.inv_mem hb)
      rw [hz₁ x⁻¹ hb, mul_zero]
  have hs : ∑ x : L, σ.character x * ρ.character x⁻¹ =
      (Module.finrank ℂ W : ℂ) * (Module.finrank ℂ U : ℂ) *
        (Nat.card (H₁ ⊓ H₂ : Subgroup L) : ℂ) := by
    rw [Finset.sum_congr_set ((H₁ ⊓ H₂ : Subgroup L) : Set L)
      (fun x => σ.character x * ρ.character x⁻¹)
      (fun _ => (Module.finrank ℂ W : ℂ) * (Module.finrank ℂ U : ℂ)) hp hz]
    simp only [Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
    rw [Fintype.card_eq_nat_card]
    change (Nat.card (H₁ ⊓ H₂ : Subgroup L) : ℂ) *
      ((Module.finrank ℂ W : ℂ) * (Module.finrank ℂ U : ℂ)) = _
    ring
  have he := ρ.card_inv_mul_sum_char_mul_char_eq_finrank σ
  rw [hs] at he
  have hm := congrArg (fun z : ℂ => (Nat.card L : ℂ) * z) he
  simp only [← mul_assoc, mul_inv_cancel₀ hcard, one_mul] at hm
  exact_mod_cast hm.symm

include h₁ h₂ hz₁ hz₂ hc in
/-- Dimension one is equivalent to the precise finite index identity. -/
theorem dimension_one_iff :
    Module.finrank ℂ (IntertwiningMap ρ σ) = 1 ↔
      Module.finrank ℂ W * Module.finrank ℂ U * Nat.card (H₁ ⊓ H₂ : Subgroup L) =
        Nat.card L := by
  have he := dimension_formula ρ σ H₁ H₂ θ₁ θ₂ h₁ h₂ hz₁ hz₂ hc
  constructor
  · intro h; simpa [h] using he.symm
  · intro h
    have hp := Nat.card_pos (α := L)
    have : Nat.card L * Module.finrank ℂ (IntertwiningMap ρ σ) = Nat.card L * 1 := by
      exact he.trans (h.trans (Nat.mul_one _).symm)
    exact Nat.eq_of_mul_eq_mul_left hp this

end PaperXI.CharacterPairing108
