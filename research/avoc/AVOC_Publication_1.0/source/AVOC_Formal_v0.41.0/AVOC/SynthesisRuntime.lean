import AVOC.SynthesisPromotion
import Lean

namespace Komorebi.AVOC.SynthesisRuntime

open Lean Synthesis

def programWire : Program → Json
  | .literal b => toJson [Json.str "literal", toJson b]
  | .variable v => toJson [Json.str "variable", toJson (match v with | .first => 0 | .second => 1 | .third => 2 : Nat)]
  | .neg p => toJson [Json.str "not", programWire p]
  | .conjunction p q => toJson [Json.str "and", programWire p, programWire q]
  | .disjunction p q => toJson [Json.str "or", programWire p, programWire q]
  | .exclusive p q => toJson [Json.str "xor", programWire p, programWire q]

def parseProgram : Nat → Json → Except String Program
  | 0, _ => .error "program nesting limit"
  | fuel + 1, j => do
    match (← j.getArr?).toList with
    | [.str "literal", b] => return .literal (← b.getBool?)
    | [.str "variable", n] =>
      match ← n.getNat? with
      | 0 => return .variable .first
      | 1 => return .variable .second
      | 2 => return .variable .third
      | _ => throw "variable must be 0, 1, or 2"
    | [.str "not", p] => return .neg (← parseProgram fuel p)
    | [.str "and", p, q] => return .conjunction (← parseProgram fuel p) (← parseProgram fuel q)
    | [.str "or", p, q] => return .disjunction (← parseProgram fuel p) (← parseProgram fuel q)
    | [.str "xor", p, q] => return .exclusive (← parseProgram fuel p) (← parseProgram fuel q)
    | _ => throw "unsupported pure program constructor"

def natural (j : Json) : Except String Nat := do
  let n ← j.getNat?
  if n > 100000000 then throw "integer limit"
  return n

structure Job where
  reference : Program
  calls : Nat
  credits : Nat
  depth : Nat
  trialLimit : Nat
  searchCredit : Nat
  deriving Repr, DecidableEq

def jobWire (j : Job) : Json := toJson [programWire j.reference, toJson j.calls,
  toJson j.credits, toJson j.depth, toJson j.trialLimit, toJson j.searchCredit]

def parseJob (wire : Json) : Except String Job := do
  match (← wire.getArr?).toList with
  | [r,c,b,d,l,s] =>
    let reference ← parseProgram 32 r
    if nodes reference > 127 then throw "reference size limit"
    let calls ← natural c
    let credits ← natural b
    let depth ← natural d
    let limit ← natural l
    let searchCredit ← natural s
    if depth > 2 then throw "grammar depth cap is 2"
    if limit > 21845 then throw "trial cap is 21845"
    if searchCredit > credits then throw "search credit exceeds total credit"
    return ⟨reference,calls,credits,depth,limit,searchCredit⟩
  | _ => throw "job requires reference/calls/credit/depth/trial-limit/search-credit"

def stateWire (s : Upgrade.State Program) : Json := toJson [programWire s.initial,
  programWire s.active, toJson s.revision, toJson s.trials, toJson s.evaluationSpent,
  toJson s.switchSpent, toJson s.guaranteedGain]

def parseState (j : Json) : Except String (Upgrade.State Program) := do
  match (← j.getArr?).toList with
  | [a,b,c,d,e,f,g] => return ⟨← parseProgram 32 a, ← parseProgram 32 b,
      ← natural c, ← natural d, ← natural e, ← natural f, ← natural g⟩
  | _ => throw "invalid upgrade state"

def proposalWire (p : Upgrade.Proposal Program) : Json := toJson [programWire p.parent,
  toJson p.revision, programWire p.candidate, .str p.core, .str p.objective]

def parseProposal (j : Json) : Except String (Upgrade.Proposal Program) := do
  match (← j.getArr?).toList with
  | [a,b,c,d,e] => return ⟨← parseProgram 32 a, ← natural b, ← parseProgram 32 c,
      ← d.getStr?, ← e.getStr?⟩
  | _ => throw "invalid proposal"

def ticketWire (t : DurableUpgrade.Ticket Program) : Json :=
  toJson [Json.str t.key, stateWire t.before, proposalWire t.proposal]

def parseTicket (j : Json) : Except String (DurableUpgrade.Ticket Program) := do
  match (← j.getArr?).toList with
  | [k,s,p] => return ⟨← k.getStr?, ← parseState s, ← parseProposal p⟩
  | _ => throw "invalid ticket"

def outcomeName : Upgrade.Outcome → String
  | .unfunded => "unfunded"
  | .rejected => "rejected"
  | .promoted => "promoted"

def resolutionWire : DurableUpgrade.Resolution → Json
  | .abandoned => toJson [Json.str "abandoned"]
  | .evaluated o => toJson [Json.str "evaluated", .str (outcomeName o)]

def parseResolution (j : Json) : Except String DurableUpgrade.Resolution := do
  match (← j.getArr?).toList with
  | [.str "abandoned"] => return .abandoned
  | [.str "evaluated", .str "unfunded"] => return .evaluated .unfunded
  | [.str "evaluated", .str "rejected"] => return .evaluated .rejected
  | [.str "evaluated", .str "promoted"] => return .evaluated .promoted
  | _ => throw "invalid resolution"

def journalWire (j : DurableUpgrade.Journal Program) : Json := toJson [stateWire j.current,
  match j.pending with | none => Json.null | some t => ticketWire t,
  toJson (j.closed.map (fun c => toJson [ticketWire c.ticket, resolutionWire c.resolution]))]

def parseJournal (j : Json) : Except String (DurableUpgrade.Journal Program) := do
  match (← j.getArr?).toList with
  | [s,p,cs] =>
    let pending ← if p == .null then pure none else some <$> parseTicket p
    let cs ← cs.getArr?
    if cs.size > 1 then throw "single generated submission only"
    let closed ← cs.toList.mapM (fun c => do
      match (← c.getArr?).toList with
      | [t,r] => return (⟨← parseTicket t, ← parseResolution r⟩ : DurableUpgrade.Closed Program)
      | _ => throw "invalid closed record")
    return ⟨← parseState s,pending,closed⟩
  | _ => throw "invalid journal"

def commandWire : DurableUpgrade.Command Program → Json
  | .begin t => toJson [Json.str "begin", ticketWire t]
  | .finish k => toJson [Json.str "finish", .str k]
  | .abandon k => toJson [Json.str "abandon", .str k]

def parseCommand (j : Json) : Except String (DurableUpgrade.Command Program) := do
  match (← j.getArr?).toList with
  | [.str "begin", t] => return .begin (← parseTicket t)
  | [.str "finish", .str k] => return .finish k
  | [.str "abandon", .str k] => return .abandon k
  | _ => throw "invalid command"

def invocation (p : Program) : Json :=
  toJson (inputs.map (fun s =>
    let out := runCount p s
    Json.mkObj [("input", toJson [s.first,s.second,s.third]),
      ("value",toJson out.1),("visits",toJson out.2)]))

def renderCampaign (j : Job) : Json :=
  let c := campaign j.reference j.calls j.credits j.depth j.trialLimit j.searchCredit
  let s := c.accepted.journal.current
  Json.mkObj [("status",.str "checked"),("job",jobWire j),
    ("candidate",programWire c.proposal.candidate),("active",programWire s.active),
    ("reference_nodes",toJson (nodes j.reference)),("candidate_nodes",toJson (nodes c.proposal.candidate)),
    ("active_nodes",toJson (nodes s.active)),("requested_pool_size",toJson (poolSize j.depth)),
    ("generated_pool_size",toJson (if generationCharge j.depth ≤ j.searchCredit then poolSize j.depth else 0)),
    ("tested",toJson c.proposal.tested),("generation_charge",toJson c.proposal.generation),
    ("candidate_evaluation_charge",toJson c.proposal.evaluation),
    ("promotion_evaluation_charge",toJson s.evaluationSpent),
    ("switch_charge",toJson s.switchSpent),("total_charge",toJson c.totalCharge),
    ("credits_remaining",toJson (j.credits-c.totalCharge)),("net",toJson c.net),
    ("promotions",toJson s.revision),
    ("commands",toJson (c.accepted.commands.map commandWire)),
    ("journal",journalWire c.accepted.journal),("executions",invocation s.active)]

/-- The restored interpreter reads a generated AST, never installs arbitrary code.
Its contract follows from restoreGenerated's dependent proof field. -/
def inspect (j : Job) (searchCharge : Nat) (events snapshot : Json) : Except String Json := do
  if searchCharge > j.searchCredit || searchCharge > j.credits then throw "invalid search accounting"
  let es ← events.getArr?
  if es.size > 2 then throw "single generated submission only"
  let cmds ← es.toList.mapM parseCommand
  let actual ← parseJournal snapshot
  let restored ← restoreGenerated j.reference j.calls (j.credits-searchCharge) cmds actual
  return Json.mkObj [("status",.str "checked"),("active",programWire restored.journal.current.active),
    ("journal",journalWire restored.journal),("executions",invocation restored.journal.current.active)]

/-- Wire parsing is a trusted input boundary with explicit small bounds. -/
def execute (wire : Json) : Except String Json := do
  match (← wire.getArr?).toList with
  | [.str "avoc-synthesis-v1", jw] => return renderCampaign (← parseJob jw)
  | [.str "avoc-synthesis-inspect-v1", jw, spent, events, actual] =>
    inspect (← parseJob jw) (← natural spent) events actual
  | [.str "avoc-bool-check-v1", p, q] =>
    let p ← parseProgram 32 p; let q ← parseProgram 32 q
    if nodes p > 127 || nodes q > 127 then throw "program size limit"
    return Json.mkObj [("status",.str "checked"),("equivalent",toJson (check p q)),
      ("left",invocation p),("right",invocation q)]
  | _ => throw "unknown synthesis request"

theorem rendered_campaign_sound (j : Job) (s : Input) :
    run (campaign j.reference j.calls j.credits j.depth j.trialLimit j.searchCredit).accepted.journal.current.active s =
      run j.reference s := campaign_active_sound _ s

theorem rendered_campaign_budget (j : Job) :
    (campaign j.reference j.calls j.credits j.depth j.trialLimit j.searchCredit).totalCharge ≤ j.credits :=
  campaign_total_budget _

end Komorebi.AVOC.SynthesisRuntime
