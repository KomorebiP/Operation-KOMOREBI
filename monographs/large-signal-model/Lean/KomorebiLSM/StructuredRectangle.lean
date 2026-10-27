import KomorebiLSM.CurvedMomentRecordTV
import KomorebiLSM.MarkovWindows

/-! P87's deterministic whole-rectangle certificate. The returned instruments,
observation records, Markov marginals and rolling windows are the actual laws
of the declared curved-moment family. Statistical coverage is a separate input
to the consuming process theorem, never an assumption of these domain bounds. -/
set_option autoImplicit false
namespace Komorebi.LSM.CurvedMoment.StructuredRectangle
open MeasureTheory ProbabilityTheory SequentialLowerCertificate MarkovStability
open scoped ENNReal
noncomputable section

structure Rectangle where
  lowerA : ℝ
  upperA : ℝ
  lowerB : ℝ
  upperB : ℝ

namespace Rectangle

def carrier (B : Rectangle) : Set (ℝ × ℝ) :=
  {q | q.1∈Set.Icc B.lowerA B.upperA ∧ q.2∈Set.Icc B.lowerB B.upperB}

def boundA (B : Rectangle) : ℝ := max |B.lowerA| |B.upperA|
def boundB (B : Rectangle) : ℝ := max |B.lowerB| |B.upperB|
def densityFloor (B : Rectangle) : ℝ := 1-B.boundA-B.boundB
def distanceA (B : Rectangle) (center : ℝ × ℝ) : ℝ :=
  max |B.lowerA-center.1| |B.upperA-center.1|
def distanceB (B : Rectangle) (center : ℝ × ℝ) : ℝ :=
  max |B.lowerB-center.2| |B.upperB-center.2|

theorem interval_abs_le (l u a : ℝ) (ha : a∈Set.Icc l u) :
    |a|≤max |l| |u| := by
  apply abs_le.mpr
  constructor
  · exact (neg_le_neg (le_max_left |l| |u|)).trans ((neg_abs_le l).trans ha.1)
  · exact ha.2.trans ((le_abs_self u).trans (le_max_right |l| |u|))

theorem interval_distance_le (l u c a : ℝ) (ha : a∈Set.Icc l u) :
    |a-c|≤max |l-c| |u-c| :=
  interval_abs_le (l-c) (u-c) (a-c) ⟨sub_le_sub_right ha.1 c,sub_le_sub_right ha.2 c⟩

theorem member_diamond (B : Rectangle) {q : ℝ × ℝ} (hq : q∈B.carrier) :
    |q.1|+|q.2|≤1-B.densityFloor := by
  have ha := interval_abs_le B.lowerA B.upperA q.1 hq.1
  have hb := interval_abs_le B.lowerB B.upperB q.2 hq.2
  change |q.1|+|q.2|≤1-(1-max |B.lowerA| |B.upperA|-max |B.lowerB| |B.upperB|)
  linarith

theorem densityFloor_le_one (B : Rectangle) : B.densityFloor≤1 := by
  have ha : 0≤B.boundA := (abs_nonneg B.lowerA).trans (le_max_left _ _)
  have hb : 0≤B.boundB := (abs_nonneg B.lowerB).trans (le_max_left _ _)
  dsimp [densityFloor]
  linarith

theorem member_distances (B : Rectangle) (center : ℝ × ℝ) {q : ℝ × ℝ}
    (hq : q∈B.carrier) :
    |q.1-center.1|≤B.distanceA center ∧ |q.2-center.2|≤B.distanceB center :=
  ⟨interval_distance_le _ _ _ _ hq.1,interval_distance_le _ _ _ _ hq.2⟩

theorem distanceA_nonneg (B : Rectangle) (center : ℝ × ℝ) : 0≤B.distanceA center :=
  (abs_nonneg _).trans (le_max_left _ _)
theorem distanceB_nonneg (B : Rectangle) (center : ℝ × ℝ) : 0≤B.distanceB center :=
  (abs_nonneg _).trans (le_max_left _ _)

variable {μ : Measure ℝ} (R : Reference μ)

/-- Every member, including the endpoints, defines its literal positive,
integrated-mass-preserving operator on the full curved cone. -/
def instrument (B : Rectangle) (hfloor : 0≤B.densityFloor) (q : ℝ × ℝ)
    (hq : q∈B.carrier) :
    ContinuousInstrument.DensityInstrument (A:=Unit) probabilityCone μ :=
  R.instrument q.1 q.2 B.densityFloor hfloor (B.member_diamond hq)

/-- Every finite horizon is a probability law; the geometry certificate
covers the entire rectangle rather than only its selected center. -/
theorem all_horizon_probability (B : Rectangle) (hfloor : 0≤B.densityFloor)
    (q : ℝ × ℝ) (hq : q∈B.carrier)
    (π : ContinuousRecords.Policy (A:=Unit) (Y:=ℝ))
    (z : ContinuousInstrument.DensityInstrument.State probabilityCone) (n : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw (B.instrument R hfloor q hq) π z.1 n) := by
  let := R.probability
  exact ContinuousRecords.recordLaw_probability _ π z n

def kernel (B : Rectangle) (hfloor : 0≤B.densityFloor) (q : ℝ × ℝ)
    (hq : q∈B.carrier) : Kernel ℝ ℝ :=
  R.completedKernel q.1 q.2 B.densityFloor hfloor (B.member_diamond hq)

instance kernel_markov (B : Rectangle) (hfloor : 0≤B.densityFloor) (q : ℝ × ℝ)
    (hq : q∈B.carrier) : IsMarkovKernel (B.kernel R hfloor q hq) := by
  unfold kernel
  infer_instance

def errorBudget (B : Rectangle) (center : ℝ × ℝ) : ℝ :=
  R.parameterBudget (B.distanceA center) (B.distanceB center)

theorem errorBudget_nonneg (B : Rectangle) (center : ℝ × ℝ) : 0≤B.errorBudget R center :=
  R.parameterBudget_nonneg (B.distanceA_nonneg center) (B.distanceB_nonneg center)

instance instrument_observation_probability (B : Rectangle) (hfloor : 0≤B.densityFloor)
    (q : ℝ × ℝ) (hq : q∈B.carrier) (s : Signal) (T : ℕ) : IsProbabilityMeasure
      (ContinuousRecords.observationLaw (B.instrument R hfloor q hq) (fun _ => ()) (curve s) T) := by
  unfold instrument
  infer_instance

/-- Exact next-observation TV for every common normalized state. -/
theorem observation_bound [IsProbabilityMeasure μ] (B : Rectangle) (hfloor : 0≤B.densityFloor)
    (q center : ℝ × ℝ) (hq : q∈B.carrier) (hc : center∈B.carrier)
    (z : ContinuousInstrument.DensityInstrument.State probabilityCone) :
    lawTV ((B.instrument R hfloor q hq).kernel () z)
      ((B.instrument R hfloor center hc).kernel () z)≤B.errorBudget R center := by
  obtain ⟨ha,hb⟩ := B.member_distances center hq
  exact R.observation_lawTV_le q.1 q.2 B.densityFloor center.1 center.2 B.densityFloor
    (B.distanceA center) (B.distanceB center) hfloor (B.member_diamond hq)
    hfloor (B.member_diamond hc) ha hb z

/-- Parameter uncertainty yields the actual operator-product record bound,
without adding a state-estimation term. -/
theorem complete_record_bound (B : Rectangle) (hfloor : 0≤B.densityFloor)
    (q center : ℝ × ℝ) (hq : q∈B.carrier) (hc : center∈B.carrier)
    (s : Signal) (T : ℕ) :
    lawTV (ContinuousRecords.observationLaw (B.instrument R hfloor q hq)
      (fun _ => ()) (curve s) T)
      (ContinuousRecords.observationLaw (B.instrument R hfloor center hc)
        (fun _ => ()) (curve s) T)≤min 1 ((T:ℝ)*B.errorBudget R center) := by
  obtain ⟨ha,hb⟩ := B.member_distances center hq
  exact R.observationLaw_lawTV_le q.1 q.2 B.densityFloor center.1 center.2 B.densityFloor
    (B.distanceA center) (B.distanceB center) hfloor (B.member_diamond hq)
    hfloor (B.member_diamond hc) ha hb s T

/-- The completed autonomous kernels retain the same pointwise row budget,
including declared completions at histories outside the interval support. -/
theorem kernel_row_bound (B : Rectangle) (hfloor : 0≤B.densityFloor)
    (q center : ℝ × ℝ) (hq : q∈B.carrier) (hc : center∈B.carrier) (u : ℝ) :
    lawTV (B.kernel R hfloor q hq u) (B.kernel R hfloor center hc u)≤B.errorBudget R center := by
  obtain ⟨ha,hb⟩ := B.member_distances center hq
  exact R.signalKernel_lawTV_le q.1 q.2 B.densityFloor center.1 center.2 B.densityFloor
    (B.distanceA center) (B.distanceB center) hfloor (B.member_diamond hq)
    hfloor (B.member_diamond hc) ha hb (observedSignal u)

/-- The density floor is an actual measure minorization, not an asserted
contraction coefficient. The same reference measure works for every member. -/
theorem kernel_minorized (B : Rectangle) (hfloor : 0≤B.densityFloor)
    (q : ℝ × ℝ) (hq : q∈B.carrier) :
    Minorized (B.kernel R hfloor q hq) B.densityFloor μ := by
  intro u
  change ENNReal.ofReal B.densityFloor • μ≤
    R.signalKernel q.1 q.2 B.densityFloor hfloor (B.member_diamond hq) (observedSignal u)
  rw [R.signalKernel_apply]
  calc
    ENNReal.ofReal B.densityFloor • μ=
        μ.withDensity (fun _ => ENNReal.ofReal B.densityFloor) := by simp
    _ ≤ _ := by
      apply withDensity_mono
      filter_upwards [R.support] with v hv
      apply ENNReal.ofReal_le_ofReal
      have hz : curve (observedSignal u)∈normalized := by
        rw [←base_eq_normalized]
        exact (curveState (observedSignal u)).2
      have hl := likelihood_lower q.1 q.2 B.densityFloor v hfloor (B.member_diamond hq) hv hz
      convert hl using 1
      simp [likelihood,curve]
      ring

/-- The exact geometric marginal estimate for the actual autonomous kernels,
including the complete-refresh endpoint when the floor equals one. -/
theorem marginal_bound (B : Rectangle) (hfloor : 0≤B.densityFloor)
    (hpositive : 0<B.densityFloor) (q center : ℝ × ℝ)
    (hq : q∈B.carrier) (hc : center∈B.carrier)
    (ν η : Measure ℝ) [IsProbabilityMeasure ν] [IsProbabilityMeasure η] (t : ℕ) :
    lawTV (MarkovStability.marginal (B.kernel R hfloor q hq) ν t)
      (MarkovStability.marginal (B.kernel R hfloor center hc) η t)≤
      min 1 ((1-B.densityFloor)^t*lawTV ν η+
        B.errorBudget R center*(1-(1-B.densityFloor)^t)/B.densityFloor) := by
  let := R.probability
  exact MarkovStability.marginal_bound _ _ μ _ _ hpositive B.densityFloor_le_one
    (B.kernel_minorized R hfloor q hq) (B.kernel_row_bound R hfloor q center hq hc) ν η t

/-- A common initial law gives the uniform all-time one-marginal bound. -/
theorem marginal_uniform (B : Rectangle) (hfloor : 0≤B.densityFloor)
    (hpositive : 0<B.densityFloor) (q center : ℝ × ℝ)
    (hq : q∈B.carrier) (hc : center∈B.carrier)
    (ν : Measure ℝ) [IsProbabilityMeasure ν] (t : ℕ) :
    lawTV (MarkovStability.marginal (B.kernel R hfloor q hq) ν t)
      (MarkovStability.marginal (B.kernel R hfloor center hc) ν t)≤
      min 1 (B.errorBudget R center/B.densityFloor) := by
  let := R.probability
  exact MarkovStability.marginal_same_initial_uniform _ _ μ _ _ hpositive B.densityFloor_le_one
    (B.errorBudget_nonneg R center) (B.kernel_minorized R hfloor q hq)
    (B.kernel_row_bound R hfloor q center hq hc) ν t

/-- L transitions contain L+1 consecutive observations; the literal rolling
window has the geometric entry-state budget plus L conditional-law errors. -/
theorem rolling_window_bound (B : Rectangle) (hfloor : 0≤B.densityFloor)
    (hpositive : 0<B.densityFloor) (q center : ℝ × ℝ)
    (hq : q∈B.carrier) (hc : center∈B.carrier)
    (ν η : Measure ℝ) [IsProbabilityMeasure ν] [IsProbabilityMeasure η] (t L : ℕ) :
    lawTV (rollingWindowLaw (B.kernel R hfloor q hq) ν t L)
      (rollingWindowLaw (B.kernel R hfloor center hc) η t L)≤
      min 1 ((1-B.densityFloor)^t*lawTV ν η+
        B.errorBudget R center*(1-(1-B.densityFloor)^t)/B.densityFloor+
          (L:ℝ)*B.errorBudget R center) := by
  let := R.probability
  exact MarkovStability.rollingWindow_geometric_bound _ _ μ _ _ hpositive B.densityFloor_le_one
    (B.kernel_minorized R hfloor q hq) (B.kernel_row_bound R hfloor q center hq hc) ν η t L

/-- The common-initial-law window bound is uniform in its start time, while
still retaining one conditional-law error for each additional observation. -/
theorem rolling_window_uniform (B : Rectangle) (hfloor : 0≤B.densityFloor)
    (hpositive : 0<B.densityFloor) (q center : ℝ × ℝ)
    (hq : q∈B.carrier) (hc : center∈B.carrier)
    (ν : Measure ℝ) [IsProbabilityMeasure ν] (t L : ℕ) :
    lawTV (rollingWindowLaw (B.kernel R hfloor q hq) ν t L)
      (rollingWindowLaw (B.kernel R hfloor center hc) ν t L)≤
      min 1 (B.errorBudget R center/B.densityFloor+(L:ℝ)*B.errorBudget R center) := by
  let := R.probability
  exact MarkovStability.rollingWindow_same_initial_uniform _ _ μ _ _ hpositive B.densityFloor_le_one
    (B.errorBudget_nonneg R center) (B.kernel_minorized R hfloor q hq)
    (B.kernel_row_bound R hfloor q center hq hc) ν t L

end Rectangle
end
end Komorebi.LSM.CurvedMoment.StructuredRectangle
