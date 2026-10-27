import PaperXI.CliffordMultiplicity
import PaperXI.ProjectiveCocycle

/-! Choice comparisons on the literal Clifford multiplicity operators.
The comparing scalar is derived from Schur's lemma. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordChoices
open CliffordDatum CliffordMultiplicity

variable {G W X : Type*} [Group G]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]

/-- Changing a chosen subgroup intertwiner changes the actual Hom operator by
its inverse scalar, with that inverse forced by the literal formula. -/
theorem operator_rescale (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (g : G)
    (I J : Representation.Equiv ρ (conjugate N ρ g))
    (μ : ℂˣ) (hμ : ∀ w, J w = (μ : ℂ) • I w) :
    (operator N ρ π g J).toLinearMap =
      ((μ⁻¹ : ℂˣ) : ℂ) • (operator N ρ π g I).toLinearMap := by
  have hinv (w : W) : J.symm w = ((μ⁻¹ : ℂˣ) : ℂ) • I.symm w := by
    apply J.injective
    change J (J.symm w) = J (((μ⁻¹ : ℂˣ) : ℂ) • I.symm w)
    rw [J.apply_symm_apply, map_smul, hμ, I.apply_symm_apply, smul_smul]
    simp
  ext f w
  change π g (f (J.symm w)) = ((μ⁻¹ : ℂˣ) : ℂ) • π g (f (I.symm w))
  rw [hinv, map_smul, map_smul]

/-- Any two actual conjugation intertwiners differ by a unique unit scalar. -/
theorem existsUnique_intertwiner_scalar (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) [Representation.IsIrreducible ρ]
    [FiniteDimensional ℂ W] (g : G)
    (I J : Representation.Equiv ρ (conjugate N ρ g)) :
    ∃! μ : ℂˣ, ∀ w, J w = (μ : ℂ) • I w := by
  apply SchurScalar.bridge_unique ρ (conjugate N ρ g) I.toLinearEquiv J.toLinearEquiv
  · intro n w
    exact Representation.IntertwiningMap.isIntertwining ρ (conjugate N ρ g)
      I.toIntertwiningMap n w
  · intro n w
    exact Representation.IntertwiningMap.isIntertwining ρ (conjugate N ρ g)
      J.toIntertwiningMap n w

/-- The actual scalar comparing arbitrary choices, chosen from its proved uniqueness. -/
def intertwinerScalar (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) [Representation.IsIrreducible ρ]
    [FiniteDimensional ℂ W] (g : G)
    (I J : Representation.Equiv ρ (conjugate N ρ g)) : ℂˣ :=
  Classical.choose (existsUnique_intertwiner_scalar N ρ g I J)

theorem intertwinerScalar_spec (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) [Representation.IsIrreducible ρ]
    [FiniteDimensional ℂ W] (g : G)
    (I J : Representation.Equiv ρ (conjugate N ρ g)) (w : W) :
    J w = (intertwinerScalar N ρ g I J : ℂ) • I w :=
  (Classical.choose_spec (existsUnique_intertwiner_scalar N ρ g I J)).1 w

/-- The unit scalar comparison of actual multiplicity operators is derived,
rather than required as a hypothesis on alternative choices. -/
theorem operator_choice (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) [Representation.IsIrreducible ρ]
    [FiniteDimensional ℂ W] (π : Representation ℂ G X) (g : G)
    (I J : Representation.Equiv ρ (conjugate N ρ g)) :
    (operator N ρ π g J).toLinearMap =
      (((intertwinerScalar N ρ g I J)⁻¹ : ℂˣ) : ℂ) • (operator N ρ π g I).toLinearMap := by
  exact operator_rescale N ρ π g I J (intertwinerScalar N ρ g I J)
    (intertwinerScalar_spec N ρ g I J)


/-- The actual subgroup factor relating any representative of `a` to the chosen one. -/
def representativeFactor (N : Subgroup G) [N.Normal] (a : G ⧸ N) (g : G)
    (hg : QuotientGroup.mk' N g = a) : N :=
  ⟨g * (sectionMap N a)⁻¹, by
    apply (QuotientGroup.eq_one_iff _).mp
    change (QuotientGroup.mk' N) (g * (sectionMap N a)⁻¹) = 1
    rw [map_mul, map_inv, hg, quotient_section, mul_inv_cancel]⟩

theorem representative_factorization (N : Subgroup G) [N.Normal]
    (a : G ⧸ N) (g : G) (hg : QuotientGroup.mk' N g = a) :
    g = (representativeFactor N a g hg : G) * sectionMap N a := by
  simp [representativeFactor, mul_assoc]

/-- The section intertwiner adjusted by the actual subgroup representative factor. -/
def representativeIntertwiner (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) (hρ : Invariant N ρ)
    (a : G ⧸ N) (g : G) (hg : QuotientGroup.mk' N g = a) :
    Representation.Equiv ρ (conjugate N ρ g) :=
  Representation.Equiv.mk
    (subgroupIntertwiner N ρ (representativeFactor N a g hg) (sectionMap N a)
      (sectionIntertwiner N ρ hρ a)).toLinearEquiv (by
    intro n
    apply LinearMap.ext
    intro w
    have h := intertwiner_apply N ρ
      ((representativeFactor N a g hg : G) * sectionMap N a)
      (subgroupIntertwiner N ρ (representativeFactor N a g hg) (sectionMap N a)
        (sectionIntertwiner N ρ hρ a)) n w
    simp only [subgroupIntertwiner_apply] at h
    rw [← representative_factorization] at h
    exact h)

@[simp] theorem representativeIntertwiner_apply (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) (hρ : Invariant N ρ)
    (a : G ⧸ N) (g : G) (hg : QuotientGroup.mk' N g = a) (w : W) :
    representativeIntertwiner N ρ hρ a g hg w =
      ρ (representativeFactor N a g hg) (sectionIntertwiner N ρ hρ a w) := rfl

/-- The subgroup correction cancels on the actual multiplicity space. -/
theorem operator_representative (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) (π : Representation ℂ G X) (hρ : Invariant N ρ)
    (a : G ⧸ N) (g : G) (hg : QuotientGroup.mk' N g = a) :
    operator N ρ π g (representativeIntertwiner N ρ hρ a g hg) =
      sectionOperator N ρ π hρ a := by
  have h := operator_subgroup_mul N ρ π (representativeFactor N a g hg)
    (sectionMap N a) (sectionIntertwiner N ρ hρ a)
  ext f w
  have hh := congrArg (fun e : Space N ρ π ≃ₗ[ℂ] Space N ρ π => e f w) h
  change π ((representativeFactor N a g hg : G) * sectionMap N a)
    (f ((sectionIntertwiner N ρ hρ a).symm (ρ (representativeFactor N a g hg)⁻¹ w))) = _ at hh
  rw [← representative_factorization] at hh
  exact hh

/-- The inverse cochain comparing an arbitrary quotient section and arbitrary
conjugation intertwiners to the normalized baseline. -/
def choiceCochain (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) [Representation.IsIrreducible ρ]
    [FiniteDimensional ℂ W] (hρ : Invariant N ρ)
    (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
    (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a))) (a : G ⧸ N) : ℂˣ :=
  (intertwinerScalar N ρ (s a) (representativeIntertwiner N ρ hρ a (s a) (hs a)) (I a))⁻¹

/-- All actual section and intertwiner choices have the same projective class,
with a constructed inverse cochain. The alternative choices need not be normalized. -/
theorem arbitrary_choices (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) [Representation.IsIrreducible ρ]
    [FiniteDimensional ℂ W] (π : Representation ℂ G X) (hρ : Invariant N ρ)
    (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
    (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a))) (a : G ⧸ N) :
    (operator N ρ π (s a) (I a)).toLinearMap =
      (choiceCochain N ρ hρ s hs I a : ℂ) • (sectionOperator N ρ π hρ a).toLinearMap := by
  have h := operator_choice N ρ π (s a)
    (representativeIntertwiner N ρ hρ a (s a) (hs a)) (I a)
  rw [operator_representative] at h
  exact h

end PaperXI.CliffordChoices

