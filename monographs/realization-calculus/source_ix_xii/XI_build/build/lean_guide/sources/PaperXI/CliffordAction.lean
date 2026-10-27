import PaperXI.CliffordIrreducible
import PaperXI.CliffordChoices

/-! The full Clifford choice comparison and irreducibility for every
section, intertwiner family, and equivariant tensor identification. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordAction
open CliffordDatum CliffordMultiplicity CliffordIrreducible
open scoped TensorProduct

variable {G W X : Type*} [Group G] [Finite G]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]
variable (N : Subgroup G) [N.Normal]
variable (ρ : Representation ℂ N W) (π : Representation ℂ G X)
variable [Representation.IsIrreducible ρ] [Representation.IsIrreducible π]
variable (h : Isotypic N ρ π) (hρ : Invariant N ρ)
variable (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
variable (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a)))
variable (E : W ⊗[ℂ] Space N ρ π ≃ₗ[ℂ] X)
variable (hE : ∀ (n : N) (w : W) (f : Space N ρ π),
  E ((ρ n w) ⊗ₜ[ℂ] f) = π (n : G) (E (w ⊗ₜ[ℂ] f)))
variable (T : G ⧸ N → Module.End ℂ (Space N ρ π))
variable (hT : ∀ (a : G ⧸ N) (w : W) (f : Space N ρ π),
  E ((I a w) ⊗ₜ[ℂ] T a f) = π (s a) (E (w ⊗ₜ[ℂ] f)))

include h hρ s hs I E hE T hT

/-- All three Clifford choices are compared simultaneously with the constructed
canonical action. The tensor equivalence on the right is proved from isotypy. -/
theorem all_choices :
    ∃ (L : Space N ρ π ≃ₗ[ℂ] Space N ρ π) (γ : G ⧸ N → ℂˣ),
      (∀ (w : W) (f : Space N ρ π),
        E (w ⊗ₜ[ℂ] f) = evaluation N ρ π h (w ⊗ₜ[ℂ] L f)) ∧
      ∀ (a : G ⧸ N) (f : Space N ρ π),
        T a f = (γ a : ℂ) • L.symm (sectionOperator N ρ π hρ a (L f)) := by
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional ρ
  let : FiniteDimensional ℂ X := FiniteRepresentation.finiteDimensional π
  let L := CliffordEvaluation.choiceEquiv ρ (restriction N π) E hE
  let γ := CliffordChoices.choiceCochain N ρ hρ s hs I
  refine ⟨L, γ, ?_, ?_⟩
  · intro w f
    rfl
  · intro a f
    have ht := CliffordEvaluation.choice_operator_conjugation N π ρ (s a) (I a)
      E hE (T a) (hT a) f
    have hc := LinearMap.congr_fun (CliffordChoices.arbitrary_choices N ρ π hρ s hs I a) (L f)
    change operator N ρ π (s a) (I a) (L f) =
      (γ a : ℂ) • sectionOperator N ρ π hρ a (L f) at hc
    change T a f = L.symm (operator N ρ π (s a) (I a) (L f)) at ht
    rw [ht, hc, map_smul]

/-- Every action obtained from any of the three choices is irreducible on
the actual multiplicity space. No invertibility of the alternative operators
or multiplicity dimension is assumed. -/
theorem irreducible_all_choices (S : Submodule ℂ (Space N ρ π))
    (hS : ∀ a f, f ∈ S → T a f ∈ S) : S = ⊥ ∨ S = ⊤ := by
  obtain ⟨L, γ, _, hcomp⟩ := all_choices N ρ π h hρ s hs I E hE T hT
  let P : Submodule ℂ (Space N ρ π) := S.map L.toLinearMap
  have hP (a : G ⧸ N) (f : Space N ρ π) (hf : f ∈ P) :
      sectionOperator N ρ π hρ a f ∈ P := by
    obtain ⟨g, hg, rfl⟩ := hf
    have heq : L (T a g) = (γ a : ℂ) • sectionOperator N ρ π hρ a (L g) := by
      rw [hcomp, map_smul, LinearEquiv.apply_symm_apply]
    refine ⟨(((γ a)⁻¹ : ℂˣ) : ℂ) • T a g, S.smul_mem _ (hS a g hg), ?_⟩
    change L ((((γ a)⁻¹ : ℂˣ) : ℂ) • T a g) = sectionOperator N ρ π hρ a (L g)
    rw [map_smul, heq, smul_smul]
    simp
  rcases CliffordIrreducible.irreducible N ρ π h hρ P hP with hb | ht
  · left
    apply le_antisymm _ bot_le
    intro f hf
    change f = 0
    apply L.injective
    have hm : L f ∈ P := ⟨f, hf, rfl⟩
    rw [hb] at hm
    change L f = 0 at hm
    exact hm.trans L.map_zero.symm
  · right
    apply top_unique
    intro f _
    have hm : L f ∈ P := ht ▸ (show L f ∈ (⊤ : Submodule ℂ (Space N ρ π)) from trivial)
    obtain ⟨g, hg, hgf⟩ := hm
    exact L.injective hgf ▸ hg

end PaperXI.CliffordAction
