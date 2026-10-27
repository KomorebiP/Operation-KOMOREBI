import PaperXI.HeisenbergTrace108
import PaperXI.CharacterPairing108
import PaperXI.FiniteJointQuotient108
import Mathlib.GroupTheory.Index

/-! Bounded auxiliary results for the next finite-profile bridge. These prove
generic algebraic descent prerequisites, not the actual simple-character
profile or the BK lattice-index equality. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteProfileBridge109
open Representation

variable {K W : Type*} [Group K] [AddCommGroup W] [Module ℂ W]
  [FiniteDimensional ℂ W]

/-- Positive degree and vanishing off H force the action kernel into H.
No scalar restriction or irreducibility is needed for this implication. -/
theorem kernel_le_of_trace_support
    (ρ : Representation ℂ K W) (H : Subgroup K)
    (hd : 0 < Module.finrank ℂ W)
    (hz : ∀ x : K, x ∉ H → ρ.character x = 0) : ρ.ker ≤ H := by
  intro x hx
  by_contra h
  have he : ρ.character x = (Module.finrank ℂ W : ℂ) := by
    simp [Representation.character, MonoidHom.mem_ker.mp hx]
  have hdim : (Module.finrank ℂ W : ℂ) ≠ 0 := by
    exact_mod_cast hd.ne'
  exact hdim (he.symm.trans (hz x h))

/-- A scalar character is trivial on elements that act identically, provided
the original carrier has positive degree. -/
theorem scalar_character_eq_one_on_kernel
    (ρ : Representation ℂ K W) (H : Subgroup K) (θ : H →* ℂˣ)
    (hd : 0 < Module.finrank ℂ W)
    (hscalar : ∀ h : H, ρ h = (θ h : ℂ) • LinearMap.id)
    (h : H) (hk : (h : K) ∈ ρ.ker) : θ h = 1 := by
  have he := HeisenbergTrace108.character_on_subgroup H θ ρ hscalar h
  have ht : ρ.character h = (Module.finrank ℂ W : ℂ) := by
    simp [Representation.character, MonoidHom.mem_ker.mp hk]
  have hdim : (Module.finrank ℂ W : ℂ) ≠ 0 := by
    exact_mod_cast hd.ne'
  apply Units.ext
  apply mul_left_cancel₀ hdim
  simpa using he.symm.trans ht

/-- Both trace profiles put the actual joint kernel in their intersection. -/
theorem joint_kernel_le
    (ρ σ : Representation ℂ K W) (H₁ H₂ : Subgroup K)
    (hd : 0 < Module.finrank ℂ W)
    (hz₁ : ∀ x : K, x ∉ H₁ → ρ.character x = 0)
    (hz₂ : ∀ x : K, x ∉ H₂ → σ.character x = 0) :
    FiniteJointQuotient108.kernel ρ σ ≤ H₁ ⊓ H₂ := by
  exact inf_le_inf (kernel_le_of_trace_support ρ H₁ hd hz₁)
    (kernel_le_of_trace_support σ H₂ hd hz₂)

variable {Q : Type*} [Group Q]

/-- The actual image map of a scalar subgroup. -/
def imageMap (q : K →* Q) (H : Subgroup K) : H →* H.map q where
  toFun h := ⟨q h, Subgroup.mem_map_of_mem q h.property⟩
  map_one' := Subtype.ext (map_one q)
  map_mul' a b := Subtype.ext (map_mul q (a : K) (b : K))

theorem imageMap_surjective (q : K →* Q) (H : Subgroup K) :
    Function.Surjective (imageMap q H) := by
  rintro ⟨x, hx⟩
  obtain ⟨p, hp, rfl⟩ := hx
  exact ⟨⟨p, hp⟩, rfl⟩

/-- Positive degree makes a scalar character factor through the actual image
of any quotient map through which the representation already factors. -/
theorem imageMap_kernel_le_character_kernel
    (q : K →* Q) (ρ : Representation ℂ Q W)
    (H : Subgroup K) (θ : H →* ℂˣ)
    (hd : 0 < Module.finrank ℂ W)
    (hscalar : ∀ h : H, (ρ.comp q) h = (θ h : ℂ) • LinearMap.id) :
    (imageMap q H).ker ≤ θ.ker := by
  intro h hh
  have he : q (h : K) = 1 := congrArg Subtype.val (MonoidHom.mem_ker.mp hh)
  have hk : (h : K) ∈ (ρ.comp q).ker := by
    apply MonoidHom.mem_ker.mpr
    change ρ (q (h : K)) = 1
    simp [he]
  exact MonoidHom.mem_ker.mpr
    (scalar_character_eq_one_on_kernel (ρ.comp q) H θ hd hscalar h hk)

/-- Character descent onto the named subgroup H.map q, rather than onto a
different finite quotient or an unrelated isomorphic subgroup. -/
def imageCharacter (q : K →* Q) (H : Subgroup K) (θ : H →* ℂˣ)
    (hθ : (imageMap q H).ker ≤ θ.ker) : H.map q →* ℂˣ :=
  (imageMap q H).liftOfSurjective (imageMap_surjective q H) ⟨θ, hθ⟩

@[simp] theorem imageCharacter_apply (q : K →* Q) (H : Subgroup K) (θ : H →* ℂˣ)
    (hθ : (imageMap q H).ker ≤ θ.ker) (h : H) :
    imageCharacter q H θ hθ (imageMap q H h) = θ h := by
  exact (imageMap q H).liftOfRightInverse_comp_apply
    (Function.surjInv (imageMap_surjective q H))
    (Function.rightInverse_surjInv (imageMap_surjective q H)) ⟨θ, hθ⟩ h

omit [FiniteDimensional ℂ W] in
theorem image_scalar (q : K →* Q) (ρ : Representation ℂ Q W)
    (H : Subgroup K) (θ : H →* ℂˣ)
    (hθ : (imageMap q H).ker ≤ θ.ker)
    (hscalar : ∀ h : H, (ρ.comp q) h = (θ h : ℂ) • LinearMap.id)
    (h : H.map q) :
    ρ h = (imageCharacter q H θ hθ h : ℂ) • LinearMap.id := by
  obtain ⟨p, rfl⟩ := imageMap_surjective q H h
  rw [imageCharacter_apply]
  exact hscalar p

omit [FiniteDimensional ℂ W] in
theorem image_trace_zero (q : K →* Q) (hq : Function.Surjective q)
    (ρ : Representation ℂ Q W) (H : Subgroup K)
    (hz : ∀ x : K, x ∉ H → Representation.character (ρ.comp q) x = 0)
    (x : Q) (hx : x ∉ H.map q) : ρ.character x = 0 := by
  obtain ⟨p, rfl⟩ := hq x
  exact hz p (fun hp => hx (Subgroup.mem_map_of_mem q hp))

theorem image_intersection (q : K →* Q) (hq : Function.Surjective q)
    (H₁ H₂ : Subgroup K) (hk₁ : q.ker ≤ H₁) (hk₂ : q.ker ≤ H₂) :
    (H₁ ⊓ H₂).map q = H₁.map q ⊓ H₂.map q := by
  apply Subgroup.comap_injective hq
  rw [Subgroup.comap_inf, Subgroup.comap_map_eq_self hk₁,
    Subgroup.comap_map_eq_self hk₂,
    Subgroup.comap_map_eq_self (le_inf hk₁ hk₂)]

/-- The finite image subgroup has the same index as the original subgroup;
no cardinality of the original possibly infinite group is used. -/
theorem image_index (q : K →* Q) (hq : Function.Surjective q)
    (H : Subgroup K) (hk : q.ker ≤ H) : (H.map q).index = H.index := by
  rw [← (H.map q).index_comap_of_surjective hq, Subgroup.comap_map_eq_self hk]

theorem image_characters_compatible (q : K →* Q) (hq : Function.Surjective q)
    (H₁ H₂ : Subgroup K) (θ₁ : H₁ →* ℂˣ) (θ₂ : H₂ →* ℂˣ)
    (hk₁ : q.ker ≤ H₁) (hk₂ : q.ker ≤ H₂)
    (ht₁ : (imageMap q H₁).ker ≤ θ₁.ker)
    (ht₂ : (imageMap q H₂).ker ≤ θ₂.ker)
    (hc : ∀ p : K, ∀ h₁ : p ∈ H₁, ∀ h₂ : p ∈ H₂,
      θ₁ ⟨p, h₁⟩ = θ₂ ⟨p, h₂⟩) :
    ∀ x : Q, ∀ h₁ : x ∈ H₁.map q, ∀ h₂ : x ∈ H₂.map q,
      imageCharacter q H₁ θ₁ ht₁ ⟨x, h₁⟩ =
        imageCharacter q H₂ θ₂ ht₂ ⟨x, h₂⟩ := by
  intro x hx₁ hx₂
  obtain ⟨p, rfl⟩ := hq x
  have hp₁ : p ∈ H₁ := by
    have : p ∈ (H₁.map q).comap q := hx₁
    rwa [Subgroup.comap_map_eq_self hk₁] at this
  have hp₂ : p ∈ H₂ := by
    have : p ∈ (H₂.map q).comap q := hx₂
    rwa [Subgroup.comap_map_eq_self hk₂] at this
  change imageCharacter q H₁ θ₁ ht₁ (imageMap q H₁ ⟨p, hp₁⟩) =
    imageCharacter q H₂ θ₂ ht₂ (imageMap q H₂ ⟨p, hp₂⟩)
  rw [imageCharacter_apply, imageCharacter_apply]
  exact hc p hp₁ hp₂

omit [FiniteDimensional ℂ W] in
theorem quotient_kernel_le_action_kernel (q : K →* Q) (ρ : Representation ℂ Q W) :
    q.ker ≤ (ρ.comp q).ker := by
  intro p hp
  apply MonoidHom.mem_ker.mpr
  change ρ (q p) = 1
  simp [MonoidHom.mem_ker.mp hp]

/-- The finite criterion can be fed only profiles on the original actions.
All subgroup-image, character-descent, and compatibility obligations are
discharged generically; the actual profiles and index identity remain inputs. -/
theorem dimension_one_iff_of_original_profiles [Fintype Q]
    (q : K →* Q) (hq : Function.Surjective q)
    (ρ σ : Representation ℂ Q W)
    (H₁ H₂ : Subgroup K) (θ₁ : H₁ →* ℂˣ) (θ₂ : H₂ →* ℂˣ)
    (hd : 0 < Module.finrank ℂ W)
    (h₁ : ∀ h : H₁, (ρ.comp q) h = (θ₁ h : ℂ) • LinearMap.id)
    (h₂ : ∀ h : H₂, (σ.comp q) h = (θ₂ h : ℂ) • LinearMap.id)
    (hz₁ : ∀ p : K, p ∉ H₁ → Representation.character (ρ.comp q) p = 0)
    (hz₂ : ∀ p : K, p ∉ H₂ → Representation.character (σ.comp q) p = 0)
    (hc : ∀ p : K, ∀ h₁ : p ∈ H₁, ∀ h₂ : p ∈ H₂,
      θ₁ ⟨p, h₁⟩ = θ₂ ⟨p, h₂⟩) :
    Module.finrank ℂ (IntertwiningMap ρ σ) = 1 ↔
      Module.finrank ℂ W * Module.finrank ℂ W * Nat.card ((H₁ ⊓ H₂).map q) =
        Nat.card Q := by
  have hk₁ : q.ker ≤ H₁ := (quotient_kernel_le_action_kernel q ρ).trans
    (kernel_le_of_trace_support (ρ.comp q) H₁ hd hz₁)
  have hk₂ : q.ker ≤ H₂ := (quotient_kernel_le_action_kernel q σ).trans
    (kernel_le_of_trace_support (σ.comp q) H₂ hd hz₂)
  have ht₁ := imageMap_kernel_le_character_kernel q ρ H₁ θ₁ hd h₁
  have ht₂ := imageMap_kernel_le_character_kernel q σ H₂ θ₂ hd h₂
  have he := CharacterPairing108.dimension_one_iff ρ σ (H₁.map q) (H₂.map q)
    (imageCharacter q H₁ θ₁ ht₁) (imageCharacter q H₂ θ₂ ht₂)
    (image_scalar q ρ H₁ θ₁ ht₁ h₁) (image_scalar q σ H₂ θ₂ ht₂ h₂)
    (image_trace_zero q hq ρ H₁ hz₁) (image_trace_zero q hq σ H₂ hz₂)
    (image_characters_compatible q hq H₁ H₂ θ₁ θ₂ hk₁ hk₂ ht₁ ht₂ hc)
  rwa [← image_intersection q hq H₁ H₂ hk₁ hk₂] at he

end PaperXI.FiniteProfileBridge109
