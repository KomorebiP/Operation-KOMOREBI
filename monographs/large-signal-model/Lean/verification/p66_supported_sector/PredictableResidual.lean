import KomorebiLSM.SequentialConfidence
import Mathlib.Probability.Moments.SubGaussian
import Mathlib.Topology.Algebra.InfiniteSum.ENNReal

/-! Predictable residual concentration from actual conditional expectations. -/
set_option autoImplicit false
namespace Komorebi.LSM.PredictableResidual
open MeasureTheory ProbabilityTheory Real
open scoped BigOperators NNReal ENNReal
variable {Ω : Type*} [mΩ : MeasurableSpace Ω] [StandardBorelSpace Ω]
variable {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- A function measurable before an observation is conditionally constant. -/
theorem predictable_kernel_constant {m : MeasurableSpace Ω} (hm : m≤mΩ)
    (g : Ω → ℝ) (hg : Measurable[m] g) :
    ∀ᵐ ω' ∂μ.trim hm, ∀ᵐ ω ∂condExpKernel (mΩ:=mΩ) μ m ω', g ω=g ω' := by
  let : MeasurableSpace Ω := mΩ
  apply @Measure.ae_ae_of_ae_compProd Ω Ω m mΩ (μ.trim hm)
    (condExpKernel (mΩ:=mΩ) μ m) _ _ (fun q : Ω×Ω ↦ g q.2=g q.1)
  rw [compProd_trim_condExpKernel hm]
  have hdiag : @Measurable Ω (Ω×Ω) mΩ (m.prod mΩ) Function.diag :=
    (measurable_id'' hm).prodMk measurable_id
  apply (@ae_map_iff Ω (Ω×Ω) mΩ (m.prod mΩ) μ Function.diag
    (@Measurable.aemeasurable Ω (Ω×Ω) mΩ (m.prod mΩ) Function.diag μ hdiag)
    (fun q : Ω×Ω ↦ g q.2=g q.1) ?_).mpr
  · exact ae_of_all _ (fun _ ↦ rfl)
  · exact measurableSet_eq_fun (hg.mono hm le_rfl |>.comp measurable_snd)
      (hg.comp measurable_fst)

omit [StandardBorelSpace Ω] in
/-- The true conditional mean of a bounded test remains in its probability range. -/
theorem conditional_mean_mem_Icc {m : MeasurableSpace Ω} (hm : m≤mΩ)
    (X : Ω → ℝ) (hX : @Measurable Ω ℝ mΩ _ X)
    (hb : ∀ᵐ ω ∂μ, X ω ∈ Set.Icc (0:ℝ) 1) :
    ∀ᵐ ω ∂μ, (μ[X | m]) ω ∈ Set.Icc (0:ℝ) 1 := by
  let : MeasurableSpace Ω := mΩ
  have hi := Integrable.of_mem_Icc (0:ℝ) 1 hX.aemeasurable hb
  have hlo := condExp_nonneg (m:=m) (hb.mono fun _ h ↦ h.1)
  have hhi := condExp_mono (m:=m) hi (integrable_const (1:ℝ)) (hb.mono fun _ h ↦ h.2)
  rw [condExp_const hm] at hhi
  filter_upwards [hlo,hhi] with ω hlo hhi using ⟨hlo,hhi⟩

/-- Conditional Hoeffding's lemma derived for the actual conditional mean.
This formal kernel route assumes a standard Borel sample space. -/
theorem conditional_centered_subgaussian {m : MeasurableSpace Ω} (hm : m≤mΩ)
    (X : Ω → ℝ) (hX : @Measurable Ω ℝ mΩ _ X)
    (hb : ∀ᵐ ω ∂μ, X ω ∈ Set.Icc (0:ℝ) 1) :
    HasCondSubgaussianMGF m hm (fun ω ↦ X ω-(μ[X | m]) ω) (1/4:NNReal) μ := by
  let : MeasurableSpace Ω := mΩ
  have hi := Integrable.of_mem_Icc (0:ℝ) 1 hX.aemeasurable hb
  have hmean := conditional_mean_mem_Icc hm X hX hb
  have hres : ∀ᵐ ω ∂μ, X ω-(μ[X | m]) ω ∈ Set.Icc (-1:ℝ) 1 := by
    filter_upwards [hb,hmean] with ω h h' using ⟨by linarith [h.1,h'.2], by linarith [h.2,h'.1]⟩
  have hresmeas : Measurable (fun ω ↦ X ω-(μ[X | m]) ω) :=
    hX.sub (stronglyMeasurable_condExp.measurable.mono hm le_rfl)
  refine ⟨?_,?_⟩
  · intro t
    rw [condExpKernel_comp_trim hm]
    exact integrable_exp_mul_of_mem_Icc hresmeas.aemeasurable hres
  · have hbound : ∀ᵐ ω' ∂μ.trim hm, ∀ᵐ ω ∂condExpKernel (mΩ:=mΩ) μ m ω', X ω∈Set.Icc (0:ℝ) 1 := by
      apply Measure.ae_ae_of_ae_comp
      rwa [condExpKernel_comp_trim hm]
    have hconstant := predictable_kernel_constant (μ:=μ) hm (μ[X | m]) stronglyMeasurable_condExp.measurable
    have hintegral := condExp_ae_eq_trim_integral_condExpKernel hm hi
    filter_upwards [hbound,hconstant,hintegral] with ω' hbound hconstant hintegral
    have hs := hasSubgaussianMGF_of_mem_Icc hX.aemeasurable hbound
    rw [← hintegral] at hs
    have heq : (fun ω ↦ X ω-(μ[X | m]) ω') =ᵐ[condExpKernel (mΩ:=mΩ) μ m ω']
        (fun ω ↦ X ω-(μ[X | m]) ω) := hconstant.mono fun ω h ↦ by dsimp; rw [h]
    have hs' : HasSubgaussianMGF (fun ω ↦ X ω-(μ[X | m]) ω) (1/4:NNReal)
        (condExpKernel (mΩ:=mΩ) μ m ω') := by
      convert hs.congr heq using 1
      norm_num
    exact hs'.mgf_le

/-- Actual accumulated centered test error for times 1 through n. -/
noncomputable def centeredSum (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) : ℝ :=
  ∑ i ∈ Finset.range n, (X i ω-(μ[X i | ℱ i]) ω)

/-- Conditional Hoeffding iterates along the actual filtration, without independence. -/
theorem predictable_sum_subgaussian (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i, Measurable[ℱ (i+1)] (X i))
    (hb : ∀ i, ∀ᵐ ω ∂μ, X i ω∈Set.Icc (0:ℝ) 1) (n : ℕ) :
    HasSubgaussianMGF (centeredSum (μ:=μ) ℱ X n) ((n:NNReal)/4) μ := by
  induction n with
  | zero =>
    simp only [Nat.cast_zero,zero_div]
    exact HasSubgaussianMGF.fun_zero
  | succ n ih =>
    have hsmeas : Measurable[ℱ n] (centeredSum (μ:=μ) ℱ X n) := by
      apply Finset.measurable_fun_sum
      intro i hi
      have hin : i+1≤n := by simpa using Finset.mem_range.mp hi
      exact ((hX i).mono (ℱ.mono hin) le_rfl).sub
        (stronglyMeasurable_condExp.measurable.mono (ℱ.mono (by omega)) le_rfl)
    have hc := conditional_centered_subgaussian (ℱ.le n) (X n)
      ((hX n).mono (ℱ.le (n+1)) le_rfl) (hb n)
    have ha := HasSubgaussianMGF.add_of_hasCondSubgaussianMGF (ℱ.le n)
      (ih.trim (ℱ.le n) hsmeas) hc
    convert ha using 1
    · funext ω
      simp only [centeredSum, Finset.sum_range_succ, Pi.add_apply]
    · push_cast
      ring

/-- The fixed-time two-sided martingale error, derived from bounded tests. -/
theorem predictable_sum_tail (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i, Measurable[ℱ (i+1)] (X i))
    (hb : ∀ i, ∀ᵐ ω ∂μ, X i ω∈Set.Icc (0:ℝ) 1)
    {n : ℕ} (hn : 0<n) (b : ℝ) (hbn : 0≤b) :
    μ.real {ω | b ≤ |centeredSum (μ:=μ) ℱ X n ω|} ≤ 2*exp (-2*b^2/n) := by
  have hs := predictable_sum_subgaussian ℱ X hX hb n
  have hu := hs.measure_ge_le hbn
  have hl := hs.neg.measure_ge_le hbn
  have hexp : exp (-b^2/(2*((n:NNReal)/4:NNReal)))=exp (-2*b^2/n) := by
    congr 1
    push_cast
    field_simp
    ring
  rw [hexp] at hu hl
  have hevent : {ω | b≤|centeredSum (μ:=μ) ℱ X n ω|} =
      {ω | b≤centeredSum (μ:=μ) ℱ X n ω} ∪
      {ω | b≤ -centeredSum (μ:=μ) ℱ X n ω} := by
    ext ω
    simp only [Set.mem_ofPred_eq,Set.mem_union,le_abs]
  rw [hevent]
  exact (measureReal_union_le _ _).trans (by simpa only [Pi.neg_apply,two_mul] using add_le_add hu hl)

/-- The elementary time-union boundary at a positive time. -/
noncomputable def boundary (n : ℕ) (α : ℝ) : ℝ :=
  sqrt ((n:ℝ)/2*log (2*n*(n+1)/α))

omit [MeasurableSpace Ω] [StandardBorelSpace Ω] in
/-- The declared boundary spends α/[n(n+1)] at time n. -/
theorem boundary_budget {n : ℕ} (hn : 0<n) {α : ℝ} (hα : 0<α) (hα1 : α≤1) :
    2*exp (-2*(boundary n α)^2/n)=α/(n*(n+1)) := by
  have hn0 : (0:ℝ)<n := by exact_mod_cast hn
  have hn1 : (1:ℝ)≤n := by exact_mod_cast hn
  have hr : 0<2*(n:ℝ)*(n+1)/α := by positivity
  have hr1 : 1≤2*(n:ℝ)*(n+1)/α := (le_div_iff₀ hα).mpr (by nlinarith)
  have hlog : 0≤log (2*(n:ℝ)*(n+1)/α) := log_nonneg hr1
  rw [boundary,sq_sqrt (mul_nonneg (by positivity) hlog)]
  have he : -2*((n:ℝ)/2*log (2*n*(n+1)/α))/n = -log (2*n*(n+1)/α) := by
    field_simp
  rw [he,exp_neg,exp_log hr]
  field_simp

omit [MeasurableSpace Ω] [StandardBorelSpace Ω] in
/-- Finite telescoping proves the complete time budget. -/
theorem time_partial_budget (N : ℕ) :
    (∑ n ∈ Finset.range N, (1:ℝ)/(((n:ℝ)+1)*(n+2)))=1-1/((N:ℝ)+1) := by
  induction N with
  | zero => norm_num
  | succ N ih =>
    rw [Finset.sum_range_succ,ih]
    push_cast
    field_simp
    ring

noncomputable def timeWeight (n : ℕ) : NNReal := 1/(((n:NNReal)+1)*(n+2))

omit [MeasurableSpace Ω] [StandardBorelSpace Ω] in
/-- The countable time-union weights have total at most one. -/
theorem time_partial_le (N : ℕ) : ∑ n ∈ Finset.range N, timeWeight n ≤ 1 := by
  have h : (∑ n ∈ Finset.range N, (1:ℝ)/(((n:ℝ)+1)*(n+2)))≤1 := by
    rw [time_partial_budget]
    exact sub_le_self _ (by positivity)
  apply NNReal.coe_le_coe.mp
  simpa [timeWeight] using h

omit [MeasurableSpace Ω] [StandardBorelSpace Ω] in
theorem time_summable : Summable timeWeight :=
  NNReal.summable_of_sum_range_le time_partial_le

omit [MeasurableSpace Ω] [StandardBorelSpace Ω] in
theorem time_budget : ∑' n, timeWeight n ≤ 1 :=
  NNReal.tsum_le_of_sum_range_le time_partial_le

omit [StandardBorelSpace Ω] [IsProbabilityMeasure μ] in
/-- Each finite accumulated conditional residual is measurable. -/
theorem centeredSum_measurable (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i, Measurable[ℱ (i+1)] (X i)) (n : ℕ) :
    Measurable (centeredSum (μ:=μ) ℱ X n) := by
  apply Finset.measurable_fun_sum
  intro i _
  exact ((hX i).mono (ℱ.le (i+1)) le_rfl).sub
    (stronglyMeasurable_condExp.measurable.mono (ℱ.le i) le_rfl)

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
  have hprob := SequentialConfidence.simultaneous_coverage F hF
    (fun n ↦ α*timeWeight n) hweights α hbudget hf
  convert hprob using 1
  congr 1
  ext ω
  simp [F]

/-- All prospectively registered countably many rules share one all-time event. -/
theorem time_uniform_rules (ℱ : Filtration ℕ mΩ) (X : ℕ → ℕ → Ω → ℝ)
    (hX : ∀ j i, Measurable[ℱ (i+1)] (X j i))
    (hb : ∀ j i, ∀ᵐ ω ∂μ, X j i ω∈Set.Icc (0:ℝ) 1)
    (α : ℕ → NNReal) (hα : ∀ j, 0<α j) (hs : Summable α)
    (δ : NNReal) (hbudget : ∑' j, α j ≤ δ) (hδ1 : δ≤1) :
    1-(δ:ℝ) ≤ μ.real {ω | ∀ j n,
      |centeredSum (μ:=μ) ℱ (X j) (n+1) ω|≤boundary (n+1) (α j)} := by
  let F : ℕ → Set Ω := fun j ↦ {ω | ∃ n,
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
  have hprob := SequentialConfidence.simultaneous_coverage F hF α hs δ hbudget hf
  convert hprob using 1
  congr 1
  ext ω
  simp [F]

/-- Accumulated observed residual against a possibly changing model prediction. -/
noncomputable def observedResidual (X p : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) : ℝ :=
  ∑ i ∈ Finset.range n, (X i ω-p i ω)

/-- Accumulated true conditional predictive drift. -/
noncomputable def conditionalDrift (ℱ : Filtration ℕ mΩ) (X p : ℕ → Ω → ℝ)
    (n : ℕ) (ω : Ω) : ℝ := ∑ i ∈ Finset.range n, ((μ[X i | ℱ i]) ω-p i ω)

omit [StandardBorelSpace Ω] [IsProbabilityMeasure μ] in
/-- Model predictions cancel exactly, so no independence of prediction errors is used. -/
theorem residual_sub_drift (ℱ : Filtration ℕ mΩ) (X p : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) :
    observedResidual X p n ω-conditionalDrift (μ:=μ) ℱ X p n ω =
      centeredSum (μ:=μ) ℱ X n ω := by
  simp only [observedResidual,conditionalDrift,centeredSum,← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro i _
  ring

/-- P66's residual/drift conclusion in the bounded, standard Borel sector. -/
theorem predictable_residual_certificate (ℱ : Filtration ℕ mΩ)
    (X p : ℕ → ℕ → Ω → ℝ)
    (hX : ∀ j i, Measurable[ℱ (i+1)] (X j i))
    (hb : ∀ j i, ∀ᵐ ω ∂μ, X j i ω∈Set.Icc (0:ℝ) 1)
    (α : ℕ → NNReal) (hα : ∀ j, 0<α j) (hs : Summable α)
    (δ : NNReal) (hbudget : ∑' j, α j ≤ δ) (hδ1 : δ≤1) :
    1-(δ:ℝ) ≤ μ.real {ω | ∀ j n,
      |observedResidual (X j) (p j) (n+1) ω-
        conditionalDrift (μ:=μ) ℱ (X j) (p j) (n+1) ω|≤boundary (n+1) (α j)} := by
  simpa only [residual_sub_drift] using time_uniform_rules ℱ X hX hb α hα hs δ hbudget hδ1

omit [MeasurableSpace Ω] [StandardBorelSpace Ω] in
/-- A simultaneous event survives every selected time and rule, and scalar range scaling. -/
theorem scaled_selected_bound (S : ℕ → ℕ → Ω → ℝ) (α : ℕ → NNReal)
    (ω : Ω) (hall : ∀ j n, |S j (n+1) ω|≤boundary (n+1) (α j))
    (c : ℝ) (hc : 0≤c) (time rule : Ω → ℕ) :
    |c*S (rule ω) (time ω+1) ω|≤c*boundary (time ω+1) (α (rule ω)) := by
  rw [abs_mul,abs_of_nonneg hc]
  exact mul_le_mul_of_nonneg_left (hall (rule ω) (time ω)) hc

end Komorebi.LSM.PredictableResidual
