import AVOC.ArtifactWorkflowSource
import Mathlib.Tactic.FinCases
import Mathlib.Algebra.BigOperators.Fin

set_option maxHeartbeats 800000

namespace Komorebi.AVOC.ArtifactWorkflowExamples

open Certificate Binding ArtifactWorkflow

/-- Hidden world is receipt availability, not truth of the task proposition. -/
def prior : RationalBelief Bool where
  prob _ := 1/2
  nonneg _ := by norm_num
  sum_one := by norm_num [Fintype.sum_bool]

/-- One valid-report label and two distinct rejection reasons. -/
def raw : RationalChannel Bool (Fin 3) where
  prob w o := if w then (if o = 0 then 3/4 else if o = 1 then 1/4 else 0)
    else (if o = 0 then 1/4 else if o = 1 then 1/2 else 1/4)
  nonneg w o := by cases w <;> fin_cases o <;> norm_num
  sum_one w := by
    have hne : (2 : Fin 3) ≠ 1 := by decide
    cases w <;> norm_num [Fin.sum_univ_succ, hne]

def coarse : RationalChannel Bool Bool where
  prob w d := if w = d then 3/4 else 1/4
  nonneg w d := by split <;> norm_num
  sum_one w := by cases w <;> norm_num [Fintype.sum_bool]

def verdict (o : Fin 3) : Bool := decide (o = 0)

theorem channel_is_coarse : Filtered.reportChannel raw verdict = coarse := by
  apply RationalChannel.ext
  intro w d
  have hne : (2 : Fin 3) ≠ 1 := by decide
  cases w <;> cases d <;> norm_num [Filtered.reportChannel, raw, verdict, coarse, Fin.sum_univ_succ, hne]

theorem coarse_probability (d : Bool) : predictiveProb prior coarse d = 1/2 := by
  cases d <;> norm_num [predictiveProb, prior, coarse, Fintype.sum_bool]

theorem coarse_success_posterior : (bayesUpdateTotal prior coarse true).prob true = 3/4 := by
  have h := total_posterior_scaled prior coarse true true
  rw [coarse_probability] at h
  have rhs : prior.prob true * coarse.prob true true = (3/8 : ℚ) := by norm_num [prior, coarse]
  rw [rhs] at h
  linarith

theorem coarse_rejection_posterior : (bayesUpdateTotal prior coarse false).prob true = 1/4 := by
  have h := total_posterior_scaled prior coarse false true
  rw [coarse_probability] at h
  have rhs : prior.prob true * coarse.prob true false = (1/8 : ℚ) := by norm_num [prior, coarse]
  rw [rhs] at h
  linarith

theorem raw_rejection_posterior : (bayesUpdateTotal prior raw (1 : Fin 3)).prob true = 1/3 := by
  have h := total_posterior_scaled prior raw (1 : Fin 3) true
  have hp : predictiveProb prior raw (1 : Fin 3) = 3/8 := by
    norm_num [predictiveProb, prior, raw, Fintype.sum_bool]
  rw [hp] at h
  have rhs : prior.prob true * raw.prob true (1 : Fin 3) = (1/8 : ℚ) := by norm_num [prior, raw]
  rw [rhs] at h
  linarith

theorem rejecting_is_not_ignoring :
    (bayesUpdateTotal prior coarse false).prob true ≠ prior.prob true := by
  rw [coarse_rejection_posterior]
  norm_num [prior]

theorem coarse_is_not_chosen_raw_posterior :
    (bayesUpdateTotal prior coarse false).prob true ≠
      (bayesUpdateTotal prior raw (1 : Fin 3)).prob true := by
  rw [coarse_rejection_posterior, raw_rejection_posterior]
  norm_num

def identity : Identity := ⟨"root", .truth, "[\"true\"]", [], [("backend", "propositional")]⟩
def artifact : Artifact := ⟨identity, "[\"true\"]", .truth⟩
def ticket : Ticket := ⟨0, artifact⟩
def receipt : Receipt := ⟨ticket, true⟩

def proto : Protocol Bool (Fin 1) Unit (Fin 3) where
  formula _ := .truth
  valuation _ := True
  spec _ := identity
  describes _ := by
    constructor
    · rfl
    · intro f hf
      simp [Binding.context, identity] at hf
  candidate _ _ := artifact
  registerFee _ _ := 1
  verifyFee _ := 1
  admitFee _ := 1
  admissionValue _ := 8
  rawChannel _ := raw
  rawReceipt s o := if o = 0 then s.slot.pending.map (fun t => ⟨t,true⟩)
    else if o = 1 then none else s.slot.pending.map (fun t => ⟨t,false⟩)

def initial : State Bool (Fin 1) := ⟨prior, ∅, ⟨0,none⟩, none, none, 3, 0, false⟩
def registered : State Bool (Fin 1) := registerStep proto initial 0 ()
noncomputable def passed : State Bool (Fin 1) := verifyStep proto registered true
noncomputable def rejected : State Bool (Fin 1) := verifyStep proto registered false
noncomputable def admitted : State Bool (Fin 1) := admitStep proto passed

theorem initial_safe : BudgetSafe proto 3 initial := by
  constructor
  · refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
    · intro x hx
      simp [initial] at hx
    · intro x hx
      simp [initial] at hx
    · intro t ht
      simp [initial] at ht
    · simp [initial]
    · intro x hx
      simp [initial] at hx
    · intro r hr
      simp [initial] at hr
  · rfl

theorem register_allowed : Allowed proto initial (.register 0 ()) := by
  right
  refine ⟨rfl, by decide, ?_⟩
  constructor
  · simp [initial]
  · intro y hy
    have hn : y.val < 0 := hy
    omega

theorem verify_allowed : Allowed proto registered .verify := by
  right
  exact ⟨rfl, by decide, 0, ticket, rfl, rfl⟩

theorem actual_filter (o : Fin 3) : report proto registered o = verdict o := by
  fin_cases o <;> decide

theorem registered_channel : channel proto registered .verify = coarse := by
  change Filtered.reportChannel raw (report proto registered) = coarse
  have hf : report proto registered = verdict := funext actual_filter
  rw [hf, channel_is_coarse]

theorem passed_belief : passed.belief.prob true = 3/4 := by
  change (bayesUpdateTotal prior (channel proto registered .verify) true).prob true = _
  rw [registered_channel]
  exact coarse_success_posterior

theorem rejected_belief : rejected.belief.prob true = 1/4 := by
  change (bayesUpdateTotal prior (channel proto registered .verify) false).prob true = _
  rw [registered_channel]
  exact coarse_rejection_posterior

theorem checked_receipt : passed.checked = some receipt := by rfl

theorem verified_not_admitted : passed.completed = (∅ : Finset (Fin 1)) := rfl

theorem rejection_retains_exact_ticket : rejected.slot.pending = some ticket := rfl

theorem rejection_charged : rejected.budget = 1 ∧ rejected.spent = 2 := ⟨rfl,rfl⟩

theorem admit_precondition : Precondition proto passed .admit :=
  ⟨0, ticket, receipt, rfl, rfl, checked_receipt, by decide⟩

theorem admit_allowed : Allowed proto passed .admit := by
  exact Or.inr ⟨rfl, by decide, admit_precondition⟩

theorem final_completion : admitted.completed = ({0} : Finset (Fin 1)) := rfl

theorem final_budget : admitted.budget = 0 ∧ admitted.spent = 3 := ⟨rfl,rfl⟩

theorem final_safe : BudgetSafe proto 3 admitted := by
  have h1 := step_budgetSafe proto 3 initial initial_safe (.register 0 ()) register_allowed false
  have h2 := step_budgetSafe proto 3 registered h1 .verify verify_allowed true
  exact step_budgetSafe proto 3 passed h2 .admit admit_allowed false

theorem consumed_not_replayable : ¬ Allowed proto admitted .admit :=
  replay_admission_not_allowed proto passed admit_precondition

/-- Checking has a fee and supplies no immediate admission reward. -/
theorem no_receipt_one_step (s : State Bool (Fin 1)) (hr : s.checked = none) :
    Guarded.value (controller proto) 1 s = 0 := by
  apply stop_optimal proto 0 s
  intro a ha
  rw [Guarded.qValue_zero_eq_reward]
  change reward proto s a ≤ 0
  cases a with
  | register x c => simp [reward, fee, proto]
  | verify =>
    simp only [reward]
    exact sub_nonpos.mpr (Nat.cast_nonneg _)
  | admit =>
    obtain ⟨x,t,r,hx,ht,hc,hv⟩ := (ha.resolve_left (by intro h; cases h)).2.2
    rw [hr] at hc
    cases hc
  | stop => simp [reward, fee]

theorem rejected_one_step_value : Guarded.value (controller proto) 1 rejected = 0 :=
  no_receipt_one_step rejected rfl

theorem passed_admission_reward : reward proto passed .admit = 7 := by
  norm_num [reward, fee, proto, passed, verifyStep, charge, currentReceipt, registered,
    registerStep, initial, Binding.register, Binding.consume, validate, identity, artifact, context, Certificate.check, Certificate.infer]

theorem passed_one_step_value : Guarded.value (controller proto) 1 passed = 7 := by
  have ha := (mem_actions proto passed .admit).2 admit_allowed
  rw [Guarded.value_eq_q_of_optimal (controller proto) 0 passed .admit ha]
  · rw [Guarded.qValue_zero_eq_reward]
    exact passed_admission_reward
  · intro a h
    simp only [Guarded.qValue_zero_eq_reward]
    change reward proto passed a ≤ reward proto passed .admit
    have he := passed_admission_reward
    rw [he]
    cases a with
    | register x c => norm_num [reward, fee, proto]
    | verify => norm_num [reward, fee, passed, verifyStep, charge, registered, registerStep, initial, proto]
    | admit => rw [he]
    | stop => norm_num [reward, fee]

theorem verification_two_step_q : Guarded.qValue (controller proto) 1 registered .verify = 5/2 := by
  unfold Guarded.qValue
  have hr : (controller proto).reward registered .verify = -1 := by
    norm_num [controller, reward, fee, registered, registerStep, initial, proto, charge]
  rw [hr]
  change (-1 : ℚ) + (∑ d, predictiveProb prior (channel proto registered .verify) d *
    Guarded.value (controller proto) 1 (verifyStep proto registered d)) = _
  rw [registered_channel, Fintype.sum_bool]
  change -1 + (predictiveProb prior coarse true * Guarded.value (controller proto) 1 passed +
    predictiveProb prior coarse false * Guarded.value (controller proto) 1 rejected) = _
  rw [coarse_probability, coarse_probability, passed_one_step_value, rejected_one_step_value]
  norm_num

/-- Re-registering alone cannot earn an admission reward in the next step. -/
theorem register_two_step_q (s : State Bool (Fin 1)) (x : Fin 1) (c : Unit) :
    Guarded.qValue (controller proto) 1 s (.register x c) = -1 := by
  unfold Guarded.qValue
  have hr : (controller proto).reward s (.register x c) = -1 := by
    norm_num [controller, reward, fee, proto]
  rw [hr]
  change -1 + (∑ d, predictiveProb s.belief (channel proto s (.register x c)) d *
    Guarded.value (controller proto) 1 (registerStep proto s x c)) = _
  rw [no_receipt_one_step (registerStep proto s x c) rfl]
  simp

theorem registered_two_step_value : Guarded.value (controller proto) 2 registered = 5/2 := by
  rw [Guarded.value_eq_q_of_optimal (controller proto) 1 registered .verify
    ((mem_actions proto registered _).2 verify_allowed)]
  · exact verification_two_step_q
  · intro a ha
    rw [verification_two_step_q]
    cases a with
    | register x c => rw [register_two_step_q]; norm_num
    | verify => rw [verification_two_step_q]
    | admit =>
      obtain ⟨x,t,r,hx,ht,hr,hv⟩ := ((mem_actions proto registered _).1 ha).resolve_left
        (by intro h; cases h) |>.2.2
      change (none : Option Receipt) = some r at hr
      cases hr
    | stop => rw [stop_q_zero]; norm_num

theorem initial_three_step_q :
    Guarded.qValue (controller proto) 2 initial (.register 0 ()) = 3/2 := by
  unfold Guarded.qValue
  have hr : (controller proto).reward initial (.register 0 ()) = -1 := by
    norm_num [controller, reward, fee, proto]
  rw [hr]
  change -1 + (∑ d, predictiveProb prior (channel proto initial (.register 0 ())) d *
    Guarded.value (controller proto) 2 registered) = _
  rw [registered_two_step_value, ← Finset.sum_mul, predictiveProb_sum_one]
  norm_num

theorem initial_three_step_value : Guarded.value (controller proto) 3 initial = 3/2 := by
  rw [Guarded.value_eq_q_of_optimal (controller proto) 2 initial (.register 0 ())
    ((mem_actions proto initial _).2 register_allowed)]
  · exact initial_three_step_q
  · intro a ha
    rw [initial_three_step_q]
    cases a with
    | register x c =>
      have hx : x = 0 := Subsingleton.elim _ _
      cases hx
      cases c
      rw [initial_three_step_q]
    | verify =>
      obtain ⟨x,t,hx,ht⟩ := ((mem_actions proto initial _).1 ha).resolve_left
        (by intro h; cases h) |>.2.2
      change (none : Option (Fin 1)) = some x at hx
      cases hx
    | admit =>
      obtain ⟨x,t,r,hx,ht,hr,hv⟩ := ((mem_actions proto initial _).1 ha).resolve_left
        (by intro h; cases h) |>.2.2
      change (none : Option (Fin 1)) = some x at hx
      cases hx
    | stop => rw [stop_q_zero]; norm_num

theorem initial_source_safe : SourceSafe proto 3 initial := by
  refine ⟨initial_safe, ?_⟩
  intro t ht
  cases ht

end Komorebi.AVOC.ArtifactWorkflowExamples
