import Komorebi.Foundation.ZFSetZFCModel
import Komorebi.Foundation.InternalResidualSentence

/-!
# An explicit ZFC plus guarded-residual sentence theory

The base theory is now the syntactically specified ZFC axiom theory. Its truth
in ZFSet is proved, not left as an argument. No large-cardinal existence
hypothesis is added to the environment.
-/

universe u v

namespace Komorebi.KZFCTheory

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax ZFCModelSemantics
open ZFSetZFCModel InternalResidualSentence CompactnessClassification

/-- The exact proposed extension of the explicit base axiom theory. -/
def kzfcTheory : language.Theory := extendWithResidualSentence zfcTheory

theorem zfc_subset_kzfc : zfcTheory ⊆ kzfcTheory := Set.subset_insert _ _

theorem guardedSentence_mem_kzfc : guardedExtensionSentence ∈ kzfcTheory := Set.mem_insert _ _

/-- For every structure: precisely the base axioms plus the internally read
sentence. No external size, function-space or filter is substituted here. -/
theorem model_kzfc_iff_internal (M : Type u) [language.Structure M] :
    M ⊨ kzfcTheory ↔ AxiomSemantics M ∧ GuardedExtension M := by
  rw [kzfcTheory, model_extension_iff, model_zfc_iff_axiomSemantics,
    guardedSentence_iff_internal_model]

/-- The formerly conditional base-model premise is discharged by the full
fixed-axiom and schema proof, while uncountable existence remains on the right. -/
theorem zfset_models_kzfc_iff_residual :
    ZFSet.{u} ⊨ kzfcTheory ↔ ResidualExistence.{u} :=
  zfset_model_extension_iff_of_base zfcTheory zfset_models_zfc

theorem zfset_models_kzfc_iff_filterExtension :
    ZFSet.{u} ⊨ kzfcTheory ↔ FilterExtensionExistence.{u} :=
  zfset_models_kzfc_iff_residual.trans residualExistence_iff_filterExtensionExistence

/-- The uniform internal reading agrees with the old cardinal-level assertion
in the concrete universe, but no such external identification is made for M. -/
theorem internal_guarded_zfset_iff_residual :
    GuardedExtension ZFSet.{u} ↔ ResidualExistence.{u} :=
  guardedSentence_iff_internal_model.symm.trans guardedSentence_iff_residualExistence

/-- A explicitly conditional model construction; not an existence assertion. -/
theorem zfset_models_kzfc_of_residual (h : ResidualExistence.{u}) :
    ZFSet.{u} ⊨ kzfcTheory := zfset_models_kzfc_iff_residual.mpr h

theorem model_kzfc_member_irrefl (M : Type u) [language.Structure M]
    (h : M ⊨ kzfcTheory) (x : M) : ¬ member x x := by
  have ha := ((model_kzfc_iff_internal M).mp h).1
  exact member_irrefl_of_pairing_foundation ha.pairing ha.foundation x

theorem model_kzfc_no_universal (M : Type u) [language.Structure M]
    (h : M ⊨ kzfcTheory) : ¬ ∃ a : M, ∀ x : M, member x a := by
  have ha := ((model_kzfc_iff_internal M).mp h).1
  exact no_universal_of_separation (ha.separation 0)

end Komorebi.KZFCTheory
