import AVOC.AffineFusion
import Mathlib.Data.ZMod.Basic
import Lean

namespace Komorebi.AVOC.Affine.Codec

open Lean
abbrev F := ZMod 5

structure Packed where
  input : Nat
  output : Nat
  program : DenseProgram F input output

def dimension (j : Json) : Except String Nat := do
  let n ← j.getNat?
  if n > 8 then throw "dimension cap is eight"
  return n

def residue (j : Json) : Except String F := do
  let n ← j.getNat?
  if n ≥ 5 then throw "coefficients must be canonical integers 0..4"
  return (n : F)

def vector (n : Nat) (j : Json) : Except String (Fin n → F) := do
  let xs ← j.getArr?
  if xs.size != n then throw "vector dimension mismatch"
  let vs ← xs.mapM residue
  return fun i => vs[i.val]!

def matrix (n m : Nat) (j : Json) : Except String (Matrix (Fin m) (Fin n) F) := do
  let rs ← j.getArr?
  if rs.size != m then throw "matrix row count mismatch"
  let rows ← rs.mapM (vector n)
  return fun i => rows[i.val]!

def sequence (p q : Packed) : Except String Packed :=
  match p, q with
  | ⟨n,m,p⟩, ⟨l,k,q⟩ =>
    if h : m = l then by
      subst l
      exact .ok ⟨n,k,.seq p q⟩
    else .error "composition dimension mismatch"

def summation (p q : Packed) : Except String Packed :=
  match p, q with
  | ⟨n,m,p⟩, ⟨k,l,q⟩ =>
    if h : n = k then by
      subst k
      exact if h' : m = l then by
        subst l
        exact .ok ⟨n,m,.plus p q⟩
      else .error "sum output dimension mismatch"
    else .error "sum input dimension mismatch"

def parseProgram : Nat → Json → Except String Packed
  | 0, _ => .error "program depth cap"
  | fuel+1, j => do
      match (← j.getArr?).toList with
      | [.str "map",nj,mj,a,b] =>
        let n ← dimension nj
        let m ← dimension mj
        return ⟨n,m,.atom ⟨← matrix n m a, ← vector m b⟩⟩
      | [.str "id",nj] =>
        let n ← dimension nj
        return ⟨n,n,.ident⟩
      | [.str "seq",p,q] => sequence (← parseProgram fuel p) (← parseProgram fuel q)
      | [.str "sum",p,q] => summation (← parseProgram fuel p) (← parseProgram fuel q)
      | _ => throw "unknown or malformed affine constructor"

def syntaxNodes : {n m : Nat} → DenseProgram F n m → Nat
  | _, _, .atom _ => 1
  | _, _, .ident => 1
  | _, _, .seq f g => syntaxNodes f + syntaxNodes g + 1
  | _, _, .plus f g => syntaxNodes f + syntaxNodes g + 1

/-- Loaded normal forms retain a proof connecting the decoded source and its semantics. -/
structure Compiled (source : Json) where
  parsed : Packed
  parses : parseProgram 24 source = .ok parsed
  normal : Signature F parsed.input parsed.output
  correct : ∀ x, eval normal x = execute parsed.program x

def load (source : Json) : Except String (Compiled source) :=
  match hp : parseProgram 24 source with
  | .error e => .error e
  | .ok p => if syntaxNodes p.program > 256 then .error "AST node cap"
    else .ok ⟨p,hp,coefficients p.program,coefficients_correct p.program⟩

theorem load_source {j : Json} {v : Compiled j} (_h : load j = .ok v) :
    parseProgram 24 j = .ok v.parsed := v.parses

theorem load_semantics {j : Json} {v : Compiled j} (_h : load j = .ok v) :
    ∀ x, eval v.normal x = execute v.parsed.program x := v.correct

def vectorWire {n} (x : Fin n → F) : Json :=
  toJson (List.ofFn (fun i => (x i).val))

def signatureWire {n m} (s : Signature F n m) : Json :=
  Json.mkObj [("input_dim",toJson n),("output_dim",toJson m),
    ("matrix",toJson (List.ofFn (fun i => vectorWire (s.linear i)))),
    ("offset",vectorWire s.offset)]

def compare (p q : Packed) : Except String Bool :=
  match p, q with
  | ⟨n,m,p⟩, ⟨k,l,q⟩ =>
    if h : n = k then by
      subst k
      exact if h' : m = l then by
        subst l
        exact .ok (checkProgram (fun f => f) p q)
      else .error "comparison output dimension mismatch"
    else .error "comparison input dimension mismatch"

/-- Read-only analysis. Rejected fusion does not erase the incurred normalization cost. -/
def process (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "affine-normalize-f5-v1",pj,nj,xs] =>
      let compiled ← load pj
      let p := compiled.parsed
      let calls ← nj.getNat?
      if calls > 1000000 then throw "deployment count cap"
      let inputs ← xs.getArr?
      if inputs.size > 128 then throw "input batch cap"
      let values ← inputs.mapM (vector p.input)
      let out := values.map (execute p.program)
      let normalizedOut := values.map (eval compiled.normal)
      let directCost := executionCost p.program
      let fuseCost := denseCost p.input p.output
      let compileCost := normalizationCost p.program
      let fusedTotal := compileCost + calls * fuseCost
      let directTotal := calls * directCost
      return Json.mkObj [
        ("status",.str "exact_affine_normal_form"),("field",.str "ZMod(5)"),
        ("normal",signatureWire compiled.normal),
        ("outputs",toJson (out.toList.map vectorWire)),
        ("normal_outputs",toJson (normalizedOut.toList.map vectorWire)),
        ("basis_probe_count",toJson (p.input+1)),
        ("coefficient_count",toJson (p.output*(p.input+1))),
        ("per_call_original",toJson directCost),("per_call_fused",toJson fuseCost),
        ("normalization_charge",toJson compileCost),("calls",toJson calls),
        ("baseline_deployment_charge",toJson directTotal),
        ("fused_lifecycle_charge",toJson fusedTotal),
        ("use_fused_on_per_call_tariff",toJson (decide (fuseCost ≤ directCost))),
        ("fuse_breaks_even_including_normalization",toJson (decide (fusedTotal ≤ directTotal))),
        ("strict_lifecycle_gain",toJson (decide (fusedTotal < directTotal))),
        ("cost_model",.str "dense-ring-arithmetic-tariff-v1; excludes parsing/allocation/IO/validation")]
  | [.str "affine-compare-f5-v1",pj,qj] =>
      let p ← load pj
      let q ← load qj
      return Json.mkObj [("status",.str "exact_affine_comparison"),
        ("equivalent",toJson (← compare p.parsed q.parsed))]
  | _ => throw "unknown affine request"

end Komorebi.AVOC.Affine.Codec
