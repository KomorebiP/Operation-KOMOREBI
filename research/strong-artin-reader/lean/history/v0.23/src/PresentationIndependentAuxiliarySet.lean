import IntrinsicAuxiliaryRank

/-!
# Presentation-independent intrinsic auxiliary data

The auxiliary set is selected on the intrinsic Selmer obstruction space. Hence
the same set cuts any presentation of that obstruction down to its own relation
syzygies. Under conormal independence, two presentation kernels are identified
through the common auxiliary-coordinate space.
-/

namespace Komorebi.StrongArtin.PresentationIndependentAuxiliarySet

open Module
open Komorebi.StrongArtin.AdaptiveAuxiliarySelection
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.PresentationObstructionExactSequence
open Komorebi.StrongArtin.SelmerPresentationComparison
open Komorebi.StrongArtin.SyzygyCorrectedAuxiliarySelection
open Komorebi.StrongArtin.SyzygyCorrectedAuxiliaryMinimality

noncomputable section

universe u₁ u₂ v w₁ w₂ t₁ t₂ z a

variable {R₁ : Type u₁} {R₂ : Type u₂} {S : Type v}
  {ι₁ : Type w₁} {ι₂ : Type w₂} {σ₁ : Type t₁} {σ₂ : Type t₂}
  [CommRing R₁] [CommRing R₂] [Field S]
  [Algebra R₁ S] [Algebra R₂ S]
variable {H : Type z} [AddCommGroup H] [Module S H]
variable {Aux : Type a}

/-- One intrinsic auxiliary set works simultaneously for two different
presentations of the same arithmetic obstruction space. -/
theorem exists_common_syzygy_corrected_set
    [DecidableEq Aux] [FiniteDimensional S H]
    {P₁ : Algebra.Presentation R₁ S ι₁ σ₁}
    {P₂ : Algebra.Presentation R₂ S ι₂ σ₂}
    (D₁ : Datum P₁ H) (D₂ : Datum P₂ H)
    (I : OnePrimeSelectionInterface S H Aux) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, I.admissible a) ∧
      Q.card = Module.finrank S H ∧
      LinearMap.ker (rawEvaluationMap D₁ I Q) = relationSyzygies P₁ ∧
      Function.Surjective (rawEvaluationMap D₁ I Q) ∧
      LinearMap.ker (rawEvaluationMap D₂ I Q) = relationSyzygies P₂ ∧
      Function.Surjective (rawEvaluationMap D₂ I Q) := by
  obtain ⟨Q, hgood, hcard, -, hinj⟩ :=
    exists_relative_TaylorWiles_set_exact I
  refine ⟨Q, hgood, hcard, ?_, ?_, ?_, ?_⟩
  · exact ker_rawEvaluationMap_eq_relationSyzygies D₁ I Q hinj
  · exact rawEvaluationMap_surjective D₁ I Q hcard hinj
  · exact ker_rawEvaluationMap_eq_relationSyzygies D₂ I Q hinj
  · exact rawEvaluationMap_surjective D₂ I Q hcard hinj

/-- Under conormal independence, two presentation-dependent raw obstruction
kernels are canonically compared through the same selected auxiliary-coordinate
space. -/
def rawObstructionEquivOfIndependent
    {P₁ : Algebra.Presentation R₁ S ι₁ σ₁}
    {P₂ : Algebra.Presentation R₂ S ι₂ σ₂}
    (D₁ : Datum P₁ H) (D₂ : Datum P₂ H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    [FiniteDimensional S H]
    (hrel₁ : Function.Injective
      (Algebra.Presentation.differentials.hom₁ P₁))
    (hrel₂ : Function.Injective
      (Algebra.Presentation.differentials.hom₁ P₂))
    (hcard : Q.card = Module.finrank S H)
    (hinj : Function.Injective (evaluationMap I.localFunctional Q)) :
    presentationObstructionDual P₁ ≃ₗ[S]
      presentationObstructionDual P₂ :=
  (rawEvaluationEquiv_of_relationIndependent
    D₁ I Q hrel₁ hcard hinj).trans
  (rawEvaluationEquiv_of_relationIndependent
    D₂ I Q hrel₂ hcard hinj).symm

/-- The presentation comparison preserves every selected auxiliary coordinate. -/
theorem rawObstructionEquivOfIndependent_preserves_evaluation
    {P₁ : Algebra.Presentation R₁ S ι₁ σ₁}
    {P₂ : Algebra.Presentation R₂ S ι₂ σ₂}
    (D₁ : Datum P₁ H) (D₂ : Datum P₂ H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    [FiniteDimensional S H]
    (hrel₁ : Function.Injective
      (Algebra.Presentation.differentials.hom₁ P₁))
    (hrel₂ : Function.Injective
      (Algebra.Presentation.differentials.hom₁ P₂))
    (hcard : Q.card = Module.finrank S H)
    (hinj : Function.Injective (evaluationMap I.localFunctional Q))
    (x : presentationObstructionDual P₁) :
    rawEvaluationMap D₂ I Q
        (rawObstructionEquivOfIndependent D₁ D₂ I Q
          hrel₁ hrel₂ hcard hinj x) =
      rawEvaluationMap D₁ I Q x := by
  let e₁ := rawEvaluationEquiv_of_relationIndependent
    D₁ I Q hrel₁ hcard hinj
  let e₂ := rawEvaluationEquiv_of_relationIndependent
    D₂ I Q hrel₂ hcard hinj
  change e₂ (e₂.symm (e₁ x)) = e₁ x
  exact e₂.apply_symm_apply (e₁ x)

end

end Komorebi.StrongArtin.PresentationIndependentAuxiliarySet

#print axioms Komorebi.StrongArtin.PresentationIndependentAuxiliarySet.exists_common_syzygy_corrected_set
#print axioms Komorebi.StrongArtin.PresentationIndependentAuxiliarySet.rawObstructionEquivOfIndependent
#print axioms Komorebi.StrongArtin.PresentationIndependentAuxiliarySet.rawObstructionEquivOfIndependent_preserves_evaluation
