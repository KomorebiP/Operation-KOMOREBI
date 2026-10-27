import Mathlib.Data.List.Basic
import Mathlib.Data.List.Nodup

/-!
# Finite counterexample-guided synthesis

Reviewed Core 6.1. Programs remain their original syntax values. The teacher checks
one fixed complete ordered context list. Retained counterexamples are persistent.
The implementation scans candidates once; a prefix invariant below justifies that
this is the earliest-consistent learner, not a different search convention.
No returned result represents interruption of host execution.
-/

namespace Komorebi.MachineTheory.Synthesis

universe u v w

structure Task (P : Type u) (D : Type v) (Y : Type w) where
  eval : P → D → Y
  target : D → Y
  contexts : List D
  complete : ∀ x, x ∈ contexts

variable {P : Type u} {D : Type v} {Y : Type w} [DecidableEq Y]

/-- A literal short-circuit scan: first disagreement and number of comparisons. -/
def inspect (T : Task P D Y) (p : P) : List D → Option D × Nat
  | [] => (none, 0)
  | x :: xs =>
    if T.eval p x = T.target x then
      let r := inspect T p xs
      (r.1, r.2 + 1)
    else (some x, 1)

def Correct (T : Task P D Y) (p : P) : Prop := ∀ x, T.eval p x = T.target x

def Refuted (T : Task P D Y) (E : List D) (p : P) : Prop :=
  ∃ x ∈ E, T.eval p x ≠ T.target x

def Consistent (T : Task P D Y) (E : List D) (p : P) : Prop :=
  ∀ x ∈ E, T.eval p x = T.target x

@[simp] theorem inspect_none_iff (T : Task P D Y) (p : P) (E : List D) :
    (inspect T p E).1 = none ↔ Consistent T E p := by
  induction E with
  | nil => simp [inspect, Consistent]
  | cons x xs ih =>
    by_cases hx : T.eval p x = T.target x
    · simp [inspect, hx, Consistent, ih, Consistent] at *
    · simp [inspect, hx, Consistent]

theorem inspect_some (T : Task P D Y) (p : P) (E : List D) (x : D)
    (h : (inspect T p E).1 = some x) : x ∈ E ∧ T.eval p x ≠ T.target x := by
  induction E with
  | nil => simp [inspect] at h
  | cons y ys ih =>
    by_cases hy : T.eval p y = T.target y
    · simp only [inspect, hy, ↓reduceIte] at h
      exact ⟨List.mem_cons_of_mem y (ih h).1, (ih h).2⟩
    · simp only [inspect, hy, ↓reduceIte, Option.some.injEq] at h
      subst x
      exact ⟨List.mem_cons_self, hy⟩

theorem inspect_none_of_correct (T : Task P D Y) {p : P} (h : Correct T p)
    (E : List D) : (inspect T p E).1 = none := by
  apply (inspect_none_iff T p E).2
  intro x _
  exact h x

theorem refuted_iff_inspect_ne_none (T : Task P D Y) (E : List D) (p : P) :
    Refuted T E p ↔ (inspect T p E).1 ≠ none := by
  classical
  simp only [ne_eq, inspect_none_iff, Consistent, Refuted]
  push Not
  rfl

/-- The actual deterministic, extensional, complete finite teacher. -/
def teacher (T : Task P D Y) (p : P) : Option D := (inspect T p T.contexts).1

@[simp] theorem teacher_accepts_iff (T : Task P D Y) (p : P) :
    teacher T p = none ↔ Correct T p := by
  rw [teacher, inspect_none_iff]
  exact ⟨fun h x => h x (T.complete x), fun h x _ => h x⟩

theorem teacher_refutes (T : Task P D Y) {p : P} {x : D}
    (h : teacher T p = some x) : T.eval p x ≠ T.target x :=
  (inspect_some T p T.contexts x h).2

/-- The fixed teacher's rejection is the first disagreement in its context order. -/
theorem inspect_first (T : Task P D Y) (p : P) (E : List D) :
    (inspect T p E).1 = E.find? (fun x => decide (T.eval p x ≠ T.target x)) := by
  induction E with
  | nil => rfl
  | cons x xs ih =>
    by_cases hx : T.eval p x = T.target x
    · simp [inspect, hx, ih]
    · simp [inspect, hx]

theorem inspect_comparisons_le (T : Task P D Y) (p : P) (E : List D) :
    (inspect T p E).2 ≤ E.length := by
  induction E with
  | nil => simp [inspect]
  | cons x xs ih =>
    by_cases hx : T.eval p x = T.target x
    · simp only [inspect, hx, ↓reduceIte, List.length_cons]
      omega
    · simp [inspect, hx]

structure Result (P : Type u) (D : Type v) where
  answer : Option P
  transcript : List (P × Option D)
  retained : List D
  comparisons : Nat
  visits : Nat
  deriving Repr, DecidableEq

/-- Candidate scan. Rejected examples are prepended, defining a fixed test order. -/
def scan (T : Task P D Y) : List P → List D → Result P D
  | [], E => ⟨none, [], E, 0, 0⟩
  | p :: ps, E =>
    let c := inspect T p E
    match c.1 with
    | some _ =>
      let r := scan T ps E
      ⟨r.answer, r.transcript, r.retained, c.2 + r.comparisons, 1 + r.visits⟩
    | none =>
      match teacher T p with
      | none => ⟨some p, [(p, none)], E, c.2, 1⟩
      | some x =>
        let r := scan T ps (x :: E)
        ⟨r.answer, (p, some x) :: r.transcript, r.retained,
          c.2 + r.comparisons, 1 + r.visits⟩

/-- Result semantics exclude only the separately metered search costs. -/
def SameEvidence (r s : Result P D) : Prop :=
  r.answer = s.answer ∧ r.transcript = s.transcript ∧ r.retained = s.retained

/-- No accepted candidate is replaced by a different but equivalent syntax. -/
theorem scan_answer (T : Task P D Y) (G : List P) (E : List D) :
    (scan T G E).answer = G.find? (fun p => (teacher T p).isNone) := by
  induction G generalizing E with
  | nil => rfl
  | cons p ps ih =>
    cases hc : (inspect T p E).1 with
    | some x =>
      have hn : teacher T p ≠ none := by
        intro ht
        have hp := (teacher_accepts_iff T p).mp ht
        have hi := inspect_none_of_correct T hp E
        rw [hc] at hi
        contradiction
      cases ht : teacher T p with
      | none => exact False.elim (hn ht)
      | some y => simp [scan, hc, ht, ih]
    | none =>
      cases ht : teacher T p with
      | none => simp [scan, hc, ht]
      | some x => simp [scan, hc, ht, ih]

/-- A complete scan exhausts exactly when no program in its grammar is correct. -/
theorem exhaustion_iff (T : Task P D Y) (G : List P) (E : List D) :
    (scan T G E).answer = none ↔ ∀ p ∈ G, ¬ Correct T p := by
  rw [scan_answer, List.find?_eq_none]
  simp only [Option.isNone_iff_eq_none, teacher_accepts_iff]

/-- The accepted syntax is the earliest globally correct grammar entry. -/
theorem accepted_first (T : Task P D Y) (G : List P) (E : List D) {p : P}
    (hp : (scan T G E).answer = some p) :
    ∃ before after, G = before ++ p :: after ∧ Correct T p ∧
      ∀ q ∈ before, ¬ Correct T q := by
  rw [scan_answer, List.find?_eq_some_iff_append] at hp
  rcases hp with ⟨ht, before, after, h, hbefore⟩
  refine ⟨before, after, h, ?_, ?_⟩
  · exact (teacher_accepts_iff T p).mp (Option.isNone_iff_eq_none.mp ht)
  · intro q hq hgood
    have he := (teacher_accepts_iff T q).mpr hgood
    have hn := hbefore q hq
    simp [he] at hn

/-- The teacher transcript follows the original candidate order without re-entry. -/
theorem transcript_sublist (T : Task P D Y) (G : List P) (E : List D) :
    ((scan T G E).transcript.map Prod.fst).Sublist G := by
  induction G generalizing E with
  | nil => exact List.Sublist.refl []
  | cons p ps ih =>
    cases hc : (inspect T p E).1 with
    | some x => simpa [scan, hc] using (ih E).cons p
    | none =>
      cases ht : teacher T p with
      | none => simp [scan, hc, ht]
      | some x => simpa [scan, hc, ht] using (ih (x :: E)).cons_cons p

/-- Core 6.1's bound counts actual teacher calls, including final acceptance. -/
theorem teacher_calls_le (T : Task P D Y) (G : List P) (E : List D) :
    (scan T G E).transcript.length ≤ G.length := by
  simpa using (transcript_sublist T G E).length_le

/-- No repeated submission in a grammar of distinct syntax objects. -/
theorem submitted_nodup (T : Task P D Y) (G : List P) (hG : G.Nodup) (E : List D) :
    ((scan T G E).transcript.map Prod.fst).Nodup :=
  hG.sublist (transcript_sublist T G E)

/-- Every logged rejection is a real counterexample for the submitted AST. -/
theorem transcript_rejections (T : Task P D Y) (G : List P) (E : List D) :
    ∀ p x, (p, some x) ∈ (scan T G E).transcript → T.eval p x ≠ T.target x := by
  induction G generalizing E with
  | nil => simp [scan]
  | cons p ps ih =>
    cases hc : (inspect T p E).1 with
    | some x => simpa [scan, hc] using ih E
    | none =>
      cases ht : teacher T p with
      | none => simp [scan, hc, ht]
      | some x =>
        intro q y hy
        simp only [scan, hc, ht, List.mem_cons, Prod.mk.injEq, Option.some.injEq] at hy
        rcases hy with ⟨rfl, rfl⟩ | hy
        · exact teacher_refutes T ht
        · exact ih (x :: E) q y hy

/-- Old evidence remains available; a short scan cannot erase a constraint. -/
theorem retained_persistent (T : Task P D Y) (G : List P) (E : List D) :
    ∀ x ∈ E, x ∈ (scan T G E).retained := by
  induction G generalizing E with
  | nil => simp [scan]
  | cons p ps ih =>
    cases hc : (inspect T p E).1 with
    | some x => simpa [scan, hc] using ih E
    | none =>
      cases ht : teacher T p with
      | none => simp [scan, hc, ht]
      | some x =>
        intro y hy
        simpa [scan, hc, ht] using ih (x :: E) y (List.mem_cons_of_mem x hy)

/-- One explicit source-facing contract bundles termination outcomes and call bound. -/
theorem finite_synthesis (T : Task P D Y) (G : List P) (E : List D) :
    (scan T G E).transcript.length ≤ G.length ∧
    ((scan T G E).answer = none ↔ ∀ p ∈ G, ¬ Correct T p) ∧
    (∀ p, (scan T G E).answer = some p →
      ∃ before after, G = before ++ p :: after ∧ Correct T p ∧
        ∀ q ∈ before, ¬ Correct T q) := by
  exact ⟨teacher_calls_le T G E, exhaustion_iff T G E, fun _ hp => accepted_first T G E hp⟩

end Komorebi.MachineTheory.Synthesis
