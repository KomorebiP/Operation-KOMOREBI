import SelmerPresentationComparison
import RelativeTaylorWilesFiniteSet

/-!
# Syzygy-corrected auxiliary selection

Arithmetic local functionals live on intrinsic cotangent H1 or Selmer, not on
spurious relation syzygies. Pulling an exact finite auxiliary family back to the
raw presentation kernel cuts that kernel down exactly to the syzygy submodule.
The resulting raw evaluation map is surjective onto the selected coordinate
space, so relation syzygies -> raw obstruction -> auxiliary coordinates is
short exact at the checked algebraic level.
-/

namespace Komorebi.StrongArtin.SyzygyCorrectedAuxiliarySelection

open Module
open Komorebi.StrongArtin.AdaptiveAuxiliarySelection
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.PresentationObstructionExactSequence
open Komorebi.StrongArtin.SelmerPresentationComparison

noncomputable section

universe u v w t z a

variable {R : Type u} {S : Type v} {ι : Type w} {σ : Type t}
  [CommRing R] [Field S] [Algebra R S]
variable {H : Type z} [AddCommGroup H] [Module S H]
variable {Aux : Type a}

/-- Pull an intrinsic arithmetic local functional back to the raw presentation
kernel. Every such functional automatically annihilates relation syzygies. -/
def pullbackLocalFunctional
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (a : Aux) :
    Module.Dual S (presentationObstructionDual P) :=
  (I.localFunctional a).comp D.presentationToSelmer

@[simp]
theorem pullbackLocalFunctional_apply
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (a : Aux)
    (x : presentationObstructionDual P) :
    pullbackLocalFunctional D I a x =
      I.localFunctional a (D.presentationToSelmer x) := rfl

/-- Simultaneous selected arithmetic evaluation on the raw presentation
kernel. -/
def rawEvaluationMap
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux) :
    presentationObstructionDual P →ₗ[S] (Q → S) :=
  (evaluationMap I.localFunctional Q).comp D.presentationToSelmer

@[simp]
theorem rawEvaluationMap_apply
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    (x : presentationObstructionDual P) (a : Q) :
    rawEvaluationMap D I Q x a =
      pullbackLocalFunctional D I a.1 x := rfl

/-- The raw simultaneous evaluation map is the ordinary selected evaluation
map for the pulled-back family. -/
theorem rawEvaluationMap_eq_evaluationMap_pullback
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux) :
    rawEvaluationMap D I Q =
      evaluationMap (k := S) (V := presentationObstructionDual P)
        (ι := Aux) (pullbackLocalFunctional D I) Q := by
  apply LinearMap.ext
  intro x
  funext a
  rfl

/-- Injective intrinsic evaluation cuts the raw presentation obstruction down
exactly to relation syzygies. -/
theorem ker_rawEvaluationMap_eq_relationSyzygies
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    (hinj : Function.Injective (evaluationMap I.localFunctional Q)) :
    LinearMap.ker (rawEvaluationMap D I Q) = relationSyzygies P := by
  ext x
  constructor
  · intro hx
    have hzero : evaluationMap I.localFunctional Q
        (D.presentationToSelmer x) = 0 := by
      exact LinearMap.mem_ker.mp hx
    have hselmer : D.presentationToSelmer x = 0 :=
      hinj (by simpa using hzero)
    have hxker : x ∈ LinearMap.ker D.presentationToSelmer :=
      LinearMap.mem_ker.mpr hselmer
    rw [D.ker_presentationToSelmer] at hxker
    exact hxker
  · intro hx
    have hxker : x ∈ LinearMap.ker D.presentationToSelmer := by
      rw [D.ker_presentationToSelmer]
      exact hx
    have hzero : D.presentationToSelmer x = 0 :=
      LinearMap.mem_ker.mp hxker
    apply LinearMap.mem_ker.mpr
    change evaluationMap I.localFunctional Q (D.presentationToSelmer x) = 0
    rw [hzero]
    exact map_zero _

/-- Equivalent selected-kernel formulation: genuine arithmetic probes reduce
the raw kernel to syzygies rather than to zero. -/
theorem selectedKernel_pullback_eq_relationSyzygies
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    (hinj : Function.Injective (evaluationMap I.localFunctional Q)) :
    selectedKernel (k := S) (V := presentationObstructionDual P)
      (ι := Aux) (pullbackLocalFunctional D I) Q =
      relationSyzygies P := by
  rw [← ker_evaluationMap,
    ← rawEvaluationMap_eq_evaluationMap_pullback D I Q]
  exact ker_rawEvaluationMap_eq_relationSyzygies D I Q hinj

/-- If the selected intrinsic evaluation is bijective onto a coordinate space,
then raw evaluation is surjective as well. -/
theorem rawEvaluationMap_surjective
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    [FiniteDimensional S H]
    (hcard : Q.card = Module.finrank S H)
    (hinj : Function.Injective (evaluationMap I.localFunctional Q)) :
    Function.Surjective (rawEvaluationMap D I Q) := by
  have hdim : Module.finrank S H = Module.finrank S (Q → S) := by
    simpa [Module.finrank_fintype_fun_eq_card, Fintype.card_coe]
      using hcard.symm
  have hevalsurj : Function.Surjective (evaluationMap I.localFunctional Q) :=
    (LinearMap.injective_iff_surjective_of_finrank_eq_finrank hdim).mp hinj
  exact hevalsurj.comp D.presentationToSelmer_surjective

/-- Exactness of relation redundancy, the raw presentation kernel, and the
selected auxiliary coordinate space. -/
theorem exact_relationSyzygies_rawEvaluation
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    (hinj : Function.Injective (evaluationMap I.localFunctional Q)) :
    Function.Exact (Submodule.subtype (relationSyzygies P))
      (rawEvaluationMap D I Q) := by
  rw [LinearMap.exact_iff]
  rw [ker_rawEvaluationMap_eq_relationSyzygies D I Q hinj]
  exact (Submodule.range_subtype (relationSyzygies P)).symm

/-- **Syzygy-corrected finite Taylor--Wiles selection.** Exactly the intrinsic
Selmer dimension many admissible labels cut the raw presentation obstruction
down to relation syzygies. The raw evaluation map is onto those coordinates,
and the resulting sequence is exact. -/
theorem exists_syzygy_corrected_TaylorWiles_set
    [DecidableEq Aux] [FiniteDimensional S H]
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (I : OnePrimeSelectionInterface S H Aux) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, I.admissible a) ∧
      Q.card = Module.finrank S H ∧
      LinearMap.ker (rawEvaluationMap D I Q) = relationSyzygies P ∧
      Function.Surjective (rawEvaluationMap D I Q) ∧
      Function.Exact (Submodule.subtype (relationSyzygies P))
        (rawEvaluationMap D I Q) := by
  obtain ⟨Q, hgood, hcard, -, hinj⟩ :=
    exists_relative_TaylorWiles_set_exact I
  refine ⟨Q, hgood, hcard, ?_, ?_, ?_⟩
  · exact ker_rawEvaluationMap_eq_relationSyzygies D I Q hinj
  · exact rawEvaluationMap_surjective D I Q hcard hinj
  · exact exact_relationSyzygies_rawEvaluation D I Q hinj

end

end Komorebi.StrongArtin.SyzygyCorrectedAuxiliarySelection

#print axioms Komorebi.StrongArtin.SyzygyCorrectedAuxiliarySelection.ker_rawEvaluationMap_eq_relationSyzygies
#print axioms Komorebi.StrongArtin.SyzygyCorrectedAuxiliarySelection.rawEvaluationMap_surjective
#print axioms Komorebi.StrongArtin.SyzygyCorrectedAuxiliarySelection.exists_syzygy_corrected_TaylorWiles_set
