import MachineTheory.PrefixExamples
open Komorebi.MachineTheory HardInquiry OrderedCompiler PrefixExamples Finset

/-- Deliberately false claim: the gate requires its mathematical diagnostic. -/
example : SynthesisExamples.evaluate .capped (0,5,8)=false := by
  change true=false
  simp
