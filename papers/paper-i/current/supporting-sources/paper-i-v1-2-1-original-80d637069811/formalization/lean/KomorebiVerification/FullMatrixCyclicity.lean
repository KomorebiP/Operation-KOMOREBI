import Mathlib

/-!
# Cyclicity for the full matrix algebra

Every nonzero vector in a finite-dimensional coordinate space is cyclic for
the natural action of the full matrix algebra.  Concretely, if `x ≠ 0`, then
for every target vector `y` there is a matrix `A` with `A *ᵥ x = y`.
-/

set_option autoImplicit false

namespace Komorebi.FullMatrixCyclicity

universe u v

variable {K : Type u} [Field K]
variable {ι : Type v} [Fintype ι] [DecidableEq ι]

/-- A vector is cyclic for the natural action of the full matrix algebra. -/
def IsCyclic (x : ι → K) : Prop :=
  ∀ y : ι → K, ∃ A : Matrix ι ι K, Matrix.mulVec A x = y

/-- Every nonzero vector is cyclic under the full matrix algebra. -/
theorem isCyclic_of_ne_zero {x : ι → K} (hx : x ≠ 0) : IsCyclic x := by
  obtain ⟨j, hj⟩ : ∃ j, x j ≠ 0 := by
    by_contra h
    apply hx
    funext i
    by_contra hi
    exact h ⟨i, hi⟩
  intro y
  let A : Matrix ι ι K := fun i k ↦ if k = j then y i / x j else 0
  refine ⟨A, ?_⟩
  funext i
  simp [A, Matrix.mulVec, dotProduct, hj]

end Komorebi.FullMatrixCyclicity

#print axioms Komorebi.FullMatrixCyclicity.isCyclic_of_ne_zero
