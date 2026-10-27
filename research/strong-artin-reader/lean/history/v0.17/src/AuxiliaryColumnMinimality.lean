import MinimalAuxiliaryColumnCount

/-!
# Minimality of auxiliary-column completion

Surjectivity of an augmented Jacobian forces the selected auxiliary column
functionals to separate the complete dual obstruction space.  Therefore every
surjective auxiliary completion uses at least the codimension of the original
Jacobian image.  The exact set constructed from the v0.15 interface is minimal.
-/

namespace Komorebi.StrongArtin.AuxiliaryColumnMinimality

open Komorebi.StrongArtin.AdaptiveAuxiliarySelection
open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation
open Komorebi.StrongArtin.MinimalAuxiliaryColumnCount

noncomputable section

variable {k U W Aux : Type*} [Field k]
  [AddCommGroup U] [Module k U]
  [AddCommGroup W] [Module k W]

/-- A surjective augmented Jacobian makes simultaneous evaluation of the
selected columns injective on the dual obstruction space. -/
theorem evaluationMap_injective_of_augmentedMap_surjective
    (J : U →ₗ[k] W) (column : Aux → W) (Q : Finset Aux)
    (hsurj : Function.Surjective (augmentedMap J column Q)) :
    Function.Injective
      (evaluationMap (k := k) (V := obstructionDual J)
        (columnFunctional J column) Q) := by
  rw [← selectedKernel_eq_bot_iff_evaluationMap_injective
    (k := k) (V := obstructionDual J)]
  apply le_antisymm
  · intro φ hφ
    apply Subtype.ext
    apply LinearMap.ext
    intro w
    obtain ⟨⟨u, a⟩, hw⟩ := hsurj w
    change φ.1 w = 0
    rw [← hw, augmentedMap_apply]
    simp only [map_add, map_sum, map_smul]
    have hJ : φ.1 (J u) = 0 :=
      (mem_obstructionDual J φ.1).mp φ.2 u
    rw [hJ, zero_add]
    apply Finset.sum_eq_zero
    intro i hi
    have hcol : φ.1 (column i.1) = 0 := by
      simpa [columnFunctional_apply] using hφ i.1 i.2
    rw [hcol, smul_zero]
  · exact bot_le

/-- Every surjective auxiliary completion has at least the Jacobian codimension
many selected scalar variables. -/
theorem finrank_quotient_range_le_card_of_augmentedMap_surjective
    [FiniteDimensional k W]
    (J : U →ₗ[k] W) (column : Aux → W) (Q : Finset Aux)
    (hsurj : Function.Surjective (augmentedMap J column Q)) :
    Module.finrank k (W ⧸ LinearMap.range J) ≤ Q.card := by
  have hinj := evaluationMap_injective_of_augmentedMap_surjective
    J column Q hsurj
  have hdim := finrank_le_card_of_evaluationMap_injective
    (k := k) (V := obstructionDual J)
    (columnFunctional J column) Q hinj
  rw [finrank_quotient_range_eq_finrank_obstructionDual J]
  exact hdim

/-- The exact auxiliary set obtained from a one-prime interface is cardinality-
minimal among all surjective completions by columns indexed by the same label
type. -/
theorem exists_cardinality_minimal_auxiliary_completion
    [DecidableEq Aux] [FiniteDimensional k W]
    (J : U →ₗ[k] W)
    (I : OnePrimeSelectionInterface k (obstructionDual J) Aux) :
    ∃ column : Aux → W, ∃ Q : Finset Aux,
      (∀ a : Aux, columnFunctional J column a = I.localFunctional a) ∧
      (∀ a ∈ Q, I.admissible a) ∧
      Function.Surjective (augmentedMap J column Q) ∧
      Q.card = Module.finrank k (W ⧸ LinearMap.range J) ∧
      ∀ (column' : Aux → W) (Q' : Finset Aux),
        Function.Surjective (augmentedMap J column' Q') → Q.card ≤ Q'.card := by
  obtain ⟨column, Q, hcolumn, hgood, hcard, hsurj⟩ :=
    exists_exact_codimension_auxiliary_columns J I
  refine ⟨column, Q, hcolumn, hgood, hsurj, hcard, ?_⟩
  intro column' Q' hsurj'
  rw [hcard]
  exact finrank_quotient_range_le_card_of_augmentedMap_surjective
    J column' Q' hsurj'

end

end Komorebi.StrongArtin.AuxiliaryColumnMinimality

#print axioms Komorebi.StrongArtin.AuxiliaryColumnMinimality.evaluationMap_injective_of_augmentedMap_surjective
#print axioms Komorebi.StrongArtin.AuxiliaryColumnMinimality.finrank_quotient_range_le_card_of_augmentedMap_surjective
#print axioms Komorebi.StrongArtin.AuxiliaryColumnMinimality.exists_cardinality_minimal_auxiliary_completion
