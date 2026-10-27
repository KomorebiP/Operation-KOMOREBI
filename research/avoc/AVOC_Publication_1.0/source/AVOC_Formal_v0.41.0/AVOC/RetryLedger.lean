import AVOC.RetryEvaluation
import AVOC.AttemptRecovery

namespace Komorebi.AVOC.RetryLedger

open Attempts

/-- Only remaining credit/count enter future retry value. Already charged work
is retained by the ledger and is not subtracted twice as an incremental cost. -/
def state {Ω : Type*} [Fintype Ω] (lim : Limits) (l : Ledger)
    (b : RationalBelief Ω) : RetryBayesian.State Ω :=
  ⟨b,lim.credits - l.charged,lim.attempts - l.reserved⟩

theorem enabled_iff_room {Ω : Type*} [Fintype Ω] (q : RetryBayesian.Reliability Ω)
    (lim : Limits) (l : Ledger) (b : RationalBelief Ω) (hs : Safe lim l) :
    RetryBayesian.enabled q (state lim l b) = true ↔ room lim l q.fee := by
  change decide (q.fee ≤ lim.credits - l.charged ∧ 0 < lim.attempts - l.reserved) = true ↔
    l.charged + q.fee ≤ lim.credits ∧ l.reserved < lim.attempts
  rw [decide_eq_true_eq]
  have hc := hs.1
  have hn := hs.2.1
  omega

/-- This checks the exact old-ticket phase again. It is not authority to mutate
an external store and does not authenticate the supplied database view. -/
def authorize {Ω : Type*} [Fintype Ω] (q : RetryBayesian.Reliability Ω)
    (lim : Limits) (l : Ledger) (b : RationalBelief Ω) (old : Ticket) : Except String Ledger :=
  if q.fee = old.fee then
    if RetryBayesian.recommend q (state lim l b) then renew lim l old else abandon l old
  else .error "retry cost does not match reserved operation"

theorem authorize_safe {Ω : Type*} [Fintype Ω] (q : RetryBayesian.Reliability Ω)
    (lim : Limits) (l out : Ledger) (b : RationalBelief Ω) (old : Ticket)
    (hs : Safe lim l) (h : authorize q lim l b old = .ok out) : Safe lim out := by
  unfold authorize at h
  split at h
  · split at h
    · exact renew_safe lim l out old hs h
    · exact abandon_safe lim l out old hs h
  · contradiction

theorem retry_recommendation_affordable {Ω : Type*} [Fintype Ω]
    (q : RetryBayesian.Reliability Ω) (lim : Limits) (l : Ledger)
    (b : RationalBelief Ω) (hs : Safe lim l)
    (h : RetryBayesian.recommend q (state lim l b) = true) : room lim l q.fee := by
  apply (enabled_iff_room q lim l b hs).1
  by_contra hn
  have hf : RetryBayesian.enabled q (state lim l b) = false := Bool.eq_false_iff.mpr hn
  simp [RetryBayesian.recommend,hf] at h

theorem recommended_retry_exists {Ω : Type*} [Fintype Ω]
    (q : RetryBayesian.Reliability Ω) (lim : Limits) (l : Ledger)
    (b : RationalBelief Ω) (old : Ticket) (hs : Safe lim l)
    (ht : l.terminal = false) (hp : l.published = false) (hc : l.current = some old)
    (hf : q.fee = old.fee) (hr : RetryBayesian.recommend q (state lim l b) = true) :
    ∃ out, authorize q lim l b old = .ok out ∧ Safe lim out ∧
      out.confirmed = l.confirmed ∧ out.charged = l.charged + old.fee ∧
      publish out old = .error "publication refused" := by
  have hm : room lim l old.fee := by rw [← hf]; exact retry_recommendation_affordable q lim l b hs hr
  let out : Ledger := {l with
    charged := l.charged + old.fee
    reserved := l.reserved + 1
    current := some {old with generation := l.reserved}}
  have he : renew lim l old = .ok out := by simp [renew,ht,hp,hc,hm,out]
  refine ⟨out,by simp [authorize,hf,hr,he],renew_safe lim l out old hs he,
    renew_preserves_confirmed lim l out old he,(renew_charge_and_count lim l out old he).1,?_⟩
  exact renewed_old_attempt_rejected lim l out old hs he

/-- The operational model may update its own reliability posterior. Application
of its recommendation leaves the full scientific checkpoint unchanged. -/
def applyAdvice {Ω : Type*} [Fintype Ω] (q : RetryBayesian.Reliability Ω)
    (b : RationalBelief Ω) (j : PlannerRuntime.Job) (lim : Limits)
    (s : AttemptRecovery.Session j) (old : Ticket) (actual : LiveExecution.StoreView) :
    Except String (AttemptRecovery.Session j) :=
  if q.fee = old.fee then
    if RetryBayesian.recommend q (state lim s.ledger b) then
      AttemptRecovery.retry j lim s old actual
    else AttemptRecovery.cancel j s old actual
  else .error "retry cost does not match reserved operation"

theorem applyAdvice_preserves_science {Ω : Type*} [Fintype Ω]
    (q : RetryBayesian.Reliability Ω) (b : RationalBelief Ω)
    (j : PlannerRuntime.Job) (lim : Limits) (s out : AttemptRecovery.Session j)
    (old : Ticket) (actual : LiveExecution.StoreView) (hs : AttemptRecovery.Safe j lim s)
    (h : applyAdvice q b j lim s old actual = .ok out) :
    AttemptRecovery.Safe j lim out ∧ out.checkpoint = s.checkpoint := by
  unfold applyAdvice at h
  split at h
  · split at h
    · exact ⟨AttemptRecovery.retry_safe j lim s out old actual hs h,
        (AttemptRecovery.retry_contract j lim s out old actual h).1⟩
    · exact ⟨(AttemptRecovery.cancel_safe_and_no_refund j lim s out old actual hs h).1,
        (AttemptRecovery.cancel_contract j s out old actual h).1⟩
  · contradiction

end Komorebi.AVOC.RetryLedger
