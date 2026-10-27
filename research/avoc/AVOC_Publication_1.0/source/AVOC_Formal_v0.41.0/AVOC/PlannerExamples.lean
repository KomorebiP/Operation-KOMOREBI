import AVOC.WorkflowPlanner
import AVOC.ArtifactWorkflowExamples

namespace Komorebi.AVOC.PlannerExamples

open ExecutablePlanner ArtifactWorkflowExamples

def executable := WorkflowPlanner.model proto [0] [()]

theorem realization : Realizes executable (ArtifactWorkflow.controller proto) := by
  apply WorkflowPlanner.model_realizes
  · intro x; have h : x = 0 := Subsingleton.elim _ _; simp [h]
  · intro c; cases c; simp

theorem executable_three_step_value : (evaluate executable 3 initial).score = 3/2 := by
  rw [evaluate_exact _ _ realization]
  exact initial_three_step_value

theorem branching : BranchBound executable 4 2 :=
  WorkflowPlanner.model_branch_bound proto [0] [()]

theorem depth_three_reservation : workBound 4 2 3 = 1461 := by decide

theorem depth_three_within_credit : (evaluate executable 3 initial).work ≤ 1461 :=
  evaluate_work_le executable 4 2 branching 3 initial

theorem insufficient_credit_rejects : runReserved executable 4 2 3 1460 initial = none := by
  apply runReserved_reject
  decide

theorem affordable_depth_two : affordableDepth 4 2 181 3 = some 2 := by decide

theorem affordable_depth_three : affordableDepth 4 2 1461 3 = some 3 := by decide

theorem zero_credit_no_search : affordableDepth 4 2 0 3 = none := by decide

/-- A cheap lookahead cannot claim the value of the longer research workflow. -/
theorem myopic_value_zero : (evaluate executable 1 initial).score = 0 := by
  rw [evaluate_exact _ _ realization]
  exact no_receipt_one_step initial rfl

/-- Concrete executable policy still carries source, proof and budget safety. -/
theorem executable_demo_safe (hp : ArtifactWorkflow.CatalogueParsed proto) :
    Guarded.TreeSafe (ArtifactWorkflow.controller proto) (ArtifactWorkflow.SourceSafe proto 3)
      initial (Guarded.policyPlan (ArtifactWorkflow.controller proto)
        (fun k s => choose executable (fun _ => .stop) (k + 1) s) 3 initial) := by
  apply WorkflowPlanner.executable_policy_source_safe proto hp [0] [()] _ _ (fun k => k + 1)
    3 3 initial initial_source_safe
  · intro x; have h : x = 0 := Subsingleton.elim _ _; simp [h]
  · intro c; cases c; simp

end Komorebi.AVOC.PlannerExamples
