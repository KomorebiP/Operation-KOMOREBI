import AVOC.StagedAffineOperational
import AVOC.AffineTerminalCodec
import AVOC.PlannerRuntime
import Lean

namespace Komorebi.AVOC.Affine.StagedCodec

open Lean
open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Staged
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Codec
open Komorebi.AVOC.Affine.FactorCodec
open Komorebi.AVOC.Affine.ReuseCodec
open Komorebi.AVOC.Affine.SearchGuard

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5

structure Probability where
  value : ℚ
  nonneg : 0 ≤ value
  le_one : value ≤ 1


def parseProbability (j : Json) : Except String Probability := do
  let q ← PlannerRuntime.parseRat j
  if h0 : 0 ≤ q then
    if h1 : q ≤ 1 then return ⟨q,h0,h1⟩
    else throw "probability exceeds one"
  else throw "negative probability"


def boundedNat (cap : Nat) (j : Json) : Except String Nat := do
  let n ← j.getNat?
  if n > cap then throw "integer cap exceeded"
  return n


def buildWarm {n m : Nat} (p : DenseProgram F n m) (r : Reuse.Record F n m)
    (q : Probability) : Option (OptionPlan .warm p) :=
  let credit := normalizationCost p + SearchGuard.reuseCharge n m r.candidate.width
  match h : warmFrom p r 0 credit with
  | none => none
  | some d => some {
      deployment := d
      source_eq := warmFrom_source h
      kind_eq := warmFrom_kind h
      successProb := q.value
      prob_nonneg := q.nonneg
      prob_le_one := q.le_one }


def buildCold {n m : Nat} (p : DenseProgram F n m) (c : Factorization.Candidate F n m)
    (generation : Nat) (q : Probability) : Option (OptionPlan .cold p) :=
  let credit := Factorization.upfront p c.width generation
  match h : coldFrom p c generation credit with
  | none => none
  | some d => some {
      deployment := d
      source_eq := coldFrom_source h
      kind_eq := coldFrom_kind h
      successProb := q.value
      prob_nonneg := q.nonneg
      prob_le_one := q.le_one }


def parseAction (s : String) : Except String Action :=
  match s with
  | "stop" => .ok .stop
  | "inspect_warm" => .ok .inspectWarm
  | "generate_cold" => .ok .generateCold
  | "deploy_warm" => .ok .deployWarm
  | "deploy_cold" => .ok .deployCold
  | _ => .error "unknown staged action"


def parseHistory (j : Json) : Except String (List (Action × Bool)) := do
  let xs ← j.getArr?
  if xs.size > 32 then throw "history cap"
  xs.toList.mapM fun z => do
    match (← z.getArr?).toList with
    | [.str a,o] => return (← parseAction a, ← o.getBool?)
    | _ => throw "history entries are [actionName,reportBool]"


def replay {n m : Nat} (md : Model n m) : State md →
    List (Action × Bool) → Except String (State md)
  | s, [] => .ok s
  | s, (a,o)::tail => do
      if _ha : a ∈ actions md s then
        if _hp : 0 < probability md s a o then
          replay md (step md s a o) tail
        else throw "report has zero probability under staged model"
      else throw "staged action is unavailable"


def statusWire : Status → Json
  | .untried => .str "untried"
  | .failed => .str "failed"
  | .ready => .str "ready"


def actionWire : Action → Json
  | .stop => Json.mkObj [("kind",.str "stop")]
  | .inspectWarm => Json.mkObj [("kind",.str "inspect_warm")]
  | .generateCold => Json.mkObj [("kind",.str "generate_cold")]
  | .deployWarm => Json.mkObj [("kind",.str "deploy_warm")]
  | .deployCold => Json.mkObj [("kind",.str "deploy_cold")]


def stateWire {n m : Nat} {md : Model n m} (s : State md) : Json :=
  Json.mkObj [("warm_status",statusWire s.warmStatus),
    ("cold_status",statusWire s.coldStatus),("budget",toJson s.budget),
    ("spent",toJson s.spent),("total",toJson s.total),("done",toJson s.done)]


def deploymentSummary {n m : Nat} (d : Deployment n m) (calls : Nat) : Json :=
  Json.mkObj [("setup",toJson d.setup),
    ("per_call_original",toJson (executionCost d.source)),
    ("per_call_selected",toJson (executionCost d.selected)),
    ("gross_saving",.str (toString ((calls : ℚ) *
      ((executionCost d.source : ℚ) - (executionCost d.selected : ℚ))))),
    ("net_payoff",.str (toString (d.payoff calls)))]


def process (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "staged-affine-f5-v1",source,warmJ,coldJ,callsJ,generationJ,
      warmProbJ,coldProbJ,budgetJ,horizonJ,historyJ] =>
      let compiled ← load source
      let p := compiled.parsed.program
      let n := compiled.parsed.input
      let m := compiled.parsed.output
      let record ← parseRecord n m warmJ
      let candidate ← parseCandidate n m coldJ
      let calls ← boundedNat 1000000 callsJ
      let generation ← boundedNat 100000000 generationJ
      let warmProb ← parseProbability warmProbJ
      let coldProb ← parseProbability coldProbJ
      let budget ← boundedNat 100000000 budgetJ
      let horizon ← boundedNat 8 horizonJ
      let history ← parseHistory historyJ
      let warm ← match buildWarm p record warmProb with
        | some q => pure q
        | none => throw "warm certificate rejected while constructing staged model"
      let cold ← match buildCold p candidate generation coldProb with
        | some q => pure q
        | none => throw "cold certificate rejected while constructing staged model"
      let md : Model n m := { source := p, calls := calls, warm := warm, cold := cold }
      let start := initial md budget
      let current ← replay md start history
      let result := ExecutablePlanner.evaluate (executable md) horizon current
      let choice := result.choice.getD .stop
      return Json.mkObj [("status",.str "optimal_staged_affine_policy"),
        ("field",.str "ZMod(5)"),("horizon",toJson horizon),
        ("choice",actionWire choice),("expected_net_value",.str (toString result.score)),
        ("planning_work",toJson result.work),("state",stateWire current),
        ("available_actions",toJson ((actionList md current).map actionWire)),
        ("warm_probability",.str (toString warm.successProb)),
        ("cold_probability",.str (toString cold.successProb)),
        ("warm",deploymentSummary warm.deployment calls),
        ("cold",deploymentSummary cold.deployment calls),
        ("scope",.str "certificate validation is performed to construct the typed executable model; logical setup fees are staged inside Bellman control; physical validator startup remains outside the model")]
  | _ => throw "unknown staged affine request"

end Komorebi.AVOC.Affine.StagedCodec
