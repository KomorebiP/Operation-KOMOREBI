import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : ∀ i : Fin 3, i ∈ ([0,1] : List (Fin 3)) := by
  intro i
  fin_cases i <;> simp
