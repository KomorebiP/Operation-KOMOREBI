import KTG.HodgeAnchors
open KTG.HodgeBridge
-- Must fail: the same multiplication and the first addition anchor do NOT fix 1+2.
example : observedOnePlusTwo17 standard17 = observedOnePlusTwo17 alien17 := by decide
