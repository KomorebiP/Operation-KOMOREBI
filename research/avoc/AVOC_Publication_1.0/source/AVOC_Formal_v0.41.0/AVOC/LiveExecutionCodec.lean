import AVOC.LiveExecution

namespace Komorebi.AVOC.LiveExecution
open Lean Binding PlannerRuntime ArtifactWorkflow

/-- This first live adapter is a fresh single-root run. Dependency-bearing
artifacts require a different runtime task model and are explicitly rejected. -/
def parseLiveJob (wire identity : Json) : Except String Job := do
  let j ← parseJob wire
  let i ← parseIdentity identity
  if j.horizon = 0 then throw "positive horizon required"
  if j.runTrace || !j.reports.isEmpty then throw "supplied reports are forbidden for live jobs"
  if !i.dependencies.isEmpty then throw "live adapter supports one root without dependencies"
  if i.statement != j.identity.statement then throw "target formula mismatch"
  let artifacts ← j.artifacts.mapM fun a => parseRetained i a.val.sourceBytes
  return { j with identity := i, artifacts := artifacts }

def parseOptional (f : Json → Except String α) : Json → Except String (Option α)
  | .null => .ok none
  | j => return some (← f j)

def parseView (wire : Json) : Except String StoreView := do
  match (← wire.getArr?).toList with
  | [slot, checked, admitted] =>
      return ⟨← parseSlot slot, ← parseOptional parseReceipt checked,
        ← parseOptional parseTicket admitted⟩
  | _ => throw "invalid external store view"

def parseAction (j : Job) (wire : Json) : Except String (Action (Fin 1) (Fin j.artifacts.size)) := do
  match (← wire.getArr?).toList with
  | [.str "register", c] =>
      let c ← c.getNat?
      if hc : c < j.artifacts.size then return .register 0 ⟨c,hc⟩
      else throw "candidate index outside catalogue"
  | [.str "verify"] => return .verify
  | [.str "admit"] => return .admit
  | [.str "stop"] => return .stop
  | _ => throw "invalid live action"

def parseObservation (wire : Json) : Except String Observation := do
  match (← wire.getArr?).toList with
  | [.str "report", .bool d, actual] => return .confirmed d (← parseView actual)
  | [.str "fault", .str why] => return .fault why
  | _ => throw "invalid external observation"

def parseEvent (j : Job) (wire : Json) : Except String (Event j) := do
  match (← wire.getArr?).toList with
  | [a, obs] => return (← parseAction j a, ← parseObservation obs)
  | _ => throw "invalid live event"

/-- A successful decode identifies the actual executed replay checker. The
source of the external snapshots is an explicit I/O trust boundary. -/
def decodeReplay (j : Job) (wire : Json) : Except String (List (Event j) × RunState) :=
  match wire.getArr? with
  | .error e => .error e
  | .ok arr => match arr.toList.mapM (parseEvent j) with
    | .error e => .error e
    | .ok events =>
      if events.length > j.horizon then .error "history exceeds declared horizon"
      else match replay j (initialRun j) events with
        | .error e => .error e
        | .ok s => .ok (events,s)

theorem decoded_replay_safe (j : Job) (events : List (Event j)) (s : RunState)
    (h : replay j (initialRun j) events = .ok s) :
    SourceSafe (protocol j) j.budget s.core := replay_initial_source_safe j events s h

/-- The same exact view gate used by the I/O endpoint. -/
def agrees (expected actual : StoreView) : Bool := decide (expected = actual)

@[simp] theorem agrees_iff (expected actual : StoreView) :
    agrees expected actual = true ↔ expected = actual := by simp [agrees]

theorem changed_pending_rejected (expected actual : StoreView)
    (h : expected.slot.pending ≠ actual.slot.pending) : agrees expected actual = false := by
  apply Bool.eq_false_iff.mpr
  intro he
  exact h (congrArg (fun x : StoreView => x.slot.pending) ((agrees_iff _ _).1 he))

theorem changed_checked_receipt_rejected (expected actual : StoreView)
    (h : expected.checked ≠ actual.checked) : agrees expected actual = false := by
  apply Bool.eq_false_iff.mpr
  intro he
  exact h (congrArg StoreView.checked ((agrees_iff _ _).1 he))

theorem changed_admission_rejected (expected actual : StoreView)
    (h : expected.admitted ≠ actual.admitted) : agrees expected actual = false := by
  apply Bool.eq_false_iff.mpr
  intro he
  exact h (congrArg StoreView.admitted ((agrees_iff _ _).1 he))

theorem changed_generation_rejected (expected actual : StoreView)
    (h : expected.slot.nextGeneration ≠ actual.slot.nextGeneration) : agrees expected actual = false := by
  apply Bool.eq_false_iff.mpr
  intro he
  exact h (congrArg (fun x : StoreView => x.slot.nextGeneration) ((agrees_iff _ _).1 he))

theorem decodeReplay_contract (j : Job) (wire : Json)
    (es : List (Event j)) (s : RunState) (h : decodeReplay j wire = .ok (es,s)) :
    replay j (initialRun j) es = .ok s := by
  cases hw : wire.getArr? with
  | error e => simp [decodeReplay, hw] at h
  | ok arr =>
    cases hp : arr.toList.mapM (parseEvent j) with
    | error e => simp [decodeReplay, hw, hp] at h
    | ok events =>
      by_cases hl : events.length > j.horizon
      · simp [decodeReplay, hw, hp, hl] at h
      · cases hr : replay j (initialRun j) events with
        | error e => simp [decodeReplay, hw, hp, hl, hr] at h
        | ok state =>
          have he : (events,state) = (es,s) := by
            simpa [decodeReplay, hw, hp, hl, hr] using h
          cases he
          exact hr

/-- The endpoint's full decode, replay and current-store agreement function. -/
def resume (j : Job) (wire : Json) (actual : StoreView) :
    Except String (List (Event j) × RunState) :=
  match decodeReplay j wire with
  | .error e => .error e
  | .ok (es,s) => if agrees (view s) actual then .ok (es,s)
    else .error "current external store disagrees with confirmed history"

theorem resume_contract (j : Job) (wire : Json) (actual : StoreView)
    (es : List (Event j)) (s : RunState) (h : resume j wire actual = .ok (es,s)) :
    replay j (initialRun j) es = .ok s ∧ view s = actual := by
  cases hd : decodeReplay j wire with
  | error e => simp [resume, hd] at h
  | ok pair =>
    obtain ⟨events,state⟩ := pair
    by_cases ha : agrees (view state) actual = true
    · have he : (events,state) = (es,s) := by simpa [resume,hd,ha] using h
      have hr := decodeReplay_contract j wire events state hd
      have hv := (agrees_iff _ _).1 ha
      cases he
      exact ⟨hr,hv⟩
    · simp [resume,hd,ha] at h

theorem resumed_certificate (j : Job) (wire : Json) (actual : StoreView)
    (es : List (Event j)) (s : RunState) (h : resume j wire actual = .ok (es,s)) :
    SourceSafe (protocol j) j.budget s.core ∧ ArchiveSafe s ∧ view s = actual := by
  obtain ⟨hr,hv⟩ := resume_contract j wire actual es s h
  exact ⟨replay_initial_source_safe j es s hr, replay_initial_archive_safe j es s hr, hv⟩

theorem actual_admission_has_valid_source (j : Job) (wire : Json) (actual : StoreView)
    (es : List (Event j)) (s : RunState) (ticket : Ticket)
    (h : resume j wire actual = .ok (es,s)) (ha : actual.admitted = some ticket) :
    Valid ticket.artifact ∧ SourceParsed ticket.artifact := by
  obtain ⟨_, har, hv⟩ := resumed_certificate j wire actual es s h
  have he : s.admitted = actual.admitted := congrArg StoreView.admitted hv
  exact har ticket (he.trans ha)

theorem false_root_cannot_be_confirmed (j : Job) (wire : Json) (actual : StoreView)
    (es : List (Event j)) (s : RunState) (ticket : Ticket)
    (h : resume j wire actual = .ok (es,s)) (ha : actual.admitted = some ticket)
    (hc : context ticket.artifact.identity = [])
    (hf : ticket.artifact.identity.statement = Certificate.Formula.falsity) : False := by
  have hv := (actual_admission_has_valid_source j wire actual es s ticket h ha).1
  have ht := hv (fun _ => False) (by simp [Certificate.Satisfies, hc])
  simp only [hf, Certificate.Denote] at ht

end Komorebi.AVOC.LiveExecution
