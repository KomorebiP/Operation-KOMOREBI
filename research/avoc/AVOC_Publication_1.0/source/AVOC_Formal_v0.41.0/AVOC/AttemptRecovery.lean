import AVOC.AttemptAccounting
import AVOC.CommitRecovery

namespace Komorebi.AVOC.AttemptRecovery

open PlannerRuntime LiveExecution ArtifactWorkflow

structure Session (j : Job) where
  checkpoint : CommitRecovery.Checkpoint j
  ledger : Attempts.Ledger

def Safe (j : Job) (lim : Attempts.Limits) (s : Session j) : Prop :=
  CommitRecovery.Safe j s.checkpoint ∧ Attempts.Safe lim s.ledger ∧
    s.ledger.confirmed = s.checkpoint.state.core.spent

/-- An operational retry changes only the paid attempt, never the scientific
checkpoint. Absence of a durable publication is checked by the accounting gate;
faithful projection of the protected database is still an external obligation. -/
def retry (j : Job) (lim : Attempts.Limits) (s : Session j)
    (t : Attempts.Ticket) (actual : StoreView) : Except String (Session j) :=
  if view s.checkpoint.state ≠ actual then .error "uncommitted pre-state mismatch"
  else match Attempts.renew lim s.ledger t with
    | .error e => .error e
    | .ok l => .ok ⟨s.checkpoint, l⟩

/-- Administrative termination: no scientific rejection/stop report is created. -/
def cancel (j : Job) (s : Session j) (t : Attempts.Ticket)
    (actual : StoreView) : Except String (Session j) :=
  if view s.checkpoint.state ≠ actual then .error "uncommitted pre-state mismatch"
  else match Attempts.abandon s.ledger t with
    | .error e => .error e
    | .ok l => .ok ⟨s.checkpoint, l⟩

theorem retry_contract (j : Job) (lim : Attempts.Limits) (s r : Session j)
    (t : Attempts.Ticket) (actual : StoreView) (h : retry j lim s t actual = .ok r) :
    r.checkpoint = s.checkpoint ∧ view s.checkpoint.state = actual ∧
      Attempts.renew lim s.ledger t = .ok r.ledger := by
  by_cases hv : view s.checkpoint.state = actual
  · cases hl : Attempts.renew lim s.ledger t with
    | error e => simp [retry, hv, hl] at h
    | ok l =>
        have he : (⟨s.checkpoint, l⟩ : Session j) = r := by simpa [retry, hv, hl] using h
        subst r
        exact ⟨rfl, hv, rfl⟩
  · simp [retry, hv] at h

theorem retry_safe (j : Job) (lim : Attempts.Limits) (s r : Session j)
    (t : Attempts.Ticket) (actual : StoreView) (hs : Safe j lim s)
    (h : retry j lim s t actual = .ok r) : Safe j lim r := by
  obtain ⟨hc, _, hl⟩ := retry_contract j lim s r t actual h
  refine ⟨hc ▸ hs.1, Attempts.renew_safe lim _ _ t hs.2.1 hl, ?_⟩
  rw [Attempts.renew_preserves_confirmed lim _ _ t hl, hc, hs.2.2]

theorem retry_no_bayesian_or_proof_update (j : Job) (lim : Attempts.Limits) (s r : Session j)
    (t : Attempts.Ticket) (actual : StoreView) (h : retry j lim s t actual = .ok r) :
    r.checkpoint.state.core.belief = s.checkpoint.state.core.belief ∧
    r.checkpoint.state.core.completed = s.checkpoint.state.core.completed ∧
    r.checkpoint.next = s.checkpoint.next := by
  have he := (retry_contract j lim s r t actual h).1
  rw [he]
  exact ⟨rfl,rfl,rfl⟩

theorem cancel_contract (j : Job) (s r : Session j) (t : Attempts.Ticket)
    (actual : StoreView) (h : cancel j s t actual = .ok r) :
    r.checkpoint = s.checkpoint ∧ Attempts.abandon s.ledger t = .ok r.ledger := by
  by_cases hv : view s.checkpoint.state = actual
  · cases hl : Attempts.abandon s.ledger t with
    | error e => simp [cancel, hv, hl] at h
    | ok l =>
        have he : (⟨s.checkpoint, l⟩ : Session j) = r := by simpa [cancel, hv, hl] using h
        subst r
        exact ⟨rfl, rfl⟩
  · simp [cancel, hv] at h

theorem cancel_safe_and_no_refund (j : Job) (lim : Attempts.Limits) (s r : Session j)
    (t : Attempts.Ticket) (actual : StoreView) (hs : Safe j lim s)
    (h : cancel j s t actual = .ok r) :
    Safe j lim r ∧ r.ledger.charged = s.ledger.charged ∧ r.ledger.terminal = true := by
  obtain ⟨hc, hl⟩ := cancel_contract j s r t actual h
  obtain ⟨hd, hf, ht⟩ := Attempts.charge_not_refunded_on_abandon _ _ t hl
  refine ⟨⟨hc ▸ hs.1, Attempts.abandon_safe lim _ _ t hs.2.1 hl, ?_⟩,hd,ht⟩
  rw [hf,hc,hs.2.2]

/-- Logical completion still requires the old exact proof-bearing acknowledgement.
The attempt number is fenced separately by the current paid ticket. -/
def confirm (j : Job) (s : Session j) (t : Attempts.Ticket)
    (r : CommitRecovery.Commit j) (actual : StoreView) : Except String (Session j) :=
  if r.intent.sequence = s.checkpoint.next ∧ t.operation = r.intent.sequence ∧
       t.fee = fee (protocol j) s.checkpoint.state.core r.intent.action then
    match Attempts.settle s.ledger t with
    | .error e => .error e
    | .ok l => match CommitRecovery.acknowledge j s.checkpoint r actual with
      | .error e => .error e
      | .ok c => .ok ⟨c,l⟩
  else .error "receipt operation or fee mismatch"

theorem confirm_contract (j : Job) (s out : Session j) (t : Attempts.Ticket)
    (r : CommitRecovery.Commit j) (actual : StoreView)
    (h : confirm j s t r actual = .ok out) :
    r.intent.sequence = s.checkpoint.next ∧
    t.fee = fee (protocol j) s.checkpoint.state.core r.intent.action ∧
    Attempts.settle s.ledger t = .ok out.ledger ∧
    CommitRecovery.acknowledge j s.checkpoint r actual = .ok out.checkpoint := by
  by_cases hc : r.intent.sequence = s.checkpoint.next ∧ t.operation = r.intent.sequence ∧
      t.fee = fee (protocol j) s.checkpoint.state.core r.intent.action
  · cases hl : Attempts.settle s.ledger t with
    | error e => simp [confirm,hc,hl] at h
    | ok l =>
        cases hk : CommitRecovery.acknowledge j s.checkpoint r actual with
        | error e => simp [confirm,hc,hl,hk] at h
        | ok c =>
            have he : (⟨c,l⟩ : Session j) = out := by simpa [confirm,hc,hl,hk] using h
            subst out
            exact ⟨hc.1,hc.2.2,rfl,rfl⟩
  · simp [confirm,hc] at h

theorem confirm_safe (j : Job) (lim : Attempts.Limits) (s out : Session j)
    (t : Attempts.Ticket) (r : CommitRecovery.Commit j) (actual : StoreView)
    (hs : Safe j lim s) (h : confirm j s t r actual = .ok out) : Safe j lim out := by
  obtain ⟨hf,hfee,hl,hc⟩ := confirm_contract j s out t r actual h
  refine ⟨CommitRecovery.acknowledge_safe j _ _ r actual hs.1 hc,
    Attempts.settle_safe lim _ _ t hs.2.1 hl, ?_⟩
  rw [(Attempts.settle_no_new_charge _ _ t hl).2, hs.2.2, hfee]
  exact (CommitRecovery.fresh_acknowledgement_cost j _ _ r actual hc hf).symm

theorem confirm_no_double_attempt_charge (j : Job) (s out : Session j)
    (t : Attempts.Ticket) (r : CommitRecovery.Commit j) (actual : StoreView)
    (h : confirm j s t r actual = .ok out) : out.ledger.charged = s.ledger.charged :=
  (Attempts.settle_no_new_charge _ _ t (confirm_contract j s out t r actual h).2.2.1).1

theorem confirmed_spend_le_attempt_envelope (j : Job) (lim : Attempts.Limits)
    (s : Session j) (h : Safe j lim s) :
    s.checkpoint.state.core.spent ≤ s.ledger.charged ∧ s.ledger.charged ≤ lim.credits := by
  have hi := h.2.1.2.2.1
  rw [h.2.2] at hi
  exact ⟨by omega,h.2.1.1⟩

theorem confirmed_admission_retains_source (j : Job) (lim : Attempts.Limits)
    (s : Session j) (h : Safe j lim s) (ticket : Binding.Ticket)
    (ht : s.checkpoint.state.admitted = some ticket) :
    Binding.Valid ticket.artifact ∧ ArtifactWorkflow.SourceParsed ticket.artifact := h.1.2 ticket ht

end Komorebi.AVOC.AttemptRecovery
