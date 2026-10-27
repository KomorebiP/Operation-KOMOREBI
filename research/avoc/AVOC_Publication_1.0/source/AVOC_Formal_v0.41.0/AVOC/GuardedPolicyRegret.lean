import AVOC.GuardedControl

namespace Komorebi.AVOC.Guarded

variable {S A O : Type*} [DecidableEq A] [Fintype O]

def regretBudget (err : ℕ → ℚ) (n : ℕ) : ℚ := ∑ k ∈ Finset.range n, err k

@[simp] theorem regretBudget_zero (err : ℕ → ℚ) : regretBudget err 0 = 0 := by
  simp [regretBudget]

theorem regretBudget_succ (err : ℕ → ℚ) (n : ℕ) :
    regretBudget err (n + 1) = regretBudget err n + err n := by
  simp [regretBudget, Finset.sum_range_succ]

/-- Bounds the Bellman loss at each actual choice, not merely at the first one. -/
def NearGreedy (sys : System S A O) (err : ℕ → ℚ) :
    {n : ℕ} → S → Plan A O n → Prop
  | 0, _, .done => True
  | n + 1, s, .node a next =>
      value sys (n + 1) s - qValue sys n s a ≤ err n ∧
        ∀ o, NearGreedy sys err (sys.step s a o) (next o)

/-- Whole-plan loss telescopes additively across the planning horizon. -/
theorem plan_regret_le (sys : System S A O) (err : ℕ → ℚ)
    {n : ℕ} (s : S) (p : Plan A O n) (hp : NearGreedy sys err s p) :
    value sys n s - planValue sys s p ≤ regretBudget err n := by
  induction n generalizing s with
  | zero => cases p; simp [value, planValue]
  | succ n ih =>
      cases p with
      | node a next =>
          have hsum : expectation sys (value sys n) s a -
              (∑ o, sys.prob s a o * planValue sys (sys.step s a o) (next o)) ≤
              regretBudget err n := by
            calc
              expectation sys (value sys n) s a -
                  (∑ o, sys.prob s a o * planValue sys (sys.step s a o) (next o))
                = ∑ o, sys.prob s a o *
                    (value sys n (sys.step s a o) -
                     planValue sys (sys.step s a o) (next o)) := by
                       simp [expectation, mul_sub, Finset.sum_sub_distrib]
              _ ≤ ∑ o, sys.prob s a o * regretBudget err n := by
                apply Finset.sum_le_sum
                intro o _
                exact mul_le_mul_of_nonneg_left (ih _ _ (hp.2 o)) (sys.prob_nonneg s a o)
              _ = regretBudget err n := by
                rw [← Finset.sum_mul, sys.prob_sum_one]; simp
          have hlocal := hp.1
          unfold qValue at hlocal
          rw [regretBudget_succ]
          change value sys (n + 1) s -
            (sys.reward s a + ∑ o, sys.prob s a o *
              planValue sys (sys.step s a o) (next o)) ≤ _
          linarith

/-- A supplied selector can be approximate, learned, or externally computed.
Only the declared admissibility and value-error hypotheses are used. -/
def policyPlan (sys : System S A O) (choose : ℕ → S → A) :
    (n : ℕ) → S → Plan A O n
  | 0, _ => .done
  | n + 1, s => .node (choose n s)
      (fun o => policyPlan sys choose n (sys.step s (choose n s) o))

theorem policyPlan_legal (sys : System S A O) (choose : ℕ → S → A)
    (ha : ∀ n s, choose n s ∈ sys.actions s) (n : ℕ) (s : S) :
    Legal sys s (policyPlan sys choose n s) := by
  induction n generalizing s with
  | zero => trivial
  | succ n ih => exact ⟨ha n s, fun o => ih _⟩

/-- State-dependent feasible-set version of the Q approximation argument.
The planning error tau need not be zero: exact decoded maximization is optional. -/
theorem decoded_action_gap (sys : System S A O) (n : ℕ) (s : S)
    (estimate : A → ℚ) (eta tau : ℚ) (a : A) (ha : a ∈ sys.actions s)
    (he : ∀ b ∈ sys.actions s, |qValue sys n s b - estimate b| ≤ eta)
    (hm : ∀ b ∈ sys.actions s, estimate b ≤ estimate a + tau) :
    value sys (n + 1) s - qValue sys n s a ≤ 2 * eta + tau := by
  have hx := optimalAction_mem sys n s
  have hl := (abs_le.mp (he a ha)).1
  have hu := (abs_le.mp (he (optimalAction sys n s) hx)).2
  have hmax := hm (optimalAction sys n s) hx
  rw [optimalAction_realizes]
  linarith

theorem decoded_policy_nearGreedy (sys : System S A O) (choose : ℕ → S → A)
    (estimate : ℕ → S → A → ℚ) (eta tau : ℕ → ℚ)
    (ha : ∀ n s, choose n s ∈ sys.actions s)
    (he : ∀ n s a, a ∈ sys.actions s → |qValue sys n s a - estimate n s a| ≤ eta n)
    (hm : ∀ n s a, a ∈ sys.actions s →
      estimate n s a ≤ estimate n s (choose n s) + tau n)
    (n : ℕ) (s : S) :
    NearGreedy sys (fun k => 2 * eta k + tau k) s (policyPlan sys choose n s) := by
  induction n generalizing s with
  | zero => trivial
  | succ n ih =>
      exact ⟨decoded_action_gap sys n s (estimate n s) (eta n) (tau n)
        (choose n s) (ha n s) (he n s) (hm n s), fun o => ih _⟩

/-- End-to-end deployed-policy bound for stagewise Q estimation and planner
error. It does not silently reuse the first-action 2 eta bound for a whole run. -/
theorem decoded_policy_regret (sys : System S A O) (choose : ℕ → S → A)
    (estimate : ℕ → S → A → ℚ) (eta tau : ℕ → ℚ)
    (ha : ∀ n s, choose n s ∈ sys.actions s)
    (he : ∀ n s a, a ∈ sys.actions s → |qValue sys n s a - estimate n s a| ≤ eta n)
    (hm : ∀ n s a, a ∈ sys.actions s →
      estimate n s a ≤ estimate n s (choose n s) + tau n)
    (n : ℕ) (s : S) :
    0 ≤ value sys n s - planValue sys s (policyPlan sys choose n s) ∧
    value sys n s - planValue sys s (policyPlan sys choose n s) ≤
      regretBudget (fun k => 2 * eta k + tau k) n := by
  constructor
  · exact sub_nonneg.mpr (planValue_le_value sys s _ (policyPlan_legal sys choose ha n s))
  · exact plan_regret_le sys _ s _
      (decoded_policy_nearGreedy sys choose estimate eta tau ha he hm n s)

/-- Safety does not depend on the quality of Q estimates: it depends on keeping
all selected actions inside the verified state-dependent feasible set. -/
theorem admissible_approximate_policy_safe (sys : System S A O) (safe : S → Prop)
    (hpres : Preserves sys safe) (choose : ℕ → S → A)
    (ha : ∀ n s, choose n s ∈ sys.actions s) (n : ℕ) (s : S) (hs : safe s) :
    TreeSafe sys safe s (policyPlan sys choose n s) :=
  legal_plan_safe sys safe hpres s _ hs (policyPlan_legal sys choose ha n s)

theorem constant_policy_budget (eta tau : ℚ) (n : ℕ) :
    regretBudget (fun _ => 2 * eta + tau) n = (n : ℚ) * (2 * eta + tau) := by
  simp [regretBudget]

end Komorebi.AVOC.Guarded
