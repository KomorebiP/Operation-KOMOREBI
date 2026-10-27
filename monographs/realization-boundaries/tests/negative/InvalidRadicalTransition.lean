import tests.Contracts

set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesRootTests

example : ZMod (primeRadical 10) →+ ZMod (primeRadical 6) :=
  (ZMod.castHom (primeRadical_dvd_of_dvd (by decide : 0 < 10)
    (by decide : 6 ∣ 10)) (ZMod (primeRadical 6))).toAddMonoidHom
