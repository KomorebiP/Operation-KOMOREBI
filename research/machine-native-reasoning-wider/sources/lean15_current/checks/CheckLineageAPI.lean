import MachineTheory.Lineage
import MachineTheory.LineageExamples

/-! Source-facing restatements use actual conditional expectations, measures,
and selected events, independently of the public bound abbreviation. -/
open MeasureTheory Set Filter
open scoped ENNReal NNReal Topology
open Komorebi.MachineTheory

example {Ω : Type*} [mΩ : MeasurableSpace Ω] (μ : Measure Ω) [IsProbabilityMeasure μ]
    (H : ℕ → MeasurableSpace Ω) (hH : ∀ j, H j ≤ mΩ)
    (A : ℕ → Set Ω) (hA : ∀ j, MeasurableSet (A j))
    (d : ℕ → ℝ) (hd : ∀ j, 0 ≤ d j) (hs : Summable d) (D : ℝ)
    (hD : (∑' j, d j) ≤ D)
    (hc : ∀ j, ∀ᵐ ω ∂μ, (μ[(A j).indicator (fun _ => (1 : ℝ)) | H j]) ω ≤ d j) :
    μ (⋃ j, A j) ≤ ENNReal.ofReal D :=
  Lineage.lineage_ennreal_bound μ H hH A hA d hd hs D hD hc

example {Ω : Type*} [mΩ : MeasurableSpace Ω] (μ : Measure Ω) [IsProbabilityMeasure μ]
    (H : ℕ → MeasurableSpace Ω) (hH : ∀ j, H j ≤ mΩ)
    (A : ℕ → Set Ω) (hA : ∀ j, MeasurableSet (A j))
    (d : ℕ → ℝ)
    (hc : ∀ j, ∀ᵐ ω ∂μ, (μ[(A j).indicator (fun _ => (1 : ℝ)) | H j]) ω ≤ d j)
    (s : Finset ℕ) : μ.real (⋃ j ∈ s, A j) ≤ ∑ j ∈ s, d j :=
  Lineage.finite_lineage_bound μ H hH A hA d hc s

example {Ω Candidate : Type*} [mΩ : MeasurableSpace Ω]
    (μ : Measure Ω) [IsProbabilityMeasure μ]
    (selected : ℕ → Ω → Candidate) (accepted : ℕ → Ω → Prop)
    (falseClaim : Candidate → Ω → Prop)
    (H : ℕ → MeasurableSpace Ω) (hH : ∀ j, H j ≤ mΩ)
    (hA : ∀ j, MeasurableSet {ω | accepted j ω ∧ falseClaim (selected j ω) ω})
    (d : ℕ → ℝ) (hd : ∀ j, 0 ≤ d j) (hs : Summable d) (D : ℝ)
    (hD : (∑' j, d j) ≤ D)
    (hc : ∀ j, ∀ᵐ ω ∂μ,
      (μ[({ω | accepted j ω ∧ falseClaim (selected j ω) ω}).indicator
        (fun _ => (1 : ℝ)) | H j]) ω ≤ d j)
    (stop : Ω → WithTop ℕ) :
    μ.real (⋃ j, {ω | (accepted j ω ∧ falseClaim (selected j ω) ω) ∧
      (j : WithTop ℕ) < stop ω}) ≤ D :=
  Lineage.stopped_selected_lineage_bound μ selected accepted falseClaim H hH hA
    d hd hs D hD hc stop

example : ¬ Summable (fun _ : ℕ => (1 : ℝ)) ∧
    (∑' _ : ℕ, (1 : ℝ)) = 0 ∧ (∑' _ : ℕ, (1 : ℝ≥0∞)) = ⊤ :=
  ⟨Lineage.constant_one_not_summable, Lineage.divergent_real_tsum_zero,
    Lineage.divergent_ennreal_tsum_top⟩

example : (∀ c, LineageExamples.prob LineageExamples.fair (LineageExamples.fixedBad c) = 1/2) ∧
    LineageExamples.prob LineageExamples.fair LineageExamples.selectedBad = 1 :=
  ⟨LineageExamples.fixed_candidate_half, LineageExamples.selected_candidate_certain⟩
