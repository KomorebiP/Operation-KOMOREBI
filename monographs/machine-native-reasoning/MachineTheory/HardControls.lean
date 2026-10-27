import MachineTheory.HardSemantics
import MachineTheory.RecipientExamples
import Mathlib.Tactic.NormNum

/-! # Source-bound hard-budget and actual-state controls -/
namespace Komorebi.MachineTheory.HardControls
open HardInquiry Finset

/-- Read one immutable Boolean state; both report branches must be installed. -/
def readBit : Model Bool Unit Bool Bool Unit where
  permitted := fun _ _ => true
  next := fun _ x => x
  observe := fun _ x => x
  accept := fun x c => decide (x=c)
  stepCost := fun _ _ => 1
  terminalCost := fun _ _ _ => 0

def bitTree : Tree Unit Bool Bool 1 := .inr ((),fun o => some o)
def missingBranch : Tree Unit Bool Bool 1 := .inr ((),fun o => if o then none else some false)

theorem bit_tree_valid : readBit.Valid 1 univ bitTree := by decide
theorem bit_tree_cost : readBit.profile 1 univ bitTree = (fun _ => 1,3) := by decide
theorem missing_reachable_rejected : ¬ readBit.Valid 1 univ missingBranch := by decide

def restricted : Model Bool Unit Bool Bool Unit :=
  { readBit with permitted := fun _ x => !x }

theorem permission_at_one_case : restricted.permitted () false = true := rfl
theorem permission_not_uniform : ¬ restricted.Allowed univ () := by decide
theorem existential_permission_insufficient : ¬ restricted.Valid 1 univ bitTree := by decide

def constantReport : Model Bool Unit Bool Bool Unit :=
  { readBit with observe := fun _ _ => false, accept := fun _ _ => true }

def constantTree : Tree Unit Bool Bool 1 := .inr ((),fun o => if o then none else some false)

theorem impossible_report_absent : constantReport.Valid 1 univ constantTree := by decide
theorem impossible_report_has_no_record : constantReport.profile 1 univ constantTree = (fun _ => 1,2) := by decide
theorem invented_child_rejected : ¬ constantReport.Valid 1 univ bitTree := by decide

def noArtifact : Model Bool Unit Bool Bool Unit := { readBit with accept := fun _ _ => false }
theorem unsolved_children_not_free : noArtifact.compute 1 univ = ∅ := by decide
theorem noArtifact_no_tree : ¬ ∃ t : Tree Unit Bool Bool 1, noArtifact.Valid 1 univ t := by
  apply (noArtifact.no_tree_iff_empty 1 univ).mpr
  rw [← noArtifact.compute_eq_solve,unsolved_children_not_free]

/-- Terminal execution costs are charged after the observation. -/
def paidTerminal : Model Bool Unit Bool Bool Unit :=
  { readBit with terminalCost := fun _ _ _ => 3 }

theorem terminal_cost_included : paidTerminal.profile 1 univ bitTree = (fun _ => 4,3) := by decide
theorem one_unit_not_total_work : ¬ paidTerminal.profile 1 univ bitTree ≤ (fun _ => 1,3) := by decide

/-- A reset produces knowledge of the new state, not of the old one. -/
def reset : Model Bool Unit Unit Bool Unit where
  permitted := fun _ _ => true
  next := fun _ _ => false
  observe := fun _ _ => ()
  accept := fun x c => decide (x=c)
  stepCost := fun _ _ => 1
  terminalCost := fun _ _ _ => 0

def resetTree : Tree Unit Unit Bool 1 := .inr ((),fun _ => some false)

theorem reset_post_support : reset.update univ () () = {false} := by decide
theorem reset_current_valid : reset.Valid 1 univ resetTree := by decide
theorem reset_current_profile : reset.profile 1 univ resetTree = (fun _ => 1,2) := by decide

def taggedReset : Model (Bool × Bool) Unit Unit Bool Unit where
  permitted := fun _ _ => true
  next := fun _ x => (x.1,false)
  observe := fun _ _ => ()
  accept := fun x c => decide (x.1=c)
  stepCost := fun _ _ => 1
  terminalCost := fun _ _ _ => 0

def origins : Finset (Bool × Bool) := {(false,false),(true,true)}
theorem origin_tag_survives : taggedReset.update origins () () = {(false,false),(true,false)} := by decide
theorem reset_does_not_recover_origin : ¬ taggedReset.Valid 1 origins resetTree := by decide
theorem origin_inquiry_still_unresolved : taggedReset.compute 1 origins = ∅ := by decide

/-- Separate coordinates can attain their maxima on different executions. -/
def twoCoordinates : Model Bool Unit Bool Bool Bool where
  permitted := fun _ _ => true
  next := fun _ x => x
  observe := fun _ x => x
  accept := fun x c => decide (x=c)
  stepCost := fun _ _ => 0
  terminalCost := fun _ V j => V.sup (fun x => if x=j then 10 else 0)

def twoCharge (_ : Bool) (x j : Bool) : ℕ := if x=j then 10 else 0

theorem coordinate_charge_exact : twoCoordinates.ExactCharges twoCharge := fun _ _ _ => rfl
theorem coordinate_tree_valid : twoCoordinates.Valid 1 univ bitTree := by decide
theorem coordinate_profile : twoCoordinates.profile 1 univ bitTree = (fun _ => 10,3) := by decide
theorem maxima_not_one_execution : ∀ x : Bool,
    (twoCoordinates.execute twoCharge 1 bitTree x).map (fun r => (r.cost false,r.cost true)) ≠ some (10,10) := by decide

theorem coordinate_each_attained (j : Bool) : ∃ x ∈ (univ : Finset Bool), ∃ r,
    twoCoordinates.execute twoCharge 1 bitTree x = some r ∧ r.cost j = 10 := by
  simpa only [coordinate_profile] using
    twoCoordinates.worst_coordinate_attained twoCharge coordinate_charge_exact 1 univ bitTree coordinate_tree_valid j

/-- Source sensor: observations, combined recipient arithmetic, and message bits stay separate. -/
def sensorCharge (_ : Bool) (_ : RecipientExamples.Sensor) (j : Fin 3) : ℕ :=
  if j=0 then 0 else if j=1 then 2 else 1

def sensor : Model RecipientExamples.Sensor Unit Bool Bool (Fin 3) where
  permitted := fun _ _ => true
  next := fun _ x => x
  observe := fun _ x => RecipientExamples.display x
  accept := fun x c => decide (c=RecipientExamples.display x)
  stepCost := fun _ j => if j=0 then 1 else 0
  terminalCost := fun c V j => V.sup (fun x => sensorCharge c x j)

/-- The finite terminal table is proved to be the unchanged installed audience contract. -/
theorem sensor_accept_iff (x : RecipientExamples.Sensor) (c : Bool) :
    sensor.accept x c = true ↔ RecipientExamples.xorAudience.Accepts x c := by
  simp only [sensor,decide_eq_true_eq,RecipientExamples.xor_accepts_iff]

theorem sensor_needs_observation : sensor.compute 0 univ = ∅ := by decide
theorem sensor_tree_valid : sensor.Valid 1 univ bitTree := by decide
theorem sensor_tree_profile : sensor.profile 1 univ bitTree =
    (fun j => if j=0 then 1 else if j=1 then 2 else 1, 3) := by decide

theorem sensor_frontier : sensor.compute 1 univ =
    {(fun j => if j=0 then 1 else if j=1 then 2 else 1, 3)} := by decide

theorem sensor_charge_exact : sensor.ExactCharges sensorCharge := fun _ _ _ => rfl

/-- The same single observation and broadcast succeeds for both actual fixed recipients. -/
theorem sensor_recipient_execution (x : RecipientExamples.Sensor) :
    ∃ r, sensor.execute sensorCharge 1 bitTree x = some r ∧
      RecipientExamples.xorAudience.Accepts r.finalState r.artifact ∧
      (r.cost 0,r.cost 1,r.cost 2,r.history.length) = (1,2,1,1) := by
  obtain ⟨r,hr,ha,_,_⟩ := sensor.execution_sound sensorCharge sensor_charge_exact.bounded
    1 univ bitTree sensor_tree_valid x (mem_univ _)
  refine ⟨r,hr,(sensor_accept_iff _ _).mp ha,?_⟩
  have he : (sensor.execute sensorCharge 1 bitTree x).map
      (fun r => (r.cost 0,r.cost 1,r.cost 2,r.history.length)) = some (1,2,1,1) := by
    rcases x with ⟨b,s,n⟩
    cases b <;> cases s <;> cases n <;> decide
  rw [hr] at he
  exact Option.some.inj he

/-- With fewer stored records the complete two-branch controller is unavailable. -/
theorem sensor_two_records_insufficient :
    ¬ ∃ t : Tree Unit Bool Bool 1, sensor.Valid 1 univ t ∧
      sensor.profile 1 univ t ≤ (fun j => if j=0 then 1 else if j=1 then 2 else 1, 2) := by
  rw [sensor.computed_budget_iff, sensor_frontier]
  simp only [mem_singleton,exists_eq_left]
  intro h
  have hc := h.2
  exact (by decide : ¬ (3 ≤ 2)) hc

end Komorebi.MachineTheory.HardControls
