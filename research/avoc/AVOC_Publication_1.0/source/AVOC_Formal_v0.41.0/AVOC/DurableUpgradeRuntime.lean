import AVOC.DurableUpgradeLaws
import AVOC.UpgradeRuntime

namespace Komorebi.AVOC.DurableUpgradeRuntime

open Lean UpgradeCatalogue DurableUpgrade

structure CertifiedJournal (credits : Nat) where
  journal : Journal Version
  safe : DurableUpgrade.Safe (authority credits) journal

def checkedRestore (credits : Nat) (cmds : List (Command Version))
    (actual : Journal Version) : Except String (CertifiedJournal credits) :=
  match h : restore (authority credits) .dynamic cmds actual with
  | .error msg => .error msg
  | .ok j => .ok ⟨j, restored_certificate _ _ dynamic_contract cmds actual j h⟩

def checkedApply (credits : Nat) (j : CertifiedJournal credits) (cmd : Command Version) :
    Except String (CertifiedJournal credits × Reply Version) :=
  match h : DurableUpgrade.apply (authority credits) j.journal cmd with
  | .error msg => .error msg
  | .ok r => .ok (⟨r.journal, apply_safe _ _ _ _ j.safe h⟩, r)

theorem certified_active_contract (credits : Nat) (j : CertifiedJournal credits) :
    Contract j.journal.current.active := j.safe.1.1

theorem certified_spending_bound (credits : Nat) (j : CertifiedJournal credits) :
    j.journal.current.evaluationSpent + j.journal.current.switchSpent ≤ credits :=
  j.safe.1.2.1

theorem certified_active_decision (credits : Nat) (j : CertifiedJournal credits)
    (S : Type) (m : Retry.Model S) (hm : Retry.NoRevival m) (n : Nat) (s : S) :
    (UpgradeCatalogue.execute j.journal.current.active m n s).retry = Retry.choose m n s :=
  certified_active_contract credits j S m hm n s

theorem certified_endpoint_net (credits : Nat) (j : CertifiedJournal credits) :
    (j.journal.current.guaranteedGain : Int) - (j.journal.current.evaluationSpent : Int) ≤
      Upgrade.campaignNet (authority credits) j.journal.current :=
  Upgrade.campaign_net_lower_bound _ _ j.safe.1

def stateWire (s : Upgrade.State Version) : Json := toJson
  [Json.str (UpgradeRuntime.versionName s.initial), Json.str (UpgradeRuntime.versionName s.active),
   toJson s.revision, toJson s.trials, toJson s.evaluationSpent,
   toJson s.switchSpent, toJson s.guaranteedGain]

def proposalWire (p : Upgrade.Proposal Version) : Json := toJson
  [Json.str (UpgradeRuntime.versionName p.parent), toJson p.revision,
   Json.str (UpgradeRuntime.versionName p.candidate), Json.str p.core, Json.str p.objective]

def ticketWire (t : Ticket Version) : Json :=
  toJson [Json.str t.key, stateWire t.before, proposalWire t.proposal]

def resolutionWire : Resolution → Json
  | .abandoned => toJson ["abandoned"]
  | .evaluated o => toJson ["evaluated", UpgradeRuntime.outcomeName o]

def journalWire (j : Journal Version) : Json := toJson
  [stateWire j.current, match j.pending with | none => .null | some t => ticketWire t,
    toJson (j.closed.map (fun r => toJson [ticketWire r.ticket, resolutionWire r.resolution]))]

def natField (j : Json) : Except String Nat := do
  let n ← j.getNat?
  if n > 1000000 then throw "integer limit"
  return n

def keyField (j : Json) : Except String String := do
  let k ← j.getStr?
  if k.isEmpty || k.utf8ByteSize > 128 then throw "invalid operation key"
  return k

def parseState (j : Json) : Except String (Upgrade.State Version) := do
  match (← j.getArr?).toList with
  | [v, w, n, t, e, s, g] =>
    return ⟨← UpgradeRuntime.parseVersion v, ← UpgradeRuntime.parseVersion w,
      ← natField n, ← natField t, ← natField e, ← natField s, ← natField g⟩
  | _ => throw "state requires seven fields"

def parseTicket (j : Json) : Except String (Ticket Version) := do
  match (← j.getArr?).toList with
  | [k, s, p] => return ⟨← keyField k, ← parseState s, ← UpgradeRuntime.parseProposal p⟩
  | _ => throw "ticket requires key, exact before-state and proposal"

def parseResolution (j : Json) : Except String Resolution := do
  match (← j.getArr?).toList with
  | [.str "abandoned"] => return .abandoned
  | [.str "evaluated", .str "rejected"] => return .evaluated .rejected
  | [.str "evaluated", .str "promoted"] => return .evaluated .promoted
  | [.str "evaluated", .str "unfunded"] => return .evaluated .unfunded
  | _ => throw "invalid resolution"

def parseClosed (j : Json) : Except String (Closed Version) := do
  match (← j.getArr?).toList with
  | [t, r] => return ⟨← parseTicket t, ← parseResolution r⟩
  | _ => throw "closed record requires ticket and resolution"

def parseJournal (j : Json) : Except String (Journal Version) := do
  match (← j.getArr?).toList with
  | [s, p, xs] =>
    let pending ← if p == .null then pure none else some <$> parseTicket p
    let entries ← xs.getArr?
    if entries.size > 256 then throw "history limit"
    return ⟨← parseState s, pending, ← entries.toList.mapM parseClosed⟩
  | _ => throw "journal requires state, pending and closed records"

def parseCommand (j : Json) : Except String (Command Version) := do
  match (← j.getArr?).toList with
  | [.str "begin", t] => return .begin (← parseTicket t)
  | [.str "finish", k] => return .finish (← keyField k)
  | [.str "abandon", k] => return .abandon (← keyField k)
  | _ => throw "invalid campaign command"

def render (credit : Nat) (j : CertifiedJournal credit) (changed : Bool)
    (ev sw : Nat) (invoke : Bool) : Json := Json.mkObj [
  ("status", .str "checked"), ("core", .str (authority credit).core),
  ("objective", .str (authority credit).objective), ("credits", toJson credit),
  ("changed", toJson changed), ("evaluation_debit", toJson ev), ("switch_debit", toJson sw),
  ("journal", journalWire j.journal),
  ("summary", UpgradeRuntime.stateJson credit j.journal.current),
  ("active_component_execution", if invoke then UpgradeRuntime.benchmarkJson j.journal.current.active else .null)]

/-- The physical wrapper sends the full protected event history and current
checkpoint. Successful parsing is not used as a substitute for replay checking. -/
def execute (input : Json) : Except String Json := do
  match (← input.getArr?).toList with
  | [.str "avoc-durable-upgrade-v1", credit, events, actual, command, invoke] =>
    let b ← natField credit
    if b > 10000 then throw "credit limit"
    let es ← events.getArr?
    if es.size > 512 then throw "event limit"
    let cmds ← es.toList.mapM parseCommand
    let j ← parseJournal actual
    let base ← checkedRestore b cmds j
    let invoke ← invoke.getBool?
    if command == .null then return render b base false 0 0 invoke
    let cmd ← parseCommand command
    let (out, reply) ← checkedApply b base cmd
    return render b out reply.changed reply.evaluationDebit reply.switchDebit invoke
  | _ => throw "invalid durable campaign wire"

end Komorebi.AVOC.DurableUpgradeRuntime
