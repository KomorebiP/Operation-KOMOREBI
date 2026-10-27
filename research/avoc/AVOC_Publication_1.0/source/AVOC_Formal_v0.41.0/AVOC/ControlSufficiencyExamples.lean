import AVOC.ControlSufficiency

namespace Komorebi.AVOC

/-- Three-state example witnessing that arbitrary information refinement need
not preserve control sufficiency. -/
def refinementCounterSystem : FiniteControlSystem (Fin 3) Unit where
  actions := {()}
  actions_nonempty := by simp
  transition s _ := if s = 0 then 0 else 2
  reward _ _ := 0

/-- The coarsest constant representation. -/
def refinementCounterCoarse : Fin 3 → Unit := fun _ => ()

/-- A strictly finer representation merging states 0 and 1 while separating 2. -/
def refinementCounterFine : Fin 3 → Bool := fun s => if s = 2 then true else false

/-- The fine representation deterministically decodes to the constant coarse
representation. -/
theorem refinementCounter_fine_refines_coarse :
    Refines refinementCounterFine refinementCounterCoarse := by
  refine ⟨fun _ => (), ?_⟩
  intro s
  rfl

/-- The constant coarse representation is control-sufficient because reward is
state-independent and projected transitions are necessarily constant. -/
theorem refinementCounter_coarse_controlSufficient :
    ControlSufficient refinementCounterSystem refinementCounterCoarse := by
  intro s t hst a ha
  exact ⟨rfl, rfl⟩

/-- The finer representation is not dynamically closed: states 0 and 1 are
merged now, but their successors fall in different fine fibers. -/
theorem refinementCounter_fine_not_controlSufficient :
    ¬ ControlSufficient refinementCounterSystem refinementCounterFine := by
  apply transition_mismatch_obstructs_controlSufficiency
    refinementCounterSystem (φ := refinementCounterFine)
    (s := (0 : Fin 3)) (t := (1 : Fin 3)) (a := ())
  · simp [refinementCounterFine]
  · simp [refinementCounterSystem]
  · simp [refinementCounterSystem, refinementCounterFine]

/-- Therefore control sufficiency is not monotone under arbitrary deterministic
refinement, unlike one-shot task sufficiency. -/
theorem controlSufficiency_not_monotone_under_refinement :
    Refines refinementCounterFine refinementCounterCoarse ∧
    ControlSufficient refinementCounterSystem refinementCounterCoarse ∧
    ¬ ControlSufficient refinementCounterSystem refinementCounterFine := by
  exact ⟨refinementCounter_fine_refines_coarse,
    refinementCounter_coarse_controlSufficient,
    refinementCounter_fine_not_controlSufficient⟩

end Komorebi.AVOC
