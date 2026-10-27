import AVOC.StagedAffineControl

namespace Komorebi.AVOC.Affine.Staged

open Komorebi.AVOC.Affine.Terminal

variable {n m : Nat}

/-- Operational faults are not model observations. -/
inductive AttemptResult where
  | report (value : Bool)
  | fault
  deriving Repr, DecidableEq


def Supported (md : Model n m) (s : State md) (a : Action) (o : Bool) : Prop :=
  a ∈ actions md s ∧ 0 < probability md s a o

/-- A report advances the staged controller only when the selected action was
available and the report has positive probability in the declared model. -/
noncomputable def acknowledge (md : Model n m) (s : State md) (a : Action)
    (r : AttemptResult) : Option (State md) := by
  classical
  exact match r with
    | .fault => none
    | .report o => if Supported md s a o then some (step md s a o) else none

@[simp] theorem fault_rejected (md : Model n m) (s : State md) (a : Action) :
    acknowledge md s a .fault = none := rfl


theorem supported_report_accepted (md : Model n m) (s : State md) (a : Action)
    (o : Bool) (h : Supported md s a o) :
    acknowledge md s a (.report o) = some (step md s a o) := by
  simp [acknowledge,h]


theorem unsupported_report_rejected (md : Model n m) (s : State md) (a : Action)
    (o : Bool) (h : ¬ Supported md s a o) :
    acknowledge md s a (.report o) = none := by
  simp [acknowledge,h]


theorem acknowledged_exact (md : Model n m) (s : State md) (a : Action)
    (o : Bool) (t : State md) (h : acknowledge md s a (.report o) = some t) :
    Supported md s a o ∧ t = step md s a o := by
  classical
  simp only [acknowledge] at h
  split at h
  next hs => exact ⟨hs,(Option.some.inj h).symm⟩
  next _ => simp at h


theorem acknowledged_preserves_budget (md : Model n m) (credit : Nat)
    (s : State md) (hs : BudgetSafe credit s) (a : Action) (o : Bool)
    (t : State md) (h : acknowledge md s a (.report o) = some t) :
    BudgetSafe credit t := by
  obtain ⟨ha,rfl⟩ := acknowledged_exact md s a o t h
  exact step_budgetSafe md s credit hs a ha.1 o


theorem successful_warm_report_ready (md : Model n m) (s : State md)
    (t : State md) (h : acknowledge md s .inspectWarm (.report true) = some t) :
    t.warmStatus = .ready := by
  obtain ⟨_,rfl⟩ := acknowledged_exact md s .inspectWarm true t h
  rfl


theorem failed_warm_report_not_ready (md : Model n m) (s : State md)
    (t : State md) (h : acknowledge md s .inspectWarm (.report false) = some t) :
    t.warmStatus = .failed := by
  obtain ⟨_,rfl⟩ := acknowledged_exact md s .inspectWarm false t h
  rfl


theorem successful_cold_report_ready (md : Model n m) (s : State md)
    (t : State md) (h : acknowledge md s .generateCold (.report true) = some t) :
    t.coldStatus = .ready := by
  obtain ⟨_,rfl⟩ := acknowledged_exact md s .generateCold true t h
  rfl


theorem failed_cold_report_not_ready (md : Model n m) (s : State md)
    (t : State md) (h : acknowledge md s .generateCold (.report false) = some t) :
    t.coldStatus = .failed := by
  obtain ⟨_,rfl⟩ := acknowledged_exact md s .generateCold false t h
  rfl

/-- A ready warm state exposes the model's proof-carrying warm implementation. -/
theorem ready_warm_deployment_sound (md : Model n m) (s : State md)
    (_h : s.warmStatus = .ready) :
    (∀ x, execute md.warm.deployment.selected x = execute md.source x) ∧
      executionCost md.warm.deployment.selected ≤ executionCost md.source ∧
      md.warm.deployment.kind = .warm := by
  refine ⟨?_,?_,md.warm.kind_eq⟩
  · intro x
    exact (md.warm.deployment.correct x).trans
      (congrArg (fun q => execute q x) md.warm.source_eq)
  · calc
      executionCost md.warm.deployment.selected ≤ executionCost md.warm.deployment.source :=
        md.warm.deployment.noWorse
      _ = executionCost md.source := congrArg executionCost md.warm.source_eq

/-- The analogous cold implementation proof. -/
theorem ready_cold_deployment_sound (md : Model n m) (s : State md)
    (_h : s.coldStatus = .ready) :
    (∀ x, execute md.cold.deployment.selected x = execute md.source x) ∧
      executionCost md.cold.deployment.selected ≤ executionCost md.source ∧
      md.cold.deployment.kind = .cold := by
  refine ⟨?_,?_,md.cold.kind_eq⟩
  · intro x
    exact (md.cold.deployment.correct x).trans
      (congrArg (fun q => execute q x) md.cold.source_eq)
  · calc
      executionCost md.cold.deployment.selected ≤ executionCost md.cold.deployment.source :=
        md.cold.deployment.noWorse
      _ = executionCost md.source := congrArg executionCost md.cold.source_eq

/-- A terminal action cannot be selected before its corresponding stage succeeds. -/
theorem deployWarm_requires_ready (md : Model n m) (s : State md)
    (h : .deployWarm ∈ actions md s) : s.warmStatus = .ready :=
  (deployWarm_mem_iff md s).1 h |>.2


theorem deployCold_requires_ready (md : Model n m) (s : State md)
    (h : .deployCold ∈ actions md s) : s.coldStatus = .ready :=
  (deployCold_mem_iff md s).1 h |>.2

end Komorebi.AVOC.Affine.Staged
