import PolynomialSystemTaylor
import FiniteCoordinatePolynomialHensel
import Mathlib.LinearAlgebra.Finsupp.LinearCombination
import Mathlib.Data.Fintype.Sum
import Mathlib.Tactic.Ring

/-!
# Polynomial systems with linear auxiliary variables

A finite family of auxiliary Jacobian columns is promoted to genuine polynomial
variables.  The auxiliary variables enter linearly, so the nonlinear Taylor
remainder is exactly the remainder of the original polynomial system.  This is
the algebraic shape of Taylor--Wiles variables in a finite presentation.
-/

namespace Komorebi.StrongArtin.AuxiliaryAugmentedPolynomialSystem

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.VariableJacobianHensel
open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel

noncomputable section

variable {R ι κ Aux : Type*} [CommRing R]

/-- Restrict a sum-indexed coordinate vector to its original coordinates. -/
def baseCoordinates (Q : Finset Aux) (z : Sum ι Q → R) : ι → R :=
  fun i => z (Sum.inl i)

/-- Restrict a sum-indexed coordinate vector to its auxiliary coordinates. -/
def auxiliaryCoordinates (Q : Finset Aux) (z : Sum ι Q → R) : Q → R :=
  fun a => z (Sum.inr a)

/-- The original-coordinate restriction as a linear map. -/
def baseCoordinatesLinear (Q : Finset Aux) :
    (Sum ι Q → R) →ₗ[R] (ι → R) where
  toFun := baseCoordinates Q
  map_add' := by
    intro x y
    rfl
  map_smul' := by
    intro a x
    rfl

/-- The auxiliary-coordinate restriction as a linear map. -/
def auxiliaryCoordinatesLinear (Q : Finset Aux) :
    (Sum ι Q → R) →ₗ[R] (Q → R) where
  toFun := auxiliaryCoordinates Q
  map_add' := by
    intro x y
    rfl
  map_smul' := by
    intro a x
    rfl

@[simp] theorem baseCoordinatesLinear_apply
    (Q : Finset Aux) (z : Sum ι Q → R) :
    baseCoordinatesLinear Q z = baseCoordinates Q z := rfl

@[simp] theorem auxiliaryCoordinatesLinear_apply
    (Q : Finset Aux) (z : Sum ι Q → R) :
    auxiliaryCoordinatesLinear Q z = auxiliaryCoordinates Q z := rfl

/-- Linear combination of the selected auxiliary equation columns over an
arbitrary commutative coefficient ring. -/
def auxiliaryLinearMap [DecidableEq Aux]
    (column : Aux → (κ → R)) (Q : Finset Aux) :
    (Q → R) →ₗ[R] (κ → R) :=
  Fintype.linearCombination R (fun a : Q => column a.1)

@[simp] theorem auxiliaryLinearMap_apply [DecidableEq Aux]
    (column : Aux → (κ → R)) (Q : Finset Aux) (a : Q → R) :
    auxiliaryLinearMap column Q a = ∑ i : Q, a i • column i.1 := rfl

/-- Evaluate the original polynomial equations together with linear auxiliary
columns. -/
def augmentedEval [DecidableEq Aux]
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → R) : κ → R :=
  evalSystem system (baseCoordinates Q z) +
    auxiliaryLinearMap column Q (auxiliaryCoordinates Q z)

/-- The state-dependent derivative of the auxiliary-augmented system. -/
def augmentedDerivative [DecidableEq Aux]
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → R) :
    (Sum ι Q → R) →ₗ[R] (κ → R) :=
  (systemDerivative system (baseCoordinates Q z)).comp
      (baseCoordinatesLinear Q) +
    (auxiliaryLinearMap column Q).comp (auxiliaryCoordinatesLinear Q)

@[simp] theorem augmentedEval_apply [DecidableEq Aux]
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → R) (j : κ) :
    augmentedEval system column Q z j =
      Expr.eval (system j) (baseCoordinates Q z) +
        ∑ a : Q, auxiliaryCoordinates Q z a * column a.1 j := by
  simp [augmentedEval, auxiliaryLinearMap, Fintype.linearCombination_apply]

@[simp] theorem augmentedDerivative_apply [DecidableEq Aux]
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z delta : Sum ι Q → R) (j : κ) :
    augmentedDerivative system column Q z delta j =
      Expr.deriv (system j) (baseCoordinates Q z) (baseCoordinates Q delta) +
        ∑ a : Q, auxiliaryCoordinates Q delta a * column a.1 j := by
  simp [augmentedDerivative, auxiliaryLinearMap, Fintype.linearCombination_apply]

/-- The nonlinear remainder of the augmented system is exactly the original
polynomial remainder: all auxiliary terms cancel because they are linear. -/
theorem augmented_variableRemainder_apply [DecidableEq Aux]
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z delta : Sum ι Q → R) (j : κ) :
    variableRemainder
        (augmentedEval system column Q)
        (augmentedDerivative system column Q)
        z delta j =
      Expr.remainder (system j)
        (baseCoordinates Q z) (baseCoordinates Q delta) := by
  classical
  change
    augmentedEval system column Q (z + delta) j -
        augmentedEval system column Q z j -
        augmentedDerivative system column Q z delta j =
      Expr.remainder (system j)
        (baseCoordinates Q z) (baseCoordinates Q delta)
  rw [augmentedEval_apply, augmentedEval_apply, augmentedDerivative_apply]
  unfold Expr.remainder
  have hbase : baseCoordinates Q (z + delta) =
      baseCoordinates Q z + baseCoordinates Q delta := rfl
  have haux : auxiliaryCoordinates Q (z + delta) =
      auxiliaryCoordinates Q z + auxiliaryCoordinates Q delta := rfl
  rw [hbase, haux]
  simp only [Pi.add_apply, add_mul]
  have hsum :
      (∑ x : Q,
        (auxiliaryCoordinates Q z x * column x.1 j +
          auxiliaryCoordinates Q delta x * column x.1 j)) =
        (∑ x : Q, auxiliaryCoordinates Q z x * column x.1 j) +
          (∑ x : Q, auxiliaryCoordinates Q delta x * column x.1 j) := by
    rw [Finset.sum_add_distrib]
  rw [hsum]
  ring

/-- Adding linear auxiliary variables does not alter the one-power Taylor gain
of a finite polynomial system. -/
theorem augmented_remainder_raises_one [DecidableEq Aux]
    (pi : R) (system : System ι κ R)
    (column : Aux → (κ → R)) (Q : Finset Aux) :
    VariableRemainderRaisesOne pi
      (augmentedEval system column Q)
      (augmentedDerivative system column Q) := by
  intro n hn z delta hdelta
  have hbase : PowDivisible pi n (baseCoordinates Q delta) :=
    hdelta.map (baseCoordinatesLinear Q)
  have hcoord : ∀ j : κ,
      PowDivisible pi (n + 1)
        (variableRemainder
          (augmentedEval system column Q)
          (augmentedDerivative system column Q)
          z delta j) := by
    intro j
    rw [augmented_variableRemainder_apply]
    exact Expr.remainder_powDivisible
      (system j) pi hn (baseCoordinates Q z) (baseCoordinates Q delta) hbase
  classical
  choose witness hwitness using hcoord
  refine ⟨fun j => witness j, ?_⟩
  funext j
  simpa using hwitness j

/-- The augmented base point has the original residual coordinates and zero
auxiliary coordinates. -/
def augmentedBasePoint (Q : Finset Aux) (x₀ : ι → R) : Sum ι Q → R
  | Sum.inl i => x₀ i
  | Sum.inr _ => 0

@[simp] theorem baseCoordinates_augmentedBasePoint
    (Q : Finset Aux) (x₀ : ι → R) :
    baseCoordinates Q (augmentedBasePoint Q x₀) = x₀ := rfl

@[simp] theorem auxiliaryCoordinates_augmentedBasePoint
    (Q : Finset Aux) (x₀ : ι → R) :
    auxiliaryCoordinates Q (augmentedBasePoint Q x₀) = 0 := by
  rfl

@[simp] theorem augmentedEval_augmentedBasePoint [DecidableEq Aux]
    (system : System ι κ R) (column : Aux → (κ → R))
    (Q : Finset Aux) (x₀ : ι → R) :
    augmentedEval system column Q (augmentedBasePoint Q x₀) =
      evalSystem system x₀ := by
  ext j
  simp [augmentedEval_apply]

end

end Komorebi.StrongArtin.AuxiliaryAugmentedPolynomialSystem

#print axioms Komorebi.StrongArtin.AuxiliaryAugmentedPolynomialSystem.augmented_variableRemainder_apply
#print axioms Komorebi.StrongArtin.AuxiliaryAugmentedPolynomialSystem.augmented_remainder_raises_one
#print axioms Komorebi.StrongArtin.AuxiliaryAugmentedPolynomialSystem.augmentedEval_augmentedBasePoint
