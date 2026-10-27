import AVOC.RecoveryCodec

open Lean Komorebi.AVOC
open ArtifactWorkflow PlannerRuntime LiveExecution CommitRecovery

namespace AVOCRecoveryCLI

def stateJson (s : State Bool (Fin 1)) : Json := Json.mkObj [
  ("posterior_true",toJson (toString (s.belief.prob true))),
  ("completed",toJson (decide (0 ∈ s.completed))),
  ("pending",toJson s.slot.pending.isSome),("checked",toJson s.checked.isSome),
  ("next_generation",toJson s.slot.nextGeneration),
  ("research_remaining",toJson s.budget),("research_spent",toJson s.spent),
  ("halted",toJson s.halted)]

def execute (wire : Json) : Except String Json := do
  match (← wire.getArr?).toList with
  | [.str "avoc-recovery-v1", job, identity, records, incoming, actual] =>
    let j ← parseLiveJob job identity
    let actual ← parseView actual
    let before ← decodeCheckpoint j records
    let (after, kind) ← match incoming with
      | .null => do
        let c ← resumeCheckpoint j records actual
        pure (c,"matched_checkpoint")
      | w => do
        let r ← parseCommit j w
        let c ← recoverDecoded j records r actual
        pure (c, if c.next = before.next then "already_acknowledged" else "recovered_commit")
    if after.next > j.horizon then throw "recovered count exceeds declared horizon"
    return Json.mkObj [("status",.str "ok"),("backend",.str "AVOC-v0.20-recovery-monitor"),
      ("disposition",.str kind),("confirmed_steps",toJson after.next),
      ("matched_external",.bool true),("new_planning_work",toJson (0:Nat)),
      ("current",stateJson after.state.core)]
  | _ => throw "invalid recovery-monitor request"

end AVOCRecoveryCLI

def main (args : List String) : IO UInt32 := do
  match args with
  | [path] =>
    let raw ← IO.FS.readFile path
    if raw.utf8ByteSize > 4194304 then IO.eprintln "recovery request byte limit"; return 2
    match Json.parse raw with
    | .error e => IO.eprintln e; return 2
    | .ok wire => match AVOCRecoveryCLI.execute wire with
      | .error e => IO.eprintln e; return 2
      | .ok result => IO.println result.compress; return 0
  | _ => IO.eprintln "usage: RecoveryMain request.json"; return 2
