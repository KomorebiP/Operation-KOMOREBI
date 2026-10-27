import AVOC.LiveExecutionCodec
open Lean Komorebi.AVOC
open ArtifactWorkflow PlannerRuntime LiveExecution Binding
example (j : Job) (wire : Json) (actual : StoreView) (ticket : Ticket)
    (hc : context ticket.artifact.identity = [])
    (hf : ticket.artifact.identity.statement = Certificate.Formula.falsity) :
    ∃ es s, resume j wire actual = .ok (es,s) ∧ actual.admitted = some ticket := by
  have hn : ¬ ∃ es s, resume j wire actual = .ok (es,s) ∧ actual.admitted = some ticket := by
    rintro ⟨es,s,h,ha⟩
    exact false_root_cannot_be_confirmed j wire actual es s ticket h ha hc hf
  simp only [hn]
