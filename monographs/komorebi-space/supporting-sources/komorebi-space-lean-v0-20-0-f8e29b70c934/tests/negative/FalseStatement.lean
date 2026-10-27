import Mathlib.Data.Int.Basic
-- Expected: rejected by Lean.
example : (0 : ℤ) = 1 := by decide
