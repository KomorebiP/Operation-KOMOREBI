module
public import DyadicFourLeastPeriods
@[expose] public section
set_option autoImplicit false
open KomorebiPaperIX
example : padicValRat 2
    (Congruential.unnormalized 4 2 (0 + 1) - Congruential.unnormalized 4 2 0) = 6 := by
  have h := (DyadicFourLeastPeriods.exact_displacement 2 0 1 (by decide) (by decide)).2
  rw [DyadicFourLeastPeriods.originalBonus_values.2.2.1] at h
  norm_num at h
  exact h
