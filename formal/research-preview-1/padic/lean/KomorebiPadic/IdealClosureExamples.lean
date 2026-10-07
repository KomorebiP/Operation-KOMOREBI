import KomorebiPadic.CyclicMaskAutomaton
import KomorebiPadic.PrimePowerIdealValuation
import KomorebiPadic.SupportExamples

namespace KomorebiPadic
namespace CoordinateIdeal

/-- The nilpotent witness needs one binary coordinate, not two full mod-four coordinates. -/
def nilpotentCapacity : Fin 2 → ℕ := fun i => if i = 0 then 1 else 0

theorem nilpotentCapacity_closed : Closed (p := 2) (r := 2)
    CoordinateSupport.nilpotentSystem nilpotentCapacity := by
  constructor
  · intro i
    fin_cases i <;> decide +kernel
  · intro d i j
    fin_cases d
    fin_cases i <;> fin_cases j <;>
      simp only [CoordinateSupport.nilpotentSystem, CoordinateSupport.matrixSystem_column] <;>
      decide +kernel

theorem nilpotent_least_capacity :
    least (by decide : 0 < 2) (r := 2) CoordinateSupport.nilpotentSystem = nilpotentCapacity := by
  have hle := least_le (by decide : 0 < 2) (r := 2)
    CoordinateSupport.nilpotentSystem nilpotentCapacity nilpotentCapacity_closed
  have hinit := (least_closed (by decide : 0 < 2) (r := 2)
    CoordinateSupport.nilpotentSystem).1 (0 : Fin 2)
  have hc : PrimePowerIdeal.capacity 2 2 (CoordinateSupport.nilpotentSystem.initial 0) = 1 := by
    decide +kernel
  rw [hc] at hinit
  funext i
  fin_cases i
  · exact le_antisymm (hle (0 : Fin 2)) hinit
  · exact le_antisymm (hle (1 : Fin 2)) (Nat.zero_le _)

theorem nilpotent_ideal_card :
    Nat.card (State (p := 2) (r := 2)
      (least (by decide : 0 < 2) (r := 2) CoordinateSupport.nilpotentSystem)) = 2 := by
  rw [boxState_card (by decide : 0 < 2) _
    (least_bound (by decide : 0 < 2) (r := 2) CoordinateSupport.nilpotentSystem),
    nilpotent_least_capacity]
  norm_num [nilpotentCapacity, Fin.sum_univ_succ]

/-- The old support box has sixteen states for this same witness. -/
theorem nilpotent_support_card :
    Nat.card (CoordinateSupport.State (R := ZMod 4)
      (CoordinateSupport.least CoordinateSupport.nilpotentSystem)) = 16 := by
  rw [CoordinateSupport.nilpotentSystem_least_full]
  simp [CoordinateSupport.State, Nat.card_eq_fintype_card]

end CoordinateIdeal
end KomorebiPadic
