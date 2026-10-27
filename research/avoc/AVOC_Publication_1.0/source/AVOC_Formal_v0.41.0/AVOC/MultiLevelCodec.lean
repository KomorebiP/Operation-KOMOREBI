import AVOC.MultiLevelRank
import AVOC.AffineCodec
import AVOC.PlannerRuntime
import Lean
import Mathlib.Algebra.Field.ZMod

namespace Komorebi.AVOC.Affine.MultiLevelCodec

open Lean Codec MultiLevelRank
open Komorebi.AVOC.MultiLevel
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

abbrev F := ZMod 5


structure NonnegativeRat where
  value : ℚ
  nonnegative : 0 ≤ value
  deriving Repr

instance : Inhabited NonnegativeRat := ⟨⟨0,le_rfl⟩⟩

def parseNonnegativeRat (j : Json) : Except String NonnegativeRat := do
  let q ← PlannerRuntime.parseRat j
  if h : 0 ≤ q then return ⟨q,h⟩ else throw "expected nonnegative rational"


def boundedNat (cap : Nat) (j : Json) : Except String Nat := do
  let n ← j.getNat?
  if n > cap then throw "integer cap exceeded"
  return n


def finIndex (bound : Nat) (j : Json) : Except String (Fin bound) := do
  let n ← j.getNat?
  if h : n < bound then return ⟨n,h⟩ else throw "index out of range"


def parseProbe (m n : Nat) (j : Json) : Except String (Probe m n) := do
  match (← j.getArr?).toList with
  | [.str "entry",i,j] => return .entry (← finIndex m i) (← finIndex n j)
  | [.str "minor2",a,b,c,d] =>
      return .minor2 ⟨← finIndex m a, ← finIndex m b, ← finIndex n c, ← finIndex n d⟩
  | _ => throw "probe is [entry,row,col] or [minor2,row0,row1,col0,col1]"


def parseHistory (k : Nat) (j : Json) : Except String (List (Fin k × Bool)) := do
  let xs ← j.getArr?
  if xs.size > 32 then throw "history cap"
  xs.toList.mapM fun x => do
    match (← x.getArr?).toList with
    | [p,o] => return (← finIndex k p, ← o.getBool?)
    | _ => throw "history entries are [probeIndex,outcome]"


def parseRats (expected : Nat) (j : Json) : Except String (Array ℚ) := do
  let xs ← j.getArr?
  if xs.size != expected then throw "rational vector length mismatch"
  xs.mapM PlannerRuntime.parseRat


def replay {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]
    (m : MultiLevel.Model Ω P) : MultiLevel.State m →
      List (P × Bool) → Except String (MultiLevel.State m)
  | s, [] => .ok s
  | s, (p,o)::tail => do
      if s.done then throw "history continues after terminal action"
      if _hp : p ∈ s.remaining then
        let a := MultiLevel.Action.probe p
        let q := MultiLevel.probability m s a o
        if 0 < q then replay m (MultiLevel.step m s a o) tail
        else throw "observation has zero probability under retained catalogue"
      else throw "probe is unavailable or repeated"


def actionWire {k : Nat} : MultiLevel.Action (Fin k) → Json
  | .stop => Json.mkObj [("kind",.str "stop")]
  | .reuse => Json.mkObj [("kind",.str "reuse")]
  | .cold => Json.mkObj [("kind",.str "cold")]
  | .probe p => Json.mkObj [("kind",.str "probe"),("index",toJson p.val)]


def stateWire {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]
    {m : MultiLevel.Model Ω P} (s : MultiLevel.State m) : Json :=
  Json.mkObj [("retained_worlds",toJson s.worlds.card),
    ("remaining_probes",toJson s.remaining.length),("rank_floor",toJson s.lower),
    ("done",toJson s.done)]


def probeRows {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]
    (m : MultiLevel.Model Ω P) (s : MultiLevel.State m) (indexOf : P → Nat) : Json :=
  toJson (s.remaining.map fun p => Json.mkObj [
    ("index",toJson (indexOf p)),
    ("certified_level",toJson (m.level p)),
    ("success_probability",.str (toString (MultiLevel.successProb m s p))),
    ("fee",.str (toString (m.fee p)))])


def process (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "multi-level-affine-f5-v1",rowsJ,colsJ,matricesJ,probesJ,feesJ,
      reuseEnabledJ,reusePayoffJ,coldPayoffJ,horizonJ,historyJ] =>
    let rows ← dimension rowsJ
    let cols ← dimension colsJ
    let matrixRaw ← matricesJ.getArr?
    if matrixRaw.size > 32 then throw "world catalogue cap"
    let matrices ← matrixRaw.mapM (matrix cols rows)
    if hWorlds : 0 < matrices.size then
      let probeRaw ← probesJ.getArr?
      if probeRaw.size > 16 then throw "probe catalogue cap"
      let probes ← probeRaw.mapM (parseProbe rows cols)
      let feeRaw ← feesJ.getArr?
      if feeRaw.size != probes.size then throw "fee/probe length mismatch"
      let fees ← feeRaw.mapM parseNonnegativeRat
      let reuseEnabled ← reuseEnabledJ.getBool?
      let reusePayoffs ← parseRats matrices.size reusePayoffJ
      let coldPayoffs ← parseRats matrices.size coldPayoffJ
      let horizon ← boundedNat 8 horizonJ
      let history ← parseHistory probes.size historyJ
      let c : Catalogue F (Fin matrices.size) (Fin probes.size) cols rows := {
        matrix := fun i => matrices[i]
        probe := fun i => probes[i]
        fee := fun i => (fees[i.val]!).value
        fee_nonneg := fun i => (fees[i.val]!).nonnegative
        reuseAvailable := reuseEnabled
        reusePayoff := fun i => reusePayoffs[i.val]!
        coldPayoff := fun i => coldPayoffs[i.val]! }
      let md := model c
      let initial : MultiLevel.State md := {
        worlds := Finset.univ
        worlds_nonempty := ⟨⟨0,hWorlds⟩,Finset.mem_univ _⟩
        remaining := List.finRange probes.size
        remaining_nodup := List.nodup_finRange _
        lower := 0
        done := false }
      let current ← replay md initial history
      let result := ExecutablePlanner.evaluate (MultiLevel.executable md) horizon current
      let choice := result.choice.getD .stop
      let branchRows := match choice with
        | .probe p => Json.mkObj [
              ("success_probability",.str (toString (MultiLevel.successProb md current p))),
              ("after_failure",stateWire (MultiLevel.step md current (.probe p) false)),
              ("after_success",stateWire (MultiLevel.step md current (.probe p) true))]
        | _ => Json.null
      return Json.mkObj [
          ("status",.str "optimal_multi_level_affine_policy"),
          ("field",.str "ZMod(5)"),
          ("objective",.str "declared net reuse/cold payoff minus probe fees"),
          ("horizon",toJson horizon),("state",stateWire current),
          ("choice",actionWire choice),("expected_net_value",.str (toString result.score)),
          ("planning_work",toJson result.work),
          ("reuse_available",toJson reuseEnabled),
          ("reuse_expected_payoff",.str (toString (MultiLevel.average md current md.reusePayoff))),
          ("cold_expected_payoff",.str (toString (MultiLevel.average md current md.coldPayoff))),
          ("probe_table",probeRows md current Fin.val),
          ("selected_branches",branchRows),
          ("scope",.str "uniform finite catalogue; exact entry/minor reports; payoffs are declared model data; read-only advice")]
    else throw "at least one workload matrix is required"
  | _ => throw "unknown multi-level request"

end Komorebi.AVOC.Affine.MultiLevelCodec
