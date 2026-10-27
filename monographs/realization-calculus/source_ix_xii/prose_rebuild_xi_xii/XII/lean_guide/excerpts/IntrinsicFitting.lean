import PaperXII.PresentationIndependence
import Mathlib.Algebra.Module.FinitePresentation

/-! Intrinsic Fitting ideals, with independence proved rather than supplied. -/
noncomputable section
namespace PaperXII
open Matrix DeterminantalIdeals
variable (R : Type*) [CommRing R] (M : Type*) [AddCommGroup M] [Module R M]

/-- Actual finite free relations, generators, and a surjective quotient map. -/
structure FiniteMatrixPresentation where
  generators : ℕ
  relations : ℕ
  matrix : Matrix (Fin generators) (Fin relations) R
  quotient : (Fin generators → R) →ₗ[R] M
  presents : Presents matrix quotient

instance finiteMatrixPresentation_nonempty [Module.FinitePresentation R M] : Nonempty (FiniteMatrixPresentation R M) := by
  classical
  obtain ⟨n,m,f,g,hf,hgf⟩ := Module.FinitePresentation.exists_fin' R M
  refine ⟨⟨n,m,LinearMap.toMatrix' g,f,⟨hf,?_⟩⟩⟩
  simpa only [← Matrix.toLin'_apply',Matrix.toLin'_toMatrix'] using hgf.linearMap_ker_eq.symm

/-- A chosen finite presentation. Its choice is removed by `fittingIdeal_eq_presentation`. -/
def chosenPresentation [Module.FinitePresentation R M] : FiniteMatrixPresentation R M :=
  Classical.choice inferInstance

/-- The intrinsic j-th Fitting ideal of a finitely presented module. -/
def fittingIdeal [Module.FinitePresentation R M] (j : ℕ) : Ideal R :=
  presentationIdeal (chosenPresentation R M).matrix j

variable {R M}

/-- The intrinsic ideal equals the minors computed from any actual finite presentation. -/
theorem fittingIdeal_eq_presentation [Module.FinitePresentation R M]
    {m n : Type*} [Fintype m] [Fintype n]
    (A : Matrix m n R) (π : (m → R) →ₗ[R] M) (h : Presents A π) (j : ℕ) :
    fittingIdeal R M j = presentationIdeal A j :=
  presentationIdeal_independent _ _ _ _ (chosenPresentation R M).presents h j

/-- Explicit generators give the upper-index normalization, without hidden subtraction assumptions. -/
theorem fittingIdeal_eq_top_of_generator_bound [Module.FinitePresentation R M]
    {m n : Type*} [Fintype m] [Fintype n]
    (A : Matrix m n R) (π : (m → R) →ₗ[R] M) (h : Presents A π)
    {j : ℕ} (hj : Fintype.card m ≤ j) : fittingIdeal R M j = ⊤ := by
  rw [fittingIdeal_eq_presentation A π h j,presentationIdeal_eq_top _ hj]

variable {N : Type*} [AddCommGroup N] [Module R N]

/-- The same relation matrix presents the actual transported module. -/
theorem presents_comp_equiv {m n : Type*} [Fintype n]
    (A : Matrix m n R) (π : (m → R) →ₗ[R] M) (h : Presents A π)
    (e : M ≃ₗ[R] N) : Presents A (e.toLinearMap.comp π) := by
  refine ⟨e.surjective.comp h.surjective,?_⟩
  rw [h.range_eq_ker]
  ext x
  change π x = 0 ↔ e (π x) = 0
  exact (e.map_eq_zero_iff).symm

/-- Intrinsic Fitting ideals are invariant under actual module isomorphisms. -/
theorem fittingIdeal_linearEquiv [Module.FinitePresentation R M]
    [Module.FinitePresentation R N] (e : M ≃ₗ[R] N) (j : ℕ) :
    fittingIdeal R M j = fittingIdeal R N j := by
  let P := chosenPresentation R M
  rw [fittingIdeal_eq_presentation P.matrix P.quotient P.presents j,
    fittingIdeal_eq_presentation P.matrix (e.toLinearMap.comp P.quotient)
      (presents_comp_equiv P.matrix P.quotient P.presents e) j]

end PaperXII
