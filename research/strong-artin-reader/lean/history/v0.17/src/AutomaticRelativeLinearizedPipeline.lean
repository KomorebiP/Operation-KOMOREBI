import SplitPrimeAuxiliarySelectionCapstone
import MinimalAuxiliaryColumnCount

/-!
# Automatic relative linearized pipeline

A split-prime one-class detection theorem on the global transverse quotient can
be transported across a Selmer--Jacobian equivalence.  Finite-dimensional
double duality then constructs compatible equation-space columns automatically.
The v0.15 selection theorem chooses exactly the Jacobian codimension many
admissible labels, completes the Jacobian, and supports every compatible finite-
depth linearized lift system.

No preselected columns or local-column comparison hypothesis remains.  The
arithmetic construction of the local functionals and the Selmer--Jacobian
equivalence remain explicit inputs.
-/

namespace Komorebi.StrongArtin.AutomaticRelativeLinearizedPipeline

open Komorebi.StrongArtin.SplitPrimeTransverseLocalization
open Komorebi.StrongArtin.SplitPrimeAuxiliarySelectionCapstone
open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation
open Komorebi.StrongArtin.MinimalAuxiliaryColumnCount

noncomputable section

variable {k U W H L Aux : Type*} [Field k]
  [AddCommGroup U] [Module k U]
  [AddCommGroup W] [Module k W]
  [AddCommGroup H] [Module k H]
  [AddCommGroup L] [Module k L]

/-- Transport a split-prime one-prime interface from the global transverse
quotient to the dual Jacobian obstruction space. -/
def transportedSplitPrimeInterface
    (J : U →ₗ[k] W)
    (d : H)
    (loc : Aux → H →ₗ[k] L)
    (hkill : ∀ a : Aux, loc a d = 0)
    (probe : Aux → Module.Dual k L)
    (admissible : Aux → Prop)
    (E : (H ⧸ cyclicLine (k := k) d) ≃ₗ[k] obstructionDual J)
    (hdetect : ∀ x : H ⧸ cyclicLine (k := k) d, x ≠ 0 →
      ∃ a : Aux, admissible a ∧
        transverseLocalFunctional (loc a) d (hkill a) (probe a) x ≠ 0) :
    OnePrimeSelectionInterface k (obstructionDual J) Aux where
  admissible := admissible
  localFunctional a :=
    (transverseLocalFunctional (loc a) d (hkill a) (probe a)).comp
      E.symm.toLinearMap
  detects := by
    intro φ hφ
    have hx : E.symm φ ≠ 0 := by
      intro hx
      apply hφ
      have := congrArg E hx
      simpa using this
    obtain ⟨a, ha, hlocal⟩ := hdetect (E.symm φ) hx
    exact ⟨a, ha, hlocal⟩

@[simp]
theorem transportedSplitPrimeInterface_localFunctional_apply
    (J : U →ₗ[k] W)
    (d : H)
    (loc : Aux → H →ₗ[k] L)
    (hkill : ∀ a : Aux, loc a d = 0)
    (probe : Aux → Module.Dual k L)
    (admissible : Aux → Prop)
    (E : (H ⧸ cyclicLine (k := k) d) ≃ₗ[k] obstructionDual J)
    (hdetect : ∀ x : H ⧸ cyclicLine (k := k) d, x ≠ 0 →
      ∃ a : Aux, admissible a ∧
        transverseLocalFunctional (loc a) d (hkill a) (probe a) x ≠ 0)
    (a : Aux) (φ : obstructionDual J) :
    (transportedSplitPrimeInterface J d loc hkill probe admissible E hdetect).localFunctional a φ =
      transverseLocalFunctional (loc a) d (hkill a) (probe a) (E.symm φ) :=
  rfl

/--
**Automatic relative linearized pipeline capstone.** Split-prime raw local
one-class detection and a Selmer--Jacobian equivalence automatically produce
compatible equation-space columns.  Exactly the original Jacobian codimension
many admissible labels complete the Jacobian and propagate every compatible
state-dependent linearized lift system through arbitrary finite depth.
-/
theorem exists_automatic_relative_finite_depth_pipeline
    [DecidableEq Aux] [FiniteDimensional k W]
    (J : U →ₗ[k] W)
    (d : H)
    (loc : Aux → H →ₗ[k] L)
    (hkill : ∀ a : Aux, loc a d = 0)
    (probe : Aux → Module.Dual k L)
    (admissible : Aux → Prop)
    (E : (H ⧸ cyclicLine (k := k) d) ≃ₗ[k] obstructionDual J)
    (hdetect : ∀ x : H ⧸ cyclicLine (k := k) d, x ≠ 0 →
      ∃ a : Aux, admissible a ∧
        transverseLocalFunctional (loc a) d (hkill a) (probe a) x ≠ 0) :
    ∃ column : Aux → W, ∃ Q : Finset Aux,
      (∀ a : Aux,
        columnFunctional J column a =
          (transverseLocalFunctional (loc a) d (hkill a) (probe a)).comp
            E.symm.toLinearMap) ∧
      (∀ a ∈ Q, admissible a) ∧
      Q.card = Module.finrank k (W ⧸ LinearMap.range J) ∧
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
  let I := transportedSplitPrimeInterface
    J d loc hkill probe admissible E hdetect
  obtain ⟨column, Q, hcolumn, hgood, hcard, hsurj, hlift⟩ :=
    exists_exact_codimension_columns_supporting_finite_depth_lifts J I
  refine ⟨column, Q, ?_, hgood, hcard, hsurj, hlift⟩
  intro a
  exact hcolumn a

end

end Komorebi.StrongArtin.AutomaticRelativeLinearizedPipeline

#print axioms Komorebi.StrongArtin.AutomaticRelativeLinearizedPipeline.transportedSplitPrimeInterface
#print axioms Komorebi.StrongArtin.AutomaticRelativeLinearizedPipeline.exists_automatic_relative_finite_depth_pipeline
