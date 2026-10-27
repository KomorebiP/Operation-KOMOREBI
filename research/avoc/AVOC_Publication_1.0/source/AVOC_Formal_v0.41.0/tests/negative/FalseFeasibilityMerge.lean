import AVOC.StateDependentControl

open Komorebi.AVOC

def incompatibleActionsSystem : StateControlSystem Bool Bool where
  actions s := if s then {true} else {false}
  actions_nonempty s := by cases s <;> simp
  transition s _ := s
  reward _ _ := 0

def eraseAllStates : Bool → Unit := fun _ => ()

/-- This must be rejected: the representation merges `false` and `true`, but
those states expose different feasible action sets. -/
example : StateControlSufficient incompatibleActionsSystem eraseAllStates := by
  intro s t hst
  cases s <;> cases t <;> simp [incompatibleActionsSystem]
