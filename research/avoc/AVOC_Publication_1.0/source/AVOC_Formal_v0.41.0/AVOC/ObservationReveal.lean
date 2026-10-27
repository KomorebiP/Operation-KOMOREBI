import AVOC.CalibrationLog
import Mathlib.Tactic

namespace Komorebi.AVOC.ObservationReveal

/-!
An explicit finite reveal machine. A checked report consumes exactly the next
latent Boolean for its identity; an infrastructure fault consumes nothing.
The trace may allocate reports adaptively between identities. All conclusions
below are pointwise, so no independence of the trace is needed. Independence of
latent outcomes is a separate statistical assumption, not a consequence of this
machine. In particular, conditioning on completion is not justified here.
-/

variable {Key : Type} [DecidableEq Key]

structure State (Key : Type) where
  reports : Key → List Bool
  remaining : Key → List Bool

def initial (source : Key → List Bool) : State Key :=
  ⟨fun _ => [], source⟩

/-- `none` is a fault/no-report operation. `some key` is a checked report:
both `true` (success) and `false` (rejection) consume one latent outcome.
An exhausted identity is unchanged. -/
def step (s : State Key) : Option Key → State Key
  | none => s
  | some key =>
      match s.remaining key with
      | [] => s
      | bit :: rest =>
          ⟨fun j => if j = key then s.reports j ++ [bit] else s.reports j,
           fun j => if j = key then rest else s.remaining j⟩

/-- Execute the operations in list order. -/
def runFrom (s : State Key) : List (Option Key) → State Key
  | [] => s
  | operation :: rest => runFrom (step s operation) rest

def run (source : Key → List Bool) (trace : List (Option Key)) : State Key :=
  runFrom (initial source) trace

def Conserves (source : Key → List Bool) (s : State Key) : Prop :=
  ∀ key, source key = s.reports key ++ s.remaining key

omit [DecidableEq Key] in
theorem initial_conserves (source : Key → List Bool) :
    Conserves source (initial source) := by
  intro key
  simp [initial]

theorem step_conserves (source : Key → List Bool) (s : State Key)
    (h : Conserves source s) (operation : Option Key) :
    Conserves source (step s operation) := by
  cases operation with
  | none => exact h
  | some key =>
      cases hremaining : s.remaining key with
      | nil => simpa [step, hremaining] using h
      | cons bit rest =>
          intro j
          by_cases hj : j = key
          · subst j
            simpa [step, hremaining, List.append_assoc] using h key
          · simpa [step, hremaining, hj] using h j

theorem runFrom_conserves (source : Key → List Bool) (s : State Key)
    (h : Conserves source s) (trace : List (Option Key)) :
    Conserves source (runFrom s trace) := by
  induction trace generalizing s with
  | nil => exact h
  | cons operation rest ih =>
      exact ih (step s operation) (step_conserves source s h operation)

theorem run_conserves (source : Key → List Bool) (trace : List (Option Key)) :
    Conserves source (run source trace) :=
  runFrom_conserves source (initial source) (initial_conserves source) trace

/-- Every stored sample is the initial segment of its own identity's source;
the scheduler cannot skip a latent success or rejection. -/
theorem run_reports_eq_take (source : Key → List Bool)
    (trace : List (Option Key)) (key : Key) :
    (run source trace).reports key =
      (source key).take ((run source trace).reports key).length := by
  have h := run_conserves source trace key
  rw [h]
  simp

theorem reports_length_le_source (source : Key → List Bool)
    (trace : List (Option Key)) (key : Key) :
    ((run source trace).reports key).length ≤ (source key).length := by
  have h := congrArg List.length (run_conserves source trace key)
  simp only [List.length_append] at h
  omega

/-- Readiness is checked without conditioning the sampling law on readiness.
At readiness, the stored list equals the full, fixed latent source. -/
theorem completed_reports_eq_source (source : Key → List Bool)
    (trace : List (Option Key)) (key : Key)
    (hready : (source key).length ≤ ((run source trace).reports key).length) :
    (run source trace).reports key = source key := by
  rw [run_reports_eq_take]
  exact List.take_of_length_le hready

theorem completed_success_count_eq (source : Key → List Bool)
    (trace : List (Option Key)) (key : Key)
    (hready : (source key).length ≤ ((run source trace).reports key).length) :
    ((run source trace).reports key).count true = (source key).count true := by
  rw [completed_reports_eq_source source trace key hready]

@[simp] theorem fault_preserves_state (s : State Key) : step s none = s := rfl

theorem checked_report_appends (s : State Key) (key : Key) (bit : Bool)
    (rest : List Bool) (h : s.remaining key = bit :: rest) :
    (step s (some key)).reports key = s.reports key ++ [bit] := by
  simp [step, h]

theorem checked_report_consumes_next (s : State Key) (key : Key) (bit : Bool)
    (rest : List Bool) (h : s.remaining key = bit :: rest) :
    (step s (some key)).remaining key = rest := by
  simp [step, h]

theorem other_identity_unchanged (s : State Key) (key other : Key)
    (h : other ≠ key) :
    (step s (some key)).reports other = s.reports other ∧
      (step s (some key)).remaining other = s.remaining other := by
  cases hremaining : s.remaining key <;> simp [step, hremaining, h]

@[simp] theorem exhausted_preserves_state (s : State Key) (key : Key)
    (h : s.remaining key = []) : step s (some key) = s := by
  simp [step, h]

/-- The reveal Boolean has the same checked-outcome interpretation as the
existing operation log. A rejection is a report, unlike an infrastructure fault. -/
def checkedOutcome (bit : Bool) : CalibrationLog.Outcome :=
  if bit then .success else .rejection

@[simp] theorem checkedOutcome_sample (bit : Bool) :
    (checkedOutcome bit).sample = some bit := by
  cases bit <;> rfl

theorem checked_log_appends (log : List (CalibrationLog.Event Key)) (key : Key)
    (operation : Nat) (bit : Bool) :
    CalibrationLog.samples key (log ++ [⟨operation, key, checkedOutcome bit⟩]) =
      CalibrationLog.samples key log ++ [bit] := by
  simp [CalibrationLog.samples]

/-- When the existing recorder accepts a fresh checked event, its samples agree
with the reveal step for every identity. Exact replays and conflicting operation
identifiers are handled by `CalibrationLog.record` before taking a reveal step. -/
theorem fresh_checked_record_tracks_step
    (s : State Key) (log : List (CalibrationLog.Event Key))
    (hlog : ∀ j, CalibrationLog.samples j log = s.reports j)
    (key : Key) (operation : Nat) (bit : Bool) (rest : List Bool)
    (hnext : s.remaining key = bit :: rest)
    (hfresh : ¬ ∃ old ∈ log, old.operation = operation) (j : Key) :
    (CalibrationLog.record log ⟨operation, key, checkedOutcome bit⟩).map
        (CalibrationLog.samples j) = some ((step s (some key)).reports j) := by
  rw [CalibrationLog.fresh_record log ⟨operation, key, checkedOutcome bit⟩ hfresh]
  simp only [Option.map_some]
  congr 1
  by_cases hj : j = key
  · subst j
    rw [checked_log_appends, hlog, checked_report_appends s key bit rest hnext]
  · rw [CalibrationLog.different_identity_no_observation j
        ⟨operation, key, checkedOutcome bit⟩ log (Ne.symm hj), hlog]
    exact (other_identity_unchanged s key j hj).1.symm

theorem fresh_fault_record_tracks_step
    (s : State Key) (log : List (CalibrationLog.Event Key))
    (hlog : ∀ j, CalibrationLog.samples j log = s.reports j)
    (key : Key) (operation : Nat)
    (hfresh : ¬ ∃ old ∈ log, old.operation = operation) (j : Key) :
    (CalibrationLog.record log ⟨operation, key, .fault⟩).map
        (CalibrationLog.samples j) = some ((step s none).reports j) := by
  rw [CalibrationLog.fresh_record log ⟨operation, key, .fault⟩ hfresh]
  simp only [Option.map_some, CalibrationLog.fault_not_observation,
    hlog, fault_preserves_state]

/-- The fault between two reports leaves the first rejection in the sample. -/
theorem fault_rejection_example :
    (run (fun _ : Unit => [false, true]) [some (), none, some ()]).reports () =
      [false, true] := rfl

end Komorebi.AVOC.ObservationReveal
