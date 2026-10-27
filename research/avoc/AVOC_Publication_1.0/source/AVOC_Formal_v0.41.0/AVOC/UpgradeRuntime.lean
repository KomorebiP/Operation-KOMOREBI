import AVOC.UpgradeSpecialization
import Lean

namespace Komorebi.AVOC.UpgradeRuntime

open Lean UpgradeCatalogue

structure Request where
  credits : Nat
  proposals : List (Upgrade.Proposal Version)

structure CertifiedResult (credits : Nat) where
  state : Upgrade.State Version
  safe : Upgrade.Safe (authority credits) state

def evaluate (r : Request) : CertifiedResult r.credits :=
  ⟨Upgrade.run (authority r.credits) initial r.proposals,
    Upgrade.run_safe _ _ _ (UpgradeCatalogue.initial_safe r.credits)⟩

theorem executed_campaign_preserves_contract (r : Request) :
    Contract (evaluate r).state.active := (evaluate r).safe.1

theorem executed_campaign_credit_bound (r : Request) :
    (evaluate r).state.evaluationSpent + (evaluate r).state.switchSpent ≤ r.credits :=
  (evaluate r).safe.2.1

theorem executed_campaign_net_bound (r : Request) :
    ((evaluate r).state.guaranteedGain : Int) - ((evaluate r).state.evaluationSpent : Int) ≤
      Upgrade.campaignNet (authority r.credits) (evaluate r).state :=
  Upgrade.campaign_net_lower_bound _ _ (evaluate r).safe

/-- After selection, invoke the active component. Its decision matches the
reference for ALL inputs satisfying NoRevival, not just the score workload. -/
theorem active_component_correct (r : Request) (S : Type) (m : Retry.Model S)
    (hm : Retry.NoRevival m) (n : Nat) (s : S) :
    (UpgradeCatalogue.execute (evaluate r).state.active m n s).retry = Retry.choose m n s :=
  executed_campaign_preserves_contract r S m hm n s

def versionName : Version → String
  | .dynamic => "dynamic"
  | .threshold => "threshold"
  | .alwaysRetry => "always_retry"

def parseVersion (j : Json) : Except String Version := do
  match ← j.getStr? with
  | "dynamic" => return .dynamic
  | "threshold" => return .threshold
  | "always_retry" => return .alwaysRetry
  | _ => throw "unknown immutable candidate"

def parseProposal (j : Json) : Except String (Upgrade.Proposal Version) := do
  match (← j.getArr?).toList with
  | [parent, revision, candidate, core, objective] =>
    let p ← parseVersion parent
    let n ← revision.getNat?
    let c ← parseVersion candidate
    let k ← core.getStr?
    let o ← objective.getStr?
    if n > 1000 || k.utf8ByteSize > 256 || o.utf8ByteSize > 256 then
      throw "proposal size limit"
    return ⟨p, n, c, k, o⟩
  | _ => throw "proposal must have five exact fields"

def parse (j : Json) : Except String Request := do
  match (← j.getArr?).toList with
  | [.str "avoc-upgrade-campaign-v1", credit, proposals] =>
    let b ← credit.getNat?
    let ps ← proposals.getArr?
    if b > 10000 || ps.size > 128 then throw "campaign limit"
    return ⟨b, ← ps.toList.mapM parseProposal⟩
  | _ => throw "invalid upgrade campaign wire"

def stateJson (credits : Nat) (s : Upgrade.State Version) : Json := Json.mkObj [
  ("initial", .str (versionName s.initial)),
  ("active", .str (versionName s.active)),
  ("revision", toJson s.revision), ("funded_trials", toJson s.trials),
  ("evaluation_spent", toJson s.evaluationSpent), ("switch_spent", toJson s.switchSpent),
  ("guaranteed_gain", toJson s.guaranteedGain),
  ("initial_utility", toJson (utility s.initial)), ("active_utility", toJson (utility s.active)),
  ("net_endpoint_gain", toJson (Upgrade.campaignNet (authority credits) s)),
  ("certified_net_lower_bound", toJson ((s.guaranteedGain : Int) - (s.evaluationSpent : Int)))]

def outcomeName : Upgrade.Outcome → String
  | .unfunded => "unfunded"
  | .rejected => "rejected"
  | .promoted => "promoted"

def events (credits : Nat) : Upgrade.State Version → List (Upgrade.Proposal Version) → List Json
  | _, [] => []
  | s, p :: ps =>
    let r := Upgrade.step (authority credits) s p
    Json.mkObj [("outcome", .str (outcomeName r.outcome)),
      ("candidate", .str (versionName p.candidate)),
      ("evaluation_debit", toJson r.evaluationDebit), ("switch_debit", toJson r.switchDebit),
      ("state", stateJson credits r.next)] :: events credits r.next ps

def benchmarkJson (v : Version) : Json := toJson (horizons.map fun n =>
  let old := UpgradeCatalogue.execute .dynamic exampleModel n ()
  let new := UpgradeCatalogue.execute v exampleModel n ()
  Json.mkObj [("horizon", toJson n), ("reference_retry", toJson old.retry),
    ("active_retry", toJson new.retry), ("reference_visits", toJson old.visits),
    ("active_visits", toJson new.visits)])

def execute (j : Json) : Except String Json := do
  let r ← parse j
  let checked := evaluate r
  return Json.mkObj [("status", .str "checked"),
    ("core", .str (authority r.credits).core), ("objective", .str (authority r.credits).objective),
    ("credits", toJson r.credits), ("final", stateJson r.credits checked.state),
    ("events", toJson (events r.credits initial r.proposals)),
    ("active_component_execution", benchmarkJson checked.state.active),
    ("scope", .str "immutable compiled catalogue; action-only retry contract under NoRevival; nominal state-visit objective; no arbitrary code deployment or empirical speed claim")]

end Komorebi.AVOC.UpgradeRuntime
