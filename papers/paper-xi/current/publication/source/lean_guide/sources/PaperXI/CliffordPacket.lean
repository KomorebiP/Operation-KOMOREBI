import PaperXI.CliffordSource
import PaperXI.TwistedActionEquivalence

/-! Source 9.6: the actual Clifford action algebra map is an isomorphism,
and the actual multiplicity dimension is the square root of the quotient order. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordPacket
open CliffordDatum CliffordMultiplicity CliffordIrreducible CocycleCommutator
open scoped IsMulCommutative

variable {G W X : Type*} [Group G] [Finite G]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]
variable (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)] [Fintype (G ⧸ N)]
variable (ρ : Representation ℂ N W) (π : Representation ℂ G X)
variable [Representation.IsIrreducible ρ] [Representation.IsIrreducible π]
variable (h : Isotypic N ρ π) (hρ : Invariant N ρ)

/-- The literal algebra action of the actual Clifford operators. -/
def action :
    TwistedAlgebra.Algebra (CliffordSource.cocycle N ρ π h hρ)
      (CliffordSource.normalized N ρ π h hρ) →ₐ[ℂ] Module.End ℂ (Space N ρ π) :=
  TwistedAction.action _ _ (fun a => (sectionOperator N ρ π hρ a).toLinearMap)
    (congrArg LinearEquiv.toLinearMap (sectionOperator_one N ρ π hρ))
    (CliffordSource.operator_mul N ρ π h hρ)

@[simp] theorem action_basis (a : G ⧸ N) :
    action N ρ π h hρ
      (TwistedAlgebra.basis (CliffordSource.cocycle N ρ π h hρ)
        (CliffordSource.normalized N ρ π h hρ) a) =
      (sectionOperator N ρ π hρ a).toLinearMap :=
  TwistedAction.action_basis _ _ _ _ _ a

variable (hnd : radical (CliffordSource.cocycle N ρ π h hρ) = ⊥)
include hnd

/-- Nondegeneracy makes this actual action map bijective. -/
theorem action_bijective : Function.Bijective (action N ρ π h hρ) := by
  let : Nontrivial (Space N ρ π) := multiplicity_nontrivial N ρ π h
  exact TwistedActionEquivalence.action_bijective _ _ _ _ _ hnd
    (CliffordIrreducible.irreducible N ρ π h hρ)

/-- The source algebra isomorphism is the actual action, not an unrelated matrix identification. -/
def actionEquiv :
    TwistedAlgebra.Algebra (CliffordSource.cocycle N ρ π h hρ)
      (CliffordSource.normalized N ρ π h hρ) ≃ₐ[ℂ] Module.End ℂ (Space N ρ π) :=
  AlgEquiv.ofBijective (action N ρ π h hρ) (action_bijective N ρ π h hρ hnd)

@[simp] theorem actionEquiv_apply
    (x : TwistedAlgebra.Algebra (CliffordSource.cocycle N ρ π h hρ)
      (CliffordSource.normalized N ρ π h hρ)) :
    actionEquiv N ρ π h hρ hnd x = action N ρ π h hρ x := rfl

/-- The actual multiplicity dimension satisfies the exact square equation. -/
theorem finrank_sq : Module.finrank ℂ (Space N ρ π) ^ 2 = Fintype.card (G ⧸ N) := by
  let : Nontrivial (Space N ρ π) := multiplicity_nontrivial N ρ π h
  exact TwistedActionEquivalence.finrank_sq (CliffordSource.cocycle N ρ π h hρ)
    (CliffordSource.normalized N ρ π h hρ)
    (fun a => (sectionOperator N ρ π hρ a).toLinearMap)
    (congrArg LinearEquiv.toLinearMap (sectionOperator_one N ρ π hρ))
    (CliffordSource.operator_mul N ρ π h hρ) hnd
    (CliffordIrreducible.irreducible N ρ π h hρ)

/-- Source 9.6's square-root formula, with no supplied multiplicity dimension. -/
theorem finrank_sqrt : Module.finrank ℂ (Space N ρ π) = Nat.sqrt (Fintype.card (G ⧸ N)) := by
  rw [← finrank_sq N ρ π h hρ hnd, Nat.sqrt_eq']

end PaperXI.CliffordPacket
