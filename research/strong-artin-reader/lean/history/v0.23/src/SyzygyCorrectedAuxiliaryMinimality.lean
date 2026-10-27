import SyzygyCorrectedAuxiliarySelection

/-!
# Minimality of syzygy-corrected auxiliary selection

A selected family whose pullback kernel is exactly relation redundancy must
have at least the intrinsic Selmer dimension many scalar coordinates. The
family constructed from the one-prime interface attains this lower bound.
-/

namespace Komorebi.StrongArtin.SyzygyCorrectedAuxiliaryMinimality

open Module
open Komorebi.StrongArtin.AdaptiveAuxiliarySelection
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.PresentationObstructionExactSequence
open Komorebi.StrongArtin.SelmerPresentationComparison
open Komorebi.StrongArtin.PresentationIntrinsicObstructionCapstone
open Komorebi.StrongArtin.SyzygyCorrectedAuxiliarySelection

noncomputable section

universe u v w t z a

variable {R : Type u} {S : Type v} {ι : Type w} {σ : Type t}
  [CommRing R] [Field S] [Algebra R S]
variable {H : Type z} [AddCommGroup H] [Module S H]
variable {Aux : Type a}

/-- If raw selected evaluation has exactly the relation syzygies as its kernel,
then the corresponding intrinsic evaluation on Selmer is injective. -/
theorem intrinsicEvaluation_injective_of_ker_raw_eq_syzygies
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    (hker : LinearMap.ker (rawEvaluationMap D I Q) = relationSyzygies P) :
    Function.Injective (evaluationMap I.localFunctional Q) := by
  rw [← LinearMap.ker_eq_bot]
  apply le_antisymm
  · intro h hh
    obtain ⟨x, hx⟩ := D.presentationToSelmer_surjective h
    have hxraw : x ∈ LinearMap.ker (rawEvaluationMap D I Q) := by
      apply LinearMap.mem_ker.mpr
      change evaluationMap I.localFunctional Q (D.presentationToSelmer x) = 0
      rw [hx]
      exact LinearMap.mem_ker.mp hh
    have hxsyz : x ∈ relationSyzygies P := by
      rw [← hker]
      exact hxraw
    have hxselmerKer : x ∈ LinearMap.ker D.presentationToSelmer := by
      rw [D.ker_presentationToSelmer]
      exact hxsyz
    have hxzero : D.presentationToSelmer x = 0 :=
      LinearMap.mem_ker.mp hxselmerKer
    change h = 0
    rw [← hx]
    exact hxzero
  · exact bot_le

/-- Any scalar auxiliary family which removes all intrinsic obstruction, leaving
only relation syzygies, has at least the intrinsic Selmer dimension many
labels. -/
theorem finrank_le_card_of_syzygy_corrected_family
    [FiniteDimensional S H]
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    (hker : LinearMap.ker (rawEvaluationMap D I Q) = relationSyzygies P) :
    Module.finrank S H ≤ Q.card := by
  exact finrank_le_card_of_evaluationMap_injective
    I.localFunctional Q
    (intrinsicEvaluation_injective_of_ker_raw_eq_syzygies D I Q hker)

/-- The syzygy-corrected auxiliary family supplied by v0.15 is
cardinality-minimal among all scalar families that reduce the raw presentation
kernel exactly to relation redundancy. -/
theorem exists_cardinality_minimal_syzygy_corrected_set
    [DecidableEq Aux] [FiniteDimensional S H]
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, I.admissible a) ∧
      LinearMap.ker (rawEvaluationMap D I Q) = relationSyzygies P ∧
      Function.Surjective (rawEvaluationMap D I Q) ∧
      Q.card = Module.finrank S H ∧
      ∀ Q' : Finset Aux,
        LinearMap.ker (rawEvaluationMap D I Q') = relationSyzygies P →
        Q.card ≤ Q'.card := by
  obtain ⟨Q, hgood, hcard, hker, hsurj, -⟩ :=
    exists_syzygy_corrected_TaylorWiles_set D I
  refine ⟨Q, hgood, hker, hsurj, hcard, ?_⟩
  intro Q' hQ'
  rw [hcard]
  exact finrank_le_card_of_syzygy_corrected_family D I Q' hQ'

/-- Under conormal independence, the exact selected raw evaluation map is a
linear equivalence with the auxiliary coordinate space. -/
def rawEvaluationEquiv_of_relationIndependent
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    [FiniteDimensional S H]
    (hrel : Function.Injective
      (Algebra.Presentation.differentials.hom₁ P))
    (hcard : Q.card = Module.finrank S H)
    (hinj : Function.Injective (evaluationMap I.localFunctional Q)) :
    presentationObstructionDual P ≃ₗ[S] (Q → S) := by
  apply LinearEquiv.ofBijective (rawEvaluationMap D I Q)
  constructor
  · have hkerbot : LinearMap.ker (rawEvaluationMap D I Q) =
        (⊥ : Submodule S (presentationObstructionDual P)) := by
      rw [ker_rawEvaluationMap_eq_relationSyzygies D I Q hinj]
      exact (relationSyzygies_eq_bot_iff_relationIndependent P).2 hrel
    intro x y hxy
    have hsubker : x - y ∈ LinearMap.ker (rawEvaluationMap D I Q) := by
      apply LinearMap.mem_ker.mpr
      calc
        rawEvaluationMap D I Q (x - y) =
            rawEvaluationMap D I Q x - rawEvaluationMap D I Q y :=
          (rawEvaluationMap D I Q).map_sub x y
        _ = 0 := sub_eq_zero.mpr hxy
    have hsubbot : x - y ∈
        (⊥ : Submodule S (presentationObstructionDual P)) := by
      rw [← hkerbot]
      exact hsubker
    have hsubzero : x - y = 0 := by simpa using hsubbot
    exact sub_eq_zero.mp hsubzero
  · exact rawEvaluationMap_surjective D I Q hcard hinj

end

end Komorebi.StrongArtin.SyzygyCorrectedAuxiliaryMinimality

#print axioms Komorebi.StrongArtin.SyzygyCorrectedAuxiliaryMinimality.intrinsicEvaluation_injective_of_ker_raw_eq_syzygies
#print axioms Komorebi.StrongArtin.SyzygyCorrectedAuxiliaryMinimality.exists_cardinality_minimal_syzygy_corrected_set
#print axioms Komorebi.StrongArtin.SyzygyCorrectedAuxiliaryMinimality.rawEvaluationEquiv_of_relationIndependent
