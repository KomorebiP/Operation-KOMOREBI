import AVOC.DurableUpgrade

namespace Komorebi.AVOC.DurableUpgrade

open Upgrade

variable {V : Type}

theorem findClosed_append_new (key : String) (xs : List (Closed V)) (r : Closed V)
    (h : findClosed key xs = none) (hk : r.ticket.key = key) :
    findClosed key (xs ++ [r]) = some r := by
  unfold findClosed at *
  simp [List.find?_append, h, hk]

theorem reserve_exact [DecidableEq V] (a : Authority V) (t : Ticket V)
    (xs : List (Closed V)) (hk : findClosed t.key xs = none)
    (hf : Funded a t.before t.proposal) :
    begin a ⟨t.before, none, xs⟩ t =
      .ok ⟨⟨charged a t, some t, xs⟩, true, a.evaluationCost t.proposal.candidate, 0⟩ := by
  simp [begin, hk, hf]

/-- Reservation followed by settlement is exactly the original promotion gate.
Only publication timing changes; no evaluation fee is charged twice. -/
theorem finish_reserved_exact [DecidableEq V] (a : Authority V) (t : Ticket V)
    (xs : List (Closed V)) (hk : findClosed t.key xs = none)
    (hf : Funded a t.before t.proposal) :
    finish a ⟨charged a t, some t, xs⟩ t.key =
      .ok ⟨⟨(Upgrade.step a t.before t.proposal).next, none,
          xs ++ [⟨t, .evaluated (Upgrade.step a t.before t.proposal).outcome⟩]⟩,
        true, 0, (Upgrade.step a t.before t.proposal).switchDebit⟩ := by
  simp [finish, hk, hf]

theorem begin_idempotent [DecidableEq V] (a : Authority V) (j : Journal V)
    (t : Ticket V) (r : Reply V) (h : begin a j t = .ok r) :
    begin a r.journal t = .ok (unchanged r.journal) := by
  unfold begin at h
  split at h
  next rec hr =>
    split at h
    next he => cases h; exact duplicate_closed_begin a j t rec hr he
    · cases h
  next hn =>
    split at h
    next u hu =>
      split at h
      next he => cases h; subst u; exact duplicate_pending_begin a j t hn hu
      · cases h
    · split at h
      · split at h
        · cases h; exact duplicate_pending_begin a _ t hn rfl
        · cases h
      · cases h

theorem finish_idempotent [DecidableEq V] (a : Authority V) (j : Journal V)
    (key : String) (r : Reply V) (h : finish a j key = .ok r) :
    finish a r.journal key = .ok (unchanged r.journal) := by
  unfold finish at h
  split at h
  next rec hr => cases h; exact finished_key_noop a j key rec hr
  next hn =>
    split at h
    · cases h
    next t _ =>
      split at h
      next hk =>
        split at h
        · split at h
          · cases h
            apply finished_key_noop
            exact findClosed_append_new key j.closed _ hn hk
          · cases h
        · cases h
      · cases h

theorem abandon_idempotent (j : Journal V) (key : String) (r : Reply V)
    (h : abandon j key = .ok r) : abandon r.journal key = .ok (unchanged r.journal) := by
  unfold abandon at h
  split at h
  next rec hr =>
    split at h
    next he => cases h; simp [abandon, hr, he, unchanged]
    · cases h
  next hn =>
    split at h
    · cases h
    next t _ =>
      split at h
      next hk =>
        cases h
        have hf := findClosed_append_new key j.closed (⟨t, .abandoned⟩) hn hk
        simp [abandon, hf]
      · cases h

theorem finish_does_not_lower_utility [DecidableEq V] (a : Authority V)
    (j : Journal V) (key : String) (r : Reply V) (h : finish a j key = .ok r) :
    a.utility j.current.active ≤ a.utility r.journal.current.active := by
  unfold finish at h
  split at h
  · cases h; exact Int.le_refl _
  · split at h
    · cases h
    next t _ =>
      split at h
      · split at h
        next he =>
          split at h
          · cases h
            simpa [he, charged] using Upgrade.step_utility_nondecreasing a t.before t.proposal
          · cases h
        · cases h
      · cases h

theorem apply_does_not_lower_utility [DecidableEq V] (a : Authority V)
    (j : Journal V) (cmd : Command V) (r : Reply V) (h : apply a j cmd = .ok r) :
    a.utility j.current.active ≤ a.utility r.journal.current.active := by
  cases cmd with
  | begin t => rw [begin_keeps_active a j t r h]; exact Int.le_refl _
  | finish k => exact finish_does_not_lower_utility a j k r h
  | abandon k => rw [abandon_keeps_current j k r h]; exact Int.le_refl _

/-- Witness of the actual accepted command trace and its per-command debits. -/
inductive PaidTrace [DecidableEq V] (a : Authority V) :
    Journal V → List (Command V) → Journal V → Nat → Nat → Prop
  | nil (j) : PaidTrace a j [] j 0 0
  | cons {j cmd r tail out ev sw} (head : apply a j cmd = .ok r)
      (rest : PaidTrace a r.journal tail out ev sw) :
      PaidTrace a j (cmd :: tail) out (r.evaluationDebit + ev) (r.switchDebit + sw)

theorem paid_trace_exact_accounting [DecidableEq V] (a : Authority V)
    {j : Journal V} {cmds : List (Command V)} {out : Journal V} {ev sw : Nat}
    (h : PaidTrace a j cmds out ev sw) :
    out.current.evaluationSpent = j.current.evaluationSpent + ev ∧
    out.current.switchSpent = j.current.switchSpent + sw := by
  induction h with
  | nil => simp
  | @cons j cmd r tail out ev sw head rest ih =>
    have hh := apply_accounting a j cmd r head
    constructor <;> omega

theorem replay_has_paid_trace [DecidableEq V] (a : Authority V)
    (j : Journal V) (cmds : List (Command V)) (out : Journal V)
    (h : replay a j cmds = .ok out) : ∃ ev sw, PaidTrace a j cmds out ev sw := by
  induction cmds generalizing j with
  | nil => cases h; exact ⟨0, 0, .nil _⟩
  | cons cmd tail ih =>
    cases he : apply a j cmd with
    | error msg => simp [replay, he] at h
    | ok r =>
      have hh : replay a r.journal tail = .ok out := by simpa [replay, he] using h
      obtain ⟨ev, sw, ht⟩ := ih _ hh
      exact ⟨r.evaluationDebit + ev, r.switchDebit + sw, .cons he ht⟩

theorem paid_trace_no_overspend [DecidableEq V] (a : Authority V)
    {j : Journal V} {cmds : List (Command V)} {out : Journal V} {ev sw : Nat}
    (hs : Safe a j) (h : PaidTrace a j cmds out ev sw) :
    j.current.evaluationSpent + j.current.switchSpent + ev + sw ≤ a.credits := by
  have hout : Safe a out := by
    induction h with
    | nil => exact hs
    | @cons j cmd r tail out ev sw head rest ih =>
      exact ih (apply_safe a j cmd r hs head)
  have hh := paid_trace_exact_accounting a h
  have hb := hout.1.2.1
  omega

theorem replay_utility_nondecreasing [DecidableEq V] (a : Authority V)
    (j : Journal V) (cmds : List (Command V)) (out : Journal V)
    (h : replay a j cmds = .ok out) :
    a.utility j.current.active ≤ a.utility out.current.active := by
  induction cmds generalizing j with
  | nil => cases h; exact Int.le_refl _
  | cons cmd tail ih =>
    cases he : apply a j cmd with
    | error msg => simp [replay, he] at h
    | ok r =>
      have hh : replay a r.journal tail = .ok out := by simpa [replay, he] using h
      exact Int.le_trans (apply_does_not_lower_utility a j cmd r he) (ih _ hh)

/-- Exact matching of a replayed checkpoint. This cannot authenticate the physical
origin of a supplied history, or detect replacement of both log and checkpoint. -/
def restore [DecidableEq V] (a : Authority V) (v : V)
    (cmds : List (Command V)) (actual : Journal V) : Except String (Journal V) :=
  match replay a (initial v) cmds with
  | .error msg => .error msg
  | .ok out => if out = actual then .ok out else .error "log/checkpoint mismatch"

theorem restored_is_actual [DecidableEq V] (a : Authority V) (v : V)
    (cmds : List (Command V)) (actual out : Journal V)
    (h : restore a v cmds actual = .ok out) : out = actual := by
  unfold restore at h
  split at h
  · cases h
  · split at h
    next he => cases h; exact he
    · cases h

theorem restored_certificate [DecidableEq V] (a : Authority V) (v : V)
    (hc : a.Contract v) (cmds : List (Command V)) (actual out : Journal V)
    (h : restore a v cmds actual = .ok out) : Safe a out := by
  unfold restore at h
  split at h
  · cases h
  next j hj =>
    split at h
    · cases h; exact replay_from_initial_safe a v hc cmds _ hj
    · cases h

theorem restored_idempotent [DecidableEq V] (a : Authority V) (v : V)
    (cmds : List (Command V)) (actual out : Journal V)
    (h : restore a v cmds actual = .ok out) : restore a v cmds out = .ok out := by
  have he := restored_is_actual a v cmds actual out h
  subst actual
  exact h

end Komorebi.AVOC.DurableUpgrade
