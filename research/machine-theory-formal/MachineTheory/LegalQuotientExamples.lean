import MachineTheory.LegalQuotient
import MachineTheory.LegalTrace

/-! # Exact legal-operation quotients

False names observation and true names repair. The visible bit records an
outstanding repair. A second bit is historical detail. Observation is always
enabled; repair is enabled only while outstanding. Successful steps toggle
the historical bit. Forgetting history preserves the operational interface.

Separate examples isolate the label, availability, and projected-successor
conditions. These are stipulated finite institutions, not claims of external
legal or moral authorization.
-/
namespace Komorebi.MachineTheory.LegalQuotientExamples
open LegalQuotient

abbrev FineState := Bool × Bool

def fine : System FineState Bool Bool where
  label x := x.1
  step x a := if a then
    if x.1 then some (false, !x.2) else none
    else some (x.1, !x.2)

def coarse : System Bool Bool Bool where
  label b := b
  step b a := if a then if b then some false else none else some b

def forgetHistory : FineState → Bool := Prod.fst

theorem forgetHistory_surjective : Function.Surjective forgetHistory :=
  fun b => ⟨(b,false), rfl⟩

theorem history_quotient_factors : Factors fine coarse forgetHistory := by
  apply factors_of_label_step
  · intro x; rfl
  · rintro ⟨b,h⟩ a
    cases b <;> cases a <;> rfl

/-- Fine successors may differ, provided their retained projections agree. -/
theorem projected_not_literal_successors :
    fine.step (true,false) false ≠ fine.step (true,true) false ∧
    (fine.step (true,false) false).map forgetHistory =
      (fine.step (true,true) false).map forgetHistory := by
  decide

theorem repair_then_observe :
    execute fine (true,false) [true,false] =
      some [(true,false),(false,true),(false,false)] ∧
    execute coarse true [true,false] = some [true,false,false] ∧
    labels fine (true,false) [true,false] = some [true,false,false] := by
  decide

theorem repeated_repair_refused :
    execute fine (true,false) [true,true] = none ∧
    execute coarse true [true,true] = none := by
  decide

theorem empty_trace_keeps_initial_label :
    labels fine (true,false) [] = some [true] := by
  rfl

/-- Label loss alone invalidates the collapse, though no actions are enabled. -/
def labelBad : System Bool Bool Bool where
  label := id
  step _ _ := none

theorem labels_block_collapse : ¬ FibreCompatible labelBad (fun _ => ()) := by
  intro h
  exact Bool.false_ne_true (h.label_eq false true rfl)

/-- The sensor label is identical, but only the true state permits repair. -/
def permissionBad : System Bool Bool Bool where
  label _ := false
  step b a := if a then if b then some false else none else some b

theorem same_sensor_different_permission :
    permissionBad.label false = permissionBad.label true ∧
    permissionBad.step false true = none ∧
    permissionBad.step true true = some false := by
  decide

theorem permissions_block_collapse :
    ¬ FibreCompatible permissionBad (fun _ => ()) := by
  intro h
  have he := h.enabled_eq false true rfl
  have ht : true ∈ enabled permissionBad false := by
    rw [he]
    simp [enabled, permissionBad]
  simp [enabled, permissionBad] at ht

/-- Every label and enabled set is constant, but hidden history affects the next visible bit. -/
def successorBad : System FineState Bool Bool where
  label _ := false
  step x _ := some (x.2,x.2)

theorem same_label_and_permissions_different_successor :
    successorBad.label (false,false) = successorBad.label (false,true) ∧
    enabled successorBad (false,false) = enabled successorBad (false,true) ∧
    (successorBad.step (false,false) true).map forgetHistory ≠
      (successorBad.step (false,true) true).map forgetHistory := by
  refine ⟨rfl, ?_, by decide⟩
  ext a
  simp [enabled, successorBad]

theorem successors_block_quotient : ¬ FibreCompatible successorBad forgetHistory := by
  intro h
  have he := h.successor_eq (false,false) (false,true) true
    (false,false) (true,true) rfl rfl rfl
  exact Bool.false_ne_true he

/-- A source reaching only false cannot constrain the quotient's label at true. -/
def oneSource : System Unit Bool Bool where
  label _ := false
  step _ _ := none

def offImage₀ : System Bool Bool Bool where
  label _ := false
  step _ _ := none

def offImage₁ : System Bool Bool Bool where
  label := id
  step _ _ := none

def onlyFalse (_ : Unit) : Bool := false

theorem missing_surjectivity_two_quotients :
    Factors oneSource offImage₀ onlyFalse ∧
    Factors oneSource offImage₁ onlyFalse ∧ offImage₀ ≠ offImage₁ := by
  constructor
  · apply factors_of_label_step
    · intro x; rfl
    · intro x a; rfl
  constructor
  · apply factors_of_label_step
    · intro x; rfl
    · intro x a; rfl
  · intro h
    have he := congrArg (fun M : System Bool Bool Bool => M.label true) h
    exact Bool.false_ne_true he

theorem onlyFalse_not_surjective : ¬ Function.Surjective onlyFalse := by
  intro h
  obtain ⟨x, hx⟩ := h true
  exact Bool.false_ne_true hx

/-- Disabled successors have no operational value. Arbitrary defaults are not quotient data. -/
theorem disabled_totalizations_not_unique :
    coarse.step false true = none ∧
    (coarse.step false true).getD false ≠ (coarse.step false true).getD true := by
  decide

end Komorebi.MachineTheory.LegalQuotientExamples
