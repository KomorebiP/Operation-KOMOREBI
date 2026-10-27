import KomorebiLSM.MeasureTVCalculus
import KomorebiLSM.KernelTVMeasurable
import KomorebiLSM.ObservationLawKernels

/-! P69: actual causal record-law TV is bounded by conditional kernel TV averaged
under the true process and common policy. No common latent state space is used. -/
set_option autoImplicit false
namespace Komorebi.LSM.ObservationLawComparison
open MeasureTheory ProbabilityTheory SequentialLowerCertificate MeasureTVCalculus
open scoped ENNReal BigOperators

section KernelChange
variable {X Y : Type*} [MeasurableSpace X] [MeasurableSpace Y]
variable [MeasurableSpace.CountableOrCountablyGenerated X Y]

/-- Changing one observation kernel under one actual common prefix costs its
conditional TV averaged over that prefix. -/
theorem compProd_change (μ : Measure X) [IsProbabilityMeasure μ]
    (κ η : Kernel X Y) [IsMarkovKernel κ] [IsMarkovKernel η] :
    lawTV (μ ⊗ₘ κ) (μ ⊗ₘ η)≤∫ x,KernelTVMeasurable.distance κ η x∂μ := by
  apply lawTV_le_of_bounded_tests
  intro f hf h0 h1
  have hfi (K : Kernel X Y) [IsMarkovKernel K] (x : X) :
      Integrable (fun y => f (x,y)) (K x) :=
    bounded_test_integrable (K x) _ (hf.comp (measurable_const.prodMk measurable_id))
      (fun y => h0 (x,y)) (fun y => h1 (x,y))
  have hFm (K : Kernel X Y) [IsMarkovKernel K] :
      Measurable (fun x => ∫ y,f (x,y)∂K x) :=
    hf.stronglyMeasurable.integral_kernel_prod_right'.measurable
  have hF0 (K : Kernel X Y) [IsMarkovKernel K] (x : X) :
      0≤∫ y,f (x,y)∂K x := integral_nonneg (fun y => h0 (x,y))
  have hF1 (K : Kernel X Y) [IsMarkovKernel K] (x : X) :
      (∫ y,f (x,y)∂K x)≤1 := by
    calc (∫ y,f (x,y)∂K x)≤∫ _ : Y,(1:ℝ)∂K x :=
        integral_mono (hfi K x) (integrable_const _) (fun y => h1 (x,y))
      _ = 1 := by simp
  have hFk := bounded_test_integrable μ _ (hFm κ) (hF0 κ) (hF1 κ)
  have hFe := bounded_test_integrable μ _ (hFm η) (hF0 η) (hF1 η)
  have hd : Integrable (fun x => (∫ y,f (x,y)∂κ x)-(∫ y,f (x,y)∂η x)) μ :=
    (hFk.sub hFe).congr (by filter_upwards with x; rfl)
  rw [Measure.integral_compProd (bounded_test_integrable (μ ⊗ₘ κ) f hf h0 h1),
    Measure.integral_compProd (bounded_test_integrable (μ ⊗ₘ η) f hf h0 h1),← integral_sub hFk hFe]
  calc |∫ x,(∫ y,f (x,y)∂κ x)-(∫ y,f (x,y)∂η x)∂μ|≤
      ∫ x,|(∫ y,f (x,y)∂κ x)-(∫ y,f (x,y)∂η x)|∂μ := abs_integral_le_integral_abs
    _ ≤ ∫ x,KernelTVMeasurable.distance κ η x∂μ := by
      apply integral_mono hd.abs (KernelTVMeasurable.distance_integrable κ η μ)
      intro x
      exact bounded_test_integral_le_tv (κ x) (η x) _
        (hf.comp (measurable_const.prodMk measurable_id)) (fun y => h0 (x,y)) (fun y => h1 (x,y))
end KernelChange

section CausalLaws
open ObservationLawKernels
variable {I A Y : Type*} [MeasurableSpace I] [MeasurableSpace A] [MeasurableSpace Y]
variable [StandardBorelSpace Y]
variable (π : Policy I A Y) (P Q : ObservationKernel I A Y)
variable [∀ n,IsMarkovKernel (π n)] [∀ n,IsMarkovKernel (P n)] [∀ n,IsMarkovKernel (Q n)]

/-- The actual expected conditional discrepancy, under P's histories and policy actions. -/
noncomputable def drift (μ0 : Measure I) (t : ℕ) : ℝ :=
  ∫ ha,KernelTVMeasurable.distance (P t) (Q t) ha∂policyPrefix π P μ0 t

omit [StandardBorelSpace Y] [∀ n,IsMarkovKernel (π n)] in
theorem drift_nonneg (μ0 : Measure I) (t : ℕ) : 0≤drift π P Q μ0 t :=
  integral_nonneg (fun ha => KernelTVMeasurable.distance_nonneg (P t) (Q t) ha)

theorem drift_integrable (μ0 : Measure I) [IsProbabilityMeasure μ0] (t : ℕ) :
    Integrable (fun ha => KernelTVMeasurable.distance (P t) (Q t) ha)
      (policyPrefix π P μ0 t) :=
  KernelTVMeasurable.distance_integrable (P t) (Q t) _

/-- The expected error uses the actual P-history law, followed by the common
randomized action policy. -/
theorem drift_eq_iterated (μ0 : Measure I) [IsProbabilityMeasure μ0] (t : ℕ) :
    drift π P Q μ0 t = ∫ h,∫ a,KernelTVMeasurable.distance (P t) (Q t) (h,a)
      ∂π t h∂law π P μ0 t :=
  Measure.integral_compProd (drift_integrable π P Q μ0 t)

/-- The adjacent one-step hybrid uses the P prefix and the Q continuation.
Both contraction inequalities are derived for actual common Markov kernels. -/
theorem law_step (μ0 ν0 : Measure I) [IsProbabilityMeasure μ0] [IsProbabilityMeasure ν0] (n : ℕ) :
    lawTV (law π P μ0 (n+1)) (law π Q ν0 (n+1))≤
      lawTV (law π P μ0 n) (law π Q ν0 n)+drift π P Q μ0 n := by
  have hmap := lawTV_map (((law π P μ0 n) ⊗ₘ π n) ⊗ₘ P n)
    (((law π Q ν0 n) ⊗ₘ π n) ⊗ₘ Q n) (append n) (append_measurable n)
  have htri := lawTV_triangle (((law π P μ0 n) ⊗ₘ π n) ⊗ₘ P n)
    (((law π P μ0 n) ⊗ₘ π n) ⊗ₘ Q n) (((law π Q ν0 n) ⊗ₘ π n) ⊗ₘ Q n)
  have hcost := compProd_change ((law π P μ0 n) ⊗ₘ π n) (P n) (Q n)
  have hcont := (lawTV_compProd ((law π P μ0 n) ⊗ₘ π n) ((law π Q ν0 n) ⊗ₘ π n) (Q n)).trans
    (lawTV_compProd (law π P μ0 n) (law π Q ν0 n) (π n))
  calc lawTV (law π P μ0 (n+1)) (law π Q ν0 (n+1))≤
      lawTV (((law π P μ0 n) ⊗ₘ π n) ⊗ₘ P n) (((law π Q ν0 n) ⊗ₘ π n) ⊗ₘ Q n) := hmap
    _ ≤ lawTV (((law π P μ0 n) ⊗ₘ π n) ⊗ₘ P n) (((law π P μ0 n) ⊗ₘ π n) ⊗ₘ Q n)+
        lawTV (((law π P μ0 n) ⊗ₘ π n) ⊗ₘ Q n) (((law π Q ν0 n) ⊗ₘ π n) ⊗ₘ Q n) := htri
    _ ≤ drift π P Q μ0 n+lawTV (law π P μ0 n) (law π Q ν0 n) := add_le_add hcost hcont
    _ = _ := add_comm _ _

/-- Initial-history discrepancy adds its actual TV; every later cost is averaged
under P, including histories null under Q. -/
theorem lawTV_le_expected (μ0 ν0 : Measure I) [IsProbabilityMeasure μ0] [IsProbabilityMeasure ν0]
    (n : ℕ) : lawTV (law π P μ0 n) (law π Q ν0 n)≤
      min 1 (lawTV μ0 ν0+∑ t∈Finset.range n,drift π P Q μ0 t) := by
  apply le_min (lawTV_le_one _ _)
  induction n with
  | zero =>
    simp only [law,Finset.range_zero,Finset.sum_empty,add_zero]
    exact lawTV_map μ0 ν0 (initial (A := A) (Y := Y)) initial_measurable
  | succ n ih =>
    calc lawTV (law π P μ0 (n+1)) (law π Q ν0 (n+1))≤
        lawTV (law π P μ0 n) (law π Q ν0 n)+drift π P Q μ0 n := law_step π P Q μ0 ν0 n
      _ ≤ (lawTV μ0 ν0+∑ t∈Finset.range n,drift π P Q μ0 t)+drift π P Q μ0 n :=
        add_le_add ih le_rfl
      _ = _ := by rw [Finset.sum_range_succ]; ring

/-- The registered same-initial-history statement, with an actual initial law. -/
theorem lawTV_same_initial (μ0 : Measure I) [IsProbabilityMeasure μ0] (n : ℕ) :
    lawTV (law π P μ0 n) (law π Q μ0 n)≤min 1 (∑ t∈Finset.range n,drift π P Q μ0 t) := by
  simpa only [lawTV_self,zero_add] using lawTV_le_expected π P Q μ0 μ0 n

theorem drift_le_uniform (μ0 : Measure I) [IsProbabilityMeasure μ0] (t : ℕ) (ε : ℝ)
    (hε : ∀ h a,KernelTVMeasurable.distance (P t) (Q t) (h,a)≤ε) :
    drift π P Q μ0 t≤ε := by
  calc drift π P Q μ0 t≤∫ _ : History I A Y t × A,ε∂policyPrefix π P μ0 t :=
      integral_mono (KernelTVMeasurable.distance_integrable (P t) (Q t) _)
        (integrable_const _) (fun ha => hε ha.1 ha.2)
    _ = ε := by simp

/-- Uniform conditional budgets give the usual sum bound without any shared state. -/
theorem lawTV_le_uniform (μ0 ν0 : Measure I) [IsProbabilityMeasure μ0] [IsProbabilityMeasure ν0]
    (ε : ℕ → ℝ) (hε : ∀ t h a,KernelTVMeasurable.distance (P t) (Q t) (h,a)≤ε t) (n : ℕ) :
    lawTV (law π P μ0 n) (law π Q ν0 n)≤min 1 (lawTV μ0 ν0+∑ t∈Finset.range n,ε t) := by
  apply (lawTV_le_expected π P Q μ0 ν0 n).trans
  apply min_le_min le_rfl
  exact add_le_add le_rfl (Finset.sum_le_sum (fun t _ => drift_le_uniform π P Q μ0 t (ε t) (hε t)))

/-- Uniform budgets for the registered common-initial-history comparison. -/
theorem lawTV_same_initial_uniform (μ0 : Measure I) [IsProbabilityMeasure μ0]
    (ε : ℕ → ℝ) (hε : ∀ t h a,KernelTVMeasurable.distance (P t) (Q t) (h,a)≤ε t) (n : ℕ) :
    lawTV (law π P μ0 n) (law π Q μ0 n)≤min 1 (∑ t∈Finset.range n,ε t) := by
  simpa only [lawTV_self,zero_add] using lawTV_le_uniform π P Q μ0 μ0 ε hε n

/-- A fixed initial history is the point-mass special case of the same-law bound. -/
theorem lawTV_fixed_history (i : I) (n : ℕ) :
    lawTV (law π P (Measure.dirac i) n) (law π Q (Measure.dirac i) n)≤
      min 1 (∑ t∈Finset.range n,drift π P Q (Measure.dirac i) t) :=
  lawTV_same_initial π P Q (Measure.dirac i) n

/-- Every measurable observation-only readout of the record inherits the budget. -/
theorem lawTV_readout {Z : Type*} [MeasurableSpace Z]
    (μ0 ν0 : Measure I) [IsProbabilityMeasure μ0] [IsProbabilityMeasure ν0]
    (n : ℕ) (readout : History I A Y n → Z) (hr : Measurable readout) :
    lawTV ((law π P μ0 n).map readout) ((law π Q ν0 n).map readout)≤
      min 1 (lawTV μ0 ν0+∑ t∈Finset.range n,drift π P Q μ0 t) :=
  (lawTV_map _ _ readout hr).trans (lawTV_le_expected π P Q μ0 ν0 n)

end CausalLaws
end Komorebi.LSM.ObservationLawComparison
