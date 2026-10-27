import ProofPath.Binary
open Matrix
example : dotProduct (![0] : Fin 1 → ZMod 2) ![1] = 1 := by decide
