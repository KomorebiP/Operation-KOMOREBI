import ObstructionColumnQuotient

/-!
# Exact auxiliary-column count as a Jacobian codimension

The number of scalar auxiliary conditions selected by the v0.15 interface is
exactly the dimension of the equation-space quotient by the original Jacobian
image.  This identifies the Taylor--Wiles count with a coordinate-free
linearized defect dimension.
-/

namespace Komorebi.StrongArtin.MinimalAuxiliaryColumnCount

open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation
open Komorebi.StrongArtin.ObstructionColumnQuotient

noncomputable section

variable {k U W Aux : Type*} [Field k]
  [AddCommGroup U] [Module k U]
  [AddCommGroup W] [Module k W]

/-- The dual obstruction dimension equals the codimension of the original
Jacobian image. -/
theorem finrank_quotient_range_eq_finrank_obstructionDual
    [FiniteDimensional k W] (J : U →ₗ[k] W) :
    Module.finrank k (W ⧸ LinearMap.range J) =
      Module.finrank k (obstructionDual J) := by
  calc
    Module.finrank k (W ⧸ LinearMap.range J) =
        Module.finrank k (Module.Dual k (obstructionDual J)) :=
      (quotientRangeEquivObstructionDual J).finrank_eq
    _ = Module.finrank k (obstructionDual J) :=
      (@Subspace.dual_finrank_eq k (obstructionDual J) _ _ _)

/-- Every abstract one-prime interface admits exactly the Jacobian-codimension
many admissible columns, and those columns make the augmented Jacobian
surjective. -/
theorem exists_exact_codimension_auxiliary_columns
    [DecidableEq Aux] [FiniteDimensional k W]
    (J : U →ₗ[k] W)
    (I : OnePrimeSelectionInterface k (obstructionDual J) Aux) :
    ∃ column : Aux → W, ∃ Q : Finset Aux,
      (∀ a : Aux, columnFunctional J column a = I.localFunctional a) ∧
      (∀ a ∈ Q, I.admissible a) ∧
      Q.card = Module.finrank k (W ⧸ LinearMap.range J) ∧
      Function.Surjective (augmentedMap J column Q) := by
  obtain ⟨column, Q, hcolumn, hgood, hcard, hsurj⟩ :=
    exists_representing_columns_and_surjective_auxiliary_set J I
  refine ⟨column, Q, hcolumn, hgood, ?_, hsurj⟩
  rw [finrank_quotient_range_eq_finrank_obstructionDual J]
  exact hcard

/-- The same exact codimension count supplies corrections for every compatible
state-dependent finite-depth linearized lift system. -/
theorem exists_exact_codimension_columns_supporting_finite_depth_lifts
    [DecidableEq Aux] [FiniteDimensional k W]
    (J : U →ₗ[k] W)
    (I : OnePrimeSelectionInterface k (obstructionDual J) Aux) :
    ∃ column : Aux → W, ∃ Q : Finset Aux,
      (∀ a : Aux, columnFunctional J column a = I.localFunctional a) ∧
      (∀ a ∈ Q, I.admissible a) ∧
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
  obtain ⟨column, Q, hcolumn, hgood, hcard, hsurj, hlift⟩ :=
    exists_representing_columns_supporting_finite_depth_lifts J I
  refine ⟨column, Q, hcolumn, hgood, ?_, hsurj, hlift⟩
  rw [finrank_quotient_range_eq_finrank_obstructionDual J]
  exact hcard

end

end Komorebi.StrongArtin.MinimalAuxiliaryColumnCount

#print axioms Komorebi.StrongArtin.MinimalAuxiliaryColumnCount.finrank_quotient_range_eq_finrank_obstructionDual
#print axioms Komorebi.StrongArtin.MinimalAuxiliaryColumnCount.exists_exact_codimension_auxiliary_columns
#print axioms Komorebi.StrongArtin.MinimalAuxiliaryColumnCount.exists_exact_codimension_columns_supporting_finite_depth_lifts
