import KTG.IUT312DiscreteWitness
open KTG.ValuationBridge
-- Must fail: the pilot at depth 1 is not bounded by the unmodified theta at depth 4.
example : negativeLogDepth 1 ≤ negativeLogDepth 4 := by decide
