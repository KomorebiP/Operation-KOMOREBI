import AVOC.LiveExecutionCodec

open Lean Komorebi.AVOC
open ArtifactWorkflow PlannerRuntime LiveExecution

namespace AVOCExternalCLI

def obj (xs : List (String × Json)) : Json := Json.mkObj xs
def num (n : Nat) : Json := toJson n
def rat (q : ℚ) : Json := Json.str (toString q)

def actionJson {n : Nat} : Action (Fin 1) (Fin n) → Json
  | .register _ c => obj [("kind",.str "register"),("candidate",num c.val)]
  | .verify => obj [("kind",.str "verify")]
  | .admit => obj [("kind",.str "admit")]
  | .stop => obj [("kind",.str "stop")]

def stateJson (s : State Bool (Fin 1)) : Json := obj [
  ("posterior_true",rat (s.belief.prob true)),
  ("completed",toJson (decide (0 ∈ s.completed))),
  ("pending",toJson s.slot.pending.isSome),("checked",toJson s.checked.isSome),
  ("next_generation",num s.slot.nextGeneration),
  ("research_remaining",num s.budget),("research_spent",num s.spent),
  ("halted",toJson s.halted)]

def execute (wire : Json) : Except String Json := do
  match (← wire.getArr?).toList with
  | [.str "avoc-live-v1", job, identity, events, actual, .str mode] =>
    if mode != "plan" && mode != "observe" then throw "mode must be plan or observe"
    let j ← parseLiveJob job identity
    let actual ← parseView actual
    let (es,s) ← resume j events actual
    let n := j.horizon - es.length
    let mut fields := [("status",.str "ok"),("backend",.str "AVOC-v0.19-live-monitor"),
      ("confirmed_steps",num es.length),("horizon_remaining",num n),
      ("current",stateJson s.core),("matched_external",.bool true),
      ("new_planning_work",num 0),("recommendation",.null)]
    if mode == "plan" && n > 0 && !s.core.halted then
      let r := recommend j n s.core
      let tail : ℚ := ((n-r.depth : Nat):ℚ) * rewardBound j
      fields := fields.filter (fun x => x.1 != "new_planning_work" && x.1 != "recommendation")
      fields := fields ++ [("new_planning_work",num r.work),
        ("recommendation",obj [("action",actionJson r.action),("searched_depth",num r.depth),
          ("searched",toJson r.searched),("exact_full_horizon",toJson (r.depth == n)),
          ("lookahead_value",rat r.score),("selected_action_regret_upper",rat (2*tail)),
          ("work_used",num r.work),("work_reserved",num r.reservation),
          ("unused_credit",num r.remaining),("per_decision_credit",num j.credit),
          ("declared_planning_charge",rat (j.price*(r.work:ℚ)))])]
    return obj fields
  | _ => throw "invalid live-monitor request"

end AVOCExternalCLI

def main (args : List String) : IO UInt32 := do
  match args with
  | [path] =>
    let raw ← IO.FS.readFile path
    if raw.utf8ByteSize > 2097152 then IO.eprintln "live request byte limit"; return 2
    match Json.parse raw with
    | .error e => IO.eprintln e; return 2
    | .ok wire =>
      match AVOCExternalCLI.execute wire with
      | .error e => IO.eprintln e; return 2
      | .ok result => IO.println result.compress; return 0
  | _ => IO.eprintln "usage: LivePlannerMain request.json"; return 2
