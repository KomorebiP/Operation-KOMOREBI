import KTG.HodgeFinite

-- Expected compiler rejection: this multiplicative automorphism is not additive.
example : KTG.HodgeBridge.inversion5 ((1 : Fin 5) + (1 : Fin 5)) =
    KTG.HodgeBridge.inversion5 1 + KTG.HodgeBridge.inversion5 1 := by decide
