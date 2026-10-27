import Mathlib.MeasureTheory.Function.ConditionalExpectation.Basic
import Mathlib.MeasureTheory.Measure.Real
import Mathlib.Topology.Algebra.InfiniteSum.ENNReal

/-! Countable, prospective confidence accounting. Conditional coverage is an
actual conditional expectation bound for each measurable failure event. -/
set_option autoImplicit false
namespace Komorebi.LSM.SequentialConfidence
open MeasureTheory
open scoped BigOperators ENNReal NNReal

variable {Ω : Type*} [mΩ : MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- Conditional coverage implies unconditional coverage by total expectation. -/
theorem failure_bound_of_conditional {m : MeasurableSpace Ω} (hm : m≤mΩ)
    (F : Set Ω) (hF : @MeasurableSet Ω mΩ F) (δ : NNReal)
    (hc : ∀ᵐ ω ∂μ, (μ[F.indicator (fun _ ↦ (1:ℝ)) | m]) ω ≤ (δ:ℝ)) :
    μ.real F ≤ (δ:ℝ) := by
  have hi := integral_mono_ae (integrable_condExp :
      Integrable (μ[F.indicator (fun _ ↦ (1:ℝ)) | m]) μ) (integrable_const (δ:ℝ)) hc
  rw [integral_condExp hm] at hi
  rw [integral_indicator hF, setIntegral_const] at hi
  simpa using hi

/-- A summable prospective budget controls every countably many covered stage. -/
theorem simultaneous_coverage (F : ℕ → Set Ω) (hF : ∀ n, MeasurableSet (F n))
    (δn : ℕ → NNReal) (hs : Summable δn) (δ : NNReal) (hbudget : ∑' n, δn n ≤ δ)
    (hcover : ∀ n, μ.real (F n) ≤ (δn n:ℝ)) :
    1-(δ:ℝ) ≤ μ.real (⋂ n, (F n)ᶜ) := by
  have hb : μ (⋃ n, F n) ≤ (δ:ENNReal) := by
    calc
      _ ≤ ∑' n, μ (F n) := measure_iUnion_le _
      _ ≤ ∑' n, (δn n:ENNReal) := ENNReal.tsum_le_tsum (fun n ↦ by
        have h := ENNReal.ofReal_le_ofReal (hcover n)
        simpa using h)
      _ = ↑(∑' n, δn n) := (ENNReal.coe_tsum hs).symm
      _ ≤ _ := ENNReal.coe_le_coe.mpr hbudget
  have hb' : μ.real (⋃ n, F n) ≤ (δ:ℝ) := by
    have h := ENNReal.toReal_mono ENNReal.coe_ne_top hb
    simpa only [Measure.real, ENNReal.coe_toReal] using h
  have he : (⋂ n, (F n)ᶜ) = (⋃ n, F n)ᶜ := by simp
  rw [he, measureReal_compl (MeasurableSet.iUnion hF)]
  simpa using sub_le_sub_left hb' 1

/-- P48: conditional stage coverage survives every prospective proposal sequence. -/
theorem conditional_simultaneous_coverage
    (m : ℕ → MeasurableSpace Ω) (hm : ∀ n, m n≤mΩ)
    (F : ℕ → Set Ω) (hF : ∀ n, MeasurableSet (F n))
    (δn : ℕ → NNReal) (hs : Summable δn) (δ : NNReal) (hbudget : ∑' n, δn n ≤ δ)
    (hc : ∀ n, ∀ᵐ ω ∂μ, (μ[(F n).indicator (fun _ ↦ (1:ℝ)) | m n]) ω ≤ (δn n:ℝ)) :
    1-(δ:ℝ) ≤ μ.real (⋂ n, (F n)ᶜ) :=
  simultaneous_coverage F hF δn hs δ hbudget
    (fun n ↦ failure_bound_of_conditional (hm n) (F n) (hF n) (δn n) (hc n))

/-- P48's robust acceptance conclusion on one event of confidence at least 1−δ.
The covered initial base and exact robust implication remain explicit. -/
theorem conditional_robust_certificate {Θ D : Type*}
    (m : ℕ → MeasurableSpace Ω) (hm : ∀ n, m n≤mΩ)
    (trueModel : ℕ → Ω → Θ) (U : ℕ → Ω → Set Θ)
    (hF : ∀ n, MeasurableSet {ω | trueModel n ω ∉ U n ω})
    (δn : ℕ → NNReal) (hs : Summable δn) (δ : NNReal) (hbudget : ∑' n, δn n ≤ δ)
    (hc : ∀ n, ∀ᵐ ω ∂μ,
      (μ[({ω | trueModel n ω ∉ U n ω}).indicator (fun _ ↦ (1:ℝ)) | m n]) ω ≤ (δn n:ℝ))
    (domain : ℕ → Ω → D) (Accepted InitialCovered : ℕ → Ω → Prop)
    (Valid : Θ → D → Prop)
    (sound : ∀ n ω θ, Accepted n ω → InitialCovered n ω → θ ∈ U n ω →
      Valid θ (domain n ω)) :
    1-(δ:ℝ) ≤ μ.real {ω | ∀ n, Accepted n ω → InitialCovered n ω →
      Valid (trueModel n ω) (domain n ω)} := by
  have hprob := conditional_simultaneous_coverage m hm
    (fun n ↦ {ω | trueModel n ω ∉ U n ω}) hF δn hs δ hbudget hc
  apply hprob.trans (measureReal_mono ?_)
  intro ω hω
  change ∀ n, Accepted n ω → InitialCovered n ω → Valid (trueModel n ω) (domain n ω)
  intro n ha hi
  have hcover : trueModel n ω ∈ U n ω := by
    have hn := Set.mem_iInter.mp hω n
    simpa using hn
  exact sound n ω (trueModel n ω) ha hi hcover

omit mΩ in
/-- An arbitrary selected stage is among the simultaneously valid stages.
In particular this applies to every stopping time defined from recorded data. -/
theorem validity_at_selected_stage {Θ D : Type*}
    (trueModel : ℕ → Ω → Θ) (domain : ℕ → Ω → D)
    (Accepted InitialCovered : ℕ → Ω → Prop) (Valid : Θ → D → Prop)
    (ω : Ω) (hall : ∀ n, Accepted n ω → InitialCovered n ω →
      Valid (trueModel n ω) (domain n ω))
    (selected : Ω → ℕ) (ha : Accepted (selected ω) ω)
    (hi : InitialCovered (selected ω) ω) :
    Valid (trueModel (selected ω) ω) (domain (selected ω) ω) :=
  hall (selected ω) ha hi

end Komorebi.LSM.SequentialConfidence
