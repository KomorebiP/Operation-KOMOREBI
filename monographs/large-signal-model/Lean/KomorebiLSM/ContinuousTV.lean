import KomorebiLSM.BaseNormIntegration
import KomorebiLSM.TimeRecords
import KomorebiLSM.ContinuousTVDensity
import KomorebiLSM.SequentialLowerCertificate
import Mathlib.MeasureTheory.Integral.Prod
import Mathlib.MeasureTheory.VectorMeasure.WithDensityVec

/-! Continuous full-law comparison on one actual probability cone. The positive
base norm is the infimum over positive decompositions, and lawTV is the half
variation of the difference of the actual probability measures. -/
set_option autoImplicit false
namespace Komorebi.LSM.ContinuousTV
open MeasureTheory ProbabilityTheory
open scoped ENNReal BigOperators
variable {E A Y : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace Y]
variable {C : BaseNorm.ProbabilityCone E} {μ : Measure Y}
variable (D F : ContinuousInstrument.DensityInstrument (A := A) C μ)

omit [MeasurableSpace E] [BorelSpace E] in
/-- Integrated contraction follows from actual positive decompositions. -/
theorem integrated_contraction (a : A) (z : E) :
    (∫ y,C.value (D.op a y z)∂μ)≤C.value z := by
  apply C.le_value
  intro u hu v hv hz
  have hfi := C.integrable_value (D.applied_integrable a z)
  have hgi := (D.density_integrable a u).add (D.density_integrable a v)
  have hpoint : ∀ᵐ y∂μ,C.value (D.op a y z)≤D.density a y u+D.density a y v := by
    filter_upwards [D.positive a] with y hy
    rw [hz,map_sub]
    exact (C.value_sub_le _ _).trans_eq (by
      rw [C.value_on_cone (hy u hu),C.value_on_cone (hy v hv)]
      rfl)
  calc (∫ y,C.value (D.op a y z)∂μ)≤∫ y,D.density a y u+D.density a y v∂μ :=
      integral_mono_ae hfi hgi hpoint
    _ = C.mass u+C.mass v := by
      rw [integral_add (D.density_integrable a u) (D.density_integrable a v),
        D.integral_density a u,D.integral_density a v]

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- A bound on normalized inputs extends homogeneously to the whole cone. -/
theorem integrated_discrepancy (fallback : ContinuousInstrument.DensityInstrument.State C)
    (a : A) (ε : ℝ)
    (hε : ∀ z∈C.base,(∫ y,C.value (D.op a y z-F.op a y z)∂μ)≤ε)
    {z : E} (hz : z∈C.carrier) :
    (∫ y,C.value (D.op a y z-F.op a y z)∂μ)≤ε*C.mass z := by
  have hm := C.mass_nonneg hz
  have hs (y : Y) : D.op a y z-F.op a y z=
      C.mass z • (D.op a y (ContinuousRecords.normalize fallback z).1-
        F.op a y (ContinuousRecords.normalize fallback z).1) := by
    rw [smul_sub,← map_smul,← map_smul,ContinuousRecords.mass_smul_normalize fallback hz]
  simp_rw [hs,C.value_smul,abs_of_nonneg hm]
  rw [integral_const_mul]
  simpa only [mul_comm ε] using mul_le_mul_of_nonneg_left
    (hε _ (ContinuousRecords.normalize fallback z).2) hm

omit [MeasurableSpace E] [BorelSpace E] in
/-- One step separates transported state error and the declared instrument error. -/
theorem integrated_step_error (fallback : ContinuousInstrument.DensityInstrument.State C)
    (a : A) (ε : ℝ)
    (hε : ∀ z∈C.base,(∫ y,C.value (D.op a y z-F.op a y z)∂μ)≤ε)
    (u : E) {v : E} (hv : v∈C.carrier) :
    (∫ y,C.value (D.op a y u-F.op a y v)∂μ)≤C.value (u-v)+ε*C.mass v := by
  have hi := C.integrable_value ((D.applied_integrable a u).sub (F.applied_integrable a v))
  have ht := C.integrable_value (D.applied_integrable a (u-v))
  have hd := C.integrable_value ((D.applied_integrable a v).sub (F.applied_integrable a v))
  have hp (y : Y) : C.value (D.op a y u-F.op a y v)≤
      C.value (D.op a y (u-v))+C.value (D.op a y v-F.op a y v) := by
    have he : D.op a y u-F.op a y v=D.op a y (u-v)+(D.op a y v-F.op a y v) := by
      rw [map_sub]; abel
    rw [he]
    exact C.value_add_le _ _
  calc (∫ y,C.value (D.op a y u-F.op a y v)∂μ)≤
      ∫ y,C.value (D.op a y (u-v))+C.value (D.op a y v-F.op a y v)∂μ :=
        integral_mono_ae hi (ht.add hd) (Filter.Eventually.of_forall hp)
    _ = (∫ y,C.value (D.op a y (u-v))∂μ)+(∫ y,C.value (D.op a y v-F.op a y v)∂μ) :=
      integral_add ht hd
    _ ≤ C.value (u-v)+ε*C.mass v := add_le_add (integrated_contraction D a (u-v))
      (integrated_discrepancy D F fallback a ε hε hv)


omit [MeasurableSpace E] [BorelSpace E] in
theorem lintegrated_step_error (fallback : ContinuousInstrument.DensityInstrument.State C)
    (a : A) (ε : ℝ)
    (hε : ∀ z∈C.base,(∫ y,C.value (D.op a y z-F.op a y z)∂μ)≤ε)
    (u : E) {v : E} (hv : v∈C.carrier) :
    (∫⁻ y,ENNReal.ofReal (C.value (D.op a y u-F.op a y v))∂μ)≤
      ENNReal.ofReal (C.value (u-v)+ε*C.mass v) := by
  have hi : Integrable (fun y => C.value (D.op a y u-F.op a y v)) μ :=
    C.integrable_value ((D.applied_integrable a u).sub (F.applied_integrable a v))
  rw [← ofReal_integral_eq_lintegral_ofReal hi
    (Filter.Eventually.of_forall (fun y => C.value_nonneg _))]
  exact ENNReal.ofReal_le_ofReal (integrated_step_error D F fallback a ε hε u hv)

section Records
open ContinuousRecords
variable [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] [IsProbabilityMeasure μ]
variable (Ds Fs : ℕ → ContinuousInstrument.DensityInstrument (A := A) C μ)

/-- Actual chronological states, multiplied by the common randomized policy weight. -/
noncomputable def weightedRun (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ)
    (h : History (A × Y) n) : E := (π.weight n h).toReal • TimeRecords.run Ds z n h

omit [IsProbabilityMeasure μ] in
theorem weightedRun_measurable (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ) :
    Measurable (weightedRun Ds π z n) :=
  (Policy.weight_measurable π n).ennreal_toReal.smul (TimeRecords.run_measurable Ds z n)

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem weightedRun_succ (π : Policy (A := A) (Y := Y)) (z : E) (n : ℕ)
    (h : History (A × Y) n) (r : A × Y) :
    weightedRun Ds π z (n+1) (h,r)=
      (π.probability n h r.1).toReal • (Ds n).op r.1 r.2 (weightedRun Ds π z n h) := by
  simp only [weightedRun,Policy.weight,TimeRecords.run,ENNReal.toReal_mul,map_smul,smul_smul]
  rw [mul_comm]

theorem weightedRun_mem_ae (π : Policy (A := A) (Y := Y)) {z : E}
    (hz : z∈C.carrier) (n : ℕ) :
    ∀ᵐ h∂reference (stepReference (A := A) μ) n,weightedRun Ds π z n h∈C.carrier := by
  filter_upwards [TimeRecords.run_mem_ae Ds hz n] with h hh
  exact C.smul_mem ENNReal.toReal_nonneg hh

theorem mass_lintegral (π : Policy (A := A) (Y := Y))
    (z : ContinuousInstrument.DensityInstrument.State C) (n : ℕ) :
    (∫⁻ h,ENNReal.ofReal (C.mass (weightedRun Ds π z.1 n h))∂
      reference (stepReference (A := A) μ) n)=1 := by
  have hm := TimeRecords.recordLaw_univ Ds π z n
  rw [TimeRecords.recordLaw,withDensity_apply _ MeasurableSet.univ,Measure.restrict_univ] at hm
  simpa only [TimeRecords.recordDensity_eq_ofReal_weightedRun,weightedRun] using hm


/-- Integration over both the randomized action and the next continuous record. -/
theorem policy_step_lintegral_error (fallback : ContinuousInstrument.DensityInstrument.State C)
    (π : Policy (A := A) (Y := Y)) (n : ℕ) (h : History (A × Y) n) (ε : ℝ)
    (hε : ∀ a z,z∈C.base → (∫ y,C.value (D.op a y z-F.op a y z)∂μ)≤ε)
    (u : E) {v : E} (hv : v∈C.carrier) :
    (∫⁻ r,ENNReal.ofReal (C.value ((π.probability n h r.1).toReal •
      (D.op r.1 r.2 u-F.op r.1 r.2 v)))∂stepReference (A := A) μ)≤
      ENNReal.ofReal (C.value (u-v)+ε*C.mass v) := by
  have hd (a : A) : Measurable (fun y : Y => C.value (D.op a y u-F.op a y v)) := by
    exact C.value_continuous.measurable.comp
      (((ContinuousLinearMap.apply ℝ E u).continuous.measurable.comp (D.measurable_op a)).sub
        ((ContinuousLinearMap.apply ℝ E v).continuous.measurable.comp (F.measurable_op a)))
  have hm : Measurable (fun r : A × Y => ENNReal.ofReal (C.value
      ((π.probability n h r.1).toReal • (D.op r.1 r.2 u-F.op r.1 r.2 v)))) := by
    apply measurable_from_prod_countable_right
    intro a
    simpa only [C.value_smul,abs_of_nonneg ENNReal.toReal_nonneg,Pi.mul_apply] using
      (measurable_const.mul (hd a)).ennreal_ofReal
  rw [stepReference,lintegral_prod _ hm.aemeasurable,lintegral_count,tsum_fintype]
  have hi (a : A) : (∫⁻ y,ENNReal.ofReal (C.value ((π.probability n h a).toReal •
      (D.op a y u-F.op a y v)))∂μ)≤
      π.probability n h a * ENNReal.ofReal (C.value (u-v)+ε*C.mass v) := by
    simp_rw [C.value_smul,abs_of_nonneg ENNReal.toReal_nonneg,
      ENNReal.ofReal_mul ENNReal.toReal_nonneg]
    rw [lintegral_const_mul _ (hd a).ennreal_ofReal,
      ENNReal.ofReal_toReal (TimeRecords.policy_probability_ne_top π n h a)]
    exact mul_le_mul' le_rfl (lintegrated_step_error D F fallback a ε (hε a) u hv)
  calc (∑ a,∫⁻ y,ENNReal.ofReal (C.value ((π.probability n h a).toReal •
      (D.op a y u-F.op a y v)))∂μ)≤
      ∑ a,π.probability n h a * ENNReal.ofReal (C.value (u-v)+ε*C.mass v) :=
        Finset.sum_le_sum (fun a _ => hi a)
    _ = ENNReal.ofReal (C.value (u-v)+ε*C.mass v) := by
      rw [← Finset.sum_mul,π.sum_one,one_mul]


/-- Integrated signed state error on the genuine continuous product reference. -/
noncomputable def stateError (π : Policy (A := A) (Y := Y)) (u v : E) (n : ℕ) : ℝ≥0∞ :=
  ∫⁻ h,ENNReal.ofReal (C.value (weightedRun Ds π u n h-weightedRun Fs π v n h))∂
    reference (stepReference (A := A) μ) n

omit [IsProbabilityMeasure μ] in
theorem error_integrand_measurable (π : Policy (A := A) (Y := Y)) (u v : E) (n : ℕ) :
    Measurable (fun h => ENNReal.ofReal (C.value
      (weightedRun Ds π u n h-weightedRun Fs π v n h))) :=
  (C.value_continuous.measurable.comp
    ((weightedRun_measurable Ds π u n).sub (weightedRun_measurable Fs π v n))).ennreal_ofReal

/-- The common policy preserves the one-step integrated error recurrence. -/
theorem stateError_step (fallback : ContinuousInstrument.DensityInstrument.State C)
    (π : Policy (A := A) (Y := Y)) (u : E)
    (v : ContinuousInstrument.DensityInstrument.State C) (n : ℕ) (ε : ℝ) (hε0 : 0≤ε)
    (hε : ∀ a z,z∈C.base → (∫ y,C.value ((Ds n).op a y z-(Fs n).op a y z)∂μ)≤ε) :
    stateError Ds Fs π u v.1 (n+1)≤stateError Ds Fs π u v.1 n+ENNReal.ofReal ε := by
  change (∫⁻ p : History (A × Y) n × (A × Y),ENNReal.ofReal (C.value
    (weightedRun Ds π u (n+1) p-weightedRun Fs π v.1 (n+1) p))∂
      (reference (stepReference (A := A) μ) n).prod (stepReference (A := A) μ))≤_
  have hmprod : Measurable (fun p : History (A × Y) n × (A × Y) => ENNReal.ofReal (C.value
      (weightedRun Ds π u (n+1) p-weightedRun Fs π v.1 (n+1) p))) :=
    error_integrand_measurable Ds Fs π u v.1 (n+1)
  rw [lintegral_prod _ hmprod.aemeasurable]
  calc
    (∫⁻ h,∫⁻ r,ENNReal.ofReal (C.value
      (weightedRun Ds π u (n+1) (h,r)-weightedRun Fs π v.1 (n+1) (h,r)))∂
      stepReference (A := A) μ∂reference (stepReference (A := A) μ) n)≤
      ∫⁻ h,ENNReal.ofReal (C.value (weightedRun Ds π u n h-weightedRun Fs π v.1 n h)+
        ε*C.mass (weightedRun Fs π v.1 n h))∂reference (stepReference (A := A) μ) n := by
      apply lintegral_mono_ae
      filter_upwards [weightedRun_mem_ae Fs π v.2.1 n] with h hh
      simpa only [weightedRun_succ,← smul_sub] using
        policy_step_lintegral_error (Ds n) (Fs n) fallback π n h ε hε
          (weightedRun Ds π u n h) hh
    _ = stateError Ds Fs π u v.1 n+ENNReal.ofReal ε := by
      have he : (fun h => ENNReal.ofReal (C.value
          (weightedRun Ds π u n h-weightedRun Fs π v.1 n h)+ε*C.mass (weightedRun Fs π v.1 n h)))
          =ᵐ[reference (stepReference (A := A) μ) n]
          (fun h => ENNReal.ofReal (C.value (weightedRun Ds π u n h-weightedRun Fs π v.1 n h))+
            ENNReal.ofReal ε * ENNReal.ofReal (C.mass (weightedRun Fs π v.1 n h))) := by
        filter_upwards [weightedRun_mem_ae Fs π v.2.1 n] with h hh
        rw [ENNReal.ofReal_add (C.value_nonneg _) (mul_nonneg hε0 (C.mass_nonneg hh)),
          ENNReal.ofReal_mul hε0]
      have hm : Measurable (fun h => ENNReal.ofReal (C.mass (weightedRun Fs π v.1 n h))) :=
        ((ContinuousInstrument.massCLM C).continuous.measurable.comp
          (weightedRun_measurable Fs π v.1 n)).ennreal_ofReal
      rw [lintegral_congr_ae he,lintegral_add_left (error_integrand_measurable Ds Fs π u v.1 n),
        lintegral_const_mul _ hm,mass_lintegral Fs π v n,mul_one]
      rfl

/-- Iterating the recurrence requires no branch-density lower margin. -/
theorem stateError_le (π : Policy (A := A) (Y := Y))
    (u v : ContinuousInstrument.DensityInstrument.State C) (ε : ℕ → ℝ)
    (hε0 : ∀ n,0≤ε n)
    (hε : ∀ n a z,z∈C.base → (∫ y,C.value ((Ds n).op a y z-(Fs n).op a y z)∂μ)≤ε n) :
    ∀ n,stateError Ds Fs π u.1 v.1 n≤ENNReal.ofReal (C.value (u.1-v.1)+∑ i∈Finset.range n,ε i) := by
  intro n
  induction n with
  | zero => simp [stateError,reference,weightedRun,Policy.weight,TimeRecords.run]
  | succ n ih =>
    calc stateError Ds Fs π u.1 v.1 (n+1)≤stateError Ds Fs π u.1 v.1 n+ENNReal.ofReal (ε n) :=
        stateError_step Ds Fs v π u.1 v n (ε n) (hε0 n) (hε n)
      _ ≤ ENNReal.ofReal (C.value (u.1-v.1)+∑ i∈Finset.range n,ε i)+ENNReal.ofReal (ε n) :=
        add_le_add ih le_rfl
      _ = ENNReal.ofReal (C.value (u.1-v.1)+∑ i∈Finset.range (n+1),ε i) := by
        rw [Finset.sum_range_succ,← ENNReal.ofReal_add
          (add_nonneg (C.value_nonneg _) (Finset.sum_nonneg (fun i _ => hε0 i))) (hε0 n)]
        congr 1
        ring


/-- Reading mass from the two actual positive states cannot increase their
base-norm error. This compares the literal record-measure densities. -/
theorem density_lintegral_le_stateError (π : Policy (A := A) (Y := Y))
    (u v : ContinuousInstrument.DensityInstrument.State C) (n : ℕ) :
    (∫⁻ h,ENNReal.ofReal |(TimeRecords.recordDensity Ds π u.1 n h).toReal-
      (TimeRecords.recordDensity Fs π v.1 n h).toReal|∂reference (stepReference (A := A) μ) n)≤
      stateError Ds Fs π u.1 v.1 n := by
  apply lintegral_mono_ae
  filter_upwards [weightedRun_mem_ae Ds π u.2.1 n,weightedRun_mem_ae Fs π v.2.1 n] with h hu hv
  simp only [TimeRecords.recordDensity_eq_ofReal_weightedRun]
  change ENNReal.ofReal |(ENNReal.ofReal (C.mass (weightedRun Ds π u.1 n h))).toReal-
    (ENNReal.ofReal (C.mass (weightedRun Fs π v.1 n h))).toReal|≤_
  rw [ENNReal.toReal_ofReal (C.mass_nonneg hu),ENNReal.toReal_ofReal (C.mass_nonneg hv)]
  apply ENNReal.ofReal_le_ofReal
  simpa only [map_sub] using C.abs_mass_le (weightedRun Ds π u.1 n h-weightedRun Fs π v.1 n h)


/-- The full time-dependent record-measure bound under one arbitrary common
measurable randomized policy. All instruments use the same actual cone and reference. -/
theorem record_lawTV_le (π : Policy (A := A) (Y := Y))
    (u v : ContinuousInstrument.DensityInstrument.State C) (ε : ℕ → ℝ)
    (hε0 : ∀ n,0≤ε n)
    (hε : ∀ n a z,z∈C.base → (∫ y,C.value ((Ds n).op a y z-(Fs n).op a y z)∂μ)≤ε n)
    (e0 : ℝ) (he0 : C.value (u.1-v.1)≤e0) (n : ℕ) :
    SequentialLowerCertificate.lawTV (TimeRecords.recordLaw Ds π u.1 n)
      (TimeRecords.recordLaw Fs π v.1 n)≤min 1 ((e0+∑ i∈Finset.range n,ε i)/2) := by
  have he00 : 0≤e0 := (C.value_nonneg _).trans he0
  have hB0 : 0≤e0+∑ i∈Finset.range n,ε i :=
    add_nonneg he00 (Finset.sum_nonneg (fun i _ => hε0 i))
  have hs : stateError Ds Fs π u.1 v.1 n≤ENNReal.ofReal (e0+∑ i∈Finset.range n,ε i) :=
    (stateError_le Ds Fs π u v ε hε0 hε n).trans
      (ENNReal.ofReal_le_ofReal (add_le_add he0 le_rfl))
  have hp : IsProbabilityMeasure ((reference (stepReference (A := A) μ) n).withDensity
      (TimeRecords.recordDensity Ds π u.1 n)) := TimeRecords.recordLaw_probability Ds π u n
  have hq : IsProbabilityMeasure ((reference (stepReference (A := A) μ) n).withDensity
      (TimeRecords.recordDensity Fs π v.1 n)) := TimeRecords.recordLaw_probability Fs π v n
  have hn : ENNReal.ofReal (SequentialLowerCertificate.lawTV (TimeRecords.recordLaw Ds π u.1 n)
      (TimeRecords.recordLaw Fs π v.1 n))≤ENNReal.ofReal ((e0+∑ i∈Finset.range n,ε i)/2) := by
    change ENNReal.ofReal (SequentialLowerCertificate.lawTV
      ((reference (stepReference (A := A) μ) n).withDensity (TimeRecords.recordDensity Ds π u.1 n))
      ((reference (stepReference (A := A) μ) n).withDensity (TimeRecords.recordDensity Fs π v.1 n)))≤_
    rw [ContinuousTVDensity.ofReal_lawTV_withDensity_lintegral _ _ _
      (TimeRecords.recordDensity_measurable Ds π u.1 n).aemeasurable
      (TimeRecords.recordDensity_measurable Fs π v.1 n).aemeasurable]
    calc (1/2:ℝ≥0∞) * (∫⁻ h,ENNReal.ofReal
        |(TimeRecords.recordDensity Ds π u.1 n h).toReal-(TimeRecords.recordDensity Fs π v.1 n h).toReal|∂
          reference (stepReference (A := A) μ) n)≤
        (1/2:ℝ≥0∞)*ENNReal.ofReal (e0+∑ i∈Finset.range n,ε i) :=
          mul_le_mul' le_rfl ((density_lintegral_le_stateError Ds Fs π u v n).trans hs)
      _ = ENNReal.ofReal ((e0+∑ i∈Finset.range n,ε i)/2) := by
        rw [show (1/2:ℝ≥0∞)=ENNReal.ofReal (1/2:ℝ) by
          rw [ENNReal.ofReal_div_of_pos (by norm_num : (0:ℝ)<2)]
          norm_num,← ENNReal.ofReal_mul (by norm_num : (0:ℝ)≤1/2)]
        congr 1
        ring
  have ht := ENNReal.toReal_mono ENNReal.ofReal_ne_top hn
  have hreal : SequentialLowerCertificate.lawTV (TimeRecords.recordLaw Ds π u.1 n)
      (TimeRecords.recordLaw Fs π v.1 n)≤(e0+∑ i∈Finset.range n,ε i)/2 := by
    have hhalf0 : 0≤(e0+∑ i∈Finset.range n,ε i)/2 := div_nonneg hB0 (by norm_num)
    simpa only [ENNReal.toReal_ofReal (SequentialLowerCertificate.lawTV_nonneg _ _),
      ENNReal.toReal_ofReal hhalf0] using ht
  exact le_min (SequentialLowerCertificate.lawTV_le_one _ _) hreal

end Records
end Komorebi.LSM.ContinuousTV
