import DiagonalResonantHorizon
#check map_ofNat
#check map_natCast
#check padicValNat_self
#check padicValNat.prime_pow
#check Pi.isUnit_iff
example : PadicInt.toZModPow 2 (4 : PadicInt 3) = 4 := by
  norm_num [map_ofNat]
example : padicValNat 3 3 = 1 := by
  exact padicValNat_self
example : padicValNat 3 9 = 2 := by
  change padicValNat 3 (3 ^ 2) = 2
  exact padicValNat.prime_pow 2
