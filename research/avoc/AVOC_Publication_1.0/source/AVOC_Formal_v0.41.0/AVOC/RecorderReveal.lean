import AVOC.ObservationRecorder
import AVOC.ObservationReveal

namespace Komorebi.AVOC.RecorderReveal

/-!
A finite source-coupled recorder. Its checked-report command obtains the next
latent Boolean, after checking for an exact prior terminal replay. Thus a replay
never consumes the next Boolean. Every accepted command is also emitted as an
ordinary `ObservationRecorder.Command`; the projection theorem checks the whole
emitted execution, not only a single fresh event.

The source coupling is an explicit model assumption. These theorems do not show
that an external physical operation or Python adapter follows the latent source.
-/

abbrev CoreState := ObservationRecorder.State
abbrev CoreCommand := ObservationRecorder.Command
abbrev RevealState := ObservationReveal.State

inductive Command (Key : Type) where
  | begin (operation : Nat) (key : Key)
  | report (operation : Nat) (key : Key)
  | fault (operation : Nat) (key : Key)
  deriving DecidableEq

structure State (Key : Type) where
  recorder : CoreState Key
  reveal : RevealState Key
  emitted : List (CoreCommand Key)
  effectiveTrace : List (Option Key)

variable {Key : Type} [DecidableEq Key]

def initial (source : Key → List Bool) : State Key :=
  ⟨ObservationRecorder.initial, ObservationReveal.initial source, [], []⟩

/-- Commit only after the ordinary recorder has accepted the emitted command. -/
def commit (s : State Key) (c : CoreCommand Key) (r : Option Key) :
    Option (State Key) :=
  (ObservationRecorder.step s.recorder c).map fun t =>
    ⟨t, ObservationReveal.step s.reveal r, s.emitted ++ [c], s.effectiveTrace ++ [r]⟩

/-- A repeated report reuses its already recorded terminal Boolean. A fresh
report reads exactly the next source bit; exhaustion fails closed. -/
def step (s : State Key) : Command Key → Option (State Key)
  | .begin id key => commit s (.begin id key) none
  | .fault id key => commit s (.finish ⟨id, key, .fault⟩) none
  | .report id key =>
      if ⟨id, key, CalibrationLog.Outcome.success⟩ ∈ s.recorder.log then
        commit s (.finish ⟨id, key, .success⟩) none
      else if ⟨id, key, CalibrationLog.Outcome.rejection⟩ ∈ s.recorder.log then
        commit s (.finish ⟨id, key, .rejection⟩) none
      else match s.reveal.remaining key with
        | [] => none
        | bit :: _ =>
            commit s (.finish ⟨id, key, ObservationReveal.checkedOutcome bit⟩) (some key)

def runFrom (s : State Key) : List (Command Key) → Option (State Key)
  | [] => some s
  | c :: cs => (step s c).bind (fun t => runFrom t cs)

def run (source : Key → List Bool) (commands : List (Command Key)) :
    Option (State Key) := runFrom (initial source) commands

/-- The emitted commands, effective reveal trace, and observed samples agree. -/
structure Tracks (source : Key → List Bool) (s : State Key) : Prop where
  recorder_projection : ObservationRecorder.run s.emitted = some s.recorder
  reveal_projection : s.reveal = ObservationReveal.run source s.effectiveTrace
  samples : ∀ key, CalibrationLog.samples key s.recorder.log = s.reveal.reports key

theorem core_runFrom_append (s : CoreState Key) (a b : List (CoreCommand Key)) :
    ObservationRecorder.runFrom s (a ++ b) =
      (ObservationRecorder.runFrom s a).bind (fun t => ObservationRecorder.runFrom t b) := by
  induction a generalizing s with
  | nil => rfl
  | cons c cs ih =>
      simp only [List.cons_append, ObservationRecorder.runFrom]
      cases ObservationRecorder.step s c <;> simp [ih]

theorem reveal_runFrom_append (s : RevealState Key) (a b : List (Option Key)) :
    ObservationReveal.runFrom s (a ++ b) =
      ObservationReveal.runFrom (ObservationReveal.runFrom s a) b := by
  induction a generalizing s with
  | nil => rfl
  | cons c cs ih => exact ih _

@[simp] theorem initial_tracks (source : Key → List Bool) : Tracks source (initial source) := by
  constructor
  · rfl
  · rfl
  · intro key; rfl

theorem commit_effect {s t : State Key} {c : CoreCommand Key} {r : Option Key}
    (h : commit s c r = some t) :
    ObservationRecorder.step s.recorder c = some t.recorder ∧
      t.reveal = ObservationReveal.step s.reveal r ∧
      t.emitted = s.emitted ++ [c] ∧ t.effectiveTrace = s.effectiveTrace ++ [r] := by
  unfold commit at h
  cases hs : ObservationRecorder.step s.recorder c with
  | none => simp [hs] at h
  | some u =>
      simp only [hs, Option.map_some, Option.some.injEq] at h
      subst t
      exact ⟨rfl, rfl, rfl, rfl⟩

theorem commit_tracks {source : Key → List Bool} {s t : State Key}
    {c : CoreCommand Key} {r : Option Key} (hs : Tracks source s)
    (h : commit s c r = some t)
    (hlog : ∀ key, CalibrationLog.samples key t.recorder.log =
      (ObservationReveal.step s.reveal r).reports key) : Tracks source t := by
  obtain ⟨hc, hr, he, ht⟩ := commit_effect h
  constructor
  · rw [he, ObservationRecorder.run, core_runFrom_append]
    change (ObservationRecorder.run s.emitted).bind _ = _
    rw [hs.recorder_projection]
    simp [ObservationRecorder.runFrom, hc]
  · rw [ht, ObservationReveal.run, reveal_runFrom_append]
    change t.reveal = ObservationReveal.step (ObservationReveal.run source s.effectiveTrace) r
    rw [← hs.reveal_projection]
    exact hr
  · intro key
    rw [hr]
    exact hlog key

theorem replay_commit_tracks {source : Key → List Bool} {s t : State Key}
    {e : CalibrationLog.Event Key} (hs : Tracks source s)
    (he : e ∈ s.recorder.log)
    (h : commit s (.finish e) none = some t) : Tracks source t := by
  apply commit_tracks hs h
  have hc := (commit_effect h).1
  have hrecord := ObservationRecorder.finish_record hc
  rw [CalibrationLog.exact_replay _ _ he] at hrecord
  have hlogs : s.recorder.log = t.recorder.log := Option.some.inj hrecord
  intro key
  rw [← hlogs]
  exact hs.samples key

theorem fresh_report_commit_tracks {source : Key → List Bool} {s t : State Key}
    (hs : Tracks source s) (id : Nat) (key : Key) (bit : Bool) (rest : List Bool)
    (hnext : s.reveal.remaining key = bit :: rest)
    (hnew : (⟨id, key, ObservationReveal.checkedOutcome bit⟩ : CalibrationLog.Event Key)
      ∉ s.recorder.log)
    (h : commit s (.finish ⟨id, key, ObservationReveal.checkedOutcome bit⟩) (some key) = some t) :
    Tracks source t := by
  apply commit_tracks hs h
  have hc := (commit_effect h).1
  obtain ⟨_, hsame | hfresh⟩ := ObservationRecorder.finish_effect hc
  · exact False.elim (hnew hsame.2)
  · rcases hfresh with ⟨_, _, ht⟩
    intro j
    rw [ht]
    change CalibrationLog.samples j (s.recorder.log ++
      [⟨id, key, ObservationReveal.checkedOutcome bit⟩]) = _
    by_cases hj : j = key
    · subst j
      rw [ObservationReveal.checked_log_appends, hs.samples,
        ObservationReveal.checked_report_appends s.reveal key bit rest hnext]
    · rw [CalibrationLog.different_identity_no_observation j
        ⟨id, key, ObservationReveal.checkedOutcome bit⟩ s.recorder.log (Ne.symm hj),
        hs.samples]
      exact (ObservationReveal.other_identity_unchanged s.reveal key j hj).1.symm

theorem step_tracks {source : Key → List Bool} {s t : State Key}
    (hs : Tracks source s) (c : Command Key) (h : step s c = some t) : Tracks source t := by
  cases c with
  | begin id key =>
      apply commit_tracks hs h
      have hc := (commit_effect h).1
      have hlog := ObservationRecorder.begin_log_unchanged hc
      intro j
      rw [hlog]
      exact hs.samples j
  | fault id key =>
      apply commit_tracks hs h
      have hc := (commit_effect h).1
      obtain ⟨_, hsame | hfresh⟩ := ObservationRecorder.finish_effect hc
      · rw [hsame.1]
        exact hs.samples
      · rcases hfresh with ⟨_, _, ht⟩
        intro j
        rw [ht]
        simpa only [CalibrationLog.fault_not_observation, ObservationReveal.fault_preserves_state] using hs.samples j
  | report id key =>
      simp only [step] at h
      split at h
      · rename_i he
        exact replay_commit_tracks hs he h
      · rename_i hsuc
        split at h
        · rename_i he
          exact replay_commit_tracks hs he h
        · rename_i hrej
          cases hn : s.reveal.remaining key with
          | nil => simp [hn] at h
          | cons bit rest =>
              simp only [hn] at h
              apply fresh_report_commit_tracks hs id key bit rest hn _ h
              cases bit with
              | false => exact hrej
              | true => exact hsuc

theorem runFrom_tracks {source : Key → List Bool} {s t : State Key}
    (hs : Tracks source s) (commands : List (Command Key))
    (h : runFrom s commands = some t) : Tracks source t := by
  induction commands generalizing s with
  | nil =>
      have he : s = t := Option.some.inj h
      simpa only [← he] using hs
  | cons c cs ih =>
      simp only [runFrom] at h
      cases hc : step s c with
      | none => simp [hc] at h
      | some u =>
          simp only [hc, Option.bind_some] at h
          exact ih (step_tracks hs c hc) h

theorem run_tracks (source : Key → List Bool) (commands : List (Command Key))
    {s : State Key} (h : run source commands = some s) : Tracks source s :=
  runFrom_tracks (initial_tracks source) commands h

/-- Universal finite-command refinement to the ordinary intent recorder and
existing reveal machine, including all successful replay-containing traces. -/
theorem run_refines (source : Key → List Bool) (commands : List (Command Key))
    {s : State Key} (h : run source commands = some s) :
    ObservationRecorder.run s.emitted = some s.recorder ∧
      ∀ key, CalibrationLog.samples key s.recorder.log =
        (ObservationReveal.run source s.effectiveTrace).reports key := by
  have ht := run_tracks source commands h
  refine ⟨ht.recorder_projection, ?_⟩
  intro key
  rw [ht.samples, ht.reveal_projection]

theorem run_samples_eq_take (source : Key → List Bool) (commands : List (Command Key))
    {s : State Key} (h : run source commands = some s) (key : Key) :
    CalibrationLog.samples key s.recorder.log =
      (source key).take (CalibrationLog.samples key s.recorder.log).length := by
  rw [(run_refines source commands h).2 key]
  exact ObservationReveal.run_reports_eq_take source s.effectiveTrace key

theorem completed_samples_eq_source (source : Key → List Bool)
    (commands : List (Command Key)) {s : State Key}
    (h : run source commands = some s) (key : Key)
    (hready : (source key).length ≤ (CalibrationLog.samples key s.recorder.log).length) :
    CalibrationLog.samples key s.recorder.log = source key := by
  rw [run_samples_eq_take source commands h key]
  exact List.take_of_length_le hready


/-- Pending operations block issuance even if some other identity is ready.
This gate does not authenticate external outcomes or commit a sampling schedule. -/
def issue {Quote : Type} (s : State Key) (next : Quote) : Option Quote :=
  if s.recorder.pending = [] then some next else none

omit [DecidableEq Key] in
@[simp] theorem pending_blocks_issue {Quote : Type} (s : State Key) (next : Quote)
    (h : s.recorder.pending ≠ []) : issue s next = none := by
  simp [issue, h]

omit [DecidableEq Key] in
@[simp] theorem resolved_allows_issue {Quote : Type} (s : State Key) (next : Quote)
    (h : s.recorder.pending = []) : issue s next = some next := by
  simp [issue, h]

omit [DecidableEq Key] in
theorem issued_has_no_pending {Quote : Type} (s : State Key) (next : Quote)
    (h : issue s next = some next) : s.recorder.pending = [] := by
  unfold issue at h
  split at h
  · assumption
  · simp at h

theorem run_samples_length_le_source (source : Key → List Bool)
    (commands : List (Command Key)) {s : State Key}
    (h : run source commands = some s) (key : Key) :
    (CalibrationLog.samples key s.recorder.log).length ≤ (source key).length := by
  rw [(run_refines source commands h).2 key]
  exact ObservationReveal.reports_length_le_source source s.effectiveTrace key

theorem completed_success_count_eq (source : Key → List Bool)
    (commands : List (Command Key)) {s : State Key}
    (h : run source commands = some s) (key : Key)
    (hready : (source key).length ≤ (CalibrationLog.samples key s.recorder.log).length) :
    (CalibrationLog.samples key s.recorder.log).count true = (source key).count true := by
  rw [completed_samples_eq_source source commands h key hready]

/-- Replays before and after exhaustion, an intervening fault, and a late begin
all preserve the two checked source outcomes. -/
theorem replay_fault_exhaustion_example :
    (run (fun _ : Unit => [false, true])
      [.begin 0 (), .report 0 (), .report 0 (), .begin 1 (), .fault 1 (),
       .begin 2 (), .report 2 (), .report 0 (), .begin 0 ()]).map
        (fun s => CalibrationLog.samples () s.recorder.log) = some [false, true] := by
  decide

theorem replay_fault_exhaustion_has_no_pending :
    (run (fun _ : Unit => [false, true])
      [.begin 0 (), .report 0 (), .report 0 (), .begin 1 (), .fault 1 (),
       .begin 2 (), .report 2 (), .report 0 (), .begin 0 ()]).map
        (fun s => s.recorder.pending) = some [] := by
  decide

theorem exhausted_fresh_report_rejected :
    run (fun _ : Unit => [true])
      [.begin 0 (), .report 0 (), .begin 1 (), .report 1 ()] = none := by
  decide

theorem unknown_report_rejected :
    run (fun _ : Unit => [false]) [.report 0 ()] = none := by
  decide

theorem changed_identity_report_rejected :
    run (fun _ : Bool => [true]) [.begin 0 false, .report 0 true] = none := by
  decide

theorem report_after_fault_rejected :
    run (fun _ : Unit => [true]) [.begin 0 (), .fault 0 (), .report 0 ()] = none := by
  decide

end Komorebi.AVOC.RecorderReveal
