import AVOC.ArtifactWorkflowControl
import AVOC.BayesianGuardedBridge

namespace Komorebi.AVOC.ArtifactWorkflow

open Certificate Binding Scheduling

variable {Ω P C O : Type*} [Fintype Ω] [Fintype O] [PartialOrder P] [DecidableEq P]

theorem admit_belief (p : Protocol Ω P C O) (s : State Ω P) :
    (admitStep p s).belief = s.belief := by
  cases hx : s.owner with
  | none => simp [admitStep, hx, charge]
  | some x =>
    cases hr : s.checked with
    | none => simp [admitStep, hx, hr, charge]
    | some r =>
      cases hc : Binding.consume s.slot (p.spec x) r with
      | mk sl result => cases result <;> simp [admitStep, hx, hr, hc, charge]

/-- Every stage has the declared Bayesian belief transition. Deterministic
register/admit/stop stages use a silent observation law and leave belief unchanged. -/
theorem step_belief (p : Protocol Ω P C O) (s : State Ω P)
    (a : Action P C) (d : Bool) :
    (step p s a d).belief = bayesUpdateTotal s.belief (channel p s a) d := by
  cases a with
  | register x c => exact (Filtered.silent_posterior s.belief false d).symm
  | verify => rfl
  | admit => simpa [step, channel, Filtered.silent_posterior] using admit_belief p s
  | stop => exact (Filtered.silent_posterior s.belief false d).symm

omit [DecidableEq P] in
/-- An actual positive-probability success report has an actual raw receipt witness.
Formal safety on impossible branches does not manufacture positive evidence. -/
theorem positive_success_has_receipt (p : Protocol Ω P C O) (s : State Ω P)
    (hp : 0 < predictiveProb s.belief (channel p s .verify) true) :
    ∃ o x t r, 0 < predictiveProb s.belief (p.rawChannel s) o ∧
      report p s o = true ∧ s.owner = some x ∧ s.slot.pending = some t ∧
      p.rawReceipt s o = some r ∧ r.subject = t ∧
      t.artifact.identity = p.spec x ∧ Valid t.artifact := by
  have hex : ∃ o, 0 < predictiveProb s.belief (p.rawChannel s) o ∧ report p s o = true := by
    by_contra h
    push Not at h
    have hsum : (∑ o, if report p s o = true then
        predictiveProb s.belief (p.rawChannel s) o else 0) ≤ 0 := by
      apply Finset.sum_nonpos
      intro o _
      by_cases hr : report p s o = true
      · simp only [hr, ite_true]
        exact le_of_not_gt (fun hpos => h o hpos hr)
      · simp [hr]
    change 0 < predictiveProb s.belief
      (Filtered.reportChannel (p.rawChannel s) (report p s)) true at hp
    rw [Filtered.predictive_report] at hp
    exact (not_lt_of_ge hsum) hp
  obtain ⟨o, ho, hr⟩ := hex
  obtain ⟨x, t, r, hx, ht, hraw, hb, hi, hv⟩ := report_true_bound p s o hr
  exact ⟨o, x, t, r, ho, hr, hx, ht, hraw, hb, hi, hv⟩

/-- A declared legal action cannot add a result by merely registering or checking. -/
theorem new_completion_requires_admit (p : Protocol Ω P C O) (s : State Ω P)
    (a : Action P C) (ha : Allowed p s a) (d : Bool) (y : P)
    (hy : y ∈ (step p s a d).completed) (hfresh : y ∉ s.completed) :
    a = .admit ∧ ∃ x t r, s.owner = some x ∧ s.slot.pending = some t ∧
      s.checked = some r ∧ r.subject = t ∧
      t.artifact.identity = p.spec x ∧ Valid t.artifact := by
  cases a with
  | register x c => exact False.elim (hfresh hy)
  | verify => exact False.elim (hfresh hy)
  | stop => exact False.elim (hfresh hy)
  | admit =>
    exact ⟨rfl, admission_has_exact_ticket p s ((ha.resolve_left (by intro h; cases h)).2.2)⟩

noncomputable def execute (p : Protocol Ω P C O) :
    State Ω P → List (Action P C × Bool) → State Ω P
  | s, [] => s
  | s, (a,d)::xs => execute p (step p s a d) xs

def TraceLegal (p : Protocol Ω P C O) : State Ω P → List (Action P C × Bool) → Prop
  | _, [] => True
  | s, (a,d)::xs => Allowed p s a ∧ TraceLegal p (step p s a d) xs

/-- State-dependent fee sum along the actual execution, including each retry. -/
noncomputable def traceCost (p : Protocol Ω P C O) : State Ω P → List (Action P C × Bool) → Nat
  | _, [] => 0
  | s, (a,d)::xs => fee p s a + traceCost p (step p s a d) xs

theorem execute_spent (p : Protocol Ω P C O) (s : State Ω P)
    (xs : List (Action P C × Bool)) :
    (execute p s xs).spent = s.spent + traceCost p s xs := by
  induction xs generalizing s with
  | nil => simp [execute, traceCost]
  | cons z xs ih =>
    obtain ⟨a,d⟩ := z
    simp only [execute, traceCost, ih, (step_budget_spent p s a d).2]
    omega

theorem legal_trace_safe (p : Protocol Ω P C O) (B : Nat) (s : State Ω P)
    (xs : List (Action P C × Bool)) (hs : BudgetSafe p B s) (hl : TraceLegal p s xs) :
    BudgetSafe p B (execute p s xs) := by
  induction xs generalizing s with
  | nil => exact hs
  | cons z xs ih =>
    obtain ⟨a,d⟩ := z
    exact ih _ (step_budgetSafe p B s hs a hl.1 d) hl.2

theorem legal_trace_cost_bound (p : Protocol Ω P C O) (s : State Ω P)
    (xs : List (Action P C × Bool)) (hs : Safe p s) (hl : TraceLegal p s xs) :
    traceCost p s xs ≤ s.budget := by
  have hb := (legal_trace_safe p (s.budget+s.spent) s xs ⟨hs,rfl⟩ hl).2
  rw [execute_spent] at hb
  omega

variable [Fintype P] [Fintype C] [DecidableEq C]

/-- The primitive model-error theorem is now specialized to the exact filtered,
artifact-bound process, not silently reassigned from the older task-ID protocol. -/
theorem artifact_bayesian_model_policy {M : Type*}
    (p : Protocol Ω P C O)
    (model : Guarded.System (RationalBelief Ω × M) (Action P C) Bool)
    (phi : State Ω P → RationalBelief Ω × M)
    (W : Nat → (RationalBelief Ω × M) → ℚ)
    (eps alpha beta : ℚ) (L R chi residual : Nat → ℚ)
    (hc : Guarded.BayesianModelCertificate (controller p) model phi
      (fun s => s.belief) W eps alpha beta L R chi residual)
    (estimate : Nat → State Ω P → Action P C → ℚ)
    (choose : Nat → State Ω P → Action P C) (codeError tau : Nat → ℚ)
    (ha : ∀ k s, Allowed p s (choose k s))
    (he : ∀ k s a, Allowed p s a →
      |Guarded.tableQ model (W k) (phi s) a - estimate k s a| ≤ codeError k)
    (hm : ∀ k s a, Allowed p s a → estimate k s a ≤ estimate k s (choose k s) + tau k)
    (B n : Nat) (s : State Ω P) (hs : BudgetSafe p B s) :
    Guarded.TreeSafe (controller p) (BudgetSafe p B) s
      (Guarded.policyPlan (controller p) choose n s) ∧
    0 ≤ Guarded.value (controller p) n s -
      Guarded.planValue (controller p) s (Guarded.policyPlan (controller p) choose n s) ∧
    Guarded.value (controller p) n s -
      Guarded.planValue (controller p) s (Guarded.policyPlan (controller p) choose n s) ≤
      Guarded.regretBudget (fun k => 2 *
        (Guarded.modelQBudget eps (Guarded.bayesianTransportBudget alpha beta L R chi) residual k +
          codeError k) + tau k) n := by
  have hf : ∀ k s, choose k s ∈ (controller p).actions s :=
    fun k s => (mem_actions p s _).2 (ha k s)
  refine ⟨Guarded.admissible_approximate_policy_safe (controller p) (BudgetSafe p B)
    (controller_preserves p B) choose hf n s hs, ?_⟩
  exact Guarded.model_decoded_policy_regret (controller p) model phi W eps _ residual
    hc.toModelCertificate estimate choose codeError tau hf
    (fun k s a h => he k s a ((mem_actions p s a).1 h))
    (fun k s a h => hm k s a ((mem_actions p s a).1 h)) n s

end Komorebi.AVOC.ArtifactWorkflow
