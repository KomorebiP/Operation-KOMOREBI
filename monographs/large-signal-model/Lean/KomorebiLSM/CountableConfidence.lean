import KomorebiLSM.SequentialConfidence

/-! Exact prospective confidence accounting for arbitrary finite/countable
rule indices. Reindexing changes neither the events nor their total budget. -/
set_option autoImplicit false
namespace Komorebi.LSM.CountableConfidence
open MeasureTheory
open scoped BigOperators ENNReal NNReal
variable {Ω J : Type*} [MeasurableSpace Ω] [Countable J]
variable {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- The actual countable union bound, with the original total budget. -/
theorem simultaneous_coverage (F : J → Set Ω) (hF : ∀ j,MeasurableSet (F j))
    (α : J → NNReal) (hs : Summable α) (δ : NNReal) (hbudget : ∑' j,α j≤δ)
    (hcover : ∀ j,μ.real (F j)≤(α j:ℝ)) :
    1-(δ:ℝ)≤μ.real (⋂ j,(F j)ᶜ) := by
  have hb : μ (⋃ j,F j)≤(δ:ENNReal) := by
    calc
      _ ≤ ∑' j,μ (F j) := measure_iUnion_le _
      _ ≤ ∑' j,(α j:ENNReal) := ENNReal.tsum_le_tsum (fun j => by
        have h := ENNReal.ofReal_le_ofReal (hcover j)
        simpa using h)
      _ = ↑(∑' j,α j) := (ENNReal.coe_tsum hs).symm
      _ ≤ _ := ENNReal.coe_le_coe.mpr hbudget
  have hb' : μ.real (⋃ j,F j)≤(δ:ℝ) := by
    have h := ENNReal.toReal_mono ENNReal.coe_ne_top hb
    simpa only [Measure.real,ENNReal.coe_toReal] using h
  have he : (⋂ j,(F j)ᶜ)=(⋃ j,F j)ᶜ := by simp
  rw [he,measureReal_compl (MeasurableSet.iUnion hF)]
  simpa using sub_le_sub_left hb' 1

omit [MeasurableSpace Ω] [Countable J] in
/-- An equivalence preserves summability and the actual total budget exactly. -/
theorem budget_transport {K : Type*} (e : K ≃ J) (α : J → NNReal) (hs : Summable α) :
    Summable (fun k => α (e k)) ∧ (∑' k,α (e k))=∑' j,α j := by
  exact ⟨e.summable_iff.mpr hs,e.tsum_eq α⟩

omit [MeasurableSpace Ω] [Countable J] in
/-- Relabeling rules changes no simultaneous pathwise assertion. -/
theorem forall_transport {K : Type*} (e : K ≃ J) (P : J → Prop) :
    (∀ k,P (e k)) ↔ ∀ j,P j := by
  constructor
  · intro h j
    simpa using h (e.symm j)
  · exact fun h k => h (e k)

/-- Finite-family accounting uses the literal finite sum, without padded rules. -/
theorem finite_simultaneous_coverage [Fintype J]
    (F : J → Set Ω) (hF : ∀ j,MeasurableSet (F j))
    (α : J → NNReal) (δ : NNReal) (hbudget : ∑ j,α j≤δ)
    (hcover : ∀ j,μ.real (F j)≤(α j:ℝ)) :
    1-(δ:ℝ)≤μ.real (⋂ j,(F j)ᶜ) := by
  apply simultaneous_coverage F hF α (summable_of_hasFiniteSupport (Set.toFinite _)) δ
  · simpa only [tsum_fintype] using hbudget
  · exact hcover

end Komorebi.LSM.CountableConfidence
