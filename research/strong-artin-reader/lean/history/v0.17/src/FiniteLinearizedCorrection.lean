import RelativeTaylorWilesJacobianCapstone

/-!
# Finite linearized correction after auxiliary-column completion

This module records the exact finite-depth consequence of a surjective augmented
Jacobian.  Every prescribed finite family of linearized error terms admits
simultaneous correction.  This is the linear algebra needed at each square-zero
lifting step; it does not assert nonlinear Hensel lifting or compatibility of
successive arithmetic deformation problems.
-/

namespace Komorebi.StrongArtin.FiniteLinearizedCorrection

open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.RelativeTaylorWilesJacobianCapstone

noncomputable section

variable {k U W Aux : Type*} [Field k]
  [AddCommGroup U] [Module k U]
  [AddCommGroup W] [Module k W]

/-- Surjectivity solves one affine linearized correction equation. -/
theorem exists_correction_of_surjective
    {X : Type*} [AddCommGroup X] [Module k X]
    (F : X →ₗ[k] W) (hF : Function.Surjective F) (error : W) :
    ∃ correction : X, F correction + error = 0 := by
  obtain ⟨correction, hcorrection⟩ := hF (-error)
  refine ⟨correction, ?_⟩
  rw [hcorrection]
  exact neg_add_cancel error

/-- A surjective linearized map solves any indexed family of error equations. -/
theorem exists_corrections_of_surjective
    {X I : Type*} [AddCommGroup X] [Module k X]
    (F : X →ₗ[k] W) (hF : Function.Surjective F)
    (error : I → W) :
    ∃ correction : I → X, ∀ i, F (correction i) + error i = 0 := by
  choose correction hcorrection using fun i => exists_correction_of_surjective F hF (error i)
  exact ⟨correction, hcorrection⟩

/-- A surjective augmented Jacobian solves every finite list of linearized
lifting errors using the original and auxiliary variables together. -/
theorem augmentedMap_solves_finite_linearized_errors
    (J : U →ₗ[k] W) (column : Aux → W) (Q : Finset Aux)
    (hQ : Function.Surjective (augmentedMap J column Q))
    {m : ℕ} (error : Fin m → W) :
    ∃ correction : Fin m → (U × (Q → k)),
      ∀ i, augmentedMap J column Q (correction i) + error i = 0 :=
  exists_corrections_of_surjective (augmentedMap J column Q) hQ error

/--
**Finite linearized lifting capstone.** If every nonzero dual obstruction is
seen by one admissible auxiliary column, then exactly the dual-obstruction
dimension many admissible columns may be chosen so that every finite family of
linearized errors admits corrections.
-/
theorem exists_exact_admissible_columns_solving_finite_errors
    [DecidableEq Aux] [FiniteDimensional k W]
    (J : U →ₗ[k] W) (column : Aux → W) (admissible : Aux → Prop)
    (hdetect : ∀ φ : obstructionDual J, φ ≠ 0 →
      ∃ a : Aux, admissible a ∧ columnFunctional J column a φ ≠ 0) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, admissible a) ∧
      Q.card = Module.finrank k (obstructionDual J) ∧
      Function.Surjective (augmentedMap J column Q) ∧
      ∀ {m : ℕ} (error : Fin m → W),
        ∃ correction : Fin m → (U × (Q → k)),
          ∀ i, augmentedMap J column Q (correction i) + error i = 0 := by
  obtain ⟨Q, hgood, hcard, hsurj⟩ :=
    exists_exact_admissible_columns_making_augmentedMap_surjective
      J column admissible hdetect
  refine ⟨Q, hgood, hcard, hsurj, ?_⟩
  intro m error
  exact augmentedMap_solves_finite_linearized_errors J column Q hsurj error

end

end Komorebi.StrongArtin.FiniteLinearizedCorrection

#print axioms Komorebi.StrongArtin.FiniteLinearizedCorrection.exists_correction_of_surjective
#print axioms Komorebi.StrongArtin.FiniteLinearizedCorrection.augmentedMap_solves_finite_linearized_errors
#print axioms Komorebi.StrongArtin.FiniteLinearizedCorrection.exists_exact_admissible_columns_solving_finite_errors
