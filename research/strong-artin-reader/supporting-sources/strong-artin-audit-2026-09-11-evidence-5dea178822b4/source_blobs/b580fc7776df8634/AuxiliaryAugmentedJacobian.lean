import AuxiliaryAugmentedPolynomialSystem
import ResidualMatrixRightInverseLift
import Mathlib.Tactic.Abel

/-!
# Jacobian stability for polynomial systems with linear auxiliary variables

The derivative of the auxiliary-augmented system is represented in standard
sum coordinates.  Its matrix varies only through the original polynomial
coordinates; the auxiliary columns are constant.  Hence a right inverse modulo
the nilpotent parameter remains an approximate right inverse throughout the
residual fibre, and the variable-Jacobian Hensel theorem applies.
-/

namespace Komorebi.StrongArtin.AuxiliaryAugmentedJacobian

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.VariableJacobianHensel
open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel
open Komorebi.StrongArtin.AuxiliaryAugmentedPolynomialSystem

noncomputable section

set_option linter.unusedSectionVars false

variable {R ι κ Aux : Type*} [CommRing R]
  [Fintype ι] [DecidableEq ι]
  [Fintype κ] [DecidableEq κ]
  [DecidableEq Aux]

/-- Standard-coordinate Jacobian of the polynomial system after adjoining the
selected auxiliary variables. -/
def augmentedJacobianMatrix
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → R) : Matrix κ (Sum ι Q) R :=
  fun j s => match s with
    | Sum.inl i => jacobianMatrix system (baseCoordinates Q z) j i
    | Sum.inr a => column a.1 j

@[simp] theorem augmentedJacobianMatrix_apply_inl
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → R) (j : κ) (i : ι) :
    augmentedJacobianMatrix system column Q z j (Sum.inl i) =
      jacobianMatrix system (baseCoordinates Q z) j i := rfl

@[simp] theorem augmentedJacobianMatrix_apply_inr
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → R) (j : κ) (a : Q) :
    augmentedJacobianMatrix system column Q z j (Sum.inr a) =
      column a.1 j := rfl

/-- The matrix-linear map of the augmented Jacobian is its derivative. -/
theorem matrixLinear_augmentedJacobianMatrix
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → R) :
    matrixLinear (augmentedJacobianMatrix system column Q z) =
      augmentedDerivative system column Q z := by
  apply LinearMap.ext
  intro delta
  funext j
  simp only [matrixLinear, Matrix.toLin_eq_toLin',
    Matrix.toLin'_apply', Matrix.mulVecLin_apply, Matrix.mulVec,
    dotProduct, augmentedDerivative_apply]
  rw [Fintype.sum_sum_type]
  simp only [augmentedJacobianMatrix_apply_inl, augmentedJacobianMatrix_apply_inr]
  have hfirst :
      (∑ i : ι,
        jacobianMatrix system (baseCoordinates Q z) j i * delta (Sum.inl i)) =
        Expr.deriv (system j) (baseCoordinates Q z) (baseCoordinates Q delta) := by
    change matrixLinear (jacobianMatrix system (baseCoordinates Q z))
        (baseCoordinates Q delta) j = _
    have hmap :
        matrixLinear (jacobianMatrix system (baseCoordinates Q z)) =
          systemDerivative system (baseCoordinates Q z) := by
      unfold jacobianMatrix
      exact matrixLinear_toMatrix _
    have happ := LinearMap.congr_fun hmap (baseCoordinates Q delta)
    simpa using congrFun happ j
  rw [hfirst]
  congr 1
  apply Finset.sum_congr rfl
  intro a ha
  simp [auxiliaryCoordinates, mul_comm]

/-- Residual equivalence of augmented points implies residual equivalence of
their original-coordinate parts. -/
theorem sameResidual_baseCoordinates
    (pi : R) (Q : Finset Aux) (base z : Sum ι Q → R)
    (h : SameResidual pi base z) :
    SameResidual pi (baseCoordinates Q base) (baseCoordinates Q z) := by
  unfold SameResidual at h ⊢
  have hmapped := h.map (baseCoordinatesLinear Q)
  change PowDivisible pi 1 (baseCoordinates Q (z - base)) at hmapped
  have hcoord : baseCoordinates Q (z - base) =
      baseCoordinates Q z - baseCoordinates Q base := rfl
  rw [hcoord] at hmapped
  exact hmapped

/-- The augmented Jacobian is stable modulo the same power as a change of base
point.  Auxiliary columns contribute zero to the difference. -/
theorem augmentedJacobianMatrix_sub_powDivisible
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (pi : R) {n : ℕ} (z z₀ : Sum ι Q → R)
    (hzz₀ : PowDivisible pi n (z - z₀)) :
    EntrywisePowDivisible pi n
      (augmentedJacobianMatrix system column Q z -
        augmentedJacobianMatrix system column Q z₀) := by
  intro j s
  cases s with
  | inl i =>
      simp only [Matrix.sub_apply, augmentedJacobianMatrix_apply_inl]
      have hbase : PowDivisible pi n
          (baseCoordinates Q z - baseCoordinates Q z₀) := by
        have hmapped := hzz₀.map (baseCoordinatesLinear Q)
        change PowDivisible pi n (baseCoordinates Q (z - z₀)) at hmapped
        have hcoord : baseCoordinates Q (z - z₀) =
            baseCoordinates Q z - baseCoordinates Q z₀ := rfl
        rw [hcoord] at hmapped
        exact hmapped
      exact Expr.deriv_sub_deriv_powDivisible
        (system j) pi (baseCoordinates Q z) (baseCoordinates Q z₀)
        (Pi.single i 1) hbase
  | inr a =>
      simp [augmentedJacobianMatrix_apply_inr]

/-- A lifted right inverse at the augmented base point remains an approximate
right inverse throughout its residual fibre. -/
theorem exists_augmented_residualFiber_error_endomorphism
    (pi : R) (system : System ι κ R) (column : Aux → (κ → R))
    (Q : Finset Aux) (z₀ : Sum ι Q → R)
    (rightInvMatrix : Matrix (Sum ι Q) κ R)
    (hbase : EntrywisePowDivisible pi 1
      (augmentedJacobianMatrix system column Q z₀ * rightInvMatrix - 1)) :
    ∃ E : (Sum ι Q → R) → Module.End R (κ → R),
      ∀ z : Sum ι Q → R, SameResidual pi z₀ z →
        (augmentedDerivative system column Q z).comp
            (matrixLinear rightInvMatrix) =
          LinearMap.id + pi • E z := by
  classical
  have hex : ∀ z : Sum ι Q → R,
      ∃ Ez : Module.End R (κ → R), SameResidual pi z₀ z →
        (augmentedDerivative system column Q z).comp
            (matrixLinear rightInvMatrix) =
          LinearMap.id + pi • Ez := by
    intro z
    by_cases hz : SameResidual pi z₀ z
    · have hJdiff := augmentedJacobianMatrix_sub_powDivisible
          system column Q pi z z₀ hz
      have hprod := hJdiff.mul_right rightInvMatrix
      have htotal : EntrywisePowDivisible pi 1
          (augmentedJacobianMatrix system column Q z * rightInvMatrix - 1) := by
        have heq :
            augmentedJacobianMatrix system column Q z * rightInvMatrix - 1 =
              (augmentedJacobianMatrix system column Q z -
                  augmentedJacobianMatrix system column Q z₀) * rightInvMatrix +
                (augmentedJacobianMatrix system column Q z₀ * rightInvMatrix - 1) := by
          ext i j
          simp only [Matrix.sub_apply, Matrix.add_apply, Matrix.mul_apply]
          have hsum :
              (∑ a, (augmentedJacobianMatrix system column Q z i a -
                    augmentedJacobianMatrix system column Q z₀ i a) *
                    rightInvMatrix a j) =
                (∑ a, augmentedJacobianMatrix system column Q z i a *
                    rightInvMatrix a j) -
                  (∑ a, augmentedJacobianMatrix system column Q z₀ i a *
                    rightInvMatrix a j) := by
            rw [← Finset.sum_sub_distrib]
            apply Finset.sum_congr rfl
            intro a ha
            ring
          rw [hsum]
          ring
        rw [heq]
        exact hprod.add hbase
      obtain ⟨Emat, hEmat⟩ :=
        exists_error_matrix_of_entrywise_depth_one pi
          (augmentedJacobianMatrix system column Q z * rightInvMatrix) 1 htotal
      refine ⟨matrixLinear Emat, fun _ => ?_⟩
      calc
        (augmentedDerivative system column Q z).comp
            (matrixLinear rightInvMatrix) =
            matrixLinear
              (augmentedJacobianMatrix system column Q z * rightInvMatrix) := by
                rw [← matrixLinear_augmentedJacobianMatrix]
                exact matrixLinear_mul _ _
        _ = matrixLinear (1 + pi • Emat) := by rw [hEmat]
        _ = LinearMap.id + pi • matrixLinear Emat := by simp
    · exact ⟨0, fun hres => (hz hres).elim⟩
  choose E hE using hex
  exact ⟨E, hE⟩

/-- Hensel lifting for an original polynomial system augmented by genuine
linear auxiliary variables. -/
theorem exists_exact_augmented_solution_of_residual_matrix_rightInverse
    (pi : R) (system : System ι κ R) (column : Aux → (κ → R))
    (Q : Finset Aux) (x₀ : ι → R)
    (rightInvMatrix : Matrix (Sum ι Q) κ R)
    (hbase : EntrywisePowDivisible pi 1
      (augmentedJacobianMatrix system column Q (augmentedBasePoint Q x₀) *
        rightInvMatrix - 1))
    (hpi : IsNilpotent pi)
    (hx₀ : PowDivisible pi 1 (evalSystem system x₀)) :
    ∃ z : Sum ι Q → R,
      SameResidual pi (augmentedBasePoint Q x₀) z ∧
      augmentedEval system column Q z = 0 := by
  obtain ⟨E, hE⟩ :=
    exists_augmented_residualFiber_error_endomorphism
      pi system column Q (augmentedBasePoint Q x₀) rightInvMatrix hbase
  have hstart : PowDivisible pi 1
      (augmentedEval system column Q (augmentedBasePoint Q x₀)) := by
    simpa using hx₀
  exact exists_exact_solution_variableJacobian
    pi (augmentedEval system column Q)
    (augmentedDerivative system column Q)
    (matrixLinear rightInvMatrix) E (augmentedBasePoint Q x₀)
    hE hpi (augmented_remainder_raises_one pi system column Q) hstart

end

end Komorebi.StrongArtin.AuxiliaryAugmentedJacobian

#print axioms Komorebi.StrongArtin.AuxiliaryAugmentedJacobian.augmentedJacobianMatrix_sub_powDivisible
#print axioms Komorebi.StrongArtin.AuxiliaryAugmentedJacobian.exists_augmented_residualFiber_error_endomorphism
#print axioms Komorebi.StrongArtin.AuxiliaryAugmentedJacobian.exists_exact_augmented_solution_of_residual_matrix_rightInverse
