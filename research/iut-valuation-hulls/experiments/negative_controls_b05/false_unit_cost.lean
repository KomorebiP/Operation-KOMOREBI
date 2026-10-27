import KTG.ValuationCost
open KTG.ValuationBridge
-- Must fail: scalar depth 4 to depth 1 has exact cost 3, not 0.
example : enlargementCost 4 1 = 0 := by decide
