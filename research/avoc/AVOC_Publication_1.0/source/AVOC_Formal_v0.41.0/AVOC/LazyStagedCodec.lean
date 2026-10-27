import AVOC.LazyStagedRecovery
import AVOC.StagedAffineCodec
import Lean

namespace Komorebi.AVOC.Affine.LazyStagedCodec

open Lean
open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Factorization
open Komorebi.AVOC.Affine.Codec
open Komorebi.AVOC.Affine.FactorCodec
open Komorebi.AVOC.Affine.ReuseCodec
open Komorebi.AVOC.Affine.Staged (Action Status)
open Komorebi.AVOC.Affine.StagedCodec
open Komorebi.AVOC.Affine.LazyStaged

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5

structure ParsedQuote where
  fee : Nat
  gross : ℚ
  gross_nonneg : 0 ≤ gross
  probability : Probability


def parseQuote (j : Json) : Except String ParsedQuote := do
  match (← j.getArr?).toList with
  | [feeJ,grossJ,probJ] =>
      let fee ← StagedCodec.boundedNat 100000000 feeJ
      let gross ← PlannerRuntime.parseRat grossJ
      if hg : 0 ≤ gross then
        return ⟨fee,gross,hg,← parseProbability probJ⟩
      else throw "negative gross saving"
  | _ => throw "quote is [fee,gross,successProbability]"


def mkQuote (k : Kind) (q : ParsedQuote) : Quote k where
  fee := q.fee
  gross := q.gross
  gross_nonneg := q.gross_nonneg
  successProb := q.probability.value
  prob_nonneg := q.probability.nonneg
  prob_le_one := q.probability.le_one


def parseStatus : Json → Except String Status
  | .str "untried" => .ok .untried
  | .str "failed" => .ok .failed
  | .str "ready" => .ok .ready
  | _ => .error "status must be untried, failed or ready"


def parseAction : Json → Except String Action
  | .str "stop" => .ok .stop
  | .str "inspect_warm" => .ok .inspectWarm
  | .str "generate_cold" => .ok .generateCold
  | .str "deploy_warm" => .ok .deployWarm
  | .str "deploy_cold" => .ok .deployCold
  | _ => .error "unknown lazy staged action"


def parsePlan (md : Model n m) (j : Json) : Except String (PlanState md) := do
  match (← j.getArr?).toList with
  | [warmJ,coldJ,budgetJ,spentJ,totalJ,doneJ] =>
      let s : PlanState md :=
        ⟨← parseStatus warmJ,← parseStatus coldJ,
          ← StagedCodec.boundedNat 100000000 budgetJ,← StagedCodec.boundedNat 100000000 spentJ,
          ← StagedCodec.boundedNat 100000000 totalJ,← doneJ.getBool?⟩
      if s.budget + s.spent = s.total then return s
      else throw "budget + spent must equal total"
  | _ => throw "state is [warmStatus,coldStatus,budget,spent,total,done]"


def statusWire : Status → Json
  | .untried => .str "untried"
  | .failed => .str "failed"
  | .ready => .str "ready"


def actionName : Action → String
  | .stop => "stop"
  | .inspectWarm => "inspect_warm"
  | .generateCold => "generate_cold"
  | .deployWarm => "deploy_warm"
  | .deployCold => "deploy_cold"


def actionWire (a : Action) : Json := .str (actionName a)


def planWire {md : Model n m} (s : PlanState md) : Json :=
  Json.arr #[statusWire s.warmStatus,statusWire s.coldStatus,toJson s.budget,
    toJson s.spent,toJson s.total,toJson s.done]


def mkModel (p : DenseProgram F n m) (calls : Nat)
    (w c : ParsedQuote) : Model n m :=
  { source := p, calls := calls, warm := mkQuote .warm w, cold := mkQuote .cold c }


def checkedWarm (md : Model n m) (r : Reuse.Record F n m) : Option (CheckedArtifact md .warm) :=
  match h : warmFrom md.source r 0 md.warm.fee with
  | none => none
  | some d =>
      if hs : d.setup = md.warm.fee then
        if hg : deploymentGross d md.calls = md.warm.gross then
          some {
            deployment := d
            kind_eq := warmFrom_kind h
            source_eq := warmFrom_source h
            setup_eq := hs
            gross_eq := hg }
        else none
      else none


def checkedCold (md : Model n m) (c : Candidate F n m) (generation : Nat) :
    Option (CheckedArtifact md .cold) :=
  match h : coldFrom md.source c generation md.cold.fee with
  | none => none
  | some d =>
      if hs : d.setup = md.cold.fee then
        if hg : deploymentGross d md.calls = md.cold.gross then
          some {
            deployment := d
            kind_eq := coldFrom_kind h
            source_eq := coldFrom_source h
            setup_eq := hs
            gross_eq := hg }
        else none
      else none


def parseOptionalWarm (md : Model n m) (status : Status) (j : Json) :
    Except String (Option (CheckedArtifact md .warm)) := do
  match status,j with
  | .ready,.null => throw "ready warm state requires retained warm certificate"
  | .ready,_ =>
      let r ← parseRecord n m j
      match checkedWarm md r with
      | some a => return some a
      | none => throw "retained warm certificate rejected or quote mismatch"
  | _,.null => return none
  | _,_ => throw "non-ready warm state must not carry a warm certificate"


def parseOptionalCold (md : Model n m) (status : Status) (j : Json) (generation : Nat) :
    Except String (Option (CheckedArtifact md .cold)) := do
  match status,j with
  | .ready,.null => throw "ready cold state requires retained cold certificate"
  | .ready,_ =>
      let c ← parseCandidate n m j
      match checkedCold md c generation with
      | some a => return some a
      | none => throw "retained cold certificate rejected or quote mismatch"
  | _,.null => return none
  | _,_ => throw "non-ready cold state must not carry a cold certificate"


def parseRuntime (md : Model n m) (stateJ warmJ coldJ : Json) (generation : Nat) :
    Except String (RuntimeState md) := do
  let p ← parsePlan md stateJ
  let w ← parseOptionalWarm md p.warmStatus warmJ
  let c ← parseOptionalCold md p.coldStatus coldJ generation
  return ⟨p,w,c⟩


def resultArtifactWire {md : Model n m} {k : Kind} (a : CheckedArtifact md k) : Json :=
  Json.mkObj [
    ("kind",.str (match k with | .warm => "warm" | .cold => "cold")),
    ("setup",toJson a.deployment.setup),
    ("source_cost",toJson (executionCost a.deployment.source)),
    ("selected_cost",toJson (executionCost a.deployment.selected)),
    ("gross",.str (toString (deploymentGross a.deployment md.calls)))]


def planReply (md : Model n m) (s : PlanState md) (h : Nat) : Json :=
  let r := ExecutablePlanner.evaluate (executable md) h s
  Json.mkObj [("status",.str "lazy_staged_recommendation"),
    ("choice",actionWire (r.choice.getD .stop)),
    ("expected_value",.str (toString r.score)),
    ("planning_work",toJson r.work),
    ("state",planWire s),
    ("available_actions",Json.arr ((actionList md s).map actionWire).toArray)]


def tagName : OutcomeTag → String
  | .noExternal => "no_external"
  | .rejected => "rejected"
  | .warmSuccess => "warm_success"
  | .coldSuccess => "cold_success"
  | .fault => "fault"

def transitionReply (md : Model n m) (s : RuntimeState md) (a : Action)
    (out : Outcome md) : Except String Json := do
  match confirmExec md s a out with
  | none => throw "checked outcome does not realize selected action"
  | some t =>
      return Json.mkObj [("status",.str "lazy_staged_transition"),
        ("action",actionWire a),("outcome",.str (tagName out.tag)),
        ("before",planWire s.plan),("after",planWire t.plan),
        ("warm_artifact",match t.warmArtifact with | none => .null | some x => resultArtifactWire x),
        ("cold_artifact",match t.coldArtifact with | none => .null | some x => resultArtifactWire x)]


def parseCore (sourceJ callsJ warmQJ coldQJ : Json) :
    Except String (Sigma fun n => Sigma fun m => Model n m) := do
  let compiled ← load sourceJ
  let calls ← StagedCodec.boundedNat 1000000 callsJ
  let w ← parseQuote warmQJ
  let c ← parseQuote coldQJ
  return ⟨compiled.parsed.input,compiled.parsed.output,
    mkModel compiled.parsed.program calls w c⟩


def process (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "lazy-staged-plan-f5-v1",sourceJ,callsJ,warmQJ,coldQJ,stateJ,horizonJ] =>
      let ⟨_,_,md⟩ ← parseCore sourceJ callsJ warmQJ coldQJ
      let state ← parsePlan md stateJ
      let h ← StagedCodec.boundedNat 8 horizonJ
      return planReply md state h
  | [.str "lazy-staged-transition-f5-v1",sourceJ,callsJ,warmQJ,coldQJ,stateJ,
      actionJ,outcomeJ,currentWarmJ,currentColdJ,resultJ,generationJ] =>
      let ⟨n,m,md⟩ ← parseCore sourceJ callsJ warmQJ coldQJ
      let generation ← StagedCodec.boundedNat 100000000 generationJ
      let state ← parseRuntime md stateJ currentWarmJ currentColdJ generation
      let action ← parseAction actionJ
      let outcome ← match outcomeJ with
        | .str "local" => pure (Outcome.noExternal : Outcome md)
        | .str "rejected" => pure (Outcome.rejected : Outcome md)
        | .str "fault" => pure (Outcome.fault : Outcome md)
        | .str "success" =>
            match action with
            | .inspectWarm =>
                let r ← parseRecord n m resultJ
                match checkedWarm md r with
                | some a => pure (.warmSuccess a)
                | none => throw "warm result rejected or quote mismatch"
            | .generateCold =>
                let c ← parseCandidate n m resultJ
                match checkedCold md c generation with
                | some a => pure (.coldSuccess a)
                | none => throw "cold result rejected or quote mismatch"
            | _ => throw "success artifact only applies to setup actions"
        | _ => throw "outcome must be local, rejected, success or fault"
      transitionReply md state action outcome
  | _ => throw "unknown lazy staged request"

end Komorebi.AVOC.Affine.LazyStagedCodec
