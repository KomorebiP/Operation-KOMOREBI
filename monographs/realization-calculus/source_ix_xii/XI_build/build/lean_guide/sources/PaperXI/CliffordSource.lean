import PaperXI.CliffordIrreducible
import PaperXI.CliffordCocycle

/-! The normalized cocycle and literal projective action for the source
Clifford datum, with all auxiliary dimensions and nontriviality derived. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordSource
open CliffordDatum CliffordMultiplicity CliffordIrreducible CocycleCommutator
open scoped IsMulCommutative

variable {G W X : Type*} [Group G] [Finite G]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]
variable (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)]
variable (ρ : Representation ℂ N W) (π : Representation ℂ G X)
variable [Representation.IsIrreducible ρ] [Representation.IsIrreducible π]
variable (h : Isotypic N ρ π) (hρ : Invariant N ρ)

/-- The actual Clifford cocycle on the quotient, extracted from its actual Hom action. -/
def cocycle : Cocycle (G ⧸ N) ℂˣ := by
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional ρ
  let : Nontrivial (Space N ρ π) := multiplicity_nontrivial N ρ π h
  exact CliffordCocycle.cocycle N ρ π hρ

/-- The source cocycle is normalized at the identity. -/
theorem normalized : Normalized (cocycle N ρ π h hρ) := by
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional ρ
  let : Nontrivial (Space N ρ π) := multiplicity_nontrivial N ρ π h
  exact CliffordCocycle.normalized N ρ π hρ

/-- The cocycle acts by the literal section operators, with the proved inverse-defect convention. -/
theorem operator_mul (a b : G ⧸ N) :
    (sectionOperator N ρ π hρ a).toLinearMap * (sectionOperator N ρ π hρ b).toLinearMap =
      ((cocycle N ρ π h hρ).coeff a b : ℂ) •
        (sectionOperator N ρ π hρ (a * b)).toLinearMap := by
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional ρ
  exact CliffordCocycle.sectionOperator_mul N ρ π hρ a b

include h
omit [IsMulCommutative (G ⧸ N)] in
/-- The actual operators and cocycle have a nonzero carrier and an irreducible action. -/
theorem projective_irreducible :
    Nontrivial (Space N ρ π) ∧
      ∀ L : Submodule ℂ (Space N ρ π),
        (∀ a f, f ∈ L → sectionOperator N ρ π hρ a f ∈ L) → L = ⊥ ∨ L = ⊤ :=
  ⟨multiplicity_nontrivial N ρ π h, CliffordIrreducible.irreducible N ρ π h hρ⟩

end PaperXI.CliffordSource
