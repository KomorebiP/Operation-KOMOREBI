import Controls.FallingPositive

open Polynomial
open Komorebi.Polynomial.FallingPackets
open Komorebi.Polynomial.Packets
open Komorebi.Polynomial.Controls.FallingPositive

-- Deliberately false: ordinary even degree retains the whole square; falling even degree does not.
example :
    (fallingPacket 2 0 ((X : ℚ[X]) ^ 2)).eval 1 =
      (packet 2 0 ((X : ℚ[X]) ^ 2)).eval 1 := by
  rw [even_square, packet_X_pow]
  norm_num
  decide
