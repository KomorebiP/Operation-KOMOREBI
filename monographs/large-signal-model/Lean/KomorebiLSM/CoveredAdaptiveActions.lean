import KomorebiLSM.SequentialConfidence
import Mathlib.Probability.Kernel.Composition.IntegralCompProd
import Mathlib.MeasureTheory.Integral.Bochner.SumMeasure
import Mathlib.Tactic

/-! Covered action evidence from a literal conditional experiment.
The experiment assumption is equality of joint measures, not an assumed
conditional expectation of the importance-weighted observation. -/
set_option autoImplicit false
namespace Komorebi.LSM.CoveredAdaptiveActions
open MeasureTheory ProbabilityTheory
open scoped ENNReal BigOperators

section KernelCalculation
variable {H A Y : Type*} [mH : MeasurableSpace H] [MeasurableSpace A] [MeasurableSpace Y]
variable [Fintype A] [DecidableEq A] [MeasurableSingletonClass A]
variable (π : Kernel H A) (Q : Kernel (H × A) Y)
variable [IsMarkovKernel π] [IsMarkovKernel Q]

/-- The recorded target-action probability of the actual policy kernel. -/
noncomputable def propensity (a : A) (h : H) : ℝ := (π h).real {a}

omit [Fintype A] [DecidableEq A] [IsMarkovKernel π] in
theorem propensity_measurable (a : A) : Measurable (propensity π a) :=
  (π.measurable_coe (measurableSet_singleton a)).ennreal_toReal

/-- A predictable bounded test evaluated under the target observation kernel. -/
noncomputable def targetMean (φ : H × Y → ℝ) (a : A) (h : H) : ℝ :=
  ∫ y, φ (h,y) ∂Q (h,a)

omit [Fintype A] [DecidableEq A] [MeasurableSingletonClass A] in
theorem targetMean_measurable (φ : H × Y → ℝ) (hφ : Measurable φ) (a : A) :
    Measurable (targetMean Q φ a) := by
  let Qa : Kernel H Y := Q.comap (fun h => (h,a)) (measurable_id.prodMk measurable_const)
  exact hφ.stronglyMeasurable.integral_kernel_prod_right' (κ := Qa) |>.measurable

omit [Fintype A] [DecidableEq A] [MeasurableSingletonClass A] in
theorem targetMean_mem_Icc (φ : H × Y → ℝ) (hφ : Measurable φ)
    (hb : ∀ h y,φ (h,y)∈Set.Icc (0:ℝ) 1) (a : A) (h : H) :
    targetMean Q φ a h∈Set.Icc (0:ℝ) 1 := by
  have hi : Integrable (fun y => φ (h,y)) (Q (h,a)) := Integrable.of_mem_Icc (0:ℝ) 1
    ((hφ.comp (measurable_const.prodMk measurable_id)).aemeasurable)
    (Filter.Eventually.of_forall (hb h))
  refine ⟨integral_nonneg (fun y => (hb h y).1),?_⟩
  have h := integral_mono_ae hi (integrable_const (1:ℝ))
    (Filter.Eventually.of_forall (fun y => (hb h y).2))
  simpa only [targetMean,integral_const,probReal_univ,one_smul] using h

/-- Importance weighting before sampling the action/observation pair. -/
noncomputable def weightedTest (φ : H × Y → ℝ) (a : A) (p : H × (A × Y)) : ℝ :=
  if p.2.1=a then φ (p.1,p.2.2)/propensity π a p.1 else 0

omit [Fintype A] [IsMarkovKernel π] in
theorem weightedTest_measurable (φ : H × Y → ℝ) (hφ : Measurable φ) (a : A) :
    Measurable (weightedTest π φ a) := by
  apply Measurable.ite
    ((measurableSet_singleton a).preimage (measurable_fst.comp measurable_snd))
    ((hφ.comp (measurable_fst.prodMk (measurable_snd.comp measurable_snd))).div
      ((propensity_measurable π a).comp measurable_fst)) measurable_const

omit [MeasurableSpace Y] [Fintype A] [MeasurableSingletonClass A] [IsMarkovKernel π] in
theorem weightedTest_mem_Icc (φ : H × Y → ℝ)
    (hb : ∀ h y,φ (h,y)∈Set.Icc (0:ℝ) 1) (a : A)
    (c : ℝ) (hc : 0<c) (hcover : ∀ h,c≤propensity π a h) (p : H × (A × Y)) :
    weightedTest π φ a p∈Set.Icc (0:ℝ) (1/c) := by
  have hp : 0<propensity π a p.1 := hc.trans_le (hcover p.1)
  by_cases ha : p.2.1=a
  · simp only [weightedTest,ha,ite_true,Set.mem_Icc]
    refine ⟨div_nonneg (hb _ _).1 hp.le,?_⟩
    apply (div_le_div_iff₀ hp hc).mpr
    have := (hb p.1 p.2.2).2
    nlinarith [hcover p.1]
  · simp only [weightedTest,ha,ite_false,Set.mem_Icc,le_refl,true_and]
    exact one_div_nonneg.mpr hc.le

/-- Sampling the policy and then its action-conditioned observation cancels
the strictly positive target propensity exactly. -/
theorem integral_weightedTest (φ : H × Y → ℝ) (hφ : Measurable φ)
    (hb : ∀ h y,φ (h,y)∈Set.Icc (0:ℝ) 1) (a : A)
    (c : ℝ) (hc : 0<c) (hcover : ∀ h,c≤propensity π a h) (h : H) :
    (∫ r,weightedTest π φ a (h,r)∂(π ⊗ₖ Q) h)=targetMean Q φ a h := by
  have hmeas : Measurable (fun r => weightedTest π φ a (h,r)) :=
    (weightedTest_measurable π φ hφ a).comp (measurable_const.prodMk measurable_id)
  have hi : Integrable (fun r => weightedTest π φ a (h,r)) ((π ⊗ₖ Q) h) :=
    Integrable.of_mem_Icc (0:ℝ) (1/c) hmeas.aemeasurable
    (Filter.Eventually.of_forall (fun r => weightedTest_mem_Icc π φ hb a c hc hcover (h,r)))
  rw [ProbabilityTheory.integral_compProd hi]
  have hinner (b : A) : (∫ y,weightedTest π φ a (h,(b,y))∂Q (h,b))=
      if b=a then targetMean Q φ a h/propensity π a h else 0 := by
    by_cases ha : b=a
    · subst b
      simp only [weightedTest,ite_true,targetMean,integral_div]
    · simp [weightedTest,ha]
  rw [integral_fintype hi.integral_compProd]
  simp_rw [hinner,smul_eq_mul]
  simp only [mul_ite,mul_zero,Finset.sum_ite_eq',Finset.mem_univ,ite_true]
  exact mul_div_cancel₀ _ (ne_of_gt (hc.trans_le (hcover h)))

end KernelCalculation

section ConditionalExperiment
variable {Ω A Y : Type*} [mΩ : MeasurableSpace Ω] [mA : MeasurableSpace A]
variable [mY : MeasurableSpace Y] [Fintype A] [DecidableEq A] [MeasurableSingletonClass A]
variable {μ : Measure Ω} [IsProbabilityMeasure μ]
variable {m : MeasurableSpace Ω} (hm : m≤mΩ)

/-- A literal history/action/observation joint law. Its factorization says that
the recorded action is drawn from π before drawing from Q at that action.
The preaction information m and the full sample space are arbitrary. -/
structure Experiment (action : Ω → A) (observation : Ω → Y) where
  policy : @Kernel Ω A m mA
  observationKernel : @Kernel (Ω × A) Y (m.prod mA) mY
  policy_markov : IsMarkovKernel policy
  observation_markov : IsMarkovKernel observationKernel
  action_measurable : @Measurable Ω A mΩ mA action
  observation_measurable : @Measurable Ω Y mΩ mY observation
  joint_law :
    @Measure.map Ω (Ω × (A × Y)) mΩ (m.prod (mA.prod mY))
      (fun ω => (ω,(action ω,observation ω))) μ =
      (μ.trim hm) ⊗ₘ (policy ⊗ₖ observationKernel)

attribute [instance] Experiment.policy_markov Experiment.observation_markov

variable {action : Ω → A} {observation : Ω → Y}
variable (E : Experiment (mΩ := mΩ) (μ := μ) hm action observation)

omit [Fintype A] [DecidableEq A] [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
include hm E in
theorem recorded_joint_measurable :
    @Measurable Ω (Ω × (A × Y)) mΩ (m.prod (mA.prod mY))
      (fun ω => (ω,(action ω,observation ω))) :=
  (measurable_id'' hm).prodMk ((Experiment.action_measurable (mΩ := mΩ) E).prodMk (Experiment.observation_measurable (mΩ := mΩ) E))

/-- The actual importance-weighted random observation on the given experiment. -/
noncomputable def evidence (φ : Ω × Y → ℝ) (a : A) (ω : Ω) : ℝ :=
  weightedTest (mH := m) (Experiment.policy (mΩ := mΩ) E) φ a (ω,(action ω,observation ω))

omit [Fintype A] [IsProbabilityMeasure μ] in
theorem evidence_measurable (φ : Ω × Y → ℝ)
    (hφ : @Measurable (Ω × Y) ℝ (m.prod mY) _ φ) (a : A) :
    @Measurable Ω ℝ mΩ _ (evidence (mΩ := mΩ) hm E φ a) :=
  (weightedTest_measurable (mH := m) (Experiment.policy (mΩ := mΩ) E) φ hφ a).comp (recorded_joint_measurable (mΩ := mΩ) hm E)

omit [Fintype A] [MeasurableSingletonClass A] [IsProbabilityMeasure μ] in
theorem evidence_mem_Icc (φ : Ω × Y → ℝ)
    (hb : ∀ ω y,φ (ω,y)∈Set.Icc (0:ℝ) 1) (a : A)
    (c : ℝ) (hc : 0<c) (hcover : ∀ ω,c≤propensity (mH := m) (Experiment.policy (mΩ := mΩ) E) a ω) (ω : Ω) :
    evidence (mΩ := mΩ) hm E φ a ω∈Set.Icc (0:ℝ) (1/c) :=
  weightedTest_mem_Icc (mH := m) (Experiment.policy (mΩ := mΩ) E) φ hb a c hc hcover _

omit [Fintype A] [IsProbabilityMeasure μ] in
/-- Recording the action and observation at the next filtration level makes
the importance-weighted evidence adapted at that level. -/
theorem evidence_measurable_at {m' : MeasurableSpace Ω} (hmm' : m≤m')
    (ha : @Measurable Ω A m' mA action) (hy : @Measurable Ω Y m' mY observation)
    (φ : Ω × Y → ℝ) (hφ : @Measurable (Ω × Y) ℝ (m.prod mY) _ φ) (a : A) :
    @Measurable Ω ℝ m' _ (evidence (mΩ := mΩ) hm E φ a) :=
  (weightedTest_measurable (mH := m) (Experiment.policy (mΩ := mΩ) E) φ hφ a).comp
    ((measurable_id'' hmm').prodMk (ha.prodMk hy))

/-- Joint-law factorization and exact finite-action cancellation identify the
actual conditional expectation. No conditional-mean equation is an input. -/
theorem evidence_condExp (φ : Ω × Y → ℝ)
    (hφ : @Measurable (Ω × Y) ℝ (m.prod mY) _ φ)
    (hb : ∀ ω y,φ (ω,y)∈Set.Icc (0:ℝ) 1) (a : A)
    (c : ℝ) (hc : 0<c) (hcover : ∀ ω,c≤propensity (mH := m) (Experiment.policy (mΩ := mΩ) E) a ω) :
    μ[evidence (mΩ := mΩ) hm E φ a | m] =ᵐ[μ] targetMean (mH := m) (Experiment.observationKernel (mΩ := mΩ) E) φ a := by
  let : MeasurableSpace Ω := mΩ
  have hW := weightedTest_measurable (mH := m) (Experiment.policy (mΩ := mΩ) E) φ hφ a
  have hWi : Integrable (weightedTest (mH := m) (Experiment.policy (mΩ := mΩ) E) φ a)
      ((μ.trim hm) ⊗ₘ ((Experiment.policy (mΩ := mΩ) E) ⊗ₖ (Experiment.observationKernel (mΩ := mΩ) E))) :=
    Integrable.of_mem_Icc (0:ℝ) (1/c) hW.aemeasurable
      (Filter.Eventually.of_forall (weightedTest_mem_Icc (mH := m) (Experiment.policy (mΩ := mΩ) E) φ hb a c hc hcover))
  have hevi : Integrable (evidence (mΩ := mΩ) hm E φ a) μ :=
    Integrable.of_mem_Icc (0:ℝ) (1/c) (evidence_measurable (mΩ := mΩ) hm E φ hφ a).aemeasurable
      (Filter.Eventually.of_forall (evidence_mem_Icc (mΩ := mΩ) hm E φ hb a c hc hcover))
  have hg := targetMean_measurable (mH := m) (Experiment.observationKernel (mΩ := mΩ) E) φ hφ a
  have hgi : Integrable (targetMean (mH := m) (Experiment.observationKernel (mΩ := mΩ) E) φ a) μ :=
    Integrable.of_mem_Icc (0:ℝ) 1 (hg.mono hm le_rfl).aemeasurable
      (Filter.Eventually.of_forall (targetMean_mem_Icc (mH := m) (Experiment.observationKernel (mΩ := mΩ) E) φ hφ hb a))
  apply (ae_eq_condExp_of_forall_setIntegral_eq hm hevi
    (fun _ _ _ => hgi.integrableOn) ?_ hg.stronglyMeasurable.aestronglyMeasurable).symm
  intro s hs _
  calc
    (∫ ω in s,targetMean (mH := m) (Experiment.observationKernel (mΩ := mΩ) E) φ a ω∂μ)=
        ∫ ω in s,targetMean (mH := m) (Experiment.observationKernel (mΩ := mΩ) E) φ a ω∂μ.trim hm :=
      setIntegral_trim hm hg.stronglyMeasurable hs
    _ = ∫ p in s ×ˢ Set.univ,weightedTest (mH := m) (Experiment.policy (mΩ := mΩ) E) φ a p∂
        (μ.trim hm) ⊗ₘ ((Experiment.policy (mΩ := mΩ) E) ⊗ₖ (Experiment.observationKernel (mΩ := mΩ) E)) := by
      rw [Measure.setIntegral_compProd hs MeasurableSet.univ hWi.integrableOn]
      simp only [Measure.restrict_univ]
      apply setIntegral_congr_fun hs
      intro ω _
      exact (integral_weightedTest (mH := m) (Experiment.policy (mΩ := mΩ) E) (Experiment.observationKernel (mΩ := mΩ) E) φ hφ hb a c hc hcover ω).symm
    _ = ∫ p in s ×ˢ Set.univ,weightedTest (mH := m) (Experiment.policy (mΩ := mΩ) E) φ a p∂
        @Measure.map Ω (Ω × (A × Y)) mΩ (m.prod (mA.prod mY))
          (fun ω => (ω,(action ω,observation ω))) μ := by rw [(Experiment.joint_law (mΩ := mΩ) E)]
    _ = ∫ ω in s,evidence (mΩ := mΩ) hm E φ a ω∂μ := by
      let : MeasurableSpace (Ω × (A × Y)) := m.prod (mA.prod mY)
      rw [setIntegral_map (hs.prod MeasurableSet.univ) hW.aestronglyMeasurable
        (recorded_joint_measurable (mΩ := mΩ) hm E).aemeasurable]
      have hpre : (fun ω => (ω,(action ω,observation ω))) ⁻¹' (s ×ˢ Set.univ)=s := by
        ext ω
        simp
      rw [hpre]
      rfl

end ConditionalExperiment
end Komorebi.LSM.CoveredAdaptiveActions
