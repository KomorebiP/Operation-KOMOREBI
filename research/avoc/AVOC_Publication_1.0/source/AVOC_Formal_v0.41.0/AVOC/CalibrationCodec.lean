import AVOC.FiniteCalibration
import AVOC.CalibrationBridge
import Lean

namespace Komorebi.AVOC.CalibrationCodec
open Lean FiniteCalibration

/-- Reject fractional or exponent notation in numeric tokens before Json.parse
normalizes them. String contents (including quote identity fields) are skipped. -/
def hasNonIntegerNumberToken (text : String) : Bool := Id.run do
  let mut quoted := false
  let mut escaped := false
  let mut number := false
  for ch in text.toList do
    if quoted then
      if escaped then escaped := false
      else if ch == '\\' then escaped := true
      else if ch == '"' then quoted := false
    else if ch == '"' then
      quoted := true
      number := false
    else if number then
      if ch == '.' || ch == 'e' || ch == 'E' then return true
      if !ch.isDigit then number := false
    else if ch.isDigit || ch == '-' then
      number := true
  return false

/-- The executable surface accepts exact integer tokens and rational strings. -/
def exactInt (j : Json) : Except String Int := do
  match j with
  | .num q =>
      if q.exponent = 0 then return q.mantissa
      else throw "decimal numeric token rejected"
  | _ => throw "integer token required"

def exactNat (cap : Nat) (j : Json) : Except String Nat := do
  let z ← exactInt j
  if z < 0 then throw "negative natural"
  let n := z.toNat
  if n > cap then throw "natural exceeds execution cap"
  return n

def parseRat (j : Json) : Except String ℚ := do
  match j with
  | .num _ => return (← exactInt j : Int)
  | .str s =>
      if s.length > 120 then throw "rational token too long"
      match s.splitOn "/" with
      | [a,b] =>
          let z ← match a.toInt? with
            | some z => pure z
            | none => throw "invalid rational numerator"
          let d ← match b.toNat? with
            | some d => pure d
            | none => throw "invalid rational denominator"
          if a != toString z || b != toString d || d = 0 then
            throw "rational must use exact normalized integer tokens and positive denominator"
          let q : ℚ := (z : ℚ) / d
          if q.num != z || q.den != d || d = 1 then
            throw "fraction must be reduced and nonintegral"
          return q
      | _ => throw "rational must be integer or numerator/denominator"
  | _ => throw "exact rational required"

def ratWire (q : ℚ) : Json := .str (toString q)

def processOne (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "calibration-binomial-v1", nj, kj, mj, aj] =>
      let n ← exactNat 10000 nj
      let k ← exactNat 10000 kj
      let m ← exactNat 1000 mj
      let alpha ← parseRat aj
      if k > n then throw "success count exceeds trial count"
      if m = 0 then throw "grid must contain at least one cell"
      if n * m > 500000 then throw "calibration execution cap"
      if alpha ≤ 0 || 1 ≤ alpha then throw "alpha must lie in (0,1)"
      return Json.mkObj [
        ("status", .str "calibrated"), ("n",toJson n), ("k",toJson k),
        ("grid_cells",toJson m), ("alpha",ratWire alpha),
        ("lower",ratWire (lower n k m alpha)),
        ("upper",ratWire (upper n k m alpha)),
        ("threshold",ratWire (threshold n alpha))]
  | [.str "calibrated-quote-plan-f5-v1",sourceJ,callsJ,warmJ,coldJ,stateJ,horizonJ] =>
      let ⟨_,_,md⟩ ← Affine.RobustQuoteCodec.parseCore sourceJ callsJ warmJ coldJ
      let s ← Affine.LazyStagedCodec.parsePlan (Affine.QuoteAuthority.nominal md) stateJ
      let h ← exactNat 8 horizonJ
      let rows := (Affine.LazyStaged.actionList (Affine.QuoteAuthority.nominal md) s).map
        fun a => Json.mkObj [("action",Affine.LazyStagedCodec.actionWire a),
          ("certified_dominance",toJson (Affine.CalibrationBridge.competitorDominanceCheck md h s a))]
      return Json.mkObj [("status",.str "calibrated_quote_plan"),
        ("plan",Affine.RobustQuoteCodec.planReply md s h),
        ("competitor_dominance",.arr rows.toArray)]
  | _ => throw "unknown calibration request"

def process (request : Json) : Except String Json := do
  let items ← request.getArr?
  if items.size == 2 && items[0]? == some (.str "calibration-batch-v1") then
    let batch ← items[1]!.getArr?
    if batch.size > 256 then throw "batch cap"
    let values := batch.map fun req => match processOne req with
      | .ok j => Json.mkObj [("ok",.bool true),("value",j)]
      | .error e => Json.mkObj [("ok",.bool false),("error",.str e)]
    return Json.mkObj [("status",.str "calibration_batch"),("results",.arr values)]
  else processOne request

end Komorebi.AVOC.CalibrationCodec
