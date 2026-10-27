import PaperXI.GeneratedIrreducibility

/-! An explicit invariant-subspace criterion for actual irreducibility. This
interface keeps the nonzero-space condition when comparing group actions and
algebra actions. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.RepresentationStability

variable {k G W : Type*} [Field k] [Group G] [AddCommGroup W] [Module k W]

/-- Invariance under every actual group operator. -/
def Stable (ρ : Representation k G W) (S : Submodule k W) : Prop :=
  ∀ g w, w ∈ S → ρ g w ∈ S

/-- Every stable subspace in an irreducible representation is zero or the whole space. -/
theorem eq_bot_or_top (ρ : Representation k G W) [Representation.IsIrreducible ρ]
    (S : Submodule k W) (hS : Stable ρ S) : S = ⊥ ∨ S = ⊤ := by
  let T : Subrepresentation ρ := ⟨S, hS⟩
  rcases eq_bot_or_eq_top T with h | h
  · exact Or.inl (congrArg Subrepresentation.toSubmodule h)
  · exact Or.inr (congrArg Subrepresentation.toSubmodule h)

/-- The stable-subspace condition together with nontriviality proves irreducibility. -/
theorem irreducible_of_stable (ρ : Representation k G W) [Nontrivial W]
    (h : ∀ S : Submodule k W, Stable ρ S → S = ⊥ ∨ S = ⊤) :
    Representation.IsIrreducible ρ := by
  let : Nontrivial (Subrepresentation ρ) :=
    ⟨⟨⊥, ⊤, fun heq => bot_ne_top (congrArg Subrepresentation.toSubmodule heq)⟩⟩
  refine ⟨fun S => ?_⟩
  rcases h S.toSubmodule S.apply_mem_toSubmodule with hS | hS
  · exact Or.inl (Subrepresentation.toSubmodule_injective hS)
  · exact Or.inr (Subrepresentation.toSubmodule_injective hS)

/-- No zero representation is hidden in the invariant-subspace formulation. -/
theorem irreducible_iff (ρ : Representation k G W) :
    Representation.IsIrreducible ρ ↔ Nontrivial W ∧
      ∀ S : Submodule k W, Stable ρ S → S = ⊥ ∨ S = ⊤ := by
  constructor
  · intro h
    let : Representation.IsIrreducible ρ := h
    exact ⟨GeneratedIrreducibility.nontrivial_space ρ, eq_bot_or_top ρ⟩
  · rintro ⟨hW, h⟩
    let : Nontrivial W := hW
    exact irreducible_of_stable ρ h

end PaperXI.RepresentationStability
