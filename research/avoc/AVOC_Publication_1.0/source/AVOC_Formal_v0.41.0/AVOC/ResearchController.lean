import AVOC.GuardedControl
import AVOC.SchedulingCertificates
import Mathlib.Data.Fintype.Option

namespace Komorebi.AVOC.Research

/-- An attempted proof is not an admission. Verification is a separate action. -/
inductive Action (P : Type*) where
  | stop
  | attempt (task : P)
  | verify (task : P)
  deriving DecidableEq, Repr

/-- A Bayesian research state with a concrete dependency ledger, pending queue,
remaining resource budget, cumulative spend, and an absorbing stop flag. -/
structure State (Ω P : Type*) [Fintype Ω] where
  belief : RationalBelief Ω
  completed : Finset P
  pending : Finset P
  budget : ℕ
  spent : ℕ
  halted : Bool

/-- A gate checks finite receipt identifiers. Its soundness must be supplied as an
actual Lean proof of the local rule, not as a string/Boolean status assertion.
The experiment may depend on the full current research state. -/
structure Protocol (Ω P C : Type*) [Fintype Ω] [Fintype C] [PartialOrder P]
    (claim : P → Prop) where
  attemptFee : P → ℕ
  verifyFee : P → ℕ
  check : P → C → Bool
  check_sound : ∀ x c, check x c = true → Scheduling.LocalRule claim x
  experiment : State Ω P → Action P → RationalChannel Ω (Option C)
  admissionValue : P → ℚ
  congestion : ℕ → ℚ

variable {Ω P C : Type*} [Fintype Ω] [Fintype C] [PartialOrder P]
  [DecidableEq P] {claim : P → Prop}

def fee (p : Protocol Ω P C claim) : Action P → ℕ
  | .stop => 0
  | .attempt x => p.attemptFee x
  | .verify x => p.verifyFee x

def accepted (p : Protocol Ω P C claim) (x : P) : Option C → Bool
  | none => false
  | some c => p.check x c

omit [DecidableEq P] in
theorem accepted_local_rule (p : Protocol Ω P C claim) (x : P) (o : Option C)
    (h : accepted p x o = true) : Scheduling.LocalRule claim x := by
  cases o with
  | none => simp [accepted] at h
  | some c => exact p.check_sound x c h

/-- Fixed dependency closure, actual certified truth, and only ready pending tasks. -/
def Safe (claim : P → Prop) (s : State Ω P) : Prop :=
  Scheduling.IsIdeal s.completed ∧ Scheduling.Certified claim s.completed ∧
    ∀ x ∈ s.pending, Scheduling.Ready s.completed x

/-- The only action always available is stopping. A pending result still needs
readiness and a passing sound receipt before it can become a completed theorem. -/
def Allowed (p : Protocol Ω P C claim) (s : State Ω P) : Action P → Prop
  | .stop => True
  | .attempt x => s.halted = false ∧ Scheduling.Ready s.completed x ∧
      x ∉ s.pending ∧ p.attemptFee x ≤ s.budget
  | .verify x => s.halted = false ∧ Scheduling.Ready s.completed x ∧
      x ∈ s.pending ∧ p.verifyFee x ≤ s.budget

noncomputable def actions [Fintype P] (p : Protocol Ω P C claim) (s : State Ω P) :
    Finset (Action P) := by
  classical
  exact (insert .stop ((Finset.univ.image Action.attempt) ∪
    (Finset.univ.image Action.verify))).filter (Allowed p s)

@[simp] theorem mem_actions [Fintype P] (p : Protocol Ω P C claim)
    (s : State Ω P) (a : Action P) : a ∈ actions p s ↔ Allowed p s a := by
  classical
  have hall : a ∈ insert Action.stop ((Finset.univ.image Action.attempt) ∪
      (Finset.univ.image Action.verify)) := by
    cases a <;> simp
  simp only [actions, Finset.mem_filter]
  exact ⟨And.right, fun h => ⟨hall, h⟩⟩

omit [DecidableEq P] in
theorem stop_allowed (p : Protocol Ω P C claim) (s : State Ω P) :
    Allowed p s .stop := trivial

theorem actions_nonempty [Fintype P] (p : Protocol Ω P C claim) (s : State Ω P) :
    (actions p s).Nonempty := ⟨.stop, (mem_actions p s .stop).2 trivial⟩

omit [DecidableEq P] in
theorem allowed_fee_le (p : Protocol Ω P C claim) (s : State Ω P) (a : Action P)
    (ha : Allowed p s a) : fee p a ≤ s.budget := by
  cases a with
  | stop => exact Nat.zero_le _
  | attempt x => exact ha.2.2.2
  | verify x => exact ha.2.2.2

/-- Total transition, with safety required only for allowed inputs. Even a passing
receipt received during `attempt` cannot upgrade the completion ledger. -/
noncomputable def step (p : Protocol Ω P C claim) (s : State Ω P)
    (a : Action P) (o : Option C) : State Ω P :=
  match a with
  | .stop => {s with halted := true}
  | .attempt x =>
      {s with belief := bayesUpdateTotal s.belief (p.experiment s a) o
              pending := insert x s.pending
              budget := s.budget - p.attemptFee x
              spent := s.spent + p.attemptFee x}
  | .verify x =>
      {s with belief := bayesUpdateTotal s.belief (p.experiment s a) o
              completed := if accepted p x o = true then insert x s.completed else s.completed
              pending := s.pending.erase x
              budget := s.budget - p.verifyFee x
              spent := s.spent + p.verifyFee x}

@[simp] theorem attempt_completed_unchanged (p : Protocol Ω P C claim)
    (s : State Ω P) (x : P) (o : Option C) :
    (step p s (.attempt x) o).completed = s.completed := rfl

@[simp] theorem attempt_queues (p : Protocol Ω P C claim)
    (s : State Ω P) (x : P) (o : Option C) :
    (step p s (.attempt x) o).pending = insert x s.pending := rfl

theorem rejected_completed_unchanged (p : Protocol Ω P C claim)
    (s : State Ω P) (x : P) (o : Option C) (hg : accepted p x o ≠ true) :
    (step p s (.verify x) o).completed = s.completed := by simp [step, hg]

theorem passing_receipt_admits (p : Protocol Ω P C claim)
    (s : State Ω P) (x : P) (o : Option C) (hg : accepted p x o = true) :
    (step p s (.verify x) o).completed = insert x s.completed := by simp [step, hg]

/-- No theorem can enter this ledger except through a verification action with
a passing receipt. This is an exact converse, not just a one-way safety rule. -/
theorem new_completion_requires_verification (p : Protocol Ω P C claim)
    (s : State Ω P) (a : Action P) (o : Option C) (x : P)
    (hx : x ∈ (step p s a o).completed) (hfresh : x ∉ s.completed) :
    a = .verify x ∧ accepted p x o = true := by
  cases a with
  | stop => exact False.elim (hfresh hx)
  | attempt y => exact False.elim (hfresh hx)
  | verify y =>
      by_cases hg : accepted p y o = true
      · simp only [step, ite_eq_left hg, Finset.mem_insert] at hx
        rcases hx with heq | hx
        · subst x
          exact ⟨rfl, hg⟩
        · exact False.elim (hfresh hx)
      · have heq := rejected_completed_unchanged p s y o hg
        rw [heq] at hx
        exact False.elim (hfresh hx)

/-- The certificate/queue/ideal invariant holds even on impossible observations.
Bayesian fallback on zero predictive mass cannot fabricate a certificate. -/
theorem step_safe (p : Protocol Ω P C claim) (s : State Ω P)
    (hs : Safe claim s) (a : Action P) (ha : Allowed p s a) (o : Option C) :
    Safe claim (step p s a o) := by
  rcases hs with ⟨hi, hc, hp⟩
  cases a with
  | stop => exact ⟨hi, hc, hp⟩
  | attempt x =>
      refine ⟨hi, hc, ?_⟩
      intro y hy
      change y ∈ insert x s.pending at hy
      rcases Finset.mem_insert.mp hy with heq | hy
      · subst y; exact ha.2.1
      · exact hp y hy
  | verify x =>
      by_cases hg : accepted p x o = true
      · have hnew := Scheduling.checked_step_preserves hi hc ha.2.1
          (accepted_local_rule p x o hg)
        refine ⟨?_, ?_, ?_⟩
        · simpa only [step, ite_eq_left hg] using hnew.1
        · simpa only [step, ite_eq_left hg] using hnew.2
        · intro y hy
          change y ∈ s.pending.erase x at hy
          obtain ⟨hne, hym⟩ := Finset.mem_erase.mp hy
          simpa only [step, ite_eq_left hg] using
            (Scheduling.ready_persists (hp y hym) hne)
      · refine ⟨?_, ?_, ?_⟩
        · simpa only [step, ite_eq_right hg] using hi
        · simpa only [step, ite_eq_right hg] using hc
        · intro y hy
          change y ∈ s.pending.erase x at hy
          simpa only [step, ite_eq_right hg] using (hp y (Finset.mem_of_mem_erase hy))

/-- Resource accounting is exact for allowed actions. Natural subtraction cannot
silently hide an overspend because feasibility supplies the needed inequality. -/
theorem step_budget_accounting (p : Protocol Ω P C claim) (s : State Ω P)
    (a : Action P) (ha : Allowed p s a) (o : Option C) :
    (step p s a o).budget + (step p s a o).spent = s.budget + s.spent := by
  have hf := allowed_fee_le p s a ha
  cases a <;> simp only [step, fee] at * <;> omega

theorem step_budget_le (p : Protocol Ω P C claim) (s : State Ω P)
    (a : Action P) (o : Option C) : (step p s a o).budget ≤ s.budget := by
  cases a <;> simp only [step] <;> omega

theorem step_spent_increment (p : Protocol Ω P C claim) (s : State Ω P)
    (a : Action P) (o : Option C) :
    (step p s a o).spent = s.spent + fee p a := by cases a <;> simp [step, fee]

def BudgetSafe (claim : P → Prop) (B : ℕ) (s : State Ω P) : Prop :=
  Safe claim s ∧ s.budget + s.spent = B

theorem step_budgetSafe (p : Protocol Ω P C claim) (B : ℕ) (s : State Ω P)
    (hs : BudgetSafe claim B s) (a : Action P) (ha : Allowed p s a) (o : Option C) :
    BudgetSafe claim B (step p s a o) :=
  ⟨step_safe p s hs.1 a ha o, (step_budget_accounting p s a ha o).trans hs.2⟩

/-- Predictive observation probabilities are drawn from the certified Bayesian
belief, even when the experiment depends on the queue, budget, or completed set. -/
def probability (p : Protocol Ω P C claim) (s : State Ω P)
    (a : Action P) (o : Option C) : ℚ := predictiveProb s.belief (p.experiment s a) o

/-- Reward counts admission benefits only on passing verification branches;
attempts have no completion reward. Resource units and rational utility are a
declared modeling convention, not measured real-world costs. -/
def reward (p : Protocol Ω P C claim) (s : State Ω P) (a : Action P) : ℚ :=
  if s.halted = true then 0 else
    match a with
    | .stop => 0
    | .attempt x => -(p.attemptFee x : ℚ) - p.congestion s.pending.card
    | .verify x => -(p.verifyFee x : ℚ) - p.congestion s.pending.card +
        ∑ o, probability p s a o *
          (if accepted p x o = true then p.admissionValue x else 0)

/-- The actual link to the state-dependent Bellman system. -/
noncomputable def controller [Fintype P] (p : Protocol Ω P C claim) :
    Guarded.System (State Ω P) (Action P) (Option C) where
  actions := actions p
  actions_nonempty := actions_nonempty p
  prob := probability p
  prob_nonneg s a o := predictiveProb_nonneg s.belief (p.experiment s a) o
  prob_sum_one s a := predictiveProb_sum_one s.belief (p.experiment s a)
  step := step p
  reward := reward p

theorem controller_preserves [Fintype P] (p : Protocol Ω P C claim) :
    Guarded.Preserves (controller p) (Safe claim) := by
  intro s hs a ha o
  exact step_safe p s hs a ((mem_actions p s a).1 ha) o

theorem controller_budget_preserves [Fintype P] (p : Protocol Ω P C claim) (B : ℕ) :
    Guarded.Preserves (controller p) (BudgetSafe claim B) := by
  intro s hs a ha o
  exact step_budgetSafe p B s hs a ((mem_actions p s a).1 ha) o

/-- Main integration theorem: there exists a globally optimal deterministic
adaptive finite-horizon plan, feasible at every branch, preserving certified
truth, dependency closure, pending readiness, and the entire resource budget. -/
theorem certified_budget_optimal_plan_exists [Fintype P]
    (p : Protocol Ω P C claim) (B n : ℕ) (s : State Ω P)
    (hs : BudgetSafe claim B s) :
    ∃ plan : Guarded.Plan (Action P) (Option C) n,
      Guarded.Legal (controller p) s plan ∧
      Guarded.TreeSafe (controller p) (BudgetSafe claim B) s plan ∧
      Guarded.planValue (controller p) s plan = Guarded.value (controller p) n s ∧
      ∀ other : Guarded.Plan (Action P) (Option C) n,
        Guarded.Legal (controller p) s other →
        Guarded.planValue (controller p) s other ≤ Guarded.planValue (controller p) s plan :=
  Guarded.safe_optimal_plan_exists (controller p) (BudgetSafe claim B)
    (controller_budget_preserves p B) n s hs

end Komorebi.AVOC.Research
