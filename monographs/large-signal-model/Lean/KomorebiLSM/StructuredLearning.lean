import KomorebiLSM.ObservableMomentConditional
import KomorebiLSM.RationalRegressionConfidence
import KomorebiLSM.CurvedMomentMarkov

/-! P87: the two predictable scalar regressions are derived from the literal
declared observation law before their common all-time coverage event is used.
The true parameters need not satisfy the sufficient diamond test at early
checkpoints. Their actual nonnegative conditional density is an explicit model
assumption, rather than a claimed consequence of one observed path. -/
set_option autoImplicit false
namespace Komorebi.LSM.CurvedMoment
open MeasureTheory ProbabilityTheory
open scoped ENNReal
noncomputable section

namespace Reference
variable {ν : Measure ℝ} (R : Reference ν)

/-- A globally declared true transition law. The sufficient rectangle test is
not assumed here: only the actual conditional density and its nonnegativity. -/
structure TrueKernel (_R : Reference ν) (a b : ℝ) where
  kernel : Kernel Signal ℝ
  markov : IsMarkovKernel kernel
  density : ∀ s,kernel s=ν.withDensity
    (fun u => ENNReal.ofReal (1+a*s*u+b*(s:ℝ)^2*legendre u))
  nonnegative : ∀ s : Signal,∀ᵐ u∂ν,0≤1+a*s*u+b*(s:ℝ)^2*legendre u

namespace TrueKernel
variable {R} {a b : ℝ} (K : R.TrueKernel a b)

theorem integral (s : Signal) (g : ℝ → ℝ) :
    (∫ u,g u∂K.kernel s)=∫ u,g u*likelihood a b u (curve s)∂ν := by
  rw [K.density]
  have hd : Measurable (fun u : ℝ =>
      ENNReal.ofReal (1+a*(s:ℝ)*u+b*(s:ℝ)^2*legendre u)) := by
    unfold legendre
    fun_prop
  rw [integral_withDensity_eq_integral_toReal_smul hd
    (Filter.Eventually.of_forall (fun _ => ENNReal.ofReal_lt_top))]
  apply integral_congr_ae
  filter_upwards [K.nonnegative s] with u hu
  rw [ENNReal.toReal_ofReal hu]
  change (1+a*(s:ℝ)*u+b*(s:ℝ)^2*legendre u)*g u=g u*likelihood a b u (curve s)
  simp [likelihood,curve]
  ring

theorem signal_mean (s : Signal) : (∫ u,u∂K.kernel s)=a/3*s := by
  rw [K.integral,R.integral_signal_likelihood]
  simp [curve]
  ring

theorem legendre_mean (s : Signal) : (∫ u,legendre u∂K.kernel s)=b/5*(s:ℝ)^2 := by
  rw [K.integral,R.integral_legendre_likelihood]
  simp [curve]
  ring

end TrueKernel

section Process
variable {Ω H : Type*} [mΩ : MeasurableSpace Ω] [mH : MeasurableSpace H]
variable {μ : Measure Ω} [IsProbabilityMeasure μ] (F : Filtration ℕ mΩ)
variable {a b : ℝ} (K : R.TrueKernel a b)

/-- The conditional law is recorded as an equality of actual joint measures.
Current and next scalar observations are accessible from the recorded history.
The filtration is exactly its declared history sigma algebra. -/
structure ObservableProcess where
  history : ℕ → Ω → H
  history_measurable : ∀ n,Measurable[F n] (history n)
  history_sigma : ∀ n,F n=mH.comap (history n)
  signal : ℕ → H → Signal
  signal_measurable : ∀ n,Measurable (signal n)
  observation : ℕ → Ω → Signal
  observation_measurable : ∀ n,Measurable[F (n+1)] (observation n)
  next_signal : ∀ n ω,signal (n+1) (history (n+1) ω)=observation n ω
  joint : ∀ n,μ.map (fun ω => (history n ω,(observation n ω : ℝ)))=
    (μ.map (history n)) ⊗ₘ (K.kernel.comap (signal n) (signal_measurable n))

namespace ObservableProcess
variable {R F K} (P : R.ObservableProcess (H := H) (μ := μ) F K)

def current (n : ℕ) (ω : Ω) : ℝ := P.signal n (P.history n ω)
def designA (n : ℕ) (ω : Ω) : ℝ := P.current n ω/3
def designB (n : ℕ) (ω : Ω) : ℝ := (P.current n ω)^2/5
def responseA (n : ℕ) (ω : Ω) : ℝ := P.observation n ω
def responseB (n : ℕ) (ω : Ω) : ℝ := legendre (P.responseA n ω)

omit [IsProbabilityMeasure μ] in
theorem current_measurable (n : ℕ) : Measurable[F n] (P.current n) :=
  measurable_subtype_coe.comp ((P.signal_measurable n).comp (P.history_measurable n))

omit [IsProbabilityMeasure μ] in
theorem designA_measurable (n : ℕ) : Measurable[F n] (P.designA n) :=
  (P.current_measurable n).div_const 3

omit [IsProbabilityMeasure μ] in
theorem designB_measurable (n : ℕ) : Measurable[F n] (P.designB n) :=
  ((P.current_measurable n).pow_const 2).div_const 5

omit [IsProbabilityMeasure μ] in
theorem responseA_measurable (n : ℕ) : Measurable[F (n+1)] (P.responseA n) :=
  measurable_subtype_coe.comp (P.observation_measurable n)

omit [IsProbabilityMeasure μ] in
theorem responseB_measurable (n : ℕ) : Measurable[F (n+1)] (P.responseB n) := by
  have hy := P.responseA_measurable n
  unfold responseB legendre
  exact (((hy.pow_const 2).const_mul 3).sub_const 1).div_const 2

omit [IsProbabilityMeasure μ] in
theorem responseA_bounds (n : ℕ) (ω : Ω) : P.responseA n ω∈Set.Icc (-1:ℝ) 1 :=
  (P.observation n ω).2

omit [IsProbabilityMeasure μ] in
theorem responseB_bounds (n : ℕ) (ω : Ω) : P.responseB n ω∈Set.Icc (-(1/2):ℝ) 1 := by
  have hu := P.responseA_bounds n ω
  have hs : (P.responseA n ω)^2≤1 := (sq_le_one_iff_abs_le_one _).mpr (abs_le.mpr hu)
  unfold responseB legendre
  constructor <;> nlinarith [sq_nonneg (P.responseA n ω)]

/-- Conditional means are consequences of the joint law, not input fields. -/
theorem responseA_condExp (n : ℕ) :
    (μ[P.responseA n|F n])=ᵐ[μ] (fun ω => a*P.designA n ω) := by
  let := K.markov
  let κ := K.kernel.comap (P.signal n) (P.signal_measurable n)
  have hh := (P.history_measurable n).mono (F.le n) le_rfl
  have hy := (P.responseA_measurable n).mono (F.le (n+1)) le_rfl
  have hi : Integrable (P.responseA n) μ :=
    Integrable.of_mem_Icc (-1:ℝ) 1 hy.aemeasurable
      (Filter.Eventually.of_forall (P.responseA_bounds n))
  have hc := ObservableMoments.history_condExp (P.history n) (P.responseA n)
    hh hy κ (P.joint n) (fun p : H × ℝ => p.2) measurable_snd hi
  rw [← P.history_sigma n] at hc
  filter_upwards [hc] with ω hω
  rw [hω]
  change (∫ u,u∂K.kernel (P.signal n (P.history n ω)))=a*P.designA n ω
  rw [K.signal_mean]
  unfold designA current
  ring

theorem responseB_condExp (n : ℕ) :
    (μ[P.responseB n|F n])=ᵐ[μ] (fun ω => b*P.designB n ω) := by
  let := K.markov
  let κ := K.kernel.comap (P.signal n) (P.signal_measurable n)
  have hh := (P.history_measurable n).mono (F.le n) le_rfl
  have hy := (P.responseA_measurable n).mono (F.le (n+1)) le_rfl
  have hm := (P.responseB_measurable n).mono (F.le (n+1)) le_rfl
  have hi : Integrable (P.responseB n) μ :=
    Integrable.of_mem_Icc (-(1/2):ℝ) 1 hm.aemeasurable
      (Filter.Eventually.of_forall (P.responseB_bounds n))
  have hg : Measurable (fun p : H × ℝ => legendre p.2) := by unfold legendre;fun_prop
  have hc := ObservableMoments.history_condExp (P.history n) (P.responseA n)
    hh hy κ (P.joint n) (fun p : H × ℝ => legendre p.2) hg hi
  rw [← P.history_sigma n] at hc
  filter_upwards [hc] with ω hω
  change (μ[fun ω => legendre (P.responseA n ω)|F n]) ω=_
  rw [hω]
  change (∫ u,legendre u∂K.kernel (P.signal n (P.history n ω)))=b*P.designB n ω
  rw [K.legendre_mean]
  unfold designB current
  ring

/-- The actual prescribed regressions and rational outward arithmetic provide
one measurable event of probability at least 19/20 covering every finite time.
This endpoint assumes neither a confidence event nor a conditional mean. -/
theorem simultaneous_rational_coverage (endpointGrid : ℕ) (he : 0<endpointGrid)
    (ha : |a|≤1) (hb : |b|≤1) :
    let G := RegressionConfidence.scalarGood 1 (1/40) P.designA P.responseA a∩
      RegressionConfidence.scalarGood (3/4) (1/40) P.designB P.responseB b
    MeasurableSet G ∧ (19/20:ℝ)≤μ.real G ∧ ∀ ω∈G,∀ n,
      a∈Set.Icc
        (RationalRegressionConfidence.lower (10^12) endpointGrid 1 (1/40) P.designA P.responseA n ω:ℝ)
        (RationalRegressionConfidence.upper (10^12) endpointGrid 1 (1/40) P.designA P.responseA n ω:ℝ) ∧
      b∈Set.Icc
        (RationalRegressionConfidence.lower (10^12) endpointGrid (3/4) (1/40) P.designB P.responseB n ω:ℝ)
        (RationalRegressionConfidence.upper (10^12) endpointGrid (3/4) (1/40) P.designB P.responseB n ω:ℝ) := by
  exact RationalRegressionConfidence.two_regression_outer_certificate F endpointGrid he
    P.designA P.responseA P.designB P.responseB a b
    P.designA_measurable P.responseA_measurable P.designB_measurable P.responseB_measurable
    (fun n => Filter.Eventually.of_forall (P.responseA_bounds n))
    (fun n => Filter.Eventually.of_forall (P.responseB_bounds n))
    P.responseA_condExp P.responseB_condExp ha hb

end ObservableProcess
end Process
end Reference
end
end Komorebi.LSM.CurvedMoment
