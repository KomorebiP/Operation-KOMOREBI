import AVOC.AtomicCommitModel
import AVOC.LiveExecutionCodec

namespace Komorebi.AVOC.CommitRecovery
open Lean Binding PlannerRuntime LiveExecution ArtifactWorkflow

def parseIntent (j : Job) (wire : Json) : Except String (Intent j) := do
  match (← wire.getArr?).toList with
  | [sequence, before, action] => return ⟨← sequence.getNat?, ← parseView before, ← parseAction j action⟩
  | _ => throw "invalid recovery intent"

def parseCommit (j : Job) (wire : Json) : Except String (Commit j) := do
  match (← wire.getArr?).toList with
  | [intent, .bool report, after] => return ⟨← parseIntent j intent, report, ← parseView after⟩
  | _ => throw "invalid commit receipt"

/-- Decoder invokes the proved reconciliation code on the parsed records.
No parsed record is itself evidence that the SQLite backend committed it. -/
def decodeCheckpoint (j : Job) (wire : Json) : Except String (Checkpoint j) :=
  match wire.getArr? with
  | .error e => .error e
  | .ok arr => match arr.toList.mapM (parseCommit j) with
    | .error e => .error e
    | .ok rs =>
      if rs.length > j.horizon then .error "commit history exceeds horizon"
      else CommitRecovery.replay j (CommitRecovery.initial j) rs

theorem decodeCheckpoint_safe (j : Job) (wire : Json) (c : Checkpoint j)
    (h : decodeCheckpoint j wire = .ok c) : Safe j c := by
  cases hw : wire.getArr? with
  | error msg => simp [decodeCheckpoint, hw] at h
  | ok arr =>
      cases hr : arr.toList.mapM (parseCommit j) with
      | error msg => simp [decodeCheckpoint, hw, hr] at h
      | ok rs =>
          by_cases hl : rs.length > j.horizon
          · simp [decodeCheckpoint, hw, hr, hl] at h
          · exact replay_initial_safe j rs c (by simpa [decodeCheckpoint, hw, hr, hl] using h)

def resumeCheckpoint (j : Job) (wire : Json) (actual : StoreView) :
    Except String (Checkpoint j) :=
  match decodeCheckpoint j wire with
  | .error e => .error e
  | .ok c => if view c.state = actual then .ok c else .error "checkpoint/store mismatch"

theorem resumeCheckpoint_contract (j : Job) (wire : Json) (actual : StoreView)
    (c : Checkpoint j) (h : resumeCheckpoint j wire actual = .ok c) :
    Safe j c ∧ view c.state = actual := by
  cases hc : decodeCheckpoint j wire with
  | error msg => simp [resumeCheckpoint, hc] at h
  | ok d =>
      by_cases hv : view d.state = actual
      · have he : d = c := by simpa [resumeCheckpoint, hc, hv] using h
        subst c
        exact ⟨decodeCheckpoint_safe j wire d hc, hv⟩
      · simp [resumeCheckpoint, hc, hv] at h

/-- A committed-but-unacknowledged operation may be added to the checkpoint
only by the same exact transition checker used for normal acknowledgement. -/
def recoverDecoded (j : Job) (wire : Json) (r : Commit j) (actual : StoreView) :
    Except String (Checkpoint j) :=
  match decodeCheckpoint j wire with
  | .error e => .error e
  | .ok c => acknowledge j c r actual

theorem recoverDecoded_contract (j : Job) (wire : Json) (r : Commit j)
    (actual : StoreView) (d : Checkpoint j)
    (h : recoverDecoded j wire r actual = .ok d) :
    Safe j d ∧ view d.state = actual ∧ d.next = r.intent.sequence + 1 := by
  cases hc : decodeCheckpoint j wire with
  | error msg => simp [recoverDecoded, hc] at h
  | ok c =>
      have ha : acknowledge j c r actual = .ok d := by simpa [recoverDecoded, hc] using h
      have hs := acknowledge_safe j c d r actual (decodeCheckpoint_safe j wire c hc) ha
      obtain ⟨_,hn,hv⟩ := acknowledge_result_identity j c d r actual ha
      exact ⟨hs,hv,hn⟩

theorem recoverDecoded_no_overspend (j : Job) (wire : Json) (r : Commit j)
    (actual : StoreView) (d : Checkpoint j)
    (h : recoverDecoded j wire r actual = .ok d) : d.state.core.spent ≤ j.budget := by
  have hb := (recoverDecoded_contract j wire r actual d h).1.1.1.2
  omega

end Komorebi.AVOC.CommitRecovery
