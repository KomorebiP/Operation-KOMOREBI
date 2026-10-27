import AVOC.PlannerRuntime

namespace Komorebi.AVOC.LiveExecution

open ArtifactWorkflow PlannerRuntime Binding

/-- Exact protected-store projection. The external parser must construct these
records from the actual retained files, not from the planner's predictions. -/
structure StoreView where
  slot : Slot
  checked : Option Receipt
  admitted : Option Ticket
  deriving DecidableEq, Repr

structure RunState where
  core : State Bool (Fin 1)
  admitted : Option Ticket

/-- Operational failures are not negative Bayesian evidence. -/
inductive Observation where
  | confirmed (report : Bool) (actual : StoreView)
  | fault (reason : String)
  deriving DecidableEq, Repr

abbrev Event (j : Job) := Action (Fin 1) (Fin j.artifacts.size) × Observation

def initialRun (j : Job) : RunState := ⟨initial j, none⟩

def view (s : RunState) : StoreView := ⟨s.core.slot, s.core.checked, s.admitted⟩

/-- The extra admitted-ticket field retains the exact snapshot lost by the
single-task controller after consuming its in-flight slot. -/
def move (j : Job) (s : RunState) (a : Action (Fin 1) (Fin j.artifacts.size))
    (d : Bool) : RunState :=
  let next := (runtimeModel j).step s.core a d
  ⟨next, if 0 ∈ next.completed ∧ 0 ∉ s.core.completed then s.core.slot.pending else s.admitted⟩

/-- No update is returned for an operational fault, illegal action, impossible
model report, post-halt event, or exact external snapshot disagreement. -/
def acceptStep (j : Job) (s : RunState) (e : Event j) : Except String RunState :=
  match e.2 with
  | .fault why => .error ("operational fault; not Bayesian evidence: " ++ why)
  | .confirmed d actual =>
    if s.core.halted then .error "event after terminal stop"
    else if WorkflowPlanner.allowedCheck (protocol j) [0] s.core e.1 then
      if 0 < (runtimeModel j).prob s.core e.1 d then
        let next := move j s e.1 d
        if view next = actual then .ok next else .error "external snapshot mismatch"
      else .error "report outside declared model support"
    else .error "action is not allowed"

def replay (j : Job) : RunState → List (Event j) → Except String RunState
  | s, [] => .ok s
  | s, e :: es => match acceptStep j s e with
    | .error msg => .error msg
    | .ok next => replay j next es

@[simp] theorem move_core (j : Job) (s : RunState)
    (a : Action (Fin 1) (Fin j.artifacts.size)) (d : Bool) :
    (move j s a d).core = ArtifactWorkflow.step (protocol j) s.core a d :=
  WorkflowPlanner.step_eq (protocol j) s.core a d

@[simp] theorem fault_rejected (j : Job) (s : RunState)
    (a : Action (Fin 1) (Fin j.artifacts.size)) (why : String) :
    acceptStep j s (a, .fault why) =
      .error ("operational fault; not Bayesian evidence: " ++ why) := rfl

theorem accepted_step_contract (j : Job) (s t : RunState) (e : Event j)
    (h : acceptStep j s e = .ok t) :
    ∃ d actual, e.2 = .confirmed d actual ∧ s.core.halted = false ∧
      Allowed (protocol j) s.core e.1 ∧
      0 < (runtimeModel j).prob s.core e.1 d ∧
      view t = actual ∧ t = move j s e.1 d := by
  rcases e with ⟨a, obs⟩
  cases obs with
  | fault why => simp [acceptStep] at h
  | confirmed d actual =>
    cases hh : s.core.halted with
    | true => simp [acceptStep, hh] at h
    | false =>
      by_cases ha : WorkflowPlanner.allowedCheck (protocol j) [0] s.core a = true
      · by_cases hp : 0 < (runtimeModel j).prob s.core a d
        · by_cases hv : view (move j s a d) = actual
          · have he : move j s a d = t := by simpa [acceptStep, hh, ha, hp, hv] using h
            subst t
            refine ⟨d, actual, rfl, rfl, ?_, hp, hv, rfl⟩
            exact (WorkflowPlanner.allowedCheck_correct (protocol j) [0]
              (fun x => by have hx : x = 0 := Subsingleton.elim _ _; simp [hx]) s.core a).1 ha
          · simp [acceptStep, hh, ha, hp, hv] at h
        · simp [acceptStep, hh, ha, hp] at h
      · simp [acceptStep, hh, ha] at h

theorem accepted_step_source_safe (j : Job) (s t : RunState) (e : Event j)
    (hs : SourceSafe (protocol j) j.budget s.core) (h : acceptStep j s e = .ok t) :
    SourceSafe (protocol j) j.budget t.core := by
  obtain ⟨d, actual, _, _, ha, _, _, ht⟩ := accepted_step_contract j s t e h
  subst t
  rw [move_core]
  exact step_source_safe (protocol j) (runtime_catalogue_parsed j) j.budget
    s.core hs e.1 ha d

theorem accepted_step_matches_external (j : Job) (s t : RunState)
    (a : Action (Fin 1) (Fin j.artifacts.size)) (d : Bool) (actual : StoreView)
    (h : acceptStep j s (a, .confirmed d actual) = .ok t) : view t = actual := by
  obtain ⟨d', v', he, _, _, _, hv, _⟩ := accepted_step_contract j s t _ h
  cases he
  exact hv

theorem accepted_step_cost (j : Job) (s t : RunState) (e : Event j)
    (h : acceptStep j s e = .ok t) :
    t.core.spent = s.core.spent + fee (protocol j) s.core e.1 := by
  obtain ⟨d, _, _, _, _, _, _, ht⟩ := accepted_step_contract j s t e h
  subst t
  rw [move_core]
  exact (step_budget_spent (protocol j) s.core e.1 d).2

theorem replay_source_safe (j : Job) (es : List (Event j)) (s t : RunState)
    (hs : SourceSafe (protocol j) j.budget s.core) (h : replay j s es = .ok t) :
    SourceSafe (protocol j) j.budget t.core := by
  induction es generalizing s with
  | nil => have he : s = t := by simpa [replay] using h
           simpa [he] using hs
  | cons e es ih =>
    cases he : acceptStep j s e with
    | error msg => simp [replay, he] at h
    | ok next =>
      apply ih next (accepted_step_source_safe j s next e hs he)
      simpa [replay, he] using h

theorem replay_initial_source_safe (j : Job) (es : List (Event j)) (s : RunState)
    (h : replay j (initialRun j) es = .ok s) :
    SourceSafe (protocol j) j.budget s.core :=
  replay_source_safe j es (initialRun j) s (runtime_initial_safe j) h

theorem replay_no_overspend (j : Job) (es : List (Event j)) (s : RunState)
    (h : replay j (initialRun j) es = .ok s) : s.core.spent ≤ j.budget := by
  have hb := (replay_initial_source_safe j es s h).1.2
  omega

theorem replay_certifies (j : Job) (es : List (Event j)) (s : RunState)
    (h : replay j (initialRun j) es = .ok s) :
    ∀ x ∈ s.core.completed, claim (protocol j) x :=
  (replay_initial_source_safe j es s h).1.1.certified

theorem replay_append (j : Job) (xs ys : List (Event j)) (s : RunState) :
    replay j s (xs ++ ys) =
      match replay j s xs with
      | .error msg => .error msg
      | .ok next => replay j next ys := by
  induction xs generalizing s with
  | nil => rfl
  | cons e xs ih =>
    cases he : acceptStep j s e <;> simp [replay, he, ih]

theorem fault_suffix_aborts (j : Job) (s : RunState)
    (a : Action (Fin 1) (Fin j.artifacts.size)) (why : String) (es : List (Event j)) :
    replay j s ((a, .fault why) :: es) =
      .error ("operational fault; not Bayesian evidence: " ++ why) := rfl

theorem replay_then_recommend_allowed (j : Job) (es : List (Event j)) (s : RunState)
    (_h : replay j (initialRun j) es = .ok s) (n : Nat) :
    Allowed (protocol j) s.core (recommend j n s.core).action :=
  runtime_recommend_allowed j n s.core

theorem replay_then_policy_source_safe (j : Job) (es : List (Event j)) (s : RunState)
    (h : replay j (initialRun j) es = .ok s) (n : Nat) :
    Guarded.TreeSafe (controller (protocol j)) (SourceSafe (protocol j) j.budget) s.core
      (Guarded.policyPlan (controller (protocol j))
        (fun k t => (recommend j (k+1) t).action) n s.core) := by
  exact source_bound_approximate_policy_safe (protocol j) (runtime_catalogue_parsed j)
    _ (fun k t => runtime_recommend_allowed j (k+1) t) j.budget n s.core
    (replay_initial_source_safe j es s h)

/-- Existing performance theorem applies to the normal matched continuation.
No assertion about an aborted physical execution is substituted for it. -/
theorem matched_continuation_regret (j : Job) (s : RunState) (n : Nat) :
    let selector := fun k t => (recommend j (k+1) t).action
    0 ≤ Guarded.value (controller (protocol j)) n s.core -
      Guarded.planValue (controller (protocol j)) s.core
        (Guarded.policyPlan (controller (protocol j)) selector n s.core) ∧
    Guarded.value (controller (protocol j)) n s.core -
      Guarded.planValue (controller (protocol j)) s.core
        (Guarded.policyPlan (controller (protocol j)) selector n s.core) ≤
      Guarded.regretBudget (fun k => 2 *
        ((k+1 - ExecutablePlanner.selectedDepth (3+j.artifacts.size) 2 (k+1) j.credit : Nat):ℚ)
        * rewardBound j) n := runtime_policy_regret j n s.core

/-- An acknowledged new completion includes the actual prior ticket and
checked certificate; it cannot arise from registration or verification alone. -/
theorem acknowledged_admission_has_ticket (j : Job) (s t : RunState) (e : Event j)
    (h : acceptStep j s e = .ok t) (hn : 0 ∈ t.core.completed) (hf : 0 ∉ s.core.completed) :
    e.1 = .admit ∧ ∃ x ticket receipt,
      s.core.owner = some x ∧ s.core.slot.pending = some ticket ∧
      s.core.checked = some receipt ∧ receipt.subject = ticket ∧
      ticket.artifact.identity = (protocol j).spec x ∧ Valid ticket.artifact := by
  obtain ⟨d, _, _, _, ha, _, _, ht⟩ := accepted_step_contract j s t e h
  subst t
  rw [move_core] at hn
  exact new_completion_requires_admit (protocol j) s.core e.1 ha d 0 hn hf

/-- The external admitted record retains both valid proof semantics and its
exact source-to-AST connection after the controller consumes pending. -/
def ArchiveSafe (s : RunState) : Prop :=
  ∀ t, s.admitted = some t → Valid t.artifact ∧ SourceParsed t.artifact

theorem accepted_step_archive_safe (j : Job) (s t : RunState) (e : Event j)
    (hs : SourceSafe (protocol j) j.budget s.core) (harch : ArchiveSafe s)
    (h : acceptStep j s e = .ok t) : ArchiveSafe t := by
  obtain ⟨d, _, _, _, ha, _, _, ht⟩ := accepted_step_contract j s t e h
  subst t
  intro ticket hticket
  by_cases hn : 0 ∈ ((runtimeModel j).step s.core e.1 d).completed ∧ 0 ∉ s.core.completed
  · have hold : s.core.slot.pending = some ticket := by simpa [move, hn] using hticket
    have hnew : 0 ∈ (ArtifactWorkflow.step (protocol j) s.core e.1 d).completed := by
      simpa only [runtimeModel, WorkflowPlanner.model, WorkflowPlanner.step_eq] using hn.1
    obtain ⟨_, _, t0, _, _, hp, _, _, _, hv⟩ :=
      new_completion_requires_admit (protocol j) s.core e.1 ha d 0 hnew hn.2
    have he : t0 = ticket := Option.some.inj (hp.symm.trans hold)
    exact ⟨by simpa only [he] using hv, hs.2 ticket hold⟩
  · exact harch ticket (by simpa [move, hn] using hticket)

theorem replay_archive_safe (j : Job) (es : List (Event j)) (s t : RunState)
    (hs : SourceSafe (protocol j) j.budget s.core) (har : ArchiveSafe s)
    (h : replay j s es = .ok t) : ArchiveSafe t := by
  induction es generalizing s with
  | nil => have he : s = t := by simpa [replay] using h
           simpa [he] using har
  | cons e es ih =>
    cases he : acceptStep j s e with
    | error msg => simp [replay, he] at h
    | ok next =>
      exact ih next (accepted_step_source_safe j s next e hs he)
        (accepted_step_archive_safe j s next e hs har he) (by simpa [replay, he] using h)

theorem replay_initial_archive_safe (j : Job) (es : List (Event j)) (s : RunState)
    (h : replay j (initialRun j) es = .ok s) : ArchiveSafe s := by
  apply replay_archive_safe j es (initialRun j) s (runtime_initial_safe j) _ h
  intro t ht
  cases ht

end Komorebi.AVOC.LiveExecution
