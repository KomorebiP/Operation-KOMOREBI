module

public section
set_option autoImplicit false

-- EXPECTED FAILURE: false equality, not part of the theorem library.
theorem falseEquality : (0 : Nat) = 1 := by decide
