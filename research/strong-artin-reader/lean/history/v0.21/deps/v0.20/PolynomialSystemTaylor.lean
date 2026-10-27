import PolynomialExpressionTaylor
import VariableJacobianHensel

/-!
# Automatic Taylor gain for finite-coordinate polynomial systems

A system is a family of scalar polynomial expressions.  Its directional
Jacobian is assembled coordinatewise.  The scalar Taylor theorem proves the
state-dependent remainder gain required by the nonlinear Hensel theorem.
-/

namespace Komorebi.StrongArtin.PolynomialSystemTaylor

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.VariableJacobianHensel
open Komorebi.StrongArtin.PolynomialExpressionTaylor

variable {ι κ R : Type*} [CommRing R]

/-- A coordinate polynomial system. -/
abbrev System (ι κ R : Type*) := κ → Expr ι R

/-- Evaluate every equation in a polynomial system. -/
def evalSystem (system : System ι κ R) (x : ι → R) : κ → R :=
  fun j => Expr.eval (system j) x

/-- The state-dependent directional Jacobian of a polynomial system. -/
def systemDerivative (system : System ι κ R) (x : ι → R) :
    (ι → R) →ₗ[R] (κ → R) where
  toFun := fun delta j => Expr.deriv (system j) x delta
  map_add' := by
    intro delta eta
    funext j
    exact Expr.deriv_add_direction (system j) x delta eta
  map_smul' := by
    intro a delta
    funext j
    simpa [smul_eq_mul] using
      Expr.deriv_smul_direction (system j) x delta a

@[simp] theorem evalSystem_apply (system : System ι κ R) (x : ι → R) (j : κ) :
    evalSystem system x j = Expr.eval (system j) x := rfl

@[simp] theorem systemDerivative_apply
    (system : System ι κ R) (x delta : ι → R) (j : κ) :
    systemDerivative system x delta j = Expr.deriv (system j) x delta := rfl

/-- The vector-valued variable remainder is coordinatewise the scalar
expression remainder. -/
theorem variableRemainder_apply
    (system : System ι κ R) (x delta : ι → R) (j : κ) :
    variableRemainder (evalSystem system) (systemDerivative system) x delta j =
      Expr.remainder (system j) x delta := by
  rfl

/-- Every coordinate polynomial system satisfies the one-power Taylor-gain
hypothesis required by `VariableJacobianHensel`. -/
theorem polynomialSystem_remainder_raises_one
    (pi : R) (system : System ι κ R) :
    VariableRemainderRaisesOne pi
      (evalSystem system) (systemDerivative system) := by
  intro n hn x delta hdelta
  have hcoord : ∀ j : κ,
      PowDivisible pi (n + 1)
        (variableRemainder (evalSystem system) (systemDerivative system) x delta j) := by
    intro j
    rw [variableRemainder_apply]
    exact Expr.remainder_powDivisible (system j) pi hn x delta hdelta
  classical
  choose witness hwitness using hcoord
  refine ⟨fun j => witness j, ?_⟩
  funext j
  simpa using hwitness j

/-- Polynomial systems over a nilpotent coefficient thickening have an exact
solution whenever their Jacobians possess one residual-fibre-stable approximate
right inverse and the initial point solves the equations modulo `pi`. -/
theorem exists_exact_polynomial_system_solution
    (pi : R) (system : System ι κ R)
    (approxRightInv : (κ → R) →ₗ[R] (ι → R))
    (E : (ι → R) → Module.End R (κ → R))
    (x₀ : ι → R)
    (happrox : ∀ x : ι → R, SameResidual pi x₀ x →
      (systemDerivative system x).comp approxRightInv =
        LinearMap.id + pi • E x)
    (hpi : IsNilpotent pi)
    (hx₀ : PowDivisible pi 1 (evalSystem system x₀)) :
    ∃ x : ι → R,
      SameResidual pi x₀ x ∧ evalSystem system x = 0 := by
  exact exists_exact_solution_variableJacobian
    pi (evalSystem system) (systemDerivative system)
    approxRightInv E x₀ happrox hpi
    (polynomialSystem_remainder_raises_one pi system) hx₀

end Komorebi.StrongArtin.PolynomialSystemTaylor

#print axioms Komorebi.StrongArtin.PolynomialSystemTaylor.systemDerivative
#print axioms Komorebi.StrongArtin.PolynomialSystemTaylor.polynomialSystem_remainder_raises_one
#print axioms Komorebi.StrongArtin.PolynomialSystemTaylor.exists_exact_polynomial_system_solution
