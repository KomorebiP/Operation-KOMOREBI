import KomorebiLSM.ConditionalHoeffding
import KomorebiLSM.PredictableResidualAffine
import KomorebiLSM.ConditionalRandomMultiplier

/-! Conditional regression noise scales are derived from actual bounded
responses and their actual conditional means on arbitrary probability spaces. -/
set_option autoImplicit false
namespace Komorebi.LSM.BoundedResponseNoise
open MeasureTheory ProbabilityTheory
open Komorebi.LSM.RegressionConfidence

variable {Ω : Type*} [mΩ : MeasurableSpace Ω]
variable {μ : Measure Ω} [IsProbabilityMeasure μ]

omit [IsProbabilityMeasure μ] in
/-- An actual a.e. identity transports the conditional exponential structure;
ambient measurability of the chosen version is retained explicitly. -/
theorem conditionalSubgaussian_congr {m : MeasurableSpace Ω} {hm : m≤mΩ}
    {X Z : Ω → ℝ} {σ : ℝ} (H : ConditionalSubgaussian (mΩ := mΩ) hm X σ μ)
    (hZ : @Measurable Ω ℝ mΩ _ Z) (hXZ : X=ᵐ[μ] Z) :
    ConditionalSubgaussian (mΩ := mΩ) hm Z σ μ := by
  let : MeasurableSpace Ω := mΩ
  have he (h : ℝ) : (fun ω => Real.exp (h*X ω))=ᵐ[μ] (fun ω => Real.exp (h*Z ω)) := by
    filter_upwards [hXZ] with ω hω
    rw [hω]
  refine ⟨hZ,fun h => (H.integrable_exp h).congr (he h),?_⟩
  intro h
  filter_upwards [H.condExp_le h,condExp_congr_ae (he h)] with ω hb hc
  exact hc.symm.trans_le hb

/-- Actual affine normalization and the sharp conditional unit Hoeffding
bound give the interval-width noise scale (b-a)/2. -/
theorem centered_interval {m : MeasurableSpace Ω} (hm : m≤mΩ)
    (Y : Ω → ℝ) (hY : @Measurable Ω ℝ mΩ _ Y)
    (a b : ℝ) (hab : a<b) (hb : ∀ᵐ ω∂μ,Y ω∈Set.Icc a b) :
    ConditionalSubgaussian (mΩ := mΩ) hm (fun ω => Y ω-(μ[Y|m]) ω) ((b-a)/2) μ := by
  let : MeasurableSpace Ω := mΩ
  let c := b-a
  have hc : 0<c := sub_pos.mpr hab
  let U : Ω → ℝ := fun ω => (Y ω-a)/c
  have hU : @Measurable Ω ℝ mΩ _ U := (hY.sub_const a).div_const c
  have hunit : ∀ᵐ ω∂μ,U ω∈Set.Icc (0:ℝ) 1 := by
    filter_upwards [hb] with ω hω
    refine ⟨div_nonneg (sub_nonneg.mpr hω.1) hc.le,?_⟩
    apply (div_le_iff₀ hc).2
    dsimp [c]
    linarith [hω.2]
  have hi : Integrable U μ := Integrable.of_mem_Icc (0:ℝ) 1 hU.aemeasurable hunit
  have hrep (ω : Ω) : a+c*U ω=Y ω := by
    dsimp [U]
    field_simp [ne_of_gt hc]
    ring
  have hce := PredictableResidualAffine.condExp_affine_ae hm U hi a c
  rw [show (fun ω => a+c*U ω)=Y from funext hrep] at hce
  have hcenter : (fun ω => Y ω-(μ[Y|m]) ω)=ᵐ[μ]
      (fun ω => c*(U ω-(μ[U|m]) ω)) := by
    filter_upwards [hce] with ω hω
    rw [hω,← hrep ω]
    ring
  have hexp (h : ℝ) : (fun ω => Real.exp (h*(Y ω-(μ[Y|m]) ω)))=ᵐ[μ]
      (fun ω => Real.exp ((h*c)*(U ω-(μ[U|m]) ω))) := by
    filter_upwards [hcenter] with ω hω
    rw [hω]
    congr 1
    ring
  refine ⟨hY.sub (stronglyMeasurable_condExp.measurable.mono hm le_rfl),?_,?_⟩
  · intro h
    exact (ConditionalHoeffding.centered_exp_integrable hm U hU hunit (h*c)).congr (hexp h).symm
  · intro h
    have hbound := ConditionalHoeffding.centered_condExp_le hm U hU hunit (h*c)
    have he := condExp_congr_ae (m := m) (hexp h)
    have hscale : (h*c)^2/8=h^2*((b-a)/2)^2/2 := by dsimp [c]; ring
    filter_upwards [hbound,he] with ω hω heω
    rw [heω]
    simpa only [hscale] using hω

/-- A declared regression mean is used only after its actual conditional
expectation identity has been proved. No noise certificate is an input. -/
theorem regression_interval {m : MeasurableSpace Ω} (hm : m≤mΩ)
    (Y : Ω → ℝ) (hY : @Measurable Ω ℝ mΩ _ Y)
    (a b : ℝ) (hab : a<b) (hb : ∀ᵐ ω∂μ,Y ω∈Set.Icc a b)
    (θ : ℝ) (φ : Ω → ℝ) (hφ : @Measurable Ω ℝ m _ φ)
    (hmean : (μ[Y|m])=ᵐ[μ] (fun ω => θ*φ ω)) :
    ConditionalSubgaussian (mΩ := mΩ) hm (fun ω => Y ω-θ*φ ω) ((b-a)/2) μ := by
  let : MeasurableSpace Ω := mΩ
  apply conditionalSubgaussian_congr (centered_interval hm Y hY a b hab hb)
    (hY.sub ((hφ.mono hm le_rfl).const_mul θ))
  filter_upwards [hmean] with ω hω
  change Y ω-(μ[Y|m]) ω=Y ω-θ*φ ω
  rw [hω]

/-- A response in [-1,1] has the derived conditional noise scale one. -/
theorem regression_neg_one_one {m : MeasurableSpace Ω} (hm : m≤mΩ)
    (Y : Ω → ℝ) (hY : @Measurable Ω ℝ mΩ _ Y)
    (hb : ∀ᵐ ω∂μ,Y ω∈Set.Icc (-1:ℝ) 1)
    (θ : ℝ) (φ : Ω → ℝ) (hφ : @Measurable Ω ℝ m _ φ)
    (hmean : (μ[Y|m])=ᵐ[μ] (fun ω => θ*φ ω)) :
    ConditionalSubgaussian (mΩ := mΩ) hm (fun ω => Y ω-θ*φ ω) 1 μ := by
  let : MeasurableSpace Ω := mΩ
  convert regression_interval hm Y hY (-1) 1 (by norm_num) hb θ φ hφ hmean using 1; norm_num

/-- A response in [-1/2,1] has the derived conditional noise scale three quarters. -/
theorem regression_neg_half_one {m : MeasurableSpace Ω} (hm : m≤mΩ)
    (Y : Ω → ℝ) (hY : @Measurable Ω ℝ mΩ _ Y)
    (hb : ∀ᵐ ω∂μ,Y ω∈Set.Icc (-(1/2):ℝ) 1)
    (θ : ℝ) (φ : Ω → ℝ) (hφ : @Measurable Ω ℝ m _ φ)
    (hmean : (μ[Y|m])=ᵐ[μ] (fun ω => θ*φ ω)) :
    ConditionalSubgaussian (mΩ := mΩ) hm (fun ω => Y ω-θ*φ ω) (3/4) μ := by
  let : MeasurableSpace Ω := mΩ
  convert regression_interval hm Y hY (-(1/2)) 1 (by norm_num) hb θ φ hφ hmean using 1; norm_num

/-- Predictable scalar regressors and next-level recorded [-1,1] responses
supply P81's actual noise input with sigma=1 at every time. -/
theorem process_neg_one_one (ℱ : Filtration ℕ mΩ) (θ : ℝ)
    (φ Y : ℕ → Ω → ℝ) (hφ : ∀ n,Measurable[ℱ n] (φ n))
    (hY : ∀ n,Measurable[ℱ (n+1)] (Y n))
    (hb : ∀ n,∀ᵐ ω∂μ,Y n ω∈Set.Icc (-1:ℝ) 1)
    (hmean : ∀ n,(μ[Y n|ℱ n])=ᵐ[μ] (fun ω => θ*φ n ω)) :
    ∀ n,ConditionalSubgaussian (mΩ := mΩ) (ℱ.le n) (fun ω => Y n ω-θ*φ n ω) 1 μ :=
  fun n => regression_neg_one_one (ℱ.le n) (Y n) ((hY n).mono (ℱ.le (n+1)) le_rfl)
    (hb n) θ (φ n) (hφ n) (hmean n)

/-- The [-1/2,1] predictable regression analog supplies sigma=3/4. -/
theorem process_neg_half_one (ℱ : Filtration ℕ mΩ) (θ : ℝ)
    (φ Y : ℕ → Ω → ℝ) (hφ : ∀ n,Measurable[ℱ n] (φ n))
    (hY : ∀ n,Measurable[ℱ (n+1)] (Y n))
    (hb : ∀ n,∀ᵐ ω∂μ,Y n ω∈Set.Icc (-(1/2):ℝ) 1)
    (hmean : ∀ n,(μ[Y n|ℱ n])=ᵐ[μ] (fun ω => θ*φ n ω)) :
    ∀ n,ConditionalSubgaussian (mΩ := mΩ) (ℱ.le n) (fun ω => Y n ω-θ*φ n ω) (3/4) μ :=
  fun n => regression_neg_half_one (ℱ.le n) (Y n) ((hY n).mono (ℱ.le (n+1)) le_rfl)
    (hb n) θ (φ n) (hφ n) (hmean n)

end Komorebi.LSM.BoundedResponseNoise
