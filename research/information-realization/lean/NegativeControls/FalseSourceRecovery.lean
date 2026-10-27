module
public import KomorebiInformation
public section
open KomorebiInformation.Haar
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
-- EXPECTED REJECTION: predictive state equality does not imply source equality.
theorem invisibleEqualsZero : (invisible : Source (ZMod 5)) = 0 := by decide
