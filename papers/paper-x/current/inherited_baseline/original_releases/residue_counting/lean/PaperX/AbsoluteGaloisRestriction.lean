import Mathlib.FieldTheory.AbsoluteGaloisGroup
import Mathlib.FieldTheory.Normal.Basic

/-! Restriction from the actual absolute Galois group of Q to a normal extension,
using a chosen embedding into the fixed algebraic closure. Surjectivity follows
from extension of field automorphisms. Finite extensions give continuous maps
for the existing Krull topologies. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.AbsoluteGaloisRestriction

variable (L : Type*) [Field L] [Algebra ℚ L] [Normal ℚ L]

/-- A chosen Q-embedding into Mathlib's fixed algebraic closure of Q. -/
def embedding : L →ₐ[ℚ] AlgebraicClosure ℚ := IsAlgClosed.lift

/-- Restriction along the chosen embedding, as an actual group homomorphism. -/
def restriction : Field.absoluteGaloisGroup ℚ →* Gal(L/ℚ) := by
  let : Algebra L (AlgebraicClosure ℚ) := (embedding L).toAlgebra
  exact AlgEquiv.restrictNormalHom L

/-- The restricted automorphism acts on every embedded field element as the
original absolute automorphism. -/
theorem restriction_commutes (σ : Field.absoluteGaloisGroup ℚ) (x : L) :
    embedding L (restriction L σ x) = (show Gal(AlgebraicClosure ℚ/ℚ) from σ) (embedding L x) := by
  let : Algebra L (AlgebraicClosure ℚ) := (embedding L).toAlgebra
  exact AlgEquiv.restrictNormal_commutes σ L x

/-- Every automorphism of the normal extension extends to the algebraic closure. -/
theorem restriction_surjective : Function.Surjective (restriction L) := by
  let : Algebra L (AlgebraicClosure ℚ) := (embedding L).toAlgebra
  exact AlgEquiv.restrictNormalHom_surjective (AlgebraicClosure ℚ)

/-- Restriction is the identity exactly when the absolute automorphism fixes
all elements of the chosen embedded field. -/
theorem restriction_eq_one_iff (σ : Field.absoluteGaloisGroup ℚ) :
    restriction L σ = 1 ↔ ∀ x : L, (show Gal(AlgebraicClosure ℚ/ℚ) from σ) (embedding L x) = embedding L x := by
  constructor
  · intro h x
    simpa [h] using (restriction_commutes L σ x).symm
  · intro h
    ext x
    apply (embedding L).injective
    exact (restriction_commutes L σ x).trans (h x)

/-- The restriction homomorphism is continuous when the extension is finite. -/
theorem restriction_continuous [FiniteDimensional ℚ L] : Continuous (restriction L) := by
  change Continuous (show Gal(AlgebraicClosure ℚ/ℚ) → Gal(L/ℚ) from restriction L)
  let F : IntermediateField ℚ (AlgebraicClosure ℚ) := (embedding L).fieldRange
  let : FiniteDimensional ℚ F := Module.Finite.equiv (embedding L).equivFieldRange.toLinearEquiv
  apply continuous_of_continuousAt_one (restriction L) (continuousAt_def.mpr ?_)
  intro N hN
  have h1 : (1 : Gal(L/ℚ)) ∈ N := by simpa using mem_of_mem_nhds hN
  apply mem_nhds_iff.mpr
  refine ⟨(F.fixingSubgroup : Set Gal(AlgebraicClosure ℚ/ℚ)), ?_,
    F.fixingSubgroup_isOpen, ?_⟩
  · intro σ hσ
    have heq : restriction L σ = 1 := (restriction_eq_one_iff L σ).mpr (by
      intro x
      exact hσ ⟨embedding L x, ⟨x, rfl⟩⟩)
    change restriction L σ ∈ N
    rw [heq]
    exact h1
  · exact F.fixingSubgroup.one_mem

/-- The finite normal extension defines an open kernel in the actual absolute
Galois group, so it is a continuous finite quotient. -/
theorem restriction_kernel_isOpen [FiniteDimensional ℚ L] :
    IsOpen ((restriction L).ker : Set (Field.absoluteGaloisGroup ℚ)) := by
  exact (isOpen_discrete ({1} : Set Gal(L/ℚ))).preimage (restriction_continuous L)

/-- Restriction packaged with its proved continuity. -/
def continuousRestriction [FiniteDimensional ℚ L] :
    Field.absoluteGaloisGroup ℚ →ₜ* Gal(L/ℚ) :=
  ⟨restriction L, restriction_continuous L⟩

end PaperX.AbsoluteGaloisRestriction
