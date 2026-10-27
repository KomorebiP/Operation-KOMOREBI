import AVOC.AffineTerminal
import AVOC.MultiLevelCodec
import Lean

namespace Komorebi.AVOC.Affine.TerminalCodec

open Lean Codec FactorCodec Factorization ReuseCodec SearchGuard
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.MultiLevelRank

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5


def boundedNat (cap : Nat) (j : Json) : Except String Nat := do
  let n ← j.getNat?
  if n > cap then throw "integer cap exceeded"
  return n


def deploymentWire {n m : Nat} (d : Deployment n m) (calls : Nat)
    (inputs : Array (Fin n → F)) : Json :=
  Json.mkObj [
    ("kind",.str (match d.kind with | .warm => "warm" | .cold => "cold")),
    ("setup_charge",toJson d.setup),
    ("per_call_original",toJson (executionCost d.source)),
    ("per_call_selected",toJson (executionCost d.selected)),
    ("modeled_net_payoff",.str (toString (d.payoff calls))),
    ("selected",FactorCodec.programWire d.selected),
    ("outputs",toJson (inputs.toList.map (fun x => vectorWire (execute d.selected x))))]


def parseInputs (n : Nat) (j : Json) : Except String (Array (Fin n → F)) := do
  let xs ← j.getArr?
  if xs.size > 128 then throw "input batch cap"
  xs.mapM (vector n)


def warm (source saved callsJ paidJ creditJ inputsJ : Json) : Except String Json := do
  let compiled ← load source
  let p := compiled.parsed.program
  let n := compiled.parsed.input
  let m := compiled.parsed.output
  let record ← parseRecord n m saved
  let calls ← boundedNat 1000000 callsJ
  let paid ← boundedNat 100000000 paidJ
  let credit ← boundedNat 100000000 creditJ
  let inputs ← parseInputs n inputsJ
  let setup := normalizationCost p + reuseCharge n m record.candidate.width
  if paid + setup > credit then
    return Json.mkObj [("status",.str "unfunded_warm_validation"),
      ("spent",toJson paid),("required_additional",toJson setup),
      ("remaining",toJson (credit-paid)),("certificate_executed",toJson false)]
  match warmFrom p record paid credit with
  | none =>
      return Json.mkObj [("status",.str "rejected_warm_certificate"),
        ("spent",toJson (paid+setup)),("remaining",toJson (credit-(paid+setup))),
        ("certificate_executed",toJson true)]
  | some d =>
      return Json.mkObj [("status",.str "certified_warm_deployment"),
        ("spent",toJson (paid+d.setup)),("remaining",toJson (credit-(paid+d.setup))),
        ("certificate_executed",toJson true),("deployment",deploymentWire d calls inputs)]


def cold (source candidateJ callsJ generationJ creditJ inputsJ : Json) : Except String Json := do
  let compiled ← load source
  let p := compiled.parsed.program
  let n := compiled.parsed.input
  let m := compiled.parsed.output
  let candidate ← parseCandidate n m candidateJ
  let calls ← boundedNat 1000000 callsJ
  let generation ← boundedNat 100000000 generationJ
  let credit ← boundedNat 100000000 creditJ
  let inputs ← parseInputs n inputsJ
  let required := upfront p candidate.width generation
  if required > credit then
    return Json.mkObj [("status",.str "unfunded_cold_certificate"),
      ("spent",toJson (normalizationCost p + generation)),
      ("required",toJson required),("remaining",toJson (credit-(normalizationCost p+generation))),
      ("certificate_executed",toJson false)]
  match coldFrom p candidate generation credit with
  | none =>
      return Json.mkObj [("status",.str "rejected_cold_certificate"),
        ("spent",toJson required),("remaining",toJson (credit-required)),
        ("certificate_executed",toJson true)]
  | some d =>
      return Json.mkObj [("status",.str "certified_cold_deployment"),
        ("spent",toJson d.setup),("remaining",toJson (credit-d.setup)),
        ("certificate_executed",toJson true),("deployment",deploymentWire d calls inputs)]


def actualProbe (source probeJ : Json) : Except String Json := do
  let compiled ← load source
  let p := compiled.parsed.program
  let n := compiled.parsed.input
  let m := compiled.parsed.output
  let probe ← MultiLevelCodec.parseProbe m n probeJ
  let report := detects (coefficients p).linear probe
  return Json.mkObj [("status",.str "exact_affine_probe_report"),
    ("report",toJson report),("certified_level",toJson (level probe)),
    ("scope",.str "positive report proves the level rank lower bound; negative report has no upper-rank meaning")]


theorem warm_decoded_sound {n m : Nat} (p : DenseProgram F n m)
    (r : Reuse.Record F n m) (paid credit : Nat) (d : Deployment n m)
    (h : warmFrom p r paid credit = some d) :
    (∀ x, execute d.selected x = execute p x) ∧
      executionCost d.selected ≤ executionCost p :=
  warmFrom_sound h


theorem cold_decoded_sound {n m : Nat} (p : DenseProgram F n m)
    (c : Candidate F n m) (generation credit : Nat) (d : Deployment n m)
    (h : coldFrom p c generation credit = some d) :
    (∀ x, execute d.selected x = execute p x) ∧
      executionCost d.selected ≤ executionCost p :=
  coldFrom_sound h


theorem positive_actual_probe_rank {n m : Nat} (p : DenseProgram F n m)
    (q : Probe m n) (h : detects (coefficients p).linear q = true) :
    level q ≤ (coefficients p).linear.rank :=
  detects_rank_lower _ _ h



def normalize (source : Json) : Except String Json := do
  let compiled ← load source
  let p := compiled.parsed.program
  return Json.mkObj [("status",.str "certified_affine_normal_form"),
    ("input_dim",toJson compiled.parsed.input),
    ("output_dim",toJson compiled.parsed.output),
    ("normal",signatureWire (coefficients p)),
    ("per_call_original",toJson (executionCost p)),
    ("per_call_dense",toJson (denseCost compiled.parsed.input compiled.parsed.output))]

def process (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "affine-terminal-warm-f5-v1",source,saved,calls,paid,credit,inputs] =>
      warm source saved calls paid credit inputs
  | [.str "affine-terminal-cold-f5-v1",source,candidate,calls,generation,credit,inputs] =>
      cold source candidate calls generation credit inputs
  | [.str "affine-terminal-probe-f5-v1",source,probe] =>
      actualProbe source probe
  | [.str "affine-terminal-normalize-f5-v1",source] =>
      normalize source
  | _ => throw "unknown affine terminal request"

end Komorebi.AVOC.Affine.TerminalCodec
