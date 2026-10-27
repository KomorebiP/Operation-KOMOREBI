import FiniteLinearizedCorrection

/-!
# Finite-depth linearized lift systems

A surjective linearized correction map can be used recursively when the error at
the next stage depends on the state reached at the previous stage.  This is the
abstract induction underlying repeated square-zero corrections.

The theorem is deliberately conditional on a `step_valid` implication.  It does
not prove that a nonlinear deformation functor has this Taylor expansion, that
the same Jacobian controls every arithmetic depth, or that inverse-limit
compatibility holds.
-/

namespace Komorebi.StrongArtin.FiniteDepthLinearizedLiftSystem

open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.RelativeTaylorWilesJacobianCapstone
open Komorebi.StrongArtin.FiniteLinearizedCorrection

noncomputable section

variable {k U W Aux : Type*} [Field k]
  [AddCommGroup U] [Module k U]
  [AddCommGroup W] [Module k W]

/-- A surjective correction operator propagates validity through every prescribed
finite depth, even when each new error depends on the current state. -/
theorem exists_valid_state_at_depth
    {X State : Type*} [AddCommGroup X] [Module k X]
    (F : X →ₗ[k] W) (hF : Function.Surjective F)
    (initial : State)
    (defect : ℕ → State → W)
    (update : ℕ → State → X → State)
    (Valid : ℕ → State → Prop)
    (hinitial : Valid 0 initial)
    (hstep : ∀ n s correction,
      Valid n s →
      F correction + defect n s = 0 →
      Valid (n + 1) (update n s correction)) :
    ∀ N : ℕ, ∃ state : State, Valid N state := by
  intro N
  induction N with
  | zero => exact ⟨initial, hinitial⟩
  | succ N ih =>
      obtain ⟨state, hstate⟩ := ih
      obtain ⟨correction, hcorrection⟩ :=
        exists_correction_of_surjective F hF (defect N state)
      exact ⟨update N state correction,
        hstep N state correction hstate hcorrection⟩

/--
**Finite-depth relative lifting capstone.** Exact admissible auxiliary columns
can be selected so that every state-dependent linearized lift system governed by
the resulting augmented Jacobian reaches every finite depth.
-/
theorem exists_exact_admissible_columns_supporting_finite_depth_lifts
    [DecidableEq Aux] [FiniteDimensional k W]
    (J : U →ₗ[k] W) (column : Aux → W) (admissible : Aux → Prop)
    (hdetect : ∀ φ : obstructionDual J, φ ≠ 0 →
      ∃ a : Aux, admissible a ∧ columnFunctional J column a φ ≠ 0) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, admissible a) ∧
      Q.card = Module.finrank k (obstructionDual J) ∧
      Function.Surjective (augmentedMap J column Q) ∧
      ∀ {State : Type*}
        (initial : State)
        (defect : ℕ → State → W)
        (update : ℕ → State → (U × (Q → k)) → State)
        (Valid : ℕ → State → Prop),
        Valid 0 initial →
        (∀ n s correction,
          Valid n s →
          augmentedMap J column Q correction + defect n s = 0 →
          Valid (n + 1) (update n s correction)) →
        ∀ N : ℕ, ∃ state : State, Valid N state := by
  obtain ⟨Q, hgood, hcard, hsurj⟩ :=
    exists_exact_admissible_columns_making_augmentedMap_surjective
      J column admissible hdetect
  refine ⟨Q, hgood, hcard, hsurj, ?_⟩
  intro State initial defect update Valid hinitial hstep N
  exact exists_valid_state_at_depth
    (augmentedMap J column Q) hsurj initial defect update Valid
    hinitial hstep N

end

end Komorebi.StrongArtin.FiniteDepthLinearizedLiftSystem

#print axioms Komorebi.StrongArtin.FiniteDepthLinearizedLiftSystem.exists_valid_state_at_depth
#print axioms Komorebi.StrongArtin.FiniteDepthLinearizedLiftSystem.exists_exact_admissible_columns_supporting_finite_depth_lifts
