import PresentationIndependentAuxiliarySet

/-!
# Intrinsic syzygy-corrected Taylor--Wiles capstone

Auxiliary selection is performed on intrinsic cotangent H1 / Selmer.  For an
arbitrary presentation, the pulled-back arithmetic evaluations therefore cut
the raw transpose-Jacobian kernel down exactly to relation syzygies.  The
selected set has intrinsic cardinality and is minimal among all scalar families
with this property.  One intrinsic set works simultaneously for distinct
presentations of the same obstruction space.
-/

namespace Komorebi.StrongArtin.IntrinsicSyzygyCorrectedCapstone

open Module
open Komorebi.StrongArtin.AdaptiveAuxiliarySelection
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.PresentationObstructionExactSequence
open Komorebi.StrongArtin.SelmerPresentationComparison
open Komorebi.StrongArtin.SyzygyCorrectedAuxiliarySelection
open Komorebi.StrongArtin.SyzygyCorrectedAuxiliaryMinimality
open Komorebi.StrongArtin.IntrinsicAuxiliaryRank
open Komorebi.StrongArtin.PresentationIndependentAuxiliarySet

noncomputable section

universe u v w t z a

variable {R : Type u} {S : Type v} {ι : Type w} {σ : Type t}
  [CommRing R] [Field S] [Algebra R S]
variable {H : Type z} [AddCommGroup H] [Module S H]
variable {Aux : Type a}

/-- **Intrinsic syzygy-corrected auxiliary theorem.**  A one-prime interface
on the intrinsic Selmer obstruction space selects an admissible scalar family
whose pullback is short exact modulo presentation syzygies.  The family has
intrinsic cotangent-H1 cardinality and is minimal among all families cutting
the raw kernel exactly to those syzygies. -/
theorem exists_intrinsic_minimal_exact_auxiliary_set
    [DecidableEq Aux] [FiniteDimensional S H]
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, I.admissible a) ∧
      Q.card = Module.finrank S P.toExtension.H1Cotangent ∧
      LinearMap.ker (rawEvaluationMap D I Q) = relationSyzygies P ∧
      Function.Surjective (rawEvaluationMap D I Q) ∧
      Function.Exact (Submodule.subtype (relationSyzygies P))
        (rawEvaluationMap D I Q) ∧
      ∀ Q' : Finset Aux,
        LinearMap.ker (rawEvaluationMap D I Q') = relationSyzygies P →
        Q.card ≤ Q'.card := by
  obtain ⟨Q, hgood, hker, hsurj, hcardH, hminimal⟩ :=
    exists_cardinality_minimal_syzygy_corrected_set D I
  refine ⟨Q, hgood, ?_, hker, hsurj, ?_, hminimal⟩
  · exact hcardH.trans (finrank_selmer_eq_finrank_cotangentH1 D)
  · have hinj : Function.Injective (evaluationMap I.localFunctional Q) :=
      intrinsicEvaluation_injective_of_ker_raw_eq_syzygies D I Q hker
    exact exact_relationSyzygies_rawEvaluation D I Q hinj

end

end Komorebi.StrongArtin.IntrinsicSyzygyCorrectedCapstone

#print axioms Komorebi.StrongArtin.IntrinsicSyzygyCorrectedCapstone.exists_intrinsic_minimal_exact_auxiliary_set
