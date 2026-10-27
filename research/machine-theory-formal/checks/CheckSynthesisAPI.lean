import MachineTheory

open Komorebi.MachineTheory.Synthesis

universe u v w z
variable {P : Type u} {D : Type v} {Y : Type w} {K : Type z}
variable [DecidableEq Y] [DecidableEq K]

/-- Core 6.1: arbitrary truthful interaction prefixes cannot exceed the grammar. -/
example (T : Task P D Y) (G : List P) (E : List D)
    (tr : List (P × Option D)) (out : TraceStatus P)
    (h : TruthfulProtocol T G E tr out) :
    (tr.map Prod.fst).Nodup ∧ tr.length ≤ G.length :=
  ⟨truthful_nodup T h, truthful_call_bound T h⟩

/-- The actual implementation follows the specified restart-earliest learner. -/
example (T : Task P D Y) (G : List P) :
    Protocol T G [] (scan T G []).transcript (scan T G []).answer :=
  scan_protocol T G []

example (T : Task P D Y) (G : List P) (E : List D) :
    (scan T G E).answer = none ↔ ∀ p ∈ G, ¬ (∀ x, T.eval p x = T.target x) :=
  exhaustion_iff T G E

example (T : Task P D Y) (G : List P) (E : List D) (p : P)
    (h : (scan T G E).answer = some p) :
    ∃ before after, G = before ++ p :: after ∧ (∀ x, T.eval p x = T.target x) ∧
      ∀ q ∈ before, ¬ (∀ x, T.eval q x = T.target x) :=
  accepted_first T G E h

/-- Core 6.2: a one-way semantic condition suffices, not a complete equivalence oracle. -/
example (T : Task P D Y) (key : P → K)
    (hs : ∀ p q, key p = key q → ∀ x, T.eval p x = T.eval q x)
    (G : List P) (E : List D) :
    (scan T (representatives key [] G) E).answer = (scan T G E).answer ∧
    (scan T (representatives key [] G) E).transcript = (scan T G E).transcript ∧
    (scan T (representatives key [] G) E).retained = (scan T G E).retained ∧
    (scan T (representatives key [] G) E).comparisons ≤ (scan T G E).comparisons := by
  obtain ⟨⟨ha, ht, he⟩, hc, _⟩ := ordered_compression T key hs G E
  exact ⟨ha,ht,he,hc⟩

example (T : Task P D Y) (G : List P) (E : List D) (n : Nat) :
    resume T (boundedScan T n G E) = scan T G E := resume_bounded T n G E

example (T : Task P D Y) (G : List P) (E : List D) :
    boundedScan T G.length G E = .complete (scan T G E) :=
  enough_inspections T G.length G E (Nat.le_refl _)

example (T : Task P D Y) (key : P → K) (hs : KeySound T key) (G : List P) (E : List D) :
    teacherComparisons T (scan T (representatives key [] G) E) =
      teacherComparisons T (scan T G E) := teacher_work_preserved T key hs G E
