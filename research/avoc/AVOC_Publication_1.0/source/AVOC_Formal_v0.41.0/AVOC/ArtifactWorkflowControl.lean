import AVOC.ArtifactWorkflow

namespace Komorebi.AVOC.ArtifactWorkflow

open Certificate Binding Scheduling

variable {Ω P C O : Type*} [Fintype Ω] [Fintype O] [PartialOrder P] [DecidableEq P]

/-- Every consuming stage accounts for its fee, including rejected verification. -/
theorem admit_budget_spent (p : Protocol Ω P C O) (s : State Ω P) :
    (admitStep p s).budget = s.budget - fee p s .admit ∧
    (admitStep p s).spent = s.spent + fee p s .admit := by
  cases hx : s.owner with
  | none => simp [admitStep, hx, charge]
  | some x =>
    cases hr : s.checked with
    | none => simp [admitStep, hx, hr, charge]
    | some r =>
      cases hc : Binding.consume s.slot (p.spec x) r with
      | mk sl result =>
        cases result <;> simp [admitStep, hx, hr, hc, charge]

theorem step_budget_spent (p : Protocol Ω P C O) (s : State Ω P)
    (a : Action P C) (d : Bool) :
    (step p s a d).budget = s.budget - fee p s a ∧
    (step p s a d).spent = s.spent + fee p s a := by
  cases a with
  | register x c => exact ⟨rfl, rfl⟩
  | verify => exact ⟨rfl, rfl⟩
  | admit => exact admit_budget_spent p s
  | stop => simp [step, fee]

theorem step_budgetSafe (p : Protocol Ω P C O) (B : Nat) (s : State Ω P)
    (hs : BudgetSafe p B s) (a : Action P C) (ha : Allowed p s a) (d : Bool) :
    BudgetSafe p B (step p s a d) := by
  refine ⟨step_safe p s hs.1 a ha d, ?_⟩
  obtain ⟨hb, he⟩ := step_budget_spent p s a d
  rw [hb, he]
  have hf := allowed_fee p s a ha
  have ht := hs.2
  omega

variable [Fintype P] [Fintype C] [DecidableEq C]

def actionPool : Finset (Action P C) :=
  (Finset.univ.image (fun pc : P × C => Action.register pc.1 pc.2)) ∪
    {Action.verify, Action.admit, Action.stop}

omit [PartialOrder P] in
theorem mem_actionPool (a : Action P C) : a ∈ (actionPool : Finset (Action P C)) := by
  cases a with
  | register x c => exact Finset.mem_union_left _ (Finset.mem_image.mpr ⟨(x,c), by simp, rfl⟩)
  | verify => simp [actionPool]
  | admit => simp [actionPool]
  | stop => simp [actionPool]

/-- The control model uses the processed report law, not the unfiltered raw law.
The feasible set includes separately costed register, verify, admit and stop. -/
noncomputable def controller (p : Protocol Ω P C O) :
    Guarded.System (State Ω P) (Action P C) Bool where
  actions s := by
    classical
    exact actionPool.filter (Allowed p s)
  actions_nonempty s := by
    classical
    exact ⟨.stop, Finset.mem_filter.mpr ⟨mem_actionPool _, stop_allowed p s⟩⟩
  prob s a := predictiveProb s.belief (channel p s a)
  prob_nonneg s a d := predictiveProb_nonneg _ _ _
  prob_sum_one s a := predictiveProb_sum_one _ _
  step := step p
  reward := reward p

theorem mem_actions (p : Protocol Ω P C O) (s : State Ω P) (a : Action P C) :
    a ∈ (controller p).actions s ↔ Allowed p s a := by
  classical
  change a ∈ actionPool.filter (Allowed p s) ↔ _
  simp [mem_actionPool]

theorem controller_preserves (p : Protocol Ω P C O) (B : Nat) :
    Guarded.Preserves (controller p) (BudgetSafe p B) := by
  intro s hs a ha d
  exact step_budgetSafe p B s hs a ((mem_actions p s a).1 ha) d

/-- Full deterministic adaptive-tree optimum for this exact artifact workflow. -/
theorem artifact_safe_optimal_plan (p : Protocol Ω P C O)
    (B n : Nat) (s : State Ω P) (hs : BudgetSafe p B s) :
    ∃ plan : Guarded.Plan (Action P C) Bool n,
      Guarded.Legal (controller p) s plan ∧
      Guarded.TreeSafe (controller p) (BudgetSafe p B) s plan ∧
      Guarded.planValue (controller p) s plan = Guarded.value (controller p) n s ∧
      ∀ other : Guarded.Plan (Action P C) Bool n, Guarded.Legal (controller p) s other →
        Guarded.planValue (controller p) s other ≤ Guarded.planValue (controller p) s plan :=
  Guarded.safe_optimal_plan_exists (controller p) (BudgetSafe p B)
    (controller_preserves p B) n s hs

/-- Complete-policy regret is restated for the new law and receipt transitions.
No equality with the old, unfiltered protocol's values is assumed. -/
theorem artifact_approximate_policy (p : Protocol Ω P C O)
    (choose : Nat → State Ω P → Action P C)
    (estimate : Nat → State Ω P → Action P C → ℚ) (eta tau : Nat → ℚ)
    (ha : ∀ k s, Allowed p s (choose k s))
    (he : ∀ k s a, Allowed p s a →
      |Guarded.qValue (controller p) k s a - estimate k s a| ≤ eta k)
    (hm : ∀ k s a, Allowed p s a → estimate k s a ≤ estimate k s (choose k s) + tau k)
    (B n : Nat) (s : State Ω P) (hs : BudgetSafe p B s) :
    Guarded.TreeSafe (controller p) (BudgetSafe p B) s
      (Guarded.policyPlan (controller p) choose n s) ∧
    0 ≤ Guarded.value (controller p) n s - Guarded.planValue (controller p) s
      (Guarded.policyPlan (controller p) choose n s) ∧
    Guarded.value (controller p) n s - Guarded.planValue (controller p) s
      (Guarded.policyPlan (controller p) choose n s) ≤
      Guarded.regretBudget (fun k => 2 * eta k + tau k) n := by
  have hf : ∀ k s, choose k s ∈ (controller p).actions s :=
    fun k s => (mem_actions p s _).2 (ha k s)
  refine ⟨Guarded.admissible_approximate_policy_safe (controller p) (BudgetSafe p B)
    (controller_preserves p B) choose hf n s hs, ?_⟩
  exact Guarded.decoded_policy_regret (controller p) choose estimate eta tau hf
    (fun k s a h => he k s a ((mem_actions p s a).1 h))
    (fun k s a h => hm k s a ((mem_actions p s a).1 h)) n s

/-- Expansion over private raw outcomes computes precisely the public-report
continuation expectation. This is regrouping of one information regime, not
an equivalence with a controller allowed to retain the raw signal. -/
theorem verification_expectation_raw_expansion (p : Protocol Ω P C O)
    (s : State Ω P) (W : State Ω P → ℚ) :
    Guarded.expectation (controller p) W s .verify =
      ∑ o, predictiveProb s.belief (p.rawChannel s) o * W (verifyStep p s (report p s o)) := by
  exact Filtered.predictive_report_expectation s.belief (p.rawChannel s) (report p s)
    (fun d => W (verifyStep p s d))

omit [DecidableEq P] [Fintype P] [Fintype C] [DecidableEq C] in
theorem verify_posterior_is_report_posterior (p : Protocol Ω P C O)
    (s : State Ω P) (d : Bool) :
    (verifyStep p s d).belief =
      bayesUpdateTotal s.belief (Filtered.reportChannel (p.rawChannel s) (report p s)) d := rfl

theorem halted_value_zero (p : Protocol Ω P C O) (n : Nat)
    (s : State Ω P) (hh : s.halted = true) : Guarded.value (controller p) n s = 0 := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
    obtain ⟨a, ha, hm⟩ := Guarded.optimal_action_exists (controller p) n s
    have he : a = .stop := halted_only_stop p s hh a ((mem_actions p s a).1 ha)
    rw [Guarded.value_eq_q_of_optimal (controller p) n s a ha hm, he]
    change reward p s .stop + ∑ d, predictiveProb s.belief (channel p s .stop) d *
      Guarded.value (controller p) n (step p s .stop d) = 0
    have hv : ∀ d, Guarded.value (controller p) n (step p s .stop d) = 0 := fun _ => ih _ rfl
    simp_rw [hv]
    simp [reward, fee]

theorem stop_q_zero (p : Protocol Ω P C O) (n : Nat) (s : State Ω P) :
    Guarded.qValue (controller p) n s .stop = 0 := by
  change reward p s .stop + ∑ d, predictiveProb s.belief (channel p s .stop) d *
    Guarded.value (controller p) n (step p s .stop d) = 0
  have hv : ∀ d, Guarded.value (controller p) n (step p s .stop d) = 0 :=
    fun _ => halted_value_zero p n _ rfl
  simp_rw [hv]
  simp [reward, fee]

theorem stop_optimal (p : Protocol Ω P C O) (n : Nat) (s : State Ω P)
    (h : ∀ a, Allowed p s a → Guarded.qValue (controller p) n s a ≤ 0) :
    Guarded.value (controller p) (n+1) s = 0 := by
  rw [Guarded.value_eq_q_of_optimal (controller p) n s .stop
    ((mem_actions p s _).2 (stop_allowed p s))]
  · exact stop_q_zero p n s
  · intro a ha
    rw [stop_q_zero]
    exact h a ((mem_actions p s a).1 ha)

end Komorebi.AVOC.ArtifactWorkflow
