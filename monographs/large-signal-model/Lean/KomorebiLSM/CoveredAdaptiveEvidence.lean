import KomorebiLSM.CoveredAdaptiveActions
import KomorebiLSM.PredictableResidualP66

/-! Sequential covered-action evidence for actual contextual kernel means. -/
set_option autoImplicit false
namespace Komorebi.LSM.CoveredAdaptiveActions
open MeasureTheory ProbabilityTheory
open scoped BigOperators NNReal

variable {Ω A Y J : Type*} [mΩ : MeasurableSpace Ω] [mA : MeasurableSpace A]
variable [mY : MeasurableSpace Y] [Fintype A] [DecidableEq A] [MeasurableSingletonClass A]
variable {μ : Measure Ω} [IsProbabilityMeasure μ] [Countable J]
variable (ℱ : Filtration ℕ mΩ) (action : ℕ → Ω → A) (observation : ℕ → Ω → Y)
variable (E : ∀ n,Experiment (μ := μ) (ℱ.le n) (action n) (observation n))

/-- Actual observations with the recorded propensity correction. -/
noncomputable def evidenceProcess (φ : J → ℕ → Ω × Y → ℝ) (target : J → A)
    (j : J) (n : ℕ) : Ω → ℝ :=
  evidence (ℱ.le n) (E n) (φ j n) (target j)

/-- The action-conditioned quantities along the contexts actually encountered. -/
noncomputable def kernelMeanProcess (φ : J → ℕ → Ω × Y → ℝ) (target : J → A)
    (j : J) (n : ℕ) : Ω → ℝ :=
  targetMean (mH := ℱ n) (E n).observationKernel (φ j n) (target j)

omit [IsProbabilityMeasure μ] [Countable J] [Fintype A] in
theorem evidenceProcess_adapted (φ : J → ℕ → Ω × Y → ℝ) (target : J → A)
    (ha : ∀ n,Measurable[ℱ (n+1)] (action n))
    (hy : ∀ n,Measurable[ℱ (n+1)] (observation n))
    (hφ : ∀ j n,@Measurable (Ω × Y) ℝ ((ℱ n).prod mY) _ (φ j n)) (j : J) (n : ℕ) :
    Measurable[ℱ (n+1)] (evidenceProcess ℱ action observation E φ target j n) :=
  evidence_measurable_at (ℱ.le n) (E n) (ℱ.mono (by omega)) (ha n) (hy n) (φ j n) (hφ j n) (target j)

omit [Countable J] in
theorem evidenceProcess_condExp (φ : J → ℕ → Ω × Y → ℝ) (target : J → A)
    (hφ : ∀ j n,@Measurable (Ω × Y) ℝ ((ℱ n).prod mY) _ (φ j n))
    (hb : ∀ j n ω y,φ j n (ω,y)∈Set.Icc (0:ℝ) 1)
    (c : J → ℝ) (hc : ∀ j,0<c j)
    (hcover : ∀ j n ω,c j≤propensity (mH := ℱ n) (E n).policy (target j) ω)
    (j : J) (n : ℕ) :
    μ[evidenceProcess ℱ action observation E φ target j n | ℱ n] =ᵐ[μ]
      kernelMeanProcess ℱ action observation E φ target j n :=
  evidence_condExp (ℱ.le n) (E n) (φ j n) (hφ j n) (hb j n) (target j) (c j) (hc j)
    (hcover j n)

/-- Every actual conditional mean in the accumulated error can be replaced
simultaneously by its derived action-conditioned observation-kernel integral. -/
theorem centeredSum_eq_kernelSum_ae (φ : J → ℕ → Ω × Y → ℝ) (target : J → A)
    (hφ : ∀ j n,@Measurable (Ω × Y) ℝ ((ℱ n).prod mY) _ (φ j n))
    (hb : ∀ j n ω y,φ j n (ω,y)∈Set.Icc (0:ℝ) 1)
    (c : J → ℝ) (hc : ∀ j,0<c j)
    (hcover : ∀ j n ω,c j≤propensity (mH := ℱ n) (E n).policy (target j) ω) :
    ∀ᵐ ω∂μ,∀ j n,
      PredictableResidual.centeredSum (μ := μ) ℱ
        (evidenceProcess ℱ action observation E φ target j) n ω=
      (∑ i∈Finset.range n,evidenceProcess ℱ action observation E φ target j i ω)-
        ∑ i∈Finset.range n,kernelMeanProcess ℱ action observation E φ target j i ω := by
  have hce : ∀ᵐ ω∂μ,∀ j n,
      (μ[evidenceProcess ℱ action observation E φ target j n | ℱ n]) ω=
        kernelMeanProcess ℱ action observation E φ target j n ω :=
    ae_all_iff.mpr (fun j => ae_all_iff.mpr (fun n =>
      evidenceProcess_condExp ℱ action observation E φ target hφ hb c hc hcover j n))
  filter_upwards [hce] with ω hω
  intro j n
  rw [PredictableResidual.centeredSum,← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro i _
  rw [hω j i]

omit [IsProbabilityMeasure μ] [Fintype A] in
/-- The actual simultaneous contextual evidence event is measurable. -/
theorem covered_event_measurable (φ : J → ℕ → Ω × Y → ℝ) (target : J → A)
    (ha : ∀ n,Measurable[ℱ (n+1)] (action n))
    (hy : ∀ n,Measurable[ℱ (n+1)] (observation n))
    (hφ : ∀ j n,@Measurable (Ω × Y) ℝ ((ℱ n).prod mY) _ (φ j n))
    (c : J → ℝ) (α : J → NNReal) :
    MeasurableSet {ω | ∀ j n,
      |(∑ i∈Finset.range (n+1),evidenceProcess ℱ action observation E φ target j i ω)-
        ∑ i∈Finset.range (n+1),kernelMeanProcess ℱ action observation E φ target j i ω|≤
          (1/c j)*PredictableResidual.boundary (n+1) (α j)} := by
  simp only [Set.ofPred_forall]
  apply MeasurableSet.iInter
  intro j
  apply MeasurableSet.iInter
  intro n
  apply measurableSet_le _ measurable_const
  simp_rw [← Real.norm_eq_abs]
  apply Measurable.norm
  apply Measurable.sub
  · apply Finset.measurable_fun_sum
    intro i _
    exact (evidenceProcess_adapted ℱ action observation E φ target ha hy hφ j i).mono
      (ℱ.le (i+1)) le_rfl
  · apply Finset.measurable_fun_sum
    intro i _
    exact (targetMean_measurable (mH := ℱ i) (E i).observationKernel (φ j i) (hφ j i)
      (target j)).mono (ℱ.le i) le_rfl

/-- Full P67: covered randomized actions estimate their actual contextual
kernel means simultaneously at every positive time and every registered rule.
The interval-width boundary comes from the full P66 theorem, not an assumed
concentration certificate. -/
theorem covered_adaptive_action_certificate (φ : J → ℕ → Ω × Y → ℝ) (target : J → A)
    (ha : ∀ n,Measurable[ℱ (n+1)] (action n))
    (hy : ∀ n,Measurable[ℱ (n+1)] (observation n))
    (hφ : ∀ j n,@Measurable (Ω × Y) ℝ ((ℱ n).prod mY) _ (φ j n))
    (hb : ∀ j n ω y,φ j n (ω,y)∈Set.Icc (0:ℝ) 1)
    (c : J → ℝ) (hc : ∀ j,0<c j)
    (hcover : ∀ j n ω,c j≤propensity (mH := ℱ n) (E n).policy (target j) ω)
    (α : J → NNReal) (hα : ∀ j,0<α j) (hs : Summable α)
    (δ : NNReal) (hbudget : ∑' j,α j≤δ) (hδ1 : δ≤1) :
    MeasurableSet {ω | ∀ j n,
      |(∑ i∈Finset.range (n+1),evidenceProcess ℱ action observation E φ target j i ω)-
        ∑ i∈Finset.range (n+1),kernelMeanProcess ℱ action observation E φ target j i ω|≤
          (1/c j)*PredictableResidual.boundary (n+1) (α j)} ∧
    1-(δ:ℝ)≤μ.real {ω | ∀ j n,
      |(∑ i∈Finset.range (n+1),evidenceProcess ℱ action observation E φ target j i ω)-
        ∑ i∈Finset.range (n+1),kernelMeanProcess ℱ action observation E φ target j i ω|≤
          (1/c j)*PredictableResidual.boundary (n+1) (α j)} := by
  refine ⟨covered_event_measurable ℱ action observation E φ target ha hy hφ c α,?_⟩
  have ht := PredictableResidualGeneral.predictable_sum_interval_rules (μ := μ) ℱ
    (evidenceProcess ℱ action observation E φ target) (fun _ => 0) (fun j => 1/c j)
    (fun j => one_div_nonneg.mpr (hc j).le)
    (evidenceProcess_adapted ℱ action observation E φ target ha hy hφ)
    (fun j n => Filter.Eventually.of_forall (fun ω => by
      simpa only [zero_add,evidenceProcess] using evidence_mem_Icc (ℱ.le n) (E n) (φ j n) (hb j n)
        (target j) (c j) (hc j) (hcover j n) ω)) α hα hs δ hbudget hδ1
  apply ht.trans
  apply ENNReal.toReal_mono (measure_ne_top _ _)
  apply measure_mono_ae
  filter_upwards [centeredSum_eq_kernelSum_ae ℱ action observation E φ target hφ hb c hc hcover]
    with ω hω
  intro hgood j n
  rw [← hω j (n+1)]
  exact hgood j n

omit [Countable J] [IsProbabilityMeasure μ] [Fintype A] [MeasurableSingletonClass A] in
/-- A rule and a positive observation time selected using the data already
belong to the same simultaneous contextual evidence event. -/
theorem covered_bound_at_selected_time (φ : J → ℕ → Ω × Y → ℝ) (target : J → A)
    (c : J → ℝ) (α : J → NNReal) (ω : Ω)
    (hall : ∀ j n,
      |(∑ i∈Finset.range (n+1),evidenceProcess ℱ action observation E φ target j i ω)-
        ∑ i∈Finset.range (n+1),kernelMeanProcess ℱ action observation E φ target j i ω|≤
          (1/c j)*PredictableResidual.boundary (n+1) (α j))
    (time : Ω → ℕ) (rule : Ω → J) (ht : 0<time ω) :
    |(∑ i∈Finset.range (time ω),evidenceProcess ℱ action observation E φ target (rule ω) i ω)-
      ∑ i∈Finset.range (time ω),kernelMeanProcess ℱ action observation E φ target (rule ω) i ω|≤
        (1/c (rule ω))*PredictableResidual.boundary (time ω) (α (rule ω)) := by
  have he : (time ω-1)+1=time ω := by omega
  simpa only [he] using hall (rule ω) (time ω-1)

end Komorebi.LSM.CoveredAdaptiveActions
