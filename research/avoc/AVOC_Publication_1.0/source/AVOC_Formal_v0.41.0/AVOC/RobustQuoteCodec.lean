import AVOC.RobustQuoteRecovery
import AVOC.LazyStagedCodec
import AVOC.AffineReuseCodec
import AVOC.AffineFactorCodec
import Lean

namespace Komorebi.AVOC.Affine.RobustQuoteCodec

open Lean
open Komorebi.AVOC
open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Factorization
open Komorebi.AVOC.Affine.Codec
open Komorebi.AVOC.Affine.FactorCodec
open Komorebi.AVOC.Affine.ReuseCodec
open Komorebi.AVOC.Affine.Staged (Action Status)
open Komorebi.AVOC.Affine.StagedCodec
open Komorebi.AVOC.Affine.LazyStaged
open Komorebi.AVOC.Affine.LazyStagedCodec
open Komorebi.AVOC.Affine.QuoteAuthority
open Komorebi.AVOC.Affine.RobustQuote
open Komorebi.AVOC.Affine.RobustQuoteRecovery

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5

private def getString : Json → Except String String
  | .str s => .ok s
  | _ => .error "expected string"

private def parseKind : Json → Except String Kind
  | .str "warm" => .ok .warm
  | .str "cold" => .ok .cold
  | _ => .error "kind must be warm or cold"

def kindWire : Kind → Json
  | .warm => .str "warm"
  | .cold => .str "cold"

def parseNatBand (j : Json) : Except String NatBand := do
  match (← j.getArr?).toList with
  | [loJ,hiJ] =>
      let lo ← StagedCodec.boundedNat 100000000 loJ
      let hi ← StagedCodec.boundedNat 100000000 hiJ
      if h : lo ≤ hi then return ⟨lo,hi,h⟩
      else throw "natural interval is not ordered"
  | _ => throw "natural interval is [lower,upper]"

def parseRatBand (j : Json) : Except String RatBand := do
  match (← j.getArr?).toList with
  | [loJ,hiJ] =>
      let lo ← PlannerRuntime.parseRat loJ
      let hi ← PlannerRuntime.parseRat hiJ
      if h : lo ≤ hi then return ⟨lo,hi,h⟩
      else throw "rational interval is not ordered"
  | _ => throw "rational interval is [lower,upper]"

def parseProbabilityBand (j : Json) : Except String ProbabilityBand := do
  let b ← parseRatBand j
  if h0 : 0 ≤ b.lower then
    if h1 : b.upper ≤ 1 then return ⟨b,h0,h1⟩
    else throw "probability upper endpoint exceeds one"
  else throw "probability lower endpoint is negative"

def natBandWire (b : NatBand) : Json := Json.arr #[toJson b.lower,toJson b.upper]
def ratWire (q : ℚ) : Json := .str (toString q)
def ratBandWire (b : RatBand) : Json := Json.arr #[ratWire b.lower,ratWire b.upper]
def probabilityBandWire (b : ProbabilityBand) : Json := ratBandWire b.toRatBand

def parseIdentity (n m : Nat) (j : Json) : Except String (Identity n m) := do
  match (← j.getArr?).toList with
  | [kindJ,matrixJ,offsetJ,callsJ,costJ,providerJ,checkerJ,environmentJ,schemaJ] =>
      return {
        kind := ← parseKind kindJ
        source := ⟨← matrix n m matrixJ,← vector m offsetJ⟩
        calls := ← StagedCodec.boundedNat 1000000 callsJ
        costModel := ← getString costJ
        provider := ← getString providerJ
        checker := ← getString checkerJ
        environment := ← getString environmentJ
        schema := ← getString schemaJ }
  | _ => throw "identity is [kind,matrix,offset,calls,costModel,provider,checker,environment,schema]"

def identityWire {n m} (i : Identity n m) : Json :=
  Json.arr #[kindWire i.kind,
    toJson (List.ofFn (fun r => vectorWire (i.source.linear r))),
    vectorWire i.source.offset,toJson i.calls,.str i.costModel,.str i.provider,
    .str i.checker,.str i.environment,.str i.schema]

def parseRawQuote (n m : Nat) (j : Json) : Except String (RawQuote n m) := do
  match (← j.getArr?).toList with
  | [identityJ,setupJ,grossJ,probJ] =>
      let identity ← parseIdentity n m identityJ
      let setup ← parseNatBand setupJ
      let gross ← parseRatBand grossJ
      let probability ← parseProbabilityBand probJ
      return { identity := identity, setup := setup, gross := gross, probability := probability }
  | _ => throw "quote is [identity,setupBand,grossBand,probabilityBand]"

def rawQuoteWire {n m} (q : RawQuote n m) : Json :=
  Json.arr #[identityWire q.identity,natBandWire q.setup,ratBandWire q.gross,
    probabilityBandWire q.probability]

def mkAuthority (k : Kind) (q : RawQuote n m) : Except String (Authority n m k) := do
  if hk : q.identity.kind = k then
    if hg : 0 ≤ q.gross.lower then return ⟨q,hk,hg⟩
    else throw "gross lower bound is negative"
  else throw "quote operation kind mismatch"

structure PackedModel where
  input : Nat
  output : Nat
  model : QuoteAuthority.Model input output

def parseModel (sourceJ callsJ warmJ coldJ : Json) : Except String PackedModel := do
  let compiled ← load sourceJ
  let calls ← StagedCodec.boundedNat 1000000 callsJ
  let wr ← parseRawQuote compiled.parsed.input compiled.parsed.output warmJ
  let cr ← parseRawQuote compiled.parsed.input compiled.parsed.output coldJ
  let wa ← mkAuthority .warm wr
  let ca ← mkAuthority .cold cr
  if hwsb : Affine.check wa.approved.identity.source (coefficients compiled.parsed.program) = true then
    let hws : wa.approved.identity.source = coefficients compiled.parsed.program :=
      (Affine.eq_iff_eval _ _).2 ((Affine.check_iff _ _).1 hwsb)
    if hcsb : Affine.check ca.approved.identity.source (coefficients compiled.parsed.program) = true then
      let hcs : ca.approved.identity.source = coefficients compiled.parsed.program :=
        (Affine.eq_iff_eval _ _).2 ((Affine.check_iff _ _).1 hcsb)
      if hwc : wa.approved.identity.calls = calls then
        if hcc : ca.approved.identity.calls = calls then
          return ⟨compiled.parsed.input,compiled.parsed.output,
            { source := compiled.parsed.program, calls := calls, warm := wa, cold := ca,
              warm_source := hws, cold_source := hcs, warm_calls := hwc, cold_calls := hcc }⟩
        else throw "cold quote workload count mismatch"
      else throw "warm quote workload count mismatch"
    else throw "cold quote source mismatch"
  else throw "warm quote source mismatch"

def actionScore (md : QModel n m) (h : Nat) (s : State md) (a : Action) : ℚ :=
  (ExecutablePlanner.actionEval (LazyStaged.executable (nominal md))
    (ExecutablePlanner.evaluate (LazyStaged.executable (nominal md)) h) s a).score

def lowerScore (md : QModel n m) (h : Nat) (s : State md) (a : Action) : ℚ :=
  actionScore md h s a - localQRadius md h a

def upperScore (md : QModel n m) (h : Nat) (s : State md) (a : Action) : ℚ :=
  actionScore md h s a + localQRadius md h a

theorem actionScore_eq_q (md : QModel n m) (h : Nat) (s : State md) (a : Action) :
    actionScore md h s a = Guarded.qValue (LazyStaged.system (nominal md)) h s a := by
  exact ExecutablePlanner.actionEval_exact
    (LazyStaged.executable (nominal md)) (LazyStaged.system (nominal md))
    (LazyStaged.executable_realizes (nominal md)) _ h
    (LazyStaged.evaluated_value_exact (nominal md) h) s a

@[simp] theorem lowerScore_eq_lowerQ (md : QModel n m) (h : Nat) (s : State md) (a : Action) :
    lowerScore md h s a = lowerQ md h s a := by
  simp [lowerScore,lowerQ,actionScore_eq_q]

@[simp] theorem upperScore_eq_upperQ (md : QModel n m) (h : Nat) (s : State md) (a : Action) :
    upperScore md h s a = upperQ md h s a := by
  simp [upperScore,upperQ,actionScore_eq_q]

def dominatesCheck (md : QModel n m) (h : Nat) (s : State md) (a : Action) : Bool :=
  decide (a ∈ LazyStaged.actions (nominal md) s) &&
    (LazyStaged.actionList (nominal md) s).all
      (fun b => decide (upperScore md h s b ≤ lowerScore md h s a))

theorem dominatesCheck_sound (md : QModel n m) (h : Nat) (s : State md) (a : Action)
    (hc : dominatesCheck md h s a = true) (r : Realization md) :
    ∀ b ∈ (trueSystem md r).actions s,
      Guarded.qValue (trueSystem md r) h s b ≤ Guarded.qValue (trueSystem md r) h s a := by
  have hp : decide (a ∈ LazyStaged.actions (nominal md) s) = true ∧
      (LazyStaged.actionList (nominal md) s).all
        (fun b => decide (upperScore md h s b ≤ lowerScore md h s a)) = true := by
    simpa [dominatesCheck] using hc
  have ha : a ∈ LazyStaged.actions (nominal md) s := of_decide_eq_true hp.1
  apply certified_dominance md h s a ha _ r
  intro b hb
  have hmem : b ∈ LazyStaged.actionList (nominal md) s :=
    (LazyStaged.mem_actionList (nominal md) s b).2 hb
  have hall := List.all_eq_true.mp hp.2 b hmem
  simpa using (of_decide_eq_true hall : upperScore md h s b ≤ lowerScore md h s a)

def exactBandsCheck (md : QModel n m) : Bool :=
  decide ((setupBand md .warm).width = 0) &&
  decide ((setupBand md .cold).width = 0) &&
  decide ((grossBand md .warm).width = 0) &&
  decide ((grossBand md .cold).width = 0) &&
  decide ((probBand md .warm).width = 0) &&
  decide ((probBand md .cold).width = 0)

def actionRowWire (md : QModel n m) (h : Nat) (s : State md) (a : Action) : Json :=
  Json.mkObj [("action",LazyStagedCodec.actionWire a),("nominal_q",ratWire (actionScore md h s a)),
    ("radius",ratWire (localQRadius md h a)),("lower_q",ratWire (lowerScore md h s a)),
    ("upper_q",ratWire (upperScore md h s a)),
    ("certified_dominance",toJson (dominatesCheck md h s a))]

def planReply (md : QModel n m) (s : State md) (h : Nat) : Json :=
  let nominalResult := ExecutablePlanner.evaluate (LazyStaged.executable (nominal md)) (h+1) s
  let robust := robustChoice md h s
  let radius := valueRadius md (h+1)
  let gap := 2 * globalQRadius md h
  Json.mkObj [
    ("status",.str "robust_quote_plan"),
    ("continuation_horizon",toJson h),
    ("robust_choice",LazyStagedCodec.actionWire robust),
    ("nominal_choice",LazyStagedCodec.actionWire (nominalResult.choice.getD .stop)),
    ("nominal_value",ratWire nominalResult.score),
    ("lower_value",ratWire (nominalResult.score-radius)),
    ("upper_value",ratWire (nominalResult.score+radius)),
    ("local_regret_bound",ratWire gap),
    ("whole_policy_regret_bound",ratWire
      (Guarded.regretBudget (fun k => 2 * globalQRadius md k) (h+1))),
    ("exact_bands",toJson (exactBandsCheck md)),
    ("state",planWire s),
    ("actions",Json.arr ((LazyStaged.actionList (nominal md) s).map
      (actionRowWire md h s)).toArray)]

def identityMatches (a b : Identity n m) : Bool :=
  decide (a.kind = b.kind) && Affine.check a.source b.source &&
    decide (a.calls = b.calls) && decide (a.costModel = b.costModel) &&
    decide (a.provider = b.provider) && decide (a.checker = b.checker) &&
    decide (a.environment = b.environment) && decide (a.schema = b.schema)

def rawQuoteMatches (a b : RawQuote n m) : Bool :=
  identityMatches a.identity b.identity &&
    decide (a.setup.lower = b.setup.lower) && decide (a.setup.upper = b.setup.upper) &&
    decide (a.gross.lower = b.gross.lower) && decide (a.gross.upper = b.gross.upper) &&
    decide (a.probability.lower = b.probability.lower) &&
    decide (a.probability.upper = b.probability.upper)

theorem identityMatches_sound {a b : Identity n m}
    (h : identityMatches a b = true) : a = b := by
  simp only [identityMatches, Bool.and_eq_true, decide_eq_true_eq, Affine.check_iff] at h
  rcases h with ⟨⟨⟨⟨⟨⟨⟨hk,hs⟩,hc⟩,hcm⟩,hp⟩,hch⟩,he⟩,hsc⟩
  have hsig : a.source = b.source := (Affine.eq_iff_eval _ _).2 hs
  cases a
  cases b
  simp_all

theorem natBand_eq_of_bounds {a b : NatBand}
    (hl : a.lower = b.lower) (hu : a.upper = b.upper) : a = b := by
  cases a
  cases b
  simp_all

theorem ratBand_eq_of_bounds {a b : RatBand}
    (hl : a.lower = b.lower) (hu : a.upper = b.upper) : a = b := by
  cases a
  cases b
  simp_all

theorem probabilityBand_eq_of_bounds {a b : ProbabilityBand}
    (hl : a.lower = b.lower) (hu : a.upper = b.upper) : a = b := by
  cases a with
  | mk ar an ao =>
    cases b with
    | mk br bn bo =>
      have hr : ar = br := ratBand_eq_of_bounds hl hu
      subst br
      rfl

theorem rawQuoteMatches_sound {a b : RawQuote n m}
    (h : rawQuoteMatches a b = true) : a = b := by
  simp only [rawQuoteMatches, Bool.and_eq_true, decide_eq_true_eq] at h
  rcases h with ⟨⟨⟨⟨⟨⟨hi,hsl⟩,hsu⟩,hgl⟩,hgu⟩,hpl⟩,hpu⟩
  have hid : a.identity = b.identity := identityMatches_sound hi
  have hs : a.setup = b.setup := natBand_eq_of_bounds hsl hsu
  have hg : a.gross = b.gross := ratBand_eq_of_bounds hgl hgu
  have hp : a.probability = b.probability := probabilityBand_eq_of_bounds hpl hpu
  cases a
  cases b
  simp_all

def validateReply (a : Authority n m k) (q : RawQuote n m) : Json :=
  Json.mkObj [("status",.str "quote_validation"),
    ("accepted",toJson (rawQuoteMatches q a.approved)),
    ("approved",rawQuoteWire a.approved),("submitted",rawQuoteWire q)]


def refinedWire {md : QModel n m} {k : Kind} (q : RefinedQuote md k) : Json :=
  Json.mkObj [("setup",toJson q.setup),("gross",ratWire q.gross),
    ("setup_band",natBandWire q.setupBand),("gross_band",ratBandWire q.grossBand),
    ("probability_band",probabilityBandWire q.probabilityBand)]

def boundedArtifactWire {md : QModel n m} {k : Kind} (a : BoundedArtifact md k) : Json :=
  Json.mkObj [("kind",kindWire k),("identity",identityWire a.identity),
    ("setup",toJson a.deployment.setup),("gross",ratWire a.gross),
    ("source_cost",toJson (executionCost a.deployment.source)),
    ("selected_cost",toJson (executionCost a.deployment.selected)),
    ("selected",programWire a.deployment.selected),("refined",refinedWire a.refined)]

def optionalWarmWire {md : QModel n m} : Option (BoundedArtifact md .warm) → Json
  | none => .null
  | some a => boundedArtifactWire a

def optionalColdWire {md : QModel n m} : Option (BoundedArtifact md .cold) → Json
  | none => .null
  | some a => boundedArtifactWire a

def optionalWarmEvidenceWire {md : QModel n m} : Option (RefinedQuote md .warm) → Json
  | none => .null
  | some q => refinedWire q

def optionalColdEvidenceWire {md : QModel n m} : Option (RefinedQuote md .cold) → Json
  | none => .null
  | some q => refinedWire q

def runtimeWire {md : QModel n m} (s : RuntimeState md) : Json :=
  Json.mkObj [("plan",planWire s.plan),("warm_artifact",optionalWarmWire s.warmArtifact),
    ("cold_artifact",optionalColdWire s.coldArtifact),
    ("warm_evidence",optionalWarmEvidenceWire s.warmEvidence),
    ("cold_evidence",optionalColdEvidenceWire s.coldEvidence)]

def parseEmptyRuntime (md : QModel n m) (j : Json) : Except String (RuntimeState md) := do
  let p ← LazyStagedCodec.parsePlan (nominal md) j
  if p.warmStatus = .ready || p.coldStatus = .ready then
    throw "ready state requires retained artifact input"
  return ⟨p,none,none,none,none⟩

def checkedWarmBounded (md : QModel n m) (i : Identity n m)
    (r : Reuse.Record F n m) : Except String (BoundedArtifact md .warm) := do
  if hi : identityMatches i (quoteIdentity md .warm) = true then
    let hieq : i = quoteIdentity md .warm := identityMatches_sound hi
    match h : warmFrom md.source r 0 (setupBand md .warm).upper with
    | none => throw "warm certificate rejected or exceeds setup upper bound"
    | some d =>
        if hs0 : (setupBand md .warm).lower ≤ d.setup then
          if hs1 : d.setup ≤ (setupBand md .warm).upper then
            let gross := LazyStaged.deploymentGross d md.calls
            if hg0 : (grossBand md .warm).lower ≤ gross then
              if hg1 : gross ≤ (grossBand md .warm).upper then
                return ⟨d,i,hieq,warmFrom_kind h,warmFrom_source h,⟨hs0,hs1⟩,⟨hg0,hg1⟩⟩
              else throw "warm artifact gross exceeds authorized interval"
            else throw "warm artifact gross is below authorized interval"
          else throw "warm artifact setup exceeds authorized interval"
        else throw "warm artifact setup is below authorized interval"
  else throw "warm artifact identity mismatch"

def checkedColdBounded (md : QModel n m) (i : Identity n m)
    (c : Candidate F n m) (generation : Nat) : Except String (BoundedArtifact md .cold) := do
  if hi : identityMatches i (quoteIdentity md .cold) = true then
    let hieq : i = quoteIdentity md .cold := identityMatches_sound hi
    match h : coldFrom md.source c generation (setupBand md .cold).upper with
    | none => throw "cold certificate rejected or exceeds setup upper bound"
    | some d =>
        if hs0 : (setupBand md .cold).lower ≤ d.setup then
          if hs1 : d.setup ≤ (setupBand md .cold).upper then
            let gross := LazyStaged.deploymentGross d md.calls
            if hg0 : (grossBand md .cold).lower ≤ gross then
              if hg1 : gross ≤ (grossBand md .cold).upper then
                return ⟨d,i,hieq,coldFrom_kind h,coldFrom_source h,⟨hs0,hs1⟩,⟨hg0,hg1⟩⟩
              else throw "cold artifact gross exceeds authorized interval"
            else throw "cold artifact gross is below authorized interval"
          else throw "cold artifact setup exceeds authorized interval"
        else throw "cold artifact setup is below authorized interval"
  else throw "cold artifact identity mismatch"

def parseOutcome (md : QModel n m) (a : Action) (tagJ identityJ artifactJ generationJ : Json) :
    Except String (Outcome md) := do
  let tag ← getString tagJ
  match tag,a with
  | "no_external",_ => return .noExternal
  | "rejected",_ => return .rejected
  | "fault",_ => return .fault
  | "warm_success",.inspectWarm =>
      let i ← parseIdentity n m identityJ
      let r ← parseRecord n m artifactJ
      return .warmSuccess (← checkedWarmBounded md i r)
  | "cold_success",.generateCold =>
      let i ← parseIdentity n m identityJ
      let c ← parseCandidate n m artifactJ
      let generation ← StagedCodec.boundedNat 100000000 generationJ
      return .coldSuccess (← checkedColdBounded md i c generation)
  | "warm_success",_ => throw "warm success does not match selected action"
  | "cold_success",_ => throw "cold success does not match selected action"
  | _,_ => throw "unknown robust quote outcome"

def transitionReply (md : QModel n m) (s : RuntimeState md) (a : Action) (out : Outcome md) :
    Except String Json := do
  match confirmExec md s a out with
  | none => throw "checked outcome does not realize selected action"
  | some t =>
      return Json.mkObj [("status",.str "robust_quote_transition"),
        ("action",LazyStagedCodec.actionWire a),
        ("outcome",.str (match out.tag with
          | .noExternal => "no_external" | .rejected => "rejected"
          | .warmSuccess => "warm_success" | .coldSuccess => "cold_success"
          | .fault => "fault")),
        ("before",runtimeWire s),("after",runtimeWire t)]

def initialExec (md : QModel n m) (credit : Nat) : RuntimeState md :=
  ⟨LazyStaged.initialPlan (nominal md) credit,none,none,none,none⟩

@[simp] theorem initialExec_eq_initial (md : QModel n m) (credit : Nat) :
    initialExec md credit = RobustQuote.initial md credit := rfl

structure ExecRecovery (md : QModel n m) where
  action : Action
  outcome : Outcome md
  after : RuntimeState md

/-- Executable one-step recovery checker. It validates the exact quote evidence
bound into the intent before re-running only the pure checked transition. -/
def recoverExec (md : QModel n m) (credit : Nat) (a : Action) (out : Outcome md)
    (intentWarm intentCold : RawQuote n m) : Except String (ExecRecovery md) := do
  if _hw : rawQuoteMatches intentWarm (rawQuote md .warm) = true then
    if _hc : rawQuoteMatches intentCold (rawQuote md .cold) = true then
      let s := initialExec md credit
      match confirmExec md s a out with
      | none => throw "committed outcome does not realize selected action"
      | some t => return ⟨a,out,t⟩
    else throw "cold quote evidence changed after planning"
  else throw "warm quote evidence changed after planning"

theorem recoverExec_sound (md : QModel n m) (credit : Nat) (a : Action) (out : Outcome md)
    (iw ic : RawQuote n m) (r : ExecRecovery md)
    (h : recoverExec md credit a out iw ic = .ok r) :
    let c := RobustQuoteRecovery.initial md credit
    acknowledge md c (commitFor md c a out r.after) out (view r.after) (evidence md) =
      .ok ⟨c.next+1,r.after,some (commitFor md c a out r.after)⟩ := by
  dsimp
  by_cases hw : rawQuoteMatches iw (rawQuote md .warm) = true
  · by_cases hc : rawQuoteMatches ic (rawQuote md .cold) = true
    · cases ht : confirmExec md (RobustQuote.initial md credit) a out with
      | none => simp [recoverExec,hw,hc,ht] at h
      | some t =>
          simp only [recoverExec,hw,hc,initialExec_eq_initial,ht] at h
          injection h with hr
          subst r
          have htc := ht
          rw [RobustQuote.confirmExec_eq_confirm] at htc
          apply acknowledge_checked_transition
          · simpa [RobustQuoteRecovery.initial] using htc
          · simp [commitFor,intentFor,RobustQuoteRecovery.initial]
    · simp [recoverExec,hw,hc] at h
  · simp [recoverExec,hw] at h

def recoveryReply (md : QModel n m) (credit : Nat) (a : Action) (out : Outcome md)
    (iw ic : RawQuote n m) : Except String Json := do
  let r ← recoverExec md credit a out iw ic
  return Json.mkObj [("status",.str "robust_quote_recovered"),
    ("sequence_before",toJson (0:Nat)),("sequence_after",toJson (1:Nat)),
    ("action",LazyStagedCodec.actionWire a),("after",runtimeWire r.after),
    ("intent_warm",rawQuoteWire iw),("intent_cold",rawQuoteWire ic),
    ("current_warm",rawQuoteWire (rawQuote md .warm)),
    ("current_cold",rawQuoteWire (rawQuote md .cold)),
    ("commit_outcome",.str (match out.tag with
      | .noExternal => "no_external" | .rejected => "rejected"
      | .warmSuccess => "warm_success" | .coldSuccess => "cold_success" | .fault => "fault")),
    ("duplicate_ack_idempotent",toJson true)]

def parseCore (sourceJ callsJ warmJ coldJ : Json) : Except String PackedModel :=
  parseModel sourceJ callsJ warmJ coldJ

def processOne (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "robust-quote-plan-f5-v1",sourceJ,callsJ,warmJ,coldJ,stateJ,horizonJ] =>
      let ⟨_,_,md⟩ ← parseCore sourceJ callsJ warmJ coldJ
      let s ← LazyStagedCodec.parsePlan (nominal md) stateJ
      let h ← StagedCodec.boundedNat 8 horizonJ
      return planReply md s h
  | [.str "robust-quote-validate-f5-v1",sourceJ,callsJ,warmJ,coldJ,kindJ,submittedJ] =>
      let ⟨n,m,md⟩ ← parseCore sourceJ callsJ warmJ coldJ
      let k ← parseKind kindJ
      let q ← parseRawQuote n m submittedJ
      return match k with
        | .warm => validateReply md.warm q
        | .cold => validateReply md.cold q
  | [.str "robust-quote-transition-f5-v1",sourceJ,callsJ,warmJ,coldJ,stateJ,
      actionJ,outcomeJ,identityJ,artifactJ,generationJ] =>
      let ⟨_,_,md⟩ ← parseCore sourceJ callsJ warmJ coldJ
      let s ← parseEmptyRuntime md stateJ
      let a ← LazyStagedCodec.parseAction actionJ
      let out ← parseOutcome md a outcomeJ identityJ artifactJ generationJ
      transitionReply md s a out
  | [.str "robust-quote-recover-f5-v1",sourceJ,callsJ,warmJ,coldJ,creditJ,
      actionJ,outcomeJ,identityJ,artifactJ,generationJ,intentWarmJ,intentColdJ] =>
      let ⟨n,m,md⟩ ← parseCore sourceJ callsJ warmJ coldJ
      let credit ← StagedCodec.boundedNat 100000000 creditJ
      let a ← LazyStagedCodec.parseAction actionJ
      let out ← parseOutcome md a outcomeJ identityJ artifactJ generationJ
      let iw ← parseRawQuote n m intentWarmJ
      let ic ← parseRawQuote n m intentColdJ
      recoveryReply md credit a out iw ic
  | [.str "robust-quote-unfinished-f5-v1",sourceJ,callsJ,warmJ,coldJ,creditJ,actionJ] =>
      let _ ← parseCore sourceJ callsJ warmJ coldJ
      let _ ← StagedCodec.boundedNat 100000000 creditJ
      let _ ← LazyStagedCodec.parseAction actionJ
      throw "no durable result: do not infer a report or retry"
  | _ => throw "unknown robust quote request"


/-- Batch executable boundary.  Each element is checked independently so expected
rejections remain explicit data rather than aborting unrelated comparisons. -/
def processBatch (requests : Array Json) : Json := Id.run do
  let mut outputs : Array Json := #[]
  for request in requests do
    let item := match processOne request with
      | .ok value => Json.mkObj [("ok",toJson true),("value",value)]
      | .error e => Json.mkObj [("ok",toJson false),("error",.str e)]
    outputs := outputs.push item
  return Json.mkObj [("status",.str "robust_quote_batch"),("results",Json.arr outputs)]

def process (request : Json) : Except String Json := do
  match (← request.getArr?).toList with
  | [.str "robust-quote-batch-v1", Json.arr requests] => return processBatch requests
  | _ => processOne request

end Komorebi.AVOC.Affine.RobustQuoteCodec
