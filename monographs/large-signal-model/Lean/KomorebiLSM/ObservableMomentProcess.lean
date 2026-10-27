import KomorebiLSM.ObservableMomentConditional
import Mathlib.MeasureTheory.Function.ConditionalExpectation.PullOut
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Probability.Process.Filtration

/-! Actual observable-history instruments yield predictable moment-regression
designs and responses. Accessibility and conditional experiment laws are
explicit inputs; no regression mean or confidence event is an input field. -/
set_option autoImplicit false
namespace Komorebi.LSM.ObservableMoments
open MeasureTheory ProbabilityTheory Matrix
open scoped ENNReal BigOperators Matrix

section Process
variable {Ω H E A Y : Type*} [mΩ : MeasurableSpace Ω] [mH : MeasurableSpace H]
variable [NormedAddCommGroup E] [NormedSpace ℝ E] [FiniteDimensional ℝ E]
variable [MeasurableSpace E] [BorelSpace E] [MeasurableSpace Y]
variable [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]
variable {C : BaseNorm.ProbabilityCone E} {ν : Measure Y} [IsProbabilityMeasure ν]
variable (D : ContinuousInstrument.DensityInstrument (A := A) C ν)
variable {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- The information is exactly a recorded history, and both successive states
are given by specified measurable maps of those observations. -/
structure AccessibleProcess (ℱ : Filtration ℕ mΩ) where
  history : ℕ → Ω → H
  history_measurable : ∀ n,Measurable[ℱ n] (history n)
  history_generates : ∀ n,mH.comap (history n)=ℱ n
  observation : ℕ → Ω → Y
  observation_measurable : ∀ n,Measurable[ℱ (n+1)] (observation n)
  stateMap : ℕ → AccessibleState (H := H) D
  joint_law : ∀ n,μ.map (fun ω => (history n ω,observation n ω))=
    (μ.map (history n)) ⊗ₘ historyKernel D (stateMap n)
  next_state : ∀ n,∀ᵐ ω∂μ,(stateMap n).next (history n ω,observation n ω)=
    (stateMap (n+1)).state (history (n+1) ω)

variable {ℱ : Filtration ℕ mΩ} (P : AccessibleProcess (H := H) (μ := μ) D ℱ)

noncomputable def currentState (n : ℕ) (ω : Ω) : E := (P.stateMap n).state (P.history n ω)
def currentAction (n : ℕ) (ω : Ω) : A := (P.stateMap n).action (P.history n ω)

omit [FiniteDimensional ℝ E] [BorelSpace E] [IsProbabilityMeasure μ] in
theorem currentState_measurable (n : ℕ) : Measurable[ℱ n] (currentState D P n) :=
  measurable_subtype_coe.comp ((P.stateMap n).state_measurable.comp (P.history_measurable n))

omit [FiniteDimensional ℝ E] [BorelSpace E] [IsProbabilityMeasure μ] in
theorem currentAction_measurable (n : ℕ) : Measurable[ℱ n] (currentAction D P n) :=
  (P.stateMap n).action_measurable.comp (P.history_measurable n)

omit [FiniteDimensional ℝ E] [BorelSpace E] [IsProbabilityMeasure μ] in
theorem currentState_mem (n : ℕ) (ω : Ω) : currentState D P n ω∈C.base :=
  ((P.stateMap n).state (P.history n ω)).2

theorem currentState_integrable (n : ℕ) : Integrable (currentState D P n) μ := by
  obtain ⟨R,_,hR⟩ := C.exists_cone_bound
  apply (integrable_const R).mono'
    ((currentState_measurable D P n).mono (ℱ.le n) le_rfl).aestronglyMeasurable
  exact Filter.Eventually.of_forall (fun ω => by
    simpa only [(currentState_mem D P n ω).2,mul_one] using
      hR (currentState D P n ω) (currentState_mem D P n ω).1)

/-- The literal next accessible state gives an integrable moment response. -/
theorem momentResponse_integrable (g : Y → ℝ) (hg : Measurable g)
    (hgi : ∀ a,Integrable (fun y => g y • D.op a y) ν) (n : ℕ) :
    Integrable (fun ω => g (P.observation n ω) • currentState D P (n+1) ω) μ := by
  have hi := accessible_response_integrable D (P.stateMap n) (P.history n) (P.observation n)
    ((P.history_measurable n).mono (ℱ.le n) le_rfl)
    ((P.observation_measurable n).mono (ℱ.le (n+1)) le_rfl) (P.joint_law n) g hg hgi
  apply hi.congr
  filter_upwards [P.next_state n] with ω he
  rw [he]
  rfl

/-- The conditional moment is derived for the actual next state, with respect
to the actual observed-history filtration, at each dependent time. -/
theorem process_conditional_moment (g : Y → ℝ) (hg : Measurable g)
    (hgi : ∀ a,Integrable (fun y => g y • D.op a y) ν) (n : ℕ) :
    μ[fun ω => g (P.observation n ω) • currentState D P (n+1) ω | ℱ n] =ᵐ[μ]
      (fun ω => momentOperator D g (currentAction D P n ω) (currentState D P n ω)) := by
  have hc := accessible_conditional_moment D (P.stateMap n) (P.history n) (P.observation n)
    ((P.history_measurable n).mono (ℱ.le n) le_rfl)
    ((P.observation_measurable n).mono (ℱ.le (n+1)) le_rfl) (P.joint_law n) g hg hgi
  rw [P.history_generates n] at hc
  have heq : (fun ω => g (P.observation n ω) • currentState D P (n+1) ω)=ᵐ[μ]
      (fun ω => g (P.observation n ω) • ((P.stateMap n).next (P.history n ω,P.observation n ω)).1) := by
    filter_upwards [P.next_state n] with ω he
    rw [he]
    rfl
  exact (condExp_congr_ae heq).trans hc

/-- The action gate is known before the response is observed. -/
noncomputable def actionGate (a : A) (n : ℕ) (ω : Ω) : ℝ := by
  classical
  exact if currentAction D P n ω=a then 1 else 0

omit [FiniteDimensional ℝ E] [BorelSpace E] [IsProbabilityMeasure μ] in
theorem actionGate_measurable (a : A) (n : ℕ) : Measurable[ℱ n] (actionGate D P a n) := by
  classical
  exact measurable_const.ite
    ((measurableSet_singleton a).preimage (currentAction_measurable D P n)) measurable_const

omit [FiniteDimensional ℝ E] [BorelSpace E] [IsProbabilityMeasure μ] in
theorem actionGate_norm_le (a : A) (n : ℕ) (ω : Ω) : ‖actionGate D P a n ω‖≤1 := by
  classical
  by_cases h : currentAction D P n ω=a <;> simp [actionGate,h]

/-- An exact observable regressor for each target action, with zeros on all
other action visits. It is not an estimated hidden state. -/
noncomputable def gatedDesign (a : A) (n : ℕ) (ω : Ω) : E :=
  actionGate D P a n ω • currentState D P n ω

omit [FiniteDimensional ℝ E] [IsProbabilityMeasure μ] in
theorem gatedDesign_measurable (a : A) (n : ℕ) : Measurable[ℱ n] (gatedDesign D P a n) :=
  (actionGate_measurable D P a n).smul (currentState_measurable D P n)

theorem gatedDesign_integrable (a : A) (n : ℕ) : Integrable (gatedDesign D P a n) μ := by
  apply ((currentState_integrable D P n).norm).mono'
    ((gatedDesign_measurable D P a n).mono (ℱ.le n) le_rfl).aestronglyMeasurable
  exact Filter.Eventually.of_forall (fun ω => by
    rw [gatedDesign,norm_smul]
    exact (mul_le_mul_of_nonneg_right (actionGate_norm_le D P a n ω) (norm_nonneg _)).trans_eq (one_mul _))

end Process

section Rows
variable {Ω H A Y : Type*} {r : ℕ} [mΩ : MeasurableSpace Ω] [mH : MeasurableSpace H]
variable [MeasurableSpace Y] [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]
variable {C : BaseNorm.ProbabilityCone (Fin r → ℝ)} {ν : Measure Y} [IsProbabilityMeasure ν]
variable (D : ContinuousInstrument.DensityInstrument (A := A) C ν)
variable {μ : Measure Ω} [IsProbabilityMeasure μ] {ℱ : Filtration ℕ mΩ}
variable (P : AccessibleProcess (H := H) (μ := μ) D ℱ)

/-- The actual matrix of an integrated operator moment in the fixed observable
coordinates, with no additional fit or coordinate identification. -/
noncomputable def momentMatrix (g : Y → ℝ) (a : A) : Matrix (Fin r) (Fin r) ℝ :=
  LinearMap.toMatrix' (momentOperator D g a).toLinearMap

omit [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] [IsProbabilityMeasure ν] in
@[simp] theorem momentMatrix_mulVec (g : Y → ℝ) (a : A) (z : Fin r → ℝ) :
    momentMatrix D g a *ᵥ z=momentOperator D g a z :=
  LinearMap.toMatrix'_mulVec _ _

noncomputable def gatedResponse (a : A) (g : Y → ℝ) (i : Fin r) (n : ℕ) (ω : Ω) : ℝ :=
  actionGate D P a n ω*(g (P.observation n ω)*currentState D P (n+1) ω i)

omit [IsProbabilityMeasure μ] in
/-- The response is genuinely recorded at the next filtration level. -/
theorem gatedResponse_measurable (a : A) (g : Y → ℝ) (hg : Measurable g)
    (i : Fin r) (n : ℕ) : Measurable[ℱ (n+1)] (gatedResponse D P a g i n) :=
  ((actionGate_measurable D P a n).mono (ℱ.mono (by omega)) le_rfl).mul
    ((hg.comp (P.observation_measurable n)).mul
      ((measurable_pi_apply i).comp (currentState_measurable D P (n+1))))

/-- The action-gated response has the exact fixed row-moment regression mean.
This mean equation is a conclusion of the instrument experiment. -/
theorem gatedResponse_condExp (a : A) (g : Y → ℝ) (hg : Measurable g)
    (hgi : ∀ b,Integrable (fun y => g y • D.op b y) ν) (i : Fin r) (n : ℕ) :
    μ[gatedResponse D P a g i n | ℱ n] =ᵐ[μ]
      (fun ω => (momentMatrix D g a *ᵥ gatedDesign D P a n ω) i) := by
  let L : (Fin r → ℝ) →L[ℝ] ℝ := ContinuousLinearMap.proj i
  have hi := momentResponse_integrable D P g hg hgi n
  have hcoord := L.comp_condExp_comm (m := ℱ n) hi
  have hcoord' : (fun ω => (μ[fun ω => g (P.observation n ω) • currentState D P (n+1) ω | ℱ n]) ω i)=ᵐ[μ]
      μ[(fun ω => g (P.observation n ω)*currentState D P (n+1) ω i) | ℱ n] := by
    simpa only [L,Function.comp_def,ContinuousLinearMap.proj_apply,Pi.smul_apply,smul_eq_mul] using hcoord
  have hvec := process_conditional_moment D P g hg hgi n
  have hrow : μ[(fun ω => g (P.observation n ω)*currentState D P (n+1) ω i) | ℱ n]=ᵐ[μ]
      (fun ω => (momentOperator D g (currentAction D P n ω) (currentState D P n ω)) i) := by
    filter_upwards [hcoord',hvec] with ω hc hv
    rw [← hc,hv]
  have hip : Integrable (fun ω => g (P.observation n ω)*currentState D P (n+1) ω i) μ :=
    L.integrable_comp hi
  have hpull := condExp_stronglyMeasurable_mul_of_bound (ℱ.le n)
    (actionGate_measurable D P a n).stronglyMeasurable hip (1:ℝ)
    (Filter.Eventually.of_forall (actionGate_norm_le D P a n))
  filter_upwards [hpull,hrow] with ω hp hr
  change (μ[(fun ω => actionGate D P a n ω)*
    (fun ω => g (P.observation n ω)*currentState D P (n+1) ω i) | ℱ n]) ω=_
  rw [hp]
  change actionGate D P a n ω*(μ[fun ω => g (P.observation n ω)*currentState D P (n+1) ω i | ℱ n]) ω=_
  rw [hr,momentMatrix_mulVec,gatedDesign,map_smul]
  classical
  by_cases ha : currentAction D P n ω=a
  · simp [actionGate,ha]
  · simp [actionGate,ha]

end Rows
end Komorebi.LSM.ObservableMoments
