import AVOC.VerifiedUpgrade

namespace Komorebi.AVOC.DurableUpgrade

open Upgrade

/-- A key is local to one protected campaign. The complete parent state is bound,
including failed-trial spending, not only its active version or revision. -/
structure Ticket (V : Type) where
  key : String
  before : Upgrade.State V
  proposal : Upgrade.Proposal V
  deriving Repr, DecidableEq

inductive Resolution where
  | evaluated (outcome : Upgrade.Outcome)
  | abandoned
  deriving Repr, DecidableEq

structure Closed (V : Type) where
  ticket : Ticket V
  resolution : Resolution
  deriving Repr, DecidableEq

structure Journal (V : Type) where
  current : Upgrade.State V
  pending : Option (Ticket V)
  closed : List (Closed V)
  deriving Repr, DecidableEq

/-- Reserving an evaluation records its entire protected tariff immediately.
The active component, switching expenditure and guarantee are unchanged. -/
def charged (a : Authority V) (t : Ticket V) : Upgrade.State V :=
  { t.before with
    trials := t.before.trials + 1
    evaluationSpent := t.before.evaluationSpent + a.evaluationCost t.proposal.candidate }

def initial (v : V) : Journal V := ⟨Upgrade.initial v, none, []⟩

def Safe (a : Authority V) (j : Journal V) : Prop :=
  Upgrade.Safe a j.current ∧
    ∀ t, j.pending = some t → Upgrade.Safe a t.before ∧
      Funded a t.before t.proposal ∧ j.current = charged a t

def findClosed (key : String) (xs : List (Closed V)) : Option (Closed V) :=
  xs.find? (fun r => r.ticket.key == key)

inductive Command (V : Type) where
  | begin (ticket : Ticket V)
  | finish (key : String)
  | abandon (key : String)
  deriving Repr, DecidableEq

/-- A response carries the protected accounting increments. The runtime must
persist the response state and its canonical event atomically. -/
structure Reply (V : Type) where
  journal : Journal V
  changed : Bool
  evaluationDebit : Nat
  switchDebit : Nat
  deriving Repr, DecidableEq

def unchanged (j : Journal V) : Reply V := ⟨j, false, 0, 0⟩

def begin [DecidableEq V] (a : Authority V) (j : Journal V) (t : Ticket V) :
    Except String (Reply V) :=
  match findClosed t.key j.closed with
  | some r =>
    if r.ticket = t then .ok (unchanged j) else .error "key/request conflict"
  | none => match j.pending with
    | some u =>
      if u = t then .ok (unchanged j) else .error "pending evaluation or key conflict"
    | none =>
      if t.before = j.current then
        if Funded a j.current t.proposal then
          .ok ⟨⟨charged a t, some t, j.closed⟩, true,
            a.evaluationCost t.proposal.candidate, 0⟩
        else .error "evaluation credit exhausted"
      else .error "stale complete parent state"

def finish [DecidableEq V] (a : Authority V) (j : Journal V) (key : String) :
    Except String (Reply V) :=
  match findClosed key j.closed with
  | some _ => .ok (unchanged j)
  | none => match j.pending with
    | none => .error "no pending evaluation"
    | some t =>
      if t.key = key then
        if j.current = charged a t then
          if Funded a t.before t.proposal then
            let r := Upgrade.step a t.before t.proposal
            .ok ⟨⟨r.next, none, j.closed ++ [⟨t, .evaluated r.outcome⟩]⟩,
              true, 0, r.switchDebit⟩
          else .error "invalid reservation"
        else .error "reservation state mismatch"
      else .error "wrong pending key"

def abandon (j : Journal V) (key : String) : Except String (Reply V) :=
  match findClosed key j.closed with
  | some r => match r.resolution with
    | .abandoned => .ok (unchanged j)
    | .evaluated _ => .error "evaluated results cannot be abandoned"
  | none => match j.pending with
    | none => .error "no pending evaluation"
    | some t =>
      if t.key = key then
        .ok ⟨⟨j.current, none, j.closed ++ [⟨t, .abandoned⟩]⟩, true, 0, 0⟩
      else .error "wrong pending key"

def apply [DecidableEq V] (a : Authority V) (j : Journal V) :
    Command V → Except String (Reply V)
  | .begin t => begin a j t
  | .finish key => finish a j key
  | .abandon key => abandon j key

theorem charged_safe (a : Authority V) (t : Ticket V)
    (hs : Upgrade.Safe a t.before) (hf : Funded a t.before t.proposal) :
    Upgrade.Safe a (charged a t) := by
  rcases hs with ⟨hc, _, hu, hg, hn⟩
  exact ⟨hc, hf, hu, hg, by dsimp [charged]; omega⟩

theorem initial_safe (a : Authority V) (v : V) (hc : a.Contract v) :
    Safe a (initial v) := by
  exact ⟨Upgrade.initial_safe a v hc, by intro t h; cases h⟩

theorem begin_safe [DecidableEq V] (a : Authority V) (j : Journal V)
    (t : Ticket V) (r : Reply V) (hs : Safe a j) (h : begin a j t = .ok r) :
    Safe a r.journal := by
  unfold begin at h
  split at h
  · split at h
    · cases h; exact hs
    · cases h
  · split at h
    · split at h
      · cases h; exact hs
      · cases h
    · split at h
      next he =>
        split at h
        next hf =>
          cases h
          have hb : Upgrade.Safe a t.before := by simpa only [he] using hs.1
          have hfund : Funded a t.before t.proposal := by simpa only [he] using hf
          refine ⟨charged_safe a t hb hfund, ?_⟩
          intro u hu
          cases Option.some.inj hu
          exact ⟨hb, hfund, rfl⟩
        · cases h
      · cases h

theorem finish_safe [DecidableEq V] (a : Authority V) (j : Journal V)
    (key : String) (r : Reply V) (hs : Safe a j) (h : finish a j key = .ok r) :
    Safe a r.journal := by
  unfold finish at h
  split at h
  · cases h; exact hs
  · split at h
    · cases h
    next t ht =>
      split at h
      · split at h
        · split at h
          · cases h
            exact ⟨Upgrade.step_safe a t.before t.proposal (hs.2 t ht).1,
              by intro u hu; cases hu⟩
          · cases h
        · cases h
      · cases h

theorem abandon_safe (a : Authority V) (j : Journal V)
    (key : String) (r : Reply V) (hs : Safe a j) (h : abandon j key = .ok r) :
    Safe a r.journal := by
  unfold abandon at h
  split at h
  · split at h
    · cases h; exact hs
    · cases h
  · split at h
    · cases h
    · split at h
      · cases h; exact ⟨hs.1, by intro u hu; cases hu⟩
      · cases h

theorem apply_safe [DecidableEq V] (a : Authority V) (j : Journal V)
    (cmd : Command V) (r : Reply V) (hs : Safe a j) (h : apply a j cmd = .ok r) :
    Safe a r.journal := by
  cases cmd with
  | begin t => exact begin_safe a j t r hs h
  | finish k => exact finish_safe a j k r hs h
  | abandon k => exact abandon_safe a j k r hs h

/-- A reservation never switches the active component, even with a correct proof. -/
theorem begin_keeps_active [DecidableEq V] (a : Authority V) (j : Journal V)
    (t : Ticket V) (r : Reply V) (h : begin a j t = .ok r) :
    r.journal.current.active = j.current.active := by
  unfold begin at h
  split at h <;> split at h
  · cases h; rfl
  · cases h
  · split at h
    · cases h; rfl
    · cases h
  · split at h
    next he =>
      split at h
      · cases h; simp only [charged, he]
      · cases h
    · cases h

theorem abandon_keeps_current (j : Journal V) (key : String) (r : Reply V)
    (h : abandon j key = .ok r) : r.journal.current = j.current := by
  unfold abandon at h
  split at h
  · split at h
    · cases h; rfl
    · cases h
  · split at h
    · cases h
    · split at h
      · cases h; rfl
      · cases h

/-- Finalizing an already prepaid evaluation cannot debit that evaluation again. -/
theorem finish_evaluation_unchanged [DecidableEq V] (a : Authority V)
    (j : Journal V) (key : String) (r : Reply V) (h : finish a j key = .ok r) :
    r.journal.current.evaluationSpent = j.current.evaluationSpent := by
  unfold finish at h
  split at h
  · cases h; rfl
  · split at h
    · cases h
    next t _ =>
      split at h
      · split at h
        next he =>
          split at h
          next hf =>
            cases h
            rw [Upgrade.funded_trial_is_charged a t.before t.proposal hf, he]
            rfl
          · cases h
        · cases h
      · cases h

/-- Each successful command has exact, nonnegative ledger increments. -/
theorem begin_accounting [DecidableEq V] (a : Authority V) (j : Journal V)
    (t : Ticket V) (r : Reply V) (h : begin a j t = .ok r) :
    r.journal.current.evaluationSpent = j.current.evaluationSpent + r.evaluationDebit ∧
    r.journal.current.switchSpent = j.current.switchSpent + r.switchDebit := by
  unfold begin at h
  split at h <;> split at h
  · cases h; simp [unchanged]
  · cases h
  · split at h
    · cases h; simp [unchanged]
    · cases h
  · split at h
    next he =>
      split at h
      · cases h; simp [charged, he]
      · cases h
    · cases h

theorem finish_accounting [DecidableEq V] (a : Authority V) (j : Journal V)
    (key : String) (r : Reply V) (h : finish a j key = .ok r) :
    r.journal.current.evaluationSpent = j.current.evaluationSpent + r.evaluationDebit ∧
    r.journal.current.switchSpent = j.current.switchSpent + r.switchDebit := by
  have hpaid := finish_evaluation_unchanged a j key r h
  unfold finish at h
  split at h
  · cases h; simp [unchanged]
  · split at h
    · cases h
    next t _ =>
      split at h
      · split at h
        next he =>
          split at h
          · cases h
            refine ⟨by simpa using hpaid, ?_⟩
            rw [(Upgrade.step_accounting a t.before t.proposal).2, he]
            rfl
          · cases h
        · cases h
      · cases h

theorem abandon_accounting (j : Journal V) (key : String) (r : Reply V)
    (h : abandon j key = .ok r) :
    r.journal.current.evaluationSpent = j.current.evaluationSpent + r.evaluationDebit ∧
    r.journal.current.switchSpent = j.current.switchSpent + r.switchDebit := by
  unfold abandon at h
  split at h
  · split at h
    · cases h; simp [unchanged]
    · cases h
  · split at h
    · cases h
    · split at h
      · cases h; simp
      · cases h

theorem apply_accounting [DecidableEq V] (a : Authority V) (j : Journal V)
    (cmd : Command V) (r : Reply V) (h : apply a j cmd = .ok r) :
    r.journal.current.evaluationSpent = j.current.evaluationSpent + r.evaluationDebit ∧
    r.journal.current.switchSpent = j.current.switchSpent + r.switchDebit := by
  cases cmd with
  | begin t => exact begin_accounting a j t r h
  | finish k => exact finish_accounting a j k r h
  | abandon k => exact abandon_accounting j k r h

/-- Replaying known keys is inspection: no new state change or charge. -/
theorem duplicate_closed_begin [DecidableEq V] (a : Authority V) (j : Journal V)
    (t : Ticket V) (r : Closed V) (h : findClosed t.key j.closed = some r)
    (he : r.ticket = t) : begin a j t = .ok (unchanged j) := by
  simp [begin, h, he]

theorem duplicate_pending_begin [DecidableEq V] (a : Authority V) (j : Journal V)
    (t : Ticket V) (h : findClosed t.key j.closed = none) (hp : j.pending = some t) :
    begin a j t = .ok (unchanged j) := by simp [begin, h, hp]

theorem finished_key_noop [DecidableEq V] (a : Authority V) (j : Journal V)
    (key : String) (r : Closed V) (h : findClosed key j.closed = some r) :
    finish a j key = .ok (unchanged j) := by simp [finish, h]

theorem changed_key_request_rejected [DecidableEq V] (a : Authority V)
    (j : Journal V) (t : Ticket V) (r : Closed V)
    (h : findClosed t.key j.closed = some r) (he : r.ticket ≠ t) :
    begin a j t = .error "key/request conflict" := by simp [begin, h, he]

theorem stale_complete_parent_rejected [DecidableEq V] (a : Authority V)
    (j : Journal V) (t : Ticket V) (hk : findClosed t.key j.closed = none)
    (hp : j.pending = none) (he : t.before ≠ j.current) :
    begin a j t = .error "stale complete parent state" := by simp [begin, hk, hp, he]

def replay [DecidableEq V] (a : Authority V) :
    Journal V → List (Command V) → Except String (Journal V)
  | j, [] => .ok j
  | j, cmd :: tail => match apply a j cmd with
    | .error msg => .error msg
    | .ok r => replay a r.journal tail

theorem replay_safe [DecidableEq V] (a : Authority V) (j : Journal V)
    (cmds : List (Command V)) (out : Journal V) (hs : Safe a j)
    (h : replay a j cmds = .ok out) : Safe a out := by
  induction cmds generalizing j with
  | nil => cases h; exact hs
  | cons cmd tail ih =>
    cases he : apply a j cmd with
    | error msg => simp [replay, he] at h
    | ok r =>
      have hh : replay a r.journal tail = .ok out := by simpa [replay, he] using h
      exact ih _ (apply_safe a j cmd r hs he) hh

theorem replay_from_initial_safe [DecidableEq V] (a : Authority V) (v : V)
    (hc : a.Contract v) (cmds : List (Command V)) (out : Journal V)
    (h : replay a (initial v) cmds = .ok out) : Safe a out :=
  replay_safe a _ cmds out (initial_safe a v hc) h

theorem replay_contract_and_budget [DecidableEq V] (a : Authority V) (v : V)
    (hc : a.Contract v) (cmds : List (Command V)) (out : Journal V)
    (h : replay a (initial v) cmds = .ok out) :
    a.Contract out.current.active ∧
    out.current.evaluationSpent + out.current.switchSpent ≤ a.credits := by
  have hs := (replay_from_initial_safe a v hc cmds out h).1
  exact ⟨hs.1, hs.2.1⟩

theorem replay_net_bound [DecidableEq V] (a : Authority V) (v : V)
    (hc : a.Contract v) (cmds : List (Command V)) (out : Journal V)
    (h : replay a (initial v) cmds = .ok out) :
    (out.current.guaranteedGain : Int) - (out.current.evaluationSpent : Int) ≤
      Upgrade.campaignNet a out.current :=
  Upgrade.campaign_net_lower_bound a _ (replay_from_initial_safe a v hc cmds out h).1

end Komorebi.AVOC.DurableUpgrade
