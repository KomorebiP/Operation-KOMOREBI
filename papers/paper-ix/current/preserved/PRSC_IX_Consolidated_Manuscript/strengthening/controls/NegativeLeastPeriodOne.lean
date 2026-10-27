module
public import ExactPeriodControls
@[expose] public section
set_option autoImplicit false
open KomorebiPaperIX
example : IsLeast
    {T : ℕ | ExactPeriodClassification.IsPeriod 2 (Congruential.unnormalized 4 2) 6 T} 1 := by
  exact ExactPeriodControls.address_two_mod64_least
