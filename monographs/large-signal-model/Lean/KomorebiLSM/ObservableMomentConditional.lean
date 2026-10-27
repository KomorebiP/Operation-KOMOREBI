import KomorebiLSM.ContinuousInstrument
import KomorebiLSM.BaseNormTopology
import Mathlib.Probability.Kernel.Composition.IntegralCompProd
import Mathlib.MeasureTheory.Function.ConditionalExpectation.Basic
import Mathlib.Tactic

/-! P82: conditional moments from literal observation kernels and accessible
normalized posterior states. No conditional-mean identity is an input field. -/
set_option autoImplicit false
namespace Komorebi.LSM.ObservableMoments
open MeasureTheory ProbabilityTheory
open scoped ENNReal BigOperators

section HistoryConditional
variable {Ω H Y E : Type*} [mΩ : MeasurableSpace Ω] [mH : MeasurableSpace H]
variable [MeasurableSpace Y] [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- Equality of the actual joint history/observation measure identifies the
conditional integral relative to exactly the recorded history sigma algebra. -/
theorem history_condExp (history : Ω → H) (observation : Ω → Y)
    (hh : Measurable history) (hy : Measurable observation)
    (κ : Kernel H Y) [IsMarkovKernel κ]
    (hlaw : μ.map (fun ω => (history ω,observation ω))=(μ.map history) ⊗ₘ κ)
    (F : H × Y → E) (hF : Measurable F)
    (hFi : Integrable (fun ω => F (history ω,observation ω)) μ) :
    μ[fun ω => F (history ω,observation ω) | mH.comap history] =ᵐ[μ]
      (fun ω => ∫ y,F (history ω,y)∂κ (history ω)) := by
  have hj := hh.prodMk hy
  have hiMap : Integrable F (μ.map (fun ω => (history ω,observation ω))) :=
    (integrable_map_measure hF.stronglyMeasurable.aestronglyMeasurable hj.aemeasurable).mpr hFi
  have hi : Integrable F ((μ.map history) ⊗ₘ κ) := by rwa [hlaw] at hiMap
  have hparts := (Measure.integrable_compProd_iff hi.aestronglyMeasurable).mp hi
  have hg : Measurable (fun h => ∫ y,F (h,y)∂κ h) :=
    hF.stronglyMeasurable.integral_kernel_prod_right'.measurable
  have hgi : Integrable (fun h => ∫ y,F (h,y)∂κ h) (μ.map history) := by
    apply hparts.2.mono' hg.aestronglyMeasurable
    exact Filter.Eventually.of_forall (fun h => norm_integral_le_integral_norm _)
  have hgc : @Measurable Ω E (mH.comap history) _
      (fun ω => ∫ y,F (history ω,y)∂κ (history ω)) := hg.comp (comap_measurable history)
  apply (ae_eq_condExp_of_forall_setIntegral_eq hh.comap_le hFi
    (fun _ _ _ => (hgi.comp_measurable hh).integrableOn) ?_
    hgc.stronglyMeasurable.aestronglyMeasurable).symm
  intro s hs _
  obtain ⟨S,hS,rfl⟩ := MeasurableSpace.measurableSet_comap.mp hs
  calc
    (∫ ω in history ⁻¹' S,(∫ y,F (history ω,y)∂κ (history ω))∂μ)=
      ∫ h in S,(∫ y,F (h,y)∂κ h)∂μ.map history :=
        (setIntegral_map hS hg.aestronglyMeasurable hh.aemeasurable).symm
    _ = ∫ p in S ×ˢ Set.univ,F p∂(μ.map history) ⊗ₘ κ := by
      rw [Measure.setIntegral_compProd hS MeasurableSet.univ hi.integrableOn]
      simp only [Measure.restrict_univ]
    _ = ∫ ω in history ⁻¹' S,F (history ω,observation ω)∂μ := by
      rw [← hlaw,setIntegral_map (hS.prod MeasurableSet.univ)
        hF.stronglyMeasurable.aestronglyMeasurable hj.aemeasurable]
      have hp : (fun ω => (history ω,observation ω)) ⁻¹' (S ×ˢ Set.univ)=history ⁻¹' S := by
        ext ω
        simp
      rw [hp]

end HistoryConditional

section Instrument
variable {E A Y : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [MeasurableSpace Y] {C : BaseNorm.ProbabilityCone E} {ν : Measure Y}
variable [IsProbabilityMeasure ν]
variable (D : ContinuousInstrument.DensityInstrument (A := A) C ν)
open ContinuousInstrument.DensityInstrument

/-- The literal weighted integral of the submitted operator density. -/
noncomputable def momentOperator (g : Y → ℝ) (a : A) : E →L[ℝ] E :=
  ∫ y,g y • D.op a y∂ν

/-- The observation density cancels the actual normalized posterior,
including zero-density branches through their zero measure contribution. -/
theorem kernel_weighted_posterior (fallback : State C) (a : A) (z : State C)
    (g : Y → ℝ)
    (hgi : Integrable (fun y => g y • D.op a y) ν) :
    (∫ y,g y • (D.update fallback a z y).1∂D.kernel a z)=momentOperator D g a z.1 := by
  have hd : Measurable (fun y => ENNReal.ofReal (D.density a y z.1)) :=
    (((D.density_measurable a).comp (measurable_const.prodMk measurable_id)).ennreal_ofReal)
  rw [D.kernel_apply,integral_withDensity_eq_integral_toReal_smul hd
    (Filter.Eventually.of_forall (fun _ => ENNReal.ofReal_lt_top))]
  rw [momentOperator,ContinuousLinearMap.integral_apply hgi]
  apply integral_congr_ae
  filter_upwards [D.density_smul_update_ae fallback a z,D.density_nonneg_ae a z.2.1] with y he hn
  rw [ENNReal.toReal_ofReal hn,smul_smul,mul_comm,← smul_smul,he]
  rfl

variable [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]

/-- The literal instrument kernel with its observed chosen action included. -/
noncomputable def controlledKernel : Kernel (A × State C) Y where
  toFun p := D.kernel p.1 p.2
  measurable' := measurable_from_prod_countable_right (fun a => (D.kernel a).measurable)

instance controlledKernel_markov : IsMarkovKernel (controlledKernel D) := by
  constructor
  intro p
  change IsProbabilityMeasure (D.kernel p.1 p.2)
  infer_instance

omit [IsProbabilityMeasure ν] in
theorem controlled_update_measurable (fallback : State C) :
    Measurable (fun p : A × (State C × Y) => (D.update fallback p.1 p.2.1 p.2.2).1) := by
  apply measurable_from_prod_countable_right
  intro a
  exact measurable_subtype_coe.comp (D.update_measurable fallback a)

variable {H : Type*} [MeasurableSpace H]

/-- Every state in this experiment is a specified measurable function of the
recorded context. The next state is also accessible from that context and the
new observation. Its positive-density branch formula is a separate assumption. -/
structure AccessibleState where
  action : H → A
  state : H → State C
  next : H × Y → State C
  action_measurable : Measurable action
  state_measurable : Measurable state
  next_measurable : Measurable next
  posterior : ∀ h,∀ᵐ y∂ν,0<D.density (action h) y (state h).1 →
    (next (h,y)).1=(D.density (action h) y (state h).1)⁻¹ • D.op (action h) y (state h).1

variable (X : AccessibleState (H := H) D)

/-- The actual chosen-action observation kernel along the accessible state. -/
noncomputable def historyKernel : Kernel H Y :=
  (controlledKernel D).comap (fun h => (X.action h,X.state h))
    (X.action_measurable.prodMk X.state_measurable)

instance historyKernel_markov : IsMarkovKernel (historyKernel D X) := by
  unfold historyKernel
  infer_instance

omit [FiniteDimensional ℝ E] [BorelSpace E] [IsProbabilityMeasure ν] [Fintype A]
  [MeasurableSingletonClass A] in
/-- The normalized posterior cancels on positive branches. At zero mass the
true positive branch is zero, so the identity extends almost everywhere. -/
theorem density_smul_accessible (h : H) :
    ∀ᵐ y∂ν,D.density (X.action h) y (X.state h).1 • (X.next (h,y)).1=
      D.op (X.action h) y (X.state h).1 := by
  filter_upwards [X.posterior h,D.positive (X.action h)] with y hp hy
  have hcone := hy _ (X.state h).2.1
  have hn : 0≤D.density (X.action h) y (X.state h).1 := C.mass_nonneg hcone
  by_cases hpos : 0<D.density (X.action h) y (X.state h).1
  · rw [hp hpos,smul_smul,mul_inv_cancel₀ hpos.ne',one_smul]
  · have hz : D.density (X.action h) y (X.state h).1=0 := le_antisymm (le_of_not_gt hpos) hn
    have ho : D.op (X.action h) y (X.state h).1=0 := (C.mass_zero_iff hcone).mp hz
    rw [hz,zero_smul,ho]

/-- Literal integration of the accessible response gives the unnormalized
operator moment; no observation density remains in the denominator. -/
theorem kernel_weighted_accessible (g : Y → ℝ)
    (hgi : ∀ a,Integrable (fun y => g y • D.op a y) ν) (h : H) :
    (∫ y,g y • (X.next (h,y)).1∂historyKernel D X h)=
      momentOperator D g (X.action h) (X.state h).1 := by
  change (∫ y,g y • (X.next (h,y)).1∂D.kernel (X.action h) (X.state h))=_
  have hd : Measurable (fun y => ENNReal.ofReal (D.density (X.action h) y (X.state h).1)) :=
    (((D.density_measurable (X.action h)).comp
      (measurable_const.prodMk measurable_id)).ennreal_ofReal)
  rw [D.kernel_apply,integral_withDensity_eq_integral_toReal_smul hd
    (Filter.Eventually.of_forall (fun _ => ENNReal.ofReal_lt_top)),momentOperator,
    ContinuousLinearMap.integral_apply (hgi (X.action h))]
  apply integral_congr_ae
  filter_upwards [density_smul_accessible D X h,
    D.density_nonneg_ae (X.action h) (X.state h).2.1] with y he hn
  rw [ENNReal.toReal_ofReal hn,smul_smul,mul_comm,← smul_smul,he]
  rfl

/-- Weighted operator integrability supplies the genuine conditional
response integrability after density/posterior cancellation. -/
theorem accessible_response_integrable_kernel (g : Y → ℝ)
    (hgi : ∀ a,Integrable (fun y => g y • D.op a y) ν) (h : H) :
    Integrable (fun y => g y • (X.next (h,y)).1) (historyKernel D X h) := by
  change Integrable _ (D.kernel (X.action h) (X.state h))
  have hd : Measurable (fun y => ENNReal.ofReal (D.density (X.action h) y (X.state h).1)) :=
    (((D.density_measurable (X.action h)).comp
      (measurable_const.prodMk measurable_id)).ennreal_ofReal)
  rw [D.kernel_apply,integrable_withDensity_iff_integrable_smul' hd
    (Filter.Eventually.of_forall (fun _ => ENNReal.ofReal_lt_top))]
  apply ((ContinuousLinearMap.apply ℝ E (X.state h).1).integrable_comp (hgi (X.action h))).congr
  filter_upwards [density_smul_accessible D X h,
    D.density_nonneg_ae (X.action h) (X.state h).2.1] with y he hn
  rw [ENNReal.toReal_ofReal hn,smul_smul,mul_comm,← smul_smul,he]
  rfl

/-- The conditional absolute response integral has a uniform finite bound
from the compact normalized base and the actual weighted operator norms. -/
theorem exists_response_norm_bound (g : Y → ℝ)
    (hgi : ∀ a,Integrable (fun y => g y • D.op a y) ν) :
    ∃ K : ℝ,∀ h,(∫ y,‖g y • (X.next (h,y)).1‖∂historyKernel D X h)≤K := by
  obtain ⟨R,hRpos,hR⟩ := C.exists_cone_bound
  refine ⟨R*∑ a,∫ y,‖g y • D.op a y‖∂ν,?_⟩
  intro h
  have hzR : ‖(X.state h).1‖≤R := by
    simpa only [(X.state h).2.2,mul_one] using hR (X.state h).1 (X.state h).2.1
  have heq : (∫ y,‖g y • (X.next (h,y)).1‖∂historyKernel D X h)=
      ∫ y,‖(g y • D.op (X.action h) y) (X.state h).1‖∂ν := by
    change (∫ y,‖g y • (X.next (h,y)).1‖∂D.kernel (X.action h) (X.state h))=_
    have hd : Measurable (fun y => ENNReal.ofReal (D.density (X.action h) y (X.state h).1)) :=
      (((D.density_measurable (X.action h)).comp
        (measurable_const.prodMk measurable_id)).ennreal_ofReal)
    rw [D.kernel_apply,integral_withDensity_eq_integral_toReal_smul hd
      (Filter.Eventually.of_forall (fun _ => ENNReal.ofReal_lt_top))]
    apply integral_congr_ae
    filter_upwards [density_smul_accessible D X h,
      D.density_nonneg_ae (X.action h) (X.state h).2.1] with y he hn
    rw [ENNReal.toReal_ofReal hn]
    have hv : D.density (X.action h) y (X.state h).1 • (g y • (X.next (h,y)).1)=
        (g y • D.op (X.action h) y) (X.state h).1 := by
      rw [smul_smul,mul_comm,← smul_smul,he]
      rfl
    have hvnorm := congrArg norm hv
    rw [norm_smul,Real.norm_eq_abs,abs_of_nonneg hn] at hvnorm
    exact hvnorm
  rw [heq]
  calc
    _ ≤ ∫ y,R*‖g y • D.op (X.action h) y‖∂ν := by
      apply integral_mono_ae
        (((ContinuousLinearMap.apply ℝ E (X.state h).1).integrable_comp (hgi (X.action h))).norm)
        ((hgi (X.action h)).norm.const_mul R)
      exact Filter.Eventually.of_forall (fun y =>
        ((g y • D.op (X.action h) y).le_opNorm (X.state h).1).trans
          (by nlinarith [norm_nonneg (g y • D.op (X.action h) y)]))
    _ = R*(∫ y,‖g y • D.op (X.action h) y‖∂ν) := integral_const_mul _ _
    _ ≤ _ := by
      have hs : (∫ y,‖g y • D.op (X.action h) y‖∂ν)≤
          ∑ a : A,∫ y,‖g y • D.op a y‖∂ν :=
        Finset.single_le_sum (f := fun a : A => ∫ y,‖g y • D.op a y‖∂ν)
          (fun (a : A) _ => integral_nonneg (fun _ => norm_nonneg _))
          (Finset.mem_univ (X.action h))
      exact mul_le_mul_of_nonneg_left hs hRpos.le

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- The actual observable-history experiment proves the conditional moment
identity. Integrability is the ordinary analytic hypothesis for this vector
conditional expectation, not an assumed conditional-mean certificate. -/
theorem accessible_conditional_moment_of_integrable (history : Ω → H) (observation : Ω → Y)
    (hh : Measurable history) (hy : Measurable observation)
    (hlaw : μ.map (fun ω => (history ω,observation ω))=(μ.map history) ⊗ₘ historyKernel D X)
    (g : Y → ℝ) (hg : Measurable g)
    (hgi : ∀ a,Integrable (fun y => g y • D.op a y) ν)
    (hi : Integrable (fun ω => g (observation ω) • (X.next (history ω,observation ω)).1) μ) :
    μ[fun ω => g (observation ω) • (X.next (history ω,observation ω)).1 |
      (inferInstance : MeasurableSpace H).comap history] =ᵐ[μ]
      (fun ω => momentOperator D g (X.action (history ω)) (X.state (history ω)).1) := by
  have hF : Measurable (fun p : H × Y => g p.2 • (X.next p).1) :=
    (hg.comp measurable_snd).smul (measurable_subtype_coe.comp X.next_measurable)
  have hc := history_condExp history observation hh hy (historyKernel D X) hlaw _ hF hi
  apply hc.trans
  exact Filter.Eventually.of_forall (fun ω => kernel_weighted_accessible D X g hgi (history ω))

/-- Actual response integrability follows from weighted operator
integrability and normalized accessible states, without a bounded-test proxy. -/
theorem accessible_response_integrable (history : Ω → H) (observation : Ω → Y)
    (hh : Measurable history) (hy : Measurable observation)
    (hlaw : μ.map (fun ω => (history ω,observation ω))=(μ.map history) ⊗ₘ historyKernel D X)
    (g : Y → ℝ) (hg : Measurable g)
    (hgi : ∀ a,Integrable (fun y => g y • D.op a y) ν) :
    Integrable (fun ω => g (observation ω) • (X.next (history ω,observation ω)).1) μ := by
  have hF : Measurable (fun p : H × Y => g p.2 • (X.next p).1) :=
    (hg.comp measurable_snd).smul (measurable_subtype_coe.comp X.next_measurable)
  have hn : Measurable (fun h => ∫ y,‖g y • (X.next (h,y)).1‖∂historyKernel D X h) :=
    hF.norm.stronglyMeasurable.integral_kernel_prod_right'.measurable
  obtain ⟨K,hK⟩ := exists_response_norm_bound D X g hgi
  have hni : Integrable (fun h => ∫ y,‖g y • (X.next (h,y)).1‖∂historyKernel D X h)
      (μ.map history) := by
    apply (integrable_const K).mono' hn.aestronglyMeasurable
    exact Filter.Eventually.of_forall (fun h => by
      rw [Real.norm_eq_abs,abs_of_nonneg (integral_nonneg (fun _ => norm_nonneg _))]
      exact hK h)
  have hFi : Integrable (fun p : H × Y => g p.2 • (X.next p).1)
      ((μ.map history) ⊗ₘ historyKernel D X) :=
    (Measure.integrable_compProd_iff hF.stronglyMeasurable.aestronglyMeasurable).mpr
      ⟨Filter.Eventually.of_forall (accessible_response_integrable_kernel D X g hgi),hni⟩
  rw [← hlaw] at hFi
  exact hFi.comp_measurable (hh.prodMk hy)

/-- P82's actual conditional moment identity with its analytic integrability
derived from the instrument and weighted basis products. -/
theorem accessible_conditional_moment (history : Ω → H) (observation : Ω → Y)
    (hh : Measurable history) (hy : Measurable observation)
    (hlaw : μ.map (fun ω => (history ω,observation ω))=(μ.map history) ⊗ₘ historyKernel D X)
    (g : Y → ℝ) (hg : Measurable g)
    (hgi : ∀ a,Integrable (fun y => g y • D.op a y) ν) :
    μ[fun ω => g (observation ω) • (X.next (history ω,observation ω)).1 |
      (inferInstance : MeasurableSpace H).comap history] =ᵐ[μ]
      (fun ω => momentOperator D g (X.action (history ω)) (X.state (history ω)).1) :=
  accessible_conditional_moment_of_integrable D X history observation hh hy hlaw g hg hgi
    (accessible_response_integrable D X history observation hh hy hlaw g hg hgi)

end Instrument
end Komorebi.LSM.ObservableMoments
