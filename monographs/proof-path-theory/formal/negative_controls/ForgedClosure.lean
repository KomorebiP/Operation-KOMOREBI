import ProofPath.TraceExamples
open ProofPath.Trace ProofPath.Trace.Examples
example : checkClosure chain [] [0, 1, 2, 3] = true := by decide
