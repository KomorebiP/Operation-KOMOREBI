import KomorebiRepair
-- Expected compiler rejection: an explicit false arithmetic statement.
theorem false_equality : (0 : ℕ) = 1 := by decide
