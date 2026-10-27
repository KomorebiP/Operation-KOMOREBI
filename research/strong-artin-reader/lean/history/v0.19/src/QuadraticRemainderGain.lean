import VariableJacobianHensel
import Mathlib.LinearAlgebra.BilinearMap
import Mathlib.Tactic.Abel

/-!
# Automatic remainder gain for quadratic equation systems

Quadratic polynomial equations satisfy the Taylor remainder hypothesis used by
the variable-Jacobian Hensel theorem.  This demonstrates that the nonlinear
capstone applies to a concrete, non-affine class of equation systems.
-/

namespace Komorebi.StrongArtin.QuadraticRemainderGain

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.VariableJacobianHensel

variable {R X W : Type*} [CommRing R]
  [AddCommGroup X] [Module R X]
  [AddCommGroup W] [Module R W]

/-- An affine-quadratic equation map. -/
def quadraticMap
    (constant : W) (linear : X →ₗ[R] W)
    (bilinear : X →ₗ[R] X →ₗ[R] W) (x : X) : W :=
  constant + linear x + bilinear x x

/-- Its state-dependent first derivative. -/
def quadraticDerivative
    (linear : X →ₗ[R] W) (bilinear : X →ₗ[R] X →ₗ[R] W) (x : X) : X →ₗ[R] W :=
  linear + bilinear x + bilinear.flip x

/-- The Taylor remainder of an affine-quadratic map is exactly the pure
quadratic term in the correction. -/
theorem quadratic_variableRemainder
    (constant : W) (linear : X →ₗ[R] W)
    (bilinear : X →ₗ[R] X →ₗ[R] W) (x delta : X) :
    variableRemainder
      (quadraticMap constant linear bilinear)
      (quadraticDerivative linear bilinear) x delta
      = bilinear delta delta := by
  simp [variableRemainder, quadraticMap, quadraticDerivative]
  abel

/-- Quadratic remainders gain one filtration power for every correction of
positive depth. -/
theorem quadratic_remainder_raises_one
    (pi : R) (constant : W) (linear : X →ₗ[R] W)
    (bilinear : X →ₗ[R] X →ₗ[R] W) :
    VariableRemainderRaisesOne pi
      (quadraticMap constant linear bilinear)
      (quadraticDerivative linear bilinear) := by
  intro n hn x delta hdelta
  rw [quadratic_variableRemainder]
  obtain ⟨delta₀, rfl⟩ := hdelta
  apply PowDivisible.mono (Nat.add_le_add_left hn n)
  refine ⟨bilinear delta₀ delta₀, ?_⟩
  simp [pow_add, smul_smul]


/-- A quadratic equation system over a nilpotent coefficient thickening has an
exact solution whenever its derivative admits one residual-fibre-stable
approximate right inverse and the initial point solves the equations modulo
`pi`. -/
theorem exists_exact_quadratic_solution
    (pi : R) (constant : W) (linear : X →ₗ[R] W)
    (bilinear : X →ₗ[R] X →ₗ[R] W)
    (approxRightInv : W →ₗ[R] X) (E : X → Module.End R W)
    (x₀ : X)
    (happrox : ∀ x : X, SameResidual pi x₀ x →
      (quadraticDerivative linear bilinear x).comp approxRightInv =
        LinearMap.id + pi • E x)
    (hpi : IsNilpotent pi)
    (hx₀ : PowDivisible pi 1 (quadraticMap constant linear bilinear x₀)) :
    ∃ x : X,
      SameResidual pi x₀ x ∧ quadraticMap constant linear bilinear x = 0 := by
  exact exists_exact_solution_variableJacobian
    pi (quadraticMap constant linear bilinear)
    (quadraticDerivative linear bilinear)
    approxRightInv E x₀ happrox hpi
    (quadratic_remainder_raises_one pi constant linear bilinear) hx₀

end Komorebi.StrongArtin.QuadraticRemainderGain

#print axioms Komorebi.StrongArtin.QuadraticRemainderGain.quadratic_variableRemainder
#print axioms Komorebi.StrongArtin.QuadraticRemainderGain.quadratic_remainder_raises_one
#print axioms Komorebi.StrongArtin.QuadraticRemainderGain.exists_exact_quadratic_solution
