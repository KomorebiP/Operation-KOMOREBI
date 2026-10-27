import KomorebiPadic.SupportExamples
open KomorebiPadic.CoordinateSupport
example : (least nilpotentSystem).card = 1 := by rw [nilpotentSystem_least_full]; decide
