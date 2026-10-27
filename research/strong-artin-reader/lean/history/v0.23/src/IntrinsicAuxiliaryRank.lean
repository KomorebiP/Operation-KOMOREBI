import SyzygyCorrectedAuxiliaryMinimality

/-!
# Intrinsic auxiliary rank

The number of arithmetic auxiliary conditions is the dimension of intrinsic
cotangent H1, not the dimension of a redundant transpose-Jacobian kernel.
Presentation redundancy contributes a separate syzygy summand to the raw
kernel dimension.
-/

namespace Komorebi.StrongArtin.IntrinsicAuxiliaryRank

open Module
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.PresentationObstructionExactSequence
open Komorebi.StrongArtin.SelmerPresentationComparison
open Komorebi.StrongArtin.SyzygyCorrectedAuxiliarySelection
open Komorebi.StrongArtin.SyzygyCorrectedAuxiliaryMinimality

noncomputable section

universe u v w t z a

variable {R : Type u} {S : Type v} {ι : Type w} {σ : Type t}
  [CommRing R] [Field S] [Algebra R S]
variable {H : Type z} [AddCommGroup H] [Module S H]
variable {Aux : Type a}

/-- The arithmetic Selmer dimension equals the intrinsic cotangent-H1
dimension supplied by the comparison datum. -/
theorem finrank_selmer_eq_finrank_cotangentH1
    {P : Algebra.Presentation R S ι σ} (D : Datum P H) :
    Module.finrank S H = Module.finrank S P.toExtension.H1Cotangent :=
  D.intrinsicEquiv.finrank_eq.symm

/-- A syzygy-corrected exact auxiliary family has cardinality equal to intrinsic
cotangent H1, independently of the number of redundant presentation
relations. -/
theorem exists_intrinsic_rank_auxiliary_set
    [DecidableEq Aux] [FiniteDimensional S H]
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, I.admissible a) ∧
      Q.card = Module.finrank S P.toExtension.H1Cotangent ∧
      LinearMap.ker (rawEvaluationMap D I Q) = relationSyzygies P ∧
      Function.Surjective (rawEvaluationMap D I Q) := by
  obtain ⟨Q, hgood, hcard, hker, hsurj, -⟩ :=
    exists_syzygy_corrected_TaylorWiles_set D I
  refine ⟨Q, hgood, ?_, hker, hsurj⟩
  exact hcard.trans (finrank_selmer_eq_finrank_cotangentH1 D)

/-- Rank-nullity for a syzygy-corrected selected evaluation: the raw
presentation kernel splits numerically into intrinsic auxiliary coordinates
plus relation redundancy. -/
theorem card_add_finrank_syzygies_eq_finrank_raw
    {P : Algebra.Presentation R S ι σ}
    [FiniteDimensional S (presentationObstructionDual P)]
    (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    (hker : LinearMap.ker (rawEvaluationMap D I Q) = relationSyzygies P)
    (hsurj : Function.Surjective (rawEvaluationMap D I Q)) :
    Q.card + Module.finrank S (relationSyzygies P) =
      Module.finrank S (presentationObstructionDual P) := by
  have h := LinearMap.finrank_range_add_finrank_ker
    (K := S) (V := presentationObstructionDual P) (V₂ := (Q → S))
    (rawEvaluationMap D I Q)
  rw [LinearMap.range_eq_top.mpr hsurj, hker] at h
  simpa [Module.finrank_fintype_fun_eq_card, Fintype.card_coe]
    using h

/-- The exact family constructed from a one-prime interface realizes the
intrinsic/raw/syzygy dimension formula. -/
theorem exists_intrinsic_rank_decomposition
    [DecidableEq Aux] [FiniteDimensional S H]
    {P : Algebra.Presentation R S ι σ}
    [FiniteDimensional S (presentationObstructionDual P)]
    (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, I.admissible a) ∧
      Q.card = Module.finrank S P.toExtension.H1Cotangent ∧
      LinearMap.ker (rawEvaluationMap D I Q) = relationSyzygies P ∧
      Function.Surjective (rawEvaluationMap D I Q) ∧
      Q.card + Module.finrank S (relationSyzygies P) =
        Module.finrank S (presentationObstructionDual P) := by
  obtain ⟨Q, hgood, hcard, hker, hsurj⟩ :=
    exists_intrinsic_rank_auxiliary_set D I
  exact ⟨Q, hgood, hcard, hker, hsurj,
    card_add_finrank_syzygies_eq_finrank_raw D I Q hker hsurj⟩

end

end Komorebi.StrongArtin.IntrinsicAuxiliaryRank

#print axioms Komorebi.StrongArtin.IntrinsicAuxiliaryRank.finrank_selmer_eq_finrank_cotangentH1
#print axioms Komorebi.StrongArtin.IntrinsicAuxiliaryRank.exists_intrinsic_rank_auxiliary_set
#print axioms Komorebi.StrongArtin.IntrinsicAuxiliaryRank.exists_intrinsic_rank_decomposition
