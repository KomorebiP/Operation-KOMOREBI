import Komorebi.Foundation.GuardedExistenceFormula

/-!
# Adjoining the closed sentence to an explicit base theory

The base theory remains an argument. In particular it is not identified with
ZFC or with the complete theory of the ambient structure by convention.
The arbitrary-model theorem below is the logical insertion rule only. The
set-theoretic interpretation theorem remains specific to ZFSet.
-/

universe u v

namespace Komorebi.MembershipFormula

open FirstOrder FirstOrder.Language
open CompactnessClassification

/-- Adjoin the constructed sentence to a supplied membership-language theory. -/
def extendWithResidualSentence (T : language.Theory) : language.Theory :=
  insert guardedExtensionSentence T

theorem base_subset_extension (T : language.Theory) :
    T ⊆ extendWithResidualSentence T := Set.subset_insert _ _

theorem guardedSentence_mem_extension (T : language.Theory) :
    guardedExtensionSentence ∈ extendWithResidualSentence T := Set.mem_insert _ _

/-- Valid in every membership structure. This is not a classification of
internally interpreted ZFC cardinals in arbitrary models. -/
theorem model_extension_iff (T : language.Theory) (M : Type u) [language.Structure M] :
    M ⊨ extendWithResidualSentence T ↔
      M ⊨ T ∧ M ⊨ guardedExtensionSentence := by
  exact Theory.model_insert_iff.trans and_comm

/-- The concrete semantic bridge for the adjoining operation. -/
theorem zfset_model_extension_iff (T : language.Theory) :
    ZFSet.{u} ⊨ extendWithResidualSentence T ↔
      ZFSet.{u} ⊨ T ∧ ResidualExistence.{u} := by
  rw [model_extension_iff, guardedSentence_iff_residualExistence]

/-- When the base theory is known in this structure, the sole remaining
semantic obligation is the independently specified uncountable existence. -/
theorem zfset_model_extension_iff_of_base (T : language.Theory) (hT : ZFSet.{u} ⊨ T) :
    ZFSet.{u} ⊨ extendWithResidualSentence T ↔ ResidualExistence.{u} := by
  rw [zfset_model_extension_iff]
  exact and_iff_right hT

/-- Truth of this sentence is invariant under elementary equivalence. This
ordinary logical fact does not assert absoluteness under forcing or submodels. -/
theorem guardedSentence_of_elementarilyEquivalent
    (M : Type u) (N : Type v) [language.Structure M] [language.Structure N]
    (h : M ≅[language] N) :
    M ⊨ guardedExtensionSentence ↔ N ⊨ guardedExtensionSentence :=
  (elementarilyEquivalent_iff.mp h) guardedExtensionSentence

end Komorebi.MembershipFormula
