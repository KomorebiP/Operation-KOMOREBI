import AVOC.BayesianControl

namespace Komorebi.AVOC.Guarded

/-- Finite branching, state-dependent control. The state space need not be finite:
normalized rational Bayesian beliefs are an intended instance. -/
structure System (S A O : Type*) [DecidableEq A] [Fintype O] where
  actions : S → Finset A
  actions_nonempty : ∀ s, (actions s).Nonempty
  prob : S → A → O → ℚ
  prob_nonneg : ∀ s a o, 0 ≤ prob s a o
  prob_sum_one : ∀ s a, ∑ o, prob s a o = 1
  step : S → A → O → S
  reward : S → A → ℚ

variable {S A O : Type*} [DecidableEq A] [Fintype O]

/-- Expected continuation after a single admissible or hypothetical action. -/
def expectation (sys : System S A O) (W : S → ℚ) (s : S) (a : A) : ℚ :=
  ∑ o, sys.prob s a o * W (sys.step s a o)

theorem expectation_mono (sys : System S A O) {V W : S → ℚ}
    (h : ∀ s, V s ≤ W s) (s : S) (a : A) :
    expectation sys V s a ≤ expectation sys W s a := by
  apply Finset.sum_le_sum
  intro o _
  exact mul_le_mul_of_nonneg_left (h _) (sys.prob_nonneg s a o)

theorem expectation_const (sys : System S A O) (c : ℚ) (s : S) (a : A) :
    expectation sys (fun _ => c) s a = c := by
  unfold expectation
  rw [← Finset.sum_mul, sys.prob_sum_one]
  simp

/-- Bellman values with a new feasible action set at every state. -/
noncomputable def value (sys : System S A O) : ℕ → S → ℚ
  | 0, _ => 0
  | n + 1, s =>
    let vals := (sys.actions s).image
      (fun a => sys.reward s a + expectation sys (value sys n) s a)
    vals.max' ((sys.actions_nonempty s).image _)

noncomputable def qValue (sys : System S A O) (n : ℕ) (s : S) (a : A) : ℚ :=
  sys.reward s a + expectation sys (value sys n) s a

@[simp] theorem value_zero (sys : System S A O) (s : S) : value sys 0 s = 0 := rfl

theorem value_succ (sys : System S A O) (n : ℕ) (s : S) :
    value sys (n + 1) s =
      ((sys.actions s).image (qValue sys n s)).max'
        ((sys.actions_nonempty s).image _) := rfl

theorem optimal_action_exists (sys : System S A O) (n : ℕ) (s : S) :
    ∃ a ∈ sys.actions s, ∀ b ∈ sys.actions s,
      qValue sys n s b ≤ qValue sys n s a :=
  Finset.exists_max_image (sys.actions s) (qValue sys n s) (sys.actions_nonempty s)

theorem q_le_value (sys : System S A O) (n : ℕ) (s : S) (a : A)
    (ha : a ∈ sys.actions s) : qValue sys n s a ≤ value sys (n + 1) s := by
  rw [value_succ]
  exact Finset.le_max' _ _ (Finset.mem_image.mpr ⟨a, ha, rfl⟩)

theorem value_eq_q_of_optimal (sys : System S A O) (n : ℕ) (s : S) (a : A)
    (ha : a ∈ sys.actions s)
    (hm : ∀ b ∈ sys.actions s, qValue sys n s b ≤ qValue sys n s a) :
    value sys (n + 1) s = qValue sys n s a := by
  apply le_antisymm
  · rw [value_succ]
    apply Finset.max'_le
    intro y hy
    obtain ⟨b, hb, rfl⟩ := Finset.mem_image.mp hy
    exact hm b hb
  · exact q_le_value sys n s a ha

/-- This choice is a mathematical selector, not a claimed efficient planner. -/
noncomputable def optimalAction (sys : System S A O) (n : ℕ) (s : S) : A :=
  Classical.choose (optimal_action_exists sys n s)

theorem optimalAction_mem (sys : System S A O) (n : ℕ) (s : S) :
    optimalAction sys n s ∈ sys.actions s :=
  (Classical.choose_spec (optimal_action_exists sys n s)).1

theorem optimalAction_max (sys : System S A O) (n : ℕ) (s : S) :
    ∀ b ∈ sys.actions s, qValue sys n s b ≤ qValue sys n s (optimalAction sys n s) :=
  (Classical.choose_spec (optimal_action_exists sys n s)).2

theorem optimalAction_realizes (sys : System S A O) (n : ℕ) (s : S) :
    value sys (n + 1) s = qValue sys n s (optimalAction sys n s) :=
  value_eq_q_of_optimal sys n s _ (optimalAction_mem sys n s) (optimalAction_max sys n s)

@[simp] theorem qValue_zero_eq_reward (sys : System S A O) (s : S) (a : A) :
    qValue sys 0 s a = sys.reward s a := by
  simp [qValue, expectation, value]

/-- A complete adaptive observation tree. Different branches may choose entirely
different future actions, so competitors need not be Markov policies. -/
inductive Plan (A O : Type*) : ℕ → Type _ where
  | done : Plan A O 0
  | node {n : ℕ} (action : A) (next : O → Plan A O n) : Plan A O (n + 1)

/-- Legality is checked along every branch, including zero-mass branches. -/
def Legal (sys : System S A O) : {n : ℕ} → S → Plan A O n → Prop
  | 0, _, .done => True
  | _ + 1, s, .node a next =>
      a ∈ sys.actions s ∧ ∀ o, Legal sys (sys.step s a o) (next o)

def planValue (sys : System S A O) : {n : ℕ} → S → Plan A O n → ℚ
  | 0, _, .done => 0
  | _ + 1, s, .node a next =>
      sys.reward s a + ∑ o, sys.prob s a o * planValue sys (sys.step s a o) (next o)

theorem planValue_le_value (sys : System S A O) {n : ℕ} (s : S) (p : Plan A O n)
    (hp : Legal sys s p) : planValue sys s p ≤ value sys n s := by
  induction n generalizing s with
  | zero => cases p; exact le_rfl
  | succ n ih =>
    cases p with
    | node a next =>
      have he : (∑ o, sys.prob s a o * planValue sys (sys.step s a o) (next o)) ≤
          expectation sys (value sys n) s a := by
        apply Finset.sum_le_sum
        intro o _
        exact mul_le_mul_of_nonneg_left (ih _ _ (hp.2 o)) (sys.prob_nonneg s a o)
      have hv := q_le_value sys n s a hp.1
      unfold qValue at hv
      change sys.reward s a + (∑ o, sys.prob s a o *
        planValue sys (sys.step s a o) (next o)) ≤ value sys (n + 1) s
      linarith

/-- Unroll the horizon-dependent Markov maximizer into a complete adaptive plan. -/
noncomputable def optimalPlan (sys : System S A O) : (n : ℕ) → S → Plan A O n
  | 0, _ => .done
  | n + 1, s => .node (optimalAction sys n s)
      (fun o => optimalPlan sys n (sys.step s (optimalAction sys n s) o))

theorem optimalPlan_legal (sys : System S A O) (n : ℕ) (s : S) :
    Legal sys s (optimalPlan sys n s) := by
  induction n generalizing s with
  | zero => trivial
  | succ n ih => exact ⟨optimalAction_mem sys n s, fun o => ih _⟩

theorem optimalPlan_value (sys : System S A O) (n : ℕ) (s : S) :
    planValue sys s (optimalPlan sys n s) = value sys n s := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
    change sys.reward s (optimalAction sys n s) +
        (∑ o, sys.prob s (optimalAction sys n s) o *
          planValue sys (sys.step s (optimalAction sys n s) o)
            (optimalPlan sys n (sys.step s (optimalAction sys n s) o))) = _
    simp_rw [ih]
    exact (optimalAction_realizes sys n s).symm

/-- One-step invariant preservation. It is an obligation to prove for a concrete
protocol; it is not an axiom asserting that arbitrary external tools are safe. -/
def Preserves (sys : System S A O) (safe : S → Prop) : Prop :=
  ∀ s, safe s → ∀ a ∈ sys.actions s, ∀ o, safe (sys.step s a o)

def TreeSafe (sys : System S A O) (safe : S → Prop) :
    {n : ℕ} → S → Plan A O n → Prop
  | 0, s, .done => safe s
  | _ + 1, s, .node a next =>
      safe s ∧ ∀ o, TreeSafe sys safe (sys.step s a o) (next o)

theorem legal_plan_safe (sys : System S A O) (safe : S → Prop)
    (hpres : Preserves sys safe) {n : ℕ} (s : S) (p : Plan A O n)
    (hs : safe s) (hp : Legal sys s p) : TreeSafe sys safe s p := by
  induction n generalizing s with
  | zero => cases p; exact hs
  | succ n ih =>
    cases p with
    | node a next =>
      exact ⟨hs, fun o => ih _ _ (hpres s hs a hp.1 o) (hp.2 o)⟩

/-- Complete deterministic adaptive-policy optimality and safety, not just
existence of a maximizing next action. -/
theorem safe_optimal_plan_exists (sys : System S A O) (safe : S → Prop)
    (hpres : Preserves sys safe) (n : ℕ) (s : S) (hs : safe s) :
    ∃ p : Plan A O n,
      Legal sys s p ∧ TreeSafe sys safe s p ∧
      planValue sys s p = value sys n s ∧
      ∀ q : Plan A O n, Legal sys s q → planValue sys s q ≤ planValue sys s p := by
  refine ⟨optimalPlan sys n s, optimalPlan_legal sys n s,
    legal_plan_safe sys safe hpres s _ hs (optimalPlan_legal sys n s),
    optimalPlan_value sys n s, ?_⟩
  intro q hq
  rw [optimalPlan_value]
  exact planValue_le_value sys s q hq

/-- Randomizing among admissible first actions cannot beat their Bellman maximum.
This is a one-step statement, not a claim about constrained randomized policies. -/
theorem mixture_q_le_value (sys : System S A O) (n : ℕ) (s : S)
    (w : A → ℚ) (hw : ∀ a ∈ sys.actions s, 0 ≤ w a)
    (hunit : ∑ a ∈ sys.actions s, w a = 1) :
    (∑ a ∈ sys.actions s, w a * qValue sys n s a) ≤ value sys (n + 1) s := by
  calc
    (∑ a ∈ sys.actions s, w a * qValue sys n s a)
      ≤ ∑ a ∈ sys.actions s, w a * value sys (n + 1) s := by
        apply Finset.sum_le_sum
        intro a ha
        exact mul_le_mul_of_nonneg_left (q_le_value sys n s a ha) (hw a ha)
    _ = value sys (n + 1) s := by rw [← Finset.sum_mul, hunit]; simp

end Komorebi.AVOC.Guarded
