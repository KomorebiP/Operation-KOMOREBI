import ProofPath.Extension
import Mathlib.Data.List.Basic

/-!
An executable finite trace checker refining the existing Field semantics.
Node identifiers are natural-number slots. Rule identifiers are list positions,
so even identical rule rows remain distinct addresses. Out-of-range addresses
are rejected rather than interpreted by the default row of the total Field.
-/
namespace ProofPath.Trace

structure Rule where
  premises : List Nat
  conclusion : Nat
  deriving DecidableEq, Repr

structure Problem where
  nodeCount : Nat
  leaves : List Nat
  rules : List Rule
  positive : List Nat
  negative : List Nat
  deriving DecidableEq, Repr

structure Witness where
  target : Nat
  trace : List Nat
  deriving DecidableEq, Repr

structure Certificate where
  feasible : Bool
  closure : List Nat
  trace : List Nat
  obstruction : Option Witness
  deriving DecidableEq, Repr

/-- Total finite lookup with an explicit failure value. -/
def lookup {α : Type*} : List α → Nat → Option α
  | [], _ => none
  | x :: _, 0 => some x
  | _ :: xs, i+1 => lookup xs i

theorem lookup_mem {α : Type*} {xs : List α} {i : Nat} {a : α}
    (h : lookup xs i = some a) : a ∈ xs := by
  induction xs generalizing i with
  | nil => simp [lookup] at h
  | cons x xs ih =>
    cases i with
    | zero => simp [lookup] at h; simp [h]
    | succ i => exact List.mem_cons_of_mem _ (ih h)

theorem mem_lookup {α : Type*} {xs : List α} {a : α} (h : a ∈ xs) :
    ∃ i, lookup xs i = some a := by
  induction xs with
  | nil => simp at h
  | cons x xs ih =>
    rcases List.mem_cons.mp h with h | h
    · exact ⟨0, by simp [lookup, h]⟩
    · obtain ⟨i, hi⟩ := ih h
      exact ⟨i+1, hi⟩

def Problem.initial (p : Problem) : List Nat := p.leaves ++ p.positive

def Problem.field (p : Problem) : Field Nat Nat where
  leaf := {v | v ∈ p.leaves}
  premises j := {v | v ∈ ((lookup p.rules j).getD ⟨[], 0⟩).premises}
  conclusion j := ((lookup p.rules j).getD ⟨[], 0⟩).conclusion
  certified j := (lookup p.rules j).isSome = true

def Problem.seeds (p : Problem) : Set Nat := {v | v ∈ p.positive}
def Problem.forbidden (p : Problem) : Set Nat := {v | v ∈ p.negative}
def Problem.exactClosure (p : Problem) : Set Nat := p.field.closure p.seeds

def enabled (r : Rule) (known : List Nat) : Bool :=
  r.premises.all (fun v => known.contains v)

theorem enabled_iff (r : Rule) (known : List Nat) :
    enabled r known = true ↔ ∀ v, v ∈ r.premises → v ∈ known := by
  simp [enabled]

/-- Repeated conclusions are allowed for a causal witness, but not for a
strict complete-closure trace. The two modes have the same logical meaning. -/
def replay (p : Problem) (strict : Bool) : List Nat → List Nat → Option (List Nat)
  | known, [] => some known
  | known, j :: js =>
    match lookup p.rules j with
    | none => none
    | some r =>
      if enabled r known && (!strict || !(known.contains r.conclusion)) then
        replay p strict (r.conclusion :: known) js
      else none

theorem initial_sound (p : Problem) :
    ∀ v, v ∈ p.initial → v ∈ p.exactClosure := by
  intro v hv
  rcases List.mem_append.mp hv with hv | hv
  · exact Field.Derives.leaf (Or.inl hv)
  · exact p.field.closure_contains_seed p.seeds hv

theorem rule_sound (p : Problem) {known : List Nat} {j : Nat} {r : Rule}
    (hj : lookup p.rules j = some r) (he : enabled r known = true)
    (hk : ∀ v, v ∈ known → v ∈ p.exactClosure) :
    r.conclusion ∈ p.exactClosure := by
  have hp := (enabled_iff r known).mp he
  have hc : (p.field.seeded p.seeds).Derives (p.field.conclusion j) := by
    apply Field.Derives.step j
    · simp [Problem.field, Field.seeded, hj]
    · intro v hv
      apply hk v
      apply hp v
      simpa [Problem.field, Field.seeded, hj] using hv
  simpa [Problem.exactClosure, Field.closure, Problem.field, hj] using hc

/-- No execution step can insert a node without a declared derivation. -/
theorem replay_sound (p : Problem) (strict : Bool) {known trace out : List Nat}
    (hk : ∀ v, v ∈ known → v ∈ p.exactClosure)
    (h : replay p strict known trace = some out) :
    ∀ v, v ∈ out → v ∈ p.exactClosure := by
  induction trace generalizing known with
  | nil =>
    have he : known = out := Option.some.inj h
    simpa [← he] using hk
  | cons j js ih =>
    cases hj : lookup p.rules j with
    | none => simp [replay, hj] at h
    | some r =>
      simp only [replay, hj] at h
      split at h
      next ha =>
        have he := (Bool.and_eq_true_iff.mp ha).1
        apply ih ?_ h
        intro v hv
        rcases List.mem_cons.mp hv with hv | hv
        · subst v
          exact rule_sound p hj he hk
        · exact hk v hv
      next => simp at h

/-- Replay preserves every initially known node. -/
theorem replay_extensive (p : Problem) (strict : Bool) {known trace out : List Nat}
    (h : replay p strict known trace = some out) :
    ∀ v, v ∈ known → v ∈ out := by
  induction trace generalizing known with
  | nil =>
    have he : known = out := Option.some.inj h
    exact fun v hv => he ▸ hv
  | cons j js ih =>
    cases hj : lookup p.rules j with
    | none => simp [replay, hj] at h
    | some r =>
      simp only [replay, hj] at h
      split at h
      next => exact fun v hv => ih h v (List.mem_cons_of_mem _ hv)
      next => simp at h

/-- Execution composes by concatenation, including explicit failure propagation. -/
theorem replay_append (p : Problem) (strict : Bool) (known left right : List Nat) :
    replay p strict known (left ++ right) =
      (replay p strict known left).bind (fun middle => replay p strict middle right) := by
  induction left generalizing known with
  | nil => rfl
  | cons j js ih =>
    cases hj : lookup p.rules j with
    | none => simp [replay, hj]
    | some r =>
      simp only [List.cons_append, replay, hj]
      split
      · exact ih _
      · rfl

/-- A list-coded model predicate, with all rule rows checked. -/
def closed (p : Problem) (known : List Nat) : Bool :=
  p.leaves.all (fun v => known.contains v) &&
    p.rules.all (fun r => !enabled r known || known.contains r.conclusion)

theorem closed_iff_model (p : Problem) (known : List Nat) :
    closed p known = true ↔ p.field.Model (fun v => v ∈ known) := by
  constructor
  · intro h
    have hl := (Bool.and_eq_true_iff.mp h).1
    have hr := (Bool.and_eq_true_iff.mp h).2
    constructor
    · intro v hv
      exact (List.all_eq_true.mp hl v hv) |> (by simpa using ·)
    · intro j hj hp
      cases he : lookup p.rules j with
      | none => simp [Problem.field, he] at hj
      | some r =>
        have hm := lookup_mem he
        have hh := List.all_eq_true.mp hr r hm
        have en : enabled r known = true := by
          apply (enabled_iff r known).mpr
          intro v hv
          apply hp v
          simpa [Problem.field, he] using hv
        have hc : r.conclusion ∈ known := by simpa [en] using hh
        simpa [Problem.field, he] using hc
  · rintro ⟨hl, hr⟩
    apply Bool.and_eq_true_iff.mpr
    constructor
    · apply List.all_eq_true.mpr
      intro v hv
      simpa using hl v hv
    · apply List.all_eq_true.mpr
      intro r hm
      by_cases he : enabled r known = true
      · obtain ⟨j, hj⟩ := mem_lookup hm
        have hc : p.field.certified j := by simp [Problem.field, hj]
        have hp : ∀ v, v ∈ p.field.premises j → v ∈ known := by
          intro v hv
          apply (enabled_iff r known).mp he v
          simpa [Problem.field, hj] using hv
        have hh := hr j hc hp
        simpa [Problem.field, hj, he] using hh
      · simp [he]

def sameMembers (a b : List Nat) : Bool :=
  a.all (fun v => b.contains v) && b.all (fun v => a.contains v)

theorem sameMembers_iff (a b : List Nat) :
    sameMembers a b = true ↔ ∀ v, v ∈ a ↔ v ∈ b := by
  simp only [sameMembers, Bool.and_eq_true, List.all_eq_true, List.contains_iff_mem]
  constructor
  · rintro ⟨hab, hba⟩ v
    exact ⟨hab v, hba v⟩
  · intro h
    exact ⟨fun v => (h v).mp, fun v => (h v).mpr⟩

/-- Complete replay plus a model check establishes equality with the least closure. -/
def checkClosure (p : Problem) (trace known : List Nat) : Bool :=
  match replay p true p.initial trace with
  | none => false
  | some out => sameMembers out known && closed p known

theorem checkClosure_exact (p : Problem) (trace known : List Nat)
    (h : checkClosure p trace known = true) :
    ∀ v, v ∈ known ↔ v ∈ p.exactClosure := by
  cases he : replay p true p.initial trace with
  | none => simp [checkClosure, he] at h
  | some out =>
    have hh : sameMembers out known = true ∧ closed p known = true := by
      simpa [checkClosure, he] using h
    have hm := (sameMembers_iff out known).mp hh.1
    have hs := replay_sound p true (initial_sound p) he
    have hi := replay_extensive p true he
    have hmodel := (closed_iff_model p known).mp hh.2
    have seed : ∀ v, v ∈ p.seeds → v ∈ known := by
      intro v hv
      exact (hm v).mp (hi v (List.mem_append_right _ hv))
    exact fun v => ⟨fun hv => hs v ((hm v).mpr hv),
      p.field.closure_le_model p.seeds hmodel seed v⟩

def checkWitness (p : Problem) (w : Witness) : Bool :=
  match replay p false p.initial w.trace with
  | none => false
  | some out => out.contains w.target && p.negative.contains w.target

theorem checkWitness_sound (p : Problem) (w : Witness)
    (h : checkWitness p w = true) :
    w.target ∈ p.forbidden ∧ w.target ∈ p.exactClosure := by
  cases he : replay p false p.initial w.trace with
  | none => simp [checkWitness, he] at h
  | some out =>
    have hh : w.target ∈ out ∧ w.target ∈ p.negative := by
      simpa [checkWitness, he] using h
    exact ⟨hh.2, replay_sound p false (initial_sound p) he _ hh.1⟩

theorem checkWitness_refutes (p : Problem) (w : Witness)
    (h : checkWitness p w = true) :
    ¬ ∃ x, p.field.Extends p.seeds p.forbidden x := by
  apply (p.field.infeasible_iff_forbidden_derivation p.seeds p.forbidden).mpr
  exact ⟨w.target, checkWitness_sound p w h⟩

/-- Complete positive and negative result verification. Both require the full
least-closure certificate; a bare negative witness has its own checker. -/
def checkCertificate (p : Problem) (c : Certificate) : Bool :=
  checkClosure p c.trace c.closure &&
    if c.feasible then
      c.obstruction.isNone && !(c.closure.any (fun v => p.negative.contains v))
    else
      match c.obstruction with
      | none => false
      | some w => checkWitness p w

theorem certificate_closure (p : Problem) (c : Certificate)
    (h : checkCertificate p c = true) :
    ∀ v, v ∈ c.closure ↔ v ∈ p.exactClosure :=
  checkClosure_exact p c.trace c.closure (Bool.and_eq_true_iff.mp h).1

theorem certificate_positive (p : Problem) (c : Certificate)
    (h : checkCertificate p c = true) (hf : c.feasible = true) :
    p.field.Extends p.seeds p.forbidden (fun v => v ∈ c.closure) := by
  have he := certificate_closure p c h
  have branch := (Bool.and_eq_true_iff.mp h).2
  have hn : ∀ v, v ∈ c.closure → v ∉ p.negative := by
    have hh : c.obstruction = none ∧ (∀ v, v ∈ c.closure → v ∉ p.negative) := by
      simpa [hf] using branch
    exact hh.2
  refine ⟨?_, ?_, ?_⟩
  · constructor
    · intro v hv
      apply (he v).mpr
      exact Field.Derives.leaf (Or.inl hv)
    · intro j hj hp
      apply (he _).mpr
      exact Field.Derives.step j hj (fun v hv => (he v).mp (hp v hv))
  · exact fun v hv => (he v).mpr (p.field.closure_contains_seed p.seeds hv)
  · exact fun v hv hc => hn v hc hv

theorem certificate_negative (p : Problem) (c : Certificate)
    (h : checkCertificate p c = true) (hf : c.feasible = false) :
    ¬ ∃ x, p.field.Extends p.seeds p.forbidden x := by
  have branch := (Bool.and_eq_true_iff.mp h).2
  cases hw : c.obstruction with
  | none => simp [hf, hw] at branch
  | some w =>
    apply checkWitness_refutes p w
    simpa [hf, hw] using branch

theorem certificate_decides_feasibility (p : Problem) (c : Certificate)
    (h : checkCertificate p c = true) :
    (c.feasible = true ↔ ∃ x, p.field.Extends p.seeds p.forbidden x) := by
  constructor
  · exact fun hf => ⟨_, certificate_positive p c h hf⟩
  · intro hx
    cases hf : c.feasible with
    | true => rfl
    | false => exact False.elim (certificate_negative p c h hf hx)

/-- Semantic validity remains conditional on an interpretation and true seeds. -/
theorem accepted_meaning (p : Problem) (c : Certificate)
    (h : checkCertificate p c = true) (meaning : Nat → Prop)
    (hm : p.field.Model meaning) (hs : ∀ v, v ∈ p.seeds → meaning v)
    {v : Nat} (hv : v ∈ c.closure) : meaning v :=
  p.field.closure_le_model p.seeds hm hs v ((certificate_closure p c h v).mp hv)

end ProofPath.Trace
