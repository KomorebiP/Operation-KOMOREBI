import Controls.FourierPositive

open Polynomial
open scoped BigOperators
open Komorebi.Polynomial.RootsOfUnity
open Komorebi.Polynomial.Controls.FourierPositive

-- Deliberately false: the positive character sends degree one to the opposite residue modulo four.
example :
    ((1 / (4 : ℂ)) • ∑ ℓ ∈ Finset.range 4,
      (Complex.I ^ ((1 * ℓ : ℕ) : ℤ)) •
        (X : ℂ[X]).comp (C (Complex.I ^ ℓ) * X)).coeff 1 =
      (average 4 1 Complex.I (X : ℂ[X])).coeff 1 := by
  rw [positive_character_degree_one, order_four_degree_one]
  norm_num
  decide
