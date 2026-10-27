import FiniteCoordinatePolynomialHensel

/-!
# From a surjective residual Jacobian to an exact polynomial solution

Over a residue field, a surjective coordinate Jacobian has a linear right
inverse.  In standard bases this is a matrix right inverse.  Lifting that
matrix entrywise and applying the finite-coordinate polynomial Hensel theorem
produces an exact solution over a nilpotent thickening.
-/

namespace Komorebi.StrongArtin.SurjectiveMatrixRightInverse

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.VariableJacobianHensel

noncomputable section

/-- A surjective linear map onto a finite standard coordinate space has a
linear right inverse. -/
theorem exists_linear_rightInverse_of_surjective_standard
    {k X κ : Type*} [Field k]
    [AddCommGroup X] [Module k X]
    [Fintype κ] [DecidableEq κ]
    (f : X →ₗ[k] (κ → k)) (hf : Function.Surjective f) :
    ∃ r : (κ → k) →ₗ[k] X, f.comp r = LinearMap.id := by
  classical
  have hpre : ∀ j : κ, ∃ x : X, f x = (Pi.basisFun k κ) j := by
    intro j
    exact hf ((Pi.basisFun k κ) j)
  choose pre hpre using hpre
  let r : (κ → k) →ₗ[k] X := (Pi.basisFun k κ).constr k pre
  refine ⟨r, ?_⟩
  apply (Pi.basisFun k κ).ext
  intro j
  simp [r, hpre]

/-- A surjective matrix map over a field admits a matrix right inverse. -/
theorem exists_matrix_rightInverse_of_surjective
    {k ι κ : Type*} [Field k]
    [Fintype ι] [DecidableEq ι]
    [Fintype κ] [DecidableEq κ]
    (J : Matrix κ ι k)
    (hJ : Function.Surjective (matrixLinear J)) :
    ∃ R : Matrix ι κ k, J * R = 1 := by
  obtain ⟨r, hr⟩ :=
    exists_linear_rightInverse_of_surjective_standard (matrixLinear J) hJ
  let R : Matrix ι κ k :=
    (LinearMap.toMatrix (Pi.basisFun k κ) (Pi.basisFun k ι)) r
  refine ⟨R, ?_⟩
  apply (Matrix.toLin (Pi.basisFun k κ) (Pi.basisFun k κ)).injective
  change matrixLinear (J * R) = matrixLinear (1 : Matrix κ κ k)
  rw [← matrixLinear_mul]
  rw [matrixLinear_one]
  rw [show matrixLinear R = r by
    exact Matrix.toLin_toMatrix _ _ r]
  exact hr


end

end Komorebi.StrongArtin.SurjectiveMatrixRightInverse

#print axioms Komorebi.StrongArtin.SurjectiveMatrixRightInverse.exists_linear_rightInverse_of_surjective_standard
#print axioms Komorebi.StrongArtin.SurjectiveMatrixRightInverse.exists_matrix_rightInverse_of_surjective
