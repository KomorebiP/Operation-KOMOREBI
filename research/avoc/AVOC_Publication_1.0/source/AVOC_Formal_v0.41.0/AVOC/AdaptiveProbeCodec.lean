import AVOC.AdaptiveRankProbe
import AVOC.AffineCodec
import Lean
import Mathlib.Algebra.Field.ZMod

namespace Komorebi.AVOC.Affine.AdaptiveProbeCodec

open Lean Codec AdaptiveRankProbe
open Komorebi.AVOC.AdaptiveProbe
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

abbrev F := ZMod 5

def boundedNat (cap : Nat) (j : Json) : Except String Nat := do
  let n ← j.getNat?
  if n > cap then throw "integer cap exceeded"
  return n

def finIndex (bound : Nat) (j : Json) : Except String (Fin bound) := do
  let n ← j.getNat?
  if h : n < bound then return ⟨n,h⟩ else throw "index out of range"

def parseProbe (m n : Nat) (j : Json) : Except String (RankProbe.MinorTwo m n) := do
  match (← j.getArr?).toList with
  | [a,b,c,d] => return ⟨← finIndex m a, ← finIndex m b, ← finIndex n c, ← finIndex n d⟩
  | _ => throw "probe requires four indices"

def parseHistory (k : Nat) (j : Json) : Except String (List (Fin k × Bool)) := do
  let xs ← j.getArr?
  if xs.size > 32 then throw "history cap"
  xs.toList.mapM fun x => do
    match (← x.getArr?).toList with
    | [p,o] => return (← finIndex k p, ← o.getBool?)
    | _ => throw "history entries are [probeIndex, outcome]"

def replay {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]
    (m : AdaptiveProbe.Model Ω P) : AdaptiveProbe.State Ω P →
      List (P × Bool) → Except String (AdaptiveProbe.State Ω P)
  | s, [] => .ok s
  | s, (p,o)::tail => do
      if s.done then throw "history continues after terminal success"
      if _hp : p ∈ s.remaining then
        let a := AdaptiveProbe.Action.probe p
        let q := AdaptiveProbe.probability m s a o
        if 0 < q then replay m (AdaptiveProbe.step m s a o) tail
        else throw "observation has zero probability under retained catalogue"
      else throw "probe is unavailable or repeated"

def actionWire {k : Nat} : AdaptiveProbe.Action (Fin k) → Json
  | .stop => Json.mkObj [("kind",.str "stop")]
  | .probe p => Json.mkObj [("kind",.str "probe"),("index",toJson p.val)]

def stateWire {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]
    (s : AdaptiveProbe.State Ω P) : Json :=
  Json.mkObj [("retained_worlds",toJson s.worlds.card),
    ("remaining_probes",toJson s.remaining.length),("done",toJson s.done)]

def probeRows {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]
    (m : AdaptiveProbe.Model Ω P) (s : AdaptiveProbe.State Ω P)
    (indexOf : P → Nat) : Json :=
  toJson (s.remaining.map fun p => Json.mkObj [
    ("index",toJson (indexOf p)),
    ("success_probability",.str (toString (AdaptiveProbe.successProb m s p))),
    ("fee",.str (toString (m.fee p)))])

def process (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "adaptive-rank-probe-f5-v1",rowsJ,colsJ,matricesJ,probesJ,feesJ,gainJ,horizonJ,historyJ] =>
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
      let fees ← feeRaw.mapM (boundedNat 1000000)
      let gain ← boundedNat 100000000 gainJ
      let horizon ← boundedNat 8 horizonJ
      let history ← parseHistory probes.size historyJ
      let c : Catalogue (R:=F) (Ω:=Fin matrices.size) (P:=Fin probes.size)
          (n:=cols) (m:=rows) := {
        matrix := fun i => matrices[i]
        probe := fun i => probes[i]
        fee := fun i => (fees[i.val]! : ℚ)
        fee_nonneg := by intro i; positivity
        denialBenefit := (gain : ℚ)
        denialBenefit_nonneg := by positivity }
      let md := model c
      let initial : AdaptiveProbe.State (Fin matrices.size) (Fin probes.size) := {
        worlds := Finset.univ
        worlds_nonempty := ⟨⟨0,hWorlds⟩,Finset.mem_univ _⟩
        remaining := List.finRange probes.size
        remaining_nodup := List.nodup_finRange _
        done := false }
      let current ← replay md initial history
      let result := ExecutablePlanner.evaluate (AdaptiveProbe.executable md) horizon current
      let choice := result.choice.getD .stop
      let branchRows := match choice with
        | .stop => Json.null
        | .probe p => Json.mkObj [
            ("success_probability",.str (toString (AdaptiveProbe.successProb md current p))),
            ("after_failure",stateWire (AdaptiveProbe.step md current (.probe p) false)),
            ("after_success",stateWire (AdaptiveProbe.step md current (.probe p) true))]
      return Json.mkObj [
        ("status",.str "optimal_uniform_catalogue_probe_policy"),
        ("field",.str "ZMod(5)"),
        ("objective",.str "expected terminal denial benefit minus probe fees"),
        ("horizon",toJson horizon),("state",stateWire current),
        ("choice",actionWire choice),("expected_net_value",.str (toString result.score)),
        ("planning_work",toJson result.work),("probe_table",probeRows md current Fin.val),
        ("selected_branches",branchRows),
        ("scope",.str "uniform finite workload catalogue; deterministic minor outcomes; duplicate worlds encode integer weights; read-only advice")]
    else throw "at least one workload matrix is required"
  | _ => throw "unknown adaptive-probe request"

end Komorebi.AVOC.Affine.AdaptiveProbeCodec
