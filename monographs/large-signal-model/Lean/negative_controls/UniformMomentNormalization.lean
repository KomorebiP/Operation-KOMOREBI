import KomorebiLSM.UniformIntervalMoments
open Komorebi.LSM.UniformIntervalMoments

/- The reference law is normalized uniform measure. Replacing it by raw
Lebesgue measure changes the zeroth moment and therefore the population Gram. -/
example : moment 0 = 2 := by norm_num
