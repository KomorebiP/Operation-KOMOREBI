import AVOC.HorizonContext

namespace Komorebi.AVOC

/-- A four-state one-action system where states 0 and 1 have the same immediate
reward but transition to states 2 and 3, whose rewards differ. -/
def delayedDistinctionSystem : StateControlSystem (Fin 4) Unit where
  actions _ := {()}
  actions_nonempty _ := by simp
  transition s _ := if s = 0 then 2 else if s = 1 then 3 else s
  reward s _ := if s = 3 then 1 else 0

/-- States 0 and 1 are behaviorally indistinguishable for one decision. -/
theorem delayedDistinction_equiv_horizon_one :
    HorizonEquivalent delayedDistinctionSystem 1 (0 : Fin 4) (1 : Fin 4) := by
  simp [HorizonEquivalent, delayedDistinctionSystem]

/-- The same states are not behaviorally equivalent for two decisions, because
their successors expose different next-step reward. -/
theorem delayedDistinction_not_equiv_horizon_two :
    ¬ HorizonEquivalent delayedDistinctionSystem 2 (0 : Fin 4) (1 : Fin 4) := by
  simp [HorizonEquivalent, delayedDistinctionSystem]

/-- Thus the two-step behavioral quotient is strictly more discriminating on
this pair than the one-step quotient. -/
theorem delayedDistinction_strict_horizon_refinement :
    horizonQuotientMap delayedDistinctionSystem 1 (0 : Fin 4) =
      horizonQuotientMap delayedDistinctionSystem 1 (1 : Fin 4) ∧
    horizonQuotientMap delayedDistinctionSystem 2 (0 : Fin 4) ≠
      horizonQuotientMap delayedDistinctionSystem 2 (1 : Fin 4) := by
  constructor
  · exact Quotient.sound delayedDistinction_equiv_horizon_one
  · intro h
    exact delayedDistinction_not_equiv_horizon_two (Quotient.exact h)

end Komorebi.AVOC
