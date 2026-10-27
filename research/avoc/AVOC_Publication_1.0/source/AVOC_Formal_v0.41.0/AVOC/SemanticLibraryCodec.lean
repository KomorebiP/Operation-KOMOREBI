import AVOC.SemanticLibrary
import Lean

namespace Komorebi.AVOC.LibraryCodec

open Lean Synthesis BoolClosure SemanticLibrary

/-- The only accepted semantics, bit order and cost identity. There is no trusted depth label. -/
def grammarID : String := "bool3-not-and-or-xor-v1"
def orderID : String := "lexicographic-false-first-bit0"
def costID : String := "eager-tree-nodes-v1"
def schemaID : String := "avoc-global-cost-library-v1"

def programWire : Program → Json
  | .literal b => toJson [Json.str "literal", toJson b]
  | .variable v => toJson [Json.str "variable",toJson (match v with
      | .first => 0 | .second => 1 | .third => 2 : Nat)]
  | .neg p => toJson [Json.str "not",programWire p]
  | .conjunction p q => toJson [Json.str "and",programWire p,programWire q]
  | .disjunction p q => toJson [Json.str "or",programWire p,programWire q]
  | .exclusive p q => toJson [Json.str "xor",programWire p,programWire q]

def parseProgram : Nat → Json → Except String Program
  | 0, _ => .error "program nesting limit"
  | fuel + 1, j => do
    match (← j.getArr?).toList with
    | [.str "literal",b] => return .literal (← b.getBool?)
    | [.str "variable",n] =>
      match ← n.getNat? with
      | 0 => return .variable .first
      | 1 => return .variable .second
      | 2 => return .variable .third
      | _ => throw "variable index outside [0,2]"
    | [.str "not",p] => return .neg (← parseProgram fuel p)
    | [.str "and",p,q] => return .conjunction (← parseProgram fuel p) (← parseProgram fuel q)
    | [.str "or",p,q] => return .disjunction (← parseProgram fuel p) (← parseProgram fuel q)
    | [.str "xor",p,q] => return .exclusive (← parseProgram fuel p) (← parseProgram fuel q)
    | _ => throw "unsupported expression constructor"

def parseSig (j : Json) : Except String Sig := do
  match (← j.getArr?).toList with
  | [a,b,c,d,e,f,g,h] => return ⟨← a.getBool?,← b.getBool?,← c.getBool?,← d.getBool?,
      ← e.getBool?,← f.getBool?,← g.getBool?,← h.getBool?⟩
  | _ => throw "signature must contain eight Boolean entries"

def sigWire (s : Sig) : Json := toJson [s.a,s.b,s.c,s.d,s.e,s.f,s.g,s.h]

def parseRow (j : Json) : Except String Row := do
  match (← j.getArr?).toList with
  | [sig,n,p] =>
    let size ← n.getNat?
    if size > 4096 then throw "declared node cost limit"
    let code ← parseProgram 64 p
    if nodes code > 4096 then throw "witness node limit"
    return ⟨← parseSig sig,size,code⟩
  | _ => throw "row requires signature, node cost and expression"

def parseCertificate (j : Json) : Except String (Array Row) := do
  match (← j.getArr?).toList with
  | [.str schema,.str grammar,.str order,.str metric,rs] =>
    if schema != schemaID || grammar != grammarID || order != orderID || metric != costID then
      throw "incompatible certificate schema, grammar, input order or metric"
    let rows ← rs.getArr?
    if rows.size != 256 then throw "exactly 256 indexed rows required"
    rows.mapM parseRow
  | _ => throw "invalid certificate envelope"

/-- Successful loading only returns banks constructed by the paid executable verifier. -/
def load (j : Json) (credit : Nat) : Except String ImportResult :=
  match parseCertificate j with
  | .error e => .error e
  | .ok rows => .ok (paidImport rows credit)

theorem load_accepted_source (j : Json) (credit : Nat) (r : ImportResult)
    (b : CheckedBank) (hl : load j credit = .ok r) (hb : r.checked = some b) :
    ∃ rows, parseCertificate j = .ok rows ∧ b.rows = rows ∧ checkBank rows = true := by
  unfold load at hl
  cases hp : parseCertificate j with
  | error e => simp only [hp] at hl; cases hl
  | ok rows =>
    simp only [hp] at hl
    have hr : paidImport rows credit = r := Except.ok.inj hl
    subst r
    exact ⟨rows,rfl,accepted_rows_exact rows credit b hb,(accepted_import_valid rows credit b hb).1⟩

theorem loaded_query_global (j : Json) (credit : Nat) (r : ImportResult)
    (b : CheckedBank) (_hl : load j credit = .ok r) (_hb : r.checked = some b)
    (p : Program) : Equivalent (query b p) p ∧
      ∀ q, Equivalent q p → nodes (query b p) ≤ nodes q :=
  ⟨query_equivalent b p,query_globally_minimum b p⟩

def renderQuery (q : QueryResult) : Json := Json.mkObj
  [("status",.str (if q.result.isSome then "globally_optimal" else "query_unfunded")),
   ("program",match q.result with | none => .null | some p => programWire p),
   ("nodes",match q.result with | none => .null | some p => toJson (nodes p)),
   ("charged",toJson q.charged),("remaining",toJson q.remaining)]

def parseQueries (j : Json) : Except String (List Program) := do
  let qs ← j.getArr?
  if qs.size > 512 then throw "query batch limit"
  let ps ← qs.toList.mapM (parseProgram 64)
  if ps.any (fun p => nodes p > 4096) then throw "query node limit"
  return ps

/-- Parsing/preflight costs are outside the declared checking and query tariffs. -/
def execute (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "avoc-library-load-v1",cert,amount,qs] =>
    let credit ← amount.getNat?
    if credit > 1000000000 then throw "credit limit"
    let queries ← parseQueries qs
    let rows ← parseCertificate cert
    let imported := paidImport rows credit
    match imported.checked with
    | none =>
      return Json.mkObj [("status",.str (if imported.attempted then "invalid_certificate" else "unfunded")),
       ("validation_charged",toJson imported.charged),("query_charged",toJson (0 : Nat)),
       ("remaining",toJson imported.remaining),("required_validation",toJson (validationCharge rows)),
       ("queries",toJson ([] : List Json))]
    | some bank =>
      let answer := queryMany bank queries imported.remaining
      return Json.mkObj [("status",.str "globally_certified"),
        ("grammar",.str grammarID),("cost_model",.str costID),
        ("validation_charged",toJson imported.charged),
        ("query_charged",toJson answer.charged),("remaining",toJson answer.remaining),
        ("entries",toJson bank.rows.size),
        ("inequality_obligations",toJson closureObligations),
        ("node_sum",toJson ((rows.toList.map Row.size).sum)),
        ("queries",toJson (answer.queries.map renderQuery))]
  | _ => throw "unknown library request"

end Komorebi.AVOC.LibraryCodec
