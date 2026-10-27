import AVOC.WorkflowPlanner
import AVOC.BoundedRecommendation
import Lean.Data.Json.Parser

namespace Komorebi.AVOC.PlannerRuntime

open Lean Certificate Binding ArtifactWorkflow

abbrev Probability := { q : ℚ // 0 ≤ q ∧ q ≤ 1 }
abbrev ParsedArtifact := { a : Artifact // SourceParsed a }

structure Job where
  prior : Probability
  successFalse : Probability
  successTrue : Probability
  registerFee : Nat
  verifyFee : Nat
  admitFee : Nat
  benefit : ℚ
  benefit_nonneg : 0 ≤ benefit
  budget : Nat
  horizon : Nat
  credit : Nat
  price : ℚ
  price_nonneg : 0 ≤ price
  identity : Identity
  artifacts : Array ParsedArtifact
  reports : List Bool
  runTrace : Bool

def belief (j : Job) : RationalBelief Bool where
  prob w := if w then j.prior.val else 1 - j.prior.val
  nonneg w := by cases w <;> simp only [Bool.false_eq_true, ite_false, ite_true] <;> linarith [j.prior.property.1, j.prior.property.2]
  sum_one := by simp

def rawChannel (j : Job) : RationalChannel Bool Bool where
  prob w d := let q := if w then j.successTrue.val else j.successFalse.val
              if d then q else 1 - q
  nonneg w d := by
    cases w <;> cases d <;> simp only [Bool.false_eq_true, ite_false, ite_true] <;>
      linarith [j.successFalse.property.1,j.successFalse.property.2,j.successTrue.property.1,j.successTrue.property.2]
  sum_one w := by simp

def protocol (j : Job) : Protocol Bool (Fin 1) (Fin j.artifacts.size) Bool where
  formula _ := j.identity.statement
  valuation _ := True
  spec _ := {j.identity with dependencies := []}
  describes _ := by
    constructor
    · rfl
    · intro f hf; simp [Binding.context] at hf
  candidate _ c := (j.artifacts[c]).val
  registerFee _ _ := j.registerFee
  verifyFee _ := j.verifyFee
  admitFee _ := j.admitFee
  admissionValue _ := j.benefit
  rawChannel _ := rawChannel j
  rawReceipt s d := if d then s.slot.pending.map (fun t => ⟨t,true⟩) else none

def initial (j : Job) : State Bool (Fin 1) :=
  ⟨belief j, ∅, ⟨0,none⟩, none, none, j.budget, 0, false⟩

def runtimeModel (j : Job) := WorkflowPlanner.model (protocol j) [0] (List.finRange j.artifacts.size)

theorem runtime_realizes (j : Job) :
    ExecutablePlanner.Realizes (runtimeModel j) (controller (protocol j)) := by
  apply WorkflowPlanner.model_realizes
  · intro x; have h : x = 0 := Subsingleton.elim _ _; simp [h]
  · intro c; exact List.mem_finRange c

theorem runtime_branch_bound (j : Job) :
    ExecutablePlanner.BranchBound (runtimeModel j) (3 + j.artifacts.size) 2 := by
  have h := WorkflowPlanner.model_branch_bound (protocol j) [0] (List.finRange j.artifacts.size)
  simpa [runtimeModel] using h

theorem runtime_catalogue_parsed (j : Job) : CatalogueParsed (protocol j) := by
  intro x c; exact (j.artifacts[c]).property

theorem runtime_initial_safe (j : Job) : SourceSafe (protocol j) j.budget (initial j) := by
  constructor
  · constructor
    · refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
      · intro x hx; simp [initial] at hx
      · intro x hx; simp [initial] at hx
      · intro t ht; simp [initial] at ht
      · simp [initial]
      · intro x hx; simp [initial] at hx
      · intro r hr; simp [initial] at hr
    · rfl
  · intro t ht; simp [initial] at ht

def rewardBound (j : Job) : ℚ :=
  j.benefit + (j.registerFee : ℚ) + (j.verifyFee : ℚ) + (j.admitFee : ℚ)

theorem runtime_fee_bound (j : Job) (s : State Bool (Fin 1))
    (a : Action (Fin 1) (Fin j.artifacts.size)) :
    fee (protocol j) s a ≤ j.registerFee + j.verifyFee + j.admitFee := by
  cases a <;> cases ho : s.owner <;> simp [fee, protocol, ho] <;> omega

theorem runtime_reward_bound (j : Job) (s : State Bool (Fin 1))
    (a : Action (Fin 1) (Fin j.artifacts.size)) :
    |reward (protocol j) s a| ≤ rewardBound j := by
  have hf0 : (0 : ℚ) ≤ fee (protocol j) s a := Nat.cast_nonneg _
  have hf : (fee (protocol j) s a : ℚ) ≤
      (j.registerFee : ℚ) + (j.verifyFee : ℚ) + (j.admitFee : ℚ) := by
    exact_mod_cast runtime_fee_bound j s a
  have hneg : |-(fee (protocol j) s a : ℚ)| ≤ rewardBound j := by
    rw [abs_neg, abs_of_nonneg hf0]
    unfold rewardBound
    linarith [j.benefit_nonneg]
  have hpos : |j.benefit - (fee (protocol j) s a : ℚ)| ≤ rewardBound j := by
    apply abs_le.mpr
    unfold rewardBound
    constructor <;> linarith [j.benefit_nonneg]
  cases a with
  | register x c => simpa only [reward, zero_sub] using hneg
  | verify => simpa only [reward, zero_sub] using hneg
  | stop => simpa only [reward, zero_sub] using hneg
  | admit =>
      cases ho : s.owner with
      | none => simpa only [reward, ho, zero_sub] using hneg
      | some x =>
          cases hr : s.checked with
          | none => simpa only [reward, ho, hr, zero_sub] using hneg
          | some r =>
              cases hc : (Binding.consume s.slot ((protocol j).spec x) r).2 with
              | none => simpa only [reward, ho, hr, hc, zero_sub] using hneg
              | some t =>
                  simp only [reward, ho, hr, hc]
                  exact hpos

def recommend (j : Job) (horizon : Nat) (s : State Bool (Fin 1)) :=
  ExecutablePlanner.recommend (runtimeModel j) (3 + j.artifacts.size) 2 horizon j.credit
    (fun _ => .stop) s

theorem runtime_recommend_allowed (j : Job) (horizon : Nat) (s : State Bool (Fin 1)) :
    Allowed (protocol j) s (recommend j horizon s).action := by
  apply (mem_actions (protocol j) s _).mp
  exact ExecutablePlanner.recommend_allowed _ _ (runtime_realizes j) _ _ _ _
    (fun _ => .stop) (fun t => (mem_actions (protocol j) t .stop).mpr (stop_allowed _ _)) s

theorem runtime_recommend_credit (j : Job) (horizon : Nat) (s : State Bool (Fin 1)) :
    (recommend j horizon s).work ≤ j.credit ∧
    (recommend j horizon s).work + (recommend j horizon s).remaining = j.credit := by
  have h := ExecutablePlanner.recommend_credit _ _ _ horizon j.credit (runtime_branch_bound j)
    (fun _ => .stop) s
  exact ⟨h.1.trans h.2.1,h.2.2⟩

theorem runtime_recommend_gap (j : Job) (n : Nat) (s : State Bool (Fin 1)) :
    Guarded.value (controller (protocol j)) (n + 1) s -
      Guarded.qValue (controller (protocol j)) n s (recommend j (n + 1) s).action ≤
    2 * ((n + 1 - (recommend j (n + 1) s).depth : Nat) : ℚ) * rewardBound j := by
  apply ExecutablePlanner.recommend_gap _ _ (runtime_realizes j) _ _ j.credit n
    (fun _ => .stop) (fun t => (mem_actions (protocol j) t .stop).mpr (stop_allowed _ _))
  intro t a _; exact runtime_reward_bound j t a

/-- The actual executable selector, not a separate ideal policy, preserves
source/certificate/budget invariants on every observation branch. -/
theorem runtime_policy_source_safe (j : Job) (n : Nat) :
    Guarded.TreeSafe (controller (protocol j)) (SourceSafe (protocol j) j.budget)
      (initial j) (Guarded.policyPlan (controller (protocol j))
        (fun k s => (recommend j (k + 1) s).action) n (initial j)) := by
  exact source_bound_approximate_policy_safe (protocol j) (runtime_catalogue_parsed j)
    (fun k s => (recommend j (k + 1) s).action)
    (fun k s => runtime_recommend_allowed j (k + 1) s) j.budget n (initial j)
    (runtime_initial_safe j)

/-- Uniform credit per decision gives a declared depth schedule and a complete
replanning-policy bound. Unused per-call credit is not silently recycled. -/
theorem runtime_policy_regret (j : Job) (n : Nat) (s : State Bool (Fin 1)) :
    let selector := fun k t => (recommend j (k + 1) t).action
    0 ≤ Guarded.value (controller (protocol j)) n s -
      Guarded.planValue (controller (protocol j)) s
        (Guarded.policyPlan (controller (protocol j)) selector n s) ∧
    Guarded.value (controller (protocol j)) n s -
      Guarded.planValue (controller (protocol j)) s
        (Guarded.policyPlan (controller (protocol j)) selector n s) ≤
      Guarded.regretBudget (fun k => 2 *
        ((k + 1 - ExecutablePlanner.selectedDepth (3 + j.artifacts.size) 2
          (k + 1) j.credit : Nat) : ℚ) * rewardBound j) n := by
  exact ExecutablePlanner.recommendation_policy_regret (runtimeModel j)
    (controller (protocol j)) (runtime_realizes j) (3 + j.artifacts.size) 2
    (fun _ => j.credit) (fun _ => .stop)
    (fun t => (mem_actions (protocol j) t .stop).mpr (stop_allowed _ _))
    (rewardBound j) (fun t a _ => runtime_reward_bound j t a) n s

/-- Successful construction contains an actual source-parsing witness. No
separate, unconnected proof AST is supplied to the planner. -/
def parseRetained (i : Identity) (source : String) : Except String ParsedArtifact :=
  match h : artifactFromSource i source with
  | .error e => .error e
  | .ok a => .ok ⟨a, successful_parse_is_sourceParsed i source a h⟩

def parseRat (j : Json) : Except String ℚ := do
  match (← j.getArr?).toList with
  | [num,den] =>
      let n ← num.getInt?
      let d ← den.getNat?
      if d = 0 then throw "zero rational denominator"
      return (n : ℚ) / (d : ℚ)
  | _ => throw "expected rational [integer,natural-denominator]"

def parseProbability (j : Json) : Except String Probability := do
  let q ← parseRat j
  if h : 0 ≤ q ∧ q ≤ 1 then return ⟨q,h⟩ else throw "probability outside [0,1]"

/-- Fixed-arity wire data avoid duplicate object-field interpretation. Input
limits are implementation guards, not a proof of parser bit-complexity. -/
def parseJob (j : Json) : Except String Job := do
  match (← j.getArr?).toList with
  | [.str "avoc-planner-v1",prior,pf,pt,rf,vf,af,benefit,budget,horizon,credit,price,
      .str target,.arr sources,.arr reports,.bool runTrace] =>
      let b ← parseProbability prior
      let p0 ← parseProbability pf
      let p1 ← parseProbability pt
      let r ← rf.getNat?
      let v ← vf.getNat?
      let a ← af.getNat?
      let u ← parseRat benefit
      let budget ← budget.getNat?
      let horizon ← horizon.getNat?
      let credit ← credit.getNat?
      let price ← parseRat price
      if horizon > 12 || credit > 200000 || sources.size > 8 || sources.isEmpty then
        throw "horizon/credit/catalogue limit"
      if r > 1000000 || v > 1000000 || a > 1000000 || budget > 1000000 then
        throw "research fee/budget limit"
      if hprice : 0 ≤ price then
        if hu : 0 ≤ u then
          let formula ← parseFormula 64 (← Json.parse target)
          let identity : Identity := ⟨"root",formula,target,[],[("backend","AVOC-v0.18-propositional") ]⟩
          let artifacts ← sources.mapM (fun s => do
            let bytes ← s.getStr?
            if bytes.utf8ByteSize > 8192 then throw "candidate byte limit"
            parseRetained identity bytes)
          let reports ← reports.toList.mapM Json.getBool?
          return ⟨b,p0,p1,r,v,a,u,hu,budget,horizon,credit,price,hprice,identity,artifacts,reports,runTrace⟩
        else throw "negative admission value"
      else throw "negative planning price"
  | _ => throw "invalid avoc-planner-v1 request"

end Komorebi.AVOC.PlannerRuntime
