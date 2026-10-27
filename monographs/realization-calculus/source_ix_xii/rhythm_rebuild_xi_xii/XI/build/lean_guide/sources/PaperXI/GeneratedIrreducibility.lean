import PaperXI.CyclicAction
import Mathlib.RepresentationTheory.Irreducible

/-! Pass from stability under explicit group generators to Mathlib's actual
representation irreducibility. No orbit-transitivity assumption occurs here. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.GeneratedIrreducibility
variable {K G V : Type*} [Field K] [Group G] [AddCommGroup V] [Module K V]

theorem nontrivial_space (π : Representation K G V) [Representation.IsIrreducible π] :
    Nontrivial V := by
  by_contra h
  have : Subsingleton V := not_nontrivial_iff_subsingleton.mp h
  have hbt : (⊥ : Subrepresentation π) = ⊤ :=
    Subrepresentation.toSubmodule_injective (Subsingleton.elim _ _)
  exact bot_ne_top hbt

/-- The invertible linear action of an actual group element. -/
def actionEquiv (π : Representation K G V) (g : G) : V ≃ₗ[K] V where
  toLinearMap := π g
  invFun := π g⁻¹
  left_inv := π.inv_self_apply g
  right_inv := π.self_inv_apply g

@[simp] theorem actionEquiv_apply (π : Representation K G V) (g : G) (v : V) :
    actionEquiv π g v = π g v := rfl

@[simp] theorem actionEquiv_symm_apply (π : Representation K G V) (g : G) (v : V) :
    (actionEquiv π g).symm v = π g⁻¹ v := rfl

theorem stable_of_generators (π : Representation K G V) (s : Set G)
    (hgen : Submonoid.closure s = ⊤) (S : Submodule K V)
    (hs : ∀ g ∈ s, ∀ v ∈ S, π g v ∈ S) (g : G) {v : V} (hv : v ∈ S) :
    π g v ∈ S := by
  have hg : g ∈ Submonoid.closure s := by rw [hgen]; trivial
  have h : ∀ w ∈ S, π g w ∈ S := by
    induction hg using Submonoid.closure_induction with
    | mem g hg => exact hs g hg
    | one => intro w hw; simpa using hw
    | mul a b _ _ ha hb =>
      intro w hw
      simpa [map_mul, Module.End.mul_apply] using ha (π b w) (hb w hw)
  exact h v hv

/-- Irreducibility is used only through the simple lattice of subrepresentations. -/
theorem eq_bot_or_top (π : Representation K G V) [Representation.IsIrreducible π]
    (s : Set G) (hgen : Submonoid.closure s = ⊤) (S : Submodule K V)
    (hs : ∀ g ∈ s, ∀ v ∈ S, π g v ∈ S) : S = ⊥ ∨ S = ⊤ := by
  let R : Subrepresentation π := ⟨S, fun g _ hv => stable_of_generators π s hgen S hs g hv⟩
  rcases eq_bot_or_eq_top R with h | h
  · exact Or.inl (congrArg Subrepresentation.toSubmodule h)
  · exact Or.inr (congrArg Subrepresentation.toSubmodule h)

end PaperXI.GeneratedIrreducibility
