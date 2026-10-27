import Mathlib.Data.List.Basic

namespace Komorebi.AVOC.CalibrationLog

/-- Only checked binary outcomes are statistical observations. -/
inductive Outcome where
  | success | rejection | fault | unfinished
  deriving DecidableEq, Repr

def Outcome.sample : Outcome → Option Bool
  | .success => some true
  | .rejection => some false
  | .fault => none
  | .unfinished => none

structure Event (Key : Type) where
  operation : Nat
  key : Key
  outcome : Outcome
  deriving DecidableEq

variable {Key : Type} [DecidableEq Key]

/-- Exact replay is idempotent; reuse of an operation id with any changed
field is rejected. A new id appends exactly one event. -/
def record (log : List (Event Key)) (e : Event Key) : Option (List (Event Key)) :=
  if e ∈ log then some log
  else if ∃ old ∈ log, old.operation = e.operation then none
  else some (log ++ [e])

/-- Identity strata are compared by equality, not by a hash assumption. -/
def samples (key : Key) (log : List (Event Key)) : List Bool :=
  log.filterMap fun e => if e.key = key then e.outcome.sample else none

@[simp] theorem exact_replay (log : List (Event Key)) (e : Event Key)
    (h : e ∈ log) : record log e = some log := by
  simp [record, h]

theorem conflicting_replay (log : List (Event Key)) (e : Event Key)
    (hnew : e ∉ log) (hid : ∃ old ∈ log, old.operation = e.operation) :
    record log e = none := by
  simp [record, hnew, hid]

theorem fresh_record (log : List (Event Key)) (e : Event Key)
    (hid : ¬ ∃ old ∈ log, old.operation = e.operation) :
    record log e = some (log ++ [e]) := by
  have hnew : e ∉ log := by
    intro h
    exact hid ⟨e, h, rfl⟩
  simp [record, hnew, hid]

theorem accepted_mem {log after : List (Event Key)} {e : Event Key}
    (h : record log e = some after) : e ∈ after := by
  unfold record at h
  split at h
  · simp_all
  · split at h
    · simp at h
    · have he : log ++ [e] = after := Option.some.inj h
      rw [← he]
      simp

theorem accepted_replay {log after : List (Event Key)} {e : Event Key}
    (h : record log e = some after) : record after e = some after :=
  exact_replay after e (accepted_mem h)

@[simp] theorem samples_append (key : Key) (a b : List (Event Key)) :
    samples key (a ++ b) = samples key a ++ samples key b := by
  simp [samples]

@[simp] theorem fault_not_observation (key eventKey : Key) (id : Nat)
    (log : List (Event Key)) :
    samples key (log ++ [⟨id, eventKey, .fault⟩]) = samples key log := by
  simp [samples, Outcome.sample]

@[simp] theorem unfinished_not_observation (key eventKey : Key) (id : Nat)
    (log : List (Event Key)) :
    samples key (log ++ [⟨id, eventKey, .unfinished⟩]) = samples key log := by
  simp [samples, Outcome.sample]

@[simp] theorem success_observation (key : Key) (id : Nat)
    (log : List (Event Key)) :
    samples key (log ++ [⟨id, key, .success⟩]) = samples key log ++ [true] := by
  simp [samples, Outcome.sample]

@[simp] theorem rejection_observation (key : Key) (id : Nat)
    (log : List (Event Key)) :
    samples key (log ++ [⟨id, key, .rejection⟩]) = samples key log ++ [false] := by
  simp [samples, Outcome.sample]

theorem different_identity_no_observation (key : Key) (e : Event Key)
    (log : List (Event Key)) (h : e.key ≠ key) :
    samples key (log ++ [e]) = samples key log := by
  simp [samples, h]

theorem replay_preserves_samples (key : Key) (log : List (Event Key))
    (e : Event Key) (h : e ∈ log) :
    (record log e).map (samples key) = some (samples key log) := by
  simp [exact_replay log e h]

/-- Refresh is permitted only between episodes, without an unresolved intent.
This gate does not assert that a supplied new quote is statistically calibrated. -/
def refresh {Quote : Type} (inFlight : Bool) (next : Quote) : Option Quote :=
  if inFlight then none else some next

@[simp] theorem pending_intent_blocks_refresh {Quote : Type} (next : Quote) :
    refresh true next = none := rfl

@[simp] theorem fresh_episode_refresh {Quote : Type} (next : Quote) :
    refresh false next = some next := rfl

end Komorebi.AVOC.CalibrationLog
