import PaperXI.CliffordMultiplicity
import PaperXI.CliffordEvaluation
import PaperXI.TensorSubspace

/-! Canonical evaluation and irreducibility on the actual Clifford
multiplicity space. All finite dimensions and tensor-image properties are
derived from the finite-group irreducibles and genuine module isotypy. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordIrreducible
open CliffordDatum CliffordMultiplicity
open scoped TensorProduct

variable {G W X : Type*} [Group G] [Finite G]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]
variable (N : Subgroup G)
variable (ρ : Representation ℂ N W) (π : Representation ℂ G X)
variable [Representation.IsIrreducible ρ] [Representation.IsIrreducible π]

/-- The isotypic source condition on the actual restricted group-algebra module. -/
abbrev Isotypic : Prop :=
  IsIsotypicOfType (MonoidAlgebra ℂ N) (restriction N π).asModule ρ.asModule

/-- The actual Hom space has finite dimension, derived from the finite-group actions. -/
theorem multiplicity_finiteDimensional : FiniteDimensional ℂ (Space N ρ π) := by
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional ρ
  let : FiniteDimensional ℂ X := FiniteRepresentation.finiteDimensional π
  infer_instance

/-- Genuine isotypy and the nonzero original representation force nonzero multiplicity. -/
theorem multiplicity_nontrivial (h : Isotypic N ρ π) : Nontrivial (Space N ρ π) := by
  let : FiniteDimensional ℂ X := FiniteRepresentation.finiteDimensional π
  let : Nontrivial X := GeneratedIrreducibility.nontrivial_space π
  exact CliffordEvaluation.multiplicity_nontrivial ρ (restriction N π) h

/-- The source evaluation equivalence, with its bijectivity proved from isotypy. -/
def evaluation (h : Isotypic N ρ π) : W ⊗[ℂ] Space N ρ π ≃ₗ[ℂ] X := by
  let : FiniteDimensional ℂ X := FiniteRepresentation.finiteDimensional π
  exact CliffordEvaluation.equiv ρ (restriction N π) h

@[simp] theorem evaluation_tmul (h : Isotypic N ρ π) (w : W) (f : Space N ρ π) :
    evaluation N ρ π h (w ⊗ₜ[ℂ] f) = f w := rfl

variable [N.Normal]

/-- The literal section action factors through the proved canonical evaluation. -/
theorem section_action (h : Isotypic N ρ π) (hρ : Invariant N ρ)
    (a : G ⧸ N) (t : W ⊗[ℂ] Space N ρ π) :
    π (sectionMap N a) (evaluation N ρ π h t) =
      evaluation N ρ π h (TensorProduct.map
        (sectionIntertwiner N ρ hρ a).toLinearMap
        (sectionOperator N ρ π hρ a).toLinearMap t) := by
  induction t using TensorProduct.induction_on with
  | zero => simp
  | add s t hs ht => simp [hs, ht]
  | tmul w f =>
    simp only [TensorProduct.map_tmul, evaluation_tmul]
    change π (sectionMap N a) (f w) =
      π (sectionMap N a) (f ((sectionIntertwiner N ρ hρ a).symm
        (sectionIntertwiner N ρ hρ a w)))
    rw [Representation.Equiv.symm_apply_apply]

/-- The actual group normal form gives the factorwise action needed for every g. -/
theorem group_action (h : Isotypic N ρ π) (hρ : Invariant N ρ)
    (g : G) (w : W) (f : Space N ρ π) :
    π g (evaluation N ρ π h (w ⊗ₜ[ℂ] f)) =
      evaluation N ρ π h
        (ρ (coordinate N g) (sectionIntertwiner N ρ hρ (QuotientGroup.mk' N g) w) ⊗ₜ[ℂ]
          sectionOperator N ρ π hρ (QuotientGroup.mk' N g) f) := by
  rw [evaluation_tmul, evaluation_tmul, space_intertwines]
  change π g (f w) = π (coordinate N g : G)
    (π (sectionMap N (QuotientGroup.mk' N g))
      (f ((sectionIntertwiner N ρ hρ (QuotientGroup.mk' N g)).symm
        (sectionIntertwiner N ρ hρ (QuotientGroup.mk' N g) w))))
  rw [Representation.Equiv.symm_apply_apply]
  change π g (f w) = (π (coordinate N g : G) * π (sectionMap N (QuotientGroup.mk' N g))) (f w)
  rw [← map_mul, ← normal_form]

/-- The projective multiplicity action is actually irreducible. -/
theorem irreducible (h : Isotypic N ρ π) (hρ : Invariant N ρ)
    (L : Submodule ℂ (Space N ρ π))
    (hL : ∀ a f, f ∈ L → sectionOperator N ρ π hρ a f ∈ L) :
    L = ⊥ ∨ L = ⊤ := by
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional ρ
  let : FiniteDimensional ℂ (Space N ρ π) := multiplicity_finiteDimensional N ρ π
  let : Nontrivial W := GeneratedIrreducibility.nontrivial_space ρ
  let E := evaluation N ρ π h
  have hs : RepresentationStability.Stable π (TensorSubspace.image E L) := by
    intro g
    exact TensorSubspace.image_stable E L (π g)
      ((ρ (coordinate N g)).comp (sectionIntertwiner N ρ hρ (QuotientGroup.mk' N g)).toLinearMap)
      (sectionOperator N ρ π hρ (QuotientGroup.mk' N g)).toLinearMap
      (hL (QuotientGroup.mk' N g)) (group_action N ρ π h hρ g)
  rcases RepresentationStability.eq_bot_or_top π (TensorSubspace.image E L) hs with hb | ht
  · exact Or.inl ((TensorSubspace.image_eq_bot_iff E L).mp hb)
  · exact Or.inr ((TensorSubspace.image_eq_top_iff E L).mp ht)

end PaperXI.CliffordIrreducible
