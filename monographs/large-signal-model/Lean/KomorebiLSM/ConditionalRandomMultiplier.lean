import Mathlib.MeasureTheory.Function.ConditionalExpectation.PullOut
import Mathlib.MeasureTheory.Function.ConditionalExpectation.Indicator
import Mathlib.MeasureTheory.Function.SimpleFuncDense
import Mathlib.MeasureTheory.Integral.Bochner.Set
import Mathlib.MeasureTheory.Integral.Lebesgue.Add
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Tactic

/-! Deterministic conditional exponential bounds transfer to a predictable
random multiplier on an arbitrary probability space. Finite simple-function
approximation and nonnegative Fatou limits avoid a uniform all-parameter null
set and avoid any regular-conditional-distribution assumption on the sample
space. -/
set_option autoImplicit false
namespace Komorebi.LSM.RegressionConfidence
open MeasureTheory ProbabilityTheory Real Filter
open scoped ENNReal Topology
variable {Ω : Type*} {m : MeasurableSpace Ω} [mΩ : MeasurableSpace Ω]
variable {μ : Measure Ω}
/-- The normalized one-step exponential factor. -/
noncomputable def factor (X : Ω → ℝ) (σ : ℝ) (a : Ω → ℝ) (ω : Ω) : ℝ :=
  exp (a ω*X ω-(a ω)^2*σ^2/2)

variable {X : Ω → ℝ} {σ : ℝ}

variable (hm : m ≤ mΩ)

/-- The real coefficient is chosen before the almost-everywhere conclusion.
This field does not assert a uniform event for all coefficients. -/
structure ConditionalSubgaussian (hm : m ≤ mΩ) (X : Ω → ℝ) (σ : ℝ) (μ : @Measure Ω mΩ) : Prop where
  measurable : @Measurable Ω ℝ mΩ _ X
  integrable_exp : ∀ h : ℝ, Integrable (fun ω => exp (h*X ω)) μ
  condExp_le : ∀ h : ℝ, (μ[fun ω => exp (h*X ω)|m])≤ᵐ[μ]
    fun _ => exp (h^2*σ^2/2)

variable {hm}

omit [MeasurableSpace Ω] in
theorem factor_pos (a : Ω → ℝ) (ω : Ω) : 0<factor X σ a ω := exp_pos _

theorem factor_measurable (hX : @Measurable Ω ℝ mΩ _ X) {a : Ω → ℝ}
    (ha : @Measurable Ω ℝ mΩ _ a) : @Measurable Ω ℝ mΩ _ (factor X σ a) :=
  (ha.mul hX |>.sub (((ha.pow_const 2).mul_const (σ^2)).div_const 2)).exp

/-- A nonnegative pointwise Fatou limit inherits both integrability and an
integral budget. This is valid on any measurable sample space. -/
theorem nonnegative_limit_budget (ν : @Measure Ω mΩ) (f : Ω → ℝ) (fn : ℕ → Ω → ℝ)
    (hf : Measurable f) (h0 : ∀ ω,0≤f ω) (hfn0 : ∀ n ω,0≤fn n ω)
    (hfn : ∀ n,Integrable (fn n) ν) (C : ℝ) (hC : 0≤C)
    (hbudget : ∀ n,(∫ ω,fn n ω∂ν)≤C)
    (hlim : ∀ ω,Tendsto (fun n => fn n ω) atTop (𝓝 (f ω))) :
    Integrable f ν ∧ (∫ ω,f ω∂ν)≤C := by
  have hfatou : (∫⁻ ω,ENNReal.ofReal (f ω)∂ν)≤ENNReal.ofReal C := by
    calc (∫⁻ ω,ENNReal.ofReal (f ω)∂ν)=
        ∫⁻ ω,liminf (fun n => ENNReal.ofReal (fn n ω)) atTop∂ν := by
          apply lintegral_congr
          intro ω
          exact ((ENNReal.continuous_ofReal.tendsto _).comp (hlim ω)).liminf_eq.symm
      _ ≤ liminf (fun n => ∫⁻ ω,ENNReal.ofReal (fn n ω)∂ν) atTop :=
        lintegral_liminf_le' (fun n => (hfn n).aemeasurable.ennreal_ofReal)
      _ ≤ ENNReal.ofReal C := by
        apply liminf_le_of_frequently_le'
        apply Filter.Eventually.frequently
        exact Filter.Eventually.of_forall (fun n => by
          rw [← ofReal_integral_eq_lintegral_ofReal (hfn n) (ae_of_all _ (hfn0 n))]
          exact ENNReal.ofReal_le_ofReal (hbudget n))
  have hfi : Integrable f ν := ⟨hf.aestronglyMeasurable,
    (hasFiniteIntegral_iff_ofReal (ae_of_all _ h0)).2
      (lt_of_le_of_lt hfatou ENNReal.ofReal_lt_top)⟩
  refine ⟨hfi,?_⟩
  have hreal := ENNReal.toReal_mono ENNReal.ofReal_ne_top hfatou
  rw [← ofReal_integral_eq_lintegral_ofReal hfi (ae_of_all _ h0),
    ENNReal.toReal_ofReal (integral_nonneg h0),ENNReal.toReal_ofReal hC] at hreal
  exact hreal

namespace ConditionalSubgaussian
variable (H : ConditionalSubgaussian (mΩ := mΩ) hm X σ μ)
include H

theorem constant_factor_integrable (h : ℝ) : Integrable (factor X σ (fun _ => h)) μ := by
  have he : factor X σ (fun _ => h) = fun ω => exp (-(h^2*σ^2/2))*exp (h*X ω) := by
    funext ω
    dsimp [factor]
    rw [← exp_add]
    congr 1
    ring
  rw [he]
  exact (H.integrable_exp h).const_mul _

theorem constant_factor_condExp_le (h : ℝ) :
    (μ[factor X σ (fun _ => h)|m])≤ᵐ[μ] fun _ => 1 := by
  have he : factor X σ (fun _ => h) = exp (-(h^2*σ^2/2)) • (fun ω => exp (h*X ω)) := by
    funext ω
    simp only [factor, Pi.smul_apply, smul_eq_mul, ← exp_add]
    congr 1
    ring
  rw [he]
  filter_upwards [condExp_smul (μ := μ) (exp (-(h^2*σ^2/2))) (fun ω => exp (h*X ω)) m,
    H.condExp_le h] with ω hp hb
  rw [hp]
  simp only [Pi.smul_apply,smul_eq_mul]
  calc exp (-(h^2*σ^2/2))*(μ[fun ω => exp (h*X ω)|m]) ω ≤
      exp (-(h^2*σ^2/2))*exp (h^2*σ^2/2) := mul_le_mul_of_nonneg_left hb (exp_pos _).le
    _ = 1 := by rw [← exp_add]; simp

/-- Each finite-valued predictable multiplier uses only finitely many of the
deterministic-coefficient conditional bounds. -/
theorem simple_factor (a : @SimpleFunc Ω m ℝ) :
    Integrable (factor X σ a) μ ∧ (μ[factor X σ a|m])≤ᵐ[μ] fun _ => 1 := by
  classical
  induction a using SimpleFunc.induction' with
  | const c => exact ⟨H.constant_factor_integrable c,H.constant_factor_condExp_le c⟩
  | @pcw f g s hs hf hg =>
    change Integrable (factor X σ (s.piecewise f g)) μ ∧
      (μ[factor X σ (s.piecewise f g)|m])≤ᵐ[μ] fun _ => 1
    have he : factor X σ (s.piecewise f g) =
        s.indicator (factor X σ f)+sᶜ.indicator (factor X σ g) := by
      funext ω
      by_cases hω : ω∈s <;> simp [factor,hω]
    rw [he]
    have hfi := hf.1.indicator (hm _ hs)
    have hgi := hg.1.indicator (hm _ hs.compl)
    refine ⟨hfi.add hgi,?_⟩
    filter_upwards [condExp_add hfi hgi (m := m),condExp_indicator hf.1 hs,
      condExp_indicator hg.1 hs.compl,hf.2,hg.2] with ω ha hb hc hd he
    rw [ha]
    simp only [Pi.add_apply]
    rw [hb,hc]
    by_cases hω : ω∈s
    · simpa [hω] using hd
    · simpa [hω] using he

variable [IsProbabilityMeasure μ]

/-- A predictable multiplier is approximated by finite-valued predictable
functions. Fatou is applied separately on each conditioning event. -/
theorem random_factor_setIntegral (a : Ω → ℝ) (ha : Measurable[m] a)
    {s : Set Ω} (hs : MeasurableSet[m] s) :
    IntegrableOn (factor X σ a) s μ ∧ (∫ ω in s,factor X σ a ω∂μ)≤μ.real s := by
  let an (n : ℕ) : @SimpleFunc Ω m ℝ := by
    letI := m
    exact SimpleFunc.approxOn a ha Set.univ 0 (by simp) n
  have hlim (ω : Ω) : Tendsto (fun n => (an n) ω) atTop (𝓝 (a ω)) := by
    let : MeasurableSpace Ω := m
    exact SimpleFunc.tendsto_approxOn ha (by simp) (by simp)
  have hlimf (ω : Ω) : Tendsto (fun n => factor X σ (an n) ω) atTop (𝓝 (factor X σ a ω)) := by
    exact Real.continuous_exp.continuousAt.tendsto.comp
      (((hlim ω).mul_const (X ω)).sub ((((hlim ω).pow 2).mul_const (σ^2)).div_const 2))
  have hb (n : ℕ) : (∫ ω in s,factor X σ (an n) ω∂μ)≤μ.real s := by
    calc (∫ ω in s,factor X σ (an n) ω∂μ)=
        ∫ ω in s,(μ[factor X σ (an n)|m]) ω∂μ :=
          (setIntegral_condExp hm (H.simple_factor (an n)).1 hs).symm
      _ ≤ ∫ _ in s,(1:ℝ)∂μ :=
        integral_mono_ae integrable_condExp.integrableOn (integrable_const _)
          (ae_restrict_of_ae (H.simple_factor (an n)).2)
      _ = μ.real s := by simp
  exact nonnegative_limit_budget (μ.restrict s) (factor X σ a) (fun n => factor X σ (an n))
    (factor_measurable H.measurable (ha.mono hm le_rfl))
    (fun ω => (factor_pos a ω).le) (fun n ω => (factor_pos (an n) ω).le)
    (fun n => (H.simple_factor (an n)).1.integrableOn) (μ.real s) ENNReal.toReal_nonneg hb hlimf

/-- Unbounded predictable multipliers give an integrable normalized factor. -/
theorem random_factor_integrable (a : Ω → ℝ) (ha : Measurable[m] a) :
    Integrable (factor X σ a) μ := by
  simpa only [IntegrableOn,Measure.restrict_univ] using
    (H.random_factor_setIntegral a ha MeasurableSet.univ).1

/-- The deterministic-parameter hypotheses imply the actual conditional bound
at a random predictable parameter, with no uniform all-parameter event assumed. -/
theorem random_factor_condExp_le (a : Ω → ℝ) (ha : Measurable[m] a) :
    (μ[factor X σ a|m])≤ᵐ[μ] fun _ => 1 := by
  apply ae_le_of_ae_le_trim (hm := hm)
  refine ae_le_of_forall_setIntegral_le
    (Integrable.trim hm integrable_condExp stronglyMeasurable_condExp) (integrable_const 1) ?_
  intro s hs _
  rw [← setIntegral_trim hm stronglyMeasurable_condExp hs,
    ← setIntegral_trim hm stronglyMeasurable_const hs,
    setIntegral_condExp hm (H.random_factor_integrable a ha) hs]
  simpa only [setIntegral_const,smul_eq_mul,mul_one] using (H.random_factor_setIntegral a ha hs).2

/-- First pull out a bounded nonnegative conditioning-measurable weight. -/
theorem bounded_weight_factor (a : Ω → ℝ) (ha : Measurable[m] a)
    (W : Ω → ℝ) (hW : Measurable[m] W) (hWi : Integrable W μ)
    (hW0 : ∀ ω,0≤W ω) (K : ℝ) (hWK : ∀ ω,W ω≤K) :
    Integrable (fun ω => W ω*factor X σ a ω) μ ∧
      (∫ ω,W ω*factor X σ a ω∂μ)≤∫ ω,W ω∂μ := by
  have hF := H.random_factor_integrable a ha
  have hWF : Integrable (fun ω => W ω*factor X σ a ω) μ :=
    hF.bdd_mul (hW.mono hm le_rfl).aestronglyMeasurable
      (ae_of_all _ (fun ω => by simpa only [Real.norm_eq_abs,abs_of_nonneg (hW0 ω)] using hWK ω))
  have hpull := condExp_mul_of_stronglyMeasurable_left hW.stronglyMeasurable hWF hF
  refine ⟨hWF,?_⟩
  calc (∫ ω,W ω*factor X σ a ω∂μ)=∫ ω,(μ[fun ω => W ω*factor X σ a ω|m]) ω∂μ :=
      (integral_condExp hm).symm
    _ ≤ ∫ ω,W ω∂μ := by
      apply integral_mono_ae integrable_condExp hWi
      filter_upwards [hpull,H.random_factor_condExp_le a ha] with ω hp hb
      change (μ[W*factor X σ a|m]) ω≤W ω
      rw [hp]
      exact mul_le_of_le_one_right (hW0 ω) hb

/-- Nonnegative Fatou localization removes the bounded-weight condition.
Weighted integrability is derived, rather than assumed. -/
theorem weighted_factor (a : Ω → ℝ) (ha : Measurable[m] a)
    (W : Ω → ℝ) (hW : Measurable[m] W) (hWi : Integrable W μ) (hW0 : ∀ ω,0≤W ω) :
    Integrable (fun ω => W ω*factor X σ a ω) μ ∧
      (∫ ω,W ω*factor X σ a ω∂μ)≤∫ ω,W ω∂μ := by
  let Wn (n : ℕ) (ω : Ω) : ℝ := min (W ω) (n:ℝ)
  have hWnm (n : ℕ) : Measurable[m] (Wn n) := hW.min measurable_const
  have hWn0 (n : ℕ) (ω : Ω) : 0≤Wn n ω := le_min (hW0 ω) (Nat.cast_nonneg n)
  have hWnK (n : ℕ) (ω : Ω) : Wn n ω≤(n:ℝ) := min_le_right _ _
  have hWni (n : ℕ) : Integrable (Wn n) μ := by
    apply Integrable.of_bound (hWnm n |>.mono hm le_rfl).aestronglyMeasurable (n:ℝ)
    exact ae_of_all _ (fun ω => by
      simpa only [Real.norm_eq_abs,abs_of_nonneg (hWn0 n ω)] using hWnK n ω)
  have hproduct (n : ℕ) := H.bounded_weight_factor a ha (Wn n) (hWnm n) (hWni n) (hWn0 n) n (hWnK n)
  have hb (n : ℕ) : (∫ ω,Wn n ω*factor X σ a ω∂μ)≤∫ ω,W ω∂μ :=
    (hproduct n).2.trans (integral_mono (hWni n) hWi (fun ω => min_le_left _ _))
  have hlim (ω : Ω) : Tendsto (fun n => Wn n ω) atTop (𝓝 (W ω)) := by
    obtain ⟨N,hN⟩ := exists_nat_ge (W ω)
    have he : (fun n => Wn n ω)=ᶠ[atTop] fun _ => W ω := by
      filter_upwards [eventually_ge_atTop N] with n hn
      exact min_eq_left (hN.trans (by exact_mod_cast hn))
    exact tendsto_const_nhds.congr' he.symm
  exact nonnegative_limit_budget μ (fun ω => W ω*factor X σ a ω)
    (fun n ω => Wn n ω*factor X σ a ω)
    ((hW.mono hm le_rfl).mul (factor_measurable H.measurable (ha.mono hm le_rfl)))
    (fun ω => mul_nonneg (hW0 ω) (factor_pos a ω).le)
    (fun n ω => mul_nonneg (hWn0 n ω) (factor_pos a ω).le)
    (fun n => (hproduct n).1) (∫ ω,W ω∂μ) (integral_nonneg hW0) hb
    (fun ω => (hlim ω).mul_const (factor X σ a ω))

theorem weighted_factor_integrable (a : Ω → ℝ) (ha : Measurable[m] a)
    (W : Ω → ℝ) (hW : Measurable[m] W) (hWi : Integrable W μ) (hW0 : ∀ ω,0≤W ω) :
    Integrable (fun ω => W ω*factor X σ a ω) μ := (H.weighted_factor a ha W hW hWi hW0).1

theorem integral_weighted_factor_le (a : Ω → ℝ) (ha : Measurable[m] a)
    (W : Ω → ℝ) (hW : Measurable[m] W) (hWi : Integrable W μ) (hW0 : ∀ ω,0≤W ω) :
    (∫ ω,W ω*factor X σ a ω∂μ)≤∫ ω,W ω∂μ := (H.weighted_factor a ha W hW hWi hW0).2

/-- The same weighted inequality holds on every conditioning-measurable event. -/
theorem setIntegral_weighted_factor_le (a : Ω → ℝ) (ha : Measurable[m] a)
    (W : Ω → ℝ) (hW : Measurable[m] W) (hWi : Integrable W μ) (hW0 : ∀ ω,0≤W ω)
    {s : Set Ω} (hs : MeasurableSet[m] s) :
    (∫ ω in s,W ω*factor X σ a ω∂μ)≤∫ ω in s,W ω∂μ := by
  have h0 (ω : Ω) : 0≤s.indicator W ω := by
    by_cases hω : ω∈s <;> simp [hω,hW0]
  have hbound := H.integral_weighted_factor_le a ha (s.indicator W)
    (hW.indicator hs) (hWi.indicator (hm _ hs)) h0
  have he : (fun ω => s.indicator W ω*factor X σ a ω)=
      s.indicator (fun ω => W ω*factor X σ a ω) := by
    funext ω
    by_cases hω : ω∈s <;> simp [hω]
  rw [he,integral_indicator (hm _ hs),integral_indicator (hm _ hs)] at hbound
  exact hbound

end ConditionalSubgaussian
end Komorebi.LSM.RegressionConfidence
