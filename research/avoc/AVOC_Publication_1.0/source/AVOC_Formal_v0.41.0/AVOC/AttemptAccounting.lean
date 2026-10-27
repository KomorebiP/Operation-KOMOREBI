import Std

namespace Komorebi.AVOC.Attempts

/-- A separate nominal envelope for all attempts, including failed attempts. -/
structure Limits where
  credits : Nat
  attempts : Nat
  deriving Repr, DecidableEq

/-- Operation number is logical. Generation identifies one paid physical attempt. -/
structure Ticket where
  operation : Nat
  generation : Nat
  fee : Nat
  deriving Repr, DecidableEq

structure Ledger where
  charged : Nat
  confirmed : Nat
  reserved : Nat
  current : Option Ticket
  published : Bool
  terminal : Bool
  deriving Repr, DecidableEq

def initial : Ledger := ⟨0, 0, 0, none, false, false⟩

def held (l : Ledger) : Nat := match l.current with
  | none => 0
  | some t => t.fee

def Safe (lim : Limits) (l : Ledger) : Prop :=
  l.charged ≤ lim.credits ∧ l.reserved ≤ lim.attempts ∧
  l.confirmed + held l ≤ l.charged ∧
  (∀ t, l.current = some t → t.generation < l.reserved) ∧
  (l.published = true → l.current ≠ none)

def room (lim : Limits) (l : Ledger) (fee : Nat) : Prop :=
  l.charged + fee ≤ lim.credits ∧ l.reserved < lim.attempts

instance (lim : Limits) (l : Ledger) (fee : Nat) : Decidable (room lim l fee) :=
  inferInstanceAs (Decidable (_ ∧ _))

def reserve (lim : Limits) (l : Ledger) (operation fee : Nat) : Except String Ledger :=
  if l.terminal = false ∧ l.published = false ∧ l.current = none ∧ room lim l fee then
    .ok { l with charged := l.charged + fee, reserved := l.reserved + 1, current := some ⟨operation, l.reserved, fee⟩ }
  else .error "reservation refused"

/-- Renewal is charged afresh and cannot change the operation or its fee. -/
def renew (lim : Limits) (l : Ledger) (old : Ticket) : Except String Ledger :=
  if l.terminal = false ∧ l.published = false ∧ l.current = some old ∧ room lim l old.fee then
    .ok { l with charged := l.charged + old.fee, reserved := l.reserved + 1, current := some {old with generation := l.reserved} }
  else .error "retry refused"

/-- A stale attempt must not publish even when its artifact bytes still match. -/
def publish (l : Ledger) (t : Ticket) : Except String Ledger :=
  if l.terminal = false ∧ l.published = false ∧ l.current = some t then
    .ok {l with published := true}
  else .error "publication refused"

/-- Call only after the committed receipt passed the separate semantic monitor. -/
def settle (l : Ledger) (t : Ticket) : Except String Ledger :=
  if l.terminal = false ∧ l.published = true ∧ l.current = some t then
    .ok {l with confirmed := l.confirmed + t.fee, current := none, published := false}
  else .error "settlement refused"

/-- Terminal abandonment is not a scientific stop or rejection observation. -/
def abandon (l : Ledger) (t : Ticket) : Except String Ledger :=
  if l.terminal = false ∧ l.published = false ∧ l.current = some t then
    .ok {l with current := none, terminal := true}
  else .error "abandonment refused"

@[simp] theorem initial_safe (lim : Limits) : Safe lim initial := by
  simp [Safe, initial, held]

theorem reserve_contract (lim : Limits) (l r : Ledger) (op fee : Nat)
    (h : reserve lim l op fee = .ok r) :
    l.terminal = false ∧ l.published = false ∧ l.current = none ∧ room lim l fee ∧
    r = {l with charged := l.charged + fee, reserved := l.reserved + 1, current := some ⟨op, l.reserved, fee⟩} := by
  by_cases hc : l.terminal = false ∧ l.published = false ∧ l.current = none ∧ room lim l fee
  · have hr := h
    simp only [reserve, ite_eq_left hc, Except.ok.injEq] at hr
    exact ⟨hc.1, hc.2.1, hc.2.2.1, hc.2.2.2, hr.symm⟩
  · simp [reserve, hc] at h

theorem renew_contract (lim : Limits) (l r : Ledger) (t : Ticket)
    (h : renew lim l t = .ok r) :
    l.terminal = false ∧ l.published = false ∧ l.current = some t ∧ room lim l t.fee ∧
    r = {l with charged := l.charged + t.fee, reserved := l.reserved + 1, current := some {t with generation := l.reserved}} := by
  by_cases hc : l.terminal = false ∧ l.published = false ∧ l.current = some t ∧ room lim l t.fee
  · have hr := h
    simp only [renew, ite_eq_left hc, Except.ok.injEq] at hr
    exact ⟨hc.1, hc.2.1, hc.2.2.1, hc.2.2.2, hr.symm⟩
  · simp [renew, hc] at h

theorem publish_contract (l r : Ledger) (t : Ticket) (h : publish l t = .ok r) :
    l.terminal = false ∧ l.published = false ∧ l.current = some t ∧
      r = {l with published := true} := by
  by_cases hc : l.terminal = false ∧ l.published = false ∧ l.current = some t
  · have hr := h
    simp only [publish, ite_eq_left hc, Except.ok.injEq] at hr
    exact ⟨hc.1, hc.2.1, hc.2.2, hr.symm⟩
  · simp [publish, hc] at h

theorem settle_contract (l r : Ledger) (t : Ticket) (h : settle l t = .ok r) :
    l.terminal = false ∧ l.published = true ∧ l.current = some t ∧
      r = {l with confirmed := l.confirmed + t.fee, current := none, published := false} := by
  by_cases hc : l.terminal = false ∧ l.published = true ∧ l.current = some t
  · have hr := h
    simp only [settle, ite_eq_left hc, Except.ok.injEq] at hr
    exact ⟨hc.1, hc.2.1, hc.2.2, hr.symm⟩
  · simp [settle, hc] at h

theorem abandon_contract (l r : Ledger) (t : Ticket) (h : abandon l t = .ok r) :
    l.terminal = false ∧ l.published = false ∧ l.current = some t ∧
      r = {l with current := none, terminal := true} := by
  by_cases hc : l.terminal = false ∧ l.published = false ∧ l.current = some t
  · have hr := h
    simp only [abandon, ite_eq_left hc, Except.ok.injEq] at hr
    exact ⟨hc.1, hc.2.1, hc.2.2, hr.symm⟩
  · simp [abandon, hc] at h

theorem reserve_safe (lim : Limits) (l r : Ledger) (op fee : Nat)
    (hs : Safe lim l) (h : reserve lim l op fee = .ok r) : Safe lim r := by
  obtain ⟨_, hp, hc, hm, rfl⟩ := reserve_contract lim l r op fee h
  rcases hs with ⟨_, _, hh, _, _⟩
  simp only [held, hc] at hh
  refine ⟨hm.1, by change l.reserved + 1 ≤ lim.attempts; have := hm.2; omega, ?_, ?_, ?_⟩
  · simp only [held]; omega
  · intro t ht
    cases ht
    simp
  · simp

theorem renew_safe (lim : Limits) (l r : Ledger) (t : Ticket)
    (hs : Safe lim l) (h : renew lim l t = .ok r) : Safe lim r := by
  obtain ⟨_, _, hc, hm, rfl⟩ := renew_contract lim l r t h
  rcases hs with ⟨_, _, hh, _, _⟩
  simp only [held, hc] at hh
  refine ⟨hm.1, by change l.reserved + 1 ≤ lim.attempts; have := hm.2; omega, ?_, ?_, ?_⟩
  · simp only [held]; omega
  · intro t' ht
    cases ht
    simp
  · simp

theorem publish_safe (lim : Limits) (l r : Ledger) (t : Ticket)
    (hs : Safe lim l) (h : publish l t = .ok r) : Safe lim r := by
  obtain ⟨_, _, hc, rfl⟩ := publish_contract l r t h
  exact ⟨hs.1, hs.2.1, hs.2.2.1, hs.2.2.2.1, by simp [hc]⟩

theorem settle_safe (lim : Limits) (l r : Ledger) (t : Ticket)
    (hs : Safe lim l) (h : settle l t = .ok r) : Safe lim r := by
  obtain ⟨_, _, hc, rfl⟩ := settle_contract l r t h
  have hh := hs.2.2.1
  simp only [held, hc] at hh
  exact ⟨hs.1, hs.2.1, by simpa [held] using hh, by simp, by simp⟩

theorem abandon_safe (lim : Limits) (l r : Ledger) (t : Ticket)
    (hs : Safe lim l) (h : abandon l t = .ok r) : Safe lim r := by
  obtain ⟨_, hp, _, rfl⟩ := abandon_contract l r t h
  have hh := hs.2.2.1
  exact ⟨hs.1, hs.2.1, by simp only [held]; omega, by simp, by simp [hp]⟩

theorem renew_preserves_confirmed (lim : Limits) (l r : Ledger) (t : Ticket)
    (h : renew lim l t = .ok r) : r.confirmed = l.confirmed := by
  obtain ⟨_, _, _, _, rfl⟩ := renew_contract lim l r t h
  rfl

theorem renew_charge_and_count (lim : Limits) (l r : Ledger) (t : Ticket)
    (h : renew lim l t = .ok r) :
    r.charged = l.charged + t.fee ∧ r.reserved = l.reserved + 1 := by
  obtain ⟨_, _, _, _, rfl⟩ := renew_contract lim l r t h
  exact ⟨rfl, rfl⟩

theorem renew_fresh_generation (lim : Limits) (l r : Ledger) (t : Ticket)
    (hs : Safe lim l) (h : renew lim l t = .ok r) :
    ∃ t', r.current = some t' ∧ t'.operation = t.operation ∧ t'.fee = t.fee ∧
      t.generation < t'.generation := by
  obtain ⟨_, _, hc, _, rfl⟩ := renew_contract lim l r t h
  exact ⟨{t with generation := l.reserved}, rfl, rfl, rfl, hs.2.2.2.1 t hc⟩

theorem stale_publication_rejected (l : Ledger) (t : Ticket)
    (h : l.current ≠ some t) : publish l t = .error "publication refused" := by
  simp [publish, h]

theorem renewed_old_attempt_rejected (lim : Limits) (l r : Ledger) (t : Ticket)
    (hs : Safe lim l) (h : renew lim l t = .ok r) :
    publish r t = .error "publication refused" := by
  obtain ⟨t', hc, _, _, hg⟩ := renew_fresh_generation lim l r t hs h
  apply stale_publication_rejected
  intro he
  have ht : t' = t := Option.some.inj (hc.symm.trans he)
  subst t'
  omega

theorem published_retry_rejected (lim : Limits) (l : Ledger) (t : Ticket)
    (h : l.published = true) : renew lim l t = .error "retry refused" := by
  simp [renew, h]

theorem published_abandonment_rejected (l : Ledger) (t : Ticket)
    (h : l.published = true) : abandon l t = .error "abandonment refused" := by
  simp [abandon, h]

theorem charge_not_refunded_on_abandon (l r : Ledger) (t : Ticket)
    (h : abandon l t = .ok r) :
    r.charged = l.charged ∧ r.confirmed = l.confirmed ∧ r.terminal = true := by
  obtain ⟨_, _, _, rfl⟩ := abandon_contract l r t h
  exact ⟨rfl, rfl, rfl⟩

theorem terminal_reservation_rejected (lim : Limits) (l : Ledger) (op fee : Nat)
    (h : l.terminal = true) : reserve lim l op fee = .error "reservation refused" := by
  simp [reserve, h]

theorem exhausted_count_rejects_zero_fee (lim : Limits) (l : Ledger) (t : Ticket)
    (h : lim.attempts ≤ l.reserved) : renew lim l t = .error "retry refused" := by
  have hn : ¬l.reserved < lim.attempts := by omega
  simp [renew, room, hn]

theorem exhausted_credit_rejects_retry (lim : Limits) (l : Ledger) (t : Ticket)
    (h : lim.credits < l.charged + t.fee) : renew lim l t = .error "retry refused" := by
  have hn : ¬l.charged + t.fee ≤ lim.credits := by omega
  simp [renew, room, hn]

theorem settle_once (l r : Ledger) (t : Ticket) (h : settle l t = .ok r) :
    settle r t = .error "settlement refused" := by
  obtain ⟨_, _, _, rfl⟩ := settle_contract l r t h
  simp [settle]

theorem settle_no_new_charge (l r : Ledger) (t : Ticket) (h : settle l t = .ok r) :
    r.charged = l.charged ∧ r.confirmed = l.confirmed + t.fee := by
  obtain ⟨_, _, _, rfl⟩ := settle_contract l r t h
  exact ⟨rfl, rfl⟩

inductive Event where
  | reserve (operation fee : Nat)
  | renew (ticket : Ticket)
  | publish (ticket : Ticket)
  | settle (ticket : Ticket)
  | abandon (ticket : Ticket)
  deriving Repr

def step (lim : Limits) (l : Ledger) : Event → Except String Ledger
  | .reserve op f => reserve lim l op f
  | .renew t => renew lim l t
  | .publish t => publish l t
  | .settle t => settle l t
  | .abandon t => abandon l t

def run (lim : Limits) : Ledger → List Event → Except String Ledger
  | l, [] => .ok l
  | l, e :: es => match step lim l e with
    | .error msg => .error msg
    | .ok r => run lim r es

def charge : Event → Nat
  | .reserve _ f => f
  | .renew t => t.fee
  | _ => 0

def attemptCount : Event → Nat
  | .reserve _ _ => 1
  | .renew _ => 1
  | _ => 0

theorem step_safe (lim : Limits) (l r : Ledger) (e : Event)
    (hs : Safe lim l) (h : step lim l e = .ok r) : Safe lim r := by
  cases e with
  | reserve op f => exact reserve_safe lim l r op f hs h
  | renew t => exact renew_safe lim l r t hs h
  | publish t => exact publish_safe lim l r t hs h
  | settle t => exact settle_safe lim l r t hs h
  | abandon t => exact abandon_safe lim l r t hs h

theorem step_accounting (lim : Limits) (l r : Ledger) (e : Event)
    (h : step lim l e = .ok r) :
    r.charged = l.charged + charge e ∧ r.reserved = l.reserved + attemptCount e := by
  cases e with
  | reserve op f =>
      obtain ⟨_, _, _, _, rfl⟩ := reserve_contract lim l r op f h
      exact ⟨rfl, rfl⟩
  | renew t => exact renew_charge_and_count lim l r t h
  | publish t =>
      obtain ⟨_, _, _, rfl⟩ := publish_contract l r t h
      simp [charge, attemptCount]
  | settle t =>
      obtain ⟨_, _, _, rfl⟩ := settle_contract l r t h
      simp [charge, attemptCount]
  | abandon t =>
      obtain ⟨_, _, _, rfl⟩ := abandon_contract l r t h
      simp [charge, attemptCount]

theorem run_safe (lim : Limits) (es : List Event) (l r : Ledger)
    (hs : Safe lim l) (h : run lim l es = .ok r) : Safe lim r := by
  induction es generalizing l with
  | nil => have he : l = r := by simpa [run] using h
           exact he ▸ hs
  | cons e es ih =>
      cases ht : step lim l e with
      | error msg => simp [run, ht] at h
      | ok x => exact ih x (step_safe lim l x e hs ht) (by simpa [run, ht] using h)

theorem run_accounting (lim : Limits) (es : List Event) (l r : Ledger)
    (h : run lim l es = .ok r) :
    r.charged = l.charged + (es.map charge).sum ∧
    r.reserved = l.reserved + (es.map attemptCount).sum := by
  induction es generalizing l with
  | nil => have he : l = r := by simpa [run] using h
           subst r
           simp
  | cons e es ih =>
      cases ht : step lim l e with
      | error msg => simp [run, ht] at h
      | ok x =>
          obtain ⟨hc, hn⟩ := step_accounting lim l x e ht
          obtain ⟨hcc, hnn⟩ := ih x (by simpa [run, ht] using h)
          simp only [List.map_cons, List.sum_cons]
          constructor <;> omega

theorem complete_trace_bounds (lim : Limits) (es : List Event) (r : Ledger)
    (h : run lim initial es = .ok r) :
    r.confirmed ≤ r.charged ∧ r.charged = (es.map charge).sum ∧
    r.charged ≤ lim.credits ∧ (es.map attemptCount).sum ≤ lim.attempts := by
  have hs := run_safe lim es initial r (initial_safe lim) h
  obtain ⟨hc, hn⟩ := run_accounting lim es initial r h
  simp only [initial, Nat.zero_add] at hc hn
  exact ⟨by have := hs.2.2.1; omega, hc, hs.1, by rw [← hn]; exact hs.2.1⟩

end Komorebi.AVOC.Attempts
