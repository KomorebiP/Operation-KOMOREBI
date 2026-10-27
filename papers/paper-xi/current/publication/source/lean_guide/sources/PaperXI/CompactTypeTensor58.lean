import PaperXI.GallagherTensorIrreducibility58
import PaperXI.SmoothDegreeQuotient
import PaperXI.FiniteRepresentation

/-!
# The prescribed compact factor with an actual finite quotient factor

An irreducible quotient representation is tensored with the supplied extension
of an irreducible subgroup action. The resulting compact inducing action is
constructed on the literal tensor space, is irreducible and smooth, and retains
the supplied subgroup action on the first factor exactly. No type-theoretic
compact-induction theorem or arithmetic comparison is asserted.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CompactTypeTensor58

open Representation
open scoped TensorProduct

variable {J Q W U : Type*} [Group J] [Group Q]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup U] [Module ℂ U]
variable (N : Subgroup J) (q : J →* Q) (hN : N ≤ q.ker)
variable (κ : Representation ℂ J W) (σ : Representation ℂ Q U)

/-- The actual action obtained by adjoining the residue multiplicity factor. -/
abbrev action : Representation ℂ J (W ⊗[ℂ] U) := κ.tprod (σ.comp q)

include hN in
/-- Restriction retains the prescribed subgroup action, with the second factor
acting trivially; it does not identify the whole tensor space with W. -/
theorem restriction : (action q κ σ).comp N.subtype = Representation.tprod (κ.comp N.subtype) (1 : Representation ℂ N U) := by
  ext n w u
  have hn : q n = 1 := hN n.property
  simp [action, hn]

include hN in
/-- Literal subgroup action on every pure tensor. -/
theorem subgroup_action (n : N) (w : W) (u : U) :
    action q κ σ n (w ⊗ₜ[ℂ] u) = κ n w ⊗ₜ[ℂ] u := by
  have hn : q n = 1 := hN n.property
  simp [action, hn]

variable [FiniteDimensional ℂ W]

include hN in
/-- The completed compact action is irreducible, derived from the two factors. -/
theorem irreducible (hq : Function.Surjective q)
    [IsIrreducible (κ.comp N.subtype)] [IsIrreducible σ] :
    IsIrreducible (action q κ σ) :=
  GallagherTensorIrreducibility58.tensor_irreducible N q hq hN κ σ

/-- The residue factor, hence the whole tensor space, is finite-dimensional
when the actual quotient group is finite. -/
theorem finiteDimensional [Finite Q] [IsIrreducible σ] :
    FiniteDimensional ℂ (W ⊗[ℂ] U) := by
  let : FiniteDimensional ℂ U := FiniteRepresentation.finiteDimensional σ
  infer_instance

section Topology
variable [TopologicalSpace J] [IsTopologicalGroup J]

include hN in
/-- An open subgroup on which the second factor is trivial gives smoothness
of the tensor action from smoothness of the prescribed first factor. -/
theorem smooth (hopen : IsOpen (N : Set J))
    (hκ : SmoothDegreeQuotient.IsSmooth κ) :
    SmoothDegreeQuotient.IsSmooth (action q κ σ) := by
  intro x
  apply Subgroup.isOpen_mono (H₁ := κ.ker ⊓ N) ?_
    ((SmoothDegreeQuotient.isOpen_kernel_of_smooth κ hκ).inter hopen)
  intro g hg
  have hk : κ g = 1 := hg.1
  have hq : q g = 1 := hN hg.2
  change TensorProduct.map (κ g) (σ (q g)) x = x
  rw [hk, hq, map_one, TensorProduct.map_one]
  rfl

include hN in
/-- Same-candidate compact completion: all conclusions refer to the displayed
tensor action and its exact prescribed first factor. -/
theorem completed [Finite Q] (hq : Function.Surjective q)
    [IsIrreducible (κ.comp N.subtype)] [IsIrreducible σ]
    (hopen : IsOpen (N : Set J)) (hκ : SmoothDegreeQuotient.IsSmooth κ) :
    IsIrreducible (action q κ σ) ∧
    FiniteDimensional ℂ (W ⊗[ℂ] U) ∧
    SmoothDegreeQuotient.IsSmooth (action q κ σ) ∧
    (action q κ σ).comp N.subtype = Representation.tprod (κ.comp N.subtype) (1 : Representation ℂ N U) :=
  ⟨irreducible N q hN κ σ hq, finiteDimensional (W := W) σ,
    smooth N q hN κ σ hopen hκ, restriction N q hN κ σ⟩

end Topology
end PaperXI.CompactTypeTensor58
