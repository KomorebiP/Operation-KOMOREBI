import AVOC.ResearchPolicy
import AVOC.BayesianExamples
import Mathlib.Tactic.NormNum

namespace Komorebi.AVOC.Research.Examples

/-- The hidden Boolean describes whether the tool yields a useful valid receipt,
not whether the task proposition is true. The task itself is the proposition True. -/
def signal : Bool → Option Unit
  | false => none
  | true => some ()

def receiptChannel : RationalChannel Bool (Option Unit) where
  prob w o := if o = signal w then 1 else 0
  nonneg := by intro w o; split <;> norm_num
  sum_one := by intro w; simp

def demo : Protocol Bool (Fin 1) Unit (fun _ => True) where
  attemptFee _ := 1
  verifyFee _ := 1
  check _ _ := true
  check_sound := by intro x c h deps; trivial
  experiment _ _ := receiptChannel
  admissionValue _ := 6
  congestion _ := 0

def initial : State Bool (Fin 1) where
  belief := uniformBoolBelief
  completed := ∅
  pending := ∅
  budget := 2
  spent := 0
  halted := false

theorem one_ready : Scheduling.Ready (∅ : Finset (Fin 1)) 0 := by
  refine ⟨by simp, ?_⟩
  intro y hy
  have hlt : y.val < 0 := hy
  omega

theorem initial_safe : BudgetSafe (fun _ : Fin 1 => True) 2 initial := by
  refine ⟨⟨Scheduling.ideal_empty, ?_, ?_⟩, rfl⟩
  · intro x _; trivial
  · intro x hx; simp [initial] at hx

theorem initial_attempt_allowed : Allowed demo initial (.attempt 0) :=
  ⟨rfl, one_ready, by simp [initial], by decide⟩

theorem initial_verify_forbidden : ¬ Allowed demo initial (.verify 0) := by
  intro h
  simpa [initial] using h.2.2.1

theorem predictive_some (b : RationalBelief Bool) :
    predictiveProb b receiptChannel (some ()) = b.prob true := by
  unfold predictiveProb
  rw [Fintype.sum_bool]
  simp [receiptChannel, signal]

theorem predictive_none (b : RationalBelief Bool) :
    predictiveProb b receiptChannel none = b.prob false := by
  unfold predictiveProb
  rw [Fintype.sum_bool]
  simp [receiptChannel, signal]

theorem initial_some_positive : 0 < predictiveProb uniformBoolBelief receiptChannel (some ()) := by
  rw [predictive_some]
  norm_num [uniformBoolBelief]

noncomputable def afterSignal : State Bool (Fin 1) := step demo initial (.attempt 0) (some ())

theorem afterSignal_belief_true : afterSignal.belief.prob true = 1 := by
  change (bayesUpdateTotal uniformBoolBelief receiptChannel (some ())).prob true = 1
  rw [bayesUpdateTotal_eq_of_pos _ _ _ initial_some_positive]
  have h := bayesUpdate_mul_predictive uniformBoolBelief receiptChannel (some ())
    initial_some_positive true
  rw [predictive_some] at h
  norm_num [uniformBoolBelief, receiptChannel, signal] at h
  exact h

/-- Even posterior probability one and a valid receipt in an attempt observation
do not bypass the separate verification action. -/
theorem posterior_one_is_not_admission :
    afterSignal.belief.prob true = 1 ∧ afterSignal.completed = ∅ :=
  ⟨afterSignal_belief_true, rfl⟩

theorem afterSignal_verify_allowed : Allowed demo afterSignal (.verify 0) := by
  refine ⟨rfl, one_ready, ?_, ?_⟩
  · simp [afterSignal, step, initial]
  · decide

theorem successful_verification_completes :
    (step demo afterSignal (.verify 0) (some ())).completed = {0} := by
  rw [passing_receipt_admits demo afterSignal 0 (some ()) rfl]
  rfl

theorem failed_verification_does_not_complete :
    (step demo afterSignal (.verify 0) none).completed = ∅ := by
  rw [rejected_completed_unchanged demo afterSignal 0 none (by decide)]
  rfl

theorem successful_spend_exact :
    (step demo afterSignal (.verify 0) (some ())).budget = 0 ∧
    (step demo afterSignal (.verify 0) (some ())).spent = 2 := ⟨rfl, rfl⟩

theorem exhausted_attempt_forbidden :
    ¬ Allowed demo {initial with budget := 0} (.attempt 0) := by
  intro h
  have hc : 1 ≤ 0 := h.2.2.2
  omega

/-- A two-stage adaptive strategy: stop after an unproductive signal, otherwise
pay for verification. This makes the role of the Bayesian observation nontrivial. -/
def adaptivePlan : Guarded.Plan (Action (Fin 1)) (Option Unit) 2 :=
  .node (.attempt 0) (fun o =>
    match o with
    | none => .node .stop (fun _ => .done)
    | some _ => .node (.verify 0) (fun _ => .done))

theorem adaptivePlan_legal : Guarded.Legal (controller demo) initial adaptivePlan := by
  refine ⟨(mem_actions demo initial _).2 initial_attempt_allowed, ?_⟩
  intro o
  cases o with
  | none => exact ⟨(mem_actions demo _ _).2 trivial, fun _ => trivial⟩
  | some c =>
    cases c
    exact ⟨(mem_actions demo _ _).2 afterSignal_verify_allowed, fun _ => trivial⟩

theorem reward_verify_formula (s : State Bool (Fin 1)) (hh : s.halted = false) :
    reward demo s (.verify 0) = -1 + 6 * s.belief.prob true := by
  simp [reward, hh, demo, accepted, probability, predictiveProb,
    Fintype.sum_option, receiptChannel, signal]
  ring

theorem reward_afterSignal_verify : reward demo afterSignal (.verify 0) = 5 := by
  rw [reward_verify_formula afterSignal rfl, afterSignal_belief_true]
  norm_num

theorem adaptivePlan_value : Guarded.planValue (controller demo) initial adaptivePlan = 3 / 2 := by
  change reward demo initial (.attempt 0) +
    ∑ o, probability demo initial (.attempt 0) o *
      Guarded.planValue (controller demo) (step demo initial (.attempt 0) o)
        (match o with
         | none => Guarded.Plan.node .stop (fun _ => Guarded.Plan.done)
         | some _ => Guarded.Plan.node (.verify 0) (fun _ => Guarded.Plan.done)) = 3 / 2
  rw [Fintype.sum_option]
  simp only [Guarded.planValue, mul_zero, Finset.sum_const_zero, add_zero,
    Fintype.sum_unique]
  change reward demo initial (.attempt 0) +
    (probability demo initial (.attempt 0) none *
       reward demo (step demo initial (.attempt 0) none) .stop +
     probability demo initial (.attempt 0) (some ()) * reward demo afterSignal (.verify 0)) = 3 / 2
  have hprob : probability demo initial (.attempt 0) (some ()) = 1 / 2 := by
    change predictiveProb uniformBoolBelief receiptChannel (some ()) = 1 / 2
    rw [predictive_some]
    rfl
  have hstop : reward demo (step demo initial (.attempt 0) none) .stop = 0 := by
    simp [reward]
  have hcost : reward demo initial (.attempt 0) = -1 := by
    norm_num [reward, demo, initial]
  rw [reward_afterSignal_verify, hprob, hstop, hcost]
  norm_num

theorem two_step_value_positive : 0 < Guarded.value (controller demo) 2 initial := by
  have h := Guarded.planValue_le_value (controller demo) initial adaptivePlan adaptivePlan_legal
  rw [adaptivePlan_value] at h
  linarith

theorem adaptivePlan_safe :
    Guarded.TreeSafe (controller demo) (BudgetSafe (fun _ : Fin 1 => True) 2)
      initial adaptivePlan :=
  Guarded.legal_plan_safe (controller demo) _ (controller_budget_preserves demo 2)
    initial adaptivePlan initial_safe adaptivePlan_legal


theorem one_step_value_zero : Guarded.value (controller demo) 1 initial = 0 := by
  apply stop_optimal_of_nonpositive_q
  intro a ha
  cases a with
  | stop => rw [stop_q_zero]
  | attempt x =>
      rw [Guarded.qValue_zero_eq_reward]
      change reward demo initial (.attempt x) ≤ 0
      norm_num [reward, demo, initial]
  | verify x =>
      have hx : x = (0 : Fin 1) := Subsingleton.elim _ _
      subst x
      exact False.elim (initial_verify_forbidden ha)

noncomputable def afterNoSignal : State Bool (Fin 1) := step demo initial (.attempt 0) none

theorem afterNoSignal_belief_true : afterNoSignal.belief.prob true = 0 := by
  have hpos : 0 < predictiveProb uniformBoolBelief receiptChannel none := by
    rw [predictive_none]
    norm_num [uniformBoolBelief]
  change (bayesUpdateTotal uniformBoolBelief receiptChannel none).prob true = 0
  rw [bayesUpdateTotal_eq_of_pos _ _ _ hpos]
  have h := bayesUpdate_mul_predictive uniformBoolBelief receiptChannel none hpos true
  rw [predictive_none] at h
  have hrhs : uniformBoolBelief.prob true * receiptChannel.prob true none = 0 := by
    have hzero : receiptChannel.prob true none = 0 := by decide
    rw [hzero]
    simp
  rw [hrhs] at h
  change (bayesUpdate uniformBoolBelief receiptChannel none hpos).prob true * (1/2) = 0 at h
  linarith

theorem repeated_attempt_forbidden (o : Option Unit) (x : Fin 1) :
    ¬ Allowed demo (step demo initial (.attempt 0) o) (.attempt x) := by
  intro h
  have hx : x = (0 : Fin 1) := Subsingleton.elim _ _
  subst x
  exact h.2.2.1 (by simp [step])

theorem afterSignal_one_step_value : Guarded.value (controller demo) 1 afterSignal = 5 := by
  have heq := Guarded.value_eq_q_of_optimal (controller demo) 0 afterSignal (.verify 0)
    ((mem_actions demo afterSignal _).2 afterSignal_verify_allowed)
  have hm : ∀ a ∈ (controller demo).actions afterSignal,
      Guarded.qValue (controller demo) 0 afterSignal a ≤
        Guarded.qValue (controller demo) 0 afterSignal (.verify 0) := by
    intro a ha
    have hal := (mem_actions demo afterSignal a).1 ha
    cases a with
    | stop =>
        rw [stop_q_zero, Guarded.qValue_zero_eq_reward]
        change 0 ≤ reward demo afterSignal (.verify 0)
        rw [reward_afterSignal_verify]; norm_num
    | attempt x => exact False.elim (repeated_attempt_forbidden (some ()) x hal)
    | verify x =>
        have hx : x = (0 : Fin 1) := Subsingleton.elim _ _
        subst x; exact le_rfl
  rw [heq hm, Guarded.qValue_zero_eq_reward]
  exact reward_afterSignal_verify

theorem afterNoSignal_one_step_value : Guarded.value (controller demo) 1 afterNoSignal = 0 := by
  apply stop_optimal_of_nonpositive_q
  intro a ha
  cases a with
  | stop => rw [stop_q_zero]
  | attempt x => exact False.elim (repeated_attempt_forbidden none x ha)
  | verify x =>
      have hx : x = (0 : Fin 1) := Subsingleton.elim _ _
      subst x
      rw [Guarded.qValue_zero_eq_reward]
      change reward demo afterNoSignal (.verify 0) ≤ 0
      rw [reward_verify_formula afterNoSignal rfl, afterNoSignal_belief_true]
      norm_num

theorem initial_attempt_two_step_q : Guarded.qValue (controller demo) 1 initial (.attempt 0) = 3/2 := by
  change reward demo initial (.attempt 0) + ∑ o, probability demo initial (.attempt 0) o *
    Guarded.value (controller demo) 1 (step demo initial (.attempt 0) o) = 3/2
  rw [Fintype.sum_option]
  simp only [Fintype.sum_unique]
  change reward demo initial (.attempt 0) +
    (probability demo initial (.attempt 0) none * Guarded.value (controller demo) 1 afterNoSignal +
     probability demo initial (.attempt 0) (some ()) * Guarded.value (controller demo) 1 afterSignal) = 3/2
  rw [afterSignal_one_step_value, afterNoSignal_one_step_value]
  have hprob : probability demo initial (.attempt 0) (some ()) = 1/2 := by
    change predictiveProb uniformBoolBelief receiptChannel (some ()) = 1/2
    rw [predictive_some]; rfl
  rw [hprob]
  norm_num [reward, demo, initial]

theorem two_step_value_exact : Guarded.value (controller demo) 2 initial = 3/2 := by
  have heq := Guarded.value_eq_q_of_optimal (controller demo) 1 initial (.attempt 0)
    ((mem_actions demo initial _).2 initial_attempt_allowed)
  have hm : ∀ a ∈ (controller demo).actions initial,
      Guarded.qValue (controller demo) 1 initial a ≤
        Guarded.qValue (controller demo) 1 initial (.attempt 0) := by
    intro a ha
    have hal := (mem_actions demo initial a).1 ha
    cases a with
    | stop => rw [stop_q_zero, initial_attempt_two_step_q]; norm_num
    | attempt x =>
        have hx : x = (0 : Fin 1) := Subsingleton.elim _ _
        subst x; exact le_rfl
    | verify x =>
        have hx : x = (0 : Fin 1) := Subsingleton.elim _ _
        subst x; exact False.elim (initial_verify_forbidden hal)
  rw [heq hm, initial_attempt_two_step_q]


/-- A protocol cannot supply a sound always-passing receipt for a false root task. -/
theorem false_root_rule_impossible :
    ¬ Scheduling.LocalRule (fun _ : Fin 1 => False) 0 := by
  intro h
  apply h
  intro y hy
  have hlt : y.val < 0 := hy
  omega

theorem false_root_gate_cannot_pass
    (p : Protocol Bool (Fin 1) Unit (fun _ => False)) : p.check 0 () ≠ true := by
  intro h
  exact false_root_rule_impossible (p.check_sound 0 () h)

end Komorebi.AVOC.Research.Examples
