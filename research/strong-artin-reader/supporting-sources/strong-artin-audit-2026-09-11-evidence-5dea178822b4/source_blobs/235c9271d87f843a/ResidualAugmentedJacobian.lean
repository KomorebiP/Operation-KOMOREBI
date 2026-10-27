import AuxiliaryAugmentedJacobian
import ObstructionFunctionalColumnRepresentation
import SurjectiveMatrixRightInverse
import SurjectiveResidueHomPolynomialHensel
import Mathlib.Data.Fintype.Sum

/-!
# Residual auxiliary selection as an actual augmented polynomial Jacobian

The abstract Taylor--Wiles auxiliary columns selected on the residual equation
space are lifted coefficientwise and inserted as genuine linear variables in a
finite polynomial presentation.  The residual matrix of that enlarged system
is surjective exactly because the selected augmented Jacobian is surjective.
-/

namespace Komorebi.StrongArtin.ResidualAugmentedJacobian

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.VariableJacobianHensel
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel
open Komorebi.StrongArtin.SurjectiveMatrixRightInverse
open Komorebi.StrongArtin.SurjectiveResidueHomPolynomialHensel
open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation
open Komorebi.StrongArtin.AuxiliaryAugmentedPolynomialSystem
open Komorebi.StrongArtin.AuxiliaryAugmentedJacobian
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet

noncomputable section

set_option linter.unusedSectionVars false

variable {R k ι κ Aux : Type*} [CommRing R] [Field k]
  [Fintype ι] [DecidableEq ι]
  [Fintype κ] [DecidableEq κ]
  [DecidableEq Aux]

/-- The residual Jacobian of the original polynomial coordinates. -/
def residualBaseJacobian
    (q : R →+* k) (system : System ι κ R) (x₀ : ι → R) :
    (ι → k) →ₗ[k] (κ → k) :=
  matrixLinear ((jacobianMatrix system x₀).map q)

/-- Residual reduction of a family of coefficient-ring equation columns. -/
def residualColumn
    (q : R →+* k) (column : Aux → (κ → R)) : Aux → (κ → k) :=
  fun a j => q (column a j)

/-- Every residual column family lifts coefficientwise along a surjective
coefficient homomorphism. -/
theorem exists_column_lift_of_surjective
    (q : R →+* k) (hq : Function.Surjective q)
    (columnBar : Aux → (κ → k)) :
    ∃ column : Aux → (κ → R),
      ∀ a j, q (column a j) = columnBar a j := by
  have hpre : ∀ a j, ∃ x : R, q x = columnBar a j := by
    intro a j
    exact hq (columnBar a j)
  choose column hcolumn using hpre
  exact ⟨column, hcolumn⟩

/-- Merge original and auxiliary residual coordinates into a sum-indexed
coordinate vector. -/
def mergeResidualCoordinates (u : ι → k) (a : Q → k) : Sum ι Q → k
  | Sum.inl i => u i
  | Sum.inr x => a x

@[simp] theorem baseCoordinates_mergeResidualCoordinates
    (Q : Finset Aux) (u : ι → k) (a : Q → k) :
    baseCoordinates Q (mergeResidualCoordinates u a) = u := rfl

@[simp] theorem auxiliaryCoordinates_mergeResidualCoordinates
    (Q : Finset Aux) (u : ι → k) (a : Q → k) :
    auxiliaryCoordinates Q (mergeResidualCoordinates u a) = a := rfl

/-- Application formula for the residual matrix of the enlarged polynomial
system. -/
theorem residual_augmentedJacobian_apply
    (q : R →+* k) (system : System ι κ R)
    (column : Aux → (κ → R)) (Q : Finset Aux) (x₀ : ι → R)
    (delta : Sum ι Q → k) (j : κ) :
    matrixLinear
        ((augmentedJacobianMatrix system column Q
          (augmentedBasePoint Q x₀)).map q) delta j =
      residualBaseJacobian q system x₀ (baseCoordinates Q delta) j +
        ∑ a : Q,
          auxiliaryCoordinates Q delta a * residualColumn q column a.1 j := by
  change
    (∑ s : Sum ι Q,
      q (augmentedJacobianMatrix system column Q
        (augmentedBasePoint Q x₀) j s) * delta s) = _
  rw [Fintype.sum_sum_type]
  simp only [augmentedJacobianMatrix_apply_inl,
    augmentedJacobianMatrix_apply_inr]
  change
    (∑ i : ι, q (jacobianMatrix system x₀ j i) * delta (Sum.inl i)) +
      (∑ a : Q, q (column a.1 j) * delta (Sum.inr a)) = _
  have hbase :
      (∑ i : ι, q (jacobianMatrix system x₀ j i) * delta (Sum.inl i)) =
        residualBaseJacobian q system x₀ (baseCoordinates Q delta) j := by
    rfl
  have haux :
      (∑ a : Q, q (column a.1 j) * delta (Sum.inr a)) =
        ∑ a : Q,
          auxiliaryCoordinates Q delta a * residualColumn q column a.1 j := by
    apply Finset.sum_congr rfl
    intro a ha
    simp [auxiliaryCoordinates, residualColumn, mul_comm]
  rw [hbase, haux]

/-- If the abstract selected auxiliary columns make the residual augmented map
surjective, then the coordinate Jacobian of the genuine enlarged polynomial
system is surjective after reduction. -/
theorem residual_augmentedJacobian_surjective
    (q : R →+* k) (system : System ι κ R) (x₀ : ι → R)
    (columnBar : Aux → (κ → k)) (column : Aux → (κ → R))
    (hcolumn : ∀ a j, q (column a j) = columnBar a j)
    (Q : Finset Aux)
    (hsurj : Function.Surjective
      (augmentedMap (residualBaseJacobian q system x₀) columnBar Q)) :
    Function.Surjective
      (matrixLinear
        ((augmentedJacobianMatrix system column Q
          (augmentedBasePoint Q x₀)).map q)) := by
  intro y
  obtain ⟨⟨u, a⟩, hua⟩ := hsurj y
  refine ⟨mergeResidualCoordinates u a, ?_⟩
  ext j
  rw [residual_augmentedJacobian_apply]
  have hj := congrFun hua j
  simpa [augmentedMap_apply, residualColumn, hcolumn,
    baseCoordinates_mergeResidualCoordinates,
    auxiliaryCoordinates_mergeResidualCoordinates, mul_comm] using hj

/-- A surjective selected residual augmented map provides a lifted matrix right
inverse and therefore an exact solution to the genuine auxiliary-augmented
nonlinear polynomial system. -/
theorem exists_exact_augmented_solution_of_selected_residual_surjectivity
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span ({pi} : Set R))
    (system : System ι κ R) (x₀ : ι → R)
    (columnBar : Aux → (κ → k)) (column : Aux → (κ → R))
    (hcolumn : ∀ a j, q (column a j) = columnBar a j)
    (Q : Finset Aux)
    (hsurj : Function.Surjective
      (augmentedMap (residualBaseJacobian q system x₀) columnBar Q))
    (hpi : IsNilpotent pi)
    (hx₀ : PowDivisible pi 1 (evalSystem system x₀)) :
    ∃ z : Sum ι Q → R,
      SameResidual pi (augmentedBasePoint Q x₀) z ∧
      augmentedEval system column Q z = 0 := by
  have hJ := residual_augmentedJacobian_surjective
    q system x₀ columnBar column hcolumn Q hsurj
  obtain ⟨Rbar, hRbar⟩ :=
    exists_matrix_rightInverse_of_surjective
      ((augmentedJacobianMatrix system column Q
        (augmentedBasePoint Q x₀)).map q) hJ
  obtain ⟨R₀, -, hR₀⟩ :=
    exists_lifted_approx_rightInverse_of_residue_hom
      pi q hq hker
      (augmentedJacobianMatrix system column Q (augmentedBasePoint Q x₀))
      Rbar hRbar
  exact exists_exact_augmented_solution_of_residual_matrix_rightInverse
    pi system column Q x₀ R₀ hR₀ hpi hx₀

/--
**Taylor--Wiles auxiliary variables to nonlinear polynomial solution.**
Any v0.15 one-prime selection interface on the dual obstruction space of the
residual base Jacobian automatically supplies residual equation columns, an
exact admissible finite set, coefficient-ring lifts of those columns, a
surjective enlarged residual coordinate Jacobian, and an exact nonlinear
solution over the nilpotent coefficient thickening.
-/
theorem exists_exact_solution_from_onePrimeSelectionInterface
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span ({pi} : Set R))
    (system : System ι κ R) (x₀ : ι → R)
    (I : OnePrimeSelectionInterface k
      (obstructionDual (residualBaseJacobian q system x₀)) Aux)
    (hpi : IsNilpotent pi)
    (hx₀ : PowDivisible pi 1 (evalSystem system x₀)) :
    ∃ columnBar : Aux → (κ → k),
      ∃ column : Aux → (κ → R),
      ∃ Q : Finset Aux,
        (∀ a, columnFunctional
            (residualBaseJacobian q system x₀) columnBar a =
              I.localFunctional a) ∧
        (∀ a j, q (column a j) = columnBar a j) ∧
        (∀ a ∈ Q, I.admissible a) ∧
        Q.card = Module.finrank k
          (obstructionDual (residualBaseJacobian q system x₀)) ∧
        ∃ z : Sum ι Q → R,
          SameResidual pi (augmentedBasePoint Q x₀) z ∧
          augmentedEval system column Q z = 0 := by
  obtain ⟨columnBar, Q, hfunctional, hgood, hcard, hsurj⟩ :=
    exists_representing_columns_and_surjective_auxiliary_set
      (residualBaseJacobian q system x₀) I
  obtain ⟨column, hcolumn⟩ :=
    exists_column_lift_of_surjective q hq columnBar
  obtain ⟨z, hzres, hz⟩ :=
    exists_exact_augmented_solution_of_selected_residual_surjectivity
      pi q hq hker system x₀ columnBar column hcolumn Q hsurj hpi hx₀
  exact ⟨columnBar, column, Q, hfunctional, hcolumn, hgood, hcard,
    z, hzres, hz⟩

end

end Komorebi.StrongArtin.ResidualAugmentedJacobian

#print axioms Komorebi.StrongArtin.ResidualAugmentedJacobian.residual_augmentedJacobian_surjective
#print axioms Komorebi.StrongArtin.ResidualAugmentedJacobian.exists_exact_augmented_solution_of_selected_residual_surjectivity
#print axioms Komorebi.StrongArtin.ResidualAugmentedJacobian.exists_exact_solution_from_onePrimeSelectionInterface
