import FiniteCoordinatePolynomialHensel
import Mathlib.LinearAlgebra.Matrix.BaseChange
import Mathlib.RingTheory.Ideal.Quotient.Operations

/-!
# Lifting a residual matrix right inverse entrywise

A right inverse over the residue quotient `R / (pi)` can be lifted entrywise to
`R`.  Its composite with the original Jacobian differs from the identity by an
entrywise `pi`-multiple, exactly the hypothesis used by the finite-coordinate
polynomial Hensel theorem.
-/

namespace Komorebi.StrongArtin.ResidualMatrixRightInverseLift

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.VariableJacobianHensel

noncomputable section

variable {R ι κ : Type*} [CommRing R]

/-- Entrywise lifting of a matrix over the principal residue quotient. -/
theorem exists_matrix_lift_mod_span
    (pi : R)
    (Mbar : Matrix ι κ (R ⧸ Ideal.span ({pi} : Set R))) :
    ∃ M : Matrix ι κ R,
      M.map (Ideal.Quotient.mk (Ideal.span ({pi} : Set R))) = Mbar := by
  classical
  let q := Ideal.Quotient.mk (Ideal.span ({pi} : Set R))
  have hsurj : ∀ i j, ∃ x : R, q x = Mbar i j := by
    intro i j
    exact Ideal.Quotient.mk_surjective (Mbar i j)
  choose M hM using hsurj
  refine ⟨M, ?_⟩
  ext i j
  exact hM i j

/-- A residual matrix right inverse has an entrywise lift whose error is
`pi`-divisible. -/
theorem exists_lifted_matrix_approx_rightInverse
    [Fintype ι] [DecidableEq κ]
    (pi : R) (J : Matrix κ ι R)
    (Rbar : Matrix ι κ (R ⧸ Ideal.span ({pi} : Set R)))
    (hbar : J.map (Ideal.Quotient.mk (Ideal.span ({pi} : Set R))) * Rbar = 1) :
    ∃ R₀ : Matrix ι κ R,
      R₀.map (Ideal.Quotient.mk (Ideal.span ({pi} : Set R))) = Rbar ∧
      EntrywisePowDivisible pi 1 (J * R₀ - 1) := by
  classical
  let q := Ideal.Quotient.mk (Ideal.span ({pi} : Set R))
  obtain ⟨R₀, hR₀⟩ := exists_matrix_lift_mod_span pi Rbar
  refine ⟨R₀, hR₀, ?_⟩
  let D : Matrix κ κ R := J * R₀ - 1
  have hmatrix : D.map q = (0 : Matrix κ κ (R ⧸ Ideal.span ({pi} : Set R))) := by
    dsimp [D]
    rw [Matrix.map_sub q q.map_sub]
    rw [Matrix.map_mul]
    rw [hR₀]
    rw [hbar]
    rw [Matrix.map_one q q.map_zero q.map_one]
    simp
  intro i j
  have hentry := congrFun (congrFun hmatrix i) j
  have hq : q (D i j) = 0 := by simpa using hentry
  have hmem : D i j ∈ Ideal.span ({pi} : Set R) :=
    Ideal.Quotient.eq_zero_iff_mem.mp hq
  rw [Ideal.mem_span_singleton] at hmem
  obtain ⟨c, hc⟩ := hmem
  refine ⟨c, ?_⟩
  simpa [D, pow_one, smul_eq_mul] using hc.symm

/--
**Residual-quotient polynomial Hensel theorem.** A right inverse of the
residual Jacobian over `R / (pi)` can be lifted automatically and yields an
exact solution of the polynomial system over any nilpotent `pi`-thickening.
-/
theorem exists_exact_solution_of_residual_quotient_rightInverse
    [Fintype ι] [DecidableEq ι]
    [Fintype κ] [DecidableEq κ]
    (pi : R) (system : System ι κ R) (x₀ : ι → R)
    (Rbar : Matrix ι κ (R ⧸ Ideal.span ({pi} : Set R)))
    (hbar :
      (jacobianMatrix system x₀).map
          (Ideal.Quotient.mk (Ideal.span ({pi} : Set R))) * Rbar = 1)
    (hpi : IsNilpotent pi)
    (hx₀ : PowDivisible pi 1 (evalSystem system x₀)) :
    ∃ x : ι → R, SameResidual pi x₀ x ∧ evalSystem system x = 0 := by
  obtain ⟨R₀, -, hR₀⟩ :=
    exists_lifted_matrix_approx_rightInverse
      pi (jacobianMatrix system x₀) Rbar hbar
  exact exists_exact_solution_of_residual_matrix_rightInverse
    pi system x₀ R₀ hR₀ hpi hx₀

end

end Komorebi.StrongArtin.ResidualMatrixRightInverseLift

#print axioms Komorebi.StrongArtin.ResidualMatrixRightInverseLift.exists_matrix_lift_mod_span
#print axioms Komorebi.StrongArtin.ResidualMatrixRightInverseLift.exists_lifted_matrix_approx_rightInverse
#print axioms Komorebi.StrongArtin.ResidualMatrixRightInverseLift.exists_exact_solution_of_residual_quotient_rightInverse
