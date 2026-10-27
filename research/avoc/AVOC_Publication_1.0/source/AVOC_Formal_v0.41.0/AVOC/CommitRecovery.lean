import AVOC.LiveExecution

namespace Komorebi.AVOC.CommitRecovery

open LiveExecution ArtifactWorkflow PlannerRuntime Binding

/-- Sequence numbers are scoped to a protected run. Intent includes the exact
pre-operation store projection and selected action, not merely a verdict bit. -/
structure Intent (j : Job) where
  sequence : Nat
  before : StoreView
  action : Action (Fin 1) (Fin j.artifacts.size)
  deriving DecidableEq

/-- The transactional backend must durably store this result atomically with
its `after` state. This type alone does not authenticate physical storage. -/
structure Commit (j : Job) where
  intent : Intent j
  report : Bool
  after : StoreView
  deriving DecidableEq

structure Checkpoint (j : Job) where
  next : Nat
  state : RunState
  last : Option (Commit j)

def initial (j : Job) : Checkpoint j := ⟨0, initialRun j, none⟩

def event {j : Job} (r : Commit j) : Event j :=
  (r.intent.action, .confirmed r.report r.after)

/-- Reconciliation does not execute an external research action. A new commit
is replayed through the inherited checked transition. An exact duplicate is
idempotent; a changed sequence, result, or physical projection is rejected. -/
def acknowledge (j : Job) (c : Checkpoint j) (r : Commit j) (actual : StoreView) :
    Except String (Checkpoint j) :=
  if r.after ≠ actual then .error "commit post-state differs from current store"
  else if c.last = some r then
    if c.next = r.intent.sequence + 1 ∧ view c.state = actual then .ok c
    else .error "duplicate receipt does not match checkpoint"
  else if r.intent.sequence ≠ c.next then .error "commit sequence mismatch"
  else if r.intent.before ≠ view c.state then .error "commit pre-state mismatch"
  else match acceptStep j c.state (event r) with
    | .error msg => .error msg
    | .ok t => .ok ⟨c.next + 1, t, some r⟩

def Safe (j : Job) (c : Checkpoint j) : Prop :=
  SourceSafe (protocol j) j.budget c.state.core ∧ ArchiveSafe c.state

/-- The operational adapter never guesses an observation from an unfinished
checker call, even when the physical view happens to be unchanged. -/
inductive Outcome (j : Job) where
  | unfinished (intent : Intent j)
  | committed (receipt : Commit j)

def recover (j : Job) (c : Checkpoint j) (o : Outcome j) (actual : StoreView) :
    Except String (Checkpoint j) :=
  match o with
  | .unfinished _ => .error "no durable result: do not infer a report or retry"
  | .committed r => acknowledge j c r actual

@[simp] theorem initial_safe (j : Job) : Safe j (initial j) := by
  refine ⟨runtime_initial_safe j, ?_⟩
  intro t ht
  cases ht

@[simp] theorem unfinished_rejected (j : Job) (c : Checkpoint j)
    (i : Intent j) (v : StoreView) :
    recover j c (.unfinished i) v =
      .error "no durable result: do not infer a report or retry" := rfl

/-- A confirmed recovery is either an exact no-op duplicate or one already
validated reference-model step. No third transition is admitted. -/
theorem acknowledge_contract (j : Job) (c d : Checkpoint j)
    (r : Commit j) (actual : StoreView)
    (h : acknowledge j c r actual = .ok d) :
    r.after = actual ∧
      ((d = c ∧ c.last = some r ∧ c.next = r.intent.sequence + 1 ∧
          view c.state = actual) ∨
       (r.intent.sequence = c.next ∧ r.intent.before = view c.state ∧
          ∃ t, acceptStep j c.state (event r) = .ok t ∧
            d = ⟨c.next + 1, t, some r⟩)) := by
  by_cases hv : r.after = actual
  · refine ⟨hv, ?_⟩
    by_cases hl : c.last = some r
    · by_cases hc : c.next = r.intent.sequence + 1 ∧ view c.state = actual
      · have hd : c = d := by simpa [acknowledge, hv, hl, hc] using h
        exact Or.inl ⟨hd.symm, hl, hc⟩
      · simp [acknowledge, hv, hl, hc] at h
    · by_cases hn : r.intent.sequence = c.next
      · by_cases hb : r.intent.before = view c.state
        · cases hs : acceptStep j c.state (event r) with
          | error msg => simp [acknowledge, hv, hl, hn, hb, hs] at h
          | ok t =>
            have hd : (⟨c.next + 1, t, some r⟩ : Checkpoint j) = d := by
              simpa [acknowledge, hv, hl, hn, hb, hs] using h
            exact Or.inr ⟨hn, hb, t, rfl, hd.symm⟩
        · simp [acknowledge, hv, hl, hn, hb] at h
      · simp [acknowledge, hv, hl, hn] at h
  · simp [acknowledge, hv] at h

theorem acknowledge_safe (j : Job) (c d : Checkpoint j) (r : Commit j)
    (v : StoreView) (hs : Safe j c) (h : acknowledge j c r v = .ok d) : Safe j d := by
  obtain ⟨_, hc | hn⟩ := acknowledge_contract j c d r v h
  · exact hc.1 ▸ hs
  · obtain ⟨_, _, t, ht, hd⟩ := hn
    subst d
    exact ⟨accepted_step_source_safe j c.state t (event r) hs.1 ht,
      accepted_step_archive_safe j c.state t (event r) hs.1 hs.2 ht⟩

theorem acknowledge_result_identity (j : Job) (c d : Checkpoint j)
    (r : Commit j) (v : StoreView) (h : acknowledge j c r v = .ok d) :
    d.last = some r ∧ d.next = r.intent.sequence + 1 ∧ view d.state = v := by
  obtain ⟨hv, hc | hn⟩ := acknowledge_contract j c d r v h
  · obtain ⟨hd, hl, hn, hs⟩ := hc
    subst d
    exact ⟨hl, hn, hs⟩
  · obtain ⟨hn, _, t, ht, hd⟩ := hn
    subst d
    refine ⟨rfl, by rw [hn], ?_⟩
    exact (accepted_step_matches_external j c.state t r.intent.action r.report r.after ht).trans hv

/-- Re-acknowledging a committed operation changes no logical state, belief,
budget, receipt, or checkpoint counter. It performs no external operation. -/
theorem acknowledge_idempotent (j : Job) (c d : Checkpoint j)
    (r : Commit j) (v : StoreView) (h : acknowledge j c r v = .ok d) :
    acknowledge j d r v = .ok d := by
  have hv := (acknowledge_contract j c d r v h).1
  obtain ⟨hl, hn, hs⟩ := acknowledge_result_identity j c d r v h
  simp [acknowledge, hv, hl, hn, hs]

theorem acknowledge_count (j : Job) (c d : Checkpoint j)
    (r : Commit j) (v : StoreView) (h : acknowledge j c r v = .ok d) :
    d.next = c.next ∨ d.next = c.next + 1 := by
  obtain ⟨_, hc | hn⟩ := acknowledge_contract j c d r v h
  · exact Or.inl (congrArg Checkpoint.next hc.1)
  · obtain ⟨_, _, t, _, hd⟩ := hn
    exact Or.inr (congrArg Checkpoint.next hd)

theorem changed_poststate_rejected (j : Job) (c : Checkpoint j)
    (r : Commit j) (v : StoreView) (h : r.after ≠ v) :
    acknowledge j c r v = .error "commit post-state differs from current store" := by
  simp [acknowledge, h]

theorem wrong_sequence_rejected (j : Job) (c : Checkpoint j)
    (r : Commit j) (v : StoreView) (hv : r.after = v)
    (hl : c.last ≠ some r) (hn : r.intent.sequence ≠ c.next) :
    acknowledge j c r v = .error "commit sequence mismatch" := by
  simp [acknowledge, hv, hl, hn]

theorem wrong_prestate_rejected (j : Job) (c : Checkpoint j)
    (r : Commit j) (v : StoreView) (hv : r.after = v)
    (hl : c.last ≠ some r) (hn : r.intent.sequence = c.next)
    (hb : r.intent.before ≠ view c.state) :
    acknowledge j c r v = .error "commit pre-state mismatch" := by
  simp [acknowledge, hv, hl, hn, hb]

theorem fresh_acknowledgement_cost (j : Job) (c d : Checkpoint j)
    (r : Commit j) (v : StoreView) (h : acknowledge j c r v = .ok d)
    (hfresh : r.intent.sequence = c.next) :
    d.state.core.spent = c.state.core.spent + fee (protocol j) c.state.core r.intent.action := by
  obtain ⟨_, hc | hn⟩ := acknowledge_contract j c d r v h
  · have hn := hc.2.2.1
    omega
  · obtain ⟨_, _, t, ht, hd⟩ := hn
    subst d
    exact accepted_step_cost j c.state t (event r) ht

theorem recovered_safe (j : Job) (c d : Checkpoint j) (o : Outcome j)
    (v : StoreView) (hs : Safe j c) (h : recover j c o v = .ok d) : Safe j d := by
  cases o with
  | unfinished i => simp [recover] at h
  | committed r => exact acknowledge_safe j c d r v hs h

/-- Replay of committed records, including harmless exact duplicate records. -/
def replay (j : Job) : Checkpoint j → List (Commit j) → Except String (Checkpoint j)
  | c, [] => .ok c
  | c, r :: rs => match acknowledge j c r r.after with
    | .error msg => .error msg
    | .ok d => replay j d rs

theorem replay_safe (j : Job) (rs : List (Commit j)) (c d : Checkpoint j)
    (hs : Safe j c) (h : replay j c rs = .ok d) : Safe j d := by
  induction rs generalizing c with
  | nil => have he : c = d := by simpa [replay] using h
           exact he ▸ hs
  | cons r rs ih =>
      cases ha : acknowledge j c r r.after with
      | error msg => simp [replay, ha] at h
      | ok e =>
          exact ih e (acknowledge_safe j c e r r.after hs ha)
            (by simpa [replay, ha] using h)

theorem replay_initial_safe (j : Job) (rs : List (Commit j)) (c : Checkpoint j)
    (h : replay j (initial j) rs = .ok c) : Safe j c :=
  replay_safe j rs (initial j) c (initial_safe j) h

theorem replay_no_overspend (j : Job) (rs : List (Commit j)) (c : Checkpoint j)
    (h : replay j (initial j) rs = .ok c) : c.state.core.spent ≤ j.budget := by
  have hb := (replay_initial_safe j rs c h).1.1.2
  omega

theorem recovered_admission_valid (j : Job) (c d : Checkpoint j) (o : Outcome j)
    (v : StoreView) (hs : Safe j c) (h : recover j c o v = .ok d)
    (t : Ticket) (ht : d.state.admitted = some t) :
    Valid t.artifact ∧ SourceParsed t.artifact :=
  (recovered_safe j c d o v hs h).2 t ht

theorem recovered_false_admission_impossible (j : Job) (c d : Checkpoint j)
    (o : Outcome j) (v : StoreView) (hs : Safe j c) (h : recover j c o v = .ok d)
    (t : Ticket) (ht : d.state.admitted = some t)
    (hc : context t.artifact.identity = [])
    (hf : t.artifact.identity.statement = Certificate.Formula.falsity) : False := by
  have hv := (recovered_admission_valid j c d o v hs h t ht).1
  have truth := hv (fun _ => False) (by simp [Certificate.Satisfies, hc])
  simp only [hf, Certificate.Denote] at truth

end Komorebi.AVOC.CommitRecovery
