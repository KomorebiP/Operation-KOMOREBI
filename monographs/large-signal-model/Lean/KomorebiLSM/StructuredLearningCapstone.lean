import KomorebiLSM.StructuredLearning
import KomorebiLSM.StructuredRectangle

/-! Full P87: one all-time event covers the data-selected outward rectangle.
Every verified rectangle carries actual all-horizon probability laws and
parameter-to-law, complete-record, marginal and rolling-window bounds. -/
set_option autoImplicit false
namespace Komorebi.LSM.CurvedMoment
open MeasureTheory ProbabilityTheory SequentialLowerCertificate MarkovStability
noncomputable section

namespace StructuredRectangle.Rectangle
variable {ν : Measure ℝ}

/-- A derived theorem package for the entire submitted rectangle. Its fields
refer to actual measures and actual kernel iterates. No field is an assumption
in the construction below. -/
structure Certificate (B : StructuredRectangle.Rectangle) (R : Reference ν)
    (hfloor : 0≤B.densityFloor) [IsProbabilityMeasure ν] : Prop where
  probability : ∀ q (hq : q∈B.carrier)
    (π : ContinuousRecords.Policy (A:=Unit) (Y:=ℝ))
    (z : ContinuousInstrument.DensityInstrument.State probabilityCone) (n : ℕ),
    IsProbabilityMeasure (ContinuousRecords.recordLaw (B.instrument R hfloor q hq) π z.1 n)
  observation_error : ∀ q center (hq : q∈B.carrier) (hc : center∈B.carrier)
    (z : ContinuousInstrument.DensityInstrument.State probabilityCone),
    lawTV ((B.instrument R hfloor q hq).kernel () z)
      ((B.instrument R hfloor center hc).kernel () z)≤B.errorBudget R center
  record_error : ∀ q center (hq : q∈B.carrier) (hc : center∈B.carrier) (s : Signal) (T : ℕ),
    lawTV (ContinuousRecords.observationLaw (B.instrument R hfloor q hq) (fun _ => ()) (curve s) T)
      (ContinuousRecords.observationLaw (B.instrument R hfloor center hc) (fun _ => ()) (curve s) T)
      ≤min 1 ((T:ℝ)*B.errorBudget R center)
  marginal_geometric : ∀ (_hpositive : 0<B.densityFloor) q center
    (hq : q∈B.carrier) (hc : center∈B.carrier) (η ζ : Measure ℝ)
    [IsProbabilityMeasure η] [IsProbabilityMeasure ζ] (t : ℕ),
    lawTV (marginal (B.kernel R hfloor q hq) η t)
      (marginal (B.kernel R hfloor center hc) ζ t)≤
      min 1 ((1-B.densityFloor)^t*lawTV η ζ+
        B.errorBudget R center*(1-(1-B.densityFloor)^t)/B.densityFloor)
  window_geometric : ∀ (_hpositive : 0<B.densityFloor) q center
    (hq : q∈B.carrier) (hc : center∈B.carrier) (η ζ : Measure ℝ)
    [IsProbabilityMeasure η] [IsProbabilityMeasure ζ] (t L : ℕ),
    lawTV (rollingWindowLaw (B.kernel R hfloor q hq) η t L)
      (rollingWindowLaw (B.kernel R hfloor center hc) ζ t L)≤
      min 1 ((1-B.densityFloor)^t*lawTV η ζ+
        B.errorBudget R center*(1-(1-B.densityFloor)^t)/B.densityFloor+
          (L:ℝ)*B.errorBudget R center)
  marginal_error : ∀ (_hpositive : 0<B.densityFloor) q center
    (hq : q∈B.carrier) (hc : center∈B.carrier) (η : Measure ℝ) [IsProbabilityMeasure η] (t : ℕ),
    lawTV (marginal (B.kernel R hfloor q hq) η t)
      (marginal (B.kernel R hfloor center hc) η t)≤min 1 (B.errorBudget R center/B.densityFloor)
  window_error : ∀ (_hpositive : 0<B.densityFloor) q center
    (hq : q∈B.carrier) (hc : center∈B.carrier) (η : Measure ℝ) [IsProbabilityMeasure η] (t L : ℕ),
    lawTV (rollingWindowLaw (B.kernel R hfloor q hq) η t L)
      (rollingWindowLaw (B.kernel R hfloor center hc) η t L)
      ≤min 1 (B.errorBudget R center/B.densityFloor+(L:ℝ)*B.errorBudget R center)

/-- Deterministic internal validity is independent of whether a statistical
coverage event happens for a particular realized sample path. -/
theorem certificate (B : StructuredRectangle.Rectangle) (R : Reference ν)
    (hfloor : 0≤B.densityFloor) : @Certificate ν B R hfloor R.probability := by
  let := R.probability
  exact ⟨B.all_horizon_probability R hfloor,B.observation_bound R hfloor,
    B.complete_record_bound R hfloor,B.marginal_bound R hfloor,B.rolling_window_bound R hfloor,
    B.marginal_uniform R hfloor,B.rolling_window_uniform R hfloor⟩

end StructuredRectangle.Rectangle

namespace Reference
variable {ν : Measure ℝ} {R : Reference ν} {a b : ℝ}

/-- Whenever the true parameter belongs to a verified rectangle, its declared
actual law equals the certified member, rather than merely sharing moments. -/
theorem TrueKernel.matches_certified_member (K : R.TrueKernel a b)
    (B : StructuredRectangle.Rectangle) (htrue : (a,b)∈B.carrier)
    (hfloor : 0≤B.densityFloor) :
    K.kernel=R.signalKernel a b B.densityFloor hfloor (B.member_diamond htrue) := by
  ext s
  rw [K.density,R.signalKernel_apply]

namespace ObservableProcess
variable {Ω H : Type*} [mΩ : MeasurableSpace Ω] [mH : MeasurableSpace H]
variable {μ : Measure Ω} [IsProbabilityMeasure μ] {F : Filtration ℕ mΩ}
variable {K : R.TrueKernel a b} (P : R.ObservableProcess (H:=H) (μ:=μ) F K)

def coverageEvent : Set Ω :=
  RegressionConfidence.scalarGood 1 (1/40) P.designA P.responseA a∩
    RegressionConfidence.scalarGood (3/4) (1/40) P.designB P.responseB b

/-- The literal full outward-rounded rectangle from the two recorded scalar
regressions, with the prior intersection already included in its endpoints. -/
def returnedRectangle (endpointGrid n : ℕ) (ω : Ω) : StructuredRectangle.Rectangle where
  lowerA := RationalRegressionConfidence.lower (10^12) endpointGrid 1 (1/40) P.designA P.responseA n ω
  upperA := RationalRegressionConfidence.upper (10^12) endpointGrid 1 (1/40) P.designA P.responseA n ω
  lowerB := RationalRegressionConfidence.lower (10^12) endpointGrid (3/4) (1/40) P.designB P.responseB n ω
  upperB := RationalRegressionConfidence.upper (10^12) endpointGrid (3/4) (1/40) P.designB P.responseB n ω

/-- Full conditional data-to-domain endpoint. The selected finite time may
depend arbitrarily on the same observed data because the original measurable
event already covers every finite time. Every center and candidate in the full
rectangle receives the deterministic certificate. No stopping theorem, sample
independence, hidden-state estimate or nominal-only geometry test is assumed. -/
theorem observable_structured_learning (endpointGrid : ℕ) (he : 0<endpointGrid)
    (ha : |a|≤1) (hb : |b|≤1) :
    MeasurableSet P.coverageEvent ∧ (19/20:ℝ)≤μ.real P.coverageEvent ∧
    ∀ ω∈P.coverageEvent,∀ selectedTime : Ω → ℕ,
      let B := P.returnedRectangle endpointGrid (selectedTime ω) ω
      ∃ htrue : (a,b)∈B.carrier,∀ hfloor : 0≤B.densityFloor,
        @StructuredRectangle.Rectangle.Certificate ν B R hfloor R.probability ∧
        K.kernel=R.signalKernel a b B.densityFloor hfloor (B.member_diamond htrue) := by
  obtain ⟨hG,hprob,hcoverage⟩ := P.simultaneous_rational_coverage endpointGrid he ha hb
  refine ⟨hG,hprob,?_⟩
  intro ω hω selectedTime
  let B := P.returnedRectangle endpointGrid (selectedTime ω) ω
  have htrue : (a,b)∈B.carrier := hcoverage ω hω (selectedTime ω)
  refine ⟨htrue,fun hfloor => ⟨B.certificate R hfloor,?_⟩⟩
  exact K.matches_certified_member B htrue hfloor

end ObservableProcess
end Reference
end
end Komorebi.LSM.CurvedMoment
