import AVOC.RateDistortionExamples
import Mathlib.Tactic.FinCases

open Komorebi.AVOC

example :
    ∃ Vbar : Unit → ℚ,
      ValueApproximation (fun _ : Fin 3 => ()) threeLevelValue Vbar 1 := by
  let Vbar : Unit → ℚ := fun _ => 3
  refine ⟨Vbar, ?_⟩
  intro s
  fin_cases s <;> norm_num [threeLevelValue, Vbar]
