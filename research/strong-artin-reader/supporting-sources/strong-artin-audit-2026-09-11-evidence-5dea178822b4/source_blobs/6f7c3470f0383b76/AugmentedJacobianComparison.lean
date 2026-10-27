import PolynomialAuxiliaryAugmentation
import Mathlib.Data.Fintype.BigOperators

/-!
# Coordinate comparison for an auxiliary-augmented polynomial Jacobian

Functions on a sum of variable types are linearly equivalent to a pair of
function spaces.  Under this equivalence, the standard-coordinate linear map of
the augmented Jacobian matrix is exactly the original Jacobian together with
the auxiliary column map.
-/

namespace Komorebi.StrongArtin.AugmentedJacobianComparison

open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.PolynomialAuxiliaryAugmentation
open Komorebi.StrongArtin.AuxiliaryColumnCompletion

noncomputable section

variable {k R ι κ α Aux : Type*}

/-- Functions on a sum split linearly into their two restrictions. -/
def sumArrowLinearEquiv [Semiring k] :
    (Sum ι α → k) ≃ₗ[k] ((ι → k) × (α → k)) where
  toFun z := (fun i => z (.inl i), fun a => z (.inr a))
  invFun z := Sum.elim z.1 z.2
  left_inv z := by
    funext s
    cases s <;> rfl
  right_inv z := by
    ext <;> rfl
  map_add' x y := by
    ext <;> rfl
  map_smul' a x := by
    ext <;> rfl

@[simp] theorem sumArrowLinearEquiv_apply_inl [Semiring k]
    (z : Sum ι α → k) (i : ι) :
    (sumArrowLinearEquiv (k := k) (ι := ι) (α := α) z).1 i = z (.inl i) := rfl

@[simp] theorem sumArrowLinearEquiv_apply_inr [Semiring k]
    (z : Sum ι α → k) (a : α) :
    (sumArrowLinearEquiv (k := k) (ι := ι) (α := α) z).2 a = z (.inr a) := rfl

/-- Linear combination of all columns indexed by one finite type. -/
def allAuxiliaryMap [Field k] [Fintype α]
    (column : α → (κ → k)) : (α → k) →ₗ[k] (κ → k) :=
  Fintype.linearCombination k column

@[simp] theorem allAuxiliaryMap_apply [Field k] [Fintype α]
    (column : α → (κ → k)) (a : α → k) :
    allAuxiliaryMap column a = ∑ i : α, a i • column i := rfl

/-- Original Jacobian together with every column in a finite index type. -/
def fullAugmentedMap [Field k] [Fintype α]
    (J : (ι → k) →ₗ[k] (κ → k)) (column : α → (κ → k)) :
    ((ι → k) × (α → k)) →ₗ[k] (κ → k) :=
  J.coprod (allAuxiliaryMap column)

@[simp] theorem fullAugmentedMap_apply [Field k] [Fintype α]
    (J : (ι → k) →ₗ[k] (κ → k)) (column : α → (κ → k))
    (u : ι → k) (a : α → k) :
    fullAugmentedMap J column (u, a) =
      J u + ∑ i : α, a i • column i := rfl

/-- Explicit coordinate formula for the standard-basis matrix map. -/
theorem matrixLinear_apply_explicit
    [Field k]
    [Fintype ι] [DecidableEq ι]
    [Fintype κ] [DecidableEq κ]
    (M : Matrix κ ι k) (z : ι → k) (j : κ) :
    matrixLinear M z j = ∑ i : ι, M j i * z i := by
  simp only [matrixLinear, Matrix.toLin_apply, Pi.basisFun_repr, Pi.basisFun_apply,
    Matrix.mulVec_apply, dotProduct, Finset.sum_apply, Pi.smul_apply]
  rw [Finset.sum_eq_single j]
  · simp
  · intro b hb hbj
    simp [hbj]
  · simp

/-- The standard matrix map for adjoined columns is the full augmented map in
sum-of-variable coordinates. -/
theorem matrixLinear_augmentedMatrix
    [Field k]
    [Fintype ι] [DecidableEq ι]
    [Fintype κ] [DecidableEq κ]
    [Fintype α] [DecidableEq α]
    (J : Matrix κ ι k) (column : α → (κ → k)) :
    matrixLinear (augmentedMatrix J column) =
      (fullAugmentedMap (matrixLinear J) column).comp
        (sumArrowLinearEquiv (k := k) (ι := ι) (α := α)).toLinearMap := by
  apply LinearMap.ext
  intro z
  funext j
  simp [matrixLinear_apply_explicit, augmentedMatrix, Fintype.sum_sum_type,
    fullAugmentedMap, allAuxiliaryMap, sumArrowLinearEquiv,
    Fintype.linearCombination_apply, smul_eq_mul, mul_comm]

/-- Mapping coefficients commutes with adjoining columns. -/
theorem map_augmentedMatrix
    [CommRing R] [Field k]
    (q : R →+* k) (J : Matrix κ ι R) (column : α → (κ → R)) :
    (augmentedMatrix J column).map q =
      augmentedMatrix (J.map q) (fun a j => q (column a j)) := by
  ext j s
  cases s <;> rfl

/-- Surjectivity of the product-coordinate augmented map gives surjectivity of
the single sum-coordinate matrix map. -/
theorem matrixLinear_augmentedMatrix_surjective
    [Field k]
    [Fintype ι] [DecidableEq ι]
    [Fintype κ] [DecidableEq κ]
    [Fintype α] [DecidableEq α]
    (J : Matrix κ ι k) (column : α → (κ → k))
    (hsurj : Function.Surjective
      (fullAugmentedMap (matrixLinear J) column)) :
    Function.Surjective (matrixLinear (augmentedMatrix J column)) := by
  rw [matrixLinear_augmentedMatrix]
  exact hsurj.comp
    (sumArrowLinearEquiv (k := k) (ι := ι) (α := α)).surjective

/-- Selected-column form matching the `augmentedMap` used by v0.16--v0.17. -/
theorem matrixLinear_augmentedMatrix_surjective_of_selected
    [Field k]
    [Fintype ι] [DecidableEq ι]
    [Fintype κ] [DecidableEq κ]
    {Aux : Type*} [DecidableEq Aux]
    (J : Matrix κ ι k) (column : Aux → (κ → k)) (Q : Finset Aux)
    (hsurj : Function.Surjective
      (augmentedMap (matrixLinear J) column Q)) :
    Function.Surjective
      (matrixLinear (augmentedMatrix J (fun a : Q => column a.1))) := by
  apply matrixLinear_augmentedMatrix_surjective J (fun a : Q => column a.1)
  simpa [fullAugmentedMap, allAuxiliaryMap, augmentedMap, auxiliaryMap] using hsurj

/-- An explicit polynomial augmentation has surjective residual Jacobian as
soon as the corresponding selected-column map is surjective. -/
theorem residualJacobian_augmentedSystem_surjective
    [CommRing R] [Field k]
    [Fintype ι] [DecidableEq ι]
    [Fintype κ] [DecidableEq κ]
    [Fintype α] [DecidableEq α]
    (q : R →+* k)
    (system : System ι κ R) (column : α → (κ → R)) (x : ι → R)
    (hsurj : Function.Surjective
      (fullAugmentedMap
        (matrixLinear ((jacobianMatrix system x).map q))
        (fun a j => q (column a j)))) :
    Function.Surjective
      (matrixLinear
        ((jacobianMatrix (augmentedSystem system column) (zeroAuxPoint x)).map q)) := by
  rw [jacobianMatrix_augmentedSystem, map_augmentedMatrix]
  exact matrixLinear_augmentedMatrix_surjective
    ((jacobianMatrix system x).map q)
    (fun a j => q (column a j)) hsurj

end

end Komorebi.StrongArtin.AugmentedJacobianComparison

#print axioms Komorebi.StrongArtin.AugmentedJacobianComparison.matrixLinear_augmentedMatrix
#print axioms Komorebi.StrongArtin.AugmentedJacobianComparison.residualJacobian_augmentedSystem_surjective
