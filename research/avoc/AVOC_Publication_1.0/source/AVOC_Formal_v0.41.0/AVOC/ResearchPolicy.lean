import AVOC.ResearchController
import AVOC.GuardedPolicyRegret

namespace Komorebi.AVOC.Research

variable {Ω P C : Type*} [Fintype Ω] [Fintype C] [PartialOrder P]
  [DecidableEq P] {claim : P → Prop}

omit [DecidableEq P] in
theorem allowed_when_halted (p : Protocol Ω P C claim) (s : State Ω P)
    (hh : s.halted = true) (a : Action P) : Allowed p s a ↔ a = .stop := by
  cases a <;> simp [Allowed, hh]

theorem new_admission_has_rule (p : Protocol Ω P C claim) (s : State Ω P)
    (a : Action P) (ha : Allowed p s a) (o : Option C) (x : P)
    (hx : x ∈ (step p s a o).completed) (hfresh : x ∉ s.completed) :
    Scheduling.Ready s.completed x ∧ Scheduling.LocalRule claim x := by
  obtain ⟨heq, hg⟩ := new_completion_requires_verification p s a o x hx hfresh
  subst a
  exact ⟨ha.2.1, accepted_local_rule p x o hg⟩

theorem new_admission_is_true (p : Protocol Ω P C claim) (s : State Ω P)
    (hs : Safe claim s) (a : Action P) (ha : Allowed p s a) (o : Option C) (x : P)
    (hx : x ∈ (step p s a o).completed) : claim x :=
  (step_safe p s hs a ha o).2.1 x hx

/-- All halted states have zero continuation value: stopping is absorbing, not a
zero-cost wait that can silently resume a positive-value action later. -/
theorem halted_value_zero [Fintype P] (p : Protocol Ω P C claim) (n : ℕ)
    (s : State Ω P) (hh : s.halted = true) : Guarded.value (controller p) n s = 0 := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
      obtain ⟨a, ha, hm⟩ := Guarded.optimal_action_exists (controller p) n s
      have hstop : a = .stop :=
        (allowed_when_halted p s hh a).1 ((mem_actions p s a).1 ha)
      rw [Guarded.value_eq_q_of_optimal (controller p) n s a ha hm, hstop]
      change reward p s .stop + ∑ o, probability p s .stop o *
        Guarded.value (controller p) n (step p s .stop o) = 0
      have hz : ∀ o, Guarded.value (controller p) n (step p s .stop o) = 0 :=
        fun o => ih _ rfl
      simp_rw [hz]
      simp [reward, hh]

theorem stop_q_zero [Fintype P] (p : Protocol Ω P C claim) (n : ℕ) (s : State Ω P) :
    Guarded.qValue (controller p) n s .stop = 0 := by
  change reward p s .stop + ∑ o, probability p s .stop o *
    Guarded.value (controller p) n (step p s .stop o) = 0
  have hz : ∀ o, Guarded.value (controller p) n (step p s .stop o) = 0 :=
    fun o => halted_value_zero p n _ rfl
  simp_rw [hz]
  simp [reward]

theorem controller_value_nonneg [Fintype P] (p : Protocol Ω P C claim)
    (n : ℕ) (s : State Ω P) : 0 ≤ Guarded.value (controller p) n s := by
  cases n with
  | zero => exact le_rfl
  | succ n =>
      have h := Guarded.q_le_value (controller p) n s .stop
        ((mem_actions p s .stop).2 trivial)
      rw [stop_q_zero] at h
      exact h

/-- The stopping criterion compares full Bellman continuation values, not just
immediate rewards. It therefore does not discard valuable delayed investment. -/
theorem stop_optimal_of_nonpositive_q [Fintype P] (p : Protocol Ω P C claim)
    (n : ℕ) (s : State Ω P)
    (h : ∀ a, Allowed p s a → Guarded.qValue (controller p) n s a ≤ 0) :
    Guarded.value (controller p) (n + 1) s = 0 := by
  rw [Guarded.value_eq_q_of_optimal (controller p) n s .stop
    ((mem_actions p s .stop).2 trivial)]
  · exact stop_q_zero p n s
  · intro a ha
    rw [stop_q_zero]
    exact h a ((mem_actions p s a).1 ha)

/-- A finite realized action/observation transcript. -/
noncomputable def execute (p : Protocol Ω P C claim) :
    State Ω P → List (Action P × Option C) → State Ω P
  | s, [] => s
  | s, (a, o) :: xs => execute p (step p s a o) xs

def TraceLegal (p : Protocol Ω P C claim) :
    State Ω P → List (Action P × Option C) → Prop
  | _, [] => True
  | s, (a, o) :: xs => Allowed p s a ∧ TraceLegal p (step p s a o) xs

theorem legal_trace_preserves (p : Protocol Ω P C claim) (B : ℕ)
    (s : State Ω P) (xs : List (Action P × Option C))
    (hs : BudgetSafe claim B s) (hl : TraceLegal p s xs) :
    BudgetSafe claim B (execute p s xs) := by
  induction xs generalizing s with
  | nil => exact hs
  | cons pair xs ih =>
      rcases pair with ⟨a, o⟩
      exact ih _ (step_budgetSafe p B s hs a hl.1 o) hl.2

theorem legal_trace_certifies (p : Protocol Ω P C claim) (B : ℕ)
    (s : State Ω P) (xs : List (Action P × Option C))
    (hs : BudgetSafe claim B s) (hl : TraceLegal p s xs) :
    ∀ x ∈ (execute p s xs).completed, claim x :=
  (legal_trace_preserves p B s xs hs hl).1.2.1

theorem legal_trace_no_overspend (p : Protocol Ω P C claim) (B : ℕ)
    (s : State Ω P) (xs : List (Action P × Option C))
    (hs : BudgetSafe claim B s) (hl : TraceLegal p s xs) :
    (execute p s xs).spent ≤ B := by
  have h := (legal_trace_preserves p B s xs hs hl).2
  omega

/-- Actual expenditure is the sum of the declared fees of the chosen actions. -/
theorem execute_spent (p : Protocol Ω P C claim) (s : State Ω P)
    (xs : List (Action P × Option C)) :
    (execute p s xs).spent = s.spent + (xs.map (fun z => fee p z.1)).sum := by
  induction xs generalizing s with
  | nil => simp [execute]
  | cons pair xs ih =>
      rcases pair with ⟨a, o⟩
      simp only [execute, ih, step_spent_increment, List.map_cons, List.sum_cons]
      omega

theorem legal_trace_fee_bound (p : Protocol Ω P C claim) (s : State Ω P)
    (xs : List (Action P × Option C)) (hs : Safe claim s) (hl : TraceLegal p s xs) :
    (xs.map (fun z => fee p z.1)).sum ≤ s.budget := by
  have h := legal_trace_no_overspend p (s.budget + s.spent) s xs ⟨hs, rfl⟩ hl
  rw [execute_spent] at h
  omega

/-- Main approximation corollary for the actual Bayesian proof controller.
Estimation and optimization errors affect performance; admissibility and gate
soundness separately guarantee truth preservation and pathwise budget safety. -/
theorem certified_approximate_policy [Fintype P] (p : Protocol Ω P C claim)
    (choose : ℕ → State Ω P → Action P)
    (estimate : ℕ → State Ω P → Action P → ℚ) (eta tau : ℕ → ℚ)
    (ha : ∀ n s, Allowed p s (choose n s))
    (he : ∀ n s a, Allowed p s a →
      |Guarded.qValue (controller p) n s a - estimate n s a| ≤ eta n)
    (hm : ∀ n s a, Allowed p s a →
      estimate n s a ≤ estimate n s (choose n s) + tau n)
    (B n : ℕ) (s : State Ω P) (hs : BudgetSafe claim B s) :
    Guarded.TreeSafe (controller p) (BudgetSafe claim B) s
      (Guarded.policyPlan (controller p) choose n s) ∧
    0 ≤ Guarded.value (controller p) n s -
      Guarded.planValue (controller p) s (Guarded.policyPlan (controller p) choose n s) ∧
    Guarded.value (controller p) n s -
      Guarded.planValue (controller p) s (Guarded.policyPlan (controller p) choose n s) ≤
      Guarded.regretBudget (fun k => 2 * eta k + tau k) n := by
  have hf : ∀ n s, choose n s ∈ (controller p).actions s :=
    fun n s => (mem_actions p s _).2 (ha n s)
  refine ⟨Guarded.admissible_approximate_policy_safe (controller p) (BudgetSafe claim B)
    (controller_budget_preserves p B) choose hf n s hs, ?_⟩
  exact Guarded.decoded_policy_regret (controller p) choose estimate eta tau hf
    (fun n s a h => he n s a ((mem_actions p s a).1 h))
    (fun n s a h => hm n s a ((mem_actions p s a).1 h)) n s

end Komorebi.AVOC.Research
