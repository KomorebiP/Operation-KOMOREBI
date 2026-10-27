import PaperXI.CliffordChoices

/-! The Clifford cocycle is extracted from the literal multiplicity action.
The scalar on the multiplicity space is the inverse of the Schur scalar
comparing the subgroup intertwiners. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordCocycle
open CliffordDatum CliffordMultiplicity CliffordChoices CocycleCommutator
open scoped IsMulCommutative

variable {G W X : Type*} [Group G]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]

/-- The unique Schur scalar for the actual subgroup-valued section defect. -/
def scalar (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    [Representation.IsIrreducible ρ] [FiniteDimensional ℂ W]
    (hρ : Invariant N ρ) (a b : G ⧸ N) : ℂˣ :=
  intertwinerScalar N ρ (sectionMap N a * sectionMap N b)
    (defectIntertwiner N ρ hρ a b)
    (productIntertwiner N ρ (sectionMap N a) (sectionMap N b)
      (sectionIntertwiner N ρ hρ a) (sectionIntertwiner N ρ hρ b))

/-- The scalar convention on the original irreducible representation. -/
theorem scalar_spec (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    [Representation.IsIrreducible ρ] [FiniteDimensional ℂ W]
    (hρ : Invariant N ρ) (a b : G ⧸ N) (w : W) :
    sectionIntertwiner N ρ hρ a (sectionIntertwiner N ρ hρ b w) =
      (scalar N ρ hρ a b : ℂ) •
        ρ (defect N a b) (sectionIntertwiner N ρ hρ (a * b) w) :=
  intertwinerScalar_spec N ρ (sectionMap N a * sectionMap N b)
    (defectIntertwiner N ρ hρ a b)
    (productIntertwiner N ρ (sectionMap N a) (sectionMap N b)
      (sectionIntertwiner N ρ hρ a) (sectionIntertwiner N ρ hρ b)) w

/-- The actual defect-adjusted multiplicity operator cancels to the operator
at the product quotient element. -/
theorem operator_defect (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (hρ : Invariant N ρ) (a b : G ⧸ N) :
    operator N ρ π (sectionMap N a * sectionMap N b) (defectIntertwiner N ρ hρ a b) =
      sectionOperator N ρ π hρ (a * b) := by
  have h := operator_subgroup_mul N ρ π (defect N a b) (sectionMap N (a * b))
    (sectionIntertwiner N ρ hρ (a * b))
  ext f w
  have hh := congrArg (fun e : Space N ρ π ≃ₗ[ℂ] Space N ρ π => e f w) h
  change π ((defect N a b : G) * sectionMap N (a * b))
    (f ((sectionIntertwiner N ρ hρ (a * b)).symm (ρ (defect N a b)⁻¹ w))) = _ at hh
  rw [← section_mul] at hh
  exact hh

/-- The inverse scalar law is proved on the literal `Hom_N` operators. -/
theorem sectionOperator_mul (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    [Representation.IsIrreducible ρ] [FiniteDimensional ℂ W]
    (π : Representation ℂ G X) (hρ : Invariant N ρ) (a b : G ⧸ N) :
    (sectionOperator N ρ π hρ a).toLinearMap * (sectionOperator N ρ π hρ b).toLinearMap =
      (((scalar N ρ hρ a b)⁻¹ : ℂˣ) : ℂ) •
        (sectionOperator N ρ π hρ (a * b)).toLinearMap := by
  rw [sectionOperator, sectionOperator, operator_product]
  have h := operator_choice N ρ π (sectionMap N a * sectionMap N b)
    (defectIntertwiner N ρ hρ a b)
    (productIntertwiner N ρ (sectionMap N a) (sectionMap N b)
      (sectionIntertwiner N ρ hρ a) (sectionIntertwiner N ρ hρ b))
  rw [operator_defect] at h
  exact h

/-- An invertible multiplicity operator is nonzero on a nonzero multiplicity space. -/
theorem sectionOperator_ne_zero (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (hρ : Invariant N ρ) [Nontrivial (Space N ρ π)]
    (a : G ⧸ N) : (sectionOperator N ρ π hρ a).toLinearMap ≠ 0 := by
  intro h
  obtain ⟨f, hf⟩ := exists_ne (0 : Space N ρ π)
  have hz := LinearMap.congr_fun h f
  exact hf ((sectionOperator N ρ π hρ a).injective
    (hz.trans (sectionOperator N ρ π hρ a).map_zero.symm))

/-- The actual scalar cocycle; associativity is derived from multiplication on `Hom_N`. -/
def cocycle (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)]
    (ρ : Representation ℂ N W) [Representation.IsIrreducible ρ] [FiniteDimensional ℂ W]
    (π : Representation ℂ G X) (hρ : Invariant N ρ) [Nontrivial (Space N ρ π)] :
    Cocycle (G ⧸ N) ℂˣ :=
  ProjectiveCocycle.cocycle (fun a => (sectionOperator N ρ π hρ a).toLinearMap)
    (sectionOperator_ne_zero N ρ π hρ) (fun a b => (scalar N ρ hρ a b)⁻¹)
    (sectionOperator_mul N ρ π hρ)

@[simp] theorem cocycle_coeff (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)]
    (ρ : Representation ℂ N W) [Representation.IsIrreducible ρ] [FiniteDimensional ℂ W]
    (π : Representation ℂ G X) (hρ : Invariant N ρ) [Nontrivial (Space N ρ π)]
    (a b : G ⧸ N) : (cocycle N ρ π hρ).coeff a b = (scalar N ρ hρ a b)⁻¹ := rfl

/-- Both normalizations follow from the normalized actual quotient operators. -/
theorem normalized (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)]
    (ρ : Representation ℂ N W) [Representation.IsIrreducible ρ] [FiniteDimensional ℂ W]
    (π : Representation ℂ G X) (hρ : Invariant N ρ) [Nontrivial (Space N ρ π)] :
    Normalized (cocycle N ρ π hρ) := by
  apply ProjectiveCocycle.normalized
  exact congrArg LinearEquiv.toLinearMap (sectionOperator_one N ρ π hρ)

end PaperXI.CliffordCocycle
