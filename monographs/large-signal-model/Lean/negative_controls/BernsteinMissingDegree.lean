import KomorebiLSM.BernsteinRationalBasis

open Komorebi.LSM.BernsteinRationalBasis

-- Truncating X to degree zero loses its X coefficient; exact reconstruction needs k≤n.
example : (∑ i : Fin 1, Polynomial.C (monomialCoordinates 0 1 i) *
    bernsteinPolynomial ℚ 0 i).coeff 1 = 1 := by
  norm_num [monomialCoordinates, Fin.sum_univ_one]
