import AVOC.PaidRankProbe
import AVOC.AffineReuseCodec

namespace Komorebi.AVOC.Affine.ProbeCodec

open Lean Codec FactorCodec Factorization SearchGuard RankProbe
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

def index (bound : Nat) (j : Json) : Except String (Fin bound) := do
  let i ← j.getNat?
  if h : i < bound then return ⟨i,h⟩ else throw "minor index out of range"

def parseProbe (m n : Nat) (j : Json) : Except String (MinorTwo m n) := do
  match (← j.getArr?).toList with
  | [a,b,c,d] => return ⟨← index m a, ← index m b, ← index n c, ← index n d⟩
  | _ => throw "minor requires four row/column indices"

def probeWire {m n} (p : MinorTwo m n) : Json :=
  toJson [p.row0.val,p.row1.val,p.col0.val,p.col1.val]

def witnessWire {m n} : Option (MinorTwo m n) → Json
  | none => .null
  | some p => probeWire p

def permitted (p : DenseProgram F n m) (calls lo : Nat) : Bool :=
  worthExploring calls (executionCost (cheaper p (fuse p)))
    (menuFloor (executionCost (cheaper p (fuse p))) n m lo) (remainingMinimum p lo)

theorem executed_denial_sound (p : DenseProgram F n m) (calls probeCredit generation : Nat)
    (ps : List (MinorTwo m n)) (c : Checked (coefficients p))
    (hg : emissionCharge n m c.candidate.width ≤ generation)
    (hs : permitted p calls (scan (coefficients p).linear (widthFloor (coefficients p)) probeCredit ps).lower = false) :
    calls * executionCost (cheaper p (fuse p)) ≤
      normalizationCost p + reuseCharge n m c.candidate.width + generation +
        calls * executionCost (choose p c) :=
  paid_probe_denial_sound p _ calls generation c
    (scan_lower_preserved _ _ _ _ (widthFloor_rank (coefficients p))) hg hs

theorem funded_probe_total (p : DenseProgram F n m) (credit allowance : Nat)
    (ps : List (MinorTwo m n)) (h : ReuseCodec.preflightCharge p ≤ credit) :
    let tested := (scan (coefficients p).linear (widthFloor (coefficients p))
      (min allowance (credit-ReuseCodec.preflightCharge p)) ps).tested
    ReuseCodec.preflightCharge p + probeFee * tested ≤ credit := by
  dsimp
  have hb := scan_spent_bound (coefficients p).linear (widthFloor (coefficients p))
    (min allowance (credit-ReuseCodec.preflightCharge p)) ps
  have hm := Nat.min_le_right allowance (credit-ReuseCodec.preflightCharge p)
  omega

/-- Rank is never evaluated at runtime. The reported lower bound comes only from
zero/nonzero classification and the actual funded determinant checks. -/
def analyze (source : Json) (calls credit allowance : Nat) (planJson : Json) : Except String Json := do
  let packed ← parseProgram 24 source
  let p := packed.program
  let n := packed.input
  let m := packed.output
  if syntaxNodes p > 256 then throw "AST node cap"
  let rawPlan ← planJson.getArr?
  if rawPlan.size > 784 then throw "probe plan cap"
  let ps := (← rawPlan.mapM (parseProbe m n)).toList
  let old := executionCost p
  let preliminary := ReuseCodec.preflightCharge p
  let basic := [("original",programWire p),("per_call_original",toJson old),
    ("calls",toJson calls),("credit",toJson credit),("probe_allowance",toJson allowance)]
  if old == 0 || calls == 0 then
    return Json.mkObj (basic ++ [("status",.str "no_deployment_opportunity"),
      ("selected",programWire p),("per_call_selected",toJson old),
      ("spent",toJson (0:Nat)),("remaining",toJson credit),
      ("probe_tests",toJson (0:Nat)),("probe_spent",toJson (0:Nat)),
      ("generator_executed",toJson false)])
  if preliminary > credit then
    return Json.mkObj (basic ++ [("status",.str "unfunded_preflight"),
      ("selected",programWire p),("per_call_selected",toJson old),
      ("spent",toJson (0:Nat)),("remaining",toJson credit),
      ("probe_tests",toJson (0:Nat)),("probe_spent",toJson (0:Nat)),
      ("generator_executed",toJson false)])
  let f := coefficients p
  let base := cheaper p (fuse p)
  let baseCost := executionCost base
  let initial := widthFloor f
  let initialPermitted := permitted p calls initial
  let effective := min allowance (credit-preliminary)
  let result := if initialPermitted then scan f.linear initial effective ps
    else (⟨initial,0,effective,none⟩ : ScanResult m n)
  let spent := preliminary + probeFee * result.tested
  let finalPermitted := permitted p calls result.lower
  return Json.mkObj (basic ++ [
    ("status",.str (if !initialPermitted then "skip_initial_bound"
      else if !finalPermitted then "skip_probed_bound" else "search_may_pay")),
    ("normal",signatureWire f),("selected",programWire base),
    ("per_call_selected",toJson baseCost),("preflight_spent",toJson preliminary),
    ("initial_floor",toJson initial),("rank_lower_bound",toJson result.lower),
    ("witness",witnessWire result.witness),
    ("probe_tests",toJson result.tested),("probe_spent",toJson (probeFee*result.tested)),
    ("initial_may_pay",toJson initialPermitted),("final_may_pay",toJson finalPermitted),
    ("menu_cost_floor",toJson (menuFloor baseCost n m result.lower)),
    ("initial_remaining_minimum",toJson (remainingMinimum p initial)),
    ("remaining_minimum",toJson (remainingMinimum p result.lower)),
    ("validation_reserve",toJson (normalizationCost p + reuseCharge n m result.lower)),
    ("opportunity_ceiling",toJson (opportunity calls baseCost (menuFloor baseCost n m result.lower))),
    ("baseline_proven_two_stage_optimal",toJson (decide (factorCost n m result.lower ≥ baseCost))),
    ("spent",toJson spent),("remaining",toJson (credit-spent)),
    ("generator_executed",toJson false),
    ("rank_is_exact",toJson false)])

def process (j : Json) : Except String Json := do
  match (← j.getArr?).toList with
  | [.str "affine-rank-probe-f5-v1",source,calls,credit,allowance,plan] =>
    let c ← calls.getNat?
    let b ← credit.getNat?
    let a ← allowance.getNat?
    if c > 1000000 || b > 100000000 || a > 100000000 then throw "integer cap"
    analyze source c b a plan
  | _ => throw "unknown or malformed rank-probe request"

end Komorebi.AVOC.Affine.ProbeCodec
