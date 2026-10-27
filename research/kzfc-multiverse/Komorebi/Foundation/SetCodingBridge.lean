import Komorebi.Foundation.SetFilterCoding
import Mathlib.SetTheory.ZFC.Ordinal

/-!
# All-carrier interpretation, not merely a one-way representation

Every small Lean type is equivalent to the elements of a genuine ZFSet. The
filter-extension proposition quantified over such sets is therefore equivalent
to the predecessor's all-types proposition in the same universe.
-/

universe u

namespace Komorebi.SetFilterCoding

open Filter
open CompactnessClassification

theorem exists_carrier_equiv (A : Type u) :
    ∃ X : ZFSet.{u}, Nonempty (A ≃ Carrier X) := by
  refine ⟨(Cardinal.mk A).ord.toZFSet, Cardinal.eq.mp ?_⟩
  change Cardinal.mk A = ((Cardinal.mk A).ord.toZFSet).card
  simp [Ordinal.card_toZFSet]

theorem extension_of_setExtension (κ : Cardinal.{u})
    (h : SetCompleteFilterExtension κ) : CompleteFilterExtension κ := by
  intro A F hp hc
  obtain ⟨X, ⟨e⟩⟩ := exists_carrier_equiv A
  let : F.NeBot := hp
  let : CardinalInterFilter F κ := hc
  let G : Filter (Carrier X) := Filter.map e F
  obtain ⟨U, hU, hcomplete⟩ := (setExtensionAt_iff κ X).mp (h X) G
    (by infer_instance) (by infer_instance)
  let : CardinalInterFilter (U : Filter (Carrier X)) κ := hcomplete
  refine ⟨U.map e.symm, ?_, ?_⟩
  · change Filter.map e.symm (U : Filter (Carrier X)) ≤ F
    have ht := Filter.map_mono (m := e.symm) hU
    simpa [G, Filter.map_map, Function.comp_def] using ht
  · change CardinalInterFilter (Filter.map e.symm (U : Filter (Carrier X))) κ
    infer_instance

/-- Full semantic interpretation of the set coding, with the cardinal parameter
still represented by Lean's external Cardinal interface. -/
theorem setExtension_iff_extension (κ : Cardinal.{u}) :
    SetCompleteFilterExtension κ ↔ CompleteFilterExtension κ :=
  ⟨extension_of_setExtension κ, setExtension_of_extension κ⟩

theorem setExtension_iff_residual (κ : Cardinal.{u}) (hκ : κ.IsRegular) :
    SetCompleteFilterExtension κ ↔ FixedDomainKRR κ :=
  (setExtension_iff_extension κ).trans (krr_iff_extension κ hκ).symm

theorem setExtension_aleph0 : SetCompleteFilterExtension Cardinal.aleph0.{u} :=
  setExtension_of_extension _ extension_aleph0

end Komorebi.SetFilterCoding
