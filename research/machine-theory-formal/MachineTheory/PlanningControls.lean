import MachineTheory.PlanningSensor

/-! Kernel-checked boundaries of the planning result. Models here are explicitly separate
from the manuscript sensor when their menus, losses, or charges differ. -/
namespace Komorebi.MachineTheory.PlanningControls
open Instrument Planning BeliefPlanning PlanningSensor
open scoped BigOperators
noncomputable section

/-- Only the permitted terminal decision costs two; a forbidden zero-loss decision is not an option. -/
def noExperiments : Model Unit Unit Bool Bool where
  actions _ := ∅
  decisions _ := {false}
  decisions_nonempty _ := by simp
  cost _ _ := 0
  cost_nonnegative _ _ := le_rfl
  loss _ d := if d then 0 else 2
  prob _ _ o := if o then 0 else 1
  nonnegative _ _ o := by cases o <;> norm_num
  normalized _ _ := by norm_num
  next _ _ _ _ := ()

theorem empty_experiment_menu_value (h : Nat) : value noExperiments h () = 2 := by
  cases h <;> simp [value, finiteMin, menu, noExperiments]

theorem forbidden_terminal_not_optimized : ¬ Feasible noExperiments 0 () (.stop true) := by
  simp [Feasible, noExperiments]

/-- A permissible experiment has one possible report. -/
def oneReport : Model Unit Unit Bool Bool :=
  { noExperiments with
    actions := fun _ => {()}
    cost := fun _ _ => 1/2
    cost_nonnegative := by intros; norm_num }

def dormantBranch : Tree Unit Bool Bool :=
  .experiment () (fun o => if o then .stop true else .stop false)

/-- The dormant branch has a syntactic placeholder, but no posterior or permission claim is made there. -/
theorem impossible_branch_ignored : Feasible oneReport 1 () dormantBranch := by
  simp [Feasible, oneReport, noExperiments, dormantBranch]

theorem impossible_branch_cost_zero : evaluate oneReport dormantBranch () = 5/2 := by
  norm_num [evaluate, oneReport, noExperiments, dormantBranch]

theorem zero_horizon_forbids_experiment : ¬ Feasible oneReport 0 () dormantBranch := by
  simp [Feasible, dormantBranch]

/-- Current information states have the same observation law but different legal terminal choices. -/
def permissions : Model Bool Unit Unit Bool where
  actions _ := ∅
  decisions b := {b}
  decisions_nonempty _ := by simp
  cost _ _ := 0
  cost_nonnegative _ _ := le_rfl
  loss _ _ := 0
  prob _ _ _ := 1
  nonnegative _ _ _ := by norm_num
  normalized _ _ := by simp
  next b _ _ _ := b

theorem same_reports_different_permissions :
    permissions.prob false () () = permissions.prob true () () ∧
    Feasible permissions 0 false (.stop false) ∧ ¬ Feasible permissions 0 true (.stop false) := by
  simp [permissions, Feasible]

/-- No one-state planner can preserve both of these terminal catalogues. -/
theorem no_common_permission_quotient (N : Model Unit Unit Unit Bool) :
    ¬ ExactMap permissions N (fun _ => ()) := by
  intro H
  have he := (H.decisions false).trans (H.decisions true).symm
  have hm : false ∈ permissions.decisions true := he ▸ (by simp [permissions])
  simp [permissions] at hm

/-- Even equality of optimal numbers does not imply equality of minimizing choices. -/
def differentTargets : Model Bool Unit Unit Bool :=
  { permissions with
    decisions := fun _ => Finset.univ
    decisions_nonempty := fun _ => Finset.univ_nonempty
    loss := fun b d => if b = d then 0 else 1 }

theorem equal_values_different_choices :
    value differentTargets 1 false = value differentTargets 1 true ∧
    OptimalFirst differentTargets 0 false (.inl false) ∧
    ¬ OptimalFirst differentTargets 0 true (.inl false) := by
  norm_num [value, finiteMin, menu, differentTargets, permissions, OptimalFirst, firstValue]

/-- Raising a measurement fee leaves all sensor probabilities and posterior updates unchanged. -/
def expensiveSensor : Model Counts Unit Bool Bool :=
  { countModel with
    cost := fun _ _ => 1
    cost_nonnegative := by intros; norm_num }

theorem expense_preserves_reports (n : Counts) (o : Bool) :
    expensiveSensor.prob n () o = countModel.prob n () o := rfl

theorem expense_preserves_update (n : Counts) (o : Bool)
    (ho : 0 < expensiveSensor.prob n () o) :
    expensiveSensor.next n () o ho = countModel.next n () o ho := rfl

theorem expensive_zero (n : Counts) : value expensiveSensor 0 n = scalarValue 0 n :=
  count_value_eq_scalar 0 n

theorem expensive_first_query : backup expensiveSensor (value expensiveSensor 0) (0,0) () = 5/4 := by
  change (1 : ℝ) + (∑ o, if _ : 0 < report (0,0) o then
    report (0,0) o * value expensiveSensor 0 (advance (0,0) o) else 0) = _
  simp only [Fintype.sum_bool, report_pos, dite_true, expensive_zero]
  norm_num [scalarValue, stopRisk, report, advance, total, wTrue, wFalse]

theorem expensive_value : value expensiveSensor 1 (0,0) = 1/2 := by
  apply le_antisymm
  · have h := value_le_stop expensiveSensor 1 (0,0) false (by simp [expensiveSensor, countModel])
    change value expensiveSensor 1 (0,0) ≤ stopRisk (0,0) false at h
    norm_num [stopRisk, total, wTrue, wFalse] at h
    exact h
  · apply le_finiteMin
    intro c _
    cases c with
    | inl d => cases d <;> norm_num [expensiveSensor, countModel, stopRisk, total, wTrue, wFalse]
    | inr a => cases a; change (1/2 : ℝ) ≤ backup expensiveSensor (value expensiveSensor 0) (0,0) ()
               rw [expensive_first_query]; norm_num

theorem unchanged_filter_different_value :
    value countModel 1 (0,0) ≠ value expensiveSensor 1 (0,0) := by
  rw [sensor_value_table.2.1, expensive_value]
  norm_num

theorem expensive_experiment_not_optimal : ¬ OptimalFirst expensiveSensor 0 (0,0) (.inr ()) := by
  intro h
  have he := h.2
  change backup expensiveSensor (value expensiveSensor 0) (0,0) () = value expensiveSensor 1 (0,0) at he
  rw [expensive_first_query, expensive_value] at he
  norm_num at he

end
end Komorebi.MachineTheory.PlanningControls
