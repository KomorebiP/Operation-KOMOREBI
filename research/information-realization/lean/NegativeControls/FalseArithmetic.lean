module
public import KomorebiInformation
public section
-- EXPECTED REJECTION: a genuinely false proposition, not an import error.
theorem badArithmetic : (0 : Nat) = 1 := by decide
