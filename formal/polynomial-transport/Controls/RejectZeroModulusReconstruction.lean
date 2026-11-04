import Controls.FallingPositive

open Polynomial
open scoped BigOperators
open Komorebi.Polynomial.FallingPackets

-- Deliberately false: an empty family of packets cannot reconstruct the constant one.
example :
    (∑ r ∈ Finset.range 0, fallingPacket 0 r (1 : ℚ[X])).coeff 0 = 1 := by
  norm_num
  decide
