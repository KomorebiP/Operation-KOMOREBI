import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : teacherComparisons task (scan task quotientGrammar []) < teacherComparisons task (scan task grammar []) := by
  rw [same_teacher_work.1, same_teacher_work.2]
  norm_num
