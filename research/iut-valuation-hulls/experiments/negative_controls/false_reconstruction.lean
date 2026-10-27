import KTG.HodgeFinite

-- Expected compiler rejection: two equal multiplicative reducts have distinct sums.
example : KTG.HodgeBridge.observeOnePlusOne KTG.HodgeBridge.standard5 =
    KTG.HodgeBridge.observeOnePlusOne KTG.HodgeBridge.alien5 := by decide
