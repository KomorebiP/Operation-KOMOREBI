import Controls.FourierPositive

open Polynomial
open Komorebi.Polynomial.RootsOfUnity
open Komorebi.Polynomial.Packets
open Komorebi.Polynomial.Controls.FourierPositive

-- Deliberately false: one is a second root of unity, but not a primitive second root.
example :
    (average 2 0 1 (X : ℂ[X])).coeff 1 = (packet 2 0 (X : ℂ[X])).coeff 1 := by
  rw [nonprimitive_even_X, coeff_packet]
  norm_num
  decide
