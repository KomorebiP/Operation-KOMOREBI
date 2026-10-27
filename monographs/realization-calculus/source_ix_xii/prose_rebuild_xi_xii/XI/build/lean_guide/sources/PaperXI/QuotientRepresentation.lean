import Mathlib.RepresentationTheory.Irreducible
import Mathlib.GroupTheory.QuotientGroup.Basic

/-! Actual representation descent through a quotient group and preservation
of irreducibility and intertwining equations under a surjective group map. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.QuotientRepresentation

variable {k G Q V W : Type*} [Field k] [Group G] [Group Q]
variable [AddCommGroup V] [Module k V] [AddCommGroup W] [Module k W]

/-- Surjective pullback preserves precisely the actual stable subspaces. -/
def subrepresentationEquiv (q : G →* Q) (hq : Function.Surjective q)
    (σ : Representation k Q V) :
    Subrepresentation (σ.comp q) ≃o Subrepresentation σ where
  toFun S := ⟨S.toSubmodule, fun a v hv => by
    obtain ⟨g, rfl⟩ := hq a
    exact S.apply_mem_toSubmodule g hv⟩
  invFun S := ⟨S.toSubmodule, fun g _ hv => S.apply_mem_toSubmodule (q g) hv⟩
  left_inv _ := Subrepresentation.toSubmodule_injective rfl
  right_inv _ := Subrepresentation.toSubmodule_injective rfl
  map_rel_iff' := Iff.rfl

theorem irreducible_comp_iff (q : G →* Q) (hq : Function.Surjective q)
    (σ : Representation k Q V) :
    Representation.IsIrreducible (σ.comp q) ↔ Representation.IsIrreducible σ :=
  (subrepresentationEquiv q hq σ).isSimpleOrder_iff

theorem intertwines_comp_iff (q : G →* Q) (hq : Function.Surjective q)
    (ρ : Representation k Q V) (σ : Representation k Q W) (F : V →ₗ[k] W) :
    (∀ g v, F (ρ (q g) v) = σ (q g) (F v)) ↔
      ∀ a v, F (ρ a v) = σ a (F v) := by
  constructor
  · intro h a v
    obtain ⟨g, rfl⟩ := hq a
    exact h g v
  · intro h g v
    exact h (q g) v

/-- Descend the supplied action after proving the actual kernel condition. -/
def descend (N : Subgroup G) [N.Normal] (σ : Representation k G V)
    (hN : N ≤ σ.ker) : Representation k (G ⧸ N) V :=
  QuotientGroup.lift N σ hN

@[simp] theorem descend_apply (N : Subgroup G) [N.Normal] (σ : Representation k G V)
    (hN : N ≤ σ.ker) (g : G) : descend N σ hN (QuotientGroup.mk' N g) = σ g := rfl

@[simp] theorem descend_comp (N : Subgroup G) [N.Normal] (σ : Representation k G V)
    (hN : N ≤ σ.ker) : (descend N σ hN).comp (QuotientGroup.mk' N) = σ := rfl

theorem descend_irreducible_iff (N : Subgroup G) [N.Normal] (σ : Representation k G V)
    (hN : N ≤ σ.ker) :
    Representation.IsIrreducible (descend N σ hN) ↔ Representation.IsIrreducible σ :=
  (irreducible_comp_iff (QuotientGroup.mk' N) QuotientGroup.mk_surjective
    (descend N σ hN)).symm

theorem descend_irreducible (N : Subgroup G) [N.Normal] (σ : Representation k G V)
    (hN : N ≤ σ.ker) [Representation.IsIrreducible σ] :
    Representation.IsIrreducible (descend N σ hN) :=
  (descend_irreducible_iff N σ hN).mpr inferInstance

/-- The quotient action is determined by its evaluation on actual representatives. -/
theorem descend_unique (N : Subgroup G) [N.Normal] (σ : Representation k G V)
    (hN : N ≤ σ.ker) (τ : Representation k (G ⧸ N) V)
    (hτ : ∀ g, τ (QuotientGroup.mk' N g) = σ g) : τ = descend N σ hN := by
  apply MonoidHom.ext
  intro a
  obtain ⟨g, rfl⟩ := QuotientGroup.mk_surjective a
  exact hτ g

end PaperXI.QuotientRepresentation
