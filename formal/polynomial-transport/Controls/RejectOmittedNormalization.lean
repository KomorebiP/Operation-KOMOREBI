import Controls.FourierPositive

open Polynomial
open scoped BigOperators
open Komorebi.Polynomial.RootsOfUnity
open Komorebi.Polynomial.Controls.FourierPositive

-- Deliberately false: the unnormalized character sum doubles the retained constant.
example :
    (∑ ℓ ∈ Finset.range 2,
      ((-1 : ℂ) ^ (-((0 * ℓ : ℕ) : ℤ))) •
        (1 : ℂ[X]).comp (C ((-1 : ℂ) ^ ℓ) * X)).coeff 0 =
      (average 2 0 (-1) (1 : ℂ[X])).coeff 0 := by
  rw [unnormalized_even_constant, order_two_constant]
  norm_num
  decide
