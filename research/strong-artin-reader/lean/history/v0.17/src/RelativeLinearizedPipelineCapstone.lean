import SplitPrimeAuxiliarySelectionCapstone
import FiniteDepthLinearizedLiftSystem

/-!
# Relative linearized Strong Artin pipeline capstone

This module connects the remaining interfaces in the linearized argument.
Assume the global transverse dual-Selmer quotient is identified with the dual
Jacobian obstruction space and that raw split-prime local evaluations agree
with evaluation on the corresponding auxiliary Jacobian columns.  Then
one-prime detection selects exactly enough admissible columns, makes the
augmented Jacobian surjective, and propagates every compatible linearized lift
system through every finite depth.

The Selmer--Jacobian identification and local-column compatibility are explicit
hypotheses; this module does not prove them arithmetically.
-/

namespace Komorebi.StrongArtin.RelativeLinearizedPipelineCapstone

open Komorebi.StrongArtin.SplitPrimeTransverseLocalization
open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.FiniteDepthLinearizedLiftSystem

noncomputable section

variable {k U W H L Aux : Type*} [Field k]
  [AddCommGroup U] [Module k U]
  [AddCommGroup W] [Module k W]
  [AddCommGroup H] [Module k H]
  [AddCommGroup L] [Module k L]

/-- Raw split-prime one-class detection transfers across a linear equivalence to
admissible auxiliary-column detection on the dual Jacobian obstruction. -/
theorem column_detection_of_splitPrime_detection
    (J : U →ₗ[k] W) (column : Aux → W)
    (d : H)
    (loc : Aux → H →ₗ[k] L)
    (hkill : ∀ a : Aux, loc a d = 0)
    (probe : Aux → Module.Dual k L)
    (admissible : Aux → Prop)
    (E : (H ⧸ cyclicLine (k := k) d) ≃ₗ[k] obstructionDual J)
    (hcompat : ∀ a x,
      transverseLocalFunctional (loc a) d (hkill a) (probe a) x =
        columnFunctional J column a (E x))
    (hdetect : ∀ x : H ⧸ cyclicLine (k := k) d, x ≠ 0 →
      ∃ a : Aux, admissible a ∧
        transverseLocalFunctional (loc a) d (hkill a) (probe a) x ≠ 0) :
    ∀ φ : obstructionDual J, φ ≠ 0 →
      ∃ a : Aux, admissible a ∧ columnFunctional J column a φ ≠ 0 := by
  intro φ hφ
  have hx : E.symm φ ≠ 0 := by
    intro hx
    apply hφ
    have h := congrArg E hx
    simpa using h
  obtain ⟨a, ha, hraw⟩ := hdetect (E.symm φ) hx
  refine ⟨a, ha, ?_⟩
  have heq :
      transverseLocalFunctional (loc a) d (hkill a) (probe a) (E.symm φ) =
        columnFunctional J column a φ := by
    simpa using hcompat a (E.symm φ)
  rw [← heq]
  exact hraw

/--
**Relative linearized pipeline capstone.** Under the explicit Selmer--Jacobian
and local-column comparison hypotheses, raw split-prime one-prime detection
produces exactly enough admissible auxiliary variables for surjectivity and
supports every compatible state-dependent lift system through all finite
depths.
-/
theorem exists_auxiliary_set_supporting_relative_finite_depth_pipeline
    [DecidableEq Aux] [FiniteDimensional k W]
    (J : U →ₗ[k] W) (column : Aux → W)
    (d : H)
    (loc : Aux → H →ₗ[k] L)
    (hkill : ∀ a : Aux, loc a d = 0)
    (probe : Aux → Module.Dual k L)
    (admissible : Aux → Prop)
    (E : (H ⧸ cyclicLine (k := k) d) ≃ₗ[k] obstructionDual J)
    (hcompat : ∀ a x,
      transverseLocalFunctional (loc a) d (hkill a) (probe a) x =
        columnFunctional J column a (E x))
    (hdetect : ∀ x : H ⧸ cyclicLine (k := k) d, x ≠ 0 →
      ∃ a : Aux, admissible a ∧
        transverseLocalFunctional (loc a) d (hkill a) (probe a) x ≠ 0) :
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
  apply exists_exact_admissible_columns_supporting_finite_depth_lifts
    J column admissible
  exact column_detection_of_splitPrime_detection
    J column d loc hkill probe admissible E hcompat hdetect

end

end Komorebi.StrongArtin.RelativeLinearizedPipelineCapstone

#print axioms Komorebi.StrongArtin.RelativeLinearizedPipelineCapstone.column_detection_of_splitPrime_detection
#print axioms Komorebi.StrongArtin.RelativeLinearizedPipelineCapstone.exists_auxiliary_set_supporting_relative_finite_depth_pipeline
