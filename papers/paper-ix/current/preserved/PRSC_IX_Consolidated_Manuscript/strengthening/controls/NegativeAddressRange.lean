module
public import DyadicFourAllRows
@[expose] public section
noncomputable section
set_option autoImplicit false
open KomorebiPaperIX
example (k n : ℕ) : GlobalEulerBoundary.precision 2 (k:ℤ)
    (Mahler.difference 1 k (Congruential.coeff 4 4) n) := by
  exact DyadicFourAllRows.normalized_precision 4 1 k n (by decide)
