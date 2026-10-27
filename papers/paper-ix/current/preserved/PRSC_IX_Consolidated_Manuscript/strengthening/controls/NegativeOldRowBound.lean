module
public import DyadicFourAllRows
@[expose] public section
noncomputable section
set_option autoImplicit false
open KomorebiPaperIX
example (k : ℕ) : (2:ℤ_[2])^k ∣ Mahler.difference 1 k
    (DyadicFourCongruences.normalizedLift 0 (by decide)) 0 := by
  exact DyadicFourCongruences.base_step_bound 0 k 0 (by decide)
