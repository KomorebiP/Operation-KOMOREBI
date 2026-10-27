import AVOC.AffineSearchGuard
import AVOC.AffineFactorCodec

namespace Komorebi.AVOC.Affine.ReuseCodec

open Lean Codec FactorCodec Factorization Reuse SearchGuard
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

def schema : String := "avoc-affine-cache-f5-dense-v1"

/-- The descriptor fixes the field, coordinate ordering and cost interface.
Shapes are checked again before creating a typed record. -/
def parseRecord (n m : Nat) (j : Json) : Except String (Record F n m) := do
  match (← j.getArr?).toList with
  | [.str tag,nj,mj,aj,bj,cj] =>
    if tag != schema then throw "certificate schema/field/cost mismatch"
    let rn ← dimension nj
    let rm ← dimension mj
    if rn != n || rm != m then throw "certificate dimension mismatch"
    return ⟨⟨← matrix n m aj, ← vector m bj⟩, ← parseCandidate n m cj⟩
  | _ => throw "malformed affine cache record"

/-- Every invocation revalidates stored evidence. Cached success flags are absent. -/
def imported {n m : Nat} (p : DenseProgram F n m)
    (r : Record F n m) (paid credit : Nat) : Option (Checked (coefficients p)) :=
  if paid + normalizationCost p + reuseCharge n m r.candidate.width ≤ credit then
    importFor (coefficients p) r
  else none

theorem import_budget {n m : Nat} (p : DenseProgram F n m) (r : Record F n m)
    (paid credit : Nat) (c : Checked (coefficients p))
    (h : imported p r paid credit = some c) :
    paid + normalizationCost p + reuseCharge n m r.candidate.width ≤ credit := by
  unfold imported at h
  split at h
  · assumption
  · cases h

theorem imported_sound {n m : Nat} (p : DenseProgram F n m) (r : Record F n m)
    (paid credit : Nat) (c : Checked (coefficients p))
    (h : imported p r paid credit = some c) :
    (∀ x, execute (choose p c) x = execute p x) ∧
    executionCost (choose p c) ≤ executionCost p ∧
    paid + normalizationCost p + reuseCharge n m r.candidate.width ≤ credit :=
  ⟨choose_correct p c, choose_le_original p c, import_budget p r paid credit c h⟩

theorem imported_identity {n m : Nat} (p : DenseProgram F n m) (r : Record F n m)
    (paid credit : Nat) (c : Checked (coefficients p))
    (h : imported p r paid credit = some c) :
    Valid r.signature r.candidate ∧ (coefficients p).linear = r.signature.linear := by
  unfold imported at h
  split at h
  · exact (importFor_iff _ _).1 ⟨c,h⟩
  · cases h

theorem imported_budget_conservation {n m : Nat} (p : DenseProgram F n m)
    (r : Record F n m) (paid credit : Nat) (c : Checked (coefficients p))
    (h : imported p r paid credit = some c) :
    let spent := paid + normalizationCost p + reuseCharge n m r.candidate.width
    spent + (credit-spent) = credit := by
  dsimp
  have hb := import_budget p r paid credit c h
  omega

theorem unfunded_skips_import {n m : Nat} (p : DenseProgram F n m)
    (r : Record F n m) (paid credit : Nat)
    (h : credit < paid + normalizationCost p + reuseCharge n m r.candidate.width) :
    imported p r paid credit = none := by
  simp [imported, Nat.not_le.mpr h]

theorem decoded_import_sound {n m : Nat} (j : Json) (p : DenseProgram F n m)
    (r : Record F n m) (_hp : parseRecord n m j = .ok r) (paid credit : Nat)
    (c : Checked (coefficients p)) (_h : imported p r paid credit = some c) :
    (∀ x, execute (choose p c) x = execute p x) ∧
    (coefficients p).linear.rank = c.candidate.width :=
  ⟨choose_correct p c, valid_rank_exact c.certified⟩

def preflightCharge {n m} (p : DenseProgram F n m) : Nat := normalizationCost p + n*m

def coldMinimum {n m} (p : DenseProgram F n m) (lo : Nat) : Nat :=
  normalizationCost p + reuseCharge n m lo + emissionCharge n m lo

def warmMinimum {n m} (p : DenseProgram F n m) (lo : Nat) : Nat :=
  normalizationCost p + reuseCharge n m lo

theorem coldMinimum_lower {n m : Nat} (p : DenseProgram F n m)
    (c : Checked (coefficients p)) (generation : Nat)
    (hg : emissionCharge n m c.candidate.width ≤ generation) :
    coldMinimum p (widthFloor (coefficients p)) ≤
      normalizationCost p + reuseCharge n m c.candidate.width + generation := by
  have hw := widthFloor_le_checked (coefficients p) c
  have hr := reuseCharge_mono n m hw
  have he := (emissionCharge_mono n m hw).trans hg
  unfold coldMinimum
  omega

theorem warmMinimum_lower {n m : Nat} (p : DenseProgram F n m)
    (c : Checked (coefficients p)) :
    warmMinimum p (widthFloor (coefficients p)) ≤
      normalizationCost p + reuseCharge n m c.candidate.width :=
  Nat.add_le_add_left (reuseCharge_mono n m (widthFloor_le_checked _ c)) _

theorem baseline_floor_le_choice {n m : Nat} (p : DenseProgram F n m)
    (c : Checked (coefficients p)) :
    menuFloor (executionCost (cheaper p (fuse p))) n m (widthFloor (coefficients p)) ≤
      executionCost (choose p c) := by
  rw [Reuse.choose_cost_exact]
  have hd : executionCost (cheaper p (fuse p)) ≤ denseCost n m := cheaper_right p (fuse p)
  unfold menuFloor
  rw [Nat.min_eq_left hd, Reuse.cheaper_cost, fused_execution_cost]
  exact min_le_min_left _ (factorCost_mono (widthFloor_le_checked _ c))

/-- The exact Boolean used by cold preflight rules out positive *remaining* gain
from any certified candidate produced with the declared emission tariff. -/
theorem cold_preflight_skip_sound {n m : Nat} (p : DenseProgram F n m)
    (c : Checked (coefficients p)) (calls generation : Nat)
    (hg : emissionCharge n m c.candidate.width ≤ generation)
    (hs : worthExploring calls (executionCost (cheaper p (fuse p)))
      (menuFloor (executionCost (cheaper p (fuse p))) n m (widthFloor (coefficients p)))
      (coldMinimum p (widthFloor (coefficients p))) = false) :
    calls * executionCost (cheaper p (fuse p)) ≤
      normalizationCost p + reuseCharge n m c.candidate.width + generation +
        calls * executionCost (choose p c) :=
  skipped_search_no_positive_net _ _ _ _ _ _ (menuFloor_le_original _ _ _ _)
    (baseline_floor_le_choice p c) (coldMinimum_lower p c generation hg) hs

theorem warm_preflight_skip_sound {n m : Nat} (p : DenseProgram F n m)
    (c : Checked (coefficients p)) (calls : Nat)
    (hs : worthExploring calls (executionCost (cheaper p (fuse p)))
      (menuFloor (executionCost (cheaper p (fuse p))) n m (widthFloor (coefficients p)))
      (warmMinimum p (widthFloor (coefficients p))) = false) :
    calls * executionCost (cheaper p (fuse p)) ≤
      normalizationCost p + reuseCharge n m c.candidate.width +
        calls * executionCost (choose p c) :=
  skipped_search_no_positive_net _ _ _ _ _ _ (menuFloor_le_original _ _ _ _)
    (baseline_floor_le_choice p c) (warmMinimum_lower p c) hs

/-- Planning preflight normalizes only when its declared charge is affordable.
It does NOT generate factors, multiply candidate witnesses or compute matrix rank. -/
def preflight (source : Json) (calls credit : Nat) : Except String Json := do
  let parsed ← parseProgram 24 source
  let p := parsed.program
  let n := parsed.input
  let m := parsed.output
  if syntaxNodes p > 256 then throw "AST node cap"
  let old := executionCost p
  let preliminary := preflightCharge p
  let basic := [("original",programWire p),("per_call_original",toJson old),
    ("calls",toJson calls),("credit",toJson credit)]
  if old == 0 || calls == 0 then
    return Json.mkObj (basic ++ [("status",.str "no_deployment_opportunity"),
      ("spent",toJson (0:Nat)),("remaining",toJson credit),
      ("selected",programWire p),("per_call_selected",toJson old),
      ("generator_executed",toJson false)])
  if preliminary > credit then
    return Json.mkObj (basic ++ [("status",.str "unfunded_preflight"),
      ("spent",toJson (0:Nat)),("remaining",toJson credit),
      ("selected",programWire p),("per_call_selected",toJson old),
      ("generator_executed",toJson false)])
  let normal := coefficients p
  let base := cheaper p (fuse p)
  let baseCost := executionCost base
  let lo := widthFloor normal
  let floor := menuFloor baseCost n m lo
  return Json.mkObj (basic ++ [
    ("status",.str "preflight"),("normal",signatureWire normal),
    ("selected",programWire base),("per_call_selected",toJson baseCost),
    ("minimum_width_floor",toJson lo),("menu_cost_floor",toJson floor),
    ("prospective_savings_ceiling",toJson (opportunity calls baseCost floor)),
    ("minimum_cold_remaining_charge",toJson (coldMinimum p lo)),
    ("minimum_warm_remaining_charge",toJson (warmMinimum p lo)),
    ("search_may_pay",toJson (worthExploring calls baseCost floor (coldMinimum p lo))),
    ("cache_may_pay",toJson (worthExploring calls baseCost floor (warmMinimum p lo))),
    ("spent",toJson preliminary),("remaining",toJson (credit-preliminary)),
    ("generator_executed",toJson false)])

/-- Typed reimport rechecks the saved certificate and retargets the affine bias.
It always reselects against the current source, including a possibly free identity. -/
def reuse (source saved : Json) (calls paid credit : Nat) (inputJson : Json) : Except String Json := do
  let parsed ← parseProgram 24 source
  let p := parsed.program
  let n := parsed.input
  let m := parsed.output
  if syntaxNodes p > 256 then throw "AST node cap"
  let record ← parseRecord n m saved
  let xs ← inputJson.getArr?
  if xs.size > 128 then throw "input batch cap"
  let inputs ← xs.mapM (vector n)
  if paid > credit then throw "previously paid work exceeds credit"
  let extra := normalizationCost p + reuseCharge n m record.candidate.width
  let required := paid+extra
  let fields := [("calls",toJson calls),("credit",toJson credit),
    ("already_paid",toJson paid),("additional_charge",toJson extra),
    ("normalization_charge",toJson (normalizationCost p)),
    ("certificate_charge",toJson (checkingCharge n m record.candidate.width)),
    ("linear_match_charge",toJson (m*n)),
    ("offset_retarget_charge",toJson (denseCost record.candidate.width m))]
  if required > credit then
    return Json.mkObj (fields ++ [("status",.str "unfunded_cache_validation"),
      ("spent",toJson paid),("remaining",toJson (credit-paid)),
      ("certificate_executed",toJson false),("selected",programWire p)])
  match imported p record paid credit with
  | none => return Json.mkObj (fields ++ [("status",.str "rejected_cache_certificate"),
      ("spent",toJson required),("remaining",toJson (credit-required)),
      ("certificate_executed",toJson true),("selected",programWire p)])
  | some checked =>
    let selected := choose p checked
    let old := executionCost p
    let selectedCost := executionCost selected
    let total := required + calls*selectedCost
    return Json.mkObj (fields ++ [("status",.str "certified_reuse"),
      ("normal",signatureWire (coefficients p)),
      ("rank",toJson checked.candidate.width),
      ("spent",toJson required),("remaining",toJson (credit-required)),
      ("certificate_executed",toJson true),
      ("selected",programWire selected),("per_call_original",toJson old),
      ("per_call_dense",toJson (denseCost n m)),
      ("per_call_factor",toJson (factorCost n m checked.candidate.width)),
      ("per_call_selected",toJson selectedCost),
      ("campaign_total",toJson total),("baseline_deployment",toJson (calls*old)),
      ("net_gain",toJson (((calls*old):Int)-(total:Int))),
      ("breaks_even",toJson (decide (total ≤ calls*old))),
      ("outputs",toJson (inputs.toList.map (fun x => vectorWire (execute selected x)))),
      ("generator_executed",toJson false)])

def process (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "affine-preflight-f5-v1", source, nj, bj] =>
    preflight source (← boundedNat 1000000 nj) (← boundedNat 100000000 bj)
  | [.str "affine-reuse-f5-v1", source, saved, nj, pj, bj, inputs] =>
    reuse source saved (← boundedNat 1000000 nj) (← boundedNat 100000000 pj)
      (← boundedNat 100000000 bj) inputs
  | _ => throw "unknown affine reuse request"

end Komorebi.AVOC.Affine.ReuseCodec
