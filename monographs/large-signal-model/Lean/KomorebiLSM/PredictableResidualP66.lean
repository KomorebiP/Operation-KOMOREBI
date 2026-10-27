import KomorebiLSM.PredictableResidualAnytime
import KomorebiLSM.PredictableResidualAffine

/-! Full P66: arbitrary probability sample spaces, actual conditional means,
finite/countable prospective budgets, general intervals including zero width,
and data-selected times on the same simultaneous event. -/
set_option autoImplicit false
namespace Komorebi.LSM.PredictableResidualGeneral
open MeasureTheory ProbabilityTheory Real PredictableResidual PredictableResidualAffine
open scoped BigOperators NNReal ENNReal
variable {Ω J : Type*} [mΩ : MeasurableSpace Ω] [Countable J]
variable {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- Every registered interval-valued adapted process obeys the true
conditional-sum boundary at all positive times, on an arbitrary sample space. -/
theorem predictable_sum_interval_rules (ℱ : Filtration ℕ mΩ) (X : J → ℕ → Ω → ℝ)
    (lower width : J → ℝ) (hw : ∀ j,0≤width j)
    (hX : ∀ j i,Measurable[ℱ (i+1)] (X j i))
    (hb : ∀ j i,∀ᵐ ω∂μ,X j i ω∈Set.Icc (lower j) (lower j+width j))
    (α : J → NNReal) (hα : ∀ j,0<α j) (hs : Summable α)
    (δ : NNReal) (hbudget : ∑' j,α j≤δ) (hδ1 : δ≤1) :
    1-(δ:ℝ)≤μ.real {ω | ∀ j n,|centeredSum (μ:=μ) ℱ (X j) (n+1) ω|≤
      width j*boundary (n+1) (α j)} := by
  have ht := time_uniform_rules ℱ (normalizedProcess lower width X)
    (normalized_adapted ℱ lower width X hX) (normalized_mem_unit_ae lower width X hw hb)
    α hα hs δ hbudget hδ1
  have htrans := normalized_bound_transfer_ae ℱ lower width X hX hw hb
    (fun j n => boundary (n+1) (α j))
  have hle : μ {ω | ∀ j n,|centeredSum (μ:=μ) ℱ
      (normalizedProcess lower width X j) (n+1) ω|≤boundary (n+1) (α j)}≤
      μ {ω | ∀ j n,|centeredSum (μ:=μ) ℱ (X j) (n+1) ω|≤
        width j*boundary (n+1) (α j)} := measure_mono_ae htrans
  exact ht.trans (ENNReal.toReal_mono (measure_ne_top _ _) hle)

omit [IsProbabilityMeasure μ] in
/-- The simultaneous interval event is measurable, not merely an arbitrary
validity predicate supplied with an outer-probability interpretation. -/
theorem interval_event_measurable (ℱ : Filtration ℕ mΩ) (X : J → ℕ → Ω → ℝ)
    (hX : ∀ j i,Measurable[ℱ (i+1)] (X j i)) (width : J → ℝ) (α : J → NNReal) :
    MeasurableSet {ω | ∀ j n,|centeredSum (μ:=μ) ℱ (X j) (n+1) ω|≤
      width j*boundary (n+1) (α j)} := by
  simp only [Set.ofPred_forall]
  apply MeasurableSet.iInter
  intro j
  apply MeasurableSet.iInter
  intro n
  exact measurableSet_le (centeredSum_measurable ℱ (X j) (hX j) (n+1)).norm measurable_const

/-- The [0,1] residual/drift certificate for arbitrary countable rule indices. -/
theorem predictable_residual_certificate_countable (ℱ : Filtration ℕ mΩ)
    (X p : J → ℕ → Ω → ℝ)
    (hX : ∀ j i,Measurable[ℱ (i+1)] (X j i))
    (hb : ∀ j i,∀ᵐ ω∂μ,X j i ω∈Set.Icc (0:ℝ) 1)
    (α : J → NNReal) (hα : ∀ j,0<α j) (hs : Summable α)
    (δ : NNReal) (hbudget : ∑' j,α j≤δ) (hδ1 : δ≤1) :
    1-(δ:ℝ)≤μ.real {ω | ∀ j n,
      |observedResidual (X j) (p j) (n+1) ω-
        conditionalDrift (μ:=μ) ℱ (X j) (p j) (n+1) ω|≤boundary (n+1) (α j)} := by
  simpa only [residual_sub_drift] using time_uniform_rules ℱ X hX hb α hα hs δ hbudget hδ1

/-- Full P66 on the actual measurable residual/drift event. The predictions
may change with time; their errors cancel exactly. The interval width may be zero. -/
theorem predictable_residual_interval_certificate (ℱ : Filtration ℕ mΩ)
    (X p : J → ℕ → Ω → ℝ) (lower width : J → ℝ) (hw : ∀ j,0≤width j)
    (hX : ∀ j i,Measurable[ℱ (i+1)] (X j i))
    (hb : ∀ j i,∀ᵐ ω∂μ,X j i ω∈Set.Icc (lower j) (lower j+width j))
    (α : J → NNReal) (hα : ∀ j,0<α j) (hs : Summable α)
    (δ : NNReal) (hbudget : ∑' j,α j≤δ) (hδ1 : δ≤1) :
    MeasurableSet {ω | ∀ j n,
      |observedResidual (X j) (p j) (n+1) ω-
        conditionalDrift (μ:=μ) ℱ (X j) (p j) (n+1) ω|≤width j*boundary (n+1) (α j)} ∧
    1-(δ:ℝ)≤μ.real {ω | ∀ j n,
      |observedResidual (X j) (p j) (n+1) ω-
        conditionalDrift (μ:=μ) ℱ (X j) (p j) (n+1) ω|≤width j*boundary (n+1) (α j)} := by
  constructor
  · simpa only [residual_sub_drift] using interval_event_measurable ℱ X hX width α
  · simpa only [residual_sub_drift] using
      predictable_sum_interval_rules ℱ X lower width hw hX hb α hα hs δ hbudget hδ1

omit [Countable J] in
/-- Finite registrations retain the literal finite sum of their budgets. -/
theorem predictable_residual_interval_finite [Fintype J] (ℱ : Filtration ℕ mΩ)
    (X p : J → ℕ → Ω → ℝ) (lower width : J → ℝ) (hw : ∀ j,0≤width j)
    (hX : ∀ j i,Measurable[ℱ (i+1)] (X j i))
    (hb : ∀ j i,∀ᵐ ω∂μ,X j i ω∈Set.Icc (lower j) (lower j+width j))
    (α : J → NNReal) (hα : ∀ j,0<α j) (δ : NNReal)
    (hbudget : ∑ j,α j≤δ) (hδ1 : δ≤1) :
    1-(δ:ℝ)≤μ.real {ω | ∀ j n,
      |observedResidual (X j) (p j) (n+1) ω-
        conditionalDrift (μ:=μ) ℱ (X j) (p j) (n+1) ω|≤width j*boundary (n+1) (α j)} := by
  exact (predictable_residual_interval_certificate ℱ X p lower width hw hX hb α hα
    (summable_of_hasFiniteSupport (Set.toFinite _)) δ (by simpa only [tsum_fintype] using hbudget) hδ1).2

omit [Countable J] [IsProbabilityMeasure μ] in
/-- Exact reindexing changes neither the simultaneous residual event nor the
actual total prospective budget; no padded rules consume extra probability. -/
theorem registration_transport {K : Type*} (e : K ≃ J) (ℱ : Filtration ℕ mΩ)
    (X p : J → ℕ → Ω → ℝ) (width : J → ℝ) (α : J → NNReal) (hs : Summable α) :
    Summable (fun k => α (e k)) ∧ (∑' k,α (e k))=∑' j,α j ∧
    {ω | ∀ k n,|observedResidual (X (e k)) (p (e k)) (n+1) ω-
      conditionalDrift (μ:=μ) ℱ (X (e k)) (p (e k)) (n+1) ω|≤
        width (e k)*boundary (n+1) (α (e k))}=
    {ω | ∀ j n,|observedResidual (X j) (p j) (n+1) ω-
      conditionalDrift (μ:=μ) ℱ (X j) (p j) (n+1) ω|≤width j*boundary (n+1) (α j)} := by
  obtain ⟨hS,hSum⟩ := CountableConfidence.budget_transport e α hs
  refine ⟨hS,hSum,?_⟩
  ext ω
  exact CountableConfidence.forall_transport e (fun j => ∀ n : ℕ,
    |observedResidual (X j) (p j) (n+1) ω-conditionalDrift (μ:=μ) ℱ (X j) (p j) (n+1) ω|≤
      width j*boundary (n+1) (α j))

omit [Countable J] [IsProbabilityMeasure μ] in
/-- A data-selected positive time and registered rule are already included in
the same simultaneous event; no optional stopping or independence is needed. -/
theorem selected_interval_bound (ℱ : Filtration ℕ mΩ)
    (X p : J → ℕ → Ω → ℝ) (width : J → ℝ) (α : J → NNReal) (ω : Ω)
    (hall : ∀ j n,|observedResidual (X j) (p j) (n+1) ω-
      conditionalDrift (μ:=μ) ℱ (X j) (p j) (n+1) ω|≤width j*boundary (n+1) (α j))
    (time : Ω → ℕ) (rule : Ω → J) (ht : 0<time ω) :
    |observedResidual (X (rule ω)) (p (rule ω)) (time ω) ω-
      conditionalDrift (μ:=μ) ℱ (X (rule ω)) (p (rule ω)) (time ω) ω|≤
        width (rule ω)*boundary (time ω) (α (rule ω)) := by
  have he : (time ω-1)+1=time ω := by omega
  simpa only [he] using hall (rule ω) (time ω-1)

end Komorebi.LSM.PredictableResidualGeneral
