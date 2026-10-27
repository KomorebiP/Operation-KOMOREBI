import AVOC.RetryLedger
import AVOC.AttemptCodec

namespace Komorebi.AVOC.RetryDecisionCodec

open Lean

structure Job where
  prior : PlannerRuntime.Probability
  slow : PlannerRuntime.Probability
  fast : PlannerRuntime.Probability
  benefit : ℚ
  benefit_nonneg : 0 ≤ benefit
  limits : Attempts.Limits
  ledger : Attempts.Ledger
  ledger_safe : Attempts.CheckSafe limits ledger
  horizon : Nat

def reliability (j : Job) (fee : Nat) : RetryBayesian.Reliability Bool where
  rate w := if w then j.fast.val else j.slow.val
  rate_nonneg w := by cases w <;> simp only [Bool.false_eq_true,↓reduceIte]; exact j.slow.property.1; exact j.fast.property.1
  rate_le_one w := by cases w <;> simp only [Bool.false_eq_true,↓reduceIte]; exact j.slow.property.2; exact j.fast.property.2
  fee := fee
  benefit := j.benefit
  benefit_nonneg := j.benefit_nonneg

def belief (j : Job) : RationalBelief Bool where
  prob w := if w then j.prior.val else 1 - j.prior.val
  nonneg w := by cases w with
    | false => exact sub_nonneg.mpr j.prior.property.2
    | true => exact j.prior.property.1
  sum_one := by simp

/-- The command is advisory and read-only. No receipt, commit, authorization key,
scientific checkpoint, or database mutation is manufactured by this evaluator. -/
def recommend (j : Job) : Except String Json := do
  if j.ledger.terminal then
    return Json.mkObj [("status",.str "terminal"),("action",.str "none")]
  if j.ledger.published then
    return Json.mkObj [("status",.str "reconcile_first"),("action",.str "none")]
  let t ← match j.ledger.current with
    | none => .error "no unfinished current attempt"
    | some t => pure t
  let q := reliability j t.fee
  let s := RetryLedger.state j.limits j.ledger (belief j)
  let r := Retry.evaluate (RetryBayesian.model q) j.horizon s
  let threshold := j.horizon > 0 && RetryBayesian.recommend q s
  let predictedLedger ← if threshold then Attempts.renew j.limits j.ledger t
    else Attempts.abandon j.ledger t
  return Json.mkObj [
    ("status",.str "ok"),
    ("action",.str (if threshold then "retry" else "abandon")),
    ("horizon",toJson j.horizon),
    ("predicted_net_value",.str (toString r.netValue)),
    ("resolve_probability",.str (toString (RetryBayesian.mean q s.belief))),
    ("net_one_attempt",.str (toString (Retry.immediate (RetryBayesian.model q) s))),
    ("threshold_matches_dynamic_program",toJson (threshold == r.retry)),
    ("value_evaluation_nodes",toJson r.visits),
    ("node_bound",toJson (j.horizon + 1)),
    ("hypothetical_ledger",Attempts.ledgerJson predictedLedger),
    ("scope",.str "fixed latent operational reliability; declared benefit and nominal retry fee; read-only advice, not retry authorization")]

theorem runtime_choice_correct (j : Job) (t : Attempts.Ticket) (n : Nat)
    (h : j.horizon = n + 1) :
    RetryBayesian.recommend (reliability j t.fee)
      (RetryLedger.state j.limits j.ledger (belief j)) =
    (Retry.evaluate (RetryBayesian.model (reliability j t.fee)) j.horizon
      (RetryLedger.state j.limits j.ledger (belief j))).retry := by
  rw [h, Retry.evaluate_choice_is_threshold]

theorem runtime_value_optimal (j : Job) (t : Attempts.Ticket) :
    (Retry.evaluate (RetryBayesian.model (reliability j t.fee)) j.horizon
      (RetryLedger.state j.limits j.ledger (belief j))).netValue =
    Guarded.value (Retry.system (RetryBayesian.model (reliability j t.fee))) j.horizon
      (some (RetryLedger.state j.limits j.ledger (belief j))) :=
  Retry.evaluate_guarded_exact _ _ _

/-- Support-checked update for an explicitly supplied *operational* fault. It does
not infer a fault from a missing receipt, unfinished intent, or process timeout. -/
def updatedJob (j : Job) (fee : Nat) : Job :=
  let b' := RetryBayesian.afterFault (reliability j fee) (belief j)
  have hp : 0 ≤ b'.prob true ∧ b'.prob true ≤ 1 := by
    constructor
    · exact b'.nonneg true
    · have hh := b'.sum_one
      simp only [Fintype.sum_bool] at hh
      linarith [b'.nonneg false]
  {j with prior := ⟨b'.prob true,hp⟩}

def observeFault (j : Job) : Except String Job :=
  match j.ledger.current with
  | none => .error "no current attempt"
  | some t =>
    if 0 < 1 - RetryBayesian.mean (reliability j t.fee) (belief j) then
      .ok (updatedJob j t.fee)
    else .error "fault has zero declared probability"

theorem observeFault_ledger_unchanged (j j' : Job) (h : observeFault j = .ok j') :
    j'.ledger = j.ledger := by
  cases ht : j.ledger.current with
  | none => simp [observeFault,ht] at h
  | some t =>
    by_cases hp : 0 < 1 - RetryBayesian.mean (reliability j t.fee) (belief j)
    · have he : updatedJob j t.fee = j' := by simpa [observeFault,ht,hp] using h
      rw [← he]; rfl
    · simp [observeFault,ht,hp] at h

def parse (wire : Json) : Except String Job := do
  match (← wire.getArr?).toList with
  | [.str "avoc-retry-decision-v1",prior,slow,fast,benefit,limits,ledger,horizon] =>
    let b ← PlannerRuntime.parseProbability prior
    let p0 ← PlannerRuntime.parseProbability slow
    let p1 ← PlannerRuntime.parseProbability fast
    let g ← PlannerRuntime.parseRat benefit
    let lim ← match (← limits.getArr?).toList with
      | [c,n] => pure (⟨← c.getNat?,← n.getNat?⟩ : Attempts.Limits)
      | _ => throw "invalid attempt limits"
    let l ← Attempts.parseLedger ledger
    let n ← horizon.getNat?
    if n > 32 || lim.credits > 1000000 || lim.attempts > 1000000 then
      throw "horizon or ledger limit exceeded"
    if hg : 0 ≤ g then
      if hs : Attempts.CheckSafe lim l then return ⟨b,p0,p1,g,hg,lim,l,hs,n⟩
      else throw "invalid attempt ledger"
    else throw "negative completion benefit"
  | _ => throw "invalid retry-decision request"

def execute (wire : Json) : Except String Json := do
  match (← wire.getArr?).toList with
  | [.str "observe-operational-fault",w] =>
    let j ← parse w
    let j' ← observeFault j
    return Json.mkObj [("status",.str "ok"),("posterior_fast",.str (toString j'.prior.val)),
      ("ledger_unchanged",toJson (j'.ledger == j.ledger)),
      ("recommendation",← recommend j')]
  | _ => recommend (← parse wire)

end Komorebi.AVOC.RetryDecisionCodec
