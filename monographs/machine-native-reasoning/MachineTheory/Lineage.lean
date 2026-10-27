import Mathlib.MeasureTheory.Function.ConditionalExpectation.Basic
import Mathlib.MeasureTheory.Measure.Real
import Mathlib.Topology.Algebra.InfiniteSum.ENNReal

/-! # Conditional error budgets across an adaptive lineage

Core 7.4 on an arbitrary probability space. `H j` is the information available
before the source's attempt `j + 1`. Each assumption concerns the false-acceptance
event of that actual attempt, after its history-dependent candidate choice.

No independence, finite sample space, or monotonicity of `H` is needed for this
consequence. The conditional premise itself must be justified by the application.
A numerical schedule, or marginal bounds for candidates fixed in advance, does
not establish it. Real budget sums carry an explicit summability hypothesis.
-/
namespace Komorebi.MachineTheory.Lineage

open MeasureTheory Set Filter
open scoped ENNReal NNReal Topology
noncomputable section

variable {Ω : Type*} [mΩ : MeasurableSpace Ω]

/-- The actual conditional expectation of the false-event indicator. -/
def conditionalRisk (μ : Measure Ω) (H : MeasurableSpace Ω) (A : Set Ω) : Ω → ℝ :=
  μ[A.indicator (fun _ => (1 : ℝ)) | H]

/-- Conditional validity for one actual attempt, with a deterministic budget. -/
def ConditionalBound (μ : Measure Ω) (H : MeasurableSpace Ω)
    (A : Set Ω) (d : ℝ) : Prop := by
  letI : MeasurableSpace Ω := mΩ
  exact ∀ᵐ ω ∂μ, conditionalRisk μ H A ω ≤ d

variable (μ : Measure Ω) [IsProbabilityMeasure μ]

/-- The indicator is genuinely integrable, so its integral is a probability. -/
theorem indicator_integrable (A : Set Ω) (hA : MeasurableSet A) :
    Integrable (A.indicator (fun _ => (1 : ℝ))) μ :=
  (integrable_const (1 : ℝ)).indicator hA

/-- Taking expectations here uses Mathlib's conditional expectation integral law. -/
theorem conditional_integral_eq_probability (H : MeasurableSpace Ω) (hH : H ≤ mΩ)
    (A : Set Ω) (hA : MeasurableSet[mΩ] A) :
    (letI : MeasurableSpace Ω := mΩ
     (∫ ω, conditionalRisk μ H A ω ∂μ) = μ.real A) := by
  let : MeasurableSpace Ω := mΩ
  unfold conditionalRisk
  rw [integral_condExp hH, integral_indicator_const (1 : ℝ) hA]
  simp

/-- Conditional validity of the actual event implies its marginal bound. -/
theorem conditional_marginal_bound (H : MeasurableSpace Ω) (hH : H ≤ mΩ)
    (A : Set Ω) (hA : MeasurableSet[mΩ] A) (d : ℝ)
    (h : ConditionalBound (mΩ := mΩ) μ H A d) : μ.real A ≤ d := by
  let : MeasurableSpace Ω := mΩ
  calc
    μ.real A = ∫ ω, conditionalRisk μ H A ω ∂μ :=
      (conditional_integral_eq_probability μ H hH A hA).symm
    _ ≤ ∫ _ : Ω, d ∂μ :=
      integral_mono_ae integrable_condExp (integrable_const d) h
    _ = d := by simp

/-- A real probability bound transports to the extended nonnegative measure. -/
theorem measure_le_of_real_bound (A : Set Ω) (d : ℝ) (h : μ.real A ≤ d) :
    μ A ≤ ENNReal.ofReal d := by
  have hp := ENNReal.ofReal_le_ofReal h
  simpa only [measureReal_def, ENNReal.ofReal_toReal (measure_ne_top μ A)] using hp

omit [IsProbabilityMeasure μ] in
/-- The finite union bound uses the budgets of precisely the selected attempts. -/
theorem finite_union_bound_of_marginals (A : ℕ → Set Ω) (d : ℕ → ℝ)
    (h : ∀ j, μ.real (A j) ≤ d j) (s : Finset ℕ) :
    μ.real (⋃ j ∈ s, A j) ≤ ∑ j ∈ s, d j := by
  exact (measureReal_biUnion_finset_le s A).trans (Finset.sum_le_sum fun j _ => h j)

/-- Countable subadditivity in `ℝ≥0∞`; this step has no real-tsum convention. -/
theorem countable_union_ennreal_bound_of_marginals (A : ℕ → Set Ω) (d : ℕ → ℝ)
    (h : ∀ j, μ.real (A j) ≤ d j) :
    μ (⋃ j, A j) ≤ ∑' j, ENNReal.ofReal (d j) := by
  exact (measure_iUnion_le A).trans
    (ENNReal.tsum_le_tsum fun j => measure_le_of_real_bound μ (A j) (d j) (h j))

/-- Summability makes the real total faithful to the extended nonnegative sum. -/
theorem countable_union_bound_of_marginals (A : ℕ → Set Ω) (d : ℕ → ℝ)
    (hd : ∀ j, 0 ≤ d j) (hs : Summable d)
    (h : ∀ j, μ.real (A j) ≤ d j) :
    μ.real (⋃ j, A j) ≤ ∑' j, d j := by
  have he := countable_union_ennreal_bound_of_marginals μ A d h
  rw [← ENNReal.ofReal_tsum_of_nonneg hd hs] at he
  have hr := ENNReal.toReal_mono ENNReal.ofReal_ne_top he
  simpa only [← measureReal_def, ENNReal.toReal_ofReal (tsum_nonneg hd)] using hr

/-- Core 7.4, finite-attempt conclusion from the actual conditional premises. -/
theorem finite_lineage_bound (H : ℕ → MeasurableSpace Ω) (hH : ∀ j, H j ≤ mΩ)
    (A : ℕ → Set Ω) (hA : ∀ j, MeasurableSet (A j)) (d : ℕ → ℝ)
    (hc : ∀ j, ConditionalBound μ (H j) (A j) (d j)) (s : Finset ℕ) :
    μ.real (⋃ j ∈ s, A j) ≤ ∑ j ∈ s, d j := by
  exact finite_union_bound_of_marginals μ A d
    (fun j => conditional_marginal_bound μ (H j) (hH j) (A j) (hA j) (d j) (hc j)) s

/-- Core 7.4, countably many actual attempts with a deterministic total budget. -/
theorem lineage_bound (H : ℕ → MeasurableSpace Ω) (hH : ∀ j, H j ≤ mΩ)
    (A : ℕ → Set Ω) (hA : ∀ j, MeasurableSet (A j)) (d : ℕ → ℝ)
    (hd : ∀ j, 0 ≤ d j) (hs : Summable d) (total : ℝ)
    (htotal : (∑' j, d j) ≤ total)
    (hc : ∀ j, ConditionalBound μ (H j) (A j) (d j)) :
    μ.real (⋃ j, A j) ≤ total := by
  exact (countable_union_bound_of_marginals μ A d hd hs
    (fun j => conditional_marginal_bound μ (H j) (hH j) (A j) (hA j) (d j) (hc j))).trans htotal

/-- The corresponding nontruncated, extended-measure conclusion. -/
theorem lineage_ennreal_bound (H : ℕ → MeasurableSpace Ω) (hH : ∀ j, H j ≤ mΩ)
    (A : ℕ → Set Ω) (hA : ∀ j, MeasurableSet (A j)) (d : ℕ → ℝ)
    (hd : ∀ j, 0 ≤ d j) (hs : Summable d) (total : ℝ)
    (htotal : (∑' j, d j) ≤ total)
    (hc : ∀ j, ConditionalBound μ (H j) (A j) (d j)) :
    μ (⋃ j, A j) ≤ ENNReal.ofReal total :=
  measure_le_of_real_bound μ _ _ (lineage_bound μ H hH A hA d hd hs total htotal hc)

/-- A history-dependent gate only removes outcomes from each attempt's event. -/
def gatedEvents (A gate : ℕ → Set Ω) (j : ℕ) : Set Ω := A j ∩ gate j

omit mΩ in
/-- Containment is pointwise and does not require independence or predictable gates. -/
theorem gated_union_subset (A gate : ℕ → Set Ω) :
    (⋃ j, gatedEvents A gate j) ⊆ ⋃ j, A j := by
  intro ω hω
  obtain ⟨j,hj⟩ := mem_iUnion.mp hω
  exact mem_iUnion.mpr ⟨j,hj.1⟩

/-- Measurable gates give genuine measurable false-acceptance events. -/
theorem gatedEvents_measurable (A gate : ℕ → Set Ω)
    (hA : ∀ j, MeasurableSet (A j)) (hg : ∀ j, MeasurableSet (gate j)) (j : ℕ) :
    MeasurableSet (gatedEvents A gate j) := (hA j).inter (hg j)

/-- Even arbitrary gates cannot enlarge the outer measure of ever failing. -/
theorem gated_lineage_bound (H : ℕ → MeasurableSpace Ω) (hH : ∀ j, H j ≤ mΩ)
    (A : ℕ → Set Ω) (hA : ∀ j, MeasurableSet (A j)) (d : ℕ → ℝ)
    (hd : ∀ j, 0 ≤ d j) (hs : Summable d) (total : ℝ)
    (htotal : (∑' j, d j) ≤ total)
    (hc : ∀ j, ConditionalBound μ (H j) (A j) (d j)) (gate : ℕ → Set Ω) :
    μ.real (⋃ j, gatedEvents A gate j) ≤ total :=
  (measureReal_mono (gated_union_subset A gate)).trans
    (lineage_bound μ H hH A hA d hd hs total htotal hc)

/-- `stop ω` is the number of attempted indices, possibly infinite. -/
def stoppedEvents (A : ℕ → Set Ω) (stop : Ω → WithTop ℕ) (j : ℕ) : Set Ω :=
  gatedEvents A (fun k => {ω | (k : WithTop ℕ) < stop ω}) j

omit mΩ in
/-- Arbitrary outcome-dependent stopping only removes potential false acceptances. -/
theorem stopped_union_subset (A : ℕ → Set Ω) (stop : Ω → WithTop ℕ) :
    (⋃ j, stoppedEvents A stop j) ⊆ ⋃ j, A j :=
  gated_union_subset A _

/-- Core 7.4 with stopping. A stopping-time law is unnecessary for containment. -/
theorem stopped_lineage_bound (H : ℕ → MeasurableSpace Ω) (hH : ∀ j, H j ≤ mΩ)
    (A : ℕ → Set Ω) (hA : ∀ j, MeasurableSet (A j)) (d : ℕ → ℝ)
    (hd : ∀ j, 0 ≤ d j) (hs : Summable d) (total : ℝ)
    (htotal : (∑' j, d j) ≤ total)
    (hc : ∀ j, ConditionalBound μ (H j) (A j) (d j)) (stop : Ω → WithTop ℕ) :
    μ.real (⋃ j, stoppedEvents A stop j) ≤ total :=
  gated_lineage_bound μ H hH A hA d hd hs total htotal hc _

/-- The source's actual event includes the candidate chosen on this outcome. -/
def selectedFalseEvents {Candidate : Type*} (selected : ℕ → Ω → Candidate)
    (accepted : ℕ → Ω → Prop) (falseClaim : Candidate → Ω → Prop) (j : ℕ) : Set Ω :=
  {ω | accepted j ω ∧ falseClaim (selected j ω) ω}

/-- A candidate-selection wrapper keeps the conditional premise on the actual event. -/
theorem selected_lineage_bound {Candidate : Type*}
    (selected : ℕ → Ω → Candidate) (accepted : ℕ → Ω → Prop)
    (falseClaim : Candidate → Ω → Prop)
    (H : ℕ → MeasurableSpace Ω) (hH : ∀ j, H j ≤ mΩ)
    (hA : ∀ j, MeasurableSet (selectedFalseEvents selected accepted falseClaim j))
    (d : ℕ → ℝ) (hd : ∀ j, 0 ≤ d j) (hs : Summable d) (total : ℝ)
    (htotal : (∑' j, d j) ≤ total)
    (hc : ∀ j, ConditionalBound μ (H j)
      (selectedFalseEvents selected accepted falseClaim j) (d j)) :
    μ.real (⋃ j, selectedFalseEvents selected accepted falseClaim j) ≤ total :=
  lineage_bound μ H hH _ hA d hd hs total htotal hc

/-- The same actual selected events may be restricted by outcome-dependent stopping. -/
theorem stopped_selected_lineage_bound {Candidate : Type*}
    (selected : ℕ → Ω → Candidate) (accepted : ℕ → Ω → Prop)
    (falseClaim : Candidate → Ω → Prop)
    (H : ℕ → MeasurableSpace Ω) (hH : ∀ j, H j ≤ mΩ)
    (hA : ∀ j, MeasurableSet (selectedFalseEvents selected accepted falseClaim j))
    (d : ℕ → ℝ) (hd : ∀ j, 0 ≤ d j) (hs : Summable d) (total : ℝ)
    (htotal : (∑' j, d j) ≤ total)
    (hc : ∀ j, ConditionalBound μ (H j)
      (selectedFalseEvents selected accepted falseClaim j) (d j))
    (stop : Ω → WithTop ℕ) :
    μ.real (⋃ j, stoppedEvents (selectedFalseEvents selected accepted falseClaim) stop j) ≤ total :=
  stopped_lineage_bound μ H hH _ hA d hd hs total htotal hc stop

/-- Measurable continuation events give measurable stopped false-acceptance events. -/
theorem stoppedEvents_measurable (A : ℕ → Set Ω) (stop : Ω → WithTop ℕ)
    (hA : ∀ j, MeasurableSet (A j))
    (hstop : ∀ j : ℕ, MeasurableSet {ω | (j : WithTop ℕ) < stop ω}) (j : ℕ) :
    MeasurableSet (stoppedEvents A stop j) := gatedEvents_measurable A _ hA hstop j

/-- A constant positive real schedule is not summable. -/
theorem constant_one_not_summable : ¬ Summable (fun _ : ℕ => (1 : ℝ)) := by
  rw [summable_const_iff]
  exact one_ne_zero

/-- Lean's real total defaults to zero on this divergent schedule. -/
theorem divergent_real_tsum_zero : (∑' _ : ℕ, (1 : ℝ)) = 0 :=
  tsum_eq_zero_of_not_summable constant_one_not_summable

/-- The extended nonnegative sum correctly records infinite total expenditure. -/
theorem divergent_ennreal_tsum_top : (∑' _ : ℕ, (1 : ℝ≥0∞)) = ⊤ :=
  ENNReal.tsum_const_eq_top_of_ne_zero one_ne_zero

/-- The divergent real convention cannot bound a sequence of certain failures. -/
theorem divergent_real_total_not_union_bound :
    ¬ μ.real (⋃ _ : ℕ, (Set.univ : Set Ω)) ≤ ∑' _ : ℕ, (1 : ℝ) := by
  rw [divergent_real_tsum_zero]
  simp only [Set.iUnion_const, measureReal_def, measure_univ, ENNReal.toReal_one]
  norm_num

end
end Komorebi.MachineTheory.Lineage
