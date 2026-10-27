import KomorebiLSM.PredictableResidualGeneral

/-! The actual all-time union bound on arbitrary sample spaces and arbitrary
finite/countable prospectively registered rule indices, with unchanged budgets. -/
set_option autoImplicit false
namespace Komorebi.LSM.PredictableResidualGeneral
open MeasureTheory ProbabilityTheory Real PredictableResidual
open scoped BigOperators NNReal ENNReal
variable {Ω : Type*} [mΩ : MeasurableSpace Ω]
variable {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- One predictable rule has the declared simultaneous boundary at every positive time. -/
theorem time_uniform_one (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i, Measurable[ℱ (i+1)] (X i))
    (hb : ∀ i, ∀ᵐ ω ∂μ, X i ω∈Set.Icc (0:ℝ) 1)
    (α : NNReal) (hα : 0<α) (hα1 : α≤1) :
    1-(α:ℝ) ≤ μ.real {ω | ∀ n, |centeredSum (μ:=μ) ℱ X (n+1) ω|≤boundary (n+1) α} := by
  let F : ℕ → Set Ω := fun n ↦ {ω | boundary (n+1) α < |centeredSum (μ:=μ) ℱ X (n+1) ω|}
  have hF : ∀ n, MeasurableSet (F n) := by
    intro n
    apply measurableSet_lt measurable_const
    exact (centeredSum_measurable ℱ X hX (n+1)).norm
  have hweights : Summable (fun n ↦ α*timeWeight n) := time_summable.mul_left α
  have hbudget : ∑' n, α*timeWeight n ≤ α := by
    rw [tsum_mul_left]
    simpa using mul_le_mul_of_nonneg_left time_budget α.coe_nonneg
  have hf : ∀ n, μ.real (F n) ≤ (α*timeWeight n:NNReal) := by
    intro n
    have ht := predictable_sum_tail ℱ X hX hb (by omega : 0<n+1)
      (boundary (n+1) α) (sqrt_nonneg _)
    rw [boundary_budget (by omega) (by exact_mod_cast hα) (by exact_mod_cast hα1)] at ht
    apply (measureReal_mono (by
      intro ω h
      exact (show boundary (n+1) α < |centeredSum (μ:=μ) ℱ X (n+1) ω| from h).le)).trans
      (ht.trans_eq ?_)
    simp only [timeWeight,NNReal.coe_mul,NNReal.coe_div,NNReal.coe_one,NNReal.coe_add,NNReal.coe_natCast]
    push_cast
    field_simp
    ring
  have hprob := CountableConfidence.simultaneous_coverage F hF
    (fun n ↦ α*timeWeight n) hweights α hbudget hf
  convert hprob using 1
  congr 1
  ext ω
  simp [F]

variable {J : Type*} [Countable J]

/-- All prospectively registered countably many rules share one all-time event. -/
theorem time_uniform_rules (ℱ : Filtration ℕ mΩ) (X : J → ℕ → Ω → ℝ)
    (hX : ∀ j i, Measurable[ℱ (i+1)] (X j i))
    (hb : ∀ j i, ∀ᵐ ω ∂μ, X j i ω∈Set.Icc (0:ℝ) 1)
    (α : J → NNReal) (hα : ∀ j, 0<α j) (hs : Summable α)
    (δ : NNReal) (hbudget : ∑' j, α j ≤ δ) (hδ1 : δ≤1) :
    1-(δ:ℝ) ≤ μ.real {ω | ∀ j n,
      |centeredSum (μ:=μ) ℱ (X j) (n+1) ω|≤boundary (n+1) (α j)} := by
  let F : J → Set Ω := fun j ↦ {ω | ∃ n,
    boundary (n+1) (α j) < |centeredSum (μ:=μ) ℱ (X j) (n+1) ω|}
  have hF : ∀ j, MeasurableSet (F j) := by
    intro j
    simp only [F,Set.ofPred_exists]
    apply MeasurableSet.iUnion
    intro n
    apply measurableSet_lt measurable_const
    exact (centeredSum_measurable ℱ (X j) (hX j) (n+1)).norm
  have hf : ∀ j, μ.real (F j)≤(α j:ℝ) := by
    intro j
    have hj : α j≤1 := (hs.le_tsum j (fun _ _ ↦ by positivity)).trans (hbudget.trans hδ1)
    have ht := time_uniform_one ℱ (X j) (hX j) (hb j) (α j) (hα j) hj
    have he : {ω | ∀ n, |centeredSum (μ:=μ) ℱ (X j) (n+1) ω|≤boundary (n+1) (α j)} =
        (F j)ᶜ := by ext ω; simp [F]
    rw [he,measureReal_compl (hF j)] at ht
    simp only [probReal_univ] at ht
    linarith
  have hprob := CountableConfidence.simultaneous_coverage F hF α hs δ hbudget hf
  convert hprob using 1
  congr 1
  ext ω
  simp [F]


omit [IsProbabilityMeasure μ] in
/-- The simultaneous unit-range event is genuinely measurable. -/
theorem unit_event_measurable (ℱ : Filtration ℕ mΩ) (X : J → ℕ → Ω → ℝ)
    (hX : ∀ j i,Measurable[ℱ (i+1)] (X j i)) (α : J → NNReal) :
    MeasurableSet {ω | ∀ j n,|centeredSum (μ:=μ) ℱ (X j) (n+1) ω|≤boundary (n+1) (α j)} := by
  simp only [Set.ofPred_forall]
  apply MeasurableSet.iInter
  intro j
  apply MeasurableSet.iInter
  intro n
  exact measurableSet_le (centeredSum_measurable ℱ (X j) (hX j) (n+1)).norm measurable_const

end Komorebi.LSM.PredictableResidualGeneral
