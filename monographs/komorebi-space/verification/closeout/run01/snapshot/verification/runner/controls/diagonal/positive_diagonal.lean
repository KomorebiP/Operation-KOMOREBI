import KomorebiSpace.DiagonalTheorems
open KomorebiSpace.DiagonalRegularization
example : A 1 ≤ 4 / 3 := by simpa using A_upper 1 (by decide)
example : ‖hardPrefix 3‖ ^ 2 = 3 := by simpa using norm_hardPrefix_sq 3
#check proposition_30_1
#check corollary_30_3
#print axioms proposition_30_1
#print axioms corollary_30_3
