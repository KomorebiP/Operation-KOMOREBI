import Komorebi.Foundation.ZFSetSupportClosure
import Komorebi.Foundation.InternalCompactnessFormula
import Komorebi.Foundation.KZFCTheory

/-!
# Closed membership-language sentences for the cone reduction

The original guard and Theta are unchanged. The arithmetic discharge sentence
is defined and proved for concrete ZFSet only. For arbitrary ZFC models it is
an explicit premise, never an axiom of the project.
-/

universe u v

namespace Komorebi.InternalConeFormula

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalConstraints InternalFineCompactness
open InternalSmallSupports InternalConeFilter InternalFineSupportClosure InternalUnionReduction
open InternalSupportEquivalence InternalCompactnessFormula

variable {M : Type u} [language.Structure M]

def smallUnionClosedF {α : Type v} (k : α) : language.Formula α :=
  allF (let k := some k; let b := none
    allF ((smallF (some k) (some b)).imp
      ((allF ((memF none (some (some b))).imp (smallF (some (some k)) none))).imp
        ((unionF none (some b)).imp (smallF (some k) none)))))

@[simp]
theorem smallUnionClosedF_realize {α : Type v} (k : α) (e : α → M) :
    (smallUnionClosedF k).Realize e ↔ SmallUnionClosed (e k) := by
  simp [smallUnionClosedF,SmallUnionClosed,assign]

def smallProductClosedF {α : Type v} (k : α) : language.Formula α :=
  allF (let k := some k; let x := none
    allF (let k := some k; let x := some x; let y := none
      allF ((smallF (some k) (some x)).imp ((smallF (some k) (some y)).imp
        ((prodF none (some x) (some y)).imp (smallF (some k) none))))))

@[simp]
theorem smallProductClosedF_realize {α : Type v} (k : α) (e : α → M) :
    (smallProductClosedF k).Realize e ↔ SmallProductClosed (e k) := by
  simp [smallProductClosedF,SmallProductClosed,assign]

def unionProductSentence : language.Sentence :=
  allF ((guardF none).imp ((smallUnionClosedF none).iff (smallProductClosedF none)))

@[simp]
theorem unionProductSentence_realize : M ⊨ unionProductSentence ↔
    ∀ k : M, Guard k → (SmallUnionClosed k ↔ SmallProductClosed k) := by
  simp [Sentence.Realize,unionProductSentence,assign]

theorem model_zfc_unionProductSentence (hM : M ⊨ zfcTheory) : M ⊨ unionProductSentence := by
  rw [unionProductSentence_realize]
  exact fun _ hg => unionClosed_iff_productClosed (model_zfc_iff_axiomSemantics.mp hM) hg

/-- A proved all-model reduction, not the as-yet-unproved arithmetic discharge. -/
def coneReductionSentence : language.Sentence :=
  allF ((guardF none).imp ((extensionF none).imp
    ((internalFineF none).iff (smallProductClosedF none))))

@[simp]
theorem coneReductionSentence_realize : M ⊨ coneReductionSentence ↔
    ∀ k : M, Guard k → Extension k → (InternalFinePrinciple k ↔ SmallProductClosed k) := by
  simp [Sentence.Realize,coneReductionSentence,assign]

theorem model_zfc_coneReductionSentence (hM : M ⊨ zfcTheory) : M ⊨ coneReductionSentence := by
  rw [coneReductionSentence_realize]
  exact fun _ hg he => fine_iff_productClosed_of_extension (model_zfc_iff_axiomSemantics.mp hM) hg he

/-- This exact ordinary cardinal-arithmetic sentence remains to be proved from
encoded ZFC in arbitrary models. It is not added to zfcTheory or kzfcTheory. -/
def productArithmeticSentence : language.Sentence :=
  allF ((guardF none).imp (smallProductClosedF none))

@[simp]
theorem productArithmeticSentence_realize : M ⊨ productArithmeticSentence ↔
    ∀ k : M, Guard k → SmallProductClosed k := by
  simp [Sentence.Realize,productArithmeticSentence,assign]

theorem zfset_productArithmeticSentence : ZFSet.{u} ⊨ productArithmeticSentence := by
  rw [productArithmeticSentence_realize]
  exact fun _ hg => ZFSetSupportClosure.productClosed_of_guard hg

/-- The original forward implication, now represented as one closed sentence. -/
def guardedExtensionCompactnessSentence : language.Sentence :=
  allF ((guardF none).imp ((extensionF none).imp (constraintCompactnessF none)))

@[simp]
theorem guardedExtensionCompactnessSentence_realize : M ⊨ guardedExtensionCompactnessSentence ↔
    ∀ k : M, Guard k → Extension k → ConstraintCompactness k := by
  simp [Sentence.Realize,guardedExtensionCompactnessSentence,assign]

/-- Conditional all-model discharge. The arithmetic premise is visible. -/
theorem model_zfc_extensionCompactness_of_arithmetic (hM : M ⊨ zfcTheory)
    (harith : M ⊨ productArithmeticSentence) : M ⊨ guardedExtensionCompactnessSentence := by
  rw [guardedExtensionCompactnessSentence_realize]
  intro k hg hext
  exact model_zfc_extension_productClosed_compactness hM hg
    ((productArithmeticSentence_realize.mp harith) k hg) hext

theorem zfset_guardedExtensionCompactnessSentence :
    ZFSet.{u} ⊨ guardedExtensionCompactnessSentence :=
  model_zfc_extensionCompactness_of_arithmetic ZFSetZFCModel.zfset_models_zfc
    zfset_productArithmeticSentence

/-- No model or large cardinal is manufactured. Modelhood and the arithmetic
sentence are both premises in this arbitrary-structure application. -/
theorem model_kzfc_compactness_witness_of_arithmetic (hM : M ⊨ KZFCTheory.kzfcTheory)
    (harith : M ⊨ productArithmeticSentence) :
    ∃ k : M, Guard k ∧ ConstraintCompactness k := by
  obtain ⟨h,⟨k,hg,hext⟩⟩ := (KZFCTheory.model_kzfc_iff_internal M).mp hM
  exact ⟨k,hg,compactness_of_extension_productClosed h hg
    ((productArithmeticSentence_realize.mp harith) k hg) hext⟩

theorem zfset_kzfc_internal_compactness_witness (hM : ZFSet.{u} ⊨ KZFCTheory.kzfcTheory) :
    ∃ k : ZFSet.{u}, Guard k ∧ ConstraintCompactness k :=
  model_kzfc_compactness_witness_of_arithmetic hM zfset_productArithmeticSentence

end Komorebi.InternalConeFormula
