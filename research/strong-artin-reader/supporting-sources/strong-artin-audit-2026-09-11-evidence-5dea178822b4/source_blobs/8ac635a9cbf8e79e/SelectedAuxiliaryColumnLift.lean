import AugmentedJacobianComparison

/-!
# Lifting selected residual auxiliary columns

A finite selected family of residual equation-space columns can be lifted
entrywise along any surjective residue-field homomorphism.  The lifted columns
produce an explicit polynomial augmentation whose residual coordinate Jacobian
is surjective whenever the abstract selected-column augmented map is surjective.
-/

namespace Komorebi.StrongArtin.SelectedAuxiliaryColumnLift

open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.PolynomialAuxiliaryAugmentation
open Komorebi.StrongArtin.AugmentedJacobianComparison
open Komorebi.StrongArtin.AuxiliaryColumnCompletion

noncomputable section

variable {R k ι κ Aux : Type*}

/-- Lift every entry of the selected residual columns along a surjective ring
homomorphism. -/
theorem exists_selected_column_lift
    [CommRing R] [Field k]
    (q : R →+* k) (hq : Function.Surjective q)
    (column : Aux → (κ → k)) (Q : Finset Aux) :
    ∃ columnR : Q → (κ → R),
      ∀ a : Q, ∀ j : κ, q (columnR a j) = column a.1 j := by
  have hpre : ∀ a : Q, ∀ j : κ,
      ∃ x : R, q x = column a.1 j := by
    intro a j
    exact hq (column a.1 j)
  choose columnR hcolumn using hpre
  exact ⟨columnR, hcolumn⟩

/-- The residue of a lifted selected-column family is exactly the selected
subfamily of the original residual columns. -/
theorem mapped_selected_column_eq
    [CommRing R] [Field k]
    (q : R →+* k)
    (column : Aux → (κ → k)) (Q : Finset Aux)
    (columnR : Q → (κ → R))
    (hcolumn : ∀ a : Q, ∀ j : κ,
      q (columnR a j) = column a.1 j) :
    (fun a : Q => fun j : κ => q (columnR a j)) =
      (fun a : Q => column a.1) := by
  funext a j
  exact hcolumn a j

/-- A selected residual augmented map that is surjective remains the residual
coordinate Jacobian of any entrywise lift of those columns. -/
theorem residualJacobian_augmentedSystem_surjective_of_selected_lift
    [CommRing R] [Field k]
    [Fintype ι] [DecidableEq ι]
    [Fintype κ] [DecidableEq κ]
    [DecidableEq Aux]
    (q : R →+* k)
    (system : System ι κ R) (x : ι → R)
    (column : Aux → (κ → k)) (Q : Finset Aux)
    (columnR : Q → (κ → R))
    (hcolumn : ∀ a : Q, ∀ j : κ,
      q (columnR a j) = column a.1 j)
    (hsurj : Function.Surjective
      (augmentedMap
        (matrixLinear ((jacobianMatrix system x).map q)) column Q)) :
    Function.Surjective
      (matrixLinear
        ((jacobianMatrix (augmentedSystem system columnR)
          (zeroAuxPoint x)).map q)) := by
  rw [jacobianMatrix_augmentedSystem, map_augmentedMatrix]
  rw [mapped_selected_column_eq q column Q columnR hcolumn]
  exact matrixLinear_augmentedMatrix_surjective_of_selected
    ((jacobianMatrix system x).map q) column Q hsurj

end

end Komorebi.StrongArtin.SelectedAuxiliaryColumnLift

#print axioms Komorebi.StrongArtin.SelectedAuxiliaryColumnLift.exists_selected_column_lift
#print axioms Komorebi.StrongArtin.SelectedAuxiliaryColumnLift.residualJacobian_augmentedSystem_surjective_of_selected_lift
