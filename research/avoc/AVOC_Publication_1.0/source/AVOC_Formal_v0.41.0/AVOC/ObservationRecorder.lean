import AVOC.CalibrationLog
import Mathlib.Data.List.Nodup

namespace Komorebi.AVOC.ObservationRecorder

open CalibrationLog

/-- Pure recorder state. Pending intents and terminal records use one id space. -/
structure State (Key : Type) where
  pending : List (Nat × Key)
  log : List (Event Key)
  deriving DecidableEq

inductive Command (Key : Type) where
  | begin (operation : Nat) (key : Key)
  | finish (event : Event Key)
  deriving DecidableEq

variable {Key : Type} [DecidableEq Key]

def initial : State Key := ⟨[], []⟩

def terminalUsed (s : State Key) (id : Nat) : Prop :=
  ∃ e ∈ s.log, e.operation = id

instance (s : State Key) (id : Nat) : Decidable (terminalUsed s id) :=
  inferInstanceAs (Decidable (∃ e ∈ s.log, e.operation = id))

def pendingUsed (s : State Key) (id : Nat) : Prop :=
  ∃ p ∈ s.pending, p.1 = id

instance (s : State Key) (id : Nat) : Decidable (pendingUsed s id) :=
  inferInstanceAs (Decidable (∃ p ∈ s.pending, p.1 = id))

/-- Idempotent exact replay, conflicting id rejection, and explicit intent before
terminal outcome. A late begin replay cannot reopen a terminal operation. -/
def step (s : State Key) : Command Key → Option (State Key)
  | .begin id key =>
      if terminalUsed s id then
        if ∃ e ∈ s.log, e.operation = id ∧ e.key = key then some s else none
      else if pendingUsed s id then
        if (id, key) ∈ s.pending then some s else none
      else some ⟨s.pending ++ [(id, key)], s.log⟩
  | .finish e =>
      if e.outcome = .unfinished then none
      else if e ∈ s.log then some s
      else if terminalUsed s e.operation then none
      else if (e.operation, e.key) ∈ s.pending then
        some ⟨s.pending.filter (fun p => p.1 != e.operation), s.log ++ [e]⟩
      else none

def runFrom (s : State Key) : List (Command Key) → Option (State Key)
  | [] => some s
  | c :: cs => (step s c).bind (fun t => runFrom t cs)

def run (commands : List (Command Key)) : Option (State Key) :=
  runFrom initial commands

/-- Every operation has at most one live intent or terminal entry, and terminal
entries cannot contain an unfinished outcome. -/
structure WellFormed (s : State Key) : Prop where
  pending_ids : (s.pending.map Prod.fst).Nodup
  terminal_ids : (s.log.map Event.operation).Nodup
  disjoint : ∀ p ∈ s.pending, ∀ e ∈ s.log, p.1 ≠ e.operation
  terminal : ∀ e ∈ s.log, e.outcome ≠ .unfinished

omit [DecidableEq Key] in
@[simp] theorem initial_wellFormed : WellFormed (initial : State Key) := by
  constructor <;> simp [initial]

theorem begin_log_unchanged {s t : State Key} {id : Nat} {key : Key}
    (h : step s (.begin id key) = some t) : t.log = s.log := by
  simp only [step] at h
  split at h
  · split at h <;> simp_all
  · split at h
    · split at h <;> simp_all
    · cases Option.some.inj h
      rfl

theorem finish_effect {s t : State Key} {e : Event Key}
    (h : step s (.finish e) = some t) :
    e.outcome ≠ .unfinished ∧
      ((t = s ∧ e ∈ s.log) ∨
       (¬ terminalUsed s e.operation ∧ (e.operation, e.key) ∈ s.pending ∧
        t = ⟨s.pending.filter (fun p => p.1 != e.operation), s.log ++ [e]⟩)) := by
  simp only [step] at h
  split at h
  · simp_all
  · split at h
    · simp_all
    · split at h
      · simp_all
      · split at h <;> simp_all

theorem finish_record {s t : State Key} {e : Event Key}
    (h : step s (.finish e) = some t) : record s.log e = some t.log := by
  obtain ⟨_, h | h⟩ := finish_effect h
  · rcases h with ⟨rfl, he⟩
    exact exact_replay _ _ he
  · rcases h with ⟨hf, _, rfl⟩
    exact fresh_record _ _ hf

@[simp] theorem unfinished_rejected (s : State Key) (id : Nat) (key : Key) :
    step s (.finish ⟨id, key, .unfinished⟩) = none := by
  simp [step]

theorem exact_terminal_replay (s : State Key) (e : Event Key)
    (ht : e.outcome ≠ .unfinished) (he : e ∈ s.log) :
    step s (.finish e) = some s := by
  simp [step, ht, he]

theorem changed_terminal_rejected (s : State Key) (e : Event Key)
    (he : e ∉ s.log) (hu : terminalUsed s e.operation) :
    step s (.finish e) = none := by
  by_cases ht : e.outcome = .unfinished <;> simp [step, ht, he, hu]

theorem missing_intent_rejected (s : State Key) (e : Event Key)
    (he : e ∉ s.log) (hp : (e.operation, e.key) ∉ s.pending) :
    step s (.finish e) = none := by
  by_cases ht : e.outcome = .unfinished <;>
    by_cases hu : terminalUsed s e.operation <;> simp [step, ht, he, hp, hu]

theorem fresh_finish (s : State Key) (e : Event Key)
    (ht : e.outcome ≠ .unfinished) (hu : ¬ terminalUsed s e.operation)
    (hp : (e.operation, e.key) ∈ s.pending) :
    step s (.finish e) =
      some ⟨s.pending.filter (fun p => p.1 != e.operation), s.log ++ [e]⟩ := by
  have he : e ∉ s.log := fun h => hu ⟨e, h, rfl⟩
  simp [step, ht, he, hu, hp]

theorem late_begin_replay (s : State Key) (e : Event Key) (he : e ∈ s.log) :
    step s (.begin e.operation e.key) = some s := by
  have hu : terminalUsed s e.operation := ⟨e, he, rfl⟩
  have hk : ∃ a ∈ s.log, a.operation = e.operation ∧ a.key = e.key :=
    ⟨e, he, rfl, rfl⟩
  simp [step, hu, hk]

theorem pending_begin_replay (s : State Key) (id : Nat) (key : Key)
    (hu : ¬ terminalUsed s id) (hp : (id, key) ∈ s.pending) :
    step s (.begin id key) = some s := by
  have hpu : pendingUsed s id := ⟨(id, key), hp, rfl⟩
  simp [step, hu, hpu, hp]

theorem fresh_begin (s : State Key) (id : Nat) (key : Key)
    (hu : ¬ terminalUsed s id) (hp : ¬ pendingUsed s id) :
    step s (.begin id key) = some ⟨s.pending ++ [(id, key)], s.log⟩ := by
  simp [step, hu, hp]

omit [DecidableEq Key] in
theorem fresh_begin_wellFormed {s : State Key} (hs : WellFormed s)
    (id : Nat) (key : Key) (hu : ¬ terminalUsed s id) (hp : ¬ pendingUsed s id) :
    WellFormed (⟨s.pending ++ [(id, key)], s.log⟩ : State Key) := by
  constructor
  · simp only [List.map_append, List.map_cons, List.map_nil, List.nodup_append]
    refine ⟨hs.pending_ids, by simp, ?_⟩
    intro a ha b hb
    simp only [List.mem_singleton] at hb
    subst b
    intro h
    subst a
    obtain ⟨p, hpm, hpid⟩ := List.mem_map.mp ha
    exact hp ⟨p, hpm, hpid⟩
  · exact hs.terminal_ids
  · intro p hpm e hem
    rcases List.mem_append.mp hpm with hpm | hpm
    · exact hs.disjoint p hpm e hem
    · have heq : p = (id, key) := List.mem_singleton.mp hpm
      subst p
      exact fun h => hu ⟨e, hem, h.symm⟩
  · exact hs.terminal

omit [DecidableEq Key] in
theorem fresh_finish_wellFormed {s : State Key} (hs : WellFormed s)
    (e : Event Key) (ht : e.outcome ≠ .unfinished)
    (hu : ¬ terminalUsed s e.operation) :
    WellFormed (⟨s.pending.filter (fun p => p.1 != e.operation),
      s.log ++ [e]⟩ : State Key) := by
  constructor
  · change ((s.pending.filter (fun p => p.1 != e.operation)).map Prod.fst).Nodup
    simpa only [List.filter_map, Function.comp_def] using
      hs.pending_ids.filter (fun id => id != e.operation)
  · simp only [List.map_append, List.map_cons, List.map_nil, List.nodup_append]
    refine ⟨hs.terminal_ids, by simp, ?_⟩
    intro a ha b hb
    simp only [List.mem_singleton] at hb
    subst b
    intro h
    obtain ⟨old, hold, ho⟩ := List.mem_map.mp ha
    exact hu ⟨old, hold, ho.trans h⟩
  · intro p hp a ha
    have hpm := (List.mem_filter.mp hp).1
    have hpn : p.1 ≠ e.operation := by simpa using (List.mem_filter.mp hp).2
    rcases List.mem_append.mp ha with ha | ha
    · exact hs.disjoint p hpm a ha
    · simpa only [List.mem_singleton.mp ha] using hpn
  · intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact hs.terminal a ha
    · simpa only [List.mem_singleton.mp ha] using ht

theorem step_wellFormed {s t : State Key} (hs : WellFormed s)
    {c : Command Key} (h : step s c = some t) : WellFormed t := by
  cases c with
  | begin id key =>
      simp only [step] at h
      split at h
      · split at h
        · cases Option.some.inj h
          exact hs
        · simp at h
      · rename_i hu
        split at h
        · split at h
          · cases Option.some.inj h
            exact hs
          · simp at h
        · rename_i hp
          cases Option.some.inj h
          exact fresh_begin_wellFormed hs id key hu hp
  | finish e =>
      obtain ⟨ht, h | h⟩ := finish_effect h
      · exact h.1 ▸ hs
      · rcases h with ⟨hu, _, rfl⟩
        exact fresh_finish_wellFormed hs e ht hu

theorem runFrom_wellFormed {s t : State Key} (hs : WellFormed s)
    {cs : List (Command Key)} (h : runFrom s cs = some t) : WellFormed t := by
  induction cs generalizing s with
  | nil =>
      cases Option.some.inj h
      exact hs
  | cons c cs ih =>
      simp only [runFrom, Option.bind_eq_some_iff] at h
      obtain ⟨u, hu, hrest⟩ := h
      exact ih (step_wellFormed hs hu) hrest

theorem run_wellFormed {cs : List (Command Key)} {s : State Key}
    (h : run cs = some s) : WellFormed s :=
  runFrom_wellFormed initial_wellFormed h

omit [DecidableEq Key] in
theorem terminal_identity_unique {s : State Key} (hs : WellFormed s)
    {a b : Event Key} (ha : a ∈ s.log) (hb : b ∈ s.log)
    (hid : a.operation = b.operation) : a = b :=
  List.inj_on_of_nodup_map hs.terminal_ids ha hb hid

omit [DecidableEq Key] in
theorem pending_identity_unique {s : State Key} (hs : WellFormed s)
    {a b : Nat × Key} (ha : a ∈ s.pending) (hb : b ∈ s.pending)
    (hid : a.1 = b.1) : a = b :=
  List.inj_on_of_nodup_map hs.pending_ids ha hb hid

theorem accepted_terminal_mem {s t : State Key} {e : Event Key}
    (h : step s (.finish e) = some t) : e ∈ t.log :=
  accepted_mem (finish_record h)

theorem accepted_terminal_replay {s t : State Key} {e : Event Key}
    (h : step s (.finish e) = some t) : step t (.finish e) = some t :=
  exact_terminal_replay t e (finish_effect h).1 (accepted_terminal_mem h)

theorem accepted_terminal_clears_pending {s t : State Key} (hs : WellFormed s)
    {e : Event Key} (h : step s (.finish e) = some t) :
    ¬ pendingUsed t e.operation := by
  intro hp
  obtain ⟨p, hpm, hid⟩ := hp
  exact (step_wellFormed hs h).disjoint p hpm e (accepted_terminal_mem h) hid

theorem finish_preserves_other_pending {s t : State Key} {e : Event Key}
    (h : step s (.finish e) = some t) (p : Nat × Key) (hid : p.1 ≠ e.operation) :
    p ∈ t.pending ↔ p ∈ s.pending := by
  obtain ⟨_, h | h⟩ := finish_effect h
  · rw [h.1]
  · rcases h with ⟨_, _, rfl⟩
    simp [hid]

theorem changed_terminal_key_rejected {s : State Key} (hs : WellFormed s)
    {old e : Event Key} (hold : old ∈ s.log) (hid : old.operation = e.operation)
    (hk : old.key ≠ e.key) : step s (.finish e) = none := by
  apply changed_terminal_rejected
  · intro he
    exact hk (congrArg Event.key (terminal_identity_unique hs hold he hid))
  · exact ⟨old, hold, hid⟩

theorem changed_terminal_outcome_rejected {s : State Key} (hs : WellFormed s)
    {old e : Event Key} (hold : old ∈ s.log) (hid : old.operation = e.operation)
    (ho : old.outcome ≠ e.outcome) : step s (.finish e) = none := by
  apply changed_terminal_rejected
  · intro he
    exact ho (congrArg Event.outcome (terminal_identity_unique hs hold he hid))
  · exact ⟨old, hold, hid⟩

theorem changed_pending_key_rejected {s : State Key} (hs : WellFormed s)
    {id : Nat} {oldKey key : Key} (hp : (id, oldKey) ∈ s.pending)
    (hk : oldKey ≠ key) : step s (.begin id key) = none := by
  have hu : ¬ terminalUsed s id := by
    rintro ⟨e, he, hid⟩
    exact hs.disjoint (id, oldKey) hp e he hid.symm
  have hpu : pendingUsed s id := ⟨(id, oldKey), hp, rfl⟩
  have hnew : (id, key) ∉ s.pending := by
    intro hn
    exact hk (congrArg Prod.snd (pending_identity_unique hs hp hn rfl))
  simp [step, hu, hpu, hnew]

theorem changed_late_begin_key_rejected {s : State Key} (hs : WellFormed s)
    {e : Event Key} (he : e ∈ s.log) {key : Key} (hk : e.key ≠ key) :
    step s (.begin e.operation key) = none := by
  have hu : terminalUsed s e.operation := ⟨e, he, rfl⟩
  have hnew : ¬ ∃ a ∈ s.log, a.operation = e.operation ∧ a.key = key := by
    rintro ⟨a, ha, hid, hkey⟩
    exact hk ((congrArg Event.key (terminal_identity_unique hs he ha hid.symm)).trans hkey)
  simp [step, hu, hnew]

theorem finish_log_effect {s t : State Key} {e : Event Key}
    (h : step s (.finish e) = some t) :
    t.log = if e ∈ s.log then s.log else s.log ++ [e] := by
  obtain ⟨_, h | h⟩ := finish_effect h
  · rw [h.1, ite_eq_left h.2]
  · rcases h with ⟨hu, _, rfl⟩
    have hn : e ∉ s.log := fun hm => hu ⟨e, hm, rfl⟩
    simp [hn]

theorem fresh_success_observed_once {s t : State Key} {id : Nat} {key : Key}
    (h : step s (.finish ⟨id, key, .success⟩) = some t)
    (hu : ¬ terminalUsed s id) :
    samples key t.log = samples key s.log ++ [true] := by
  rw [finish_log_effect h]
  have hn : (⟨id, key, .success⟩ : Event Key) ∉ s.log := fun hm => hu ⟨_, hm, rfl⟩
  rw [ite_eq_right hn]
  exact success_observation _ _ _

theorem fresh_rejection_observed_once {s t : State Key} {id : Nat} {key : Key}
    (h : step s (.finish ⟨id, key, .rejection⟩) = some t)
    (hu : ¬ terminalUsed s id) :
    samples key t.log = samples key s.log ++ [false] := by
  rw [finish_log_effect h]
  have hn : (⟨id, key, .rejection⟩ : Event Key) ∉ s.log := fun hm => hu ⟨_, hm, rfl⟩
  rw [ite_eq_right hn]
  exact rejection_observation _ _ _

theorem fault_preserves_samples {s t : State Key} {id : Nat} {key : Key}
    (h : step s (.finish ⟨id, key, .fault⟩) = some t) (target : Key) :
    samples target t.log = samples target s.log := by
  rw [finish_log_effect h]
  split
  · rfl
  · exact fault_not_observation _ _ _ _

theorem different_key_preserves_samples {s t : State Key} {e : Event Key}
    (h : step s (.finish e) = some t) (target : Key) (hk : e.key ≠ target) :
    samples target t.log = samples target s.log := by
  rw [finish_log_effect h]
  split
  · rfl
  · exact different_identity_no_observation _ _ _ hk

/-- The old log's unfinished marker permanently occupies the id, explaining why
pending intent is stored separately from the terminal calibration log. -/
theorem inherited_unfinished_terminal_conflict (id : Nat) (key : Key)
    (outcome : Outcome) (ht : outcome ≠ .unfinished) :
    record [⟨id, key, .unfinished⟩] ⟨id, key, outcome⟩ = none := by
  apply conflicting_replay
  · simpa using ht
  · exact ⟨⟨id, key, .unfinished⟩, by simp, rfl⟩

theorem step_log_prefix {s t : State Key} {c : Command Key}
    (h : step s c = some t) : s.log <+: t.log := by
  cases c with
  | begin id key =>
      rw [begin_log_unchanged h]
      exact List.prefix_refl _
  | finish e =>
      rw [finish_log_effect h]
      split
      · exact List.prefix_refl _
      · exact List.prefix_append _ _

theorem runFrom_log_prefix {s t : State Key} {cs : List (Command Key)}
    (h : runFrom s cs = some t) : s.log <+: t.log := by
  induction cs generalizing s with
  | nil =>
      cases Option.some.inj h
      exact List.prefix_refl _
  | cons c cs ih =>
      simp only [runFrom, Option.bind_eq_some_iff] at h
      obtain ⟨u, hu, hrest⟩ := h
      exact (step_log_prefix hu).trans (ih hrest)

theorem accepted_terminal_occurs_once {s t : State Key} (hs : WellFormed s)
    {e : Event Key} (h : step s (.finish e) = some t) :
    (t.log.map Event.operation).count e.operation = 1 := by
  apply (step_wellFormed hs h).terminal_ids.count_of_mem
  exact List.mem_map.mpr ⟨e, accepted_terminal_mem h, rfl⟩

theorem accepted_terminal_retained_once {s t u : State Key} (hs : WellFormed s)
    {e : Event Key} {cs : List (Command Key)}
    (hf : step s (.finish e) = some t) (hr : runFrom t cs = some u) :
    e ∈ u.log ∧ (u.log.map Event.operation).count e.operation = 1 := by
  have hm : e ∈ u.log := (runFrom_log_prefix hr).subset (accepted_terminal_mem hf)
  refine ⟨hm, ?_⟩
  apply (runFrom_wellFormed (step_wellFormed hs hf) hr).terminal_ids.count_of_mem
  exact List.mem_map.mpr ⟨e, hm, rfl⟩

end Komorebi.AVOC.ObservationRecorder
