import AVOC.AffineFactorChoice
import AVOC.AffineCodec
import Mathlib.Algebra.Field.ZMod

namespace Komorebi.AVOC.Affine.FactorCodec

open Lean
open Codec Factorization
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

/-- Untyped JSON shapes are checked before constructing the dimension-indexed object.
Format: [width, firstMatrix, firstOffset, secondMatrix, secondOffset, U, V]. -/
def parseCandidate (n m : Nat) (j : Json) : Except String (Candidate F n m) := do
  match (← j.getArr?).toList with
  | [kj,d,a,c,b,u,v] =>
    let k ← dimension kj
    return ⟨k, ⟨← matrix n k d, ← vector k a⟩,
      ⟨← matrix k m c, ← vector m b⟩, ← matrix m k u, ← matrix k n v⟩
  | _ => throw "malformed affine factor certificate"

/-- Serializer for the retained typed execution plan, not just its fused semantics. -/
def programWire : {n m : Nat} → DenseProgram F n m → Json
  | n,m,.atom f => toJson ([.str "map",toJson n,toJson m,
      toJson (List.ofFn (fun i => vectorWire (f.linear i))), vectorWire f.offset] : List Json)
  | n,_,.ident => toJson ([.str "id",toJson n] : List Json)
  | _,_,.seq p q => toJson ([.str "seq",programWire p,programWire q] : List Json)
  | _,_,.plus p q => toJson ([.str "sum",programWire p,programWire q] : List Json)

def boundedNat (cap : Nat) (j : Json) : Except String Nat := do
  let n ← j.getNat?
  if n > cap then throw "integer cap exceeded"
  return n

/-- The decoded proof-carrying candidate entails both exact behavior and a global
width lower bound. This theorem says nothing about untrusted generator completeness. -/
theorem decoded_certificate_sound {n m : Nat} (j : Json) (f : Signature F n m)
    (c : Candidate F n m) (_hp : parseCandidate n m j = .ok c)
    (hc : Factorization.check f c = true) :
    (∀ x, execute (plan c) x = eval f x) ∧ f.linear.rank = c.width := by
  have h := Factorization.checked_optimal hc
  exact ⟨h.1,h.2.1⟩

def process (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "affine-factor-f5-v1",source,cj,nj,gj,bj,xj] =>
      let compiled ← load source
      let p := compiled.parsed.program
      let n := compiled.parsed.input
      let m := compiled.parsed.output
      let c ← parseCandidate n m cj
      let calls ← boundedNat 1000000 nj
      let generation ← boundedNat 100000000 gj
      let budget ← boundedNat 100000000 bj
      let xs ← xj.getArr?
      if xs.size > 128 then throw "input batch cap"
      let inputs ← xs.mapM (vector n)
      let already := normalizationCost p + generation
      if already > budget then throw "declared earlier work exceeds budget"
      let required := upfront p c.width generation
      let base := [("field",.str "ZMod(5)"),("calls",toJson calls),
        ("generation_charge",toJson generation),("normalization_charge",toJson (normalizationCost p)),
        ("certificate_charge",toJson (checkingCharge n m c.width)),("credit",toJson budget)]
      if required > budget then
        return Json.mkObj (base ++ [("status",.str "unfunded_certificate"),
          ("spent",toJson already),("remaining",toJson (budget-already)),
          ("certificate_executed",toJson false),("selected",programWire p)])
      if hc : Factorization.check (coefficients p) c = true then
        let checked : Checked (coefficients p) := ⟨c,(Factorization.check_iff _ _).1 hc⟩
        let chosen := choose p checked
        let selectedCost := executionCost chosen
        let originalCost := executionCost p
        let dense := denseCost n m
        let factored := factorCost n m c.width
        let kind := if factored < min originalCost dense then "minimum_width_factorization"
          else if dense < originalCost then "dense_normal_form" else "original"
        let baseline := calls * originalCost
        let total := required + calls * selectedCost
        return Json.mkObj (base ++ [("status",.str "certified_minimum_width"),
          ("rank",toJson c.width),("minimum_two_stage_width",toJson c.width),
          ("normal",signatureWire (coefficients p)),("selected",programWire chosen),
          ("choice",.str kind),("per_call_original",toJson originalCost),
          ("per_call_dense",toJson dense),("per_call_factor",toJson factored),
          ("per_call_selected",toJson selectedCost),("spent",toJson required),
          ("remaining",toJson (budget-required)),("certificate_executed",toJson true),
          ("baseline_deployment",toJson baseline),("campaign_total",toJson total),
          ("net_gain",toJson ((baseline : Int)-(total : Int))),
          ("breaks_even",toJson (decide (total ≤ baseline))),
          ("strict_gain",toJson (decide (total < baseline))),
          ("outputs",toJson (inputs.toList.map (fun x => vectorWire (execute chosen x)))),
          ("cost_boundary",.str "declared ring-operation/check tariffs; generator count supplied; excludes IO, parsing, allocation, bit complexity")])
      else
        return Json.mkObj (base ++ [("status",.str "rejected_certificate"),
          ("spent",toJson required),("remaining",toJson (budget-required)),
          ("certificate_executed",toJson true),("selected",programWire p)])
  | _ => throw "unknown affine factor request"

end Komorebi.AVOC.Affine.FactorCodec
