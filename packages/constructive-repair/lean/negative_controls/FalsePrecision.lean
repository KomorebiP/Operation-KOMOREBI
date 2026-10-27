import KomorebiRepair
-- Expected rejection: the valuation is two, not at least three.
theorem bad_precision : (7 : ℤ) ^ 3 ∣ -98 := by norm_num
