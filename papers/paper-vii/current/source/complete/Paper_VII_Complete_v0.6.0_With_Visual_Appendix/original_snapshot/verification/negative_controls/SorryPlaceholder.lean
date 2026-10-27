module

public section
set_option autoImplicit false

-- EXPECTED FAILURE under -DwarningAsError=true; not part of the theorem library.
theorem placeholder : False := by sorry
