import AVOC.ObservationRecorder
import AVOC.CalibrationCodec

namespace Komorebi.AVOC.RecorderCodec

open Lean ObservationRecorder

/-- Index-aware execution uses exactly the formal recorder transition. -/
def replayFrom {Key : Type} [DecidableEq Key] (s : State Key) (index : Nat) :
    List (Command Key) → Except Nat (State Key)
  | [] => .ok s
  | c :: cs => match step s c with
      | none => .error index
      | some t => replayFrom t (index + 1) cs

/-- Successful indexed execution and the core formal execution agree for every
finite command list. Rejected execution supplies no final recorder state. -/
theorem replayFrom_toOption {Key : Type} [DecidableEq Key] (s : State Key)
    (index : Nat) (commands : List (Command Key)) :
    (replayFrom s index commands).toOption = runFrom s commands := by
  induction commands generalizing s index with
  | nil => rfl
  | cons c cs ih =>
    cases h : step s c with
    | none => simp [replayFrom, runFrom, h, Except.toOption]
    | some t => simpa [replayFrom, runFrom, h] using ih t (index + 1)

def parseCommand (j : Json) : Except String (Command Nat) := do
  match (← j.getArr?).toList with
  | [.str "begin", id, key] =>
      return .begin (← CalibrationCodec.exactNat 2147483647 id)
        (← CalibrationCodec.exactNat 2147483647 key)
  | [.str "finish", id, key, .str outcome] =>
      let operation ← CalibrationCodec.exactNat 2147483647 id
      let identity ← CalibrationCodec.exactNat 2147483647 key
      let status ← match outcome with
        | "success" => pure CalibrationLog.Outcome.success
        | "rejection" => pure CalibrationLog.Outcome.rejection
        | "fault" => pure CalibrationLog.Outcome.fault
        | _ => throw "terminal outcome required"
      return .finish ⟨operation, identity, status⟩
  | _ => throw "malformed recorder command"

def parseCommands (j : Json) : Except String (List (Command Nat)) := do
  let a ← j.getArr?
  if a.size > 4096 then throw "command cap"
  a.toList.mapM parseCommand

def outcomeWire : CalibrationLog.Outcome → Json
  | .success => .str "success"
  | .rejection => .str "rejection"
  | .fault => .str "fault"
  | .unfinished => .str "unfinished"

def stateWire (s : State Nat) : Json := Json.mkObj [
  ("status", .str "recorded"),
  ("pending", .arr (s.pending.map (fun p => .arr #[toJson p.1, toJson p.2])).toArray),
  ("log", .arr (s.log.map (fun e => .arr
    #[toJson e.operation, toJson e.key, outcomeWire e.outcome])).toArray),
  ("ready", toJson s.pending.isEmpty)]

def replayWire (commands : List (Command Nat)) : Json :=
  match replayFrom initial 0 commands with
  | .ok s => stateWire s
  | .error i => Json.mkObj [("status", .str "rejected"),
      ("index", toJson i), ("error", .str "command_rejected")]

def process (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "observation-recorder-v1", commands] =>
      return replayWire (← parseCommands commands)
  | [.str "observation-recorder-batch-v1", requests] =>
      let a ← requests.getArr?
      if a.size > 256 then throw "batch cap"
      let parsed ← a.toList.mapM parseCommands
      if (parsed.map List.length).sum > 16384 then throw "aggregate command cap"
      return Json.mkObj [("status", .str "recorder_batch"),
        ("results", .arr (parsed.map replayWire).toArray)]
  | _ => throw "unknown recorder request"

end Komorebi.AVOC.RecorderCodec
