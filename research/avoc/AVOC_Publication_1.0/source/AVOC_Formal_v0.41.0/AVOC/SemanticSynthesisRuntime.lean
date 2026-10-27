import AVOC.SemanticPromotion
import Lean

namespace Komorebi.AVOC.SemanticSynthesisRuntime

open Lean Synthesis SemanticSynthesis

def programWire : Program → Json
  | .literal b => toJson [Json.str "literal", toJson b]
  | .variable v => toJson [Json.str "variable", toJson (match v with | .first => 0 | .second => 1 | .third => 2 : Nat)]
  | .neg p => toJson [Json.str "not", programWire p]
  | .conjunction p q => toJson [Json.str "and", programWire p, programWire q]
  | .disjunction p q => toJson [Json.str "or", programWire p, programWire q]
  | .exclusive p q => toJson [Json.str "xor", programWire p, programWire q]

def parseProgram : Nat → Json → Except String Program
  | 0, _ => .error "program nesting limit"
  | fuel+1, j => do
    match (← j.getArr?).toList with
    | [.str "literal",b] => return .literal (← b.getBool?)
    | [.str "variable",n] =>
      match ← n.getNat? with
      | 0 => return .variable .first
      | 1 => return .variable .second
      | 2 => return .variable .third
      | _ => throw "variable must be 0,1,2"
    | [.str "not",p] => return .neg (← parseProgram fuel p)
    | [.str "and",p,q] => return .conjunction (← parseProgram fuel p) (← parseProgram fuel q)
    | [.str "or",p,q] => return .disjunction (← parseProgram fuel p) (← parseProgram fuel q)
    | [.str "xor",p,q] => return .exclusive (← parseProgram fuel p) (← parseProgram fuel q)
    | _ => throw "unsupported program"

def workWire (w : Work) : Json := Json.mkObj
  [("emitted",toJson w.emitted),("node_mass",toJson w.nodeMass),
   ("ast_visit_tariff",toJson (10*w.nodeMass)),("index_probes",toJson w.probes),
   ("probe_tariff",toJson (9*w.probes)),("charge",toJson w.charge)]

def stageWire (s : Stage) : Json := Json.mkObj
  [("depth",toJson s.depth),("retained",toJson s.kept),("work",workWire s.work)]

def entryWire (e : Entry) : Json := Json.mkObj
  [("bits",toJson e.bits),("nodes",toJson e.size),("program",programWire e.code)]

def buildWire (b : Build) : Json := Json.mkObj
  [("retained",toJson b.entries.length),("work",workWire b.work),
   ("stages",toJson (b.stages.map stageWire)),("entries",toJson (b.entries.map entryWire))]

def queriesWire (bank : List Entry) (references : List Program) : Json :=
  toJson (references.map fun r =>
    let p := select r r (codes bank)
    Json.mkObj [("reference",programWire r),("candidate",programWire p),
      ("reference_nodes",toJson (nodes r)),("candidate_nodes",toJson (nodes p)),
      ("exact_equivalence",toJson (check p r))])

def parseReferences (j : Json) : Except String (List Program) := do
  let a ← j.getArr?
  if a.size > 256 then throw "at most 256 references"
  let ps ← a.toList.mapM (parseProgram 16)
  if ps.any (fun p => nodes p > 127) then throw "reference node cap 127"
  return ps

def execute (j : Json) : Except String Json := do
  match (← j.getArr?).toList with
  | [.str "build", .str mode, d, refs] =>
    let depth ← d.getNat?
    if depth > 3 then throw "depth cap 3"
    if mode != "feedback" && mode != "frozen" then throw "unknown build mode"
    if mode == "frozen" && depth > 2 then throw "frozen depth cap 2: avoid billion-entry layer"
    let references ← parseReferences refs
    let b := if mode == "feedback" then learnedBuild depth else (frozenBuild depth).toBuild
    return Json.mkObj [("status",.str "checked"),("mode",.str mode),("depth",toJson depth),
      ("build",buildWire b),("queries",queriesWire b.entries references)]
  | [.str "budget", d, c, refs] =>
    let depth ← d.getNat?
    let credit ← c.getNat?
    if depth > 3 then throw "depth cap 3"
    if credit > 1000000000 then throw "credit cap"
    let references ← parseReferences refs
    match paidSearch depth credit with
    | none => return Json.mkObj [("status",.str "unfunded"),("credit",toJson credit),
        ("spent",toJson (0:Nat)),("searched",toJson false)]
    | some r => return Json.mkObj [("status",.str "checked"),("credit",toJson credit),
        ("depth",toJson r.depth),("requested_depth",toJson depth),
        ("spent",toJson r.work.charge),("remaining",toJson r.remaining),
        ("build",buildWire ⟨r.bank.entries,r.work,r.stages⟩),
        ("queries",queriesWire r.bank.entries references),
        ("query_cost_in_search_credit",toJson false)]
  | [.str "campaign", ref, d, c, ncalls] =>
    let reference ← parseProgram 16 ref
    if nodes reference > 127 then throw "reference node cap"
    let depth ← d.getNat?
    let credit ← c.getNat?
    let calls ← ncalls.getNat?
    if depth > 3 || credit > 1000000000 || calls > 1000000 then throw "campaign bound"
    match paidSearch depth credit with
    | none => return Json.mkObj [("status",.str "unfunded"),("spent",toJson (0:Nat)),
        ("active",programWire reference)]
    | some search =>
      let fee := queryFee reference search.bank.entries
      if fee > search.remaining then
        return Json.mkObj [("status",.str "query_unfunded"),("spent",toJson search.work.charge),
          ("active",programWire reference),("build",buildWire ⟨search.bank.entries,search.work,search.stages⟩)]
      else
        let candidate := select reference reference (codes search.bank.entries)
        let offered := submit reference calls (search.remaining-fee) candidate
        let state := offered.journal.current
        let totalSpent := search.work.charge+fee+state.evaluationSpent+state.switchSpent
        return Json.mkObj [("status",.str "checked"),("depth",toJson search.depth),
          ("credit",toJson credit),("calls",toJson calls),
          ("candidate",programWire candidate),("active",programWire state.active),
          ("promotions",toJson state.revision),("query_charge",toJson fee),
          ("promotion_evaluation_charge",toJson state.evaluationSpent),
          ("switch_charge",toJson state.switchSpent),("total_spent",toJson totalSpent),
          ("remaining",toJson (credit-totalSpent)),
          ("endpoint_net",toJson (((calls*nodes reference:Nat):Int)-((calls*nodes state.active:Nat):Int)-(totalSpent:Int))),
          ("build",buildWire ⟨search.bank.entries,search.work,search.stages⟩)]
  | [.str "check", p, q] =>
    let p ← parseProgram 16 p
    let q ← parseProgram 16 q
    if nodes p > 127 || nodes q > 127 then throw "program node cap"
    return Json.mkObj [("status",.str "checked"),("equivalent",toJson (check p q)),
      ("p_bits",toJson (signature p)),("q_bits",toJson (signature q))]
  | _ => throw "invalid semantic synthesis request"

end Komorebi.AVOC.SemanticSynthesisRuntime
