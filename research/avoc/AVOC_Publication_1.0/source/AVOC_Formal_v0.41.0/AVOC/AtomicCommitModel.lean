import AVOC.CommitRecovery

namespace Komorebi.AVOC.AtomicCommitModel

open LiveExecution PlannerRuntime CommitRecovery

/-- Abstract atomic storage object. Physical SQLite correspondence is tested,
not assumed to be proved by this data type. -/
structure Store (j : Job) where
  current : StoreView
  next : Nat
  pending : Option (Intent j)
  last : Option (Commit j)

def prepare (j : Job) (s : Store j) (i : Intent j) : Except String (Store j) :=
  if s.pending.isSome then .error "operation already pending"
  else if i.sequence ≠ s.next ∨ i.before ≠ s.current then .error "intent mismatch"
  else .ok { s with pending := some i }

/-- All three effects (new physical view, receipt, sequence advance) occur as
one abstract persistence step. No checker verdict is inferred from view equality. -/
def publish (j : Job) (s : Store j) (r : Commit j) : Except String (Store j) :=
  if s.pending ≠ some r.intent then .error "no matching durable intent"
  else if r.intent.sequence ≠ s.next ∨ r.intent.before ≠ s.current then
    .error "commit base mismatch"
  else .ok ⟨r.after, s.next + 1, none, some r⟩

theorem prepare_contract (j : Job) (s t : Store j) (i : Intent j)
    (h : prepare j s i = .ok t) :
    s.pending = none ∧ i.sequence = s.next ∧ i.before = s.current ∧
      t = { s with pending := some i } := by
  cases hp : s.pending with
  | some p => simp [prepare, hp] at h
  | none =>
      by_cases hi : i.sequence = s.next ∧ i.before = s.current
      · have ht : ({ s with pending := some i } : Store j) = t := by
          simpa [prepare, hp, hi.1, hi.2] using h
        exact ⟨rfl, hi.1, hi.2, ht.symm⟩
      · simp only [prepare, hp, Option.isSome_none, Bool.false_eq_true, ↓reduceIte] at h
        have hb : i.sequence ≠ s.next ∨ i.before ≠ s.current := by tauto
        simp [hb] at h

theorem prepare_does_not_commit (j : Job) (s t : Store j) (i : Intent j)
    (h : prepare j s i = .ok t) : t.current = s.current ∧ t.next = s.next := by
  obtain ⟨_, _, _, ht⟩ := prepare_contract j s t i h
  subst t
  exact ⟨rfl,rfl⟩

theorem publish_contract (j : Job) (s t : Store j) (r : Commit j)
    (h : publish j s r = .ok t) :
    s.pending = some r.intent ∧ r.intent.sequence = s.next ∧
      r.intent.before = s.current ∧ t = ⟨r.after, s.next + 1, none, some r⟩ := by
  by_cases hp : s.pending = some r.intent
  · by_cases hr : r.intent.sequence = s.next ∧ r.intent.before = s.current
    · have ht : (⟨r.after, s.next + 1, none, some r⟩ : Store j) = t := by
        simpa [publish, hp, hr.1, hr.2] using h
      exact ⟨hp, hr.1, hr.2, ht.symm⟩
    · have hb : r.intent.sequence ≠ s.next ∨ r.intent.before ≠ s.current := by tauto
      simp [publish, hp, hb] at h
  · simp [publish, hp] at h

theorem published_result_matches_state (j : Job) (s t : Store j) (r : Commit j)
    (h : publish j s r = .ok t) :
    t.current = r.after ∧ t.last = some r ∧ t.next = r.intent.sequence + 1 := by
  obtain ⟨_, hn, _, ht⟩ := publish_contract j s t r h
  subst t
  exact ⟨rfl, rfl, by rw [hn]⟩

theorem duplicate_publish_rejected (j : Job) (s t : Store j) (r : Commit j)
    (h : publish j s r = .ok t) :
    publish j t r = .error "no matching durable intent" := by
  obtain ⟨_, _, _, ht⟩ := publish_contract j s t r h
  subst t
  simp [publish]

theorem stale_intent_after_publish_rejected (j : Job) (s t : Store j) (r : Commit j)
    (h : publish j s r = .ok t) : prepare j t r.intent = .error "intent mismatch" := by
  obtain ⟨_, hn, _, ht⟩ := publish_contract j s t r h
  subst t
  have he : r.intent.sequence ≠ s.next + 1 := by omega
  simp [prepare, he]

/-- Even if an operation does not change the visible store projection, the
atomic commit sequence and receipt still change. A snapshot alone cannot track it. -/
theorem no_op_commit_still_advances (j : Job) (s t : Store j) (r : Commit j)
    (h : publish j s r = .ok t) (hv : r.after = s.current) :
    t.current = s.current ∧ t.next = s.next + 1 ∧ t.next ≠ s.next := by
  obtain ⟨_, _, _, ht⟩ := publish_contract j s t r h
  subst t
  exact ⟨hv,rfl,by change s.next + 1 ≠ s.next; omega⟩

/-- Pure recovery changes the logical checkpoint only; the committed storage
object is returned byte-for-byte in the abstract state model. -/
def reconcilePublished (j : Job) (store : Store j) (c : Checkpoint j)
    (r : Commit j) : Except String (Store j × Checkpoint j) :=
  if store.last ≠ some r ∨ store.next ≠ r.intent.sequence + 1 then
    .error "commit result is not the current durable record"
  else match acknowledge j c r store.current with
    | .error msg => .error msg
    | .ok d => .ok (store,d)

theorem reconcile_physical_unchanged (j : Job) (store out : Store j)
    (c d : Checkpoint j) (r : Commit j)
    (h : reconcilePublished j store c r = .ok (out,d)) : out = store := by
  by_cases hs : store.last ≠ some r ∨ store.next ≠ r.intent.sequence + 1
  · simp [reconcilePublished, hs] at h
  · cases ha : acknowledge j c r store.current with
    | error msg => simp [reconcilePublished, hs, ha] at h
    | ok e =>
        have he : (store,e) = (out,d) := by simpa [reconcilePublished, hs, ha] using h
        exact (congrArg Prod.fst he).symm

theorem reconcile_safe (j : Job) (store out : Store j) (c d : Checkpoint j)
    (r : Commit j) (hs : CommitRecovery.Safe j c)
    (h : reconcilePublished j store c r = .ok (out,d)) : CommitRecovery.Safe j d := by
  by_cases hb : store.last ≠ some r ∨ store.next ≠ r.intent.sequence + 1
  · simp [reconcilePublished, hb] at h
  · cases ha : acknowledge j c r store.current with
    | error msg => simp [reconcilePublished, hb, ha] at h
    | ok e =>
        have he : (store,e) = (out,d) := by simpa [reconcilePublished, hb, ha] using h
        have hd : e = d := congrArg Prod.snd he
        exact hd ▸ acknowledge_safe j c e r store.current hs ha

theorem reconcile_idempotent (j : Job) (store out : Store j)
    (c d : Checkpoint j) (r : Commit j)
    (h : reconcilePublished j store c r = .ok (out,d)) :
    reconcilePublished j store d r = .ok (store,d) := by
  by_cases hb : store.last ≠ some r ∨ store.next ≠ r.intent.sequence + 1
  · simp [reconcilePublished, hb] at h
  · cases ha : acknowledge j c r store.current with
    | error msg => simp [reconcilePublished, hb, ha] at h
    | ok e =>
        have he : (store,e) = (out,d) := by simpa [reconcilePublished, hb, ha] using h
        have hd : e = d := congrArg Prod.snd he
        subst d
        simp [reconcilePublished, hb, acknowledge_idempotent j c e r store.current ha]

end Komorebi.AVOC.AtomicCommitModel
