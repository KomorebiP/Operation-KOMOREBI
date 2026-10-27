import Mathlib.Data.Set.Function
import Mathlib.Data.Fintype.Basic
namespace Komorebi.MachineTheory.LegalQuotient
universe u v w z
structure System (X : Type u) (Action : Type v) (Label : Type w) where
  label : X → Label
  step : X → Action → Option X
structure Factors {X : Type u} {Action : Type v} {Label : Type w} {Z : Type z}
    (M : System X Action Label) (Q : System Z Action Label) (π : X → Z) : Prop where
  label_eq : ∀ x, M.label x = Q.label (π x)
  step_map : ∀ x a, Q.step (π x) a = (M.step x a).map π
end Komorebi.MachineTheory.LegalQuotient

/-!
# Preservation of legal finite executions

Reviewed Core v0.2, Theorem 8.2, final clause. An execution returns the initial
state and every successor, or `none` if any requested action is disabled.
All statements quantify over arbitrary finite action lists. In particular, the
empty word retains the initial label. Encoded availability is not an assertion
of external moral or legal authority.
-/

namespace Komorebi.MachineTheory.LegalQuotient

universe u v w z

variable {X : Type u} {Action : Type v} {Label : Type w} {Z : Type z}

/-- Execute a word, retaining its initial state and all intermediate states.
`none` means that an action was disabled when it was reached. -/
def execute (M : System X Action Label) : X → List Action → Option (List X)
  | x, [] => some [x]
  | x, a :: word =>
      (M.step x a).bind fun y => (execute M y word).map (x :: ·)

@[simp] theorem execute_nil (M : System X Action Label) (x : X) :
    execute M x [] = some [x] := rfl

@[simp] theorem execute_cons (M : System X Action Label) (x : X)
    (a : Action) (word : List Action) :
    execute M x (a :: word) =
      (M.step x a).bind (fun y => (execute M y word).map (x :: ·)) := rfl

/-- A word is legal exactly when all requested successors exist. -/
def Legal (M : System X Action Label) (x : X) (word : List Action) : Prop :=
  ∃ states, execute M x word = some states

/-- The complete protected-label sequence, including the initial label. -/
def labels (M : System X Action Label) (x : X) (word : List Action) :
    Option (List Label) :=
  (execute M x word).map (List.map M.label)

/-- The final state of a legal word, extracted from its complete state trace. -/
def endpoint (M : System X Action Label) (x : X) (word : List Action) : Option X :=
  (execute M x word).bind List.getLast?

@[simp] theorem labels_nil (M : System X Action Label) (x : X) :
    labels M x [] = some [M.label x] := rfl

theorem execute_cons_eq_some_iff (M : System X Action Label) (x : X)
    (a : Action) (word : List Action) (states : List X) :
    execute M x (a :: word) = some states ↔
      ∃ y rest, M.step x a = some y ∧ execute M y word = some rest ∧
        states = x :: rest := by
  cases hs : M.step x a with
  | none => simp [execute, hs]
  | some y =>
      cases he : execute M y word with
      | none => simp [execute, hs, he]
      | some rest => simp [execute, hs, he, eq_comm]

theorem legal_cons_iff (M : System X Action Label) (x : X)
    (a : Action) (word : List Action) :
    Legal M x (a :: word) ↔ ∃ y, M.step x a = some y ∧ Legal M y word := by
  constructor
  · rintro ⟨states, hs⟩
    obtain ⟨y, rest, hy, hr, _⟩ :=
      (execute_cons_eq_some_iff M x a word states).mp hs
    exact ⟨y, hy, rest, hr⟩
  · rintro ⟨y, hy, rest, hr⟩
    exact ⟨x :: rest, (execute_cons_eq_some_iff M x a word (x :: rest)).mpr
      ⟨y, rest, hy, hr, rfl⟩⟩

theorem execute_length (M : System X Action Label) (x : X)
    (word : List Action) (states : List X)
    (h : execute M x word = some states) : states.length = word.length + 1 := by
  induction word generalizing x states with
  | nil =>
      have hs : states = [x] := (Option.some.inj h).symm
      simp [hs]
  | cons a word ih =>
      obtain ⟨y, rest, _, hr, rfl⟩ :=
        (execute_cons_eq_some_iff M x a word states).mp h
      simpa [Nat.add_comm, Nat.add_left_comm, Nat.add_assoc] using
        congrArg Nat.succ (ih y rest hr)

theorem execute_head (M : System X Action Label) (x : X)
    (word : List Action) (states : List X)
    (h : execute M x word = some states) : states.head? = some x := by
  cases word with
  | nil =>
      have hs : states = [x] := (Option.some.inj h).symm
      simp [hs]
  | cons a word =>
      obtain ⟨_, rest, _, _, rfl⟩ :=
        (execute_cons_eq_some_iff M x a word states).mp h
      rfl

/-- Every state in every finite legal execution is projected to its quotient
state. Illegal words remain illegal in both directions. -/
theorem Factors.execute_map {M : System X Action Label} {Q : System Z Action Label}
    {π : X → Z} (h : Factors M Q π) (x : X) (word : List Action) :
    execute Q (π x) word = (execute M x word).map (List.map π) := by
  induction word generalizing x with
  | nil => rfl
  | cons a word ih =>
      rw [execute_cons, execute_cons, h.step_map x a]
      cases hs : M.step x a with
      | none => rfl
      | some y =>
          simp only [Option.map_some, Option.bind_some]
          rw [ih]
          cases execute M y word <;> rfl

theorem Factors.execute_eq_some {M : System X Action Label}
    {Q : System Z Action Label} {π : X → Z} (h : Factors M Q π)
    (x : X) (word : List Action) (states : List X)
    (hs : execute M x word = some states) :
    execute Q (π x) word = some (states.map π) := by
  rw [h.execute_map, hs]
  rfl

theorem Factors.endpoint_map {M : System X Action Label}
    {Q : System Z Action Label} {π : X → Z} (h : Factors M Q π)
    (x : X) (word : List Action) :
    endpoint Q (π x) word = (endpoint M x word).map π := by
  unfold endpoint
  rw [h.execute_map]
  cases execute M x word with
  | none => rfl
  | some states =>
      simp only [Option.map_some, Option.bind_some, List.getLast?_map]

/-- Legality is reflected as well as preserved. -/
theorem Factors.legal_iff {M : System X Action Label} {Q : System Z Action Label}
    {π : X → Z} (h : Factors M Q π) (x : X) (word : List Action) :
    Legal Q (π x) word ↔ Legal M x word := by
  unfold Legal
  rw [h.execute_map]
  cases execute M x word with
  | none => simp
  | some states => simp

theorem Factors.label_trace {M : System X Action Label} {Q : System Z Action Label}
    {π : X → Z} (h : Factors M Q π) (states : List X) :
    (states.map π).map Q.label = states.map M.label := by
  induction states with
  | nil => rfl
  | cons x states ih => simp only [List.map_cons, ← h.label_eq, ih]

/-- Equality covers every intermediate label, with `none` detecting every
illegal request. It is stronger than equality of final observations. -/
theorem Factors.labels_eq {M : System X Action Label} {Q : System Z Action Label}
    {π : X → Z} (h : Factors M Q π) (x : X) (word : List Action) :
    labels Q (π x) word = labels M x word := by
  unfold labels
  rw [h.execute_map]
  cases execute M x word with
  | none => rfl
  | some states =>
      simp only [Option.map_some]
      exact congrArg some (h.label_trace states)

/-- A quotient trace can be lifted from any chosen representative of its
initial state, without changing the action word or protected labels. -/
theorem Factors.lift_execution {M : System X Action Label}
    {Q : System Z Action Label} {π : X → Z} (h : Factors M Q π)
    (x : X) (word : List Action) (quotientStates : List Z)
    (hq : execute Q (π x) word = some quotientStates) :
    ∃ states, execute M x word = some states ∧ states.map π = quotientStates ∧
      states.map M.label = quotientStates.map Q.label := by
  have hl : Legal Q (π x) word := ⟨quotientStates, hq⟩
  obtain ⟨states, hs⟩ := (h.legal_iff x word).mp hl
  have hp : states.map π = quotientStates :=
    Option.some.inj ((h.execute_eq_some x word states hs).symm.trans hq)
  exact ⟨states, hs, hp, by rw [← hp]; exact (h.label_trace states).symm⟩

/-- Exact source-facing finite-state and finite-alphabet clause of Core 8.2.
The generic result above does not require finiteness. -/
theorem finite_legal_quotient_sequences [Finite X] [Finite Action]
    {M : System X Action Label} {Q : System Z Action Label} {π : X → Z}
    (h : Factors M Q π) (x : X) (word : List Action) :
    (Legal Q (π x) word ↔ Legal M x word) ∧
      execute Q (π x) word = (execute M x word).map (List.map π) ∧
      labels Q (π x) word = labels M x word :=
  ⟨h.legal_iff x word, h.execute_map x word, h.labels_eq x word⟩

end Komorebi.MachineTheory.LegalQuotient
