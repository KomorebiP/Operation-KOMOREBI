module
public import DyadicFourAllRows
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.AllRowsControls
open Mahler DyadicFourCongruences

theorem zeroth_row_every_order (k : ℕ) :
    (2:ℤ_[2])^k ∣ difference 1 k (normalizedLift 0 (by decide)) 0 :=
  DyadicFourAllRows.base_step_bound 0 k 0 (by decide)

theorem zeroth_row_every_step (u k : ℕ) :
    GlobalEulerBoundary.precision 2 (k:ℤ)
      (difference u k (Congruential.unnormalized 4 3) 0) :=
  DyadicFourAllRows.unnormalized_precision 3 u k 0 (by decide)

theorem zero_step_every_order (j k n : ℕ) (hj : j<4) :
    GlobalEulerBoundary.precision 2 (k:ℤ)
      (difference 0 k (Congruential.coeff 4 j) n) :=
  DyadicFourAllRows.normalized_precision j 0 k n hj

#print axioms zeroth_row_every_order
#print axioms zeroth_row_every_step
#print axioms zero_step_every_order
end KomorebiPaperIX.AllRowsControls
