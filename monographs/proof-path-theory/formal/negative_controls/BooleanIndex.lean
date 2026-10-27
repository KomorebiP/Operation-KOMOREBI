import ProofPath.TraceWire
open ProofPath.Trace.Wire
example : decodeNat (.bool true) = some 1 := by decide
