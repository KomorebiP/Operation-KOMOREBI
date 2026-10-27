import MachineTheory.SynthesisExamples
open Komorebi.MachineTheory Synthesis SynthesisExamples

/-- Deliberately false claim, required to fail for the stated proof diagnostic. -/
example : ((forgetfulScan task repeatGrammar []).transcript.map Prod.fst).Nodup := by
  simp only [forgetting_repeats_submission.2]
