import MachineTheory.SynthesisBudget
import Mathlib.Tactic.FinCases
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Fintype.Fin
import Mathlib.Tactic.NormNum

/-!
# Checked finite examples and boundary controls

An eight-expression grammar is used for the displayed arithmetic synthesis.
There are exactly three declared training contexts. This is not a reproduction
of the older 3,960-expression experiment, nor a generalization claim from three
examples. The normalizer's key soundness is proved for every natural-number
prefix independently of the target labels.
-/

namespace Komorebi.MachineTheory.SynthesisExamples
open Synthesis

inductive Program where
  | zero | zeroAlias | bGtA | aLtB | bGtC | cLtB | maxGtC | swappedMax | capped
  deriving DecidableEq, Repr

abbrev Prefix := Nat × Nat × Nat

def evaluate : Program → Prefix → Bool
  | .zero, x => decide (x.1 > x.1)
  | .zeroAlias, _ => decide ((0 : Nat) = 1)
  | .bGtA, x => decide (x.2.1 > x.1)
  | .aLtB, x => decide (x.1 < x.2.1)
  | .bGtC, x => decide (x.2.1 > x.2.2)
  | .cLtB, x => decide (x.2.2 < x.2.1)
  | .maxGtC, x => decide (max x.1 x.2.1 > x.2.2)
  | .swappedMax, x => decide (max x.2.1 x.1 > x.2.2)
  | .capped, x => decide (max x.1 x.2.1 > min x.2.2 2)

def key : Program → Fin 5
  | .zero | .zeroAlias => 0
  | .bGtA | .aLtB => 1
  | .bGtC | .cLtB => 2
  | .maxGtC | .swappedMax => 3
  | .capped => 4

/-- These semantic equations hold beyond the three developmental contexts. -/
theorem arithmetic_key_sound (p q : Program) (h : key p = key q) (x : Prefix) :
    evaluate p x = evaluate q x := by
  cases p <;> cases q <;> simp_all [key, evaluate, max_comm]

def context : Fin 3 → Prefix
  | 0 => (0, 3, 2)
  | 1 => (0, 1, 2)
  | 2 => (3, 0, 2)

def task : Task Program (Fin 3) Bool where
  eval p i := evaluate p (context i)
  target i := evaluate .maxGtC (context i)
  contexts := [0,1,2]
  complete := by intro i; fin_cases i <;> decide

def grammar : List Program :=
  [.zero, .zeroAlias, .bGtA, .aLtB, .bGtC, .cLtB, .maxGtC, .swappedMax]

def quotientGrammar : List Program := [.zero, .bGtA, .bGtC, .maxGtC]

theorem task_key_sound : KeySound task key := by
  intro p q h i
  exact arithmetic_key_sound p q h (context i)

theorem prepared_grammar : representatives key [] grammar = quotientGrammar := by decide

theorem preparation_count : (prepare key [] grammar).1 = quotientGrammar ∧
    (prepare key [] grammar).2 = 10 := by decide

def expectedTrace : List (Program × Option (Fin 3)) :=
  [(.zero, some 0), (.bGtA, some 1), (.bGtC, some 2), (.maxGtC, none)]

/-- The original scan visits seven of eight ASTs and performs nine retained tests. -/
theorem original_run : scan task grammar [] =
    ⟨some .maxGtC, expectedTrace, [2,1,0], 9, 7⟩ := by decide

/-- The prepared scan has the identical transcript with six retained tests. -/
theorem compressed_run : scan task quotientGrammar [] =
    ⟨some .maxGtC, expectedTrace, [2,1,0], 6, 4⟩ := by decide

theorem arithmetic_trace_from_general_theorem :
    SameEvidence (scan task quotientGrammar []) (scan task grammar []) ∧
    (scan task quotientGrammar []).comparisons ≤ (scan task grammar []).comparisons ∧
    (scan task quotientGrammar []).visits ≤ (scan task grammar []).visits := by
  simpa [prepared_grammar] using ordered_compression task key task_key_sound grammar []

theorem same_teacher_work : teacherComparisons task (scan task grammar []) = 9 ∧
    teacherComparisons task (scan task quotientGrammar []) = 9 := by decide

theorem source_synthesis_contract :
    Protocol task grammar [] expectedTrace (some .maxGtC) ∧ expectedTrace.length = 4 := by
  constructor
  · have h := scan_protocol task grammar []
    rw [original_run] at h
    exact h
  · decide

/-- All false alternatives are excluded in this finite grammar, not all programs. -/
def failingGrammar : List Program := [.zero, .zeroAlias, .bGtA, .aLtB, .bGtC, .cLtB]

theorem failing_run : scan task failingGrammar [] =
    ⟨none, [(.zero,some 0),(.bGtA,some 1),(.bGtC,some 2)], [2,1,0], 6, 6⟩ := by decide

theorem failing_is_complete : ∀ p ∈ failingGrammar, ¬ Correct task p :=
  (exhaustion_iff task failingGrammar []).mp (by decide)

theorem outside_grammar_solution : Correct task .maxGtC ∧ Program.maxGtC ∉ failingGrammar := by
  constructor
  · intro i; rfl
  · decide

/-- Agreement on every admitted example does not prove a global arithmetic law. -/
theorem finite_fit_not_universal : Correct task .capped ∧
    evaluate .capped (0,5,8) ≠ evaluate .maxGtC (0,5,8) := by
  constructor
  · intro i; fin_cases i <;> decide
  · decide

/-- A collision from one probe erases the only correct Boolean program. -/
def probeTask : Task Bool Bool Bool where
  eval p x := if p then x else false
  target x := x
  contexts := [false,true]
  complete := by intro x; cases x <;> simp

def probeKey (p : Bool) : Bool := probeTask.eval p false

theorem probe_alias_changes_result :
    (scan probeTask [false,true] []).answer = some true ∧
    (scan probeTask (representatives probeKey [] [false,true]) []).answer = none := by decide

theorem probe_key_is_unsound : ¬ KeySound probeTask probeKey := by
  intro h
  have he := h false true (by decide) true
  simp [probeTask] at he

/-- Selecting the latest rather than the earliest equivalent AST changes the exact answer. -/
theorem later_representative_changes_ast :
    (scan task [.maxGtC,.swappedMax] []).answer = some .maxGtC ∧
    (scan task [.swappedMax] []).answer = some .swappedMax ∧
    (scan task [.maxGtC,.swappedMax] []).transcript ≠
      (scan task [.swappedMax] []).transcript := by decide

/-- A changed context order keeps correctness but not the counterexample transcript. -/
def reversedTask : Task Program (Fin 3) Bool :=
  {task with contexts := [2,1,0], complete := by intro i; fin_cases i <;> decide}

theorem changed_context_order :
    (scan reversedTask grammar []).answer = some .maxGtC ∧
    (scan reversedTask grammar []).transcript ≠ (scan task grammar []).transcript := by decide

/-- A deliberately noncompliant alternative that discards all older evidence. -/
def forgetfulScan (T : Task Program (Fin 3) Bool) : List Program → List (Fin 3) → Result Program (Fin 3)
  | [], E => ⟨none, [], E, 0, 0⟩
  | p :: ps, E =>
    let c := inspect T p E
    match c.1 with
    | some _ =>
      let r := forgetfulScan T ps E
      ⟨r.answer, r.transcript, r.retained, c.2 + r.comparisons, 1 + r.visits⟩
    | none =>
      match teacher T p with
      | none => ⟨some p, [(p,none)], E, c.2, 1⟩
      | some x =>
        let r := forgetfulScan T ps [x]
        ⟨r.answer, (p,some x) :: r.transcript, r.retained, c.2 + r.comparisons, 1 + r.visits⟩

def repeatGrammar : List Program := [.zero,.bGtA,.zero,.maxGtC]

theorem forgetting_repeats_submission :
    ((forgetfulScan task repeatGrammar []).transcript.map Prod.fst) =
      [.zero,.bGtA,.zero,.maxGtC] ∧
    ¬ ((forgetfulScan task repeatGrammar []).transcript.map Prod.fst).Nodup := by decide

theorem persistence_prevents_repeat :
    ((scan task repeatGrammar []).transcript.map Prod.fst) = [.zero,.bGtA,.maxGtC] ∧
    ((scan task repeatGrammar []).transcript.map Prod.fst).Nodup := by
  constructor
  · decide
  · exact no_repeated_submission task repeatGrammar []

/-- With four candidate inspections, one run is suspended and the other is completed. -/
theorem finite_budget_boundary :
    boundedScan task 4 grammar [] =
      .suspended ⟨[.bGtC,.cLtB,.maxGtC,.swappedMax], [1,0],
        [(.zero,some 0),(.bGtA,some 1)], 3, 4⟩ ∧
    boundedScan task 4 quotientGrammar [] = .complete (scan task quotientGrammar []) := by decide

theorem resumed_evidence : resume task (boundedScan task 4 grammar []) = scan task grammar [] :=
  resume_bounded task 4 grammar []

theorem suspension_is_not_exhaustion :
    ¬ ∃ r, boundedScan task 4 grammar [] = .complete r ∧ r.answer = none := by
  intro ⟨r, hr, _⟩
  rw [finite_budget_boundary.1] at hr
  contradiction

/-- Preparation has a separate, nonzero event count even when semantic replay is exact. -/
theorem preparation_can_outweigh_saved_tests :
    (prepare key [] grammar).2 + (scan task quotientGrammar []).comparisons >
      (scan task grammar []).comparisons := by decide

/-- Common events on a finite batch: three saved retained tests per run, ten key tests once.
This comparison does not charge key computation, index storage or all host instructions. -/
theorem illustrative_amortization (n : Nat) :
    (prepare key [] grammar).2 + n * (scan task quotientGrammar []).comparisons <
      n * (scan task grammar []).comparisons ↔ 4 ≤ n := by
  rw [preparation_count.2, original_run, compressed_run]
  dsimp
  omega

/-- With no contexts every program is vacuously correct; the first is still preserved. -/
def emptyContextTask : Task Bool Empty Bool where
  eval _ x := Empty.elim x
  target x := Empty.elim x
  contexts := []
  complete x := Empty.elim x

theorem empty_context_earliest :
    (scan emptyContextTask [false,true] []).answer = some false ∧
    (scan emptyContextTask [false,true] []).transcript.length = 1 := by decide

theorem empty_grammar_exhausted : (scan task [] []).answer = none ∧
    (scan task [] []).transcript.length = 0 := by decide

/-- A new target defines a different synthesis problem even with unchanged syntax. -/
def changedTask : Task Program (Fin 3) Bool :=
  {task with target := fun i => !(task.target i)}

theorem target_change_breaks_old_answer :
    (scan changedTask grammar []).answer = none ∧
    (scan task grammar []).answer = some .maxGtC := by decide

end Komorebi.MachineTheory.SynthesisExamples
