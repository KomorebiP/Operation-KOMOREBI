import AVOC.PlannerRuntime

open Lean Komorebi.AVOC
open ArtifactWorkflow PlannerRuntime

namespace AVOCPlannerCLI

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
  ("pending",toJson s.slot.pending.isSome),
  ("checked",toJson s.checked.isSome),
  ("next_generation",num s.slot.nextGeneration),
  ("research_remaining",num s.budget),("research_spent",num s.spent),
  ("halted",toJson s.halted)]

def recommendationJson (j : Job) (horizon : Nat)
    (r : ExecutablePlanner.Recommendation (Action (Fin 1) (Fin j.artifacts.size))) : Json :=
  let tail : ℚ := ((horizon - r.depth : Nat) : ℚ) * rewardBound j
  obj [("requested_horizon",num horizon),("searched_depth",num r.depth),
    ("searched",toJson r.searched),("action",actionJson r.action),
    ("lookahead_value",rat r.score),("value_lower",rat (r.score-tail)),
    ("value_upper",rat (r.score+tail)),("selected_action_regret_upper",rat (2*tail)),
    ("exact_full_horizon",toJson (r.depth == horizon)),
    ("work_used",num r.work),("work_reserved",num r.reservation),
    ("per_decision_credit",num j.credit),("unused_credit",num r.remaining),
    ("declared_planning_charge",rat (j.price * (r.work:ℚ)))]

structure TraceResult where
  records : List Json
  final : State Bool (Fin 1)
  work : Nat
  gross : ℚ
  unusedReports : List Bool

/-- Reports are caller-supplied public observations. This is not a filesystem
orchestrator and does not sample or claim to observe a real tool. -/
def runTrace (j : Job) : (n : Nat) → State Bool (Fin 1) → List Bool →
    Option (ExecutablePlanner.Recommendation (Action (Fin 1) (Fin j.artifacts.size))) →
    Except String TraceResult
  | 0, s, reports, _ => .ok ⟨[],s,0,0,reports⟩
  | n+1, s, reports, first => do
      let r := match first with
        | some cached => cached
        | none => recommend j (n+1) s
      let (report,rest) ← match r.action with
        | .verify => match reports with
          | [] => .error "verification requires one supplied public report"
          | d::ds => .ok (d,ds)
        | _ => .ok (false,reports)
      let model := runtimeModel j
      if !(WorkflowPlanner.allowedCheck (protocol j) [0] s r.action) then
        throw "internal guard mismatch"
      if model.prob s r.action report = 0 then
        throw "supplied report has zero model probability"
      let next := model.step s r.action report
      let gain := model.reward s r.action
      let row := obj [("before",stateJson s),("recommendation",recommendationJson j (n+1) r),
        ("report",toJson report),("report_probability",rat (model.prob s r.action report)),
        ("stage_fee",num (fee (protocol j) s r.action)),("stage_reward",rat gain),
        ("after",stateJson next)]
      if next.halted then
        return ⟨[row],next,r.work,gain,rest⟩
      let tail ← runTrace j n next rest none
      return ⟨row::tail.records,tail.final,r.work+tail.work,gain+tail.gross,tail.unusedReports⟩

def policyBound (j : Job) : ℚ :=
  ((List.range j.horizon).map fun k =>
    2 * ((k+1-ExecutablePlanner.selectedDepth (3+j.artifacts.size) 2 (k+1) j.credit:Nat):ℚ)
      * rewardBound j).sum

def execute (wire : Json) : Except String Json := do
  let j ← parseJob wire
  if j.horizon = 0 then throw "runtime horizon must be at least one"
  let s := initial j
  let r := recommend j j.horizon s
  let mut fields := [("status",.str "ok"),("backend",.str "AVOC-v0.18-executed-Lean-planner"),
    ("root",recommendationJson j j.horizon r),("initial",stateJson s),
    ("reward_magnitude_bound",rat (rewardBound j)),
    ("complete_policy_regret_upper",rat (policyBound j)),
    ("total_planning_work_cap",num (j.horizon*j.credit)),
    ("declared_planning_charge_cap",rat (j.price * (j.horizon*j.credit:Nat))),
    ("charged_policy_loss_upper",rat (policyBound j + j.price*(j.horizon*j.credit:Nat))),
    ("cost_scope",.str "tree-state/action/observation units; excludes parser, reservation arithmetic, rational bit cost and model-callback internals"),
    ("trace_scope",.str "protected fixed-catalogue model; supplied reports; no real filesystem admission")]
  if j.runTrace then
    let t ← runTrace j j.horizon s j.reports (some r)
    fields := fields ++ [("trace",toJson t.records),("final",stateJson t.final),
      ("planning_work_total",num t.work),("realized_stage_return",rat t.gross),
      ("declared_planning_charge_total",rat (j.price*(t.work:ℚ))),
      ("realized_return_less_declared_planning_charge",rat (t.gross-j.price*(t.work:ℚ))),
      ("unused_reports",toJson t.unusedReports)]
  else
    fields := fields ++ [("planning_work_total",num r.work)]
  return obj fields

end AVOCPlannerCLI

/-- Trusted I/O wrapper. Candidates remain proof data, never executable Lean. -/
def main (args : List String) : IO UInt32 := do
  let (batch,path) ← match args with
    | [p] => pure (false,p)
    | ["--batch",p] => pure (true,p)
    | _ => IO.eprintln "usage: PlannerMain [--batch] request.json" *> pure (false,"")
  if path.isEmpty then return 2
  let input ← IO.FS.readFile path
  if input.utf8ByteSize > (if batch then 8388608 else 65536) then
    IO.eprintln "input byte limit"; return 2
  match Json.parse input with
  | .error e => IO.eprintln e; return 2
  | .ok wire =>
    if batch then
      match wire.getArr? with
      | .error e => IO.eprintln e; return 2
      | .ok jobs =>
        if jobs.size > 2500 then IO.eprintln "batch count limit"; return 2
        for job in jobs do
          let out := match AVOCPlannerCLI.execute job with
            | .ok x => x
            | .error e => Json.mkObj [("status",.str "error"),("error",.str e)]
          IO.println out.compress
        return 0
    else
      match AVOCPlannerCLI.execute wire with
      | .error e => IO.eprintln e; return 2
      | .ok result => IO.println result.compress; return 0
