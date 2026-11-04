import Controls.FallingPositive

open Polynomial
open Komorebi.Polynomial.FallingFactorial
open Komorebi.Polynomial.FallingPackets
open Komorebi.Polynomial.Packets
open Komorebi.Polynomial.Controls.FallingPositive

-- Deliberately false: reversing the arrows changes the value at one from zero to two.
example :
    (fallingEquiv.symm (packet 2 0 (fallingEquiv ((X : ℚ[X]) ^ 2)))).eval 1 =
      (fallingPacket 2 0 ((X : ℚ[X]) ^ 2)).eval 1 := by
  rw [reverse_even_square, even_square]
  norm_num
  decide
