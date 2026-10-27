import ProofPath.TraceExamples
open ProofPath.Trace ProofPath.Trace.Examples
example : checkClosure chain [0] [0, 1] = true := by decide
