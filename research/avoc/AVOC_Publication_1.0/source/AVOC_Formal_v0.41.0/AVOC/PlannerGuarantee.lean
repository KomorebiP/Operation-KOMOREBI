import AVOC.PlannerWork

namespace Komorebi.AVOC.ExecutablePlanner

variable {S A O : Type*} [DecidableEq A] [DecidableEq O] [Fintype O]

/-- A supplied feasible fallback is used only at depth zero or malformed empty
action enumerations. The Realizes contract excludes the latter. -/
def choose (m : Model S A O) (fallback : S → A) (depth : Nat) (s : S) : A :=
  (evaluate m depth s).choice.getD (fallback s)

theorem choose_allowed (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (fallback : S → A)
    (hf : ∀ s, fallback s ∈ sys.actions s) (depth : Nat) (s : S) :
    choose m fallback depth s ∈ sys.actions s := by
  cases depth with
  | zero => exact hf s
  | succ n =>
      obtain ⟨a, ha, ham, _⟩ := evaluate_choice_optimal m sys h n s
      simpa [choose, ha] using ham

omit [DecidableEq O] in
theorem value_magnitude (sys : Guarded.System S A O) (R : ℚ)
    (hr : ∀ s a, a ∈ sys.actions s → |sys.reward s a| ≤ R)
    (n : Nat) (s : S) : |Guarded.value sys n s| ≤ (n : ℚ) * R := by
  induction n generalizing s with
  | zero => simp
  | succ n ih =>
      obtain ⟨a, ha, hm⟩ := Guarded.optimal_action_exists sys n s
      have hv := Guarded.value_eq_q_of_optimal sys n s a ha hm
      have he := Guarded.expectation_uniform_error sys (Guarded.value sys n)
        (fun _ => 0) ((n : ℚ) * R) (by simpa using ih) s a
      rw [Guarded.expectation_const] at he
      have her : |Guarded.expectation sys (Guarded.value sys n) s a| ≤ (n : ℚ) * R := by
        simpa using he
      rw [hv, Guarded.qValue]
      have hh := abs_add_le (sys.reward s a) (Guarded.expectation sys (Guarded.value sys n) s a)
      have hh' := hr s a ha
      push_cast
      nlinarith

omit [DecidableEq O] in
/-- Sharing a common initial planning depth is nonexpansive in terminal value.
The unplanned tail is bounded explicitly, not declared to have value zero. -/
theorem horizon_value_error (sys : Guarded.System S A O) (R : ℚ)
    (hr : ∀ s a, a ∈ sys.actions s → |sys.reward s a| ≤ R)
    (n tail : Nat) (s : S) :
    |Guarded.value sys (n + tail) s - Guarded.value sys n s| ≤ (tail : ℚ) * R := by
  induction n generalizing s with
  | zero => simpa using value_magnitude sys R hr tail s
  | succ n ih =>
      have hq : ∀ a ∈ sys.actions s,
          |Guarded.qValue sys (n + tail) s a - Guarded.tableQ sys (Guarded.value sys n) s a| ≤
          (tail : ℚ) * R := by
        intro a _
        have he := Guarded.expectation_uniform_error sys (Guarded.value sys (n + tail))
          (Guarded.value sys n) ((tail : ℚ) * R) ih s a
        simpa only [Guarded.qValue, Guarded.tableQ, add_sub_add_left_eq_sub] using he
      have hh := Guarded.value_backup_error_of_q_error sys sys id (n + tail)
        (Guarded.value sys n) ((tail : ℚ) * R) s rfl hq
      simpa only [id_eq, Guarded.backup_optimal_value, Nat.succ_add] using hh

omit [DecidableEq O] in
theorem horizon_q_error (sys : Guarded.System S A O) (R : ℚ)
    (hr : ∀ s a, a ∈ sys.actions s → |sys.reward s a| ≤ R)
    (n tail : Nat) (s : S) (a : A) :
    |Guarded.qValue sys (n + tail) s a - Guarded.qValue sys n s a| ≤ (tail : ℚ) * R := by
  have h := Guarded.expectation_uniform_error sys (Guarded.value sys (n + tail))
    (Guarded.value sys n) ((tail : ℚ) * R) (horizon_value_error sys R hr n tail) s a
  simpa only [Guarded.qValue, add_sub_add_left_eq_sub] using h

theorem truncated_action_gap (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (fallback : S → A) (R : ℚ)
    (hr : ∀ s a, a ∈ sys.actions s → |sys.reward s a| ≤ R)
    (depth tail : Nat) (s : S) :
    Guarded.value sys (depth + tail + 1) s -
      Guarded.qValue sys (depth + tail) s (choose m fallback (depth + 1) s) ≤
        2 * ((tail : ℚ) * R) := by
  obtain ⟨a, he, ha, hm⟩ := evaluate_choice_optimal m sys h depth s
  have hx : choose m fallback (depth + 1) s = a := by simp [choose, he]
  rw [hx]
  have hd := Guarded.decoded_action_gap sys (depth + tail) s
    (Guarded.qValue sys depth s) ((tail : ℚ) * R) 0 a ha
    (fun b _ => horizon_q_error sys R hr depth tail s b)
    (by simpa using hm)
  simpa using hd

omit [DecidableEq O] in
theorem feasible_action_gap_bound (sys : Guarded.System S A O) (R : ℚ)
    (hr : ∀ s a, a ∈ sys.actions s → |sys.reward s a| ≤ R)
    (n : Nat) (s : S) (a : A) (ha : a ∈ sys.actions s) :
    Guarded.value sys (n + 1) s - Guarded.qValue sys n s a ≤ 2 * ((n + 1 : Nat) : ℚ) * R := by
  have hv := (abs_le.mp (value_magnitude sys R hr (n + 1) s)).2
  have he := Guarded.expectation_uniform_error sys (Guarded.value sys n)
    (fun _ => 0) ((n : ℚ) * R) (by simpa using value_magnitude sys R hr n) s a
  rw [Guarded.expectation_const] at he
  have hl := (abs_le.mp he).1
  have hr' := (abs_le.mp (hr s a ha)).1
  unfold Guarded.qValue
  push_cast at hv ⊢
  linarith

/-- A certificate for the action returned by truncated executable lookahead.
At depth zero it is a conservative fallback bound, never a claim of optimality. -/
theorem choose_gap (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (fallback : S → A)
    (hf : ∀ s, fallback s ∈ sys.actions s) (R : ℚ)
    (hr : ∀ s a, a ∈ sys.actions s → |sys.reward s a| ≤ R)
    (n depth : Nat) (hd : depth ≤ n + 1) (s : S) :
    Guarded.value sys (n + 1) s - Guarded.qValue sys n s (choose m fallback depth s) ≤
      2 * ((n + 1 - depth : Nat) : ℚ) * R := by
  cases depth with
  | zero =>
      simpa [choose, evaluate] using feasible_action_gap_bound sys R hr n s (fallback s) (hf s)
  | succ d =>
      have hd' : d ≤ n := by omega
      have he : d + (n - d) = n := by omega
      have hh := truncated_action_gap m sys h fallback R hr d (n - d) s
      rw [he] at hh
      simpa only [Nat.succ_sub_succ_eq_sub, mul_assoc] using hh

/-- Entire policy guarantee for a prescribed affordable-depth schedule. -/
theorem lookahead_policy_regret (m : Model S A O) (sys : Guarded.System S A O)
    (h : Realizes m sys) (fallback : S → A)
    (hf : ∀ s, fallback s ∈ sys.actions s) (R : ℚ)
    (hr : ∀ s a, a ∈ sys.actions s → |sys.reward s a| ≤ R)
    (depth : Nat → Nat) (hd : ∀ k, depth k ≤ k + 1) (n : Nat) (s : S) :
    0 ≤ Guarded.value sys n s - Guarded.planValue sys s
      (Guarded.policyPlan sys (fun k t => choose m fallback (depth k) t) n s) ∧
    Guarded.value sys n s - Guarded.planValue sys s
      (Guarded.policyPlan sys (fun k t => choose m fallback (depth k) t) n s) ≤
      Guarded.regretBudget (fun k => 2 * ((k + 1 - depth k : Nat) : ℚ) * R) n := by
  have hl := Guarded.policyPlan_legal sys (fun k t => choose m fallback (depth k) t)
    (fun k t => choose_allowed m sys h fallback hf (depth k) t) n s
  constructor
  · exact sub_nonneg.mpr (Guarded.planValue_le_value sys s _ hl)
  · apply Guarded.plan_regret_le
    clear hl
    induction n generalizing s with
    | zero => trivial
    | succ n ih => exact ⟨choose_gap m sys h fallback hf R hr n (depth n) (hd n) s, fun o => ih _⟩

/-- Charged utility uses a declared conversion from counted planning work to
reward units. This does not make that conversion an empirical measurement. -/
def chargedReturn (gross computeCost : ℚ) : ℚ := gross - computeCost

theorem charged_regret (optimal gross loss computeCost maxCost : ℚ)
    (hlo : 0 ≤ optimal - gross) (hgap : optimal - gross ≤ loss)
    (hc : 0 ≤ computeCost) (hcap : computeCost ≤ maxCost) :
    0 ≤ optimal - chargedReturn gross computeCost ∧
      optimal - chargedReturn gross computeCost ≤ loss + maxCost := by
  unfold chargedReturn
  constructor <;> linarith

end Komorebi.AVOC.ExecutablePlanner
