import MachineTheory.SynthesisTrace

/-!
# Explicit suspension is not acceptance or exhaustion

Fuel bounds candidate inspections, not CPU instructions, teacher calls, or the
cost of a candidate evaluation. Suspensions retain the pending ordered grammar,
all counterexamples, the actual transcript and accumulated comparison counters.
Resumption has the same result as an uninterrupted scan.
-/

namespace Komorebi.MachineTheory.Synthesis

universe u v w
variable {P : Type u} {D : Type v} {Y : Type w} [DecidableEq Y]

structure Suspension (P : Type u) (D : Type v) where
  pending : List P
  retained : List D
  transcript : List (P × Option D)
  comparisons : Nat
  visits : Nat
  deriving Repr, DecidableEq

inductive Progress (P : Type u) (D : Type v) where
  | complete : Result P D → Progress P D
  | suspended : Suspension P D → Progress P D
  deriving Repr, DecidableEq

def prependWork (cost : Nat) : Progress P D → Progress P D
  | .complete r => .complete {r with comparisons := cost + r.comparisons, visits := 1 + r.visits}
  | .suspended s => .suspended {s with comparisons := cost + s.comparisons, visits := 1 + s.visits}

def prependCall (p : P) (x : D) (cost : Nat) : Progress P D → Progress P D
  | .complete r => .complete {r with transcript := (p, some x) :: r.transcript, comparisons := cost + r.comparisons, visits := 1 + r.visits}
  | .suspended s => .suspended {s with transcript := (p, some x) :: s.transcript, comparisons := cost + s.comparisons, visits := 1 + s.visits}

/-- No teacher is consulted when the candidate-inspection allowance is exhausted. -/
def boundedScan (T : Task P D Y) : Nat → List P → List D → Progress P D
  | _, [], E => .complete ⟨none, [], E, 0, 0⟩
  | 0, G, E => .suspended ⟨G, E, [], 0, 0⟩
  | n + 1, p :: ps, E =>
    let c := inspect T p E
    match c.1 with
    | some _ => prependWork c.2 (boundedScan T n ps E)
    | none =>
      match teacher T p with
      | none => .complete ⟨some p, [(p, none)], E, c.2, 1⟩
      | some x => prependCall p x c.2 (boundedScan T n ps (x :: E))

/-- Finish the stored pending computation, preserving the emitted prefix. -/
def resume (T : Task P D Y) : Progress P D → Result P D
  | .complete r => r
  | .suspended s =>
    let r := scan T s.pending s.retained
    ⟨r.answer, s.transcript ++ r.transcript, r.retained,
      s.comparisons + r.comparisons, s.visits + r.visits⟩

theorem resume_prependWork (T : Task P D Y) (c : Nat) (q : Progress P D) :
    resume T (prependWork c q) =
      {resume T q with comparisons := c + (resume T q).comparisons, visits := 1 + (resume T q).visits} := by
  cases q <;> simp [resume, prependWork, Nat.add_assoc]

theorem resume_prependCall (T : Task P D Y) (p : P) (x : D) (c : Nat) (q : Progress P D) :
    resume T (prependCall p x c q) =
      {resume T q with transcript := (p, some x) :: (resume T q).transcript, comparisons := c + (resume T q).comparisons, visits := 1 + (resume T q).visits} := by
  cases q <;> simp [resume, prependCall, Nat.add_assoc]

/-- Completed calls, counterexamples, answer and measured work all survive suspension. -/
theorem resume_bounded (T : Task P D Y) (n : Nat) (G : List P) (E : List D) :
    resume T (boundedScan T n G E) = scan T G E := by
  induction n generalizing G E with
  | zero =>
    cases G <;> simp [boundedScan, resume, scan]
  | succ n ih =>
    cases G with
    | nil => rfl
    | cons p ps =>
      cases hc : (inspect T p E).1 with
      | some x => simp [boundedScan, scan, hc, resume_prependWork, ih]
      | none =>
        cases ht : teacher T p with
        | none => simp [boundedScan, scan, hc, ht, resume]
        | some x => simp [boundedScan, scan, hc, ht, resume_prependCall, ih]

/-- A completion returned within a partial allowance is still the full exact result. -/
theorem bounded_completion_sound (T : Task P D Y) {n : Nat} {G : List P} {E : List D}
    {r : Result P D} (h : boundedScan T n G E = .complete r) : r = scan T G E := by
  have he := resume_bounded T n G E
  rw [h] at he
  exact he

/-- There is no assumption that one inspection has constant physical execution cost. -/
theorem enough_inspections (T : Task P D Y) (n : Nat) (G : List P) (E : List D)
    (h : G.length ≤ n) : boundedScan T n G E = .complete (scan T G E) := by
  induction n generalizing G E with
  | zero =>
    have hg : G = [] := by simpa using h
    subst G
    rfl
  | succ n ih =>
    cases G with
    | nil => rfl
    | cons p ps =>
      have htail : ps.length ≤ n := by simpa using h
      cases hc : (inspect T p E).1 with
      | some x => simp [boundedScan, scan, hc, ih ps E htail, prependWork]
      | none =>
        cases ht : teacher T p with
        | none => simp [boundedScan, scan, hc, ht]
        | some x => simp [boundedScan, scan, hc, ht, ih ps (x :: E) htail, prependCall]

end Komorebi.MachineTheory.Synthesis
